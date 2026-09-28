"""How inputs and expected outputs are loaded. Edit this to match your project.

The pipeline calls these two functions and nothing else about the data, so
implementing them is what connects the scaffold to a real project. Both return
dicts keyed by a unique identifier, and the two dicts must use the same keys:
``load_expected_outputs()[key]`` is the ground truth for ``load_inputs()[key]``.

``data_dir`` defaults to ``settings.DATA_DIR`` and exists so tests can point
the loaders at a small fixture directory.
"""

from pathlib import Path

from {{ cookiecutter.code_directory }} import settings
from {{ cookiecutter.code_directory }}.types import ExpectedOutput, Input


def load_inputs(data_dir: Path | None = None) -> dict[str, Input]:
    """Load every input the strategies should run on.

    Args:
        data_dir: Where the data lives. Defaults to ``settings.DATA_DIR``.

    Returns:
        A dict mapping a unique key to one input.
    """
    data_dir = settings.DATA_DIR if data_dir is None else data_dir
    # TODO: replace this with code that reads your input data from ``data_dir``.
    raise NotImplementedError(
        f"load_inputs() is not implemented yet (data_dir={data_dir})"
    )


def load_expected_outputs(data_dir: Path | None = None) -> dict[str, ExpectedOutput]:
    """Load the ground truth that predictions are scored against.

    Args:
        data_dir: Where the data lives. Defaults to ``settings.DATA_DIR``.

    Returns:
        A dict mapping the same keys as ``load_inputs()`` to expected outputs.
    """
    data_dir = settings.DATA_DIR if data_dir is None else data_dir
    # TODO: replace this with code that reads your expected outputs from ``data_dir``.
    raise NotImplementedError(
        f"load_expected_outputs() is not implemented yet (data_dir={data_dir})"
    )
