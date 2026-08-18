"""Orchestration entrypoint invoked by FastAPI's BackgroundTasks.

Runs synchronously in a worker thread after the HTTP response has already been sent
(that's how BackgroundTasks works for sync callables). Owns its own DB session since
the request-scoped one is closed by the time this runs.
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone

from app.agent.graph import report_graph
from app.agent.tracing import langgraph_run_config
from app.database import SessionLocal
from app.models import Job, JobStatus
from app.services.pdf_report import build_pdf_report
from app.services.storage import report_path_for

logger = logging.getLogger(__name__)


def run_pipeline(job_id: str) -> None:
    # job_id travels through BackgroundTasks/LangGraph state as a plain str (keeps the
    # state JSON-serializable), but SQLAlchemy's Uuid(as_uuid=True) column needs an
    # actual uuid.UUID object for lookups -- passing the raw string works by accident
    # on some DBAPIs and fails outright on others (e.g. SQLite), so convert explicitly.
    job_pk = uuid.UUID(job_id)
    db = SessionLocal()
    try:
        job = db.get(Job, job_pk)
        if job is None:
            logger.error("job %s: not found in DB, aborting pipeline", job_id)
            return

        job.status = JobStatus.PROCESSING
        db.commit()
        logger.info("job %s: pipeline started", job_id)

        initial_state = {"job_id": job_id, "csv_path": job.csv_path}
        result_state = report_graph.invoke(initial_state, config=langgraph_run_config(job_id))

        output_path = report_path_for(job_id)
        build_pdf_report(
            job_id=job_id,
            filename=job.filename,
            df=result_state["dataframe"],
            analysis_plan=result_state["analysis_plan"],
            chart_paths=result_state.get("chart_paths", []),
            executive_summary=result_state["executive_summary"],
            output_path=output_path,
        )

        job.report_path = str(output_path)
        job.insights_json = result_state["analysis_plan"].model_dump_json()
        job.status = JobStatus.COMPLETE
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info("job %s: pipeline complete -> %s", job_id, output_path)

    except Exception:
        logger.exception("job %s: pipeline failed", job_id)
        db.rollback()
        job = db.get(Job, job_pk)
        if job is not None:
            job.status = JobStatus.FAILED
            job.error_message = traceback.format_exc(limit=5)[-4000:]
            db.commit()
    finally:
        db.close()
