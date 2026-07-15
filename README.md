# HVAKR Python SDK

Official Python SDK for the [HVAKR API](https://hvakr.com) - HVAC load calculation and building analysis.

## Installation

```bash
pip install hvakr
```

## Quick Start

```python
from hvakr import HVAKRClient

# Initialize the client
client = HVAKRClient(access_token="your-access-token")

# List all projects
projects = client.list_projects()
for project in projects.projects:
    print(project.id, project.name)

# Get a specific project
project = client.get_project("project-id")
print(project.name)

# Get expanded project with all subcollections
expanded = client.get_project("project-id", expand=True)
print(expanded.spaces)
```

## Async Support

The SDK also provides an async client for use with asyncio:

```python
import asyncio
from hvakr import AsyncHVAKRClient

async def main():
    async with AsyncHVAKRClient(access_token="your-access-token") as client:
        projects = await client.list_projects()
        print(projects)

asyncio.run(main())
```

## API Reference

### HVAKRClient / AsyncHVAKRClient

Both clients provide the same methods. The async client methods are coroutines that must be awaited.

#### Constructor

```python
HVAKRClient(
    access_token: str,
    base_url: str = "https://api.hvakr.com",
    version: str = "v0",
    timeout: float = 30.0,
)
```

- `access_token`: Your HVAKR API access token
- `base_url`: API base URL (default: "https://api.hvakr.com")
- `version`: API version (default: "v0")
- `timeout`: Request timeout in seconds (default: 30.0)

### Project Methods

#### list_projects(limit=None, cursor=None, search=None, status=None, project_type=None)

List projects using the v0.6 paginated endpoint. Pass `next_cursor` as `cursor`
while `has_more` is true.

```python
page = client.list_projects(limit=50, search="office", project_type="commercial")
for project in page.projects:
    print(project.id, project.name)
```

#### get_project(project_id, expand=False)

Retrieve a project by ID.

```python
# Get basic project data
project = client.get_project("project-id")

# Get expanded project with all subcollections
expanded = client.get_project("project-id", expand=True)
```

#### create_project(project_data, idempotency_key=None)

Create a new project.

```python
result = client.create_project({
    "name": "My New Project",
    "address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060,
})
# `equipmentModes` can be omitted; the API seeds cooling_mode and heating_mode.
```

#### update_project(project_id, project_data, idempotency_key=None)

Update an existing project.

```python
result = client.update_project("project-id", {
    "name": "Updated Project Name",
})
```

#### delete_project(project_id)

Delete a project.

```python
result = client.delete_project("project-id")
```

#### get_project_calculations(project_id, include=None)

Run the calculator once and retrieve selected sections. Calculation airflows,
checksums, and equipment results are keyed by the project's equipment mode IDs.

```python
calculations = client.get_project_calculations(
    "project-id", include=["loads", "airflows", "equipment"]
)
cooling_airflows = calculations.airflows.project.by_mode["cooling_mode"]
```

### Jobs, products, and identity

```python
# Start a report, auto-group, check, or auto-takeoff job.
job = client.create_job("project-id", {"type": "check"})
job = client.get_job("project-id", job.job_id)

# Browse the product catalog and inspect the authenticated account.
products = client.list_products(search="fan")
identity = client.me()
```

### Upload a sheet PDF

Upload one PDF (maximum 30 MiB), then poll the returned `sheet-upload` job.
`file_name` remains the source-file identity; `name` is only a display name.

```python
with open("A-Plans.pdf", "rb") as pdf:
    job = client.create_sheet_file(
        "project-id",
        pdf,
        "A-Plans.pdf",
        name="Architectural Plans",
        idempotency_key="unique-upload-key",
    )

while job.status in {"queued", "running"}:
    job = client.get_job("project-id", job.job_id)

if job.type == "sheet-upload" and job.result and job.result.ready_for_takeoff:
    client.create_job("project-id", {"type": "auto-takeoff"})
```

If `ready_for_takeoff` is false, patch the project `sheets` subcollection to
place an eligible page before auto-takeoff. Auto-takeoff is project-wide, not
limited to this upload.

## v0.6 migration notes

This SDK follows the breaking HVAKR v0.6 API:

- Use `system.equipmentConfig` and `zone.equipmentConfig` instead of the legacy
  central/terminal configuration fields. Components are ordered in `components`
  and configured per mode in `componentConfigsByMode`.
- Use `project.equipmentModes` and mode keys such as `cooling_mode` rather than
  fixed cooling/heating output paths.
- Replace flat space airflow fields with `designAirflowsByMode`, and place
  ventilation/infiltration overrides under `airflowRequirementsByLoadCondition`.
- `get_project_outputs`, weather-station methods, and Revit payload options were
  removed by the platform. Use `get_project_calculations` and project jobs.


## Error Handling

The SDK raises `HVAKRClientError` for API errors:

```python
from hvakr import HVAKRClient, HVAKRClientError

client = HVAKRClient(access_token="your-token")

try:
    project = client.get_project("invalid-id")
except HVAKRClientError as e:
    print(f"Error {e.status_code}: {e.message}")
    print(f"Details: {e.metadata}")
```

## Type Hints

The SDK is fully typed and exports Pydantic models for all API responses:

```python
from hvakr import (
    HVAKRClient,
    Project,
    ExpandedProject,
)

client = HVAKRClient(access_token="your-token")

# Type hints work with IDE autocompletion
project: Project = client.get_project("project-id")
expanded: ExpandedProject = client.get_project("project-id", expand=True)
```

## Context Manager

Both clients support context manager protocol for automatic cleanup:

```python
# Sync client
with HVAKRClient(access_token="your-token") as client:
    projects = client.list_projects()

# Async client
async with AsyncHVAKRClient(access_token="your-token") as client:
    projects = await client.list_projects()
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/flowcircuits/hvakr-python.git
cd hvakr-python

# Install dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=hvakr

# Run integration tests (requires HVAKR_API_TOKEN)
# Option 1: Use a .env file (recommended)
cp .env.example .env
# Edit .env and add your HVAKR_API_TOKEN
pytest -m integration

# Option 2: Set inline
HVAKR_API_TOKEN=your-token pytest -m integration
```

### Type Checking

```bash
mypy src/hvakr
```

### Linting

```bash
ruff check src tests
ruff format src tests
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [HVAKR Website](https://hvakr.com)
- [API Documentation](https://docs.hvakr.com)
- [TypeScript SDK](https://github.com/flowcircuits/hvakr-client)
