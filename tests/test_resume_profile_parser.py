"""Tests for deterministic resume suggestions and confirmation request validation."""

import pytest
from pydantic import ValidationError

from app.schemas import ResumeConfirmRequest
from app.services.resume_profile_parser import suggest_profile_fields


def test_suggests_only_explicit_sections():
    raw = (
        "Jordan Example\n"
        "Professional Summary\nBackend developer\n"
        "Technical Skills\nPython, FastAPI, MySQL\n"
        "Work Experience\nIT support internship\n"
        "Education\nBEng Computer Engineering\n"
        "Projects\nResume web service\n"
        "Certifications: Cloud Fundamentals\n"
    )
    result = suggest_profile_fields(raw)
    fields = result["suggested_fields"]
    assert fields["professional_summary"] == "Backend developer"
    assert fields["skills"] == "Python, FastAPI, MySQL"
    assert fields["experience"] == "IT support internship"
    assert fields["education"] == "BEng Computer Engineering"
    assert fields["projects"] == "Resume web service"
    assert fields["certifications"] == "Cloud Fundamentals"
    assert result["unclassified_text"] == "Jordan Example"


def test_no_headings_does_not_invent_fields():
    result = suggest_profile_fields("Jordan Example\nPython Developer")
    assert all(value is None for value in result["suggested_fields"].values())
    assert "Python Developer" in result["unclassified_text"]
    assert result["warnings"]


def test_confirmation_requires_explicit_true():
    with pytest.raises(ValidationError):
        ResumeConfirmRequest.model_validate({
            "confirmed": False,
            "fields": {"skills": "Python"}
        })


def test_unknown_fields_rejected():
    with pytest.raises(ValidationError):
        ResumeConfirmRequest.model_validate({
            "confirmed": True,
            "fields": {"user_id": 999, "skills": "Python"}
        })


def test_omitted_fields_are_not_part_of_update():
    req = ResumeConfirmRequest.model_validate({
        "confirmed": True,
        "fields": {"skills": "Python, FastAPI"}
    })
    assert req.fields.model_dump(exclude_unset=True) == {
        "skills": "Python, FastAPI"
    }


def test_oversized_section_is_not_autosuggested():
    result = suggest_profile_fields("Skills\n" + "x" * 10001)
    assert result["suggested_fields"]["skills"] is None
    assert "x" * 10001 in result["unclassified_text"]
