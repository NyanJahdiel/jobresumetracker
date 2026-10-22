from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job
from ..schemas import JobCreate, JobResponse

router = APIRouter(
    prefix="/jobs",
    tags=['jobs']
)

@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
    new_job = Job(**job.model_dump())

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/", response_model=list[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.id.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job
