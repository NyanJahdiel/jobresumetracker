from fastapi import FastAPI

app = FastAPI(title='Job Resume Tracker')

@app.get("/")
def health_check():
    return {'status '}  