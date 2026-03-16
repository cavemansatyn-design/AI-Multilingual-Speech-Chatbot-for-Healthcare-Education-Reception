"""
PDF generation for patient symptom summary reports.
Uses ReportLab (no LLM).
"""

from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_patient_summary_pdf(
    report_text: str,
    structured: Optional[Dict[str, Any]] = None,
    patient_name: str = "",
    patient_age: str = "",
    patient_gender: str = "",
    patient_contact: str = "",
) -> bytes:
    """
    Generate a PDF summary of everything about the patient.

    Args:
        report_text: Natural language report summary.
        structured: Dict with symptoms, frequency, severity, duration.
        patient_name: Patient full name.
        patient_age: Age or age range.
        patient_gender: Gender.
        patient_contact: Phone/email.

    Returns:
        PDF file content as bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        name="CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=12,
    )
    body_style = styles["Normal"]

    story = []

    # Title
    story.append(Paragraph("Patient Symptom Summary Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Patient demographics
    story.append(Paragraph("Patient Information", heading_style))
    demo_data = [
        ["Name", patient_name or "—"],
        ["Age", patient_age or "—"],
        ["Gender", patient_gender or "—"],
        ["Contact", patient_contact or "—"],
    ]
    demo_table = Table(demo_data, colWidths=[1.5 * inch, 4 * inch])
    demo_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("ALIGN", (1, 0), (1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(demo_table)
    story.append(Spacer(1, 0.25 * inch))

    # Chief complaints / symptoms table
    structured = structured or {}
    symptoms: List[str] = structured.get("symptoms", [])
    frequency: Dict[str, str] = structured.get("frequency", {})
    severity: Dict[str, int] = structured.get("severity", {})
    duration: Optional[str] = structured.get("duration")

    if symptoms:
        story.append(Paragraph("Chief Complaints (Symptoms)", heading_style))
        table_data = [["Symptom", "Frequency", "Severity (1–10)", "Notes"]]
        for s in symptoms:
            freq = frequency.get(s, "—")
            sev = severity.get(s)
            sev_str = str(sev) if sev is not None else "—"
            table_data.append([s, freq, sev_str, ""])
        if duration:
            table_data.append(["Duration (overall)", duration, "", ""])

        sym_table = Table(table_data, colWidths=[1.8 * inch, 1.5 * inch, 1.5 * inch, 2.2 * inch])
        sym_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
                ]
            )
        )
        story.append(sym_table)
        story.append(Spacer(1, 0.25 * inch))

    # Summary
    story.append(Paragraph("Clinical Summary", heading_style))
    summary_para = Paragraph(report_text.replace("\n", "<br/>"), body_style)
    story.append(summary_para)
    story.append(Spacer(1, 0.2 * inch))

    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(
        Paragraph(
            "<i>This report was generated by the Multilingual Symptom Chatbot. "
            "It is for informational purposes only and does not replace professional medical advice.</i>",
            ParagraphStyle(name="Footer", parent=body_style, fontSize=8, textColor=colors.grey),
        )
    )

    doc.build(story)
    return buffer.getvalue()
