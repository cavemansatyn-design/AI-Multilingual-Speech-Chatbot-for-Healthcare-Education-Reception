"""Tests for report generation."""

import pytest
from services.report_service import generate_report


def test_generate_report_basic():
    r = generate_report(
        symptoms=["headache", "dizziness"],
        frequency={"headache": "daily"},
        severity={"headache": 8},
        duration="1 week",
    )
    assert "headache" in r.report_text
    assert "8" in r.report_text or "daily" in r.report_text
    assert "1 week" in r.report_text
    assert r.structured_data is not None
    assert r.structured_data.symptoms == ["headache", "dizziness"]
