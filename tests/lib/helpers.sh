#!/bin/bash
# Shared helper functions for template tests

# Configuration
export TEST_DIR="${TEST_DIR:-/tmp/clinic-template-test}"
export TEMPLATE_DIR="${TEMPLATE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

cleanup_project() {
    local project_dir="$1"
    if [ -d "$project_dir" ]; then
        cd "$project_dir" 2>/dev/null && docker compose down 2>/dev/null || true
        rm -rf "$project_dir"
    fi
}

#------------------------------------------------------------------------------
# Project Creation
#------------------------------------------------------------------------------

create_project() {
    local project_name="$1"
    shift  # Remove first argument, rest are cookiecutter options
    
    echo "   Creating project '$project_name'..."
    cd "$TEMPLATE_DIR"
    cookiecutter . \
        --no-input \
        --overwrite-if-exists \
        --output-dir "$TEST_DIR" \
        project_name="$project_name" \
        "$@"
    echo "   ✓ Project created"
}

#------------------------------------------------------------------------------
# Docker
#------------------------------------------------------------------------------

build_docker() {
    local project_dir="$1"
    echo "   Building Docker image..."
    cd "$project_dir"
    if ! docker info >/dev/null 2>&1; then
        echo "   ✗ Docker daemon is not running"
        return 1
    fi
    docker compose build --quiet
    echo "   ✓ Docker image built"
}

#------------------------------------------------------------------------------
# Python Tests
#------------------------------------------------------------------------------

test_python_version() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Testing Python installation..."
    cd "$project_dir"
    local version
    version=$(docker compose run --rm "$service_name" python --version 2>/dev/null)
    echo "   ✓ $version"
}

test_package_imports() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Testing package imports..."
    cd "$project_dir"
    docker compose run --rm "$service_name" python -c "
import pandas
import numpy
print(f'   ✓ pandas={pandas.__version__}')
print(f'   ✓ numpy={numpy.__version__}')
"
}

test_source_import() {
    local project_dir="$1"
    local service_name="$2"
    local module_name="$3"
    echo "   Testing source code import ($module_name)..."
    cd "$project_dir"
    docker compose run --rm "$service_name" python -c "
import $module_name
print('   ✓ $module_name package imported')
"
}

#------------------------------------------------------------------------------
# Feature-Specific Tests
#------------------------------------------------------------------------------

test_settings_import() {
    local project_dir="$1"
    local service_name="$2"
    local module_name="$3"
    echo "   Testing settings.py and DATA_DIR..."
    cd "$project_dir"
    docker compose run --rm "$service_name" python -c "
from $module_name.settings import DATA_DIR
from pathlib import Path
assert DATA_DIR is not None, 'DATA_DIR should not be None'
assert isinstance(DATA_DIR, Path), 'DATA_DIR should be a Path'
print(f'   ✓ DATA_DIR={DATA_DIR}')
"
}

test_cluster_config() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Testing cluster configuration..."
    cd "$project_dir"
    
    # Check config directory exists
    if [ ! -d "config" ]; then
        echo "   ✗ config/ directory not found"
        return 1
    fi
    echo "   ✓ config/ directory exists"
    
    # Check sample.json exists
    if [ ! -f "config/query/sample.json" ]; then
        echo "   ✗ config/query/sample.json not found"
        return 1
    fi
    echo "   ✓ config/query/sample.json exists"
    
    # Check submitit is importable
    docker compose run --rm "$service_name" python -c "
import submitit
print(f'   ✓ submitit={submitit.__version__}')
"
}

