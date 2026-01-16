"""
ImmoSafe DE - Historical Disaster Events Database
Comprehensive database of historical natural disasters in Germany.
"""

from datetime import datetime
from typing import List, Dict, Optional


class HistoricalEventsDB:
    """Database of historical natural disaster events in Germany."""

    # Major flood events in Germany
    FLOOD_EVENTS = {
        "Elbe": [
            {"year": 2002, "location": "Elbe-Region (Dresden, Meißen)", "damage_eur": 9_000_000_000, "severity": "Jahrhunderthochwasser"},
            {"year": 2013, "location": "Elbe, Donau, Saale", "damage_eur": 8_000_000_000, "severity": "Extrem"},
            {"year": 2006, "location": "Elbe", "damage_eur": 500_000_000, "severity": "Hoch"},
        ],
        "Rhein": [
            {"year": 1993, "location": "Rheinland (Köln, Bonn)", "damage_eur": 500_000_000, "severity": "Weihnachtshochwasser"},
            {"year": 1995, "location": "Rhein", "damage_eur": 300_000_000, "severity": "Hoch"},
            {"year": 2021, "location": "Ahr-Tal, Rheinland-Pfalz", "damage_eur": 30_000_000_000, "severity": "Katastrophal"},
        ],
        "Donau": [
            {"year": 1999, "location": "Donau (Passau)", "damage_eur": 200_000_000, "severity": "Pfingsthochwasser"},
            {"year": 2013, "location": "Donau (Passau, Deggendorf)", "damage_eur": 2_000_000_000, "severity": "Jahrhunderthochwasser"},
            {"year": 2016, "location": "Donau, Isar", "damage_eur": 100_000_000, "severity": "Mittel"},
        ],
        "Oder": [
            {"year": 1997, "location": "Oder (Brandenburg)", "damage_eur": 300_000_000, "severity": "Oderhochwasser"},
            {"year": 2010, "location": "Oder", "damage_eur": 50_000_000, "severity": "Mittel"},
        ],
        "Starkregen": [
            {"year": 2016, "location": "Bayern, Baden-Württemberg", "damage_eur": 1_500_000_000, "severity": "Starkregen-Katastrophe"},
            {"year": 2021, "location": "Nordrhein-Westfalen, Rheinland-Pfalz", "damage_eur": 30_000_000_000, "severity": "Jahrhundertflut"},
        ]
    }

    # Major storm events
    STORM_EVENTS = [
        {"year": 1999, "name": "Lothar", "location": "Süddeutschland, Baden-Württemberg", "wind_kmh": 272, "damage_eur": 13_000_000_000},
        {"year": 2007, "name": "Kyrill", "location": "Gesamtdeutschland", "wind_kmh": 225, "damage_eur": 6_000_000_000},
        {"year": 2010, "name": "Xynthia", "location": "Norddeutschland", "wind_kmh": 180, "damage_eur": 500_000_000},
        {"year": 2017, "name": "Xavier", "location": "Norddeutschland", "wind_kmh": 190, "damage_eur": 1_000_000_000},
        {"year": 2018, "name": "Friederike", "location": "Westdeutschland", "wind_kmh": 203, "damage_eur": 900_000_000},
        {"year": 2020, "name": "Sabine", "location": "Gesamtdeutschland", "wind_kmh": 177, "damage_eur": 500_000_000},
        {"year": 2022, "name": "Zeynep", "location": "Nord- und Ostdeutschland", "wind_kmh": 156, "damage_eur": 900_000_000},
    ]

    # Earthquake events
    EARTHQUAKE_EVENTS = [
        {"year": 1992, "location": "Roermond (Niederrhein)", "magnitude": 5.9, "damage_eur": 150_000_000},
        {"year": 2004, "location": "Waldkirch (Schwarzwald)", "magnitude": 5.4, "damage_eur": 5_000_000},
        {"year": 2011, "location": "Gera (Thüringen)", "magnitude": 3.0, "damage_eur": 100_000},
        {"year": 2016, "location": "Albstadt (Schwäbische Alb)", "magnitude": 3.7, "damage_eur": 500_000},
        {"year": 2021, "location": "Überlingen (Bodensee)", "magnitude": 3.7, "damage_eur": 200_000},
    ]

    # Wildfire events
    WILDFIRE_EVENTS = [
        {"year": 2018, "location": "Brandenburg (Jüterbog)", "area_ha": 400, "damage_eur": 3_000_000},
        {"year": 2019, "location": "Brandenburg (Lübtheen)", "area_ha": 1_000, "damage_eur": 10_000_000},
        {"year": 2022, "location": "Sächsische Schweiz", "area_ha": 1_100, "damage_eur": 50_000_000},
        {"year": 2018, "location": "Harz", "area_ha": 50, "damage_eur": 500_000},
        {"year": 2019, "location": "Bayern", "area_ha": 30, "damage_eur": 300_000},
    ]

    # Hail events
    HAIL_EVENTS = [
        {"year": 2013, "location": "Niedersachsen, Thüringen", "size_cm": 10, "damage_eur": 3_800_000_000},
        {"year": 2022, "location": "Baden-Württemberg", "size_cm": 8, "damage_eur": 500_000_000},
        {"year": 2019, "location": "Bayern, Baden-Württemberg", "size_cm": 6, "damage_eur": 200_000_000},
        {"year": 2021, "location": "Nordrhein-Westfalen", "size_cm": 7, "damage_eur": 100_000_000},
    ]

    # Snow load events
    SNOW_EVENTS = [
        {"year": 2005, "location": "Alpen, Südbayern", "snow_cm": 300, "damage_eur": 500_000_000},
        {"year": 2006, "location": "Bayern, Baden-Württemberg", "snow_cm": 250, "damage_eur": 300_000_000},
        {"year": 2019, "location": "Alpenraum", "snow_cm": 350, "damage_eur": 1_000_000_000},
    ]

    # Major rivers in Germany with flood risk
    MAJOR_RIVERS = {
        "Rhein": {"risk_level": "Sehr hoch", "avg_floods_per_decade": 3, "states": ["NRW", "RP", "BW", "HE"]},
        "Elbe": {"risk_level": "Hoch", "avg_floods_per_decade": 2, "states": ["SN", "ST", "BB", "SH", "HH"]},
        "Donau": {"risk_level": "Hoch", "avg_floods_per_decade": 2, "states": ["BY", "BW"]},
        "Main": {"risk_level": "Mittel", "avg_floods_per_decade": 1, "states": ["BY", "HE"]},
        "Neckar": {"risk_level": "Mittel", "avg_floods_per_decade": 1, "states": ["BW"]},
        "Mosel": {"risk_level": "Mittel", "avg_floods_per_decade": 1, "states": ["RP"]},
        "Weser": {"risk_level": "Mittel", "avg_floods_per_decade": 1, "states": ["NI", "HB", "NW"]},
        "Oder": {"risk_level": "Hoch", "avg_floods_per_decade": 2, "states": ["BB"]},
        "Ahr": {"risk_level": "Sehr hoch", "avg_floods_per_decade": 4, "states": ["RP"]},
        "Isar": {"risk_level": "Mittel", "avg_floods_per_decade": 1, "states": ["BY"]},
    }

    @staticmethod
    def get_flood_events_for_region(state_code: str, river_nearby: Optional[str] = None) -> List[Dict]:
        """Get relevant flood events for a region."""
        events = []

        # Check each river's events
        for river_name, river_events in HistoricalEventsDB.FLOOD_EVENTS.items():
            river_info = HistoricalEventsDB.MAJOR_RIVERS.get(river_name)
            if river_info and state_code in river_info["states"]:
                events.extend(river_events)

        # Sort by year (most recent first)
        events.sort(key=lambda x: x["year"], reverse=True)

        return events[:5]  # Return top 5 most recent

    @staticmethod
    def get_storm_events_for_region(lat: float, lng: float) -> List[Dict]:
        """Get relevant storm events for a region."""
        # North Germany (high storm risk)
        if lat > 52.5:
            return HistoricalEventsDB.STORM_EVENTS[:5]
        # Central Germany
        elif lat > 50:
            return [e for e in HistoricalEventsDB.STORM_EVENTS if e["year"] >= 2010][:3]
        # South Germany
        else:
            return [e for e in HistoricalEventsDB.STORM_EVENTS if "Süddeutschland" in e["location"] or "Gesamtdeutschland" in e["location"]][:3]

    @staticmethod
    def get_earthquake_events_for_zone(zone: int) -> List[Dict]:
        """Get earthquake events for seismic zone."""
        if zone >= 3:
            return HistoricalEventsDB.EARTHQUAKE_EVENTS
        elif zone >= 2:
            return [e for e in HistoricalEventsDB.EARTHQUAKE_EVENTS if e["magnitude"] >= 4.0]
        else:
            return []

    @staticmethod
    def get_wildfire_events_for_region(state_code: str) -> List[Dict]:
        """Get wildfire events for region."""
        state_mapping = {
            "BB": ["Brandenburg"],
            "SN": ["Sächsische Schweiz"],
            "ST": ["Harz"],
            "BY": ["Bayern"],
        }

        if state_code not in state_mapping:
            return []

        events = []
        for event in HistoricalEventsDB.WILDFIRE_EVENTS:
            for region in state_mapping[state_code]:
                if region in event["location"]:
                    events.append(event)

        return events[:3]

    @staticmethod
    def get_risk_context(risk_type: str, location_data: Dict) -> str:
        """Get contextual information about historical risk."""
        if risk_type == "flood":
            events = HistoricalEventsDB.get_flood_events_for_region(
                location_data.get("state_code", ""),
                location_data.get("river_nearby")
            )
            if events:
                most_recent = events[0]
                return f"In dieser Region gab es {len(events)} bedeutende Hochwasserereignisse seit 1990. Das letzte große Ereignis war {most_recent['year']} mit Schäden von {most_recent['damage_eur']/1_000_000:.0f} Mio. €."
            return "Keine größeren Hochwasserereignisse in jüngerer Vergangenheit dokumentiert."

        elif risk_type == "storm":
            events = HistoricalEventsDB.get_storm_events_for_region(
                location_data.get("lat", 51),
                location_data.get("lng", 10)
            )
            if events:
                strongest = max(events, key=lambda x: x["wind_kmh"])
                return f"{len(events)} schwere Stürme haben diese Region getroffen. Stärkster: {strongest['name']} ({strongest['year']}) mit {strongest['wind_kmh']} km/h."
            return "Moderate Sturm-Historie."

        elif risk_type == "earthquake":
            zone = location_data.get("earthquake_zone", 0)
            events = HistoricalEventsDB.get_earthquake_events_for_zone(zone)
            if events:
                return f"Erdbebenzone {zone}: {len(events)} spürbare Beben seit 1990. Stärkstes: Magnitude {max(e['magnitude'] for e in events)}."
            return f"Erdbebenzone {zone}: Geringe seismische Aktivität."

        elif risk_type == "fire":
            events = HistoricalEventsDB.get_wildfire_events_for_region(
                location_data.get("state_code", "")
            )
            if events:
                total_area = sum(e["area_ha"] for e in events)
                return f"{len(events)} Waldbrände dokumentiert. Insgesamt {total_area:.0f} Hektar betroffen."
            return "Keine größeren Waldbrände in jüngerer Vergangenheit."

        return "Keine historischen Daten verfügbar."
