# Multi-stage-ish: copy the official uv binary instead of pip-installing it, then use
# it for both dependency install and running the app -- one tool, same as local dev.
FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Dependency layer first, separate from app code, so `uv sync` is only re-run (and
# re-cached) when pyproject.toml/uv.lock actually change -- not on every code edit.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# Listens on $PORT if the platform sets one (Render, Heroku-style hosts all assign
# their own port dynamically), falling back to 8080 for platforms with a fixed
# internal port (Fly's fly.toml expects 8080 -- see internal_port there). Shell form
# (not exec-form JSON array) so ${PORT:-8080} and the migration step below actually
# run at container start. --workers 2 is a starting point for a single small machine;
# there's no --reload here -- that's a dev-only flag, never for production.
#
# Migration runs here rather than as a separate pre-deploy step (which Fly's
# release_command gives us, but isn't guaranteed available on every host/plan) --
# `alembic upgrade head` is idempotent, so re-running it on every container start
# is harmless once the DB is already current.
EXPOSE 8080
CMD uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2
