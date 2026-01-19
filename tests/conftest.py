"""Test configuration and fixtures."""

import os
from pathlib import Path

import pytest

# Load .env file if it exists
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


@pytest.fixture
def api_token() -> str | None:
    """Get API token from environment variable."""
    return os.environ.get("HVAKR_API_TOKEN")


@pytest.fixture
def skip_without_token(api_token: str | None) -> None:
    """Skip test if API token is not available."""
    if not api_token:
        pytest.skip("HVAKR_API_TOKEN not set")
