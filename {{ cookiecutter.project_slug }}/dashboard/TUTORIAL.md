# Tutorial: Building and Extending Your Dashboard

This walkthrough takes you from zero to a live dashboard.
By the end you will have:

1. Started the dev server and seen charts on real demo data
2. Understood how data flows from your pipeline to the browser
3. Changed an existing chart
4. Added a filter backed by the Zustand store
5. Added a new page — framed as an agent task you hand to an LLM
6. Shipped the dashboard to a public Cloudflare Pages URL

Before you start, make sure you've completed the
[computer setup guide](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/clinic-computer-setup.md)
and have Docker and Make working on your machine.

---

## Step 1: Run It

Start the dev server with the committed demo data:

```bash
make dashboard-dev
```

Open http://localhost:5173.  You should see two pages in the nav bar:
**Overview** (bar and scatter charts) and **Map** (point layer on a base map).
Both pages load data from `public/data/demo.parquet` — no network calls, no
Box setup needed yet.

> **Troubleshooting.** If `make dashboard-dev` errors with "Docker not found",
> make sure Docker Desktop is running. If Node is not installed locally but
> Docker is, run `make dashboard-install && make dashboard-dev` once to install
> deps inside the container.  See `dashboard/README.md` for the full command
> reference.

---

## Step 2: How Data Flows

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

**The demo dataset** (`public/data/demo.parquet`) is committed to the repo so
the dashboard works immediately after generation.  It contains ~1 500 rows with
columns `id, date, city, lat, lon, category, value`.

**For real project data**, the workflow is:

1. In your pipeline, call `export_dataset(df, "my_dataset")` from
   `src/<module>/dashboard_export.py`.  This writes
   `dashboard/public/data/my_dataset.parquet` and a data dictionary to
   `dashboard/data/dictionary/my_dataset.{json,md}`.
2. Upload the parquet to Box and copy the **direct-download** static link.
3. Add an entry to `data.manifest.json`:
   ```json
   {"name": "my_dataset", "url": "https://uchicago.box.com/shared/static/..."}
   ```
4. Run `make dashboard-data` to pull the file into `public/data/`.

The data dictionary (committed JSON + Markdown) documents every column's type,
null count, unique-value count, and sample values.  Hand it to an LLM instead
of pasting raw data — see Step 5.

**DuckDB views** — every parquet in `public/data/` (including `demo`) is
registered at startup as a view named after the file stem.  A query like
`SELECT * FROM demo LIMIT 5` or `SELECT * FROM my_dataset WHERE city = 'Chicago'`
just works.

---

## Step 3: Change a Chart

