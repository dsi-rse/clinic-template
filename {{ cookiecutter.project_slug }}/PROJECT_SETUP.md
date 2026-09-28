# Project Setup Guide (for mentors)

This guide walks you through the steps to turn the generated scaffold into a project your students can start working in. You should complete all of these steps before students begin.

Most of these tasks are good candidates for an AI coding agent (Cursor, Codex, etc.) — the guide calls out where that's especially effective.

---

{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}
## Data science scaffold

### 1. Set up the data on Box

The project expects data to live in Box so that everyone on the team (including students working in Docker or on the cluster) can access it from a single shared location.

#### Create the data directory

On [Box](https://uchicago.account.box.com), create a directory in dsi-core/clinic/ called {{ cookiecutter.project_slug }}.

#### Populate the data

This scaffold expects two types of data in the data directory:
- **Input data.** This can be any format, provided that it can be loaded into a dictionary with unique keys. It will be loaded, in its entirety, by a `load_input()` (or similarly named) function in io.py.
- **Expected outputs.** This can be any format, provided that it can be loaded into a dictionary with unique keys, but something simple like JSON is ideal for evaluation. It will be loaded, in its entirety, by a `load_expected_output()` (or similarly named) function in io.py. Note that the students' inference routines will be expected to produce outputs in the _exact same format_ as the expected output, so be thoughtful about how you structure this data.

**IMPORTANT:** Note that the input and expected output data **MUST** use the same set of unique keys to identify an aligned set of data points. A single input should match to a single expected output via a unique identifier.

#### Update the `.env` files

The generated `.env` and `.env.example` files point `DATA_DIR` to the default Box mount path. Update them so the path includes your project folder, which will be something like this for you:

```
DATA_DIR=~/Library/CloudStorage/Box-Box/dsi-core/clinic/{{ cookiecutter.project_slug }}
```

For students, the path will be different, since they only have access to this folder. Update the `.env.example` to match the expected path for students:
```
DATA_DIR=~/Library/CloudStorage/Box-Box/{{ cookiecutter.project_slug }}
```

---

### 2. Refactor the codebase and the tutorial to match the project

Use the following prompt to have an AI agent names and argment types in this scaffold to reflect the details of the project.

```
This is a repo scaffold that is used to get students started on data science projects, but it's totally generic and agnostic to the project content beyond that the project involves inference and evaluation. It uses uses generic names — "input," "output," "inference strategy," "evaluator," and so on — as placeholders. It also uses `Any` as a generic type for both inputs and outputs. Please review the codebase and rename them throughout the codebase so that every file, docstring, variable, CLI flag, and tutorial page uses language specific to your project.

Let's update this to be for a specific project: namely, [one sentence project description].

To start, please make the following changes:
- Update the io.py to load the input and output datafiles found in Box at [location of these files]. The loaded data should [describe expected formats, types, etc -- or if you prefer just provide the functions].
- Manually test the loading functions and check to see if they work as expected, and consider the implications before moving on to the next step.
- Take a look through the data files (analyze using pandas or other tools of your choice), and write a DATA.md describing what the files contain, where to find them, and how to load them.
```

After this step, review io.py and DATA.md to see if any refinements are needed to the data or the loading functions. Then use a variation of the following prompt to update the rest of the codebase.

```
Keeping in mind the inputs and outputs as established in io.py and DATA.md, make the following changes:
- Update the Any types for inputs and outputs to be more specific
- Update the classes, functions, and args to have names and types that are specific to this project. I don't want the students to be confused by vague, ambiguous terms like `do_inference`.
- Update the TUTORIAL.md and README.md to reflect the new function/class/arg names and to generally use more specific language to refer to the inputs, outputs, and methods for this project.
- Update the example inference strategy to output a trivial but correctly-typed output, with a TODO indicating what needs to be done to make it a real strategy.
- Remove the existing evaluators and replace them with an evaluator that will compare predicted outputs to expected in a straightforward, possibly facile way (e.g. it can just check if they're identical), with a TODO indicating what improvements may be needed.
```

### 3. Give students access to Box

Each student needs at least **Viewer** (read-only) access to the `dsi-core/clinic/{{ cookiecutter.project_slug }}/` folder on Box so their pipeline can load the data. If the pipeline writes output back to Box, they need **Editor** access to the `output/` sub-folder.

To grant access:

1. Open the folder on Box
2. Click **Share** → **Invite People**
3. Add each student's UChicago email
4. Set the appropriate permission level

Also make sure students have [Box Drive](https://www.box.com/resources/downloads) installed and syncing on their machines, so the files appear at the `~/Library/CloudStorage/Box-Box/` mount point that `DATA_DIR` points to.

---

### 4. Write a baseline strategy (optional but recommended)

It can be hard to tell if the scaffold is really working, even as a starting point, without implementing a baseline inference strategy that at least sort of works. This can be done with AI coding tools, but requires some supervision: an AI is likely to add a lot of complexity to get something that works, and what we want here is the simplest possible approach to get a non-trivial result.

Once you've implemented a baseline strategy, update the TUTORIAL.md to instruct students to implement the baseline strategy. If the baseline strategy feels like too much code to put in-line in the tutorial, then it's probably too complicated!

### 5. Verify that it's working

To verify that all of this is working, have an AI agent complete the tutorial, using a prompt like this.

```
Do the TUTORIAL.md to see if everything works. Instead of using VS Code dev container, just use `make run-interactive` and run your notebook in the docker container.
```

If that works, go through the tutorial yourself to see if you run into any issues.

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

From now on every push to `main` that touches `dashboard/` deploys.

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

The Box folder for dashboard parquet files can be the same `dsi-core/clinic/{{ cookiecutter.project_slug }}` folder you created in the data science section above.  The pipeline's evaluation outputs are the natural first dataset: call `export_dataset(results_df, "results")` from the project-root `src/{{ cookiecutter.code_directory }}/dashboard_export.py` and follow the steps above.
{% endif %}

---

{% endif %}
## Finish

Update the README to describe the project, if this hasn't already been done. Then delete this `PROJECT_SETUP.md` file — you're done!
