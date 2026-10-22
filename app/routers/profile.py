
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CandidateProfile
from ..schemas import CandidateProfileCreate, CandidateProfileResponse

router = APIRouter(
    prefix="/profiles",
    tags=["Candidate Profiles"]
)


@router.post(
    "/",
    response_model=CandidateProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    profile: CandidateProfileCreate,
    db: Session = Depends(get_db)
):
    new_profile = CandidateProfile(**profile.model_dump())

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get(
    "/{profile_id}",
    response_model=CandidateProfileResponse
)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db)
):
    profile = db.get(CandidateProfile, profile_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    return profile
