# Automated Report Generator

Upload a CSV, click Process, and an LLM agent (orchestrated with **LangGraph**, called
through an internal **LiteLLM gateway**, traced with **Langfuse**) decides what charts
and insights matter, renders them, and assembles a PDF report. Job status and metadata
are tracked in **Postgres**.

```
User uploads CSV -> clicks "Process" -> LLM (agentic) analyzes + decides what
charts/insights matter -> backend generates PDF -> stores metadata in Postgres ->
user downloads report
```

## Status

- **Backend**: complete, working vertical slice (FastAPI + LangGraph + an LLM gateway + Postgres + fpdf2).
- **Frontend**: a working Next.js app — see [frontend/README.md](frontend/README.md). You can
  also use `curl` or the Swagger UI at `http://localhost:8000/docs` to exercise the API directly.

## Architecture

| Layer | Tool | Why |
|---|---|---|
| Backend API | FastAPI | Async-friendly, great for file uploads, auto-generates docs |
| Agent | LangGraph + `langchain-openai` via an internal LLM gateway | Decides what to analyze; structured-output tool calls |
| Observability | Langfuse | Traces every node + every LLM call in one connected trace per job |
| Data processing | pandas, matplotlib | CSV profiling + chart rendering |
| Report | fpdf2 | Assembles the final PDF |
| Database | PostgreSQL + SQLAlchemy + Alembic | Job tracking, status polling |
| Background jobs | FastAPI `BackgroundTasks` | So "Process" doesn't block the request |
| Dependency mgmt | `uv` | Fast, single tool for venv + deps + lockfile |

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python dependency manager)
- Postgres reachable from your machine (Docker, a local install, or a hosted instance
  like Supabase — see `backend/app/database.py`'s comments; the models are dialect-agnostic
  and also run fine against SQLite for local dev with no Postgres at all)
- Access to the internal LLM gateway (`LLM_GATEWAY_URL` + `LLM_API_KEY`) — this typically
  means being connected to the corporate network/VPN, since the gateway is only reachable
  from inside it
- A [Langfuse](https://cloud.langfuse.com/) account (free tier is fine) for tracing

## Setup

1. **Copy env template and fill in real secrets:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env`: set `LLM_GATEWAY_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LANGFUSE_PUBLIC_KEY`,
   `LANGFUSE_SECRET_KEY`, and `DATABASE_URL` for whichever Postgres you're pointing at
   (Docker, Supabase, a local install — anything reachable via a normal connection string).

2. **Start Postgres** (skip this if you're pointing `DATABASE_URL` at an already-hosted
   instance, e.g. Supabase, or at local SQLite):
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
   # or: curl -N http://localhost:8000/jobs/<id>/events   (Server-Sent Events, pushed instead of polled)

   curl -OJ http://localhost:8000/jobs/<id>/download
   ```
   Or open `http://localhost:8000/docs` for an interactive Swagger UI, or run the frontend
   (see [frontend/README.md](frontend/README.md)) and do all of this through the UI.

7. **Inspect the DB** via Adminer at `http://localhost:8080` if using the Docker Postgres
   (system: PostgreSQL, server: `db`, credentials from `.env`) — or your hosted provider's
   own dashboard (e.g. Supabase's Table Editor) if pointing elsewhere.

8. **Check traces** in your Langfuse project dashboard — each job appears as a session
   (tagged by job id) showing the `plan_analysis` and `summarize` LLM calls.

## Running tests

No live gateway access, Postgres, or Docker needed — tests use a local SQLite DB and mock
every LLM call:
```bash
cd backend
uv run pytest -q
```

## Project layout

```
python_ARG/
├── docker-compose.yml     # optional local Postgres + Adminer
├── backend/               # FastAPI + LangGraph + LLM gateway (see backend/README.md)
└── frontend/              # Next.js UI — see frontend/README.md
```

See the backend's module docstrings (`app/agent/`, `app/services/`, `app/routers/`) for
how the pipeline is wired together: `load_data -> plan_analysis -> generate_charts ->
summarize -> PDF -> Postgres`.
