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
print(projects)  # {"ids": ["project-1", "project-2", ...]}

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

#### list_projects()

List all projects accessible to the authenticated user.

```python
result = client.list_projects()
# Returns: {"ids": ["project-1", "project-2", ...]}
```

#### get_project(project_id, expand=False)

Retrieve a project by ID.

```python
# Get basic project data
project = client.get_project("project-id")

# Get expanded project with all subcollections
expanded = client.get_project("project-id", expand=True)
```

#### create_project(project_data, revit_payload=False)

Create a new project.

```python
result = client.create_project({
    "name": "My New Project",
    "address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060,
})
# Returns: {"id": "new-project-id"}
```

#### update_project(project_id, project_data, revit_payload=False)

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

#### get_project_outputs(project_id, output_type)

Retrieve calculated outputs for a project.

```python
# Get heating/cooling loads
loads = client.get_project_outputs("project-id", "loads")

# Get dry side graph
graph = client.get_project_outputs("project-id", "dryside_graph")

# Get register schedule
schedule = client.get_project_outputs("project-id", "register_schedule")
```

### Weather Station Methods

#### search_weather_stations(latitude, longitude)

Search for weather stations near a geographic location.

```python
result = client.search_weather_stations(40.7128, -74.0060)
# Returns: {"weatherStationIds": ["station-1", "station-2", ...]}
```

#### get_weather_station(weather_station_id)

Retrieve detailed data for a specific weather station.

```python
station = client.get_weather_station("station-id")
print(station.station)        # Station name
print(station.climate_zone)   # Climate zone
print(station.elevation)      # Elevation
```

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
    WeatherStationData,
    APIProjectOutputLoads,
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
