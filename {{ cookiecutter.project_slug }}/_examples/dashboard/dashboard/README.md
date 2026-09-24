# __PROJECT_NAME__ Dashboard

A static Vite + React dashboard that queries parquet files in-browser via
DuckDB-wasm.  No backend server required — deploy anywhere static files are
served.

---

## Commands

| Command | Description |
|---|---|
| `make dashboard-install` | Install Node dependencies (run once after generating the project) |
| `make dashboard-dev` | Start dev server at http://localhost:5173 |
| `make dashboard-build` | TypeScript compile + production bundle to `dist/` |
| `make dashboard-data` | Pull datasets from Box into `public/data/` (150 MB gate) |
| `npm run test:e2e` | Playwright smoke tests (build + `vite preview`); needs Node on your machine and a one-time `npx playwright install --with-deps chromium` |

After generating the project, run `make dashboard-data` once to pull the
example datasets (Chicago 311 requests + community areas) from Box, then
`make dashboard-dev`.  No Cloudflare setup is required to run locally.

---

## Data Flow

```
pipeline → parquet → Box public static link
                              ↓
                      data.manifest.json
                              ↓
                      scripts/pull_data.py
                              ↓
                      public/data/*.parquet   (max 150 MB total)
                              ↓
                      DuckDB-wasm (in the browser)
                              ↓
                      useQuery() hook → PlotFigure / MapLibre
```

The example manifest ships two datasets: `reqs_311` (a toy sample of Chicago
311 service requests) and `community_areas` (GeoParquet boundaries +
socioeconomic indicators).  Their schemas live in `data/dictionary/`.


---

Mentor setup (Cloudflare Pages project, GitHub secrets, Box datasets) is in
the project-root `PROJECT_SETUP.md`.  The step-by-step walkthrough is in the
project-root `TUTORIAL.md`.
