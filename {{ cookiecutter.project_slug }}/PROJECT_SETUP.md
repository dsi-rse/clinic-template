# Project Setup Guide (for mentors)

This guide walks you through the steps to turn the generated scaffold into a
project your students can start working in. You should complete all of these
steps before students begin.

Most of these tasks are good candidates for an AI coding agent (Claude Code,
Cursor, Codex, etc.); the guide calls out where that is especially effective.

---

{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}
## Data science scaffold

### 1. Set up the data on Box

The project expects data to live in Box so that everyone on the team
(including students working in Docker or on the cluster) can access it from a
single shared location.

#### Create the data directory

On [Box](https://uchicago.account.box.com), create a directory in
`dsi-core/clinic/` called `{{ cookiecutter.project_slug }}`.

#### Populate the data

The scaffold expects two things in the data directory:

- **Inputs.** Any format, provided it can be loaded into a dictionary with
  unique keys. Loaded, in its entirety, by `load_inputs()` in `data.py`.
- **Expected outputs.** Any format, provided it can be loaded into a
  dictionary with the same keys; something simple like JSON is ideal.
  Loaded by `load_expected_outputs()` in `data.py`.

Predictions (`types.Prediction`) and expected outputs (`types.ExpectedOutput`)
do not have to be identical, but the evaluator has to know how to compare
them, so the simplest choice is to give them the same key(s) you score on.

**IMPORTANT:** inputs and expected outputs **MUST** use the same set of unique
keys. `load_expected_outputs()[key]` is the ground truth for
`load_inputs()[key]`.

#### Update the `.env` files

The generated `.env` and `.env.example` files point `DATA_DIR` to the default
Box mount path. Update them so the path includes your project folder, which
will be something like this for you:

```
DATA_DIR=~/Library/CloudStorage/Box-Box/dsi-core/clinic/{{ cookiecutter.project_slug }}
```

For students the path is different, since they only have access to this
folder. Update `.env.example` to match the expected path for students:

```
DATA_DIR=~/Library/CloudStorage/Box-Box/{{ cookiecutter.project_slug }}
```

(The scaffold requires a `data_dir` other than `none` when the project is
generated, because the pipeline reads `settings.DATA_DIR`.)

---

### 2. Refactor the codebase and the tutorial to match the project

Use the following prompt to have an AI agent implement the data layer.

```
This repo is a scaffold for student data-science projects. It is generic: "input", "prediction", "inference strategy", "evaluator" are placeholders, and `types.py` uses loose types. The harness in `src/{{ cookiecutter.code_directory }}/framework/` (base classes, discovery by class name, pipeline, run directory layout) and the argparse scripts in `scripts/` should keep their structure; what changes is the project-specific layer: `data.py`, `types.py`, the example strategy and evaluators, and the docs.

The project is: [one sentence project description].

To start:
- Implement `load_inputs()` and `load_expected_outputs()` in `src/{{ cookiecutter.code_directory }}/data.py` to load the files in Box at [location of these files]. Define `Input`, `Prediction` and `ExpectedOutput` in `src/{{ cookiecutter.code_directory }}/types.py` to match; [describe expected formats and types, or provide the functions].
- Test the loaders by hand (a short `uv run python -c "..."` or a notebook), and check that the keys of inputs and expected outputs line up.
- Look through the data files and write a DATA.md describing what the files contain, where they live, and how to load them.
```

After this step, review `data.py`, `types.py` and `DATA.md` to see if any
refinements are needed. Then use a variation of the following prompt to update
the rest of the codebase.

```
Keeping in mind the inputs and outputs in `data.py`, `types.py` and `DATA.md`:
- Rename the generic names (`InferenceStrategy.do_inference`, `Input`, `Prediction`, `--strategy`, and so on) to project-specific ones throughout `src/`, `scripts/`, `tests/`, `README.md`, `TUTORIAL.md` and `scripts/README.md`. I don't want students confused by vague terms like `do_inference`. Keep every name imported from the module that defines it, and keep `framework/` as the harness.
- Make `ExampleStrategy` return a trivial but correctly-typed prediction, with a TODO saying what a real strategy would do.
- Replace the shipped evaluators with one straightforward evaluator (exact match is fine) with a TODO for improvements. `classifier_evaluator.py` shows how to add a plot; keep it only if a confusion matrix makes sense for the task.
- Update the expected class names in `tests/test_scripts.py` and the default `STRATEGY` in the `Makefile`, then make `uv run ruff check .` and `uv run pytest` pass.
```

---

### 3. Give students access to Box

Each student needs at least **Viewer** (read-only) access to the
`dsi-core/clinic/{{ cookiecutter.project_slug }}/` folder on Box so their
pipeline can load the data. Pipeline runs are written to `DATA_DIR/output/`,
so students also need **Editor** access to the `output/` sub-folder (create it
if it does not exist yet).

To grant access:

1. Open the folder on Box
2. Click **Share**, then **Invite People**
3. Add each student's UChicago email
4. Set the appropriate permission level

Also make sure students have
[Box Drive](https://www.box.com/resources/downloads) installed and syncing on
their machines, so the files appear at the `~/Library/CloudStorage/Box-Box/`
mount point that `DATA_DIR` points to.

---

### 4. Write a baseline strategy (optional but recommended)

It can be hard to tell whether the scaffold is really working without a
baseline strategy that at least sort of works. AI coding tools can do this
but need supervision: they tend to add complexity, and what you want is the
simplest approach that gives a non-trivial result.

Once you have a baseline, update `TUTORIAL.md` Step 5 to have students
implement it. If it feels like too much code to put inline in the tutorial,
it is probably too complicated.

Also remove the `skip` marker from `test_run_example_strategy_end_to_end` in
`tests/test_scripts.py`, so CI exercises a real run from now on.

---

### 5. Verify that it's working

First, by hand:

```bash
make run STRATEGY=ExampleStrategy
uv run pytest
uv run ruff check .
```

Then have an AI agent complete the tutorial, with a prompt like:

```
Do TUTORIAL.md end to end. Instead of the VS Code dev container, use `make run-interactive` and run the notebook cells as a Python script inside the container. Report every step that did not work as written.
```

If that works, go through the tutorial yourself.

---

{% endif %}
{% if cookiecutter.examples in ['dashboard', 'data-science-and-dashboard'] %}
## Dashboard

Complete these steps once per project before the first deploy.  Students do not need to do this.  File paths in this section are relative to `dashboard/`.

Don't use the Cloudflare dashboard's "Create" wizard.  It defaults to a Workers project, which the CI workflow can't deploy to.  Create the project from your machine instead (step 2).

### 1. Create a Cloudflare API token

1. In [Cloudflare](https://dash.cloudflare.com), go to **Manage Account → Account API Tokens → Create token**.
2. Add one policy: scope it to the **whole account** (UChicago DSI Account), with the permission **Cloudflare Pages → Edit** (shown as "Pages Write").  Don't scope it to a single project or Worker; wrangler rejects project-scoped tokens with code 10000.
3. Set the expiry to after the quarter ends.
4. Copy the token.  Cloudflare only shows it once.
5. Copy your account ID from the dashboard URL (`dash.cloudflare.com/<account-id>/...`).

### 2. Create and test the project from your machine

{% if cookiecutter.docker == "yes" %}Run these from the project root.  wrangler runs inside the `dashboard` container, so you don't need Node installed.

```bash
make dashboard-install   # installs the same wrangler version CI uses
export CLOUDFLARE_API_TOKEN=<token from step 1>
export CLOUDFLARE_ACCOUNT_ID=<account ID from step 1>
docker compose run --rm -e CLOUDFLARE_API_TOKEN -e CLOUDFLARE_ACCOUNT_ID dashboard \
  npx wrangler pages project create {{ cookiecutter.project_slug }}-dashboard --production-branch=main
docker compose run --rm -e CLOUDFLARE_API_TOKEN -e CLOUDFLARE_ACCOUNT_ID dashboard sh -c \
  'mkdir -p /tmp/cf-test && echo ok > /tmp/cf-test/index.html && npx wrangler pages deploy /tmp/cf-test --project-name={{ cookiecutter.project_slug }}-dashboard --branch=local-test'
```

`-e NAME` with no value passes your shell's value into the container.
{% else %}This needs Node 22.  From `dashboard/`:

```bash
npm ci   # installs the same wrangler version CI uses
export CLOUDFLARE_API_TOKEN=<token from step 1>
export CLOUDFLARE_ACCOUNT_ID=<account ID from step 1>
npx wrangler pages project create {{ cookiecutter.project_slug }}-dashboard --production-branch=main
mkdir -p /tmp/cf-test && echo ok > /tmp/cf-test/index.html
npx wrangler pages deploy /tmp/cf-test --project-name={{ cookiecutter.project_slug }}-dashboard --branch=local-test
```
{% endif %}
- `--production-branch=main` is required.  CI deploys with `--branch=main`, and wrangler's default production branch is `production`, so without the flag every deploy lands on a preview URL and the public URL never updates.
- The test deploy goes to a preview URL (`local-test.{{ cookiecutter.project_slug }}-dashboard.pages.dev`).  If it succeeds, the token works.

### 3. Add GitHub secrets and run CI

In the GitHub repository go to **Settings → Secrets and variables → Actions** and add the same values you just tested:

| Secret name | Value |
|---|---|
| `CLOUDFLARE_API_TOKEN` | The token from step 1 |
| `CLOUDFLARE_ACCOUNT_ID` | The account ID from step 1 |

You can set these as organization secrets instead.  A repository secret overrides an organization secret with the same name.

Then go to **Actions → Dashboard CI/CD → Run workflow**, run it from `main`, and confirm the run goes green and this URL serves the dashboard:

```
https://{{ cookiecutter.project_slug }}-dashboard.pages.dev
```

From now on every push to `main` that touches `dashboard/` deploys.  Pull requests that touch `dashboard/` get a preview deploy, and the workflow comments the preview link on the PR.  When the PR is closed or merged, the workflow deletes the preview.  PRs from forks don't get previews, because GitHub doesn't give them the secrets.

#### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Code 10000 locally | Token is scoped to one project/Worker, or lacks Pages Edit | Recreate it scoped to the whole account with Cloudflare Pages → Edit |
| Code 10000 in CI only | The GitHub secret holds a different token | Paste the token you tested in step 2 again |
| Deploys only reach preview URLs | Production branch isn't `main` | In the Pages project, **Settings → Builds & deployments → Production branch** → `main` |
| "Project not found" | Name mismatch, or project is in a different account | Check `--project-name` in `.github/workflows/dashboard.workflow.yml` and `CLOUDFLARE_ACCOUNT_ID` |
| You created a Workers project by mistake | Dashboard wizard default | Delete it and run step 2 |

### 4. Add datasets via Box

> **Everything in `public/data/` is published to the open internet.**  The build copies it into the deployed site at a guessable public URL.  Only add datasets that are aggregated or de-identified enough to be world-readable — never partner-restricted data.

For each dataset your pipeline produces:

1. Export a parquet file from your pipeline using `export_dataset(df, "name")` in `src/{{ cookiecutter.code_directory }}/dashboard_export.py` (project root, not `dashboard/src/`).
2. Upload the parquet to the project's Box folder.
3. In Box, open the file, click **Share → Create shared link**, set access to **People with the link** (anything more restrictive returns a login page instead of the file, which breaks `pull_data.py` and CI), and set the **link expiration** far in the future (an expired link breaks every student's `make dashboard-data` and the CI deploy).  Copy the **direct download** URL.  It will look like:
   ```
   https://uchicago.box.com/shared/static/<hash>.parquet
   ```
4. Open `data.manifest.json` and add an entry:
   ```json
   { "name": "my_dataset", "url": "https://uchicago.box.com/shared/static/..." }
   ```
5. Run `make dashboard-data` to pull the file locally and verify the size gate passes.
6. Commit `data.manifest.json` and the updated `data/dictionary/` files (not the parquet itself).

Students can then run `make dashboard-data` to pull the datasets whenever they set up the project.
{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}

The Box folder for dashboard parquet files can be the same `dsi-core/clinic/{{ cookiecutter.project_slug }}` folder you created in the data science section above.  The pipeline's evaluation outputs are the natural first dataset: call `export_dataset(results_df.reset_index(), "results")` with the `results_df` from TUTORIAL.md Part 1, Step 7 (built from the `"per_item"` part of `evaluation.json`), using the project-root `src/{{ cookiecutter.code_directory }}/dashboard_export.py`, and follow the steps above.
{% endif %}

---

{% endif %}
## Finish

Update the README to describe the project, if this hasn't already been done. Then delete this `PROJECT_SETUP.md` file — you're done!
