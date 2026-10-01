"""The simplest possible strategy: predict the same label for every input."""

from {{ cookiecutter.code_directory }}.framework.base import InferenceStrategy
from {{ cookiecutter.code_directory }}.types import Input, Prediction


class ExampleStrategy(InferenceStrategy):
    """Predict a constant label for every input.

    This is a baseline to compare real strategies against, and a template for
    writing one: subclass ``InferenceStrategy``, implement ``do_inference``,
    and take anything you want to vary as a constructor argument. Constructor
    arguments are recorded in ``metadata.json`` with every run, and can be set
    from the command line with ``--param label=false``.

    TODO: replace this with a strategy that looks at the input.
    """

    def __init__(self, label: bool = True) -> None:
        """Remember which label to predict."""
        self.label = label

    def do_inference(self, inference_input: Input) -> Prediction:
        """Ignore the input and return the configured label."""
        return {"label": self.label}
