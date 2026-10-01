# scripts/

The runnable layer. Each file is a short `argparse` wrapper around one
function from `{{ cookiecutter.code_directory }}`; run it with
`python scripts/<name>.py --help` (prefix `uv run` outside the container).

| Script | Does |
| --- | --- |
| `predict_and_evaluate.py` | Run a strategy over every input, save a run directory under `DATA_DIR/output/`, evaluate it. The usual way to try a strategy. `make run STRATEGY=... ARGS="..."` calls this. |
| `evaluate.py` | Re-score a saved run directory, e.g. after changing or adding an evaluator. No inference is repeated. |

Rules: scripts import from the package, the package never imports from
scripts. Logic lives in `src/{{ cookiecutter.code_directory }}/`; the shared
argument helpers (`--strategy`, `--evaluator`, `--param`, ...) are in
`src/{{ cookiecutter.code_directory }}/framework/cli_options.py`. A script
should stay under about 50 lines. To add one, copy the nearest file, change
the function it calls, and add a row here.
