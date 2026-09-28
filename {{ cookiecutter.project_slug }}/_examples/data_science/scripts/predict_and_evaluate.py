"""Run a strategy over every input and evaluate it. The usual way to try a strategy.

Use scripts/evaluate.py to re-score a saved run without repeating inference.

Examples (inside the container; prefix with ``uv run`` outside it)::

    python scripts/predict_and_evaluate.py --strategy ExampleStrategy
    python scripts/predict_and_evaluate.py --strategy ExampleStrategy --param label=false
    python scripts/predict_and_evaluate.py --strategy MyStrategy --evaluator ClassifierEvaluator
"""

from __future__ import annotations

import json
import sys

from {{ cookiecutter.code_directory }}.framework.cli_options import (
    add_evaluator_option,
    add_run_options,
    add_strategy_option,
    configure_logging,
    make_parser,
    parse_params,
)
from {{ cookiecutter.code_directory }}.framework.pipeline import run_pipeline


def main(argv: list[str] | None = None) -> None:
    """Parse arguments, run the strategy, evaluate, print the summary."""
    parser = make_parser(__doc__)
    add_strategy_option(parser)
    add_evaluator_option(parser)
    add_run_options(parser)
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    run_dir = run_pipeline(
        args.strategy,
        args.evaluator,
        output_dir=args.output_dir,
        params=parse_params(args.param),
    )
    summary = json.loads((run_dir / "evaluation.json").read_text())["summary"]
    print(json.dumps(summary, indent=2, default=str))
    print(f"Run saved to {run_dir}")


if __name__ == "__main__":
    main(sys.argv[1:])
