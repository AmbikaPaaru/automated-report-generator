# Frontend (placeholder — not built yet)

This folder is a placeholder. The backend is complete and independently testable via `curl` /
the FastAPI Swagger UI (`http://localhost:8000/docs`); the frontend is a later implementation pass.

## Planned shape (Vite + React + TS)

```
frontend/
├── package.json / vite.config.ts / tsconfig.json / index.html
├── .env.example                # VITE_API_BASE_URL=http://localhost:8000
└── src/
    ├── main.tsx, App.tsx       # composes UploadForm -> JobStatus -> DownloadLink
    ├── api.ts                  # uploadCsv(), getJobStatus(), getDownloadUrl()
    ├── hooks/
    │   └── useJobPolling.ts    # polls GET /jobs/{id} every ~2s, stops on complete/failed
    └── components/
        ├── UploadForm.tsx      # file input + "Process" button -> POST /jobs
        ├── JobStatus.tsx       # pending/processing spinner, or failed + error_message
        └── DownloadLink.tsx    # <a href={GET /jobs/{id}/download}> once status === "complete"
```

Only 3 backend calls are needed: upload+kickoff (`POST /jobs`), poll (`GET /jobs/{id}`),
and download (`GET /jobs/{id}/download`, navigated to directly rather than fetched via JS).

To scaffold it when ready:

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```
