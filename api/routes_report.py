"""
Report retrieval by patient_id and PDF generation.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.dependencies import get_db_client, require_role
from database.mongodb_client import MongoDBClient
from models.report_model import PdfRequest
from models.user_model import UserInDB
from services.pdf_service import generate_patient_summary_pdf

router = APIRouter()


@router.post("/pdf", response_class=Response)
def generate_pdf(body: PdfRequest):
    """
    Generate and download a PDF summary of everything about the patient.
    Accepts JSON: report_text (required), structured, patient_name, patient_age, patient_gender, patient_contact.
    """
    pdf_bytes = generate_patient_summary_pdf(
        report_text=body.report_text,
        structured=body.structured,
        patient_name=body.patient_name or "",
        patient_age=body.patient_age or "",
        patient_gender=body.patient_gender or "",
        patient_contact=body.patient_contact or "",
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=patient-summary-report.pdf"},
    )


@router.get("/{patient_id}")
def get_report(
    patient_id: str,
    doctor_or_admin: UserInDB = Depends(require_role("doctor", "admin")),
    db: MongoDBClient = Depends(get_db_client),
):
    """
    Get latest report for patient_id. Requires doctor or admin role.
    """
    report = db.get_report_by_patient(patient_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    # Remove MongoDB _id for JSON response or return as str
    report["id"] = str(report.pop("_id"))
    return report


@router.get("/{patient_id}/history")
def get_report_history(
    patient_id: str,
    limit: int = 10,
    doctor_or_admin: UserInDB = Depends(require_role("doctor", "admin")),
    db: MongoDBClient = Depends(get_db_client),
):
    """Get report history for patient. Requires doctor or admin role."""
    reports = db.get_reports_by_patient(patient_id, limit=limit)
    for r in reports:
        r["id"] = str(r.pop("_id"))
    return {"patient_id": patient_id, "reports": reports}
