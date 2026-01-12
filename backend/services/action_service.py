"""
ImmoSafe DE - Action Recommendations Service
Provides actionable recommendations with priorities and cost estimates.
"""

import logging
from typing import TypedDict, Literal

logger = logging.getLogger(__name__)


class ActionItem(TypedDict):
    """Single actionable recommendation."""
    title: str
    description: str
    priority: Literal["Sofort", "Kurzfristig", "Mittelfristig", "Langfristig"]
    urgency_score: int  # 1-10
    category: Literal["Baulich", "Versicherung", "Wartung", "Notfallvorsorge"]
    estimated_cost_eur: tuple[int, int]  # (min, max)
    time_to_implement: str  # "1-2 Tage", "1-2 Wochen", etc.
    roi_description: str
    diy_possible: bool
    providers: list[str]  # Types of providers needed
    resources: list[str]  # Helpful resources/links


class ActionPlan(TypedDict):
    """Complete action plan with prioritized recommendations."""
    immediate_actions: list[ActionItem]  # Priority: Sofort
    short_term_actions: list[ActionItem]  # Priority: Kurzfristig (< 3 Monate)
    medium_term_actions: list[ActionItem]  # Priority: Mittelfristig (3-12 Monate)
    long_term_actions: list[ActionItem]  # Priority: Langfristig (> 12 Monate)
    total_estimated_cost_eur: tuple[int, int]
    estimated_risk_reduction_percent: int  # How much risk can be reduced
    summary: str


