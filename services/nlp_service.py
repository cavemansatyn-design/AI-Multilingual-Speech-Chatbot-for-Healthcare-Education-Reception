"""
NLP service: symptom extraction via keyword matching and follow-up dialogue.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from utils.text_processing import normalize_text, tokenize
from utils.constants import (
    FREQUENCY_OPTIONS,
    SEVERITY_MIN,
    SEVERITY_MAX,
    DEFAULT_SYMPTOM_LIST_PATH,
)
from models.symptom_model import SymptomExtractionResult, SymptomFollowUpState


def _load_symptom_list(path: Optional[str] = None) -> List[str]:
    """Load predefined symptom list from JSON."""
    p = path or DEFAULT_SYMPTOM_LIST_PATH
    # Support both project root and package-relative paths
    for base in [Path.cwd(), Path(__file__).resolve().parent.parent]:
        full = base / p
        if full.exists():
            with open(full, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("symptoms", [])
    return []


# Module-level cache for symptom list
_SYMPTOM_LIST: Optional[List[str]] = None


def get_symptom_list() -> List[str]:
    """Return cached symptom list."""
    global _SYMPTOM_LIST
    if _SYMPTOM_LIST is None:
        _SYMPTOM_LIST = _load_symptom_list()
    return _SYMPTOM_LIST


def extract_symptoms_from_text(
    text: str,
    symptom_list: Optional[List[str]] = None,
) -> SymptomExtractionResult:
    """
    Normalize text, tokenize, and identify symptoms via keyword matching.

    Args:
        text: Raw user input.
        symptom_list: Override default symptom list.

    Returns:
        SymptomExtractionResult with symptoms list (frequency/severity/duration empty until follow-up).
    """
    normalized = normalize_text(text)
    tokens = set(tokenize(normalized))
    symptoms_ref = symptom_list or get_symptom_list()
    found = [s for s in symptoms_ref if s in tokens or s.replace(" ", "") in normalized]
    # Deduplicate and preserve order
    seen = set()
    symptoms = []
    for s in found:
        if s not in seen:
            seen.add(s)
            symptoms.append(s)
    return SymptomExtractionResult(symptoms=symptoms)


def parse_frequency_value(text: str) -> Optional[str]:
    """Map user reply to a frequency option."""
    t = normalize_text(text)
    for opt in FREQUENCY_OPTIONS:
        if opt in t or t in opt:
            return opt
    # Allow "daily", "weekly" etc.
    if "day" in t or "daily" in t:
        return "daily"
    if "week" in t or "weekly" in t:
        return "occasionally"
    if "rare" in t:
        return "rarely"
    if "often" in t or "frequent" in t:
        return "frequently"
    if "always" in t or "all" in t:
        return "all the time"
    return None


def parse_severity_value(text: str) -> Optional[int]:
    """Extract severity 1-10 from user reply."""
    t = normalize_text(text)
    digits = "".join(c for c in t if c.isdigit())
    if not digits:
        return None
    n = int(digits)
    if SEVERITY_MIN <= n <= SEVERITY_MAX:
        return n
    # Take first digit if multiple
    first = int(digits[0])
    if SEVERITY_MIN <= first <= SEVERITY_MAX:
        return first
    return None


def parse_duration_value(text: str) -> Optional[str]:
    """Extract duration phrase (e.g. 2 days, 1 week)."""
    t = normalize_text(text)
    if not t:
        return None
    # Keep as-is for report; optionally normalize later
    return t if len(t) < 50 else t[:50]


def get_next_follow_up(
    state: SymptomFollowUpState,
) -> Tuple[SymptomFollowUpState, Optional[str]]:
    """
    Determine next follow-up question and return updated state.
    Order: frequency per symptom -> severity per symptom -> duration (once).
    """
    symptoms = state.symptoms
    freq = state.frequency
    sev = state.severity
    pending = list(state.pending_symptoms) if state.pending_symptoms else []

    # 1) Ask frequency for each symptom not yet in frequency
    for s in symptoms:
        if s not in freq and s not in pending:
            pending.append(s)
    if pending:
        sym = pending[0]
        state.pending_symptoms = pending
        state.current_question = f"How often do you experience {sym}? (e.g. rarely, occasionally, frequently, daily)"
        return state, state.current_question

    # 2) Ask severity for each symptom not yet in severity
    for s in symptoms:
        if s not in sev:
            state.pending_symptoms = [s]
            state.current_question = f"On a scale of 1 to 10, how severe is your {s}?"
            return state, state.current_question

    # 3) Ask duration once
    if state.duration is None:
        state.current_question = "How long have you been experiencing these symptoms? (e.g. 2 days, 1 week, 1 month)"
        return state, state.current_question

    state.current_question = None
    return state, None


def apply_follow_up_answer(
    state: SymptomFollowUpState,
    answer: str,
) -> SymptomFollowUpState:
    """
    Interpret user answer and update state (frequency, severity, or duration).
    """
    state = state.model_copy(deep=True)
    pending = state.pending_symptoms
    freq = state.frequency
    sev = state.severity

    # If we were waiting for frequency
    if pending:
        sym = pending[0]
        val = parse_frequency_value(answer)
        if val is not None:
            freq = {**freq, sym: val}
            state.frequency = freq
            state.pending_symptoms = pending[1:]
            return state
        # If not recognized as frequency, try severity
        val = parse_severity_value(answer)
        if val is not None:
            sev = {**sev, sym: val}
            state.severity = sev
            state.pending_symptoms = pending[1:]
            return state

    # Check if any symptom still needs severity
    for s in state.symptoms:
        if s not in sev:
            val = parse_severity_value(answer)
            if val is not None:
                state.severity = {**state.severity, s: val}
                return state
            break

    # Duration
    if state.duration is None:
        dur = parse_duration_value(answer)
        if dur:
            state.duration = dur
    return state


def build_extraction_result_from_state(state: SymptomFollowUpState) -> SymptomExtractionResult:
    """Convert follow-up state to final SymptomExtractionResult."""
    return SymptomExtractionResult(
        symptoms=state.symptoms,
        frequency=state.frequency,
        severity=state.severity,
        duration=state.duration,
    )
