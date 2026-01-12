"""
ImmoSafe DE - Natural Disaster Service
Comprehensive natural disaster risk analysis for German properties.
Uses Open-Meteo APIs (free, no API key required) for weather-based risks.
"""

import logging
import math
from datetime import date, timedelta
from typing import TypedDict, Optional

import httpx
import numpy as np
from cachetools import TTLCache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class StormRiskData(TypedDict):
    """Storm/wind risk analysis data."""
    max_wind_gust_kmh: float
    avg_annual_storm_days: float  # Days with gusts > 75 km/h
    percentile_95_gust: float
    storm_risk_score: int  # 0-100
    storm_risk_level: str
    factors: list[str]
    recommendations: list[str]


class FireRiskData(TypedDict):
    """Wildfire risk analysis data."""
    fire_weather_index: float
    avg_summer_temp: float
    drought_days_per_year: float
    fire_risk_score: int  # 0-100
    fire_risk_level: str
    factors: list[str]
    recommendations: list[str]


class TemperatureRiskData(TypedDict):
    """Extreme temperature risk analysis data."""
    heat_wave_days_per_year: float  # Days > 30°C
    frost_days_per_year: float  # Days < 0°C
    extreme_heat_days: float  # Days > 35°C
    temp_risk_score: int  # 0-100
    temp_risk_level: str
    factors: list[str]
    recommendations: list[str]


class HailRiskData(TypedDict):
    """Thunderstorm/hail risk analysis data."""
    heavy_precip_days: float  # Days with > 20mm
    avg_summer_precip_intensity: float
    hail_risk_score: int  # 0-100
    hail_risk_level: str
    factors: list[str]
    recommendations: list[str]


class EarthquakeRiskData(TypedDict):
    """Earthquake zone risk data (static for Germany)."""
    zone: int  # 0-3
    zone_name: str
    peak_ground_acceleration: float  # m/s²
    earthquake_risk_score: int  # 0-100
    earthquake_risk_level: str
    factors: list[str]
    recommendations: list[str]


class ComprehensiveRiskData(TypedDict):
    """Complete natural disaster risk analysis."""
    flood_risk: dict
    storm_risk: StormRiskData
    fire_risk: FireRiskData
    temperature_risk: TemperatureRiskData
    hail_risk: HailRiskData
    earthquake_risk: EarthquakeRiskData
    total_risk_score: int
    total_risk_level: str
    primary_risks: list[str]


# ═══════════════════════════════════════════════════════════════════════════════
# GERMAN EARTHQUAKE ZONES (Static Data based on DIN 4149 / Eurocode 8)
# ═══════════════════════════════════════════════════════════════════════════════

# Earthquake zones in Germany (simplified polygons)
# Zone 0: No significant risk (most of Germany)
# Zone 1: Low risk (parts of Swabian Alb, Vogtland)
# Zone 2: Moderate risk (Lower Rhine, parts of Upper Rhine)
# Zone 3: Higher risk (Upper Rhine Graben - Freiburg, Karlsruhe, Basel area)

