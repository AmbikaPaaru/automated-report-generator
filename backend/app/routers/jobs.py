"""Job upload, status polling, and report download endpoints."""

import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobStatus
from app.schemas import JobCreateResponse, JobStatusResponse
from app.services.pipeline import run_pipeline
from app.services.storage import save_upload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobCreateResponse, status_code=201)
def create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Job:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    job = Job(filename=file.filename, status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)

    csv_path = save_upload(file, str(job.id))
    job.csv_path = str(csv_path)
    db.commit()
    db.refresh(job)

    logger.info("job %s: created for file %s", job.id, job.filename)
    background_tasks.add_task(run_pipeline, job_id=str(job.id))
    return job


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.get("/{job_id}/download")
def download_report(job_id: uuid.UUID, db: Session = Depends(get_db)) -> FileResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != JobStatus.COMPLETE or not job.report_path:
        raise HTTPException(status_code=409, detail=f"Report not ready (status={job.status.value}).")

    return FileResponse(
        job.report_path,
        media_type="application/pdf",
        filename=f"report_{job.filename.rsplit('.', 1)[0]}.pdf",
    )
