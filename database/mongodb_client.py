"""
MongoDB client: CRUD for users, patients, symptoms, reports.
"""

from typing import Optional, List, Dict, Any
from bson import ObjectId

from database.db_connection import get_database
from database.schemas import PatientDemographics, SymptomRecord, StoredSymptomData


def _oid(s: Optional[str]) -> Optional[ObjectId]:
    if not s:
        return None
    try:
        return ObjectId(s)
    except Exception:
        return None


class MongoDBClient:
    """High-level MongoDB operations for chatbot data."""

    def __init__(self):
        self.db = get_database()
        self.users = self.db["users"]
        self.patients = self.db["patients"]
        self.symptoms = self.db["symptoms"]
        self.reports = self.db["reports"]

    # ----- Users (for auth; password stored hashed by security_service) -----
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        doc = self.users.find_one({"username": username})
        return doc

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.users.find_one({"email": email})

    def create_user(self, username: str, email: str, hashed_password: str, role: str = "user", full_name: Optional[str] = None) -> str:
        doc = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "role": role,
            "full_name": full_name or "",
            "disabled": False,
        }
        r = self.users.insert_one(doc)
        return str(r.inserted_id)

    # ----- Patients (demographics) -----
    def insert_patient(self, demographics: PatientDemographics) -> str:
        doc = demographics.model_dump(exclude_none=True)
        r = self.patients.insert_one(doc)
        return str(r.inserted_id)

    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        oid = _oid(patient_id)
        if not oid:
            return None
        return self.patients.find_one({"_id": oid})

    # ----- Symptoms -----
    def insert_symptom_data(
        self,
        patient_id: Optional[str] = None,
        symptoms: List[Dict[str, Any]] = None,
        duration: Optional[str] = None,
        report_text: Optional[str] = None,
    ) -> str:
        doc = {
            "patient_id": patient_id,
            "symptoms": symptoms or [],
            "duration": duration,
            "report_text": report_text,
        }
        r = self.symptoms.insert_one(doc)
        return str(r.inserted_id)

    # ----- Reports -----
    def save_report(
        self,
        patient_id: str,
        report_text: str,
        structured: Optional[Dict[str, Any]] = None,
    ) -> str:
        doc = {
            "patient_id": patient_id,
            "report_text": report_text,
            "structured": structured or {},
        }
        r = self.reports.insert_one(doc)
        return str(r.inserted_id)

    def get_report_by_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Return latest report for patient."""
        return self.reports.find_one(
            {"patient_id": patient_id},
            sort=[("_id", -1)],
        )

    def get_reports_by_patient(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Return list of reports for patient."""
        return list(
            self.reports.find({"patient_id": patient_id})
            .sort("_id", -1)
            .limit(limit)
        )