EARTHQUAKE_ZONES = [
    # Zone 3: Upper Rhine Graben (highest risk in Germany)
    {
        "zone": 3,
        "name": "Oberrheingraben (Zone 3)",
        "pga": 0.8,  # Peak Ground Acceleration in m/s²
        "bounds": {"lat_min": 47.5, "lat_max": 49.5, "lng_min": 7.5, "lng_max": 8.8},
    },
    # Zone 2: Lower Rhine / Cologne Bay
    {
        "zone": 2,
        "name": "Niederrheinische Bucht (Zone 2)",
        "pga": 0.6,
        "bounds": {"lat_min": 50.3, "lat_max": 51.5, "lng_min": 6.0, "lng_max": 7.5},
    },
    # Zone 2: Parts of Upper Rhine (north)
    {
        "zone": 2,
        "name": "Nördlicher Oberrhein (Zone 2)",
        "pga": 0.6,
        "bounds": {"lat_min": 49.3, "lat_max": 50.2, "lng_min": 8.0, "lng_max": 8.8},
    },
    # Zone 1: Swabian Alb
    {
        "zone": 1,
        "name": "Schwäbische Alb (Zone 1)",
        "pga": 0.4,
        "bounds": {"lat_min": 48.0, "lat_max": 49.0, "lng_min": 8.5, "lng_max": 10.5},
    },
    # Zone 1: Vogtland/Saxon area
    {
        "zone": 1,
        "name": "Vogtland (Zone 1)",
        "pga": 0.4,
        "bounds": {"lat_min": 50.0, "lat_max": 50.8, "lng_min": 11.8, "lng_max": 12.8},
    },
    # Zone 1: Lake Constance area
    {
        "zone": 1,
        "name": "Bodenseeregion (Zone 1)",
        "pga": 0.4,
        "bounds": {"lat_min": 47.5, "lat_max": 48.0, "lng_min": 8.8, "lng_max": 10.0},
    },
]


