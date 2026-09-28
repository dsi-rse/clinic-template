"""Structural checks on scripts/ and src/. They need no data.

The one end-to-end test is skipped until data.py is implemented; see the
note on it.
"""

import importlib
import re
from pathlib import Path

import evaluate
import predict_and_evaluate
import pytest

from {{ cookiecutter.code_directory }}.framework.cli_options import parse_params

PACKAGE = "{{ cookiecutter.code_directory }}"
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
SRC_DIR = ROOT / "src"


def test_package_never_imports_scripts():
    offenders = [
        p
        for p in SRC_DIR.rglob("*.py")
        if re.search(r"^\s*(from|import)\s+scripts\b", p.read_text(), re.M)
    ]
    assert offenders == []


def test_every_script_has_a_docstring_and_main():
    for path in SCRIPTS_DIR.glob("*.py"):
        text = path.read_text()
        assert text.startswith('"""'), path.name
        assert 'if __name__ == "__main__":' in text, path.name


def test_parse_params_json_decodes_values():
    assert parse_params(["model=x", "threshold=0.7", "flags=[1,2]", "on=true"]) == {
        "model": "x",
        "threshold": 0.7,
        "flags": [1, 2],
        "on": True,
    }
    with pytest.raises(SystemExit):
        parse_params(["no-equals-sign"])


def test_help_lists_strategies_and_evaluators(capsys):
    with pytest.raises(SystemExit) as exc:
        predict_and_evaluate.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in ["ExampleStrategy", "ExampleEvaluator", "ClassifierEvaluator"]:
        assert name in out


def test_evaluate_help_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        evaluate.main(["--help"])
    assert exc.value.code == 0
    assert "run_dir" in capsys.readouterr().out


def test_doc_import_lines_resolve():
    """Every `from <package>... import ...` line in the docs names real modules and names.

    Lines that import from a module the tutorial tells the student to create
    (anything containing `.my_`) are skipped.
    """
    pattern = re.compile(
        rf"^from ({re.escape(PACKAGE)}(?:\.[\w.]+)?) import ([\w, ]+)$", re.M
    )
    checked = 0
    for doc in [ROOT / "README.md", ROOT / "TUTORIAL.md"]:
        for module_name, names in pattern.findall(doc.read_text()):
            if ".my_" in module_name:
                continue
            module = importlib.import_module(module_name)
            for name in names.split(","):
                assert hasattr(
                    module, name.strip()
                ), f"{doc.name}: {module_name}.{name.strip()}"
                checked += 1
    assert checked > 0


@pytest.mark.skip(
    reason="Needs data.py implemented: remove this marker once load_inputs() and "
    "load_expected_outputs() work (see PROJECT_SETUP.md, section 4)."
)
def test_run_example_strategy_end_to_end(tmp_path, capsys):
    predict_and_evaluate.main(
        ["--strategy", "ExampleStrategy", "--output-dir", str(tmp_path)]
    )
    out = capsys.readouterr().out
    run_dirs = list((tmp_path / "ExampleStrategy").iterdir())
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    for name in [
        "predictions.json",
        "labels.json",
        "statuses.json",
        "metadata.json",
        "evaluation.json",
    ]:
        assert (run_dir / name).exists(), name
    assert f"Run saved to {run_dir}" in out

    before = (run_dir / "evaluation.json").read_text()
    evaluate.main([str(run_dir)])
    assert (run_dir / "evaluation.json").read_text() == before  # deterministic
