#!/bin/bash
# Test: Dashboard scaffold (dashboard=yes and dashboard=no scenarios)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

# ---------------------------------------------------------------------------
# Scenario 1: dashboard=yes
# ---------------------------------------------------------------------------

TEST_NAME="Dashboard scaffold (dashboard=yes)"
PROJECT_NAME="Test Dashboard Yes"
PROJECT_SLUG="test-dashboard-yes"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true
mkdir -p "$TEST_DIR"

# NOTE: the subshell must NOT be part of a `|| { ... }` list — that would
# disable `set -e` inside it and swallow failures. Capture $? instead.
set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="none" \
        cluster="no" \
        examples="no" \
        bsd="no" \
        ann="no" \
        dashboard="yes"

    test_dashboard "$PROJECT_DIR" "$PROJECT_NAME" "$PROJECT_SLUG" "utils"
)
STATUS=$?
set -e

if [ $STATUS -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR" || true
    exit 1
fi
print_test_success "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true

# ---------------------------------------------------------------------------
# Scenario 2: dashboard=no
# ---------------------------------------------------------------------------

TEST_NAME="Dashboard scaffold (dashboard=no)"
PROJECT_NAME="Test Dashboard No"
PROJECT_SLUG="test-dashboard-no"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true

set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="none" \
        cluster="no" \
        examples="no" \
        bsd="no" \
        ann="no" \
        dashboard="no"

    echo "   Checking dashboard/ is absent..."
    if [ -d "$PROJECT_DIR/dashboard" ]; then
        echo "   ✗ dashboard/ directory should not exist when dashboard=no"
        exit 1
    fi
    echo "   ✓ dashboard/ directory absent"

    echo "   Checking dashboard workflow is absent..."
    if [ -f "$PROJECT_DIR/.github/workflows/dashboard.workflow.yml" ]; then
        echo "   ✗ dashboard.workflow.yml should not exist when dashboard=no"
        exit 1
    fi
    echo "   ✓ dashboard.workflow.yml absent"

    echo "   Checking dashboard_export.py is absent..."
    if [ -f "$PROJECT_DIR/src/utils/dashboard_export.py" ]; then
        echo "   ✗ dashboard_export.py should not exist when dashboard=no"
        exit 1
    fi
    echo "   ✓ dashboard_export.py absent"

    echo "   Checking no dashboard service in docker-compose.yaml..."
    if grep -qE "dashboard_node_modules|node:22-slim" "$PROJECT_DIR/docker-compose.yaml"; then
        echo "   ✗ docker-compose.yaml still contains the dashboard service"
        exit 1
    fi
    echo "   ✓ docker-compose.yaml has no dashboard service"

    echo "   Checking no dashboard targets in Makefile..."
    if grep -qE "dashboard-data|dashboard-install|dashboard-dev|dashboard-build" "$PROJECT_DIR/Makefile"; then
        echo "   ✗ Makefile still contains dashboard targets"
        exit 1
    fi
    echo "   ✓ Makefile has no dashboard targets"

    echo "   Checking rendered docker-compose.yaml and Makefile still parse..."
    (cd "$PROJECT_DIR" && docker compose config -q)
    (cd "$PROJECT_DIR" && make -n build-only > /dev/null)
    echo "   ✓ docker compose config and make -n succeed"
)
STATUS=$?
set -e

if [ $STATUS -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR" || true
    exit 1
fi
print_test_success "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true

# ---------------------------------------------------------------------------
# Scenario 3: dashboard=yes + examples=data-science (unified root docs)
# ---------------------------------------------------------------------------

TEST_NAME="Dashboard + data-science scaffold (unified docs)"
PROJECT_NAME="Test Dashboard DS"
PROJECT_SLUG="test-dashboard-ds"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true

set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="box" \
        cluster="no" \
        examples="data-science" \
        bsd="no" \
        ann="no" \
        dashboard="yes"

    cd "$PROJECT_DIR"
    test_root_docs "Building and Running Your First Strategy" "Data science scaffold"
    test_root_docs "Building and Extending Your Dashboard" "## Dashboard"
    for marker in "Step 2b" "Part 1"; do
        if ! grep -q "$marker" TUTORIAL.md; then
            echo "   ✗ TUTORIAL.md missing combined-project text: $marker"
            exit 1
        fi
    done
    if ! grep -q "dashboard_export.py" PROJECT_SETUP.md; then
        echo "   ✗ PROJECT_SETUP.md missing the pipeline -> dashboard note"
        exit 1
    fi
    echo "   ✓ Unified TUTORIAL.md / PROJECT_SETUP.md contain both parts and the bridge"

    if [ -d "_examples" ]; then
        echo "   ✗ _examples/ staging directory was not removed"
        exit 1
    fi
    for f in "dashboard/index.html" "src/utils/dashboard_export.py" "src/utils/io.py"; do
        if [ ! -f "$f" ]; then
            echo "   ✗ Expected file not found: $f"
            exit 1
        fi
    done
    echo "   ✓ Dashboard and data-science scaffolds both present"
)
STATUS=$?
set -e

if [ $STATUS -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR" || true
    exit 1
fi
print_test_success "$TEST_NAME"

cleanup_project "$PROJECT_DIR" || true
