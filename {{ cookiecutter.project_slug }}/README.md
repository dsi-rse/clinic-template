# {{ cookiecutter.project_name }}

## Project Background

[Please add project background]

## Project Goals

[Please add project goals]

## Usage

{% if cookiecutter.docker == 'yes' %}### Docker & Make

We use `docker` and `make` to run our code. The built-in `make` commands:

* `make build-only`: Build the image only. Useful for testing and making changes to the Dockerfile.
* `make run-notebooks`: Run a Jupyter server with the current directory mounted into `/project`.
* `make run-interactive`: Create a container (with the current directory mounted as `/project`) and open an interactive shell.
{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}* `make run STRATEGY=ExampleStrategy ARGS="..."`: Run one strategy end to end (see "Working with This Project").
{% endif %}
The file `Makefile` contains information about the specific commands that are run when calling each `make` statement.

{% endif %}

{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}
## Working with This Project

The project is built around two ideas:

- **Inference strategies** — different approaches to solving the problem. You will spend most of your time adding and improving these.
- **Evaluators** — code that scores how well a strategy did. You may also add or improve these.

The key files are:

| File/Folder | What it's for |
|---|---|
| `src/{{ cookiecutter.code_directory }}/inference_strategies/` | **Add your strategies here** |
| `src/{{ cookiecutter.code_directory }}/evaluators/` | Add or improve evaluators here |
| `src/{{ cookiecutter.code_directory }}/data.py` | How inputs and expected outputs are loaded (fill this in for your project) |
| `src/{{ cookiecutter.code_directory }}/types.py` | What a strategy receives (`Input`) and returns (`Prediction`) |
| `src/{{ cookiecutter.code_directory }}/framework/` | The harness that runs and scores strategies. You should not need to edit it. |
| `scripts/` | Command-line entry points (see `scripts/README.md`) |
| `DATA_DIR/output/` | One folder per run, next to the data (see `framework/pipeline.py` for the layout) |

For a step-by-step first run, see [`TUTORIAL.md`](TUTORIAL.md).

---

### How to add an inference strategy

1. Create a new `.py` file in `src/{{ cookiecutter.code_directory }}/inference_strategies/`. Name it something descriptive, e.g. `my_strategy.py`.
2. Copy this template into the file and fill in your logic:

```python
"""One sentence describing what this strategy does."""

from {{ cookiecutter.code_directory }}.framework.base import InferenceStrategy
from {{ cookiecutter.code_directory }}.types import Input, Prediction


class MyStrategy(InferenceStrategy):
    """One sentence describing what this strategy does."""

    def do_inference(self, inference_input: Input) -> Prediction:
        """Produce a prediction for one input."""
        # Write your logic here.
        # inference_input is one item from your dataset.
        # Return a dict with the keys defined by Prediction in types.py, e.g.:
        return {"label": True}
```

3. Save the file. Your strategy is now available to use everywhere by its class name — `"MyStrategy"` in this example.

If your strategy has settings you want to tune (like a threshold or a model name), add them as parameters to `__init__`. They are recorded with every run:

```python
def __init__(self, threshold: float = 0.5) -> None:
    """Remember the threshold."""
    self.threshold = threshold
```

---

### How to test a strategy on one value in a notebook

Import your strategy class directly and call `do_inference` on a single input:

```python
from {{ cookiecutter.code_directory }}.data import load_inputs
from {{ cookiecutter.code_directory }}.inference_strategies.my_strategy import MyStrategy

inputs = load_inputs()
key, single_input = next(iter(inputs.items()))

strategy = MyStrategy(threshold=0.8)
result = strategy.do_inference(single_input)
print(key, result)
```

This is the fastest way to check that your logic works before running it on the full dataset.

---

### How to run the full pipeline in a notebook

Once your strategy works on a single input, run it across the whole dataset and evaluate:

```python
from {{ cookiecutter.code_directory }}.framework.pipeline import run_pipeline

run_dir = run_pipeline(
    "MyStrategy",
    "ClassifierEvaluator",
    params={"threshold": 0.8},  # optional — only if your strategy takes parameters
)
print("Results saved to:", run_dir)
```

Results (predictions, scores, and any plots) are saved to a timestamped folder inside `DATA_DIR/output/`, so everyone on the team can see every run. The expected outputs are saved with the run too, so it can be re-scored later.

To run inference and evaluation as separate steps:

