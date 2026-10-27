from sqlalchemy import Column, Boolean, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base 


from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    Boolean,
    func
)
from sqlalchemy.orm import relationship

from .database import Base
from sqlalchemy import UniqueConstraint

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    profile_id = Column(
        Integer, 
        ForeignKey("candidate_profiles.id"),
        nullable= True,
        index=True
    )

    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    posting_text = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    applications = relationship(
        "Application",
        back_populates="job"
    )

    profile = relationship(
        "CandidateProfile",
        back_populates="jobs"
    )


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="drafted"
    )

    applied_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    job = relationship(
        "Job",
        back_populates="applications"
    )

    materials = relationship(
        "Material",
        back_populates="application"
    )

    tailoring_runs = relationship(
        "TailoringRun",
        back_populates="application"
    )


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False
    )

    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)

    application = relationship(
        "Application",
        back_populates="materials"
    )


class TailoringRun(Base):
    __tablename__ = "tailoring_runs"

    id = Column(Integer, primary_key=True, index=True)

    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False
    )

    prompt = Column(Text, nullable=False)
    output = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    application = relationship(
        "Application",
        back_populates="tailoring_runs"
    )


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)

    professional_summary = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    experience = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    projects = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    jobs = relationship(
    "Job",
    back_populates="profile"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="profile"
    )
    
class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer, 
        primary_key= True, 
        index= True
    )

    email = Column(
        String(255),
        unique= True,
        nullable= False,
        index= True
    )
    hashed_password = Column(
        String(255),
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    profile = relationship(
        "CandidateProfile",
        back_populates="user",
        uselist=False
    )
