from datetime import datetime
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