```python
from {{ cookiecutter.code_directory }}.framework.pipeline import run_inference, run_evaluation

run_dir = run_inference("MyStrategy", params={"threshold": 0.8})
run_evaluation(run_dir, "ClassifierEvaluator")
```

---

### How to run the pipeline from the command line

Inside the container (`make run-interactive`), run inference and evaluation together:

```bash
python scripts/predict_and_evaluate.py \
    --strategy MyStrategy \
    --evaluator ClassifierEvaluator \
    --param threshold=0.8
```

To re-score an existing run with a different evaluator, without re-running inference:

```bash
python scripts/evaluate.py "$DATA_DIR/output/MyStrategy/2025-01-01_12-00-00" --evaluator ExampleEvaluator
```

Add `--help` to see all available options for either script, including the list of strategies and evaluators it found:

```bash
python scripts/predict_and_evaluate.py --help
```

Outside the container, prefix each command with `uv run`. From the host without opening a shell: `make run STRATEGY=MyStrategy ARGS="--param threshold=0.8"`.

---

### How to add or improve an evaluator

Evaluators live in `src/{{ cookiecutter.code_directory }}/evaluators/`. Each evaluator scores a single prediction against the expected output, and can optionally summarize the whole run.

1. Create a new `.py` file in the `evaluators/` folder.
2. Use this template:

```python
"""One sentence describing what this evaluator measures."""

from {{ cookiecutter.code_directory }}.framework.base import Evaluator
from {{ cookiecutter.code_directory }}.types import ExpectedOutput, Prediction


class MyEvaluator(Evaluator):
    """One sentence describing what this evaluator measures."""

    def evaluate_single_output(
        self, predicted: Prediction, expected: ExpectedOutput
    ) -> dict[str, object]:
        """Compare one prediction to the expected output. Return a dict of scores."""
        return {"is_correct": predicted["label"] == expected["label"]}
```

The per-item results land under `"per_item"` in `evaluation.json`. To add dataset-level numbers (accuracy, F1, ...), add an `aggregate` method; its result lands under `"summary"`. See `example_evaluator.py` for the smallest complete example.

To add a plot to the evaluation report, add a `make_plots` method. It should return a dict where each key is a plot name and each value is a matplotlib figure — the figures are saved automatically as `.png` files when evaluation runs.

```python
import matplotlib.pyplot as plt

def make_plots(self, results: dict) -> dict[str, plt.Figure]:
    fig, ax = plt.subplots()
    # ... build your plot using results["summary"] and results["per_item"] ...
    return {"my_plot": fig}
```

See `classifier_evaluator.py` for a complete example.
{% endif %}
{% if cookiecutter.examples in ['dashboard', 'data-science-and-dashboard'] %}
### Dashboard

The project includes an optional browser dashboard built with Vite, React, and DuckDB-wasm.  It queries parquet files in the browser — no backend required.

**Start it locally (pull the example data from Box first):**

```bash
make dashboard-data
make dashboard-dev
```

Open http://localhost:5173.

**Build for deployment:**

```bash
make dashboard-build
```

See `TUTORIAL.md` for a step-by-step walkthrough, `dashboard/README.md` for the command reference, and `PROJECT_SETUP.md` for one-time mentor setup (Cloudflare Pages deployment, Box static links).

{% endif %}

## Repository Structure

### {{ cookiecutter.code_directory }}
Project python code

### scripts
Runnable Python scripts. Each script is listed and described in `scripts/README.md`.

### notebooks
Contains short, clean notebooks to demonstrate analysis.

{% if cookiecutter.examples in ['data-science', 'data-science-and-dashboard'] %}### tests
Structural tests for the scaffold. Run with `uv run pytest`.

{% endif %}{% if cookiecutter.data_dir == 'github' %}### data

Contains details of acquiring all raw data used in repository. If data is small (<25MB) then it is okay to save it to the repo, making sure to clearly document how the data is obtained.

If the data is larger than 25MB then you should not add it to the repo and instead document how to get the data in the README.md file in the data directory.

This [README.md file](/data/README.md) should be kept up to date.

{% endif %}### output
Should contain work product generated by the analysis. Keep in mind that results should (generally) be excluded from the git repository.

{% if cookiecutter.examples in ['dashboard', 'data-science-and-dashboard'] %}
### dashboard
Optional browser dashboard (Vite + React + DuckDB-wasm).  See `TUTORIAL.md` to get started.
{% endif %}
