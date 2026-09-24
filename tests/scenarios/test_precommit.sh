#!/bin/bash
# Test: Pre-commit hooks

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Pre-commit Hooks"
PROJECT_NAME="Test Precommit"
PROJECT_SLUG="test-precommit"
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
        data_dir="none" \
        cluster="no" \
        examples="no" \
        bsd="yes" \
        ann="yes"
    
    build_docker "$PROJECT_DIR"
    test_precommit "$PROJECT_DIR" "$PROJECT_SLUG"
    
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