class ActionService:
    """Service for generating actionable recommendations."""

    @staticmethod
    def generate_action_plan(
        flood_score: int,
        storm_score: int,
        fire_score: int,
        temperature_score: int,
        hail_score: int,
        earthquake_score: int,
        elevation: float,
        has_basement: bool = True
    ) -> ActionPlan:
        """
        Generate comprehensive action plan based on risk scores.

        Args:
            flood_score: Flood risk score (0-100)
            storm_score: Storm risk score (0-100)
            fire_score: Fire risk score (0-100)
            temperature_score: Temperature extremes risk score (0-100)
            hail_score: Hail risk score (0-100)
            earthquake_score: Earthquake risk score (0-100)
            elevation: Elevation in meters
            has_basement: Whether property has basement

        Returns:
            Complete action plan with prioritized recommendations
        """
        all_actions: list[ActionItem] = []

        # Generate flood-related actions
        if flood_score > 30:
            all_actions.extend(ActionService._get_flood_actions(flood_score, elevation, has_basement))

        # Generate storm-related actions
        if storm_score > 30:
            all_actions.extend(ActionService._get_storm_actions(storm_score))

        # Generate fire-related actions
        if fire_score > 30:
            all_actions.extend(ActionService._get_fire_actions(fire_score))

        # Generate temperature-related actions
        if temperature_score > 40:
            all_actions.extend(ActionService._get_temperature_actions(temperature_score))

        # Generate hail-related actions
        if hail_score > 40:
            all_actions.extend(ActionService._get_hail_actions(hail_score))

        # Generate earthquake-related actions
        if earthquake_score > 40:
            all_actions.extend(ActionService._get_earthquake_actions(earthquake_score))

        # General emergency preparedness (always recommended)
        all_actions.extend(ActionService._get_general_preparedness_actions())

        # Sort actions by priority and urgency
        immediate = [a for a in all_actions if a["priority"] == "Sofort"]
        short_term = [a for a in all_actions if a["priority"] == "Kurzfristig"]
        medium_term = [a for a in all_actions if a["priority"] == "Mittelfristig"]
        long_term = [a for a in all_actions if a["priority"] == "Langfristig"]

        # Sort each list by urgency score
        immediate.sort(key=lambda x: x["urgency_score"], reverse=True)
        short_term.sort(key=lambda x: x["urgency_score"], reverse=True)
        medium_term.sort(key=lambda x: x["urgency_score"], reverse=True)
        long_term.sort(key=lambda x: x["urgency_score"], reverse=True)

        # Calculate total cost
        total_min = sum(a["estimated_cost_eur"][0] for a in all_actions)
        total_max = sum(a["estimated_cost_eur"][1] for a in all_actions)

        # Estimate risk reduction
        risk_reduction = min(50, len(all_actions) * 5)  # Simplified

        # Generate summary
        summary = ActionService._generate_plan_summary(
            len(immediate), len(short_term), len(medium_term), len(long_term),
            total_min, total_max, risk_reduction
        )

        return {
            "immediate_actions": immediate,
            "short_term_actions": short_term,
            "medium_term_actions": medium_term,
            "long_term_actions": long_term,
            "total_estimated_cost_eur": (total_min, total_max),
            "estimated_risk_reduction_percent": risk_reduction,
            "summary": summary
        }

    @staticmethod
    def _get_flood_actions(score: int, elevation: float, has_basement: bool) -> list[ActionItem]:
        """Generate flood-specific actions."""
        actions: list[ActionItem] = []

        if score > 60:
            # High flood risk - immediate actions
            actions.append({
                "title": "Rückstauklappe installieren",
                "description": "Verhindert das Eindringen von Abwasser aus der Kanalisation bei Starkregen. Pflicht in vielen hochwassergefährdeten Gebieten.",
                "priority": "Sofort",
                "urgency_score": 9,
                "category": "Baulich",
                "estimated_cost_eur": (1500, 3500),
                "time_to_implement": "1-3 Tage",
                "roi_description": "Vermeidet Schäden durch Rückstau (Ø 15.000€). Amortisation bei erstem vermiedenen Schaden.",
                "diy_possible": False,
                "providers": ["Sanitärinstallateur", "Fachbetrieb für Gebäudeentwässerung"],
                "resources": ["DIN EN 13564", "Fachverband SHK"]
            })

            if has_basement:
                actions.append({
                    "title": "Kellerabdichtung prüfen und erneuern",
                    "description": "Professionelle Abdichtung gegen drückendes Wasser. Besonders wichtig bei Grundwasser-Problematik.",
                    "priority": "Kurzfristig",
                    "urgency_score": 8,
                    "category": "Baulich",
                    "estimated_cost_eur": (5000, 15000),
                    "time_to_implement": "1-2 Wochen",
                    "roi_description": "Verhindert strukturelle Schäden und Schimmelbildung (Sanierung: 20.000-50.000€)",
                    "diy_possible": False,
                    "providers": ["Abdichtungsfirma", "Bausachverständiger"],
                    "resources": ["WTA-Merkblatt", "Bundesverband Abdichtung"]
                })

        if score > 40:
            actions.append({
                "title": "Drainage-System optimieren",
                "description": "Oberflächenwasser gezielt vom Gebäude wegleiten. Drainage rund um Fundament verbessern.",
                "priority": "Kurzfristig" if score > 60 else "Mittelfristig",
                "urgency_score": 7,
                "category": "Baulich",
                "estimated_cost_eur": (3000, 10000),
                "time_to_implement": "3-5 Tage",
                "roi_description": "Reduziert Feuchtigkeit am Mauerwerk, verlängert Lebensdauer des Gebäudes",
                "diy_possible": False,
                "providers": ["Tiefbauunternehmen", "Garten- und Landschaftsbau"],
                "resources": ["DIN 4095", "Fachverband Drainage"]
            })

            actions.append({
                "title": "Hochwasserschutz-Ausstattung anschaffen",
                "description": "Mobile Hochwasserschutz-Systeme für Türen und Fenster. Sandsäcke, Alu-Dammbalken oder Wassersperren.",
                "priority": "Sofort" if score > 70 else "Kurzfristig",
                "urgency_score": 8 if score > 70 else 6,
                "category": "Notfallvorsorge",
                "estimated_cost_eur": (500, 3000),
                "time_to_implement": "Sofort verfügbar",
                "roi_description": "Kann im Ernstfall Schäden in Höhe von 10.000-50.000€ verhindern",
                "diy_possible": True,
                "providers": ["Baumarkt", "Hochwasserschutz-Fachhandel"],
                "resources": ["HochwasserKompetenzCentrum", "BBK (Bundesamt für Bevölkerungsschutz)"]
            })

        return actions

    @staticmethod
    def _get_storm_actions(score: int) -> list[ActionItem]:
        """Generate storm-specific actions."""
        actions: list[ActionItem] = []

        if score > 50:
            actions.append({
                "title": "Dachsicherung überprüfen und verstärken",
                "description": "Ziegel, Dachrinnen und Befestigung von Dachelementen prüfen. Lose Teile sichern oder ersetzen.",
                "priority": "Kurzfristig",
                "urgency_score": 8,
                "category": "Baulich",
                "estimated_cost_eur": (2000, 6000),
                "time_to_implement": "2-4 Tage",
                "roi_description": "Sturmschäden am Dach kosten durchschnittlich 8.000-25.000€",
                "diy_possible": False,
                "providers": ["Dachdeckerbetrieb", "Zimmerei"],
                "resources": ["Zentralverband Deutsches Dachdeckerhandwerk"]
            })

            actions.append({
                "title": "Bäume und Sträucher fachgerecht zurückschneiden",
                "description": "Überhängende Äste entfernen, instabile Bäume fällen. Abstand zum Gebäude mind. 5m.",
                "priority": "Kurzfristig",
                "urgency_score": 7,
                "category": "Wartung",
                "estimated_cost_eur": (300, 1500),
                "time_to_implement": "1-2 Tage",
                "roi_description": "Vermeidet Sturmschäden durch umstürzende Bäume (Ø 12.000€)",
                "diy_possible": True,
                "providers": ["Baumpflege-Fachbetrieb", "Garten- und Landschaftsbau"],
                "resources": ["ZTV-Baumpflege", "FLL (Forschungsgesellschaft Landschaftsentwicklung)"]
            })

        if score > 40:
            actions.append({
                "title": "Fenster und Türen gegen Sturm sichern",
                "description": "Fensterläden installieren oder Sturmhaken nachrüsten. Haustür gegen Aufdrücken sichern.",
                "priority": "Mittelfristig",
                "urgency_score": 6,
                "category": "Baulich",
                "estimated_cost_eur": (800, 3000),
                "time_to_implement": "1-3 Tage",
                "roi_description": "Verhindert Folgeschäden durch eindringendes Wasser (5.000-15.000€)",
                "diy_possible": True,
                "providers": ["Fensterbauer", "Schreiner", "Baumarkt"],
                "resources": ["RAL Gütegemeinschaft Fenster"]
            })

        return actions

    @staticmethod
    def _get_fire_actions(score: int) -> list[ActionItem]:
        """Generate fire-specific actions."""
        actions: list[ActionItem] = []

        if score > 50:
            actions.append({
                "title": "Brandschutzkonzept erstellen und umsetzen",
                "description": "Rauchmelder in allen Räumen, Feuerlöscher zugänglich platzieren, Löschdecke in der Küche.",
                "priority": "Sofort",
                "urgency_score": 9,
                "category": "Notfallvorsorge",
                "estimated_cost_eur": (300, 800),
                "time_to_implement": "1 Tag",
                "roi_description": "Frühwarnung kann Leben retten und Gebäudeschäden minimieren",
                "diy_possible": True,
                "providers": ["Baumarkt", "Fachhandel Brandschutz"],
                "resources": ["DIN 14676 (Rauchmelder)", "Feuerwehr-Beratung"]
            })

            actions.append({
                "title": "Vegetation rund ums Haus zurückschneiden",
                "description": "Mindestens 10m Abstand zwischen Gebäude und brennbarem Material (trockene Büsche, Holzstapel).",
                "priority": "Kurzfristig",
                "urgency_score": 7,
                "category": "Wartung",
                "estimated_cost_eur": (200, 1000),
                "time_to_implement": "1-2 Tage",
                "roi_description": "Reduziert Waldbrand-Übergreifen auf Gebäude dramatisch",
                "diy_possible": True,
                "providers": ["Gartenbau", "Eigenleistung möglich"],
                "resources": ["Waldbrandschutz-Leitfaden der Feuerwehr"]
            })

        return actions

    @staticmethod
    def _get_temperature_actions(score: int) -> list[ActionItem]:
        """Generate temperature-related actions."""
        actions: list[ActionItem] = []

        if score > 50:
            actions.append({
                "title": "Wärmedämmung und Klimatisierung verbessern",
                "description": "Dach und Fassade dämmen für Hitzeschutz im Sommer. Moderne Fenster mit Sonnenschutzverglasung.",
                "priority": "Mittelfristig",
                "urgency_score": 5,
                "category": "Baulich",
                "estimated_cost_eur": (8000, 25000),
                "time_to_implement": "2-4 Wochen",
                "roi_description": "Energieeinsparung 30-40%, Wertsteigerung der Immobilie, KfW-Förderung möglich",
                "diy_possible": False,
                "providers": ["Energieberater", "Dämmungsfachbetrieb"],
                "resources": ["KfW-Förderbank", "BAFA Energieberatung"]
            })

        return actions

    @staticmethod
    def _get_hail_actions(score: int) -> list[ActionItem]:
        """Generate hail-specific actions."""
        actions: list[ActionItem] = []

        if score > 50:
            actions.append({
                "title": "Hagelwiderstandsfähige Materialien verwenden",
                "description": "Bei Dacherneuerung hagelresistente Ziegel (Hagelregister) wählen. Rollläden zum Fensterschutz.",
                "priority": "Langfristig",
                "urgency_score": 4,
                "category": "Baulich",
                "estimated_cost_eur": (0, 5000),  # Mehrkosten bei Erneuerung
                "time_to_implement": "Bei nächster Renovierung",
                "roi_description": "Hagelschäden am Dach: 5.000-15.000€. Einmalige Investition für langfristigen Schutz",
                "diy_possible": False,
                "providers": ["Dachdeckerbetrieb mit Hagelschutz-Expertise"],
                "resources": ["VKF Hagelregister"]
            })

        return actions

    @staticmethod
    def _get_earthquake_actions(score: int) -> list[ActionItem]:
        """Generate earthquake-specific actions."""
        actions: list[ActionItem] = []

        if score > 60:
            actions.append({
                "title": "Statische Prüfung durchführen",
                "description": "Gebäudestatik von Fachingenieur prüfen lassen. Besonders bei Altbauten wichtig.",
                "priority": "Mittelfristig",
                "urgency_score": 6,
                "category": "Baulich",
                "estimated_cost_eur": (1500, 4000),
                "time_to_implement": "1 Woche (Gutachten)",
                "roi_description": "Identifiziert strukturelle Schwachstellen vor einem Ernstfall",
                "diy_possible": False,
                "providers": ["Tragwerksplaner", "Bausachverständiger"],
                "resources": ["DIN 4149", "Ingenieurkammer"]
            })

        return actions

    @staticmethod
    def _get_general_preparedness_actions() -> list[ActionItem]:
        """Generate general emergency preparedness actions."""
        return [
            {
                "title": "Notfallvorrat und Notfallplan erstellen",
                "description": "Lebensmittel und Wasser für 10 Tage, Erste-Hilfe-Set, batteriebetriebenes Radio, Dokumente sichern.",
                "priority": "Kurzfristig",
                "urgency_score": 6,
                "category": "Notfallvorsorge",
                "estimated_cost_eur": (200, 500),
                "time_to_implement": "1-2 Tage",
                "roi_description": "Sicherheit im Katastrophenfall - unbezahlbar",
                "diy_possible": True,
                "providers": ["Supermarkt", "Apotheke", "Baumarkt"],
                "resources": ["BBK Ratgeber für Notfallvorsorge", "BBK Warn-App NINA"]
            },
            {
                "title": "Elementarschadenversicherung abschließen",
                "description": "Erweitert Wohngebäudeversicherung um Naturgefahren wie Hochwasser, Starkregen, Erdrutsch.",
                "priority": "Kurzfristig",
                "urgency_score": 7,
                "category": "Versicherung",
                "estimated_cost_eur": (150, 400),  # Annual
                "time_to_implement": "Sofort",
                "roi_description": "Schützt vor existenzbedrohenden Kosten (oft 50.000€+)",
                "diy_possible": True,
                "providers": ["Versicherungsmakler", "Online-Vergleichsportale"],
                "resources": ["GDV (Gesamtverband der Deutschen Versicherungswirtschaft)"]
            }
        ]

    @staticmethod
    def _generate_plan_summary(
        immediate: int,
        short_term: int,
        medium_term: int,
        long_term: int,
        total_min: int,
        total_max: int,
        risk_reduction: int
    ) -> str:
        """Generate action plan summary."""
        total_actions = immediate + short_term + medium_term + long_term

        summary = f"Ihr maßgeschneiderter Schutzplan umfasst {total_actions} konkrete Maßnahmen: "

        if immediate > 0:
            summary += f"{immediate} sollten sofort umgesetzt werden, "

        if short_term > 0:
            summary += f"{short_term} innerhalb der nächsten 3 Monate, "

        if medium_term > 0:
            summary += f"{medium_term} bis zum Jahresende, "

        if long_term > 0:
            summary += f"und {long_term} langfristig. "

        summary += f"Investition: {total_min:,}-{total_max:,}€. "
        summary += f"Potenzielle Risikoreduktion: bis zu {risk_reduction}%."

        return summary
