"""FastAPI app factory: logging, CORS, routers."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load the repo-root .env before anything else reads os.environ (Anthropic SDK,
# Langfuse SDK, and our own Settings all rely on this having already happened).
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import configure_logging
from app.routers import jobs
from app.services.storage import ensure_storage_dirs

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_storage_dirs()
    logger.info("Automated Report Generator backend started (model=%s)", settings.anthropic_model)
    yield


app = FastAPI(title="Automated Report Generator", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
