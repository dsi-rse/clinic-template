"""Base classes for inference strategies and evaluators, plus plugin discovery.

An inference strategy is any concrete subclass of :class:`InferenceStrategy` in
a module under ``inference_strategies/``; an evaluator is any concrete subclass
of :class:`Evaluator` under ``evaluators/``. Both are found by class name at
run time, so adding one means adding a file.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from collections.abc import Mapping
from types import ModuleType
from typing import TYPE_CHECKING, Any

from {{ cookiecutter.code_directory }}.types import (
    ExpectedOutput,
    InferenceStatus,
    Input,
    Prediction,
)

if TYPE_CHECKING:  # only needed for the make_plots annotation
    import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


# ── inference strategies ─────────────────────────────────────────────────────


class InferenceStrategy(ABC):
    """Abstract base class for inference strategies.

    Subclasses implement :meth:`do_inference`, which receives one ``Input`` and
    returns a ``Prediction``. Constructor arguments become the run's recorded
    parameters, so put anything you want to vary (thresholds, model names,
    prompt paths) there rather than in module-level constants.
    """

    @abstractmethod
    def do_inference(self, inference_input: Input) -> Prediction:
        """Produce a prediction for one input.

        Args:
            inference_input: One item from ``data.load_inputs()``.

        Returns:
            A dict with at least the keys marked ``Required`` on
            ``types.Prediction``, plus any extra JSON-serializable keys.
        """

    def do_inference_safe(
        self, inference_input: Input
    ) -> tuple[Prediction | None, InferenceStatus, str | None]:
        """Run :meth:`do_inference` with exception handling and output validation.

        Returns:
            ``(prediction, status, error_message)``. ``prediction`` is None
            unless status is SUCCESS.
        """
        try:
            result = self.do_inference(inference_input)
        except Exception as exc:
            logger.exception("do_inference() raised")
            return None, InferenceStatus.ERROR, f"{type(exc).__name__}: {exc}"

        problem = validate_prediction(result)
        if problem:
            logger.warning("Invalid prediction: %s", problem)
            return None, InferenceStatus.FAILURE, problem
        return result, InferenceStatus.SUCCESS, None

    def metadata(self) -> dict[str, Any]:
        """Name, description, and parameters (saved as metadata.json with every run)."""
        return {
            "name": self.__class__.__name__,
            "description": inspect.getdoc(self),
            "parameters": self.parameters(),
        }

    def parameters(self) -> dict[str, Any]:
        """Constructor parameters, taken from public instance attributes."""
        return {
            key: _jsonable(value)
            for key, value in self.__dict__.items()
            if not callable(value) and not key.startswith("_")
        }


def validate_prediction(result: object) -> str | None:
    """Return a problem description if ``result`` is not a valid ``Prediction``.

    The checks are generic: the result must be a dict with string keys that
    contains every key marked ``Required`` on ``types.Prediction``. To validate
    more (value types, ranges), edit ``Prediction`` or override
    :meth:`InferenceStrategy.do_inference_safe`.
    """
    if result is None:
        return "do_inference() returned None"
    if not isinstance(result, Mapping):
        return f"do_inference() returned {type(result).__name__}, not a dict"
    if any(not isinstance(key, str) for key in result):
        return "prediction keys must be strings so the run can be saved as JSON"
    missing = sorted(Prediction.__required_keys__ - set(result))
    if missing:
        return f"prediction is missing required key(s): {', '.join(missing)}"
    return None


def _jsonable(value: object) -> object:
    if isinstance(value, str | int | float | bool | type(None)):
        return value
    if isinstance(value, list | tuple | set):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return str(value)


# ── evaluators ───────────────────────────────────────────────────────────────


class Evaluator(ABC):
    """Abstract base class for evaluators.

    Implement :meth:`evaluate_single_output` for per-item results and, usually,
    :meth:`aggregate` for dataset-level metrics. :meth:`evaluate_all` combines
    them into ``{"per_item": {...}, "summary": {...}}``.
    """

    @abstractmethod
    def evaluate_single_output(
        self, predicted: Prediction, expected: ExpectedOutput
    ) -> dict[str, object]:
        """Compare one prediction to its expected output. Returns per-item results."""

    def aggregate(
        self,
        predicted: Mapping[str, Prediction],
        expected: Mapping[str, ExpectedOutput],
        per_item: Mapping[str, dict],
    ) -> dict[str, object]:
        """Dataset-level metrics over the items that were evaluated.

        ``predicted``, ``expected`` and ``per_item`` are already restricted to
        keys present in both predictions and expected outputs. Default: nothing.
        """
        return {}

    def make_plots(self, results: dict) -> dict[str, plt.Figure]:
        """Optionally produce plots from :meth:`evaluate_all` output.

        Returns:
            A dict mapping plot name to matplotlib Figure. The pipeline saves
            each one as ``<name>.png`` in the run directory.
        """
        return {}

    def evaluate_all(
        self,
        predicted: Mapping[str, Prediction],
        expected: Mapping[str, ExpectedOutput],
    ) -> dict[str, dict]:
        """Evaluate every item, then aggregate.

        Items missing from either side are reported under ``per_item`` with a
        ``status`` and excluded from the summary.
        """
        per_item: dict[str, dict] = {}
        both: dict[str, tuple] = {}
        for key in sorted(set(predicted) | set(expected)):
            if key not in predicted:
                per_item[key] = {"status": "missing_from_predicted"}
            elif key not in expected:
                per_item[key] = {"status": "missing_from_expected"}
            else:
                per_item[key] = {
                    "status": "evaluated",
                    **self.evaluate_single_output(predicted[key], expected[key]),
                }
                both[key] = (predicted[key], expected[key])
        summary = self.aggregate(
            {k: p for k, (p, _) in both.items()},
            {k: e for k, (_, e) in both.items()},
            {k: per_item[k] for k in both},
        )
        statuses = [r["status"] for r in per_item.values()]
        summary = {
            "n_evaluated": len(both),
            "n_missing_from_predicted": statuses.count("missing_from_predicted"),
            "n_missing_from_expected": statuses.count("missing_from_expected"),
            **summary,
        }
        return {"per_item": per_item, "summary": summary}


# ── plugin discovery ─────────────────────────────────────────────────────────


def discover_subclasses(package: ModuleType, base_class: type) -> dict[str, type]:
    """Import every module in *package* and collect concrete subclasses of *base_class*."""
    found: dict[str, type] = {}
    for _importer, modname, _ispkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f".{modname}", package=package.__name__)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, base_class)
                and obj is not base_class
                and not inspect.isabstract(obj)
                and obj.__module__ == module.__name__
            ):
                if name in found and found[name] is not obj:
                    raise ValueError(
                        f"Duplicate class name '{name}' in '{module.__name__}' "
                        f"(already registered from '{found[name].__module__}')"
                    )
                found[name] = obj
    return found


def get_subclass(name: str, package: ModuleType, base_class: type, label: str) -> type:
    """Look up one concrete subclass by class name, with a helpful error."""
    registry = discover_subclasses(package, base_class)
    if name not in registry:
        available = ", ".join(sorted(registry)) or "(none)"
        raise KeyError(f"No {label} named '{name}'. Available: {available}")
    return registry[name]


# The four functions below import the plugin packages inside the function body
# because those packages import this module: importing them at the top would
# be a circular import.


def discover_inference_strategies() -> dict[str, type[InferenceStrategy]]:
    """All strategies under ``inference_strategies/``, by class name."""
    from {{ cookiecutter.code_directory }} import inference_strategies as pkg

    return discover_subclasses(pkg, InferenceStrategy)


def get_inference_strategy(name: str) -> type[InferenceStrategy]:
    """A strategy class by name."""
    from {{ cookiecutter.code_directory }} import inference_strategies as pkg

    return get_subclass(name, pkg, InferenceStrategy, "inference strategy")


def discover_evaluators() -> dict[str, type[Evaluator]]:
    """All evaluators under ``evaluators/``, by class name."""
    from {{ cookiecutter.code_directory }} import evaluators as pkg

    return discover_subclasses(pkg, Evaluator)


def get_evaluator(name: str) -> type[Evaluator]:
    """An evaluator class by name."""
    from {{ cookiecutter.code_directory }} import evaluators as pkg

    return get_subclass(name, pkg, Evaluator, "evaluator")