test_examples_data_science() {
    local project_dir="$1"
    local service_name="$2"
    local module_name="$3"
    echo "   Testing data-science examples scaffold..."
    cd "$project_dir"

    # _examples/ staging directory must be removed by the hook
    if [ -d "_examples" ]; then
        echo "   ✗ _examples/ staging directory was not removed"
        return 1
    fi
    echo "   ✓ _examples/ staging directory removed"

    # Every file the scaffold should have put in place
    local expected_files=(
        "src/$module_name/__init__.py"
        "src/$module_name/settings.py"
        "src/$module_name/data.py"
        "src/$module_name/types.py"
        "src/$module_name/framework/__init__.py"
        "src/$module_name/framework/base.py"
        "src/$module_name/framework/pipeline.py"
        "src/$module_name/framework/cli_options.py"
        "src/$module_name/evaluators/__init__.py"
        "src/$module_name/evaluators/example_evaluator.py"
        "src/$module_name/evaluators/classifier_evaluator.py"
        "src/$module_name/inference_strategies/__init__.py"
        "src/$module_name/inference_strategies/example_strategy.py"
        "scripts/README.md"
        "scripts/predict_and_evaluate.py"
        "scripts/evaluate.py"
        "tests/conftest.py"
        "tests/test_scripts.py"
        "TUTORIAL.md"
        "PROJECT_SETUP.md"
        "output/README.md"
    )
    for f in "${expected_files[@]}"; do
        if [ ! -f "$f" ]; then
            echo "   ✗ Expected file not found: $f"
            return 1
        fi
        echo "   ✓ $f"
    done

    # Files from the old click-based scaffold must be gone
    local removed_files=(
        "src/$module_name/cli.py"
        "src/$module_name/inference.py"
        "src/$module_name/evaluation.py"
        "src/$module_name/register.py"
        "src/$module_name/io.py"
        "src/$module_name/pipeline.py"
    )
    for f in "${removed_files[@]}"; do
        if [ -e "$f" ]; then
            echo "   ✗ Stale file still present: $f"
            return 1
        fi
    done
    echo "   ✓ no stale scaffold files"

    # Wiring checks
    if grep -q '\[project.scripts\]' pyproject.toml || grep -q 'click' pyproject.toml; then
        echo "   ✗ pyproject.toml still has the click console script"
        return 1
    fi
    if ! grep -q 'predict_and_evaluate.py' scripts/README.md; then
        echo "   ✗ scripts/README.md was not overlaid by the data-science version"
        return 1
    fi
    echo "   ✓ pyproject and scripts/README.md wired correctly"

    # Confirm every module imports inside the container and discovery finds the examples
    docker compose run --rm "$service_name" python -c "
import sys
from $module_name import data, settings, types
from $module_name.framework import base, cli_options, pipeline
from $module_name.evaluators import classifier_evaluator, example_evaluator
from $module_name.inference_strategies import example_strategy
sys.path.insert(0, 'scripts')
import evaluate, predict_and_evaluate
assert 'ExampleStrategy' in base.discover_inference_strategies()
assert {'ClassifierEvaluator', 'ExampleEvaluator'} <= set(base.discover_evaluators())
print('   ✓ all data-science example modules imported and discovered')
"
}

test_ds_scripts_help() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Testing script --help output..."
    cd "$project_dir"
    local out
    out=$(docker compose run --rm "$service_name" python scripts/predict_and_evaluate.py --help)
    for name in ExampleStrategy ClassifierEvaluator ExampleEvaluator; do
        if ! echo "$out" | grep -q "$name"; then
            echo "   ✗ predict_and_evaluate.py --help does not mention $name"
            return 1
        fi
    done
    out=$(docker compose run --rm "$service_name" python scripts/evaluate.py --help)
    if ! echo "$out" | grep -q "run_dir"; then
        echo "   ✗ evaluate.py --help does not mention run_dir"
        return 1
    fi
    echo "   ✓ both scripts print help listing the discovered plug-ins"
}

test_ds_pytest_and_ruff() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Running pytest and ruff inside the container..."
    cd "$project_dir"
    docker compose run --rm "$service_name" python -m pytest tests/ -q
    docker compose run --rm "$service_name" ruff check .
    echo "   ✓ pytest and ruff check passed"
}

test_ds_run_fails_with_not_implemented() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Running the pipeline against the unimplemented data layer..."
    cd "$project_dir"
    local out
    out=$(docker compose run --rm "$service_name" python scripts/predict_and_evaluate.py --strategy ExampleStrategy 2>&1) && {
        echo "   ✗ predict_and_evaluate.py succeeded but data.py is a stub"
        return 1
    }
    if ! echo "$out" | grep -q "NotImplementedError"; then
        echo "   ✗ expected NotImplementedError from data.py, got:"
        echo "$out" | tail -5
        return 1
    fi
    if [ -d "data/output/ExampleStrategy" ]; then
        echo "   ✗ a run directory was created even though inference never ran"
        return 1
    fi
    echo "   ✓ pipeline fails cleanly with NotImplementedError before writing anything"
}

test_precommit() {
    local project_dir="$1"
    local service_name="$2"
    echo "   Running pre-commit hooks..."
    cd "$project_dir"
    
    # Initialize git repo (required for pre-commit)
    git init --quiet
    git add -A
    
    # Run pre-commit inside container
    docker compose run --rm "$service_name" pre-commit run --all-files
    echo "   ✓ pre-commit passed"
}

#------------------------------------------------------------------------------
# Test Runner
#------------------------------------------------------------------------------

print_test_header() {
    local test_name="$1"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

print_test_success() {
    local test_name="$1"
    echo "   ✓ All checks passed for: $test_name"
    echo ""
    echo "=== TEST PASSED ==="
}

print_test_failure() {
    local test_name="$1"
    echo "   ✗ FAILED: $test_name"
    echo ""
    echo "=== TEST FAILED ==="
}

