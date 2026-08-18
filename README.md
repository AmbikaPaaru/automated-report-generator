# Automated Report Generator

Upload a CSV, click Process, and a Claude-powered agent (orchestrated with **LangGraph**,
traced with **Langfuse**) decides what charts and insights matter, renders them, and
assembles a PDF report. Job status and metadata are tracked in **Postgres**.

```
User uploads CSV -> clicks "Process" -> Claude (agentic) analyzes + decides what
charts/insights matter -> backend generates PDF -> stores metadata in Postgres ->
user downloads report
```

## Status

- **Backend**: complete, working vertical slice (FastAPI + LangGraph + Claude + Postgres + fpdf2).
- **Frontend**: not built yet — see [frontend/README.md](frontend/README.md). Use `curl` or
  the Swagger UI at `http://localhost:8000/docs` to exercise the API in the meantime.

## Architecture

| Layer | Tool | Why |
|---|---|---|
| Backend API | FastAPI | Async-friendly, great for file uploads, auto-generates docs |
| Agent | LangGraph + `langchain-anthropic` (Claude) | Decides what to analyze; structured-output tool calls |
| Observability | Langfuse | Traces every node + every LLM call in one connected trace per job |
| Data processing | pandas, matplotlib | CSV profiling + chart rendering |
| Report | fpdf2 | Assembles the final PDF |
| Database | PostgreSQL + SQLAlchemy + Alembic | Job tracking, status polling |
| Background jobs | FastAPI `BackgroundTasks` | So "Process" doesn't block the request |
| Dependency mgmt | `uv` | Fast, single tool for venv + deps + lockfile |

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python dependency manager)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Postgres)
- An [Anthropic API key](https://console.anthropic.com/)
- A [Langfuse](https://cloud.langfuse.com/) account (free tier is fine) for tracing

## Setup

1. **Copy env template and fill in real secrets:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env`: set `ANTHROPIC_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`.
   (Postgres credentials in the template already match `docker-compose.yml`'s defaults —
   change them together if you customize either.)

2. **Start Postgres (+ Adminer for DB inspection):**
   ```bash
   docker compose up -d
   ```

3. **Install backend dependencies:**
   ```bash
   cd backend
   uv sync
   ```

4. **Run database migrations:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the backend:**
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

6. **Try it** — via the sample dataset at `backend/sample_data/sample_sales.csv`:
   ```bash
   curl -F "file=@sample_data/sample_sales.csv" http://localhost:8000/jobs
   # -> {"id": "...", "status": "pending", ...}

   curl http://localhost:8000/jobs/<id>
   # poll until "status": "complete"

   curl -OJ http://localhost:8000/jobs/<id>/download
   ```
   Or open `http://localhost:8000/docs` for an interactive Swagger UI.

7. **Inspect the DB** via Adminer at `http://localhost:8080` (system: PostgreSQL, server: `db`,
   credentials from `.env`).

8. **Check traces** in your Langfuse project dashboard — each job appears as a session
   (tagged by job id) showing the `plan_analysis` and `summarize` Claude calls.

## Running tests

No live API key, Postgres, or Docker needed — tests use a local SQLite DB and mock every
Claude call:
```bash
cd backend
uv run pytest -q
```

## Project layout

```
python_ARG/
├── docker-compose.yml     # Postgres + Adminer
├── backend/               # FastAPI + LangGraph + Claude (see backend/README.md)
└── frontend/              # placeholder — see frontend/README.md
```

See the backend's module docstrings (`app/agent/`, `app/services/`, `app/routers/`) for
how the pipeline is wired together: `load_data -> plan_analysis -> generate_charts ->
summarize -> PDF -> Postgres`.
