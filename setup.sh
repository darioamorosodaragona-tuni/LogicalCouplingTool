#!/bin/bash

# Ensure the etc directory exists
mkdir -p ./etc

# Copy gitconfig and .git-credentials from /etc/ on the local server to the project root's etc directory
if [ -f /etc/gitconfig ]; then
    cp /etc/gitconfig ./etc/gitconfig
    echo "Copied /etc/gitconfig to ./etc/gitconfig"
fi

if [ -f /etc/.git-credentials ]; then
    cp /etc/.git-credentials ./etc/.git-credentials
    echo "Copied /etc/.git-credentials to ./etc/.git-credentials"
fi

# Build and run docker-compose
docker compose up --build
