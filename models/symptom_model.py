"""
Symptom extraction and follow-up dialogue models.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class SymptomExtractionResult(BaseModel):
    """Structured output from symptom NLP extraction."""

    symptoms: List[str] = Field(default_factory=list)
    frequency: Dict[str, str] = Field(default_factory=dict)
    severity: Dict[str, int] = Field(default_factory=dict)
    duration: Optional[str] = None
    notes: Optional[str] = None


class SymptomFollowUpState(BaseModel):
    """State for multi-turn follow-up (frequency, severity, duration)."""

    symptoms: List[str] = Field(default_factory=list)
    frequency: Dict[str, str] = Field(default_factory=dict)
    severity: Dict[str, int] = Field(default_factory=dict)
    duration: Optional[str] = None
    current_question: Optional[str] = None
    pending_symptoms: List[str] = Field(default_factory=list)


class SymptomInput(BaseModel):
    """User text/audio input for chat."""

    text: Optional[str] = None
    language: str = "en"
