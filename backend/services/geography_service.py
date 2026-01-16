"""
ImmoSafe DE - Advanced Geography Service
Enhanced topographical analysis and risk factor identification.
"""

import logging
import math
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class GeographyService:
    """Advanced geographical analysis for risk assessment."""

    # Major rivers and water bodies in Germany with coordinates
    MAJOR_WATER_BODIES = {
        "Rhein": [(51.0, 6.96), (50.94, 6.96), (50.73, 7.09), (50.08, 8.24), (49.01, 8.40)],
        "Elbe": [(53.87, 10.69), (53.47, 10.07), (52.88, 11.07), (51.86, 12.39), (51.05, 13.74)],
        "Donau": [(48.63, 9.17), (48.57, 10.89), (48.58, 12.14), (48.57, 13.46)],
        "Main": [(50.00, 8.27), (50.04, 8.57), (49.93, 9.13), (50.00, 10.23)],
        "Weser": [(52.50, 9.50), (52.75, 9.13), (53.08, 8.81), (53.47, 8.58)],
        "Oder": [(52.93, 14.55), (52.54, 14.55), (52.23, 14.55)],
        "Neckar": [(49.42, 8.68), (48.78, 9.18)],
        "Mosel": [(50.36, 7.60), (49.97, 6.64)],
        "Isar": [(48.14, 11.57), (48.79, 12.15)],
        "Ahr": [(50.54, 7.11), (50.51, 6.95)],
    }

    # Known flood plains and high-risk areas
    FLOOD_PLAINS = [
        {"name": "Rheintal", "center": (51.0, 6.96), "radius_km": 20, "risk_multiplier": 1.5},
        {"name": "Elbtal Dresden", "center": (51.05, 13.74), "radius_km": 15, "risk_multiplier": 1.4},
        {"name": "Donau Passau", "center": (48.57, 13.46), "radius_km": 10, "risk_multiplier": 1.6},
        {"name": "Ahr-Tal", "center": (50.54, 7.11), "radius_km": 8, "risk_multiplier": 2.0},  # 2021 flood
    ]

    # Known high-risk wildfire areas
    WILDFIRE_ZONES = [
        {"name": "Brandenburg", "center": (52.4, 13.0), "radius_km": 80, "risk_multiplier": 1.8},
        {"name": "Sächsische Schweiz", "center": (50.88, 14.27), "radius_km": 30, "risk_multiplier": 1.5},
        {"name": "Harz", "center": (51.75, 10.62), "radius_km": 40, "risk_multiplier": 1.3},
    ]

    # Coastal areas (high storm risk)
    COASTAL_AREAS = [
        {"name": "Nordseeküste", "center": (53.8, 8.5), "radius_km": 50, "storm_multiplier": 1.5},
        {"name": "Ostseeküste", "center": (54.1, 13.5), "radius_km": 40, "storm_multiplier": 1.4},
    ]

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees).
        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

    @staticmethod
    def get_nearest_river(lat: float, lng: float) -> Optional[Dict]:
        """Find the nearest major river to the given coordinates."""
        nearest_river = None
        min_distance = float('inf')

        for river_name, coordinates in GeographyService.MAJOR_WATER_BODIES.items():
            for river_lat, river_lng in coordinates:
                distance = GeographyService.haversine_distance(lat, lng, river_lat, river_lng)
                if distance < min_distance:
                    min_distance = distance
                    nearest_river = {
                        "name": river_name,
                        "distance_km": round(distance, 2)
                    }

        return nearest_river

    @staticmethod
    def is_in_flood_plain(lat: float, lng: float) -> Dict:
        """Check if location is in a known flood plain."""
        for plain in GeographyService.FLOOD_PLAINS:
            distance = GeographyService.haversine_distance(
                lat, lng,
                plain["center"][0], plain["center"][1]
            )
            if distance <= plain["radius_km"]:
                return {
                    "in_flood_plain": True,
                    "name": plain["name"],
                    "distance_km": round(distance, 2),
                    "risk_multiplier": plain["risk_multiplier"]
                }

        return {"in_flood_plain": False}

    @staticmethod
    def is_in_wildfire_zone(lat: float, lng: float) -> Dict:
        """Check if location is in a high-risk wildfire zone."""
        for zone in GeographyService.WILDFIRE_ZONES:
            distance = GeographyService.haversine_distance(
                lat, lng,
                zone["center"][0], zone["center"][1]
            )
            if distance <= zone["radius_km"]:
                return {
                    "in_wildfire_zone": True,
                    "name": zone["name"],
                    "distance_km": round(distance, 2),
                    "risk_multiplier": zone["risk_multiplier"]
                }

        return {"in_wildfire_zone": False}

    @staticmethod
    def is_coastal_area(lat: float, lng: float) -> Dict:
        """Check if location is in a coastal area with high storm risk."""
        for area in GeographyService.COASTAL_AREAS:
            distance = GeographyService.haversine_distance(
                lat, lng,
                area["center"][0], area["center"][1]
            )
            if distance <= area["radius_km"]:
                return {
                    "is_coastal": True,
                    "name": area["name"],
                    "distance_km": round(distance, 2),
                    "storm_multiplier": area["storm_multiplier"]
                }

        return {"is_coastal": False}

    @staticmethod
    def analyze_elevation_context(elevation: float, relative_height: float) -> Dict:
        """Analyze elevation in context for flood/landslide risk."""
        context = {
            "elevation_category": "",
            "flood_risk_factor": 1.0,
            "landslide_risk": False,
            "description": ""
        }

        if elevation < 50:
            context["elevation_category"] = "Tiefland"
            context["flood_risk_factor"] = 1.5
            context["description"] = "Sehr niedrige Lage mit erhöhtem Hochwasserrisiko"
        elif elevation < 100:
            context["elevation_category"] = "Flachland"
            context["flood_risk_factor"] = 1.2
            context["description"] = "Niedrige Lage mit mäßigem Hochwasserrisiko"
        elif elevation < 300:
            context["elevation_category"] = "Hügelland"
            context["flood_risk_factor"] = 0.8
            context["description"] = "Erhöhte Lage mit geringem Hochwasserrisiko"
        elif elevation < 800:
            context["elevation_category"] = "Mittelgebirge"
            context["flood_risk_factor"] = 0.5
            context["landslide_risk"] = True
            context["description"] = "Bergige Lage - geringes Hochwasser-, erhöhtes Hangrutschrisiko"
        else:
            context["elevation_category"] = "Hochgebirge"
            context["flood_risk_factor"] = 0.3
            context["landslide_risk"] = True
            context["description"] = "Hochgebirgslage - Lawinengefahr im Winter"

        # Consider relative height (terrain depression)
        if relative_height < -2:
            context["in_depression"] = True
            context["flood_risk_factor"] *= 1.4
            context["description"] += " | Senke: Stark erhöhtes Überflutungsrisiko"
        elif relative_height < 0:
            context["in_depression"] = True
            context["flood_risk_factor"] *= 1.2
            context["description"] += " | Leichte Senke: Erhöhtes Überflutungsrisiko"

        return context

    @staticmethod
    def get_state_from_coordinates(lat: float, lng: float) -> str:
        """Approximate German state from coordinates."""
        # Simplified state boundaries
        if lat > 54.5:
            return "SH"  # Schleswig-Holstein
        elif lat > 53.5 and lng < 11:
            return "HH"  # Hamburg
        elif lat > 53 and lng < 12:
            return "NI"  # Niedersachsen
        elif lat > 53 and lng > 12:
            return "MV"  # Mecklenburg-Vorpommern
        elif lat > 52 and lng < 11:
            return "NI"  # Niedersachsen
        elif lat > 52 and lng > 13:
            return "BB"  # Brandenburg
        elif lat > 51.5 and lng > 13.3 and lng < 13.5:
            return "BE"  # Berlin
        elif lat > 51 and lng > 12:
            return "SN"  # Sachsen
        elif lat > 51 and lng < 11:
            return "ST"  # Sachsen-Anhalt
        elif lat > 50 and lng < 8:
            return "NW"  # Nordrhein-Westfalen
        elif lat > 49.5 and lng < 10:
            return "HE"  # Hessen
        elif lat > 49 and lng > 12:
            return "BY"  # Bayern
        elif lat > 48 and lng < 9:
            return "BW"  # Baden-Württemberg
        elif lat > 47:
            return "BY"  # Bayern
        else:
            return "DE"  # Germany (unknown state)

    @staticmethod
    def get_comprehensive_location_analysis(lat: float, lng: float, elevation: float, relative_height: float) -> Dict:
        """Get comprehensive geographical analysis for a location."""
        nearest_river = GeographyService.get_nearest_river(lat, lng)
        flood_plain = GeographyService.is_in_flood_plain(lat, lng)
        wildfire_zone = GeographyService.is_in_wildfire_zone(lat, lng)
        coastal = GeographyService.is_coastal_area(lat, lng)
        elevation_context = GeographyService.analyze_elevation_context(elevation, relative_height)
        state_code = GeographyService.get_state_from_coordinates(lat, lng)

        return {
            "state_code": state_code,
            "nearest_river": nearest_river,
            "flood_plain": flood_plain,
            "wildfire_zone": wildfire_zone,
            "coastal": coastal,
            "elevation_context": elevation_context,
            "coordinates": {"lat": lat, "lng": lng}
        }
