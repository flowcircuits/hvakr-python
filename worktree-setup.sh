#!/bin/bash
# Setup script for Conductor worktrees

# Ensure we're on latest master before workspace diverges
git fetch origin master
git reset --hard origin/master

# Copy .env file from parent directory
if [ -f ../.env ]; then
    cp ../.env .env
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
