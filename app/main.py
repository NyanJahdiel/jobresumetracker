from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import jobs

app = FastAPI(title='Job Resume Tracker')

Base.metadata.create_all(bind=engine)

app.include_router(jobs.router)

@app.get("/")
def health_check():
    return {'status': 'ok'}  