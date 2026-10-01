"""Argument-parsing helpers shared by the scripts in ``scripts/``.

Every script is a thin wrapper: parse arguments with ``argparse``, call one
function from this package, print the result. This module holds the option
groups the scripts have in common so each script stays short. Nothing else in
the package imports it.

Note: the ``--strategy`` and ``--evaluator`` choices come from importing every
module under ``inference_strategies/`` and ``evaluators/``, so a syntax error
in any of those files will break ``--help`` for every script. That is on
purpose: the traceback points straight at the broken file.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from {{ cookiecutter.code_directory }}.framework.base import (
    discover_evaluators,
    discover_inference_strategies,
)
from {{ cookiecutter.code_directory }}.framework.pipeline import DEFAULT_EVALUATOR, OUTPUT_DIR


def make_parser(description: str) -> argparse.ArgumentParser:
    """An ArgumentParser with the shared ``--verbose`` flag."""
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging.")
    return parser


def configure_logging(verbose: bool) -> None:
    """INFO logging by default, DEBUG with ``--verbose``."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def add_strategy_option(parser: argparse.ArgumentParser) -> None:
    """``--strategy`` and ``--param KEY=VALUE`` (repeatable)."""
    parser.add_argument(
        "--strategy",
        required=True,
        choices=sorted(discover_inference_strategies()),
        help="Strategy class name (a class in inference_strategies/).",
    )
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help=(
            "Strategy constructor argument; repeat for several. "
            "Values are JSON-decoded when possible, e.g. threshold=0.7 or label=false."
        ),
    )


def add_evaluator_option(parser: argparse.ArgumentParser) -> None:
    """``--evaluator`` with the default evaluator preselected."""
    parser.add_argument(
        "--evaluator",
        default=DEFAULT_EVALUATOR,
        choices=sorted(discover_evaluators()),
        help=f"Evaluator class name (default: {DEFAULT_EVALUATOR}).",
    )


def add_run_options(parser: argparse.ArgumentParser) -> None:
    """``--output-dir``."""
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Where run directories are written (default {OUTPUT_DIR}).",
    )


def parse_params(params: list[str]) -> dict[str, object]:
    """Turn ``["threshold=0.7", "label=false", "name=x"]`` into a dict, JSON-decoding values."""
    parsed: dict[str, object] = {}
    for p in params:
        key, sep, value = p.partition("=")
        if not sep:
            raise SystemExit(f"--param expects KEY=VALUE, got {p!r}")
        try:
            parsed[key] = json.loads(value)
        except (json.JSONDecodeError, ValueError):
            parsed[key] = value
    return parsed
