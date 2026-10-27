
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, CandidateProfile
from ..schemas import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    ResumeExtractionResponse
)
from .auth import get_current_user
from ..services.resume_extractor import (
    MAX_RESUME_BYTES,
    ResumeExtractionError,
    extract_resume,
)

router = APIRouter(
    prefix="/profiles",
    tags=["Candidate Profiles"]
)


@router.post(
    "/me",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    data: CandidateProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Profile already exists"
        )

    profile_data = data.model_dump(exclude={"email"})

    profile = CandidateProfile(
        **profile_data,
        email=current_user.email,
        user_id=current_user.id
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


@router.get(
    "/me",
    response_model=CandidateProfileResponse
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    return profile


@router.patch(
    "/me",
    response_model=CandidateProfileResponse
)
def update_my_profile(
    data: CandidateProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )

    updates = data.model_dump(exclude_unset=True)

    if "full_name" in updates and updates["full_name"] is None:
        raise HTTPException(
            status_code=422,
            detail="Full name cannot be null"
        )

    for field, value in updates.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile


@router.post("/me/resume", response_model=ResumeExtractionResponse)
async def upload_resume(
    file: UploadFile = File(..., description="PDF or DOCX resume, up to 5 MB"),
    current_user: User = Depends(get_current_user),
):
    """Extract resume text for review; do not save or update the profile."""
    try:
        data = await file.read(MAX_RESUME_BYTES + 1)
    finally:
        await file.close()

    if len(data) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="Resume exceeds the 5 MB upload limit.")

    try:
        return await run_in_threadpool(extract_resume, file.filename or "", data)
    except ResumeExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
