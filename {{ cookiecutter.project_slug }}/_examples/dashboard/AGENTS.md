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
  file stem (e.g. `demo.parquet` → view `demo`).  Query with SQL.
- **UI components come from React Spectrum only.**  No raw `<button>`,
  `<select>`, `<input>`, or other HTML form elements.  Import from
  `@adobe/react-spectrum`.
- **Charts go through `useQuery` → `PlotFigure`** (Observable Plot).  Do not
  import charting libraries other than `@observablehq/plot`.
- **Maps use MapLibre GL** (`maplibre-gl`).  Do not add other map libraries.
- **Cross-page filter state lives in `src/store/filters.ts`** (Zustand).  Do
  not create local state that should be shared across pages; add it to the
  store instead.
- **Read `data/dictionary/<name>.json` before writing any query.**  Never
  guess column names, types, or value ranges.  The dictionary has everything.
- **Total parquet in `public/data/` must stay under 150 MB.**  This is
  enforced by `scripts/pull_data.py` (exit 1) and CI.  Do not commit large
  parquet files.

---

## Project Layout

```
dashboard/
├── src/
│   ├── main.tsx                  # React Spectrum Provider + BrowserRouter
│   ├── App.tsx                   # Nav shell + <Routes>
│   ├── store/filters.ts          # Zustand store — all cross-page state
│   ├── lib/
│   │   ├── duckdb.ts             # DuckDB-wasm singleton; registers views
│   │   └── useQuery.ts           # Typed React hook; module-level SQL cache
│   ├── components/
│   │   └── PlotFigure.tsx        # Observable Plot → React (≈15 lines)
│   └── pages/
│       ├── OverviewPage.tsx      # Picker (Zustand) + 2 Plot charts
│       ├── MapPage.tsx           # MapLibre + DuckDB point layer
│       └── ChicagoPage.tsx       # Choropleth + controls (the full-featured example)
├── data/dictionary/              # Committed schema JSON + MD (LLM-ingestible)
├── data.manifest.json            # Box URLs for remote datasets
├── public/data/                  # Local parquet (demo committed; others pulled)
├── scripts/pull_data.py          # Stdlib-only data puller; 150 MB gate
└── scripts/make_sample_geodata.py  # Rebuilds the community_areas GeoParquet
```

---

## How to Add a Page

1. Create `src/pages/YourPage.tsx`.  Model it on `OverviewPage.tsx` or
   `MapPage.tsx`.
2. Add a `<Route path="/your-page" element={<YourPage />} />` in `App.tsx`.
3. Add a `<Link to="/your-page">Your Page</Link>` (or a Spectrum `<Item>`) in
   the nav in `App.tsx`.
4. Use `useQuery<YourRowType>(sql)` to fetch data.  Render with
   `<PlotFigure options={Plot.plot({...})} />`.

Minimal page skeleton:

```tsx
import { useQuery } from "../lib/useQuery";
import { PlotFigure } from "../components/PlotFigure";
import * as Plot from "@observablehq/plot";

interface Row {
  city: string;
  value: number;
}

export function YourPage() {
  const { data, loading } = useQuery<Row>(
    "SELECT city, AVG(value) AS value FROM demo GROUP BY city"
  );

  if (loading) return <p>Loading…</p>;

  return (
    <PlotFigure
      options={Plot.plot({
        marks: [Plot.barY(data, { x: "city", y: "value" })],
      })}
    />
  );
}
```

---

## How to Add a Chart

Inside any page, call `useQuery` with a SQL string and pass the result to
`<PlotFigure>`:

```tsx
const { data, loading } = useQuery<{ date: string; value: number }>(
  "SELECT date, value FROM demo ORDER BY date"
);

<PlotFigure
  options={Plot.plot({
    marks: [Plot.line(data, { x: "date", y: "value" })],
  })}
/>
```

For Observable Plot documentation, see https://observablehq.com/plot/.

---

## How to Add a Filter

1. Add a field and setter to `FiltersState` in `src/store/filters.ts`:

   ```ts
   category: string;
   setCategory: (c: string) => void;
   ```

2. Initialise it in the `create` call (same file):

   ```ts
   category: "all",
   setCategory: (category) => set({ category }),
   ```

3. In any page, read and set it:

   ```tsx
   const { category, setCategory } = useFilters();
   ```

4. Include the value in your SQL `WHERE` clause:

   ```ts
   const sql =
     category === "all"
       ? "SELECT * FROM demo"
       : `SELECT * FROM demo WHERE category = '${category}'`;
   ```

---

## Commands

| Command | Description |
|---|---|
| `make dashboard-dev` | Start Vite dev server (localhost:5173) |
| `make dashboard-build` | TypeScript compile + production bundle |
| `make dashboard-data` | Pull parquet files from Box (150 MB gate) |
| `make dashboard-install` | `npm install` (first-time or after lockfile change) |
| `npm run test:e2e` | Playwright smoke tests against `vite preview` |

---

## Data Budget

- Hard limit: **150 MB** total parquet in `public/data/`.
- Enforced locally by `scripts/pull_data.py --force` (exit 1 on breach).
- Enforced in CI before every build.
- The committed demo file is ~50 KB and does not count toward the project budget.

---

## Columns in the Demo Dataset

See `data/dictionary/demo.json` for the authoritative schema.  Summary:

| Column | Type | Notes |
|---|---|---|
| `id` | INT | Row identifier |
| `date` | DATE | 365 days ending 2026-06-30 |
| `city` | VARCHAR | 5 cities with real lat/lon |
| `lat` | DOUBLE | Latitude |
| `lon` | DOUBLE | Longitude |
| `category` | VARCHAR | 4 values: A, B, C, D |
| `value` | DOUBLE | Synthetic sensor reading |

For any dataset you add, read `data/dictionary/<name>.json` — the structure is
the same: one entry per column with `dtype`, `null_count`, `n_unique`, `min`,
`max`, and `samples`.

## The community_areas Dataset (GeoParquet)

`community_areas.parquet` (pulled from Box; see `data/dictionary/community_areas.md`)
holds Chicago's 77 community areas with census socioeconomic indicators.  It is a
GeoParquet file: the `geometry` column is WKB (not queryable in DuckDB-wasm
without the spatial extension), so it also carries a `geometry_geojson` string
column — parse it with `JSON.parse` and feed it to MapLibre, as `ChicagoPage.tsx`
does.  `ChicagoPage.tsx` is the reference for choropleths, map hover popups, and
indicator pickers.
