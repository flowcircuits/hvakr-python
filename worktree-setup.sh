#!/bin/bash
# Setup script for Conductor worktrees

# Ensure we're on latest master before workspace diverges
git fetch origin master
git reset --hard origin/master

# Copy .env file from main worktree
MAIN_WORKTREE=$(git worktree list | head -1 | awk '{print $1}')
if [ -f "$MAIN_WORKTREE/.env" ]; then
    cp "$MAIN_WORKTREE/.env" .env
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
