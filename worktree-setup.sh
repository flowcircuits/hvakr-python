#!/bin/bash
# Setup script for Conductor worktrees

# Ensure we're on latest master before workspace diverges
git fetch origin master
git reset --hard origin/master

# Copy .env file from parent directory if it exists, otherwise from example
if [ -f ../.env ]; then
    cp ../.env .env
elif [ -f .env.example ] && [ ! -f .env ]; then
    cp .env.example .env
    echo 'Created .env from .env.example - please add your HVAKR_API_TOKEN'
fi

# Install Python dependencies with uv (fast) or pip as fallback
if command -v uv &> /dev/null; then
    uv venv
    uv pip install -e '.[dev]'
else
    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[dev]'
fi
