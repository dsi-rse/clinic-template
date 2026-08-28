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
    local version=$(docker compose run --rm "$service_name" python --version 2>&1 | grep -o 'Python.*')
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

test_dashboard() {
    local project_dir="$1"
    local project_name="$2"
    local project_slug="$3"
    local module_name="$4"
    echo "   Testing dashboard scaffold..."
    cd "$project_dir"

    echo "   Checking expected files are present..."
    local expected_files=(
        "dashboard/index.html"
        "dashboard/README.md"
        "dashboard/TUTORIAL.md"
        "dashboard/AGENTS.md"
        "dashboard/CLAUDE.md"
        "dashboard/.gitignore"
        "dashboard/package.json"
        "dashboard/package-lock.json"
        "dashboard/vite.config.ts"
        "dashboard/tsconfig.json"
        "dashboard/data.manifest.json"
        "dashboard/public/_redirects"
        "dashboard/data/dictionary/reqs_311.json"
        "dashboard/data/dictionary/reqs_311.md"
        "dashboard/data/dictionary/community_areas.json"
        "dashboard/data/dictionary/community_areas.md"
        "dashboard/scripts/pull_data.py"
        "dashboard/scripts/make_sample_geodata.py"
        "dashboard/src/main.tsx"
        "dashboard/src/App.tsx"
        "dashboard/src/store/filters.ts"
        "dashboard/src/lib/duckdb.ts"
        "dashboard/src/lib/useQuery.ts"
        "dashboard/src/components/PlotFigure.tsx"
        "dashboard/src/components/Card.tsx"
        "dashboard/src/pages/OverviewPage.tsx"
        "dashboard/src/pages/MapPage.tsx"
        "dashboard/src/pages/SqlPage.tsx"
        "dashboard/e2e/smoke.spec.ts"
        "dashboard/playwright.config.ts"
        ".github/workflows/dashboard.workflow.yml"
        "src/$module_name/dashboard_export.py"
    )
    for f in "${expected_files[@]}"; do
        if [ ! -f "$f" ]; then
            echo "   ✗ Expected file not found: $f"
            return 1
        fi
    done
    echo "   ✓ All expected dashboard files present"

    echo "   Checking for no leaked Jinja in dashboard/..."
    if grep -rl "{{ cookiecutter" dashboard/ 2>/dev/null | grep -q .; then
        echo "   ✗ Found leaked {{ cookiecutter }} in dashboard/"
        grep -rl "{{ cookiecutter" dashboard/
        return 1
    fi
    if grep -rl "{%" dashboard/ 2>/dev/null | grep -q .; then
        echo "   ✗ Found leaked {%...%} in dashboard/"
        grep -rl "{%" dashboard/
        return 1
    fi
    echo "   ✓ No Jinja leaked into dashboard/"

    echo "   Checking __PROJECT_NAME__ token replacement..."
    for f in "dashboard/index.html" "dashboard/README.md"; do
        if grep -q "__PROJECT_NAME__" "$f"; then
            echo "   ✗ __PROJECT_NAME__ token not replaced in $f"
            return 1
        fi
        if ! grep -q "$project_name" "$f"; then
            echo "   ✗ Project name not found in $f"
            return 1
        fi
    done
    echo "   ✓ __PROJECT_NAME__ replaced with project name"

    echo "   Checking JSON files are valid..."
    python3 -m json.tool dashboard/package.json > /dev/null
    python3 -m json.tool dashboard/package-lock.json > /dev/null
    python3 -m json.tool dashboard/data.manifest.json > /dev/null
    python3 -m json.tool dashboard/data/dictionary/reqs_311.json > /dev/null
    python3 -m json.tool dashboard/data/dictionary/community_areas.json > /dev/null
    echo "   ✓ package.json, package-lock.json, data.manifest.json, dictionaries valid"

    echo "   Checking workflow contains project slug..."
    if ! grep -q "$project_slug" .github/workflows/dashboard.workflow.yml; then
        echo "   ✗ Project slug not found in dashboard workflow"
        return 1
    fi
    echo "   ✓ Workflow contains project slug"

    echo "   Building dashboard in Docker (npm ci && npm run build)..."
    docker compose run --rm dashboard sh -c "npm ci && npm run build"
    echo "   ✓ Dashboard builds (tsc + vite) in node:22-slim"
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

