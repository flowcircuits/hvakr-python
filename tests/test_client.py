"""Tests for HVAKRClient."""

import pytest
from pytest_httpx import HTTPXMock

from hvakr import (
    AsyncHVAKRClient,
    HVAKRClient,
    HVAKRClientError,
    Project,
    WeatherStationData,
)
from hvakr.schemas.outputs import APIProjectOutputLoads


class TestHVAKRClient:
    """Tests for synchronous HVAKRClient."""

    def test_create_url_basic(self) -> None:
        """Test URL creation without query params."""
        client = HVAKRClient(access_token="test-token")
        url = client._create_url("/projects")
        assert url == "https://api.hvakr.com/v0/projects"

    def test_create_url_with_string_params(self) -> None:
        """Test URL creation with string query params."""
        client = HVAKRClient(access_token="test-token")
        url = client._create_url("/weather-stations", {"latitude": "40.7", "longitude": "-74.0"})
        assert url == "https://api.hvakr.com/v0/weather-stations?latitude=40.7&longitude=-74.0"

    def test_create_url_with_bool_params(self) -> None:
        """Test URL creation with boolean query params."""
        client = HVAKRClient(access_token="test-token")
        url = client._create_url("/projects/123", {"expand": True})
        assert url == "https://api.hvakr.com/v0/projects/123?expand"

    def test_create_url_with_false_bool_params(self) -> None:
        """Test URL creation with false boolean query params (should be omitted)."""
        client = HVAKRClient(access_token="test-token")
        url = client._create_url("/projects/123", {"expand": False})
        assert url == "https://api.hvakr.com/v0/projects/123"

    def test_custom_base_url(self) -> None:
        """Test client with custom base URL."""
        client = HVAKRClient(access_token="test-token", base_url="https://custom.api.com")
        url = client._create_url("/projects")
        assert url == "https://custom.api.com/v0/projects"

    def test_custom_version(self) -> None:
        """Test client with custom API version."""
        client = HVAKRClient(access_token="test-token", version="v1")
        url = client._create_url("/projects")
        assert url == "https://api.hvakr.com/v1/projects"

    def test_auth_headers(self) -> None:
        """Test authentication headers."""
        client = HVAKRClient(access_token="my-secret-token")
        headers = client._get_auth_headers()
        assert headers == {"Authorization": "Bearer my-secret-token"}

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with HVAKRClient(access_token="test-token") as client:
            assert client._client is None  # Client created lazily

    def test_list_projects(self, httpx_mock: HTTPXMock) -> None:
        """Test listing projects."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            json={"ids": ["project-1", "project-2", "project-3"]},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.list_projects()

        assert result == {"ids": ["project-1", "project-2", "project-3"]}

    def test_get_project(self, httpx_mock: HTTPXMock) -> None:
        """Test getting a project."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123",
            json={
                "id": "project-123",
                "name": "Test Project",
                "users": {
                    "user-1": {"role": 10}
                },
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.get_project("project-123")

        assert isinstance(result, Project)
        assert result.id == "project-123"
        assert result.name == "Test Project"

    def test_create_project(self, httpx_mock: HTTPXMock) -> None:
        """Test creating a project."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            json={"id": "new-project-id"},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.create_project({"name": "New Project"})

        assert result == {"id": "new-project-id"}

    def test_update_project(self, httpx_mock: HTTPXMock) -> None:
        """Test updating a project."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123",
            json={"id": "project-123", "name": "Updated Project"},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.update_project("project-123", {"name": "Updated Project"})

        assert result["name"] == "Updated Project"

    def test_delete_project(self, httpx_mock: HTTPXMock) -> None:
        """Test deleting a project."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123",
            json={"deleted": True},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.delete_project("project-123")

        assert result == {"deleted": True}

    def test_search_weather_stations(self, httpx_mock: HTTPXMock) -> None:
        """Test searching weather stations."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/weather-stations?latitude=40.7128&longitude=-74.006",
            json={"weatherStationIds": ["station-1", "station-2"]},
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.search_weather_stations(40.7128, -74.006)

        assert result == {"weatherStationIds": ["station-1", "station-2"]}

    def test_get_weather_station(self, httpx_mock: HTTPXMock) -> None:
        """Test getting weather station data."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/weather-stations/station-123",
            json={
                "station": "NYC Central Park",
                "latitude": 40.7128,
                "longitude": -74.006,
                "elevation": 10.0,
                "climateZone": "4A",
                "timezoneOffset": -5,
                "averageDailyTemperature": [30, 32, 40, 50, 60, 70, 75, 74, 67, 55, 45, 35],
                "stdDevDailyTemperature": [5, 5, 6, 7, 7, 6, 5, 5, 6, 7, 6, 5],
                "dbRange": [10, 10, 12, 14, 15, 14, 13, 12, 11, 10, 10, 10],
                "wbRange": [8, 8, 9, 10, 11, 10, 9, 9, 8, 8, 8, 8],
                "hdd50": [600, 500, 300, 100, 0, 0, 0, 0, 0, 50, 200, 500],
                "hdd65": [1000, 900, 700, 400, 150, 20, 0, 0, 50, 250, 500, 900],
                "cdd50": [0, 0, 0, 0, 100, 300, 500, 450, 250, 50, 0, 0],
                "cdd65": [0, 0, 0, 0, 0, 100, 300, 250, 100, 0, 0, 0],
                "cdh74": [0, 0, 0, 0, 50, 200, 400, 350, 150, 0, 0, 0],
                "cdh80": [0, 0, 0, 0, 10, 100, 250, 200, 50, 0, 0, 0],
                "taub": [0.35, 0.36, 0.40, 0.42, 0.45, 0.47, 0.50, 0.48, 0.44, 0.40, 0.37, 0.35],
                "taud": [2.3, 2.2, 2.1, 2.0, 1.9, 1.8, 1.7, 1.8, 2.0, 2.1, 2.2, 2.3],
                "dbTempByHeatingPercent": {"99": 10, "99.6": 5},
                "monthlyBulbTempsByCoolingPercent": {
                    "0.4": {"db": [85, 86, 87], "wb": [70, 71, 72]},
                    "2": {"db": [83, 84, 85], "wb": [68, 69, 70]},
                    "5": {"db": [81, 82, 83], "wb": [66, 67, 68]},
                    "10": {"db": [79, 80, 81], "wb": [64, 65, 66]},
                },
            },
        )

        with HVAKRClient(access_token="test-token") as client:
            result = client.get_weather_station("station-123")

        assert isinstance(result, WeatherStationData)
        assert result.station == "NYC Central Park"
        assert result.latitude == 40.7128

    def test_error_response(self, httpx_mock: HTTPXMock) -> None:
        """Test error handling for failed requests."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            status_code=401,
            json={"error": "Unauthorized", "message": "Invalid token"},
        )

        with HVAKRClient(access_token="bad-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                client.list_projects()

        assert exc_info.value.status_code == 401
        assert exc_info.value.metadata == {"error": "Unauthorized", "message": "Invalid token"}


class TestAsyncHVAKRClient:
    """Tests for asynchronous AsyncHVAKRClient."""

    @pytest.mark.asyncio
    async def test_list_projects(self, httpx_mock: HTTPXMock) -> None:
        """Test listing projects asynchronously."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            json={"ids": ["project-1", "project-2"]},
        )

        async with AsyncHVAKRClient(access_token="test-token") as client:
            result = await client.list_projects()

        assert result == {"ids": ["project-1", "project-2"]}

    @pytest.mark.asyncio
    async def test_get_project(self, httpx_mock: HTTPXMock) -> None:
        """Test getting a project asynchronously."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects/project-123",
            json={
                "id": "project-123",
                "name": "Async Test Project",
                "users": {
                    "user-1": {"role": 10}
                },
            },
        )

        async with AsyncHVAKRClient(access_token="test-token") as client:
            result = await client.get_project("project-123")

        assert isinstance(result, Project)
        assert result.name == "Async Test Project"

    @pytest.mark.asyncio
    async def test_error_response(self, httpx_mock: HTTPXMock) -> None:
        """Test error handling for failed async requests."""
        httpx_mock.add_response(
            url="https://api.hvakr.com/v0/projects",
            status_code=403,
            json={"error": "Forbidden"},
        )

        async with AsyncHVAKRClient(access_token="test-token") as client:
            with pytest.raises(HVAKRClientError) as exc_info:
                await client.list_projects()

        assert exc_info.value.status_code == 403


class TestSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_project_validation(self) -> None:
        """Test Project schema validation."""
        data = {
            "id": "project-123",
            "name": "Test Project",
            "users": {
                "user-1": {"role": 10, "firstName": "John", "lastName": "Doe"}
            },
            "latitude": 40.7128,
            "longitude": -74.006,
        }
        project = Project.model_validate(data)
        assert project.id == "project-123"
        assert project.name == "Test Project"
        assert project.latitude == 40.7128

    def test_weather_station_validation(self) -> None:
        """Test WeatherStationData schema validation."""
        data = {
            "station": "Test Station",
            "latitude": 40.0,
            "longitude": -74.0,
            "elevation": 100.0,
            "climateZone": "4A",
            "timezoneOffset": -5,
            "averageDailyTemperature": [30] * 12,
            "stdDevDailyTemperature": [5] * 12,
            "dbRange": [10] * 12,
            "wbRange": [8] * 12,
            "hdd50": [500] * 12,
            "hdd65": [800] * 12,
            "cdd50": [100] * 12,
            "cdd65": [50] * 12,
            "cdh74": [200] * 12,
            "cdh80": [100] * 12,
            "taub": [0.4] * 12,
            "taud": [2.0] * 12,
            "dbTempByHeatingPercent": {"99": 10, "99.6": 5},
            "monthlyBulbTempsByCoolingPercent": {
                "0.4": {"db": [85] * 12, "wb": [70] * 12},
                "2": {"db": [83] * 12, "wb": [68] * 12},
                "5": {"db": [81] * 12, "wb": [66] * 12},
                "10": {"db": [79] * 12, "wb": [64] * 12},
            },
        }
        station = WeatherStationData.model_validate(data)
        assert station.station == "Test Station"
        assert station.climate_zone == "4A"


