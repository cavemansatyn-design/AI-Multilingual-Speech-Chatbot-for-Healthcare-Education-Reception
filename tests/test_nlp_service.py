"""
Tests for NLP service: normalization, symptom extraction, follow-up.
"""

import pytest
from utils.text_processing import normalize_text, tokenize
from services.nlp_service import (
    extract_symptoms_from_text,
    parse_frequency_value,
    parse_severity_value,
    parse_duration_value,
    get_next_follow_up,
    apply_follow_up_answer,
    build_extraction_result_from_state,
)
from models.symptom_model import SymptomFollowUpState


def test_normalize_text():
    assert normalize_text("  Hello, World!  ") == "hello world"
    assert normalize_text("") == ""
    assert normalize_text("FEVER & cough") == "fever cough"


def test_tokenize():
    assert tokenize("hello world") == ["hello", "world"]
    assert tokenize("") == []


def test_extract_symptoms():
    result = extract_symptoms_from_text("I have a headache and fever")
    assert "headache" in result.symptoms
    assert "fever" in result.symptoms

    result2 = extract_symptoms_from_text("nothing special here")
    assert len(result2.symptoms) == 0


def test_parse_frequency():
    assert parse_frequency_value("daily") == "daily"
    assert parse_frequency_value("rarely") == "rarely"
    assert parse_frequency_value("frequently") == "frequently"


def test_parse_severity():
    assert parse_severity_value("8") == 8
    assert parse_severity_value("about 7") == 7
    assert parse_severity_value("ten") is None or parse_severity_value("10") == 10


def test_parse_duration():
    assert parse_duration_value("1 week") == "1 week"
    assert parse_duration_value("2 days") == "2 days"


def test_follow_up_flow():
    state = SymptomFollowUpState(symptoms=["headache"])
    state, q1 = get_next_follow_up(state)
    assert q1 is not None
    assert "often" in q1.lower() or "frequency" in q1.lower() or "headache" in q1.lower()

    state = apply_follow_up_answer(state, "daily")
    state, q2 = get_next_follow_up(state)
    assert q2 is not None
    assert "scale" in q2.lower() or "1" in q2 or "10" in q2

    state = apply_follow_up_answer(state, "8")
    state, q3 = get_next_follow_up(state)
    assert q3 is not None
    assert "long" in q3.lower() or "duration" in q3.lower() or "week" in q3.lower()

    state = apply_follow_up_answer(state, "1 week")
    state, q4 = get_next_follow_up(state)
    assert q4 is None

    result = build_extraction_result_from_state(state)
    assert result.symptoms == ["headache"]
    assert result.frequency.get("headache") == "daily"
    assert result.severity.get("headache") == 8
    assert result.duration == "1 week"
