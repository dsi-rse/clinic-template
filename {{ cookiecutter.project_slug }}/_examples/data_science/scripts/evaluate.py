"""Re-score a saved run directory against the expected outputs saved with it.

Evaluation is cheap and deterministic; inference may not be. Use this after
changing or adding an evaluator, so no inference is repeated.

Example::

    python scripts/evaluate.py "$DATA_DIR/output/ExampleStrategy/2026-09-27_10-15-00" --evaluator ExampleEvaluator
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from {{ cookiecutter.code_directory }}.framework.cli_options import (
    add_evaluator_option,
    configure_logging,
    make_parser,
)
from {{ cookiecutter.code_directory }}.framework.pipeline import run_evaluation


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and evaluate the run."""
    parser = make_parser(__doc__)
    parser.add_argument(
        "run_dir", type=Path, help="A run directory under DATA_DIR/output/."
    )
    add_evaluator_option(parser)
    args = parser.parse_args(argv)
    configure_logging(args.verbose)

    results = run_evaluation(args.run_dir, args.evaluator)
    print(json.dumps(results["summary"], indent=2, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])
