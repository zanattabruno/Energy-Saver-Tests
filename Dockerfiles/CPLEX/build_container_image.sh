#!/bin/bash

# Check if docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker is not installed. Please install Docker and try again."
    exit
fi

# Define the Docker image name and tag
IMAGE_NAME="cplex-python38"
TAG="latest"

# Define the Docker Hub username
DOCKER_HUB_USERNAME="zanattabruno"

# Build the Docker image
docker build -t ${IMAGE_NAME}:${TAG} .

# Tag the Docker image
docker tag ${IMAGE_NAME}:${TAG} ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}

# Check if user is logged in to Docker Hub
if ! docker info | grep -q Username
then
    echo "Not logged in to Docker Hub. Please login and try again."
    exit
fi

# Push the Docker image to Docker Hub
docker push ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}

echo "Docker image has been pushed to Docker Hub: ${DOCKER_HUB_USERNAME}/${IMAGE_NAME}:${TAG}"