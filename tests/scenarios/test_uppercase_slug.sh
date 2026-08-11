#!/bin/bash
# Test: Docker image name is lowercase even when the project slug has uppercase
# Regression test for https://github.com/uchicago-dsi/clinic-template/issues/36

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/../lib/helpers.sh"

TEST_NAME="Uppercase Slug (lowercase docker image name)"
PROJECT_NAME="Autumn IRC"
# A slug containing uppercase, as a user may enter at the prompt (see issue #36)
PROJECT_SLUG="2024-Autumn-IRC"
PROJECT_DIR="$TEST_DIR/$PROJECT_SLUG"

print_test_header "$TEST_NAME"

# Cleanup before test
cleanup_project "$PROJECT_DIR"
mkdir -p "$TEST_DIR"

(
    set -e
    create_project "$PROJECT_NAME" \
        project_slug="$PROJECT_SLUG" \
        docker="yes" \
        data_dir="none" \
        cluster="no" \
        examples="no" \
        bsd="yes" \
        ann="no"

    # docker compose derives the image reference from the service name, which is
    # the slug. Without a lowercased image name, `docker compose build` fails with
    # "invalid reference format: repository name must be lowercase".
    echo "   Building Docker image for an uppercase slug..."
    cd "$PROJECT_DIR"
    docker compose build --quiet
    echo "   ✓ Docker image built for uppercase slug"

    # The resolved image reference must be all lowercase.
    image=$(docker compose config --images)
    echo "   Resolved image: $image"
    if [ "$image" != "$(echo "$image" | tr '[:upper:]' '[:lower:]')" ]; then
        echo "   ✗ Resolved image name is not lowercase: $image"
        exit 1
    fi
    echo "   ✓ Resolved image name is lowercase"
)
STATUS=$?
set -e

if [ $STATUS -ne 0 ]; then
    print_test_failure "$TEST_NAME"
    cleanup_project "$PROJECT_DIR"
    exit 1
fi

print_test_success "$TEST_NAME"

# Cleanup after success
cleanup_project "$PROJECT_DIR"
