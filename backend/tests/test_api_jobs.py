"""API-level tests: upload -> poll -> download, with the real LangGraph/Claude pipeline
stubbed out (BackgroundTasks would otherwise run it synchronously inside TestClient).
"""

import uuid

from fpdf import FPDF
from fastapi.testclient import TestClient

import app.routers.jobs as jobs_module
from app.database import SessionLocal
from app.main import app
from app.models import Job, JobStatus


def _fake_run_pipeline_success(job_id: str) -> None:
    """Stand-in for the real pipeline: skips Claude/LangGraph, writes a tiny real PDF."""
    db = SessionLocal()
    try:
        job = db.get(Job, uuid.UUID(job_id))
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, "fake report")
        report_path = job.csv_path.rsplit(".", 1)[0] + "_report.pdf"
        pdf.output(report_path)

        job.status = JobStatus.COMPLETE
        job.report_path = report_path
        db.commit()
    finally:
        db.close()


def test_create_job_rejects_non_csv():
    with TestClient(app) as client:
        resp = client.post("/jobs", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert resp.status_code == 400


def test_unknown_job_returns_404():
    with TestClient(app) as client:
        resp = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_create_job_then_poll_and_download(monkeypatch, sample_csv_path):
    monkeypatch.setattr(jobs_module, "run_pipeline", _fake_run_pipeline_success)

    with TestClient(app) as client:
        with open(sample_csv_path, "rb") as f:
            create_resp = client.post("/jobs", files={"file": ("sample_sales.csv", f, "text/csv")})
        assert create_resp.status_code == 201
        job_id = create_resp.json()["id"]

        status_resp = client.get(f"/jobs/{job_id}")
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["filename"] == "sample_sales.csv"
        assert body["status"] == "complete"  # TestClient runs BackgroundTasks inline
        assert body["report_ready"] is True

        download_resp = client.get(f"/jobs/{job_id}/download")
        assert download_resp.status_code == 200
        assert download_resp.headers["content-type"] == "application/pdf"
        assert len(download_resp.content) > 0


def test_download_before_complete_returns_409(monkeypatch, sample_csv_path):
    monkeypatch.setattr(jobs_module, "run_pipeline", lambda job_id: None)  # never completes

    with TestClient(app) as client:
        with open(sample_csv_path, "rb") as f:
            create_resp = client.post("/jobs", files={"file": ("sample_sales.csv", f, "text/csv")})
        job_id = create_resp.json()["id"]

        download_resp = client.get(f"/jobs/{job_id}/download")
        assert download_resp.status_code == 409