class TestHVAKRClientError:
    """Tests for HVAKRClientError."""

    def test_error_str(self) -> None:
        """Test error string representation."""
        error = HVAKRClientError("Something went wrong", status_code=500)
        assert str(error) == "Error 500: Something went wrong"

    def test_error_str_without_status(self) -> None:
        """Test error string without status code."""
        error = HVAKRClientError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_repr(self) -> None:
        """Test error repr."""
        error = HVAKRClientError("Error", status_code=400, metadata={"detail": "Bad request"})
        repr_str = repr(error)
        assert "HVAKRClientError" in repr_str
        assert "Error" in repr_str
        assert "400" in repr_str


# Integration tests - only run with HVAKR_API_TOKEN set
class TestIntegration:
    """Integration tests that require a real API token."""

    @pytest.mark.integration
    def test_list_projects_integration(
        self, api_token: str | None, skip_without_token: None
    ) -> None:
        """Test listing projects with real API."""
        assert api_token is not None
        with HVAKRClient(access_token=api_token) as client:
            result = client.list_projects()
            assert "ids" in result
            assert isinstance(result["ids"], list)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_projects_async_integration(
        self, api_token: str | None, skip_without_token: None
    ) -> None:
        """Test listing projects asynchronously with real API."""
        assert api_token is not None
        async with AsyncHVAKRClient(access_token=api_token) as client:
            result = await client.list_projects()
            assert "ids" in result
            assert isinstance(result["ids"], list)
