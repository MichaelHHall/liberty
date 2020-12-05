#!/bin/bash
# This will hopefully build and run the liberty docker container
# Also hopefully will skip building if it has already been built
set -euo pipefail

# Ensure that the bot is not already running
docker rm --force liberty >/dev/null 2>&1 || true

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $DIR
IMAGE_NAME=libertyprime
IMAGE_TAG=$(git -C "${DIR}" rev-parse --short HEAD)

FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

# If I were smart I would check for dirty git first, since this could build
# a container using uncommitted code but tag it as non-dirty
# But I guess I don't really care right now
if ! docker inspect --type=image "${FULL_IMAGE_NAME}" >/dev/null 2>&1; then
    # Need to rebuild. Also prune old images (older than 10 days).
    docker image prune -a -f --filter "until=240h"
    docker build -t "${FULL_IMAGE_NAME}" "${DIR}"
else
    # Check if git is dirty, if so rebuild
    if [[ $(git -C "${DIR}" diff --stat) != '' ]]; then
        docker image prune -a -f --filter "until=240h"
        FULL_IMAGE_NAME="${IMAGE_NAME}:dirty"
        docker build -t "${FULL_IMAGE_NAME}" "${DIR}"
    fi
fi

# Run image
docker run --detach --name liberty "${FULL_IMAGE_NAME}"
