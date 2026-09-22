#!/bin/bash
# Test: Basic Docker setup (data_dir=none)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Basic Docker (data_dir=none)"
PROJECT_NAME="Test Basic Docker"
PROJECT_SLUG="test-basic-docker"
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
        cluster="no" \
        examples="no" \
        bsd="yes" \
        ann="no"
    
    build_docker "$PROJECT_DIR"
    test_python_version "$PROJECT_DIR" "$PROJECT_SLUG"
    test_package_imports "$PROJECT_DIR" "$PROJECT_SLUG"
    test_source_import "$PROJECT_DIR" "$PROJECT_SLUG" "utils"

    for f in TUTORIAL.md PROJECT_SETUP.md; do
        if [ -f "$PROJECT_DIR/$f" ]; then
            echo "   ✗ $f should not exist with examples=no"
            exit 1
        fi
    done
    echo "   ✓ Root TUTORIAL.md / PROJECT_SETUP.md absent"
    
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

