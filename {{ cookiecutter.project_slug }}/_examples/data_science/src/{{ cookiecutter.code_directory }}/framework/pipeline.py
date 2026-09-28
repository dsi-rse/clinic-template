"""Run a strategy over every input, save the run, evaluate it.

Run directory layout, under ``DATA_DIR/output/<StrategyName>/<timestamp>/``:

- ``predictions.json``  key -> the prediction dict returned by do_inference
- ``labels.json``       key -> expected output, for the inputs in this run.
                        Evaluation reads this file, not ``data.load_expected_outputs()``,
                        so a run stays reproducible if the expected outputs change.
- ``statuses.json``     key -> success | failure | error, with the error message
- ``metadata.json``     strategy name, description and parameters; number of
                        inputs; git commit; run time
- ``evaluation.json``   {"per_item": {...}, "summary": {...}} once evaluated
- ``*.png``             evaluator plots
"""

from __future__ import annotations

import json
import logging
import subprocess
from collections import Counter
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any

from tqdm import tqdm

from {{ cookiecutter.code_directory }} import data
from {{ cookiecutter.code_directory }}.framework.base import get_evaluator, get_inference_strategy
from {{ cookiecutter.code_directory }}.settings import DATA_DIR
from {{ cookiecutter.code_directory }}.types import ExpectedOutput, InferenceStatus, Prediction

logger = logging.getLogger(__name__)

# Where run directories are written, next to the data so the whole team sees the same runs.
OUTPUT_DIR = DATA_DIR / "output"

DEFAULT_EVALUATOR = "ExampleEvaluator"


def run_inference(
    strategy_name: str,
    *,
    output_dir: Path = OUTPUT_DIR,
    params: Mapping[str, Any] | None = None,
) -> Path:
    """Load the inputs, run a strategy on each one, and save the run.

    Args:
        strategy_name: Class name of an :class:`InferenceStrategy` subclass.
        output_dir: Base directory; the run lands in ``output_dir/<name>/<timestamp>``.
        params: Keyword arguments for the strategy's constructor.

    Returns:
        The run directory.
    """
    strategy = get_inference_strategy(strategy_name)(**(params or {}))

    logger.info("Loading inputs")
    inputs = data.load_inputs()
    expected = data.load_expected_outputs()
    logger.info("Running %s on %d inputs", strategy_name, len(inputs))

    predictions: dict[str, Prediction] = {}
    statuses: dict[str, dict[str, str | None]] = {}
    for key, item in tqdm(inputs.items(), desc=strategy_name, unit="input"):
        result, status, error = strategy.do_inference_safe(item)
        statuses[key] = {"status": status.value, "error": error}
        if result is not None:
            predictions[key] = result

    labels = {k: expected[k] for k in inputs if k in expected}
    if len(labels) < len(inputs):
        logger.warning(
            "%d of %d inputs have no expected output; they will be excluded from evaluation",
            len(inputs) - len(labels),
            len(inputs),
        )

    run_dir = output_dir / strategy_name / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    _dump(run_dir / "predictions.json", predictions)
    _dump(run_dir / "labels.json", labels)
    _dump(run_dir / "statuses.json", statuses)
    _dump(
        run_dir / "metadata.json",
        {
            **strategy.metadata(),
            "n_inputs": len(inputs),
            "keys": sorted(inputs),
            "git_commit": _git_commit(),
            "run_at": datetime.now().isoformat(timespec="seconds"),
        },
    )

    counts = Counter(s["status"] for s in statuses.values())
    logger.info(
        "Saved %d predictions to %s (%d success, %d failure, %d error)",
        len(predictions),
        run_dir,
        counts[InferenceStatus.SUCCESS],
        counts[InferenceStatus.FAILURE],
        counts[InferenceStatus.ERROR],
    )
    return run_dir


def run_evaluation(run_dir: Path, evaluator_name: str = DEFAULT_EVALUATOR) -> dict:
    """Evaluate a saved run against the expected outputs saved with it.

    Writes ``evaluation.json`` and any plots into ``run_dir`` and returns the
    evaluation dict. Safe to run repeatedly, e.g. after changing an evaluator.
    """
    run_dir = Path(run_dir)
    predicted = load_predictions(run_dir)
    labels_path = run_dir / "labels.json"
    if labels_path.exists():
        expected: dict[str, ExpectedOutput] = json.loads(labels_path.read_text())
    else:
        logger.warning("No labels.json in %s; using current expected outputs", run_dir)
        expected = data.load_expected_outputs()

    evaluator = get_evaluator(evaluator_name)()
    results = evaluator.evaluate_all(predicted, expected)
    _dump(run_dir / "evaluation.json", results)
    for name, fig in evaluator.make_plots(results).items():
        fig.savefig(run_dir / f"{name}.png", bbox_inches="tight")
    logger.info("Evaluation summary: %s", json.dumps(results["summary"], default=str))
    return results


def run_pipeline(
    strategy_name: str,
    evaluator_name: str = DEFAULT_EVALUATOR,
    *,
    output_dir: Path = OUTPUT_DIR,
    params: Mapping[str, Any] | None = None,
) -> Path:
    """Run inference then evaluation; returns the run directory."""
    run_dir = run_inference(strategy_name, output_dir=output_dir, params=params)
    run_evaluation(run_dir, evaluator_name)
    return run_dir


# ── run-directory I/O ────────────────────────────────────────────────────────


def load_predictions(run_dir: Path) -> dict[str, Prediction]:
    """Read ``predictions.json`` from a run directory."""
    return json.loads((Path(run_dir) / "predictions.json").read_text())


def _dump(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")


def _git_commit() -> str | None:
    try:
        return subprocess.run(  # noqa: S603 - fixed argv, no user input
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
