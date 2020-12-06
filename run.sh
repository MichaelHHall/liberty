#!/bin/bash
# This will hopefully build and run the liberty docker container
# Also hopefully will skip building if it has already been built
set -euo pipefail

# Ensure that the bot is not already running
docker rm --force liberty >/dev/null 2>&1 || true

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Get tag for liberty-core using commit hash
LIBERTY_CORE_NAME=libertycore
LIBERTY_CORE_TAG=$(git -C "${DIR}" rev-list --abbrev-commit -1 HEAD -- ./liberty-core-docker)

CORE_IMAGE_NAME="${LIBERTY_CORE_NAME}:${LIBERTY_CORE_TAG}"

# Image name and tag for main container
IMAGE_NAME=libertyprime
IMAGE_TAG=$(git -C "${DIR}" rev-parse --short HEAD)

FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

IMAGE_REBUILD=true
# Check various rebuild conditions
if [[ $( git status --porcelain "${DIR}/liberty-core-docker") ]]; then
    # Core dockerfile needs to be rebuilt
    LIBERTY_CORE_TAG=dirty
    CORE_IMAGE_NAME="${LIBERTY_CORE_NAME}:${LIBERTY_CORE_TAG}"
    IMAGE_TAG=dirty
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
elif [[ $(git -C "${DIR}" diff --stat) != '' ]]; then
    # Main repo is dirty, but core dockerfile is clean
    IMAGE_TAG=dirty
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
elif docker inspect --type=image "${FULL_IMAGE_NAME}" >/dev/null 2>&1; then
    # Neither the core folder or the repo is dirty, and we have an image for this commit
    IMAGE_REBUILD=false
fi

if [[ $IMAGE_REBUILD == true ]]; then
    if ! docker inspect --type=image "${CORE_IMAGE_NAME}" >/dev/null 2>&1 \
      || [[ $LIBERTY_CORE_TAG == dirty ]]; then
        # Rebuild core image
        docker build -t "${CORE_IMAGE_NAME}" "${DIR}/liberty-core-docker"
    fi
    #Export core tag as some kind of env var?
    docker build --build-arg liberty_core_tag=$LIBERTY_CORE_TAG -t "${FULL_IMAGE_NAME}" "${DIR}"
fi

# If I were smart I would check for dirty git first, since this could build
# a container using uncommitted code but tag it as non-dirty
# But I guess I don't really care right now
#if ! docker inspect --type=image "${FULL_IMAGE_NAME}" >/dev/null 2>&1; then
#    # Need to rebuild. Also prune old images (older than 10 days).
#    docker image prune -a -f --filter "until=240h"
#    docker build -t "${FULL_IMAGE_NAME}" "${DIR}"
#else
#    # Check if git is dirty, if so rebuild
#    if [[ $(git -C "${DIR}" diff --stat) != '' ]]; then
#        docker image prune -a -f --filter "until=240h"
#        FULL_IMAGE_NAME="${IMAGE_NAME}:dirty"
#        docker build -t "${FULL_IMAGE_NAME}" "${DIR}"
#    fi
#fi

# Run image
docker run --detach --name liberty "${FULL_IMAGE_NAME}"
