
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, CandidateProfile
from ..schemas import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate
)
from .auth import get_current_user

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
    