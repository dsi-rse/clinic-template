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
