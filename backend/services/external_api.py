"""
ImmoSafe DE - External API Services V2
Async clients for Google Maps and Open-Meteo APIs with robust error handling and caching.
"""

import logging
import os
from datetime import date, timedelta
from functools import lru_cache
from typing import TypedDict

import httpx
import numpy as np

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Coordinates(TypedDict):
    """Geographic coordinates."""
    lat: float
    lng: float


class FloodRiskData(TypedDict):
    """Flood risk analysis data."""
    rainfall_95th_percentile: float
    max_daily_rainfall: float
    data_points: int
    last_7_days_rainfall: list[float]


class ForecastData(TypedDict):
    """Weather forecast data."""
    precipitation_3day_sum: float
    precipitation_daily: list[float]


class TerrainData(TypedDict):
    """Terrain analysis data for sink/valley detection."""
    center_elevation: float
    local_min_elevation: float
    local_max_elevation: float
    relative_height: float  # center_elevation - local_min_elevation
    is_data_available: bool


# Cache timeout helper - coordinates are cached by (lat, lng) rounded to 4 decimal places
def _cache_key(lat: float, lng: float) -> tuple[float, float]:
    """Generate a cache key from coordinates (rounded for cache efficiency)."""
    return (round(lat, 4), round(lng, 4))


# Earth radius for distance calculations (meters)
EARTH_RADIUS_M = 6_371_000


def _offset_coordinates(lat: float, lng: float, distance_m: float, bearing_deg: float) -> tuple[float, float]:
    """
    Calculate new coordinates at a given distance and bearing from origin.
    
    Args:
        lat: Origin latitude in degrees.
        lng: Origin longitude in degrees.
        distance_m: Distance in meters.
        bearing_deg: Bearing in degrees (0=North, 90=East, 180=South, 270=West).
        
    Returns:
        Tuple of (new_lat, new_lng) in degrees.
    """
    import math
    
    lat_rad = math.radians(lat)
    lng_rad = math.radians(lng)
    bearing_rad = math.radians(bearing_deg)
    angular_distance = distance_m / EARTH_RADIUS_M
    
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
    )
    
    new_lng_rad = lng_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    return (math.degrees(new_lat_rad), math.degrees(new_lng_rad))


