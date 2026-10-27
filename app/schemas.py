from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, EmailStr

class JobCreate(BaseModel): 
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    posting_text: str = Field(min_length=1)

class JobResponse(JobCreate): 
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = None
    location: str | None = None 

    professional_summary : str | None = None
    skills : str | None = None
    experience : str | None = None
    education: str | None = None
    projects: str | None = None
    certifications: str | None = None

class CandidateProfileResponse(CandidateProfileCreate):
    id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class CandidateProfileUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )
    phone: str | None = None
    location: str | None = None
    professional_summary: str | None = None
    skills: str | None = None
    experience: str | None = None
    education: str | None = None
    projects: str | None = None
    certifications: str | None = None


class ResumeProfileFields(BaseModel):
    """Only fields already present in the current CandidateProfile table."""

    model_config = ConfigDict(extra="forbid")

    professional_summary: str | None = Field(default=None, min_length=1, max_length=10000)
    skills: str | None = Field(default=None, min_length=1, max_length=10000)
    experience: str | None = Field(default=None, min_length=1, max_length=10000)
    education: str | None = Field(default=None, min_length=1, max_length=10000)
    projects: str | None = Field(default=None, min_length=1, max_length=10000)
    certifications: str | None = Field(default=None, min_length=1, max_length=10000)


class ResumeExtractionResponse(BaseModel):
    """Preview only. No profile changes until /resume/confirm."""

    filename: str
    file_type: str
    file_size_bytes: int
    character_count: int
    extracted_text: str
    suggested_fields: ResumeProfileFields
    unclassified_text: str = ""
    warnings: list[str] = Field(default_factory=list)


class ResumeConfirmRequest(BaseModel):
    """Explicitly confirmed fields after a user has reviewed the preview."""

    confirmed: Literal[True]
    fields: ResumeProfileFields
