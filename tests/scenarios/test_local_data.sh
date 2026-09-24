#!/bin/bash
# Test: Local data directory (data_dir=local)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Local Data Directory (data_dir=local)"
PROJECT_NAME="Test Local Data"
PROJECT_SLUG="test-local-data"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

# Cleanup before test
cleanup_project "$PROJECT_DIR"
mkdir -p "$TEST_DIR"

# Run test.
# NOTE: bash ignores errexit inside a subshell that is part of an || list, so the
# subshell is run on its own and its exit status is checked explicitly.
set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="local" \
        cluster="no" \
        examples="no" \
        bsd="yes" \
        ann="no"
    
    build_docker "$PROJECT_DIR"
    test_python_version "$PROJECT_DIR" "$PROJECT_SLUG"
    test_package_imports "$PROJECT_DIR" "$PROJECT_SLUG"
    test_source_import "$PROJECT_DIR" "$PROJECT_SLUG" "utils"
    test_settings_import "$PROJECT_DIR" "$PROJECT_SLUG" "utils"
    
    print_test_success "$TEST_NAME"
)
status=$?
set -e
if [ "$status" -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR"
    exit 1
fi

# Cleanup after success
cleanup_project "$PROJECT_DIR"

