"""
ImmoSafe DE - Insurance & Financial Impact Service
Provides insurance recommendations and financial impact analysis.
"""

import logging
from typing import TypedDict, Literal

logger = logging.getLogger(__name__)


class InsuranceRecommendation(TypedDict):
    """Insurance recommendation with cost estimates."""
    type: str  # "Elementarversicherung", "Wohngebäudeversicherung", etc.
    priority: Literal["Erforderlich", "Empfohlen", "Optional"]
    estimated_annual_cost_eur: tuple[int, int]  # (min, max)
    coverage_details: list[str]
    reasoning: str
    provider_tips: list[str]


class FinancialImpact(TypedDict):
    """Financial impact analysis."""
    property_value_impact_percent: tuple[float, float]  # (min, max) percentage
    annual_insurance_cost_eur: tuple[int, int]  # (min, max)
    potential_damage_cost_eur: tuple[int, int]  # (min, max) for worst case
    mitigation_cost_eur: tuple[int, int]  # (min, max) for recommended actions
    roi_years: float  # Return on investment for mitigation measures


class InsuranceAnalysis(TypedDict):
    """Complete insurance and financial analysis."""
    recommendations: list[InsuranceRecommendation]
    financial_impact: FinancialImpact
    total_annual_cost_estimate_eur: tuple[int, int]
    comparison_to_average: str  # "20% höher als Durchschnitt"


