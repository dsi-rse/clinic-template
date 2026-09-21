{% if cookiecutter.examples == 'data-science' and cookiecutter.dashboard == 'yes' %}
# Tutorial

This tutorial has two parts.  **Part 1** builds and runs a strategy in the
pipeline.  **Part 2** puts the results in a browser dashboard.  Do them in
order — Part 2 uses the output of Part 1.

---

{% endif %}
{% if cookiecutter.examples == 'data-science' %}
# Tutorial: Building and Running Your First Strategy

This walkthrough takes you from zero to a working end-to-end run.
By the end you will have:

1. Started a Docker container and attached VS Code to it
2. Written a new strategy that processes a single input
3. Tested it interactively in a notebook
4. Run it across the full dataset and inspected the evaluation results in a notebook
5. Run the same thing from the command line

Before you start, make sure you've completed the
[computer setup guide](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/clinic-computer-setup.md)
and have Docker, VS Code, and Make working on your machine. You should also
have
[Box Drive](https://www.box.com/resources/downloads) installed, signed in
with your UChicago account, and syncing (your mentor will have shared the
data folder with you).

For general clinic expectations around code quality, documentation, and
repository standards, see the
[coding standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md).

---

## Step 1: Start the Docker Container

All of your work — notebooks and command-line runs — happens inside a Docker
container. This keeps everyone on the team using the exact same environment
regardless of what operating system they're on.

Open a terminal, `cd` into the project directory, and run:

```bash
make run-interactive
```

This builds the Docker image (if it hasn't been built yet) and drops you into
a bash shell inside the container. Leave this terminal open — you'll come back to it for command-line runs later.

### Verify the install

Inside the container, run:

```bash
{{ cookiecutter.project_slug }} --help
```

You should see a list of available commands. If you get a "command not found"
error, ask your mentor for help.

> **Troubleshooting.** If `make run-interactive` fails, check that Docker
> Desktop is running and that your terminal is a Unix shell (Terminal on Mac,
> WSL on Windows — *not* PowerShell). See the clinic
> [Docker FAQ](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/Docker.md)
> for common issues.

---

## Step 2: Attach VS Code to the Container

You'll write code and run notebooks from inside VS Code, attached to the
same container you just started.

1. Open VS Code
2. Open the Command Palette (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on
   Windows/Linux)
3. Type **Dev Containers: Attach to Running Container** and select it
4. Pick the container from the list (it will have `{{ cookiecutter.project_slug }}`
   in the name)

VS Code will open a new window connected to the container. Use
**File → Open Folder** and open `/program` — that's where the project lives
inside the container.

> **Tip:** You only need to do this once per session. As long as the container
> is running, VS Code stays attached. If you close VS Code and reopen it
> later, just attach again.

---

## Step 3: Configure Your Data Directory

Before you write any code, make sure the project knows where your shared data
folder lives.

In the VS Code window attached to the container:

1. Copy `.env.example` to `.env`
2. Open `.env` and check the `DATA_DIR` value
3. Make sure it points to the Box folder your mentor shared with you

You can sanity-check that the data is accessible from inside the container:

```bash
ls "$DATA_DIR"
```

If that path is empty or missing, fix it now. Most notebook and CLI issues in
this scaffold come from the data directory being misconfigured.

---

## Step 4: Explore One Real Input First

Before writing a strategy, look at an actual input so you understand the data
shape you need to handle. Create a notebook in `notebooks/` and inspect a
single example.

```python
from {{ cookiecutter.code_directory }}.settings import DATA_DIR
from {{ cookiecutter.code_directory }}.io import load_inputs

inputs = load_inputs(DATA_DIR / "input")
key, single_input = next(iter(inputs.items()))

print(key)
single_input
```

Spend a minute answering basic questions before coding:

- What Python type is each input?
- What fields or structure does it contain?
- What does a reasonable output dict need to capture?

Once you understand one real example, writing `do_inference` gets much easier.

---

## Step 5: Create a New Strategy

Every strategy lives in its own file inside
`src/{{ cookiecutter.code_directory }}/inference_strategies/`.
The framework discovers new strategies automatically — all you have to do is
drop a file in that folder.

In the VS Code window attached to the container, create a new file — for this
tutorial we'll call it `my_strategy.py`:

```
src/{{ cookiecutter.code_directory }}/inference_strategies/my_strategy.py
```

Paste in this starter template:

```python
"""Strategy that does XYZ."""

from typing import Any

from {{ cookiecutter.code_directory }}.inference import InferenceStrategy


class MyStrategy(InferenceStrategy):
    """A short description of what this strategy does."""

    def do_inference(self, inference_input: Any) -> dict[str, Any]:
        """Process a single input and return results.

        Args:
            inference_input: One item from the dataset.

        Returns:
            A dict containing the results.
        """
        return {"result": "placeholder"}
```

That's a complete, working strategy. The only method you *must* implement is
`do_inference`. It receives one input and returns a dict with your results.

### Adding configurable parameters

If your strategy has settings you want to experiment with (a threshold, a
model name, a window size, etc.), accept them in `__init__`:

```python
class MyStrategy(InferenceStrategy):
    """Strategy with a configurable threshold."""

    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def do_inference(self, inference_input: Any) -> dict[str, Any]:
        """Process a single input and return results.

        Args:
            inference_input: One item from the dataset.

        Returns:
            A dict containing the results.
        """
        # use self.threshold in your logic
        ...
```

Parameters you set on `self` are automatically recorded in the run metadata,
so you can always look back and see what settings produced a given set of
outputs.

### Check your code style

Before moving on, run the linter to make sure your code passes the project's
style checks:

```bash
pre-commit run --all-files
```

Fix any issues it reports. This same check runs automatically every time you
try to commit, so it's easier to fix things as you go.

---

## Step 6: Test It on a Single Input in a Notebook

Before running anything on the full dataset, make sure your logic works on
one item. In the VS Code window attached to the container, create a new
notebook in the `notebooks/` folder.

> **Note:** When VS Code asks you to select a kernel for the notebook, pick
> the Python interpreter that's already installed in the container. There
> should be only one option.

### Notebook guidelines

Notebooks in this project follow
[clinic standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md):

- Start with a **markdown cell** containing a title, your name, the date, and
  a brief description of what the notebook does.
- Keep each code cell to **10 lines or fewer**. If a cell is getting long,
  break it up.
- Keep the total notebook to **under 10 cells**. Notebooks are for
  *demonstrating* results, not for developing large amounts of logic.
- **Do not define functions in notebooks.** All reusable logic belongs in
  `.py` files under `src/`. Import it instead.
- **Do not use `! pip install ...`** in notebooks. All dependencies are
  managed in `pyproject.toml` and installed in the Docker image.
- Put all `import` statements in the **first code cell**.
- Remove any scratch/testing cells before you're done.

### Try it

In your first code cell, enable automatic reloading and put your imports:

```python
%load_ext autoreload
%autoreload 2

from {{ cookiecutter.code_directory }}.inference_strategies.my_strategy import MyStrategy
from {{ cookiecutter.code_directory }}.io import load_inputs
from {{ cookiecutter.code_directory }}.settings import DATA_DIR
```

`%autoreload 2` tells the notebook to re-read your `.py` files every time you
run a cell. That way, when you edit your strategy code and come back to the
notebook, you can just re-run the cell — no need to restart the kernel.

In the next cell, load one input and test your strategy:

```python
inputs = load_inputs(DATA_DIR / "input")
key, single_input = next(iter(inputs.items()))

strategy = MyStrategy()          # pass parameters here if your strategy takes any
result = strategy.do_inference(single_input)
print(key, result)
```

This is the fastest feedback loop you have — use it often. Edit your strategy,
save the file, re-run the cell, and see the updated results immediately.

> **If things get weird,** restart the kernel and re-run all cells. Autoreload
> handles most changes, but some (like renaming a class or changing
> inheritance) need a fresh kernel.

### What to check

- Does `result` have the keys you expect?
- Do the values look reasonable for this input?
- Does it run without errors?

Once you're happy with the output on a handful of individual inputs, move on
to running the full pipeline.

---

## Step 7: Run the Full Pipeline in a Notebook

Now you'll run your strategy across *every* input and evaluate the results.

In the same notebook (or a new one in the attached VS Code), run:

```python
from {{ cookiecutter.code_directory }}.pipeline import run_pipeline

run_dir = run_pipeline(
    "MyStrategy",                    # the class name of your strategy
    "ExampleEvaluator",              # the evaluator to use (ask your mentor which one)
    expected_path="data/expected",   # path to the correct answers
)
print("Results saved to:", run_dir)
```

If your strategy takes parameters:

```python
run_dir = run_pipeline(
    "MyStrategy",
    "ExampleEvaluator",
    expected_path="data/expected",
    params={"threshold": 0.8},
)
```

### What just happened?

`run_pipeline` does two things in sequence:

1. **Inference** — loads every input, runs `do_inference` on each one, and
   saves all the outputs to a timestamped folder inside `data/output/`.
2. **Evaluation** — compares your outputs to the correct answers and saves
   scores (and any plots) into the same folder.

### Inspecting the results

The returned `run_dir` is a `Path` pointing to the output folder. You can
load and explore the evaluation results right in the notebook:

```python
import json

with open(run_dir / "evaluation.json") as f:
    results = json.load(f)

# Pretty-print the first few results
for key, value in list(results.items())[:5]:
    print(key, value)
```

If you want a more tabular view, convert the results to a DataFrame:

```python
import pandas as pd

results_df = pd.read_json(run_dir / "evaluation.json").T
results_df.head()
```

`pd.DataFrame.from_dict(results, orient="index")` works too if you already
have the JSON loaded into memory.

If the evaluator produces plots (like a confusion matrix), they are saved as
`.png` files in the same folder. You can display them in the notebook:

```python
from IPython.display import Image

Image(filename=str(run_dir / "confusion_matrix.png"))
```

### Running inference and evaluation separately

Sometimes you want to run inference once and then try different evaluators on
the same outputs, or re-evaluate without re-running inference. You can split
the two steps:

```python
from {{ cookiecutter.code_directory }}.pipeline import run_inference, run_evaluation

# Run inference only
run_dir = run_inference("MyStrategy", params={"threshold": 0.8})

run_evaluation("ExampleEvaluator", run_dir=run_dir, expected_path="data/expected")
```

---

## Step 8: Run the Pipeline from the Command Line

Switch back to the terminal where you ran `make run-interactive` — you should
still have a bash prompt inside the container.

> **Tip:** If you closed that terminal, just run `make run-interactive` again
> from the project directory to start a new session.

Run inference and evaluation together:

```bash
{{ cookiecutter.project_slug }} run \
    --strategy MyStrategy \
    --evaluator ExampleEvaluator \
    --expected data/expected
```

With parameters:

```bash
{{ cookiecutter.project_slug }} run \
    --strategy MyStrategy \
    --evaluator ExampleEvaluator \
    --expected data/expected \
    --param threshold=0.8
```

You can also run inference and evaluation as separate commands:

```bash
# Run inference only
{{ cookiecutter.project_slug }} infer --strategy MyStrategy --param threshold=0.8

# Evaluate an existing run (use the path printed by the infer command)
{{ cookiecutter.project_slug }} evaluate \
    --evaluator ExampleEvaluator \
    --run-dir data/output/MyStrategy/2025-01-15_14-30-00 \
    --expected data/expected
```

To see all options for any command, add `--help`:

```bash
{{ cookiecutter.project_slug }} run --help
```

---

## Quick Reference

### Code quality checklist

- [ ] Every file, class, and function has a docstring
  ([Google style](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods))
- [ ] There is no commented-out code
- [ ] `pre-commit run --all-files` passes
- [ ] Notebooks have under 10 cells, each 10 lines or fewer
- [ ] Notebooks don't define functions — those belong in `src/`
- [ ] No `! pip install` in notebooks

### Useful links

- [Clinic coding standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md)
- [Computer setup guide](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/clinic-computer-setup.md)
- [Docker FAQ](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/Docker.md)
- [Well-documented code example](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/code-example.md)

---

## What to Do Next

- **Iterate on your strategy.** Change the logic in `do_inference`, re-test on
  single inputs in a notebook, then re-run the full pipeline to see if your
  scores improve.
- **Try different parameters.** If your strategy accepts parameters, experiment
  with different values and compare the evaluation results across runs.
  Each run gets its own timestamped folder, so nothing is overwritten.
- **Look at the example code.** The files `example_strategy.py` and
  `classifier_evaluator.py` in the source tree are short, readable references.
- **Ask your mentor** if you're not sure what evaluator to use, what the correct
  answers should look like, or how to interpret the evaluation results.

{% endif %}
{% if cookiecutter.dashboard == 'yes' %}
{% if cookiecutter.examples == 'data-science' %}

---

{% endif %}
{% raw %}
# Tutorial: Building and Extending Your Dashboard

This walkthrough takes you from zero to a live dashboard.
By the end you will have:

1. Started the dev server and seen charts on real Chicago 311 data
2. Understood how data flows from your pipeline to the browser
3. Changed an existing chart
4. Added a filter backed by the Zustand store
5. Added a new tab — framed as an agent task you hand to an LLM
6. Shipped the dashboard to a public Cloudflare Pages URL

File paths in this part are relative to `dashboard/` unless marked otherwise.

Before you start, make sure you've completed the
[computer setup guide](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/clinic-computer-setup.md)
and have **Make** plus **Docker** working on your machine.  (The dashboard
pathway is built and supported for projects generated with `docker=yes`.  If
your project was generated with `docker=no`, the `dashboard-*` Make targets
call `npm` directly instead — that path is best-effort and needs **Node 22+**
installed on your machine.)

---

## Step 1: Run It

Pull the example datasets from Box, then start the dev server:

```bash
make dashboard-data
make dashboard-dev
```

Open http://localhost:5173.  You should see a dashboard with global controls
(a request-type picker and a year-range slider) and three tabs: **Trends**
(stat tiles plus trend and breakdown charts), **Map** (a choropleth of
requests per community area), and **SQL** (a live query console).  Everything
queries the parquet files that `make dashboard-data` just placed in
`public/data/`.

> **Troubleshooting.** If `make dashboard-dev` errors with "Docker not found",
> make sure Docker Desktop is running, then run
> `make dashboard-install && make dashboard-dev` once to install deps inside
> the container.  If it errors with `npm: not found`, your project was
> generated with `docker=no` — install Node 22+ (there is no container in that
> configuration).  See `dashboard/README.md` for the full command reference.

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

**The example datasets** come from Box via the manifest: `reqs_311` (a toy
sample of ~1.6M Chicago 311 service requests: `creation_date, status,
type_of_service_request, community_area, …`) and `community_areas` (Chicago's
77 community areas as GeoParquet, with a MapLibre-ready `geometry_geojson`
column).  Their full schemas live in `data/dictionary/`.

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

**DuckDB views** — every manifest entry is registered at startup as a view
named after the file stem.  A query like `SELECT * FROM reqs_311 LIMIT 5` or
`SELECT * FROM my_dataset WHERE category = 'A'` just works.

{% endraw %}
{% if cookiecutter.examples == 'data-science' %}
---

## Step 2b: Send Your Pipeline Output to the Dashboard

In Part 1, Step 7 you ran the full pipeline in a notebook and got a results
DataFrame.  Export it for the dashboard from that same notebook:

```python
from {{ cookiecutter.code_directory }}.dashboard_export import export_dataset

export_dataset(results_df.reset_index(), "results")
```

(`reset_index()` turns the input keys from the index into a regular column, so
they become queryable.)

This writes `dashboard/public/data/results.parquet` and a data dictionary to
`dashboard/data/dictionary/results.{json,md}`.  Run `make dashboard-dev`, open
the **SQL** tab, and query it: `SELECT * FROM results LIMIT 10`.

The parquet is git-ignored, so teammates and CI won't see it yet.  Ask your
mentor to upload it to Box and add it to `data.manifest.json` (project-root
`PROJECT_SETUP.md`, Dashboard step 4).  After that, `make dashboard-data`
pulls it for everyone.

---

{% endif %}
{% raw %}
---

## Step 3: Change a Chart

Open `src/pages/OverviewPage.tsx`.  Find the `<PlotFigure options={...} />`
block.  The `options` prop is a plain
[Observable Plot](https://observablehq.com/plot/) spec — change it and the
browser hot-reloads.

For example, to switch the monthly trend from a line chart to an area chart:

```tsx
<PlotFigure
  options={{
    marks: [
      Plot.areaY(monthly, { x: (d) => new Date(d.month), y: "n" }),
    ],
  }}
/>
```

(Note `options` takes the plain spec object — `PlotFigure` calls `Plot.plot()`
for you.)

`monthly` comes from `useQuery<Row>(sql)`, which returns an array of typed row
objects.  Look at the existing tab components for the full pattern.

> **Where do column names come from?** Read
> `data/dictionary/reqs_311.json` — it lists every column with its type and
> sample values.  Never guess column names; always check the dictionary first.

---

## Step 4: Add a Filter

Filters that need to persist across tabs live in the Zustand store at
`src/store/filters.ts`.  This is the single source of truth for all UI state.

**1. Extend the store.**  Open `src/store/filters.ts` and add your field:

```ts
interface FiltersState {
  requestType: string;    // existing field
  setRequestType: (t: string) => void;
  status: string;         // ← add this
  setStatus: (s: string) => void;
}

export const useFilters = create<FiltersState>()((set) => ({
  requestType: "All",
  setRequestType: (requestType) => set({ requestType }),
  status: "All",          // ← add this
  setStatus: (status) => set({ status }),
}));
```

**2. Wire up a Spectrum picker** in your tab (derive the options from a
`SELECT DISTINCT` query, as `OverviewPage.tsx` does — never hardcode values):

```tsx
const { status, setStatus } = useFilters();

<Picker
  label="Status"
  selectedKey={status}
  onSelectionChange={(k) => setStatus(String(k))}
>
  {statuses.map((s) => (
    <Item key={s}>{s}</Item>
  ))}
</Picker>
```

**3. Use it in your SQL query:**

```ts
const sql =
  status === "All"
    ? "SELECT * FROM reqs_311"
    : `SELECT * FROM reqs_311 WHERE status = '${status}'`;

const { data } = useQuery<Row>(sql);
```

Any other tab that calls `useFilters()` will see the same `status` value —
that is how the global request-type picker applies to both the Trends and Map tabs.

---

## Step 5: Add a Tab (Agent Task)

Adding a full tab is a good task to hand to an LLM.  Prepare two files:

- `AGENTS.md` — the hard rules for this codebase (no backend, Spectrum-only
  components, query via `useQuery`, etc.)
- `data/dictionary/<name>.json` — the schema of the dataset you want to query

Then prompt your agent:

> Read `dashboard/AGENTS.md` and `dashboard/data/dictionary/reqs_311.json`.
> Create `src/pages/StatusTab.tsx` that shows a line chart of monthly request
> counts broken down by `status`.  Add it as a new tab in `src/App.tsx`.

The agent has everything it needs: the rules, the column types, the patterns
from `OverviewPage.tsx` and `MapPage.tsx`, and the `useQuery` / `PlotFigure`
primitives.

After the agent writes the files:

1. Check the dev server — the new tab should appear immediately.
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
3. Runs the Playwright smoke tests (all three tabs render; the filter
   changes the numbers).
4. Deploys to Cloudflare Pages: `https://<slug>-dashboard.pages.dev`.

The deploy step is skipped on pull requests — PRs only build and test.

> **One-time setup required** before the first deploy.  Ask your mentor to
> follow the Cloudflare and Box setup steps in the project-root `PROJECT_SETUP.md`.

---

## Quick Reference

### Commands

| Command | What it does |
|---|---|
| `make dashboard-install` | Install Node dependencies |
| `make dashboard-dev` | Dev server at localhost:5173 |
| `make dashboard-build` | Production build to `dist/` |
| `make dashboard-data` | Pull parquet files from Box |
| `npm run test:e2e` | Playwright smoke tests (needs Node + one-time `npx playwright install --with-deps chromium`; in docker=yes projects, CI runs these for you) |

### Where things live

| Path | Purpose |
|---|---|
| `src/pages/` | One file per tab |
| `src/store/filters.ts` | Cross-tab filter state (Zustand) + `filterSql()` |
| `src/lib/duckdb.ts` | DuckDB-wasm singleton and query helper |
| `src/lib/useQuery.ts` | React hook wrapping the query helper |
| `src/components/PlotFigure.tsx` | Observable Plot → React wrapper |
| `data/dictionary/` | Per-dataset schema JSON + Markdown |
| `data.manifest.json` | Box URLs for remote datasets |
| `public/data/` | Local parquet files (git-ignored; pulled from Box) |

### Useful links

- [Observable Plot docs](https://observablehq.com/plot/)
- [React Spectrum components](https://react-spectrum.adobe.com/react-spectrum/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [DuckDB-wasm](https://duckdb.org/docs/api/wasm/overview)
- [Clinic coding standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md)

---

## What to Do Next

- **Explore the 311 data.** Use the **SQL** tab to run queries live against
  the parquet views — it is the fastest way to prototype the SQL for a new
  chart before writing any code.
- **Export your first real dataset.** Run `dashboard_export.py` on a DataFrame
  from your pipeline and add it to the manifest.
- **Hand a tab to an LLM.** Follow Step 5 with your real data dictionary and
  see how quickly a new visualization comes together.
- **Ask your mentor** if you need help with the one-time Cloudflare or Box
  setup, or if the CI deploy step fails.
{% endraw %}
{% endif %}
