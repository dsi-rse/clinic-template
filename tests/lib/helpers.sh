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

    # Every file that should have been copied into src/<module>/
    local expected_files=(
        "src/$module_name/cli.py"
        "src/$module_name/evaluation.py"
        "src/$module_name/inference.py"
        "src/$module_name/io.py"
        "src/$module_name/pipeline.py"
        "src/$module_name/register.py"
        "src/$module_name/evaluators/__init__.py"
        "src/$module_name/evaluators/classifier_evaluator.py"
        "src/$module_name/evaluators/example_evaluator.py"
        "src/$module_name/inference_strategies/__init__.py"
        "src/$module_name/inference_strategies/example_strategy.py"
    )

    for f in "${expected_files[@]}"; do
        if [ ! -f "$f" ]; then
            echo "   ✗ Expected file not found: $f"
            return 1
        fi
        echo "   ✓ $f"
    done

    # Confirm the example submodules are importable inside the container
    docker compose run --rm "$service_name" python -c "
from $module_name import cli, evaluation, inference, io, pipeline, register
from $module_name.evaluators import classifier_evaluator, example_evaluator
from $module_name.inference_strategies import example_strategy
print('   ✓ all data-science example modules imported successfully')
"
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

