#!/bin/bash
# Test: examples=data-science scaffold files are generated correctly

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Examples (data-science scaffold)"
PROJECT_NAME="Test Examples Data Science"
PROJECT_SLUG="test-examples-data-science"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

# Cleanup before test
cleanup_project "$PROJECT_DIR"
mkdir -p "$TEST_DIR"

# The data-science scaffold imports settings.DATA_DIR, which only exists when
# data_dir != none, so generate it the way the docs assume: with Box.
# Run test
# NOTE: the subshell must NOT be part of a `|| { ... }` list — that would
# disable `set -e` inside it and swallow failures. Capture $? instead.
set +e
(
    set -e
    create_project "$PROJECT_NAME" \
        docker="yes" \
        data_dir="box" \
        cluster="no" \
        examples="data-science" \
        bsd="yes" \
        ann="no"

    build_docker "$PROJECT_DIR"
    test_examples_data_science "$PROJECT_DIR" "$PROJECT_SLUG" "utils"

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
