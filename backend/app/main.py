"""FastAPI app factory: logging, CORS, routers."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Load the repo-root .env before anything else reads os.environ (Anthropic SDK,
# Langfuse SDK, and our own Settings all rely on this having already happened).
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

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


async def catch_unhandled_exceptions(request: Request, call_next):
    # A plain @app.exception_handler(Exception) does NOT fix this: Starlette
    # attaches bare-Exception handlers to the outermost ServerErrorMiddleware,
    # which sits *outside* CORSMiddleware -- so the resulting 500 still has no
    # Access-Control-Allow-Origin header, and the browser reports a confusing
    # "CORS blocked" error instead of the real failure. A middleware added
    # *before* CORSMiddleware sits inside it in the stack, so the JSONResponse
    # it returns is still visible to CORSMiddleware afterwards.
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app = FastAPI(title="Automated Report Generator", version="0.1.0", lifespan=lifespan)

app.add_middleware(BaseHTTPMiddleware, dispatch=catch_unhandled_exceptions)

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
