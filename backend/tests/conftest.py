"""Shared pytest fixtures: an isolated SQLite test DB, no live Postgres/Anthropic needed.

Env vars are set *before* any `app.*` module is imported so pydantic-settings picks up
the test DB URL / dummy API key instead of whatever is in the real .env.
"""

import os
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DB_PATH = BACKEND_DIR / "tests" / "_test.db"

os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "")

from app.database import Base, engine  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _test_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def sample_csv_path() -> Path:
    return BACKEND_DIR / "sample_data" / "sample_sales.csv"
