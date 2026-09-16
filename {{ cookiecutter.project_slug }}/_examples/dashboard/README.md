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
| `npm run test:e2e` | Playwright smoke tests against `vite preview` |

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

## One-Time Mentor Setup

Complete these steps once per project before the first deploy.  Students do
not need to do this.

### 1. Create the Cloudflare Pages project

1. Log in to [Cloudflare](https://dash.cloudflare.com) and go to
   **Workers & Pages → Create → Pages**.
2. Choose **Direct Upload** (the CI workflow uses Wrangler, not the Git
   integration).
3. Name the project exactly **`<slug>-dashboard`**, where `<slug>` is the
   value of `cookiecutter.project_slug` used when the repo was generated (e.g.
   `my-clinic-project-dashboard`).
4. Complete the creation wizard — an initial deploy is not required.
5. **Set the project's production branch to `main`** (Settings → Builds &
   deployments).  CI deploys with `--branch=main`; if the production branch is
   anything else, every deploy silently lands on a preview URL and the public
   `pages.dev` URL never updates.  (If you create the project with the CLI
   instead, pass `--production-branch=main` — wrangler's default is
   `production`, not `main`.)

### 2. Generate a Cloudflare API token

1. In Cloudflare, go to **My Profile → API Tokens → Create Token**.
2. Choose **Create Custom Token** with a single permission:
   **Account → Cloudflare Pages → Edit**.  (Do not use the broader
   Workers template — this token lives in GitHub secrets, so give it the
   minimum scope that can deploy Pages.)
3. Scope the token to your account.
4. Copy the token — you will only see it once.

### 3. Add GitHub repository secrets

In the GitHub repository go to **Settings → Secrets and variables → Actions**
and add:

| Secret name | Value |
|---|---|
| `CLOUDFLARE_API_TOKEN` | The token from step 2 |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare account ID (visible in the Cloudflare dashboard URL or the Overview page) |

After these secrets are set, every push to `main` triggers a deploy.  The live
URL will be:

```
https://<slug>-dashboard.pages.dev
```

### 4. Add datasets via Box

> **Everything in `public/data/` is published to the open internet.**  The
> build copies it into the deployed site at a guessable public URL.  Only add
> datasets that are aggregated or de-identified enough to be world-readable —
> never partner-restricted data.

For each dataset your pipeline produces:

1. Export a parquet file from your pipeline using `export_dataset(df, "name")`
   in `src/<module>/dashboard_export.py`.
2. Upload the parquet to the project's Box folder.
3. In Box, open the file, click **Share → Create shared link**, set access to
   **People with the link** (anything more restrictive returns a login page
   instead of the file, which breaks `pull_data.py` and CI), and set the
   **link expiration** far in the future (an expired link breaks every
   student's `make dashboard-data` and the CI deploy).  Copy the
   **direct download** URL.  It will look like:
   ```
   https://uchicago.box.com/shared/static/<hash>.parquet
   ```
4. Open `data.manifest.json` and add an entry:
   ```json
   { "name": "my_dataset", "url": "https://uchicago.box.com/shared/static/..." }
   ```
5. Run `make dashboard-data` to pull the file locally and verify the size gate
   passes.
6. Commit `data.manifest.json` and the updated `data/dictionary/` files (not
   the parquet itself).

Students can then run `make dashboard-data` to pull the datasets whenever they
set up the project.
