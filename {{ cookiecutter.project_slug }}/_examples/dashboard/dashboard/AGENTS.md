# Dashboard Agent Context

This file is the authoritative guide for any AI agent (or human) working on
the dashboard.  Read it fully before writing any code.  `CLAUDE.md` points
here via `@AGENTS.md`.

---

## Hard Rules — Never Violate These

- **Static only.  NO backend ever.**  The dashboard reads parquet files in the
  browser via DuckDB-wasm.  There is no server, no API, no database connection.
  Do not add a backend, a serverless function, or a proxy.
- **Parquet lives in `public/data/`**, registered as DuckDB views named by
  file stem (e.g. `reqs_311.parquet` → view `reqs_311`).  Query with SQL.
- **UI components come from React Spectrum only.**  No raw `<button>`,
  `<select>`, `<input>`, or other HTML form elements.  Import from
  `@adobe/react-spectrum`.
- **Charts go through `useQuery` → `PlotFigure`** (Observable Plot).  Do not
  import charting libraries other than `@observablehq/plot`.
- **Maps use MapLibre GL** (`maplibre-gl`).  Do not add other map libraries.
- **Cross-tab filter state lives in `src/store/filters.ts`** (Zustand).  Do
  not create local state that should be shared across tabs; add it to the
  store instead.  Build WHERE clauses with `filterSql()` from the same file so
  every chart respects the global controls.
- **Read `data/dictionary/<name>.json` before writing any query.**  Never
  guess column names, types, or value ranges.  The dictionary has everything.
- **Never interpolate data values into raw HTML.**  MapLibre's
  `Popup.setHTML()` does not sanitize; a value from the data (an area name, a
  request type) could carry markup.  Use `setText()`, or build DOM nodes and
  assign data values with `textContent` before `setDOMContent()`, as
  `MapPage.tsx` does.
- **Everything in `public/data/` is published publicly.**  `vite build` copies
  it into `dist/`, which is deployed to a guessable public URL and cached.  Any
  URL you add to `data.manifest.json` becomes a world-readable download.
  Aggregate or de-identify before exporting, and never put partner-restricted
  data here.
- **Total parquet in `public/data/` must stay under 150 MB, and no single
  file over 25 MiB** (Cloudflare Pages rejects larger deploy assets).  Both
  are enforced by `scripts/pull_data.py` (exit 1) and CI.  Do not commit large
  parquet files.

---

## Project Layout

```
dashboard/
├── src/
│   ├── main.tsx                  # React Spectrum Provider
│   ├── App.tsx                   # Header, global filter controls, <Tabs>
│   ├── store/filters.ts          # Zustand store — all cross-tab state + filterSql()
│   ├── lib/
│   │   ├── duckdb.ts             # DuckDB-wasm singleton; registers views
│   │   └── useQuery.ts           # Typed React hook; module-level SQL cache
│   ├── components/
│   │   ├── PlotFigure.tsx        # Observable Plot → React (≈15 lines)
│   │   └── Card.tsx              # Bordered dashboard card (figure + figcaption)
│   └── pages/
│       ├── OverviewPage.tsx      # Trends tab: stat tiles + 4 Plot charts
│       ├── MapPage.tsx           # Map tab: choropleth + legend + ranking
│       └── SqlPage.tsx           # SQL tab: live query console + results table
├── data/dictionary/              # Committed schema JSON + MD (LLM-ingestible)
├── data.manifest.json            # Box URLs for remote datasets
├── public/data/                  # Local parquet (pulled from Box; git-ignored)
├── scripts/pull_data.py          # Stdlib-only data puller; 150 MB gate
└── scripts/make_sample_geodata.py  # Rebuilds the community_areas GeoParquet
```

---

## How to Add a Tab

The dashboard is a single page with Spectrum `<Tabs>` in `App.tsx`; each tab's
content is a component in `src/pages/`.

1. Create `src/pages/YourTab.tsx`.  Model it on `OverviewPage.tsx` or
   `MapPage.tsx`: return a flex-wrapped row of `<Card>` components.
2. In `App.tsx`, add `<Item key="your-tab">Your Tab</Item>` to the `<TabList>`
   and a matching `<Item key="your-tab"><YourTab /></Item>` to `<TabPanels>`.
3. Use `useQuery<YourRowType>(sql)` to fetch data, and
   `filterSql(requestType, yearRange)` from the store so the global controls
   apply.  Render charts with `<PlotFigure options={{...}} />` inside a
   `<Card>`.

Minimal tab skeleton:

```tsx
import * as Plot from "@observablehq/plot";
import PlotFigure from "../components/PlotFigure";
import Card from "../components/Card";
import { useQuery } from "../lib/useQuery";
import { useFilters, filterSql } from "../store/filters";

interface Row {
  request_type: string;
  n: number;
}

export default function YourTab() {
  const { requestType, yearRange } = useFilters();
  const { data, loading } = useQuery<Row>(
    `SELECT type_of_service_request AS request_type, CAST(COUNT(*) AS INT) AS n
     FROM reqs_311 WHERE ${filterSql(requestType, yearRange)}
     GROUP BY request_type`
  );

  if (loading || !data) return <p>Loading…</p>;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 16, paddingTop: 16 }}>
      <Card title="Requests by type">
        <PlotFigure
          options={{ marks: [Plot.barY(data, { x: "request_type", y: "n" })] }}
        />
      </Card>
    </div>
  );
}
```

