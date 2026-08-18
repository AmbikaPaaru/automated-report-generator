"""Filesystem helpers: where uploads/charts/reports live, and how uploads get saved."""

import shutil
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


def ensure_storage_dirs() -> None:
    for path in (settings.resolved_upload_dir(), settings.resolved_chart_dir(), settings.resolved_report_dir()):
        path.mkdir(parents=True, exist_ok=True)


def save_upload(file: UploadFile, job_id: str) -> Path:
    """Persist an uploaded CSV to disk, named by job id, and return its path."""
    ensure_storage_dirs()
    suffix = Path(file.filename or "upload.csv").suffix or ".csv"
    dest = settings.resolved_upload_dir() / f"{job_id}{suffix}"
    with dest.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)
    return dest


def report_path_for(job_id: str) -> Path:
    return settings.resolved_report_dir() / f"{job_id}.pdf"