Open `src/pages/OverviewPage.tsx`.  Find the `<PlotFigure options={...} />`
block.  The `options` prop is a plain
[Observable Plot](https://observablehq.com/plot/) spec — change it and the
browser hot-reloads.

For example, to switch from a bar chart to a line chart:

```tsx
<PlotFigure
  options={Plot.plot({
    marks: [
      Plot.line(data, { x: "date", y: "value", stroke: "category" }),
    ],
  })}
/>
```

`data` comes from `useQuery<Row>(sql)`, which returns an array of typed row
objects.  Look at the existing page for the full pattern.

> **Where do column names come from?** Read
> `data/dictionary/demo.json` — it lists every column with its type and sample
> values.  Never guess column names; always check the dictionary first.

---

## Step 4: Add a Filter

Filters that need to persist across pages live in the Zustand store at
`src/store/filters.ts`.  This is the single source of truth for all UI state.

**1. Extend the store.**  Open `src/store/filters.ts` and add your field:

```ts
interface FiltersState {
  city: string;           // existing field
  setCity: (c: string) => void;
  category: string;       // ← add this
  setCategory: (c: string) => void;
}

export const useFilters = create<FiltersState>()((set) => ({
  city: "all",
  setCity: (city) => set({ city }),
  category: "all",       // ← add this
  setCategory: (category) => set({ category }),
}));
```

**2. Wire up a Spectrum picker** in your page:

```tsx
const { category, setCategory } = useFilters();

<Picker
  label="Category"
  selectedKey={category}
  onSelectionChange={(k) => setCategory(String(k))}
>
  <Item key="all">All</Item>
  <Item key="A">A</Item>
  <Item key="B">B</Item>
</Picker>
```

**3. Use it in your SQL query:**

```ts
const sql =
  category === "all"
    ? "SELECT * FROM demo"
    : `SELECT * FROM demo WHERE category = '${category}'`;

const { data } = useQuery<Row>(sql);
```

Any other page that calls `useFilters()` will see the same `category` value.

---

## Step 5: Add a Page (Agent Task)

Adding a full page is a good task to hand to an LLM.  Prepare two files:

- `AGENTS.md` — the hard rules for this codebase (no backend, Spectrum-only
  components, query via `useQuery`, etc.)
- `data/dictionary/<name>.json` — the schema of the dataset you want to query

Then prompt your agent:

> Read `dashboard/AGENTS.md` and `dashboard/data/dictionary/demo.json`.
> Create `src/pages/TrendPage.tsx` that shows a line chart of average `value`
> over `date`, broken down by `category`.  Add a route and nav link in
> `src/App.tsx` so the page is reachable.

The agent has everything it needs: the rules, the column types, the patterns
from `OverviewPage.tsx` and `MapPage.tsx`, and the `useQuery` / `PlotFigure`
primitives.

After the agent writes the files:

1. Check the dev server — the new nav link should appear immediately.
2. Run `make dashboard-build` to make sure TypeScript compiles cleanly.

---

## Step 6: Ship

Push to `main`:

```bash
git add dashboard/
git commit -m "feat: update dashboard"
git push origin main
```

GitHub Actions runs automatically:

1. Pulls data from Box via `scripts/pull_data.py` (fails fast if total exceeds
   150 MB).
2. Runs `npm ci && npm run build`.
3. Runs the Playwright smoke test (Overview page renders charts, Map page
   renders).
4. Deploys to Cloudflare Pages: `https://<slug>-dashboard.pages.dev`.

The deploy step is skipped on pull requests — PRs only build and test.

> **One-time setup required** before the first deploy.  Ask your mentor to
> follow the Cloudflare and Box setup steps in `dashboard/README.md`.

---

## Quick Reference

### Commands

| Command | What it does |
|---|---|
| `make dashboard-install` | Install Node dependencies |
| `make dashboard-dev` | Dev server at localhost:5173 |
| `make dashboard-build` | Production build to `dist/` |
| `make dashboard-data` | Pull parquet files from Box |
| `npm run test:e2e` | Playwright smoke tests |

### Where things live

| Path | Purpose |
|---|---|
| `src/pages/` | One file per page |
| `src/store/filters.ts` | Cross-page filter state (Zustand) |
| `src/lib/duckdb.ts` | DuckDB-wasm singleton and query helper |
| `src/lib/useQuery.ts` | React hook wrapping the query helper |
| `src/components/PlotFigure.tsx` | Observable Plot → React wrapper |
| `data/dictionary/` | Per-dataset schema JSON + Markdown |
| `data.manifest.json` | Box URLs for remote datasets |
| `public/data/` | Local parquet files (not committed except demo) |

### Useful links

- [Observable Plot docs](https://observablehq.com/plot/)
- [React Spectrum components](https://react-spectrum.adobe.com/react-spectrum/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [DuckDB-wasm](https://duckdb.org/docs/api/wasm/overview)
- [Clinic coding standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md)

---

## What to Do Next

- **Explore the demo data.** Open a browser console, set a breakpoint, or add
  a `console.log(data)` after `useQuery` to inspect the rows your SQL returns.
- **Export your first real dataset.** Run `dashboard_export.py` on a DataFrame
  from your pipeline and add it to the manifest.
- **Hand a page to an LLM.** Follow Step 5 with your real data dictionary and
  see how quickly a new visualization comes together.
- **Ask your mentor** if you need help with the one-time Cloudflare or Box
  setup, or if the CI deploy step fails.
