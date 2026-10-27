
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job, User, CandidateProfile
from ..schemas import JobCreate, JobResponse
from .auth import get_current_user

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


def get_my_profile(db: Session, user_id: int):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user_id
    ).first()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Create your candidate profile first"
        )

    return profile


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_my_profile(db, current_user.id)

    job = Job(
        **data.model_dump(),
        profile_id=profile.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_my_profile(db, current_user.id)

    return db.query(Job).filter(
        Job.profile_id == profile.id
    ).order_by(Job.id.desc()).all()


@router.get(
    "/{job_id}",
    response_model=JobResponse
)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_my_profile(db, current_user.id)

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.profile_id == profile.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
