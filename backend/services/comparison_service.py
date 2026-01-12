"""
ImmoSafe DE - Comparison & Benchmark Service
Provides regional comparisons and context for risk assessments.
"""

import logging
from typing import TypedDict, Literal

logger = logging.getLogger(__name__)


class RegionalStats(TypedDict):
    """Regional statistics for comparison."""
    region_name: str
    average_flood_risk: int
    average_storm_risk: int
    average_fire_risk: int
    average_earthquake_risk: int
    average_total_risk: int


class ComparisonResult(TypedDict):
    """Comparison of location to region."""
    metric: str
    location_value: int
    region_average: int
    percentile: int  # 0-100, where location sits in distribution
    comparison_text: str  # "23% besser als Durchschnitt"


class BenchmarkAnalysis(TypedDict):
    """Complete benchmark analysis."""
    city_name: str
    state_name: str
    comparisons: list[ComparisonResult]
    overall_ranking: Literal["Sehr gut", "Gut", "Durchschnittlich", "Erhöht", "Hoch"]
    summary: str
    nearby_high_risk_areas: list[str]


class ComparisonService:
    """Service for regional comparisons and benchmarking."""

    # German states (Bundesländer) with typical risk profiles
    STATE_PROFILES = {
        "Baden-Württemberg": {"flood": 35, "storm": 30, "fire": 25, "earthquake": 45, "total": 34},
        "Bayern": {"flood": 40, "storm": 35, "fire": 30, "earthquake": 40, "total": 36},
        "Berlin": {"flood": 25, "storm": 30, "fire": 20, "earthquake": 15, "total": 23},
        "Brandenburg": {"flood": 30, "storm": 35, "fire": 35, "earthquake": 15, "total": 29},
        "Bremen": {"flood": 50, "storm": 40, "fire": 20, "earthquake": 10, "total": 30},
        "Hamburg": {"flood": 45, "storm": 40, "fire": 20, "earthquake": 10, "total": 29},
        "Hessen": {"flood": 35, "storm": 30, "fire": 25, "earthquake": 25, "total": 29},
        "Mecklenburg-Vorpommern": {"flood": 40, "storm": 45, "fire": 30, "earthquake": 10, "total": 31},
        "Niedersachsen": {"flood": 40, "storm": 40, "fire": 25, "earthquake": 15, "total": 30},
        "Nordrhein-Westfalen": {"flood": 45, "storm": 35, "fire": 25, "earthquake": 30, "total": 34},
        "Rheinland-Pfalz": {"flood": 50, "storm": 35, "fire": 25, "earthquake": 35, "total": 36},
        "Saarland": {"flood": 40, "storm": 30, "fire": 25, "earthquake": 30, "total": 31},
        "Sachsen": {"flood": 45, "storm": 35, "fire": 30, "earthquake": 25, "total": 34},
        "Sachsen-Anhalt": {"flood": 40, "storm": 35, "fire": 30, "earthquake": 20, "total": 31},
        "Schleswig-Holstein": {"flood": 50, "storm": 50, "fire": 20, "earthquake": 10, "total": 33},
        "Thüringen": {"flood": 35, "storm": 35, "fire": 30, "earthquake": 25, "total": 31},
    }

    # Major cities with risk profiles
    CITY_PROFILES = {
        "München": {"flood": 35, "storm": 30, "fire": 25, "earthquake": 40, "total": 33, "state": "Bayern"},
        "Berlin": {"flood": 25, "storm": 30, "fire": 20, "earthquake": 15, "total": 23, "state": "Berlin"},
        "Hamburg": {"flood": 45, "storm": 40, "fire": 20, "earthquake": 10, "total": 29, "state": "Hamburg"},
        "Köln": {"flood": 55, "storm": 35, "fire": 25, "earthquake": 35, "total": 38, "state": "Nordrhein-Westfalen"},
        "Frankfurt": {"flood": 40, "storm": 30, "fire": 25, "earthquake": 30, "total": 31, "state": "Hessen"},
        "Stuttgart": {"flood": 35, "storm": 30, "fire": 25, "earthquake": 50, "total": 35, "state": "Baden-Württemberg"},
        "Düsseldorf": {"flood": 50, "storm": 35, "fire": 25, "earthquake": 30, "total": 35, "state": "Nordrhein-Westfalen"},
        "Dresden": {"flood": 60, "storm": 35, "fire": 30, "earthquake": 25, "total": 38, "state": "Sachsen"},
        "Leipzig": {"flood": 40, "storm": 35, "fire": 30, "earthquake": 20, "total": 31, "state": "Sachsen"},
        "Nürnberg": {"flood": 30, "storm": 30, "fire": 28, "earthquake": 35, "total": 31, "state": "Bayern"},
    }

    # Known high-risk areas
    HIGH_RISK_AREAS = {
        "Hochwasser": ["Rheintal", "Elbe-Region", "Donau-Region", "Oder-Gebiet", "Mosel-Tal"],
        "Sturm": ["Nordseeküste", "Ostseeküste", "Norddeutsche Tiefebene"],
        "Erdbeben": ["Oberrheingraben", "Schwäbische Alb", "Vogtland", "Niederrhein"],
        "Waldbrand": ["Brandenburg", "Sächsische Schweiz", "Harz"],
    }

    @staticmethod
    def get_benchmark_analysis(
        lat: float,
        lng: float,
        address: str,
        flood_score: int,
        storm_score: int,
        fire_score: int,
        earthquake_score: int,
        total_score: int
    ) -> BenchmarkAnalysis:
        """
        Get comprehensive benchmark analysis for location.

        Args:
            lat: Latitude
            lng: Longitude
            address: Full address
            flood_score: Flood risk score (0-100)
            storm_score: Storm risk score (0-100)
            fire_score: Fire risk score (0-100)
            earthquake_score: Earthquake risk score (0-100)
            total_score: Total risk score (0-100)

        Returns:
            Complete benchmark analysis with comparisons
        """
        # Infer state and city from coordinates/address
        state_name, city_name = ComparisonService._infer_location(lat, lng, address)

        # Get regional baseline
        if state_name in ComparisonService.STATE_PROFILES:
            state_profile = ComparisonService.STATE_PROFILES[state_name]
        else:
            # Default to Germany average
            state_profile = {"flood": 38, "storm": 35, "fire": 27, "earthquake": 25, "total": 31}

        # Create comparisons
        comparisons: list[ComparisonResult] = []

        # Flood comparison
        comparisons.append(ComparisonService._create_comparison(
            "Hochwasserrisiko",
            flood_score,
            state_profile["flood"]
        ))

        # Storm comparison
        comparisons.append(ComparisonService._create_comparison(
            "Sturmrisiko",
            storm_score,
            state_profile["storm"]
        ))

        # Fire comparison
        comparisons.append(ComparisonService._create_comparison(
            "Waldbrandrisiko",
            fire_score,
            state_profile["fire"]
        ))

        # Earthquake comparison
        comparisons.append(ComparisonService._create_comparison(
            "Erdbebenrisiko",
            earthquake_score,
            state_profile["earthquake"]
        ))

        # Total comparison
        comparisons.append(ComparisonService._create_comparison(
            "Gesamtrisiko",
            total_score,
            state_profile["total"]
        ))

        # Overall ranking
        overall_ranking = ComparisonService._get_ranking(total_score, state_profile["total"])

        # Summary
        summary = ComparisonService._generate_summary(
            city_name, state_name, total_score, state_profile["total"], comparisons
        )

        # Nearby high-risk areas
        nearby_high_risk = ComparisonService._identify_nearby_risks(
            flood_score, storm_score, fire_score, earthquake_score, state_name
        )

        return {
            "city_name": city_name,
            "state_name": state_name,
            "comparisons": comparisons,
            "overall_ranking": overall_ranking,
            "summary": summary,
            "nearby_high_risk_areas": nearby_high_risk
        }

    @staticmethod
    def _infer_location(lat: float, lng: float, address: str) -> tuple[str, str]:
        """Infer state and city from coordinates and address."""
        # Simple heuristic based on address parsing
        address_lower = address.lower()

        # Try to find city in address
        city_name = "Unbekannt"
        for city in ComparisonService.CITY_PROFILES:
            if city.lower() in address_lower:
                city_name = city
                break

        # Try to find state based on city or coordinates
        state_name = "Deutschland"
        if city_name in ComparisonService.CITY_PROFILES:
            state_name = ComparisonService.CITY_PROFILES[city_name]["state"]
        else:
            # Approximate state from coordinates
            if lat > 53.5:
                state_name = "Schleswig-Holstein"
            elif lat > 52.5 and lng < 11:
                state_name = "Niedersachsen"
            elif lat > 52 and lng > 13:
                state_name = "Brandenburg"
            elif 51 < lat < 52 and 12 < lng < 15:
                state_name = "Sachsen-Anhalt"
            elif 50 < lat < 52 and 6 < lng < 9:
                state_name = "Nordrhein-Westfalen"
            elif 49 < lat < 51 and 10 < lng < 13:
                state_name = "Thüringen"
            elif 48 < lat < 50 and 11 < lng < 14:
                state_name = "Bayern"
            elif 48 < lat < 50 and 7 < lng < 10:
                state_name = "Baden-Württemberg"

        return state_name, city_name

    @staticmethod
    def _create_comparison(
        metric: str,
        location_value: int,
        region_average: int
    ) -> ComparisonResult:
        """Create a comparison result."""
        # Calculate percentile (simplified)
        if location_value <= region_average:
            # Better than average
            percentile = int(50 + (region_average - location_value) / region_average * 50)
        else:
            # Worse than average
            percentile = int(50 - (location_value - region_average) / location_value * 50)

        percentile = max(0, min(100, percentile))

        # Generate comparison text
        diff_percent = abs(location_value - region_average) / region_average * 100 if region_average > 0 else 0

        if location_value < region_average:
            if diff_percent > 20:
                comparison_text = f"{diff_percent:.0f}% niedriger als Durchschnitt (Sehr gut)"
            elif diff_percent > 10:
                comparison_text = f"{diff_percent:.0f}% niedriger als Durchschnitt (Gut)"
            else:
                comparison_text = "Etwa im Durchschnitt"
        elif location_value > region_average:
            if diff_percent > 30:
                comparison_text = f"{diff_percent:.0f}% höher als Durchschnitt (Erhöht)"
            elif diff_percent > 15:
                comparison_text = f"{diff_percent:.0f}% höher als Durchschnitt"
            else:
                comparison_text = "Leicht über Durchschnitt"
        else:
            comparison_text = "Genau im Durchschnitt"

        return {
            "metric": metric,
            "location_value": location_value,
            "region_average": region_average,
            "percentile": percentile,
            "comparison_text": comparison_text
        }

    @staticmethod
    def _get_ranking(
        total_score: int,
        region_average: int
    ) -> Literal["Sehr gut", "Gut", "Durchschnittlich", "Erhöht", "Hoch"]:
        """Get overall ranking."""
        if total_score < region_average * 0.7:
            return "Sehr gut"
        elif total_score < region_average * 0.9:
            return "Gut"
        elif total_score < region_average * 1.15:
            return "Durchschnittlich"
        elif total_score < region_average * 1.4:
            return "Erhöht"
        else:
            return "Hoch"

    @staticmethod
    def _generate_summary(
        city: str,
        state: str,
        total_score: int,
        state_average: int,
        comparisons: list[ComparisonResult]
    ) -> str:
        """Generate summary text."""
        # Find best and worst metrics
        best_metric = min(comparisons[:-1], key=lambda x: x["location_value"])  # Exclude total
        worst_metric = max(comparisons[:-1], key=lambda x: x["location_value"])

        summary_parts = []

        # Overall comparison
        if total_score < state_average:
            summary_parts.append(
                f"Dieser Standort weist ein unterdurchschnittliches Gesamtrisiko für {state} auf."
            )
        elif total_score > state_average * 1.2:
            summary_parts.append(
                f"Dieser Standort hat ein überdurchschnittliches Gesamtrisiko für {state}."
            )
        else:
            summary_parts.append(
                f"Dieser Standort liegt beim Gesamtrisiko im Durchschnitt für {state}."
            )

        # Best aspect
        if best_metric["location_value"] < best_metric["region_average"] * 0.8:
            summary_parts.append(
                f"Besonders positiv: {best_metric['metric']} ist deutlich niedriger als regional üblich."
            )

        # Worst aspect
        if worst_metric["location_value"] > worst_metric["region_average"] * 1.2:
            summary_parts.append(
                f"Erhöhte Aufmerksamkeit erforderlich: {worst_metric['metric']} liegt über dem Durchschnitt."
            )

        return " ".join(summary_parts)

    @staticmethod
    def _identify_nearby_risks(
        flood_score: int,
        storm_score: int,
        fire_score: int,
        earthquake_score: int,
        state: str
    ) -> list[str]:
        """Identify nearby high-risk areas relevant to this location."""
        nearby_risks = []

        if flood_score > 40:
            nearby_risks.extend([area for area in ComparisonService.HIGH_RISK_AREAS["Hochwasser"]])

        if storm_score > 40 and state in ["Schleswig-Holstein", "Mecklenburg-Vorpommern", "Niedersachsen", "Bremen", "Hamburg"]:
            nearby_risks.extend(["Nordseeküste", "Ostseeküste"])

        if earthquake_score > 40:
            nearby_risks.extend([area for area in ComparisonService.HIGH_RISK_AREAS["Erdbeben"]])

        if fire_score > 40:
            nearby_risks.extend([area for area in ComparisonService.HIGH_RISK_AREAS["Waldbrand"]])

        # Return unique list, max 5 items
        return list(set(nearby_risks))[:5]