class InsuranceService:
    """Service for insurance recommendations and financial impact analysis."""

    # Base insurance costs (annual, EUR) - German market averages 2024
    BASE_BUILDING_INSURANCE = (200, 400)  # per 100k property value
    BASE_ELEMENTAL_INSURANCE = (150, 350)  # per 100k property value
    BASE_LIABILITY_INSURANCE = (80, 150)  # flat rate

    @staticmethod
    def analyze_insurance_needs(
        flood_score: int,
        storm_score: int,
        fire_score: int,
        earthquake_score: int,
        property_value_eur: int = 400000,  # Average German property value
    ) -> InsuranceAnalysis:
        """
        Analyze insurance needs based on risk scores.

        Args:
            flood_score: Flood risk score (0-100)
            storm_score: Storm risk score (0-100)
            fire_score: Fire risk score (0-100)
            earthquake_score: Earthquake risk score (0-100)
            property_value_eur: Estimated property value

        Returns:
            Complete insurance analysis with recommendations
        """
        recommendations: list[InsuranceRecommendation] = []

        # 1. Wohngebäudeversicherung (always required)
        recommendations.append({
            "type": "Wohngebäudeversicherung",
            "priority": "Erforderlich",
            "estimated_annual_cost_eur": InsuranceService._scale_cost(
                InsuranceService.BASE_BUILDING_INSURANCE,
                property_value_eur,
                max(flood_score, storm_score, fire_score)
            ),
            "coverage_details": [
                "Schäden durch Feuer, Blitzschlag, Explosion",
                "Leitungswasserschäden",
                "Sturmschäden ab Windstärke 8",
                "Hagelschäden"
            ],
            "reasoning": "Grundschutz für Gebäudeschäden - von Banken meist vorausgesetzt",
            "provider_tips": [
                "Neuwertentschädigung statt Zeitwert wählen",
                "Unterversicherungsverzicht vereinbaren",
                "Grobe Fahrlässigkeit mitversichern"
            ]
        })

        # 2. Elementarschadenversicherung (based on flood/storm risk)
        elemental_score = max(flood_score, storm_score)
        if elemental_score > 30:
            priority: Literal["Erforderlich", "Empfohlen", "Optional"] = (
                "Erforderlich" if elemental_score > 60 else "Empfohlen"
            )
            recommendations.append({
                "type": "Elementarschadenversicherung",
                "priority": priority,
                "estimated_annual_cost_eur": InsuranceService._scale_cost(
                    InsuranceService.BASE_ELEMENTAL_INSURANCE,
                    property_value_eur,
                    elemental_score
                ),
                "coverage_details": [
                    "Überschwemmung und Hochwasser",
                    "Rückstau aus Kanalisation",
                    "Starkregen und Oberflächenwasser",
                    "Erdrutsch, Erdsenkung, Erdfall",
                    "Lawinen und Schneedruck"
                ],
                "reasoning": InsuranceService._get_elemental_reasoning(elemental_score, flood_score, storm_score),
                "provider_tips": [
                    "ZÜRS-Zone prüfen (Zonierung für Überschwemmung, Rückstau und Starkregen)",
                    "Selbstbehalt wählen um Prämie zu senken",
                    "Bei Zone 4: Nur wenige Versicherer, höhere Kosten"
                ]
            })

        # 3. Erweiterte Naturgefahren bei hohem Erdbebenrisiko
        if earthquake_score > 50:
            recommendations.append({
                "type": "Erdbebenversicherung (Erweiterung)",
                "priority": "Empfohlen",
                "estimated_annual_cost_eur": (100, 300),
                "coverage_details": [
                    "Gebäudeschäden durch Erdbeben",
                    "Folgeschäden wie Risse und Setzungen"
                ],
                "reasoning": f"Erhöhtes Erdbebenrisiko (Score: {earthquake_score}/100) in dieser Region",
                "provider_tips": [
                    "Nur als Zusatz zur Wohngebäudeversicherung verfügbar",
                    "In Deutschland selten, aber in Erdbebenzone 3 sinnvoll"
                ]
            })

        # 4. Calculate financial impact
        financial_impact = InsuranceService._calculate_financial_impact(
            flood_score, storm_score, fire_score, earthquake_score, property_value_eur
        )

        # 5. Total annual cost
        total_cost_min = sum(r["estimated_annual_cost_eur"][0] for r in recommendations)
        total_cost_max = sum(r["estimated_annual_cost_eur"][1] for r in recommendations)

        # 6. Comparison to average
        average_cost = 600  # Average German insurance cost
        avg_diff_percent = ((total_cost_min + total_cost_max) / 2 - average_cost) / average_cost * 100

        if avg_diff_percent > 10:
            comparison = f"{abs(avg_diff_percent):.0f}% höher als Durchschnitt"
        elif avg_diff_percent < -10:
            comparison = f"{abs(avg_diff_percent):.0f}% niedriger als Durchschnitt"
        else:
            comparison = "Im Durchschnitt"

        return {
            "recommendations": recommendations,
            "financial_impact": financial_impact,
            "total_annual_cost_estimate_eur": (total_cost_min, total_cost_max),
            "comparison_to_average": comparison
        }

    @staticmethod
    def _scale_cost(
        base_cost: tuple[int, int],
        property_value: int,
        risk_score: int
    ) -> tuple[int, int]:
        """Scale insurance cost based on property value and risk."""
        value_factor = property_value / 100000
        risk_multiplier = 1 + (risk_score / 100) * 0.5  # Up to 50% increase for high risk

        min_cost = int(base_cost[0] * value_factor * risk_multiplier)
        max_cost = int(base_cost[1] * value_factor * risk_multiplier)

        return (min_cost, max_cost)

    @staticmethod
    def _get_elemental_reasoning(elemental_score: int, flood_score: int, storm_score: int) -> str:
        """Generate reasoning for elemental insurance recommendation."""
        reasons = []

        if flood_score > 50:
            reasons.append(f"Hohes Hochwasserrisiko (Score: {flood_score}/100)")
        elif flood_score > 30:
            reasons.append(f"Erhöhtes Hochwasserrisiko (Score: {flood_score}/100)")

        if storm_score > 50:
            reasons.append(f"Hohes Sturmrisiko (Score: {storm_score}/100)")
        elif storm_score > 30:
            reasons.append(f"Erhöhtes Sturmrisiko (Score: {storm_score}/100)")

        if not reasons:
            reasons.append("Vorsorge gegen Elementarschäden empfohlen")

        reasons.append("Elementarschäden nicht in Standard-Wohngebäudeversicherung enthalten")

        return " - ".join(reasons)

    @staticmethod
    def _calculate_financial_impact(
        flood_score: int,
        storm_score: int,
        fire_score: int,
        earthquake_score: int,
        property_value: int
    ) -> FinancialImpact:
        """Calculate financial impact of risks."""
        # Property value impact based on highest risk
        max_risk = max(flood_score, storm_score, fire_score, earthquake_score)

        if max_risk > 70:
            value_impact = (-15.0, -5.0)
        elif max_risk > 50:
            value_impact = (-8.0, -2.0)
        elif max_risk > 30:
            value_impact = (-3.0, 0.0)
        else:
            value_impact = (0.0, 2.0)  # Low risk can increase value

        # Annual insurance cost (already calculated above, estimated)
        base_insurance = (350, 750)
        risk_factor = 1 + (max_risk / 100) * 0.6
        annual_cost = (
            int(base_insurance[0] * risk_factor),
            int(base_insurance[1] * risk_factor)
        )

        # Potential damage cost (worst case scenario)
        if max_risk > 70:
            damage_cost = (50000, 200000)
        elif max_risk > 50:
            damage_cost = (20000, 80000)
        elif max_risk > 30:
            damage_cost = (10000, 40000)
        else:
            damage_cost = (5000, 15000)

        # Mitigation cost (preventive measures)
        mitigation_items = []
        if flood_score > 40:
            mitigation_items.append(("Rückstauklappen installieren", 1500, 3000))
            mitigation_items.append(("Drainage-System verbessern", 3000, 8000))
        if storm_score > 40:
            mitigation_items.append(("Dachsicherung verstärken", 2000, 5000))
        if fire_score > 40:
            mitigation_items.append(("Feuerlöscher und Rauchmelder", 300, 800))

        if mitigation_items:
            mitigation_cost = (
                sum(item[1] for item in mitigation_items),
                sum(item[2] for item in mitigation_items)
            )
        else:
            mitigation_cost = (500, 2000)

        # ROI calculation (simplified)
        avg_mitigation = (mitigation_cost[0] + mitigation_cost[1]) / 2
        avg_annual_savings = 200  # Estimated insurance savings + damage prevention
        roi_years = round(avg_mitigation / avg_annual_savings, 1) if avg_annual_savings > 0 else 10.0

        return {
            "property_value_impact_percent": value_impact,
            "annual_insurance_cost_eur": annual_cost,
            "potential_damage_cost_eur": damage_cost,
            "mitigation_cost_eur": mitigation_cost,
            "roi_years": roi_years
        }
