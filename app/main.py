from contextlib import asynccontextmanager
from uuid import uuid4
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi.responses import Response
from sqlalchemy import func
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.kafka import publish_job
from app.models import Job


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="JobFlow",
    lifespan=lifespan,
)


class JobCreate(BaseModel):
    duration_seconds: int = Field(default=5, ge=1, le=30)


class JobResponse(BaseModel):
    id: str
    status: str
    duration_seconds: int
    result: str | None = None


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"service": "JobFlow", "status": "running"}


@app.post("/jobs", response_model=JobResponse)
def create_job(
    request: JobCreate,
    db: Session = Depends(get_db),
):
    job_id = str(uuid4())

    job = Job(
        id=job_id,
        status="queued",
        duration_seconds=request.duration_seconds,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        publish_job(
            job_id=job.id,
            duration_seconds=job.duration_seconds,
        )
    except Exception as exc:
        job.status = "publish_failed"
        job.result = str(exc)
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Could not send job to Kafka",
        )

    return job


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job
@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    statuses = [
        "queued",
        "processing",
        "completed",
        "failed",
        "publish_failed",
    ]

    lines = []

    for status in statuses:
        count = (
            db.query(func.count(Job.id))
            .filter(Job.status == status)
            .scalar()
        )

        lines.append(
            f'jobflow_jobs{{status="{status}"}} {count}'
        )

    total = db.query(func.count(Job.id)).scalar()

    lines.append(f"jobflow_jobs_total {total}")

    return Response(
        content="\n".join(lines) + "\n",
        media_type="text/plain",
    )