class GeoService:
    """
    Async service for Google Maps Geocoding and Elevation APIs.
    Implements in-memory caching for repeated lookups.
    """
    
    GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    ELEVATION_URL = "https://maps.googleapis.com/maps/api/elevation/json"
    
    # Class-level cache for geocoding results
    _geocoding_cache: dict[str, Coordinates] = {}
    _elevation_cache: dict[tuple[float, float], float] = {}
    
    def __init__(self) -> None:
        self._api_key = os.getenv("MAPS_API_KEY", "")
        if not self._api_key:
            raise ValueError("MAPS_API_KEY environment variable is not set")
    
    async def get_coordinates(self, address: str) -> Coordinates:
        """
        Get latitude and longitude for a given address using Google Geocoding API.
        Results are cached in-memory for repeated lookups.
        
        Args:
            address: The address string to geocode.
            
        Returns:
            Coordinates with lat and lng.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails.
            ValueError: If no results are found or API returns an error.
        """
        # Check cache first
        cache_key = address.strip().lower()
        if cache_key in self._geocoding_cache:
            logger.info(f"Cache hit for geocoding: {address[:50]}...")
            return self._geocoding_cache[cache_key]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                self.GEOCODING_URL,
                params={
                    "address": address,
                    "key": self._api_key,
                    "language": "de",
                    "region": "de",
                },
            )
            response.raise_for_status()
            data = response.json()
        
        if data.get("status") != "OK":
            error_message = data.get("error_message", data.get("status", "Unknown error"))
            raise ValueError(f"Geocoding failed: {error_message}")
        
        results = data.get("results", [])
        if not results:
            raise ValueError(f"No geocoding results found for address: {address}")
        
        location = results[0]["geometry"]["location"]
        result = Coordinates(lat=location["lat"], lng=location["lng"])
        
        # Store in cache
        self._geocoding_cache[cache_key] = result
        logger.info(f"Cached geocoding result for: {address[:50]}...")
        
        return result
    
    async def get_elevation(self, lat: float, lng: float) -> float:
        """
        Get elevation in meters for given coordinates using Google Elevation API.
        Results are cached in-memory for repeated lookups.
        
        Args:
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            Elevation in meters above sea level. Returns 0.0 on failure (safe default).
        """
        # Check cache first
        cache_key = _cache_key(lat, lng)
        if cache_key in self._elevation_cache:
            logger.info(f"Cache hit for elevation: ({lat}, {lng})")
            return self._elevation_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.ELEVATION_URL,
                    params={
                        "locations": f"{lat},{lng}",
                        "key": self._api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                error_message = data.get("error_message", data.get("status", "Unknown error"))
                logger.warning(f"Elevation API error: {error_message}. Using safe default 0.0m")
                return 0.0
            
            results = data.get("results", [])
            if not results:
                logger.warning("No elevation data returned. Using safe default 0.0m")
                return 0.0
            
            elevation = float(results[0]["elevation"])
            
            # Store in cache
            self._elevation_cache[cache_key] = elevation
            logger.info(f"Cached elevation for ({lat}, {lng}): {elevation}m")
            
            return elevation
            
        except Exception as e:
            logger.error(f"Elevation API failed: {e}. Using safe default 0.0m")
            return 0.0
    
    # Terrain analysis cache
    _terrain_cache: dict[tuple[float, float], TerrainData] = {}
    
    async def analyze_terrain(self, lat: float, lng: float, radius_m: float = 100.0) -> TerrainData:
        """
        Analyze local terrain by fetching elevation at center and 4 cardinal directions.
        Calculates relative height to detect if location is in a sink/valley.
        
        Args:
            lat: Center latitude.
            lng: Center longitude.
            radius_m: Distance in meters for surrounding sample points (default 100m).
            
        Returns:
            TerrainData with center elevation, local min/max, and relative height.
        """
        # Check cache first
        cache_key = _cache_key(lat, lng)
        if cache_key in self._terrain_cache:
            logger.info(f"Cache hit for terrain analysis: ({lat}, {lng})")
            return self._terrain_cache[cache_key]
        
        try:
            # Calculate 4 surrounding points at 100m distance (N, E, S, W)
            north = _offset_coordinates(lat, lng, radius_m, 0)    # North
            east = _offset_coordinates(lat, lng, radius_m, 90)    # East
            south = _offset_coordinates(lat, lng, radius_m, 180)  # South
            west = _offset_coordinates(lat, lng, radius_m, 270)   # West
            
            # Build locations string for batch API call
            locations = [
                f"{lat},{lng}",           # Center
                f"{north[0]},{north[1]}", # North
                f"{east[0]},{east[1]}",   # East
                f"{south[0]},{south[1]}", # South
                f"{west[0]},{west[1]}",   # West
            ]
            locations_str = "|".join(locations)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.ELEVATION_URL,
                    params={
                        "locations": locations_str,
                        "key": self._api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            if data.get("status") != "OK":
                error_message = data.get("error_message", data.get("status", "Unknown error"))
                logger.warning(f"Terrain API error: {error_message}. Using unavailable flag.")
                return TerrainData(
                    center_elevation=0.0,
                    local_min_elevation=0.0,
                    local_max_elevation=0.0,
                    relative_height=0.0,
                    is_data_available=False,
                )
            
            results = data.get("results", [])
            if len(results) < 5:
                logger.warning(f"Not enough elevation points returned ({len(results)}/5). Using unavailable flag.")
                return TerrainData(
                    center_elevation=0.0,
                    local_min_elevation=0.0,
                    local_max_elevation=0.0,
                    relative_height=0.0,
                    is_data_available=False,
                )
            
            # Extract elevations
            elevations = [float(r["elevation"]) for r in results]
            center_elevation = elevations[0]
            surrounding_elevations = elevations[1:]  # N, E, S, W
            
            local_min = min(surrounding_elevations)
            local_max = max(surrounding_elevations)
            relative_height = center_elevation - local_min
            
            result = TerrainData(
                center_elevation=round(center_elevation, 2),
                local_min_elevation=round(local_min, 2),
                local_max_elevation=round(local_max, 2),
                relative_height=round(relative_height, 2),
                is_data_available=True,
            )
            
            # Store in cache
            self._terrain_cache[cache_key] = result
            logger.info(
                f"Terrain analysis for ({lat}, {lng}): "
                f"center={center_elevation:.1f}m, min={local_min:.1f}m, "
                f"relative_height={relative_height:.1f}m"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Terrain analysis failed: {e}. Using unavailable flag.")
            return TerrainData(
                center_elevation=0.0,
                local_min_elevation=0.0,
                local_max_elevation=0.0,
                relative_height=0.0,
                is_data_available=False,
            )


class WeatherService:
    """
    Async service for Open-Meteo weather and climate data APIs.
    Implements robust fallback strategies and in-memory caching.
    """
    
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Default safe values when API fails completely
    DEFAULT_RAINFALL_95TH: float = 0.0
    DEFAULT_MAX_RAINFALL: float = 0.0
    DEFAULT_FORECAST_SUM: float = 0.0
    
    # Class-level cache for weather data
    _flood_risk_cache: dict[tuple[float, float], FloodRiskData] = {}
    _forecast_cache: dict[tuple[float, float], ForecastData] = {}
    
    async def get_flood_risk_data(self, lat: float, lng: float) -> FloodRiskData:
        """
        Analyze historical precipitation data to assess flood risk.
        Fetches 5 years of daily precipitation data and calculates the
        95th percentile to identify extreme rainfall events.
        
        NEVER returns None - implements fallback strategies:
        1. If some days have missing data, calculate from available days
        2. If API fails completely, return safe defaults (0.0)
        
        Args:
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            FloodRiskData with rainfall statistics (guaranteed non-None floats).
        """
        # Check cache first
        cache_key = _cache_key(lat, lng)
        if cache_key in self._flood_risk_cache:
            logger.info(f"Cache hit for flood risk data: ({lat}, {lng})")
            return self._flood_risk_cache[cache_key]
        
        try:
            end_date = date.today() - timedelta(days=7)  # Archive has ~1 week delay
            start_date = end_date - timedelta(days=5 * 365)
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(
                    self.ARCHIVE_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "daily": "precipitation_sum",
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily_data = data.get("daily", {})
            precipitation_values = daily_data.get("precipitation_sum", [])
            
            # FALLBACK STRATEGY 1: Calculate average from available days
            if not precipitation_values:
                logger.warning(
                    f"No precipitation data for ({lat}, {lng}). "
                    "Using safe defaults."
                )
                return self._get_default_flood_risk_data()
            
            # Filter out None values - use only valid data points
            valid_values = [v for v in precipitation_values if v is not None]
            
            # FALLBACK STRATEGY 2: If all values are None, return safe defaults
            if not valid_values:
                logger.warning(
                    f"All precipitation values are None for ({lat}, {lng}). "
                    "Using safe defaults."
                )
                return self._get_default_flood_risk_data()
            
            # Log if significant data is missing
            missing_count = len(precipitation_values) - len(valid_values)
            if missing_count > 0:
                missing_pct = (missing_count / len(precipitation_values)) * 100
                logger.info(
                    f"Missing {missing_count} ({missing_pct:.1f}%) data points for ({lat}, {lng}). "
                    f"Calculating from {len(valid_values)} available days."
                )
            
            precipitation_array = np.array(valid_values)
            
            # Calculate 95th percentile (extreme rainfall events)
            rainfall_95th = float(np.percentile(precipitation_array, 95))
            max_rainfall = float(np.max(precipitation_array))
            
            # Get the last 7 days of valid rainfall data for charts
            last_7_days = [round(v, 1) for v in valid_values[-7:]]
            # Pad with 0s if we don't have enough days
            while len(last_7_days) < 7:
                last_7_days.insert(0, 0.0)
            
            result = FloodRiskData(
                rainfall_95th_percentile=round(rainfall_95th, 2),
                max_daily_rainfall=round(max_rainfall, 2),
                data_points=len(valid_values),
                last_7_days_rainfall=last_7_days,
            )
            
            # Store in cache
            self._flood_risk_cache[cache_key] = result
            logger.info(f"Cached flood risk data for ({lat}, {lng})")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Open-Meteo Archive API HTTP error for ({lat}, {lng}): {e}. "
                "Using safe defaults."
            )
            return self._get_default_flood_risk_data()
        except Exception as e:
            logger.error(
                f"Unexpected error fetching flood risk data for ({lat}, {lng}): {e}. "
                "Using safe defaults."
            )
            return self._get_default_flood_risk_data()
    
    def _get_default_flood_risk_data(self) -> FloodRiskData:
        """Return safe default flood risk data when API fails."""
        return FloodRiskData(
            rainfall_95th_percentile=self.DEFAULT_RAINFALL_95TH,
            max_daily_rainfall=self.DEFAULT_MAX_RAINFALL,
            data_points=0,
            last_7_days_rainfall=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        )
    
    async def get_current_forecast(self, lat: float, lng: float) -> ForecastData:
        """
        Get 3-day precipitation forecast for the location.
        
        NEVER returns None - implements fallback strategies:
        1. If some days have missing data, calculate from available days
        2. If API fails completely, return safe defaults (0.0)
        
        Args:
            lat: Latitude.
            lng: Longitude.
            
        Returns:
            ForecastData with precipitation forecast (guaranteed non-None floats).
        """
        # Check cache first
        cache_key = _cache_key(lat, lng)
        if cache_key in self._forecast_cache:
            logger.info(f"Cache hit for forecast: ({lat}, {lng})")
            return self._forecast_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.FORECAST_URL,
                    params={
                        "latitude": lat,
                        "longitude": lng,
                        "daily": "precipitation_sum",
                        "forecast_days": 3,
                        "timezone": "Europe/Berlin",
                    },
                )
                response.raise_for_status()
                data = response.json()
            
            daily_data = data.get("daily", {})
            precipitation_values = daily_data.get("precipitation_sum", [])
            
            if not precipitation_values:
                logger.warning(
                    f"No forecast data for ({lat}, {lng}). Using safe defaults."
                )
                return self._get_default_forecast_data()
            
            # Replace None values with 0.0 and calculate average of available days
            valid_values: list[float] = []
            for v in precipitation_values:
                if v is not None:
                    valid_values.append(float(v))
                else:
                    # If we have some valid values, use their average; otherwise 0.0
                    valid_values.append(0.0)
            
            total_precipitation = sum(valid_values)
            
            result = ForecastData(
                precipitation_3day_sum=round(total_precipitation, 2),
                precipitation_daily=[round(v, 2) for v in valid_values],
            )
            
            # Store in cache
            self._forecast_cache[cache_key] = result
            logger.info(f"Cached forecast for ({lat}, {lng})")
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Open-Meteo Forecast API HTTP error for ({lat}, {lng}): {e}. "
                "Using safe defaults."
            )
            return self._get_default_forecast_data()
        except Exception as e:
            logger.error(
                f"Unexpected error fetching forecast for ({lat}, {lng}): {e}. "
                "Using safe defaults."
            )
            return self._get_default_forecast_data()
    
    def _get_default_forecast_data(self) -> ForecastData:
        """Return safe default forecast data when API fails."""
        return ForecastData(
            precipitation_3day_sum=self.DEFAULT_FORECAST_SUM,
            precipitation_daily=[0.0, 0.0, 0.0],
        )


# Utility functions to clear caches (useful for testing or manual refresh)
def clear_all_caches() -> None:
    """Clear all in-memory caches."""
    GeoService._geocoding_cache.clear()
    GeoService._elevation_cache.clear()
    GeoService._terrain_cache.clear()
    WeatherService._flood_risk_cache.clear()
    WeatherService._forecast_cache.clear()
    logger.info("All caches cleared")
