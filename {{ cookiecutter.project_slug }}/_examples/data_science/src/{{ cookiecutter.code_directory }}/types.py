"""The types that flow through the pipeline. Edit these to match your project.

These are deliberately generic placeholders. During project setup they should
be replaced with types that describe the real data: what one input looks like,
what a strategy is expected to return, and what the expected (ground-truth)
output looks like. The framework only relies on two things:

- ``Prediction`` and ``ExpectedOutput`` are dicts, so they can be saved as JSON.
- The keys listed as ``Required`` on ``Prediction`` are what
  ``framework.base.validate_prediction`` checks for.
"""

from enum import StrEnum
from typing import Any, Required, TypedDict

# One item from the dataset, as returned by ``data.load_inputs()``.
# TODO: replace ``Any`` with a real type (a dataclass, a str, a DataFrame row...).
Input = Any


class Prediction(TypedDict, total=False):
    """What ``InferenceStrategy.do_inference`` returns for one input.

    ``label`` is the one key every strategy must produce; the example
    evaluators compare it to the expected label. Strategies may add any other
    JSON-serializable keys; they are saved with the run and ignored by
    evaluators that do not know about them.

    TODO: replace ``label: bool`` with whatever your project predicts.
    """

    label: Required[bool]


class ExpectedOutput(TypedDict):
    """The ground truth for one input, as returned by ``data.load_expected_outputs()``.

    TODO: replace ``label: bool`` to match ``Prediction``.
    """

    label: bool


class InferenceStatus(StrEnum):
    """What happened when a strategy ran on one input."""

    SUCCESS = "success"  # do_inference returned a valid Prediction
    FAILURE = "failure"  # do_inference returned something invalid (see statuses.json)
    ERROR = "error"  # do_inference raised an exception
