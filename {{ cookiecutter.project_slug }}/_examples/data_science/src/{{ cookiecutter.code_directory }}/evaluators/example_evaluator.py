"""The simplest possible evaluator: exact match on every expected field."""

from collections.abc import Mapping

from {{ cookiecutter.code_directory }}.framework.base import Evaluator
from {{ cookiecutter.code_directory }}.types import ExpectedOutput, Prediction


class ExampleEvaluator(Evaluator):
    """Count a prediction as correct if it matches every field of the expected output.

    Extra keys on the prediction (for example ``confidence``) are ignored.
    The summary reports plain accuracy.

    TODO: replace or extend this with scoring that fits your project.
    """

    def evaluate_single_output(
        self, predicted: Prediction, expected: ExpectedOutput
    ) -> dict[str, object]:
        """Whether every expected field matches the prediction."""
        return {"is_correct": all(predicted.get(k) == v for k, v in expected.items())}

    def aggregate(
        self,
        predicted: Mapping[str, Prediction],
        expected: Mapping[str, ExpectedOutput],
        per_item: Mapping[str, dict],
    ) -> dict[str, object]:
        """Fraction of evaluated items that were correct."""
        correct = sum(1 for r in per_item.values() if r["is_correct"])
        return {"accuracy": correct / len(per_item) if per_item else float("nan")}
