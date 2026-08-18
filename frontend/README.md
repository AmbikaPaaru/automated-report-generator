# Frontend

Next.js (App Router, TypeScript) + Redux Toolkit / RTK Query. A single page: upload a
CSV, watch status poll to completion, download the PDF.

## Stack

- **Next.js 16** (App Router, Turbopack) — see `AGENTS.md`/`CLAUDE.md` in this folder;
  Next auto-generates those to flag that this major version has real breaking changes
  vs. older training data (no `next.config.js` boilerplate, `next lint` removed in favor
  of running `eslint` directly, Tailwind v4's CSS-first config, etc.).
- **Redux Toolkit + RTK Query** for API state — `src/features/jobs/jobsApi.ts` defines
  the 3 backend calls this app needs (`createJob`, `getJobStatus`, `downloadUrlFor`).
  Polling is handled by RTK Query's own `pollingInterval` option (see
  `src/components/JobStatusCard.tsx`), not a hand-rolled `setInterval`.
- **Tailwind CSS v4** for styling (no `tailwind.config.ts` needed at this size — v4
  auto-detects template files).

## Structure

```
src/
├── app/
│   ├── layout.tsx        # root layout, wraps children in <Providers>
│   ├── page.tsx           # the whole flow: UploadForm -> JobStatusCard
│   ├── providers.tsx      # client component holding the Redux store (one per mount)
│   └── globals.css
├── lib/
│   ├── store.ts           # configureStore + RTK Query middleware/listeners
│   └── hooks.ts           # typed useAppDispatch / useAppSelector
├── features/jobs/
│   ├── jobsApi.ts          # RTK Query slice: createJob, getJobStatus, downloadUrlFor()
│   └── types.ts            # mirrors backend/app/schemas.py
└── components/
    ├── UploadForm.tsx       # file input + "Process" -> POST /jobs
    ├── JobStatusCard.tsx     # polls GET /jobs/{id} until complete/failed
    └── DownloadButton.tsx    # links directly to GET /jobs/{id}/download
```

## Setup

```bash
cp .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL, defaults to localhost:8000
npm install
npm run dev
```

Open `http://localhost:3000`. The backend must be running (see the root
[README.md](../README.md)) and its `FRONTEND_ORIGIN` must match this app's origin
(`http://localhost:3000` by default on both sides already).

## Scripts

- `npm run dev` — dev server (Turbopack)
- `npm run build` — production build
- `npm run lint` — ESLint (flat config, `eslint.config.mjs`)
- `npm run typecheck` — `tsc --noEmit`
