"""An evaluator for label predictions that also draws a confusion matrix."""

import matplotlib.pyplot as plt

from {{ cookiecutter.code_directory }}.framework.base import Evaluator
from {{ cookiecutter.code_directory }}.types import ExpectedOutput, Prediction


class ClassifierEvaluator(Evaluator):
    """Compare the predicted ``label`` to the expected one and plot a confusion matrix.

    This is an example of an evaluator with a ``make_plots`` method. Per item
    it records the predicted and actual labels and whether they match; the
    plot counts how often each (actual, predicted) pair occurred.

    TODO: replace this with an evaluator that fits your project.
    """

    def evaluate_single_output(
        self, predicted: Prediction, expected: ExpectedOutput
    ) -> dict[str, object]:
        """Predicted label, actual label, and whether they match."""
        return {
            "predicted": predicted["label"],
            "actual": expected["label"],
            "is_correct": predicted["label"] == expected["label"],
        }

    def make_plots(self, results: dict) -> dict[str, plt.Figure]:
        """A confusion matrix over every evaluated item, saved as ``confusion_matrix.png``."""
        rows = [r for r in results["per_item"].values() if r["status"] == "evaluated"]
        labels = sorted(
            {r["actual"] for r in rows} | {r["predicted"] for r in rows}, key=str
        )
        counts = [[0] * len(labels) for _ in labels]
        for r in rows:
            counts[labels.index(r["actual"])][labels.index(r["predicted"])] += 1

        fig, ax = plt.subplots()
        ax.imshow(counts, cmap="Blues")
        for i in range(len(labels)):
            for j in range(len(labels)):
                ax.text(j, i, str(counts[i][j]), ha="center", va="center")
        ax.set_xticks(range(len(labels)), [str(x) for x in labels])
        ax.set_yticks(range(len(labels)), [str(x) for x in labels])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        return {"confusion_matrix": fig}
