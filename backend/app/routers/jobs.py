"""Job upload, status polling/streaming, and report download endpoints."""

import json
import logging
import time
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Job, JobStatus
from app.schemas import JobCreateResponse, JobStatusResponse
from app.services.pipeline import run_pipeline
from app.services.storage import save_upload

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs"])

# --- SSE tuning for GET /{job_id}/events ---
SSE_POLL_SECONDS = 1.0
SSE_HEARTBEAT_EVERY_TICKS = 15  # a ": keep-alive" comment roughly every 15s
SSE_MAX_TICKS = 900  # ~15 minutes: safety cap so a stuck job can't hold a worker thread forever


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


@router.get("/{job_id}/events")
def stream_job_status(job_id: uuid.UUID):
    """Server-Sent Events alternative to polling GET /{job_id} every few seconds.

    This still polls the database under the hood -- `run_pipeline` (services/pipeline.py)
    writes status updates through its own plain SQLAlchemy session with no in-process
    pub/sub wired up to it, so there's no true "push the instant it changes" signal to
    hook into yet. What changes is *where* the polling happens: once, server-side, on
    a single held-open connection, instead of the browser firing a fresh GET request
    every 2 seconds. The browser gets pushed an update the moment this loop notices one.

    Written as a plain (sync) generator deliberately: Starlette iterates a non-async
    generator in a worker thread (`iterate_in_threadpool`) rather than on the event
    loop, so the blocking `time.sleep` / synchronous DB calls below never stall other
    requests -- consistent with the rest of this app's synchronous DB access.
    """

    def event_stream():
        last_status: str | None = None
        for tick in range(SSE_MAX_TICKS):
            # A short-lived Session per tick, exactly like run_pipeline's own session:
            # reusing one Session across the whole connection would keep returning the
            # same cached ORM object from its identity map instead of seeing the
            # pipeline's committed updates, and a request-scoped Depends(get_db)
            # session would hold a pooled DB connection checked out for as long as the
            # browser tab stays open.
            db = SessionLocal()
            try:
                job = db.get(Job, job_id)
            finally:
                db.close()

            if job is None:
                yield _sse_event("error", {"detail": "Job not found."})
                return

            if job.status.value != last_status:
                last_status = job.status.value
                payload = JobStatusResponse.model_validate(job).model_dump(mode="json")
                yield _sse_event("status", payload)

                if job.status in (JobStatus.COMPLETE, JobStatus.FAILED):
                    return  # terminal: nothing left to watch, close the stream
            elif tick % SSE_HEARTBEAT_EVERY_TICKS == 0:
                # Keeps intermediary proxies (and the browser) from treating a long
                # quiet "still processing" stretch as a dead connection.
                yield ": keep-alive\n\n"

            time.sleep(SSE_POLL_SECONDS)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable proxy buffering if ever deployed behind nginx
        },
    )


def _sse_event(event: str, data: dict) -> str:
    """Format one Server-Sent Event frame: `event: <name>` + JSON `data:`, blank-line terminated."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


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
