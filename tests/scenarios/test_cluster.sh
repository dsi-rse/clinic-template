#!/bin/bash
# Test: Cluster configuration (cluster=yes)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Cluster Configuration (cluster=yes)"
PROJECT_NAME="Test Cluster"
PROJECT_SLUG="test-cluster"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

# Cleanup before test
cleanup_project "$PROJECT_DIR"
mkdir -p "$TEST_DIR"

# Run test
# NOTE: the subshell must NOT be part of a `|| { ... }` list — that would
# disable `set -e` inside it and swallow failures. Capture $? instead.
set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="none" \
        cluster="yes" \
        examples="no" \
        bsd="yes" \
        ann="no"
    
    build_docker "$PROJECT_DIR"
    test_python_version "$PROJECT_DIR" "$PROJECT_SLUG"
    test_package_imports "$PROJECT_DIR" "$PROJECT_SLUG"
    test_source_import "$PROJECT_DIR" "$PROJECT_SLUG" "utils"
    test_cluster_config "$PROJECT_DIR" "$PROJECT_SLUG"
    
    print_test_success "$TEST_NAME"
)
STATUS=$?
set -e

if [ $STATUS -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR"
    exit 1
fi

# Cleanup after success
cleanup_project "$PROJECT_DIR"

