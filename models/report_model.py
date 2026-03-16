"""
Report generation request/response models.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ReportRequest(BaseModel):
    """Structured symptom data used to generate a report."""

    symptoms: List[str]
    frequency: Dict[str, str] = {}
    severity: Dict[str, int] = {}
    duration: Optional[str] = None
    notes: Optional[str] = None


class ReportResponse(BaseModel):
    """Generated natural language report."""

    report_text: str
    structured_data: Optional[ReportRequest] = None


class PdfRequest(BaseModel):
    """Request body for PDF generation."""

    report_text: str
    structured: Optional[Dict[str, Any]] = None
    patient_name: str = ""
    patient_age: str = ""
    patient_gender: str = ""
    patient_contact: str = ""
