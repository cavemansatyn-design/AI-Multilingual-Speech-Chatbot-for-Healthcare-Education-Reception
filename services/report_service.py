"""
Report generation: convert structured symptom JSON to natural language.
Uses prompt template summarization (Option B). Can be extended for LLM.
"""

from typing import Dict, List, Optional

from models.report_model import ReportRequest, ReportResponse


def _template_summarize(
    symptoms: List[str],
    frequency: Dict[str, str],
    severity: Dict[str, int],
    duration: Optional[str],
    notes: Optional[str],
) -> str:
    """Build natural language report from structured data using templates."""
    parts = []
    for s in symptoms:
        freq = frequency.get(s, "unknown frequency")
        sev = severity.get(s)
        if sev is not None:
            parts.append(f"{freq} {s} (severity {sev}/10)")
        else:
            parts.append(f"{freq} {s}")
    if not parts:
        return "No symptoms reported."
    body = ", ".join(parts)
    if duration:
        body += f", lasting {duration}"
    body += "."
    if notes:
        body += f" Notes: {notes}"
    return f"Patient reports {body[0].lower()}{body[1:]}"


def generate_report(
    symptoms: List[str],
    frequency: Optional[Dict[str, str]] = None,
    severity: Optional[Dict[str, int]] = None,
    duration: Optional[str] = None,
    notes: Optional[str] = None,
) -> ReportResponse:
    """
    Convert structured symptom data into a natural language report.

    Args:
        symptoms: List of symptom names.
        frequency: Map symptom -> frequency string.
        severity: Map symptom -> 1-10.
        duration: Duration string (e.g. "1 week").
        notes: Optional notes.

    Returns:
        ReportResponse with report_text and optional structured_data.
    """
    frequency = frequency or {}
    severity = severity or {}
    report_text = _template_summarize(symptoms, frequency, severity, duration, notes)
    structured = ReportRequest(
        symptoms=symptoms,
        frequency=frequency,
        severity=severity,
        duration=duration,
        notes=notes,
    )
    return ReportResponse(report_text=report_text, structured_data=structured)
