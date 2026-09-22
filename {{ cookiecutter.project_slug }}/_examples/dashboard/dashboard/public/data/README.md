# public/data/

This directory holds parquet files that DuckDB-wasm queries in the browser.

## What lives here

| File | Source | Committed? |
|---|---|---|
| `reqs_311.parquet` | Toy sample of Chicago 311 service requests; hosted on Box, pulled via `scripts/pull_data.py` | No |
| `community_areas.parquet` | GeoParquet built by `scripts/make_sample_geodata.py`; hosted on Box, pulled via `scripts/pull_data.py` | No |
| `*.parquet` (project data) | Pulled from Box via `scripts/pull_data.py` | No |

Run `make dashboard-data` to populate this directory.

## Size limit

Total parquet in this directory must stay **under 150 MB**, and no single file
over **25 MiB** (Cloudflare Pages rejects larger deploy assets).  The pull
script enforces both and exits non-zero on a breach.  CI also checks before
every build.

Over budget?  In order: drop columns no query uses, pre-aggregate to the grain
your charts actually plot, use zstd compression, simplify geometry, and only
sample rows as a last resort (sampling makes every number wrong-by-sampling).

## How to add a dataset

1. Export a parquet from your pipeline:
   ```python
   from <module>.dashboard_export import export_dataset
   export_dataset(df, "my_dataset")   # writes public/data/my_dataset.parquet
   ```
2. Upload to Box, get the static link, add it to `data.manifest.json`.
3. Run `make dashboard-data` to pull it locally.

Each entry in `data.manifest.json` is registered as a DuckDB view named after
its `name`.  A file that only exists locally so far still needs an entry — use
an empty URL (`{ "name": "my_dataset", "url": "" }`; `pull_data.py` skips it)
and it can be queried with `SELECT * FROM my_dataset`.

## .gitignore

Parquet files are git-ignored.  Do not commit large datasets.
The file `data.manifest.json` and `data/dictionary/` entries are committed
instead — that is how collaborators reproduce the same data locally.
