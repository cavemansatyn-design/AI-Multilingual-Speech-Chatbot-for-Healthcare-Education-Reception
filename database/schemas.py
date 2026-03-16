"""
MongoDB document schemas (for validation and typing).
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    """Patient demographic data for storage."""

    name: str = ""
    age: Optional[str] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    patient_id: Optional[str] = None


class SymptomRecord(BaseModel):
    """Single symptom entry for storage."""

    symptom: str
    frequency: Optional[str] = None
    severity: Optional[int] = None
    duration: Optional[str] = None
    notes: Optional[str] = None


class StoredSymptomData(BaseModel):
    """Full symptom data document (e.g. per session)."""

    patient_id: Optional[str] = None
    symptoms: List[SymptomRecord] = Field(default_factory=list)
    duration: Optional[str] = None
    report_text: Optional[str] = None
