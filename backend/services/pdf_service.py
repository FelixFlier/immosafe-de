"""
ImmoSafe DE - PDF Report Generation Service
Professional PDF reports with comprehensive risk analysis.
"""

import io
import logging
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class PDFReportService:
    """Service for generating professional PDF reports."""

    # Brand Colors
    PRIMARY_COLOR = colors.HexColor('#0EA5E9')  # Sky blue
    SECONDARY_COLOR = colors.HexColor('#F59E0B')  # Amber
    SUCCESS_COLOR = colors.HexColor('#10B981')  # Green
    WARNING_COLOR = colors.HexColor('#F59E0B')  # Amber
    DANGER_COLOR = colors.HexColor('#EF4444')  # Red
    DARK_COLOR = colors.HexColor('#1E293B')  # Slate

    @staticmethod
    def generate_report(analysis_data: Dict[str, Any], address: str) -> bytes:
        """
        Generate a comprehensive PDF report.

        Args:
            analysis_data: Complete analysis response data
            address: The analyzed address

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=f"ImmoSafe Risikobericht - {address}",
            author="ImmoSafe DE"
        )

        # Build content
        story = []
        styles = PDFReportService._get_styles()

        # Header
        story.extend(PDFReportService._build_header(address, styles))
        story.append(Spacer(1, 0.5*cm))

        # Executive Summary
        story.extend(PDFReportService._build_executive_summary(analysis_data, styles))
        story.append(Spacer(1, 0.5*cm))

        # Risk Overview
        story.extend(PDFReportService._build_risk_overview(analysis_data, styles))
        story.append(PageBreak())

        # Detailed Risk Analysis
        story.extend(PDFReportService._build_detailed_risks(analysis_data, styles))
        story.append(PageBreak())

        # Premium Features (if available)
        if analysis_data.get('premium_features'):
            story.extend(PDFReportService._build_premium_section(
                analysis_data['premium_features'], styles
            ))
            story.append(PageBreak())

        # Footer / Disclaimer
        story.extend(PDFReportService._build_footer(styles))

        # Build PDF
        doc.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    @staticmethod
    def _get_styles():
        """Get custom paragraph styles."""
        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=PDFReportService.PRIMARY_COLOR,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=PDFReportService.DARK_COLOR,
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=PDFReportService.DARK_COLOR,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_LEFT
        ))

        styles.add(ParagraphStyle(
            name='SmallText',
            parent=styles['BodyText'],
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=4
        ))

        return styles

    @staticmethod
    def _build_header(address: str, styles):
        """Build PDF header."""
        elements = []

        # Title
        elements.append(Paragraph(
            "🏠 ImmoSafe DE",
            styles['CustomTitle']
        ))

        elements.append(Paragraph(
            "Professioneller Naturkatastrophen-Risikobericht",
            styles['CustomHeading']
        ))

        elements.append(Spacer(1, 0.3*cm))

        # Address & Date
        report_info = [
            ['<b>Adresse:</b>', address],
            ['<b>Berichtsdatum:</b>', datetime.now().strftime('%d.%m.%Y')],
            ['<b>Version:</b>', '2.1 - Umfassende Analyse']
        ]

        info_table = Table(report_info, colWidths=[4*cm, 12*cm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(info_table)

        return elements

    @staticmethod
    def _build_executive_summary(data: Dict, styles):
        """Build executive summary section."""
        elements = []

        elements.append(Paragraph("Zusammenfassung", styles['CustomHeading']))

        total_score = data.get('total_risk_score', 0)
        total_level = data.get('total_risk_level', 'Unknown')
        primary_risks = data.get('primary_risks', [])

        # Risk Score Card
        score_color = PDFReportService._get_risk_color(total_score)

        summary_data = [
            ['Gesamtrisiko-Score', f"{total_score}/100"],
            ['Risiko-Stufe', total_level],
            ['Hauptrisiken', ', '.join(primary_risks) if primary_risks else 'Keine']
        ]

        summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), score_color),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)

        return elements

    @staticmethod
    def _build_risk_overview(data: Dict, styles):
        """Build risk overview table."""
        elements = []

        elements.append(Paragraph("Risiko-Übersicht", styles['CustomHeading']))

        # Risk categories
        risks = [
            ('🌊 Hochwasser', data.get('flood_risk', {})),
            ('💨 Sturm', data.get('storm_risk', {})),
            ('🔥 Waldbrand', data.get('fire_risk', {})),
            ('🌡️ Extremtemperaturen', data.get('temperature_risk', {})),
            ('🧊 Hagel', data.get('hail_risk', {})),
            ('🏚️ Erdbeben', data.get('earthquake_risk', {})),
        ]

        risk_data = [['Risikotyp', 'Score', 'Stufe', 'Bewertung']]

        for name, risk in risks:
            score = risk.get('score', 0)
            level = risk.get('level', 'Unknown')
            color = PDFReportService._get_risk_color(score)

            risk_data.append([
                name,
                f"{score}/100",
                level,
                PDFReportService._get_risk_assessment(score)
            ])

        risk_table = Table(risk_data, colWidths=[5*cm, 3*cm, 4*cm, 4*cm])
        risk_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (-1, 0), PDFReportService.PRIMARY_COLOR),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        # Color code risk scores
        for i in range(1, len(risk_data)):
            score = risks[i-1][1].get('score', 0)
            color = PDFReportService._get_risk_color(score)
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (1, i), (1, i), color)
            ]))

        elements.append(risk_table)

        return elements

    @staticmethod
    def _build_detailed_risks(data: Dict, styles):
        """Build detailed risk analysis."""
        elements = []

        elements.append(Paragraph("Detaillierte Risikoanalyse", styles['CustomHeading']))

        risks = [
            ('Hochwasser', data.get('flood_risk', {})),
            ('Sturm', data.get('storm_risk', {})),
            ('Waldbrand', data.get('fire_risk', {})),
            ('Extremtemperaturen', data.get('temperature_risk', {})),
            ('Hagel', data.get('hail_risk', {})),
            ('Erdbeben', data.get('earthquake_risk', {})),
        ]

        for name, risk in risks:
            if not risk:
                continue

            score = risk.get('score', 0)
            level = risk.get('level', 'Unknown')
            factors = risk.get('factors', [])
            recommendations = risk.get('recommendations', [])

            # Risk header
            elements.append(Paragraph(
                f"{name} - Score: {score}/100 ({level})",
                styles['CustomSubHeading']
            ))

            # Factors
            if factors:
                elements.append(Paragraph("<b>Risikofaktoren:</b>", styles['CustomBody']))
                for factor in factors:
                    elements.append(Paragraph(f"• {factor}", styles['CustomBody']))

            # Recommendations
            if recommendations:
                elements.append(Paragraph("<b>Empfehlungen:</b>", styles['CustomBody']))
                for rec in recommendations:
                    elements.append(Paragraph(f"• {rec}", styles['CustomBody']))

            elements.append(Spacer(1, 0.3*cm))

        return elements

    @staticmethod
    def _build_premium_section(premium: Dict, styles):
        """Build premium features section."""
        elements = []

        elements.append(Paragraph("Premium-Analyse", styles['CustomHeading']))

        # Insurance Analysis
        if premium.get('insurance_analysis'):
            ins = premium['insurance_analysis']
            elements.append(Paragraph("Versicherungsempfehlungen", styles['CustomSubHeading']))

            total_cost = ins.get('total_annual_cost_estimate_eur', [0, 0])
            elements.append(Paragraph(
                f"Geschätzte jährliche Kosten: {total_cost[0]}-{total_cost[1]}€",
                styles['CustomBody']
            ))
            elements.append(Paragraph(
                f"Vergleich: {ins.get('comparison_to_average', 'N/A')}",
                styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.3*cm))

        # Benchmark Analysis
        if premium.get('benchmark_analysis'):
            bench = premium['benchmark_analysis']
            elements.append(Paragraph("Regionaler Vergleich", styles['CustomSubHeading']))
            elements.append(Paragraph(
                f"Region: {bench.get('state_name', 'N/A')}, {bench.get('city_name', 'N/A')}",
                styles['CustomBody']
            ))
            elements.append(Paragraph(
                f"Ranking: {bench.get('overall_ranking', 'N/A')}",
                styles['CustomBody']
            ))
            elements.append(Paragraph(
                bench.get('summary', ''),
                styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.3*cm))

        # Action Plan Summary
        if premium.get('action_plan'):
            plan = premium['action_plan']
            elements.append(Paragraph("Maßnahmenplan", styles['CustomSubHeading']))

            immediate = len(plan.get('immediate_actions', []))
            short_term = len(plan.get('short_term_actions', []))

            elements.append(Paragraph(
                f"Sofortmaßnahmen: {immediate}",
                styles['CustomBody']
            ))
            elements.append(Paragraph(
                f"Kurzfristige Maßnahmen: {short_term}",
                styles['CustomBody']
            ))

            total_cost = plan.get('total_estimated_cost_eur', [0, 0])
            elements.append(Paragraph(
                f"Gesamtinvestition: {total_cost[0]:,}-{total_cost[1]:,}€",
                styles['CustomBody']
            ))
            elements.append(Paragraph(
                f"Risikoreduktion: bis zu {plan.get('estimated_risk_reduction_percent', 0)}%",
                styles['CustomBody']
            ))

        return elements

    @staticmethod
    def _build_footer(styles):
        """Build PDF footer."""
        elements = []

        elements.append(Spacer(1, 1*cm))

        elements.append(Paragraph(
            "Hinweise und Haftungsausschluss",
            styles['CustomSubHeading']
        ))

        disclaimer = """
        Dieser Bericht wurde automatisch auf Basis öffentlich verfügbarer Daten erstellt.
        Die Risikoeinschätzungen basieren auf statistischen Analysen und historischen Daten.
        Für rechtsverbindliche Aussagen konsultieren Sie bitte einen Fachexperten.
        ImmoSafe DE übernimmt keine Haftung für Entscheidungen, die auf Basis dieses Berichts getroffen werden.
        """

        elements.append(Paragraph(disclaimer, styles['SmallText']))

        elements.append(Spacer(1, 0.5*cm))

        elements.append(Paragraph(
            "© 2024 ImmoSafe DE - Ihr Partner für sichere Immobilienentscheidungen",
            styles['SmallText']
        ))

        return elements

    @staticmethod
    def _get_risk_color(score: int):
        """Get color based on risk score."""
        if score >= 70:
            return colors.HexColor('#FEE2E2')  # Red light
        elif score >= 50:
            return colors.HexColor('#FEF3C7')  # Amber light
        elif score >= 30:
            return colors.HexColor('#DBEAFE')  # Blue light
        else:
            return colors.HexColor('#D1FAE5')  # Green light

    @staticmethod
    def _get_risk_assessment(score: int) -> str:
        """Get text assessment based on score."""
        if score >= 70:
            return "Hohes Risiko"
        elif score >= 50:
            return "Erhöhtes Risiko"
        elif score >= 30:
            return "Moderates Risiko"
        else:
            return "Geringes Risiko"
