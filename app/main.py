from fastapi import FastAPI

from .database import Base, engine
from . import models 
from . routers import jobs, profile

app = FastAPI(
    title= "AI Resume Tailoring Platform",
    description= "Generate custom resumes and cvs using AI"
)

Base.metadata.create_all(bind = engine)

app.include_router(jobs.router)
app.include_router(profile.router)

@app.get("/")
def health_check():
    return {"status": "ok"}