---

## How to Add a Chart

Inside any page, call `useQuery` with a SQL string and pass the result to
`<PlotFigure>`:

```tsx
const { data, loading } = useQuery<{ month: string; n: number }>(
  `SELECT CAST(date_trunc('month', creation_date) AS VARCHAR) AS month,
          CAST(COUNT(*) AS INT) AS n
   FROM reqs_311 GROUP BY month ORDER BY month`
);

<PlotFigure
  options={{
    marks: [Plot.line(data, { x: (d) => new Date(d.month), y: "n" })],
  }}
/>
```

`options` takes the plain Plot spec object — `PlotFigure` calls `Plot.plot()`
itself.  Never wrap the spec in `Plot.plot(...)` at the call site.

Note: `CAST(COUNT(*) AS INT)` — DuckDB counts are BIGINT, which arrive in
JavaScript as `BigInt`; cast to INT in SQL to get plain numbers.

For Observable Plot documentation, see https://observablehq.com/plot/.

---

## How to Add a Filter

Global filters live in `src/store/filters.ts` and reach every chart through
`filterSql()`.  Do not build a local `WHERE` for a filter that should apply
across tabs.

1. Add the field and setter to `FiltersState` and to the `create` call:

   ```ts
   status: string
   setStatus: (status: string) => void
   // ...
   status: 'All',
   setStatus: (status) => set({ status }),
   ```

2. Add a parameter and clause to `filterSql` (escape single quotes as the
   existing `requestType` clause does), then update its callers in
   `OverviewPage.tsx` and `MapPage.tsx` — TypeScript lists them for you.

3. Add the control to the controls row in `App.tsx`, next to the request-type
   `Picker`.  Derive its options with a `SELECT DISTINCT` query; check
   `data/dictionary/<name>.json` for `NULL`s to exclude.

---

## Commands

| Command | Description |
|---|---|
| `make dashboard-dev` | Start Vite dev server (localhost:5173) |
| `make dashboard-build` | TypeScript compile + production bundle |
| `make dashboard-data` | Pull parquet files from Box (150 MB gate) |
| `make dashboard-install` | `npm install` (first-time or after lockfile change) |
| `npm run test:e2e` | Playwright smoke tests (build + `vite preview`); needs host Node + one-time `npx playwright install --with-deps chromium` — in docker=yes projects the suite normally runs in CI |

---

## Data Budget

- Hard limit: **150 MB** total parquet in `public/data/`.
- Enforced on every `scripts/pull_data.py` run (exit 1 on breach); `--force`
  only controls re-downloading.
- The pull skips files that already exist, so after a mentor updates a Box
  file or the manifest, run it with `--force` (or delete the local parquet)
  to pick up the new data.
- Enforced in CI before every build.
- **Over budget?** In order: drop columns no query uses, aggregate to the
  grain your charts actually plot (this example's charts need ~84k aggregate
  rows, not 1.6M raw ones), use zstd compression, simplify geometry
  (`make_sample_geodata.py` shows how), and only sample rows as a last
  resort — sampling makes every number wrong-by-sampling.

---

## The reqs_311 Dataset

See `data/dictionary/reqs_311.json` for the authoritative schema.  A toy
sample (~1.6M rows) of Chicago 311 service requests, pulled from Box via
`make dashboard-data`.  The dashboard only shows 2011–2017 (`DATA_YEARS` in
`src/store/filters.ts`): the city migrated 311 systems in late 2018, so later
years in the extract are partial.  Summary:

| Column | Type | Notes |
|---|---|---|
| `creation_date` | TIMESTAMP | 2011 – 2019 (the dashboard shows 2011–2017) |
| `status` | VARCHAR | `Completed` / `Open`; NULL for vacant-building reports |
| `completion_date` | TIMESTAMP | NULL for open and vacant-building requests |
| `type_of_service_request` | VARCHAR | 13 values (Graffiti Removal, Pothole in Street, …) |
| `community_area` | BIGINT | 1–77; joins to `community_areas.area_num` |

(Location columns from the raw 311 data are deliberately dropped — they were
82% of the file size, and every deploy asset must stay under 25 MiB.)

For any dataset you add, read `data/dictionary/<name>.json` — the structure is
the same: one entry per column with `dtype`, `nulls`, `n_unique`, `min`, and
`max`, plus `samples` only if the dataset was exported with
`include_samples=True` (off by default: dictionaries are committed to git).

## The community_areas Dataset (GeoParquet)

`community_areas.parquet` (pulled from Box; see `data/dictionary/community_areas.md`)
holds Chicago's 77 community areas with census socioeconomic indicators.  It is a
GeoParquet file: the `geometry` column is WKB (not queryable in DuckDB-wasm
without the spatial extension), so it also carries a `geometry_geojson` string
column — parse it with `JSON.parse` and feed it to MapLibre, as `MapPage.tsx`
does.  `MapPage.tsx` is the reference for choropleths, map hover popups, and
aggregating `reqs_311` to community areas (attribute join on
`community_area = area_num` — no spatial join needed).
