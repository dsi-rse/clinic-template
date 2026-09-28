# Project Setup Guide (for mentors)

This guide walks you through the steps to turn the generated scaffold into a
project your students can start working in. You should complete all of these
steps before students begin.

Most of these tasks are good candidates for an AI coding agent (Claude Code,
Cursor, Codex, etc.); the guide calls out where that is especially effective.

---

## 1. Set up the data on Box

The project expects data to live in Box so that everyone on the team
(including students working in Docker or on the cluster) can access it from a
single shared location.

### Create the data directory

On [Box](https://uchicago.account.box.com), create a directory in
`dsi-core/clinic/` called `{{ cookiecutter.project_slug }}`.

### Populate the data

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

### Update the `.env` files

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

## 2. Refactor the codebase and the tutorial to match the project

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

## 3. Give students access to Box

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

## 4. Write a baseline strategy (optional but recommended)

It can be hard to tell whether the scaffold is really working without a
baseline strategy that at least sort of works. AI coding tools can do this
but need supervision: they tend to add complexity, and what you want is the
simplest approach that gives a non-trivial result.

Once you have a baseline, update `TUTORIAL.md` step 3 to have students
implement it. If it feels like too much code to put inline in the tutorial,
it is probably too complicated.

Also remove the `skip` marker from `test_run_example_strategy_end_to_end` in
`tests/test_scripts.py`, so CI exercises a real run from now on.

---

## 5. Verify that it's working

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

## 6. Update the README

Update the README to describe the project, if this hasn't already been done.

## 7. Delete this file

You're done! You can delete this `PROJECT_SETUP.md` file.