def get_earthquake_zone(lat: float, lng: float) -> EarthquakeRiskData:
    """
    Determine earthquake zone for a location in Germany.
    
    Args:
        lat: Latitude
        lng: Longitude
        
    Returns:
        EarthquakeRiskData with zone information and risk assessment.
    """
    # Check each zone (ordered by severity, highest first)
    for zone_data in EARTHQUAKE_ZONES:
        bounds = zone_data["bounds"]
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and
            bounds["lng_min"] <= lng <= bounds["lng_max"]):
            
            zone = zone_data["zone"]
            pga = zone_data["pga"]
            
            # Calculate risk score (Zone 3 = 75, Zone 2 = 50, Zone 1 = 25)
            risk_score = zone * 25
            
            # Determine level
            if zone >= 3:
                level = "Medium"
                factors = [
                    "Lage im Oberrheingraben - tektonisch aktive Zone",
                    "Historische Erdbeben mit Magnitude > 5 dokumentiert",
                    "Erhöhte seismische Aktivität möglich",
                ]
                recommendations = [
                    "Erdbebensichere Bauweise gemäß Eurocode 8 empfohlen",
                    "Schwere Möbel und Regale an Wänden befestigen",
                    "Erdbebenversicherung in Betracht ziehen",
                ]
            elif zone >= 2:
                level = "Low"
                factors = [
                    f"Lage in {zone_data['name']}",
                    "Gelegentliche leichte Erdbeben möglich",
                    "Moderate tektonische Aktivität",
                ]
                recommendations = [
                    "Standard-Bauvorschriften beachten",
                    "Grundlegende Erdbebensicherheit empfohlen",
                ]
            else:
                level = "Low"
                factors = [
                    f"Lage in {zone_data['name']}",
                    "Seltene, meist schwache Erdbeben",
                ]
                recommendations = [
                    "Keine besonderen Maßnahmen erforderlich",
                ]
            
            return EarthquakeRiskData(
                zone=zone,
                zone_name=zone_data["name"],
                peak_ground_acceleration=pga,
                earthquake_risk_score=risk_score,
                earthquake_risk_level=level,
                factors=factors,
                recommendations=recommendations,
            )
    
    # Default: Zone 0 (no significant risk)
    return EarthquakeRiskData(
        zone=0,
        zone_name="Erdbebenzone 0 (vernachlässigbar)",
        peak_ground_acceleration=0.0,
        earthquake_risk_score=5,  # Minimal baseline
        earthquake_risk_level="Low",
        factors=[
            "Keine signifikante Erdbebenzone",
            "Deutschland ist seismisch relativ stabil",
            "Erdbeben äußerst selten und schwach",
        ],
        recommendations=[
            "Keine besonderen Maßnahmen erforderlich",
        ],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# NATURAL DISASTER SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class NaturalDisasterService:
    """
    Comprehensive natural disaster risk analysis for German properties.
    Uses Open-Meteo APIs (free, no API key required).
    """
    
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    
    # In-memory caches with TTL (1 hour) and max size (500 entries each)
    _storm_cache = TTLCache(maxsize=500, ttl=3600)
    _fire_cache = TTLCache(maxsize=500, ttl=3600)
    _temp_cache = TTLCache(maxsize=500, ttl=3600)
    _hail_cache = TTLCache(maxsize=500, ttl=3600)
    
    @staticmethod
    def _cache_key(lat: float, lng: float) -> tuple[float, float]:
        """Generate cache key from coordinates."""
        return (round(lat, 3), round(lng, 3))
    
    @staticmethod
    def _get_risk_level(score: int) -> str:
        """Convert score to risk level."""
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"
    
    async def get_storm_risk(self, lat: float, lng: float) -> StormRiskData:
        """
        Analyze storm/wind risk using 5-year historical wind data.
        
        Factors:
        - Maximum wind gusts recorded
        - 95th percentile of daily max gusts
        - Number of storm days (gusts > 75 km/h)
        """
        cache_key = self._cache_key(lat, lng)
        if cache_key in self._storm_cache:
            return self._storm_cache[cache_key]
        
        try:
            end_date = date.today() - timedelta(days=7)
            start_date = end_date - timedelta(days=5 * 365)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    self.ARCHIVE_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "wind_gusts_10m_max",
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            gusts = [v for v in daily.get("wind_gusts_10m_max", []) if v is not None]
            
            if not gusts:
                return self._default_storm_risk()
            
            gusts_array = np.array(gusts)
            max_gust = float(np.max(gusts_array))
            p95_gust = float(np.percentile(gusts_array, 95))
            storm_days = float(np.sum(gusts_array > 75)) / 5  # Per year
            
            # Calculate risk score
            # Max 100 points: 40 for max gust, 30 for p95, 30 for frequency
            score = 0
            
            # Max gust scoring (up to 40 points)
            if max_gust > 130:
                score += 40
            elif max_gust > 100:
                score += 30
            elif max_gust > 80:
                score += 20
            elif max_gust > 60:
                score += 10
            
            # P95 scoring (up to 30 points)
            if p95_gust > 70:
                score += 30
            elif p95_gust > 55:
                score += 20
            elif p95_gust > 40:
                score += 10
            
            # Storm frequency (up to 30 points)
            if storm_days > 15:
                score += 30
            elif storm_days > 10:
                score += 20
            elif storm_days > 5:
                score += 10
            
            level = self._get_risk_level(score)
            
            factors = []
            if max_gust > 100:
                factors.append(f"Orkanböen bis {max_gust:.0f} km/h in den letzten 5 Jahren")
            if storm_days > 10:
                factors.append(f"Durchschnittlich {storm_days:.0f} Sturmtage pro Jahr")
            if p95_gust > 55:
                factors.append(f"Regelmäßig starke Böen (95. Perzentil: {p95_gust:.0f} km/h)")
            if not factors:
                factors.append("Moderate Windverhältnisse in der Region")
            
            recommendations = []
            if score >= 50:
                recommendations.extend([
                    "Sturmschäden-Versicherung empfohlen",
                    "Dachziegel und Außenelemente regelmäßig prüfen",
                    "Bäume in Hausnähe auf Standfestigkeit prüfen",
                ])
            elif score >= 25:
                recommendations.append("Standard-Gebäudeversicherung mit Sturmschutz")
            else:
                recommendations.append("Keine besonderen Maßnahmen erforderlich")
            
            result = StormRiskData(
                max_wind_gust_kmh=round(max_gust, 1),
                avg_annual_storm_days=round(storm_days, 1),
                percentile_95_gust=round(p95_gust, 1),
                storm_risk_score=min(100, score),
                storm_risk_level=level,
                factors=factors,
                recommendations=recommendations,
            )
            
            self._storm_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Storm risk analysis failed: {e}")
            return self._default_storm_risk()
    
    def _default_storm_risk(self) -> StormRiskData:
        return StormRiskData(
            max_wind_gust_kmh=0.0,
            avg_annual_storm_days=0.0,
            percentile_95_gust=0.0,
            storm_risk_score=20,
            storm_risk_level="Low",
            factors=["Keine historischen Winddaten verfügbar"],
            recommendations=["Standard-Gebäudeversicherung empfohlen"],
        )
    
    async def get_fire_risk(self, lat: float, lng: float) -> FireRiskData:
        """
        Analyze wildfire risk using temperature, humidity, and precipitation data.
        Calculates simplified Fire Weather Index (FWI).
        """
        cache_key = self._cache_key(lat, lng)
        if cache_key in self._fire_cache:
            return self._fire_cache[cache_key]
        
        try:
            end_date = date.today() - timedelta(days=7)
            start_date = end_date - timedelta(days=3 * 365)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    self.ARCHIVE_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "temperature_2m_max,precipitation_sum",
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            temps = [v for v in daily.get("temperature_2m_max", []) if v is not None]
            precip = [v for v in daily.get("precipitation_sum", []) if v is not None]
            
            if not temps or not precip:
                return self._default_fire_risk()
            
            temps_array = np.array(temps)
            precip_array = np.array(precip)
            
            # Summer months analysis (indices for June-August)
            summer_temps = temps_array[temps_array > 20]
            avg_summer_temp = float(np.mean(summer_temps)) if len(summer_temps) > 0 else 20.0
            
            # Drought days (days with temp > 25°C and no rain)
            hot_days = temps_array > 25
            dry_days = precip_array < 1.0
            drought_days = float(np.sum(hot_days & dry_days)) / 3  # Per year
            
            # Simplified Fire Weather Index
            # Based on temperature extremes and drought frequency
            fwi = (avg_summer_temp - 15) * 2 + drought_days * 0.5
            fwi = max(0, min(100, fwi))
            
            # Risk scoring
            score = 0
            
            # Temperature component (up to 40 points)
            if avg_summer_temp > 30:
                score += 40
            elif avg_summer_temp > 27:
                score += 30
            elif avg_summer_temp > 24:
                score += 20
            elif avg_summer_temp > 20:
                score += 10
            
            # Drought frequency (up to 40 points)
            if drought_days > 60:
                score += 40
            elif drought_days > 40:
                score += 30
            elif drought_days > 20:
                score += 20
            elif drought_days > 10:
                score += 10
            
            # Regional boost for Brandenburg/East Germany (fire-prone)
            if 51.5 < lat < 53.5 and 12.0 < lng < 14.5:
                score += 15
                regional_factor = "Brandenburg - erhöhtes Waldbrandrisiko (Kiefernwälder)"
            else:
                regional_factor = None
            
            score = min(100, score)
            level = self._get_risk_level(score)
            
            factors = []
            if avg_summer_temp > 27:
                factors.append(f"Hohe Sommertemperaturen (Ø {avg_summer_temp:.1f}°C)")
            if drought_days > 30:
                factors.append(f"Häufige Trockenperioden ({drought_days:.0f} Tage/Jahr)")
            if regional_factor:
                factors.append(regional_factor)
            if not factors:
                factors.append("Moderate Waldbrandgefahr in der Region")
            
            recommendations = []
            if score >= 50:
                recommendations.extend([
                    "Brandschutzstreifen um Gebäude empfohlen",
                    "Keine Lagerung von brennbaren Materialien nahe am Haus",
                    "Waldbrandwarnstufen im Sommer beachten",
                ])
            else:
                recommendations.append("Standard-Brandschutzmaßnahmen ausreichend")
            
            result = FireRiskData(
                fire_weather_index=round(fwi, 1),
                avg_summer_temp=round(avg_summer_temp, 1),
                drought_days_per_year=round(drought_days, 1),
                fire_risk_score=score,
                fire_risk_level=level,
                factors=factors,
                recommendations=recommendations,
            )
            
            self._fire_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Fire risk analysis failed: {e}")
            return self._default_fire_risk()
    
    def _default_fire_risk(self) -> FireRiskData:
        return FireRiskData(
            fire_weather_index=0.0,
            avg_summer_temp=0.0,
            drought_days_per_year=0.0,
            fire_risk_score=15,
            fire_risk_level="Low",
            factors=["Deutschland hat generell niedriges Waldbrandrisiko"],
            recommendations=["Standard-Brandschutzmaßnahmen ausreichend"],
        )
    
    async def get_temperature_risk(self, lat: float, lng: float) -> TemperatureRiskData:
        """
        Analyze extreme temperature risk (heat waves and frost).
        """
        cache_key = self._cache_key(lat, lng)
        if cache_key in self._temp_cache:
            return self._temp_cache[cache_key]
        
        try:
            end_date = date.today() - timedelta(days=7)
            start_date = end_date - timedelta(days=5 * 365)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    self.ARCHIVE_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "temperature_2m_max,temperature_2m_min",
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            max_temps = [v for v in daily.get("temperature_2m_max", []) if v is not None]
            min_temps = [v for v in daily.get("temperature_2m_min", []) if v is not None]
            
            if not max_temps or not min_temps:
                return self._default_temp_risk()
            
            max_array = np.array(max_temps)
            min_array = np.array(min_temps)
            
            heat_wave_days = float(np.sum(max_array > 30)) / 5  # Days > 30°C per year
            extreme_heat = float(np.sum(max_array > 35)) / 5  # Days > 35°C per year
            frost_days = float(np.sum(min_array < 0)) / 5  # Frost days per year
            
            # Risk scoring
            score = 0
            
            # Heat risk (up to 50 points)
            if extreme_heat > 10:
                score += 50
            elif heat_wave_days > 30:
                score += 40
            elif heat_wave_days > 20:
                score += 30
            elif heat_wave_days > 10:
                score += 20
            elif heat_wave_days > 5:
                score += 10
            
            # Frost risk (up to 30 points)
            if frost_days > 100:
                score += 30
            elif frost_days > 80:
                score += 20
            elif frost_days > 60:
                score += 10
            
            # Extreme range bonus
            temp_range = float(np.max(max_array) - np.min(min_array))
            if temp_range > 60:
                score += 20
            elif temp_range > 50:
                score += 10
            
            score = min(100, score)
            level = self._get_risk_level(score)
            
            factors = []
            if heat_wave_days > 15:
                factors.append(f"Durchschnittlich {heat_wave_days:.0f} Hitzetage (>30°C) pro Jahr")
            if extreme_heat > 5:
                factors.append(f"Extremhitze (>35°C): {extreme_heat:.0f} Tage pro Jahr")
            if frost_days > 80:
                factors.append(f"Strenge Winter mit {frost_days:.0f} Frosttagen pro Jahr")
            if not factors:
                factors.append("Gemäßigtes Klima mit moderaten Temperaturextremen")
            
            recommendations = []
            if heat_wave_days > 20:
                recommendations.extend([
                    "Klimaanlage oder effektive Beschattung empfohlen",
                    "Auf gute Gebäudedämmung achten",
                ])
            if frost_days > 80:
                recommendations.extend([
                    "Frostsichere Wasserleitungen",
                    "Heizungsanlage auf kalte Winter auslegen",
                ])
            if not recommendations:
                recommendations.append("Standard-Gebäudeisolierung ausreichend")
            
            result = TemperatureRiskData(
                heat_wave_days_per_year=round(heat_wave_days, 1),
                frost_days_per_year=round(frost_days, 1),
                extreme_heat_days=round(extreme_heat, 1),
                temp_risk_score=score,
                temp_risk_level=level,
                factors=factors,
                recommendations=recommendations,
            )
            
            self._temp_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Temperature risk analysis failed: {e}")
            return self._default_temp_risk()
    
    def _default_temp_risk(self) -> TemperatureRiskData:
        return TemperatureRiskData(
            heat_wave_days_per_year=0.0,
            frost_days_per_year=0.0,
            extreme_heat_days=0.0,
            temp_risk_score=20,
            temp_risk_level="Low",
            factors=["Gemäßigtes mitteleuropäisches Klima"],
            recommendations=["Standard-Gebäudeisolierung ausreichend"],
        )
    
    async def get_hail_risk(self, lat: float, lng: float) -> HailRiskData:
        """
        Analyze thunderstorm/hail risk based on heavy precipitation patterns.
        """
        cache_key = self._cache_key(lat, lng)
        if cache_key in self._hail_cache:
            return self._hail_cache[cache_key]
        
        try:
            end_date = date.today() - timedelta(days=7)
            start_date = end_date - timedelta(days=5 * 365)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    self.ARCHIVE_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "precipitation_sum,precipitation_hours",
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            precip = [v for v in daily.get("precipitation_sum", []) if v is not None]
            precip_hours = [v for v in daily.get("precipitation_hours", []) if v is not None]
            
            if not precip:
                return self._default_hail_risk()
            
            precip_array = np.array(precip)
            
            # Heavy precipitation days (proxy for thunderstorms)
            heavy_days = float(np.sum(precip_array > 20)) / 5  # Days > 20mm
            extreme_days = float(np.sum(precip_array > 40)) / 5  # Days > 40mm
            
            # Precipitation intensity (mm per precipitation hour)
            if precip_hours:
                hours_array = np.array(precip_hours)
                valid_mask = hours_array > 0
                if np.any(valid_mask):
                    intensity = float(np.mean(precip_array[valid_mask] / hours_array[valid_mask]))
                else:
                    intensity = 0.0
            else:
                intensity = 0.0
            
            # Risk scoring
            score = 0
            
            # Heavy precipitation frequency (up to 50 points)
            if heavy_days > 20:
                score += 50
            elif heavy_days > 15:
                score += 40
            elif heavy_days > 10:
                score += 30
            elif heavy_days > 5:
                score += 20
            
            # Extreme events (up to 30 points)
            if extreme_days > 5:
                score += 30
            elif extreme_days > 3:
                score += 20
            elif extreme_days > 1:
                score += 10
            
            # Intensity (up to 20 points)
            if intensity > 5:
                score += 20
            elif intensity > 3:
                score += 10
            
            # Regional factors (Southern Germany has more hail)
            if 47.5 < lat < 49.5 and 9.0 < lng < 13.0:
                score += 10  # Bavaria/Alps
                regional_factor = "Süddeutschland - erhöhte Gewitteraktivität"
            else:
                regional_factor = None
            
            score = min(100, score)
            level = self._get_risk_level(score)
            
            factors = []
            if heavy_days > 10:
                factors.append(f"Häufige Starkniederschläge ({heavy_days:.0f} Tage/Jahr mit >20mm)")
            if extreme_days > 2:
                factors.append(f"Extreme Niederschlagsereignisse ({extreme_days:.0f} Tage/Jahr mit >40mm)")
            if regional_factor:
                factors.append(regional_factor)
            if not factors:
                factors.append("Moderate Gewitteraktivität in der Region")
            
            recommendations = []
            if score >= 50:
                recommendations.extend([
                    "Hagelschutz für Fahrzeuge und empfindliche Außenbereiche",
                    "Elementarschadenversicherung empfohlen",
                    "Entwässerungssystem auf Starkregen auslegen",
                ])
            elif score >= 30:
                recommendations.append("Elementarschadenversicherung in Betracht ziehen")
            else:
                recommendations.append("Standard-Versicherungsschutz ausreichend")
            
            result = HailRiskData(
                heavy_precip_days=round(heavy_days, 1),
                avg_summer_precip_intensity=round(intensity, 2),
                hail_risk_score=score,
                hail_risk_level=level,
                factors=factors,
                recommendations=recommendations,
            )
            
            self._hail_cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Hail risk analysis failed: {e}")
            return self._default_hail_risk()
    
    def _default_hail_risk(self) -> HailRiskData:
        return HailRiskData(
            heavy_precip_days=0.0,
            avg_summer_precip_intensity=0.0,
            hail_risk_score=20,
            hail_risk_level="Low",
            factors=["Moderate Gewitteraktivität in Deutschland"],
            recommendations=["Standard-Versicherungsschutz ausreichend"],
        )
    
    def get_earthquake_risk(self, lat: float, lng: float) -> EarthquakeRiskData:
        """Get earthquake zone risk for location."""
        return get_earthquake_zone(lat, lng)
    
    async def analyze_all_risks(
        self, 
        lat: float, 
        lng: float,
        flood_data: Optional[dict] = None
    ) -> ComprehensiveRiskData:
        """
        Perform comprehensive natural disaster risk analysis.
        
        Args:
            lat: Latitude
            lng: Longitude
            flood_data: Existing flood risk data (to avoid re-fetching)
            
        Returns:
            ComprehensiveRiskData with all risk categories.
        """
        import asyncio
        
        # Fetch all weather-based risks in parallel
        storm_task = self.get_storm_risk(lat, lng)
        fire_task = self.get_fire_risk(lat, lng)
        temp_task = self.get_temperature_risk(lat, lng)
        hail_task = self.get_hail_risk(lat, lng)
        
        storm, fire, temp, hail = await asyncio.gather(
            storm_task, fire_task, temp_task, hail_task
        )
        
        # Earthquake is synchronous (static lookup)
        earthquake = self.get_earthquake_risk(lat, lng)
        
        # Calculate total weighted risk score
        # Weights based on frequency and impact in Germany
        weights = {
            "flood": 0.30,      # Most common and damaging
            "storm": 0.25,      # Winter storms frequent
            "temperature": 0.15,  # Increasing with climate change
            "hail": 0.15,       # Seasonal but impactful
            "fire": 0.10,       # Regional, less common
            "earthquake": 0.05,  # Very rare in Germany
        }
        
        flood_score = flood_data.get("risk_score", 30) if flood_data else 30
        
        total_score = int(
            flood_score * weights["flood"] +
            storm["storm_risk_score"] * weights["storm"] +
            temp["temp_risk_score"] * weights["temperature"] +
            hail["hail_risk_score"] * weights["hail"] +
            fire["fire_risk_score"] * weights["fire"] +
            earthquake["earthquake_risk_score"] * weights["earthquake"]
        )
        
        total_score = min(100, max(0, total_score))
        
        # Determine overall level
        if total_score >= 60:
            total_level = "High"
        elif total_score >= 35:
            total_level = "Medium"
        else:
            total_level = "Low"
        
        # Identify primary risks (top 3 by score)
        risk_scores = [
            ("Hochwasser", flood_score),
            ("Sturm", storm["storm_risk_score"]),
            ("Extremtemperaturen", temp["temp_risk_score"]),
            ("Gewitter/Hagel", hail["hail_risk_score"]),
            ("Waldbrand", fire["fire_risk_score"]),
            ("Erdbeben", earthquake["earthquake_risk_score"]),
        ]
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        primary_risks = [r[0] for r in risk_scores[:3] if r[1] >= 25]
        
        return ComprehensiveRiskData(
            flood_risk=flood_data or {"risk_score": 30, "risk_level": "Low"},
            storm_risk=storm,
            fire_risk=fire,
            temperature_risk=temp,
            hail_risk=hail,
            earthquake_risk=earthquake,
            total_risk_score=total_score,
            total_risk_level=total_level,
            primary_risks=primary_risks,
        )


# Utility to clear caches
def clear_natural_disaster_caches() -> None:
    """Clear all natural disaster service caches."""
    NaturalDisasterService._storm_cache.clear()
    NaturalDisasterService._fire_cache.clear()
    NaturalDisasterService._temp_cache.clear()
    NaturalDisasterService._hail_cache.clear()
    logger.info("Natural disaster caches cleared")
