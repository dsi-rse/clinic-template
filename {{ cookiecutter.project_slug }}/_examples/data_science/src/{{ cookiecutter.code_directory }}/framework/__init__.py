"""The harness that runs strategies and evaluators. You should not need to edit it.

- ``base.py``         the ``InferenceStrategy`` and ``Evaluator`` base classes,
                      and how concrete subclasses are found by class name.
- ``pipeline.py``     run a strategy over every input, save the run, evaluate it.
- ``cli_options.py``  the argparse option groups shared by the scripts in ``scripts/``.

Project-specific code lives one level up: ``data.py``, ``types.py``,
``inference_strategies/`` and ``evaluators/``.
"""
