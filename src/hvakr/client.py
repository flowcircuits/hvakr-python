"""HVAKR API client."""

from typing import Literal, overload

import httpx

from hvakr.exceptions import HVAKRClientError
from hvakr.schemas.outputs import (
    APIProjectOutputDrySideGraph,
    APIProjectOutputLoads,
    APIProjectOutputRegisterSchedule,
)
from hvakr.schemas.project import (
    ExpandedProject,
    ExpandedProjectPatch,
    ExpandedProjectPost,
    Project,
)
from hvakr.schemas.revit import RevitData
from hvakr.schemas.weather import WeatherStationData


class HVAKRClient:
    """Client for interacting with the HVAKR API.

    Example:
        ```python
        from hvakr import HVAKRClient

        client = HVAKRClient(access_token="your-token")
        projects = client.list_projects()
        ```
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.hvakr.com",
        version: str = "v0",
        timeout: float = 30.0,
    ) -> None:
        """Create a new HVAKR client instance.

        Args:
            access_token: Access token for authentication. Obtain from your HVAKR account settings.
            base_url: Base URL for the API. Defaults to "https://api.hvakr.com".
            version: API version to use. Defaults to "v0".
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self._access_token = access_token
        self._base_url = base_url
        self._version = version
        self._timeout = timeout
        self._client: httpx.Client | None = None

    @property
    def _http_client(self) -> httpx.Client:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout)
        return self._client

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self._access_token}"}

    def _create_url(
        self,
        path: str,
        query_params: dict[str, str | bool] | None = None,
    ) -> str:
        """Construct a full API URL with optional query parameters.

        Args:
            path: API endpoint path (e.g., "/projects").
            query_params: Optional query parameters to append.

        Returns:
            The full URL string.
        """
        url = f"{self._base_url}/{self._version}{path}"
        if query_params:
            params = []
            for key, value in query_params.items():
                if isinstance(value, bool):
                    if value:
                        params.append(key)
                elif value:
                    params.append(f"{key}={value}")
            if params:
                url += "?" + "&".join(params)
        return url

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise errors if needed.

        Args:
            response: The HTTP response.

        Returns:
            The parsed JSON response.

        Raises:
            HVAKRClientError: If the response indicates an error.
        """
        try:
            data = response.json()
        except Exception as e:
            raise HVAKRClientError(
                f"Failed to parse JSON response",
                status_code=response.status_code,
                metadata={"error": str(e)},
            ) from e

        if not response.is_success:
            raise HVAKRClientError(
                f"API request failed",
                status_code=response.status_code,
                metadata=data,
            )
        return data

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "HVAKRClient":
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()

    # Project methods

    def create_project(
        self,
        project_data: ExpandedProjectPost | RevitData | dict,
        revit_payload: bool = False,
    ) -> dict[str, str]:
        """Create a new HVAKR project.

        Args:
            project_data: The project data to create.
            revit_payload: Set to True if the data is in Revit format.

        Returns:
            A dictionary containing the ID of the newly created project.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url("/projects", {"revitPayload": revit_payload})

        if isinstance(project_data, dict):
            body = project_data
        else:
            body = project_data.model_dump(by_alias=True, exclude_none=True)

        response = self._http_client.post(
            url,
            headers={
                **self._get_auth_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=body,
        )
        return self._handle_response(response)

    def list_projects(self) -> dict[str, list[str]]:
        """List all projects accessible to the authenticated user.

        Returns:
            A dictionary containing an array of project IDs under the "ids" key.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url("/projects")
        response = self._http_client.get(url, headers=self._get_auth_headers())
        return self._handle_response(response)

    @overload
    def get_project(self, project_id: str) -> Project: ...

    @overload
    def get_project(self, project_id: str, expand: Literal[False]) -> Project: ...

    @overload
    def get_project(self, project_id: str, expand: Literal[True]) -> ExpandedProject: ...

    def get_project(
        self,
        project_id: str,
        expand: bool = False,
    ) -> Project | ExpandedProject:
        """Retrieve a project by ID.

        Args:
            project_id: The ID of the project to retrieve.
            expand: If True, returns the full expanded project data.

        Returns:
            The project data (expanded or basic depending on the expand parameter).

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url(f"/projects/{project_id}", {"expand": expand})
        response = self._http_client.get(url, headers=self._get_auth_headers())
        data = self._handle_response(response)
        if expand:
            return ExpandedProject.model_validate(data)
        return Project.model_validate(data)

    def update_project(
        self,
        project_id: str,
        project_data: ExpandedProjectPatch | RevitData | dict,
        revit_payload: bool = False,
    ) -> dict:
        """Update an existing HVAKR project.

        Args:
            project_id: The ID of the project to update.
            project_data: The updated project data.
            revit_payload: Set to True if the data is in Revit format.

        Returns:
            The updated project data.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url(f"/projects/{project_id}", {"revitPayload": revit_payload})

        if isinstance(project_data, dict):
            body = project_data
        else:
            body = project_data.model_dump(by_alias=True, exclude_none=True)

        response = self._http_client.patch(
            url,
            headers={
                **self._get_auth_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=body,
        )
        return self._handle_response(response)

    def delete_project(self, project_id: str) -> dict:
        """Delete an HVAKR project.

        Args:
            project_id: The ID of the project to delete.

        Returns:
            The deletion confirmation response.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url(f"/projects/{project_id}")
        response = self._http_client.delete(url, headers=self._get_auth_headers())
        return self._handle_response(response)

    # Project outputs

    @overload
    def get_project_outputs(
        self, project_id: str, output_type: Literal["loads"]
    ) -> APIProjectOutputLoads: ...

    @overload
    def get_project_outputs(
        self, project_id: str, output_type: Literal["dryside_graph"]
    ) -> APIProjectOutputDrySideGraph: ...

    @overload
    def get_project_outputs(
        self, project_id: str, output_type: Literal["register_schedule"]
    ) -> APIProjectOutputRegisterSchedule: ...

    def get_project_outputs(
        self,
        project_id: str,
        output_type: Literal["loads", "dryside_graph", "register_schedule"],
    ) -> APIProjectOutputLoads | APIProjectOutputDrySideGraph | APIProjectOutputRegisterSchedule:
        """Retrieve calculated outputs for a project.

        Args:
            project_id: The ID of the project.
            output_type: The type of output ("loads", "dryside_graph", or "register_schedule").

        Returns:
            The project output data for the specified type.

        Raises:
            HVAKRClientError: If the API returns an error or JSON parsing fails.
        """
        url = self._create_url(f"/projects/{project_id}/outputs/{output_type}")
        response = self._http_client.get(url, headers=self._get_auth_headers())
        data = self._handle_response(response)

        if output_type == "loads":
            return APIProjectOutputLoads.model_validate(data)
        elif output_type == "dryside_graph":
            return APIProjectOutputDrySideGraph.model_validate(data)
        else:
            return APIProjectOutputRegisterSchedule.model_validate(data)

    # Weather station methods

    def search_weather_stations(self, latitude: float, longitude: float) -> dict[str, list[str]]:
        """Search for weather stations near a geographic location.

        Args:
            latitude: The latitude coordinate.
            longitude: The longitude coordinate.

        Returns:
            A dictionary containing an array of nearby weather station IDs.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url(
            "/weather-stations",
            {"latitude": str(latitude), "longitude": str(longitude)},
        )
        response = self._http_client.get(url, headers=self._get_auth_headers())
        return self._handle_response(response)

    def get_weather_station(self, weather_station_id: str) -> WeatherStationData:
        """Retrieve detailed data for a specific weather station.

        Args:
            weather_station_id: The ID of the weather station.

        Returns:
            The weather station data including climate information.

        Raises:
            HVAKRClientError: If the API returns an error response.
        """
        url = self._create_url(f"/weather-stations/{weather_station_id}")
        response = self._http_client.get(url, headers=self._get_auth_headers())
        data = self._handle_response(response)
        return WeatherStationData.model_validate(data)


class AsyncHVAKRClient:
    """Async client for interacting with the HVAKR API.

    Example:
        ```python
        import asyncio
        from hvakr import AsyncHVAKRClient

        async def main():
            async with AsyncHVAKRClient(access_token="your-token") as client:
                projects = await client.list_projects()

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.hvakr.com",
        version: str = "v0",
        timeout: float = 30.0,
    ) -> None:
        """Create a new async HVAKR client instance.

        Args:
            access_token: Access token for authentication. Obtain from your HVAKR account settings.
            base_url: Base URL for the API. Defaults to "https://api.hvakr.com".
            version: API version to use. Defaults to "v0".
            timeout: Request timeout in seconds. Defaults to 30.0.
        """
        self._access_token = access_token
        self._base_url = base_url
        self._version = version
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def _http_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        return {"Authorization": f"Bearer {self._access_token}"}

    def _create_url(
        self,
        path: str,
        query_params: dict[str, str | bool] | None = None,
    ) -> str:
        """Construct a full API URL with optional query parameters."""
        url = f"{self._base_url}/{self._version}{path}"
        if query_params:
            params = []
            for key, value in query_params.items():
                if isinstance(value, bool):
                    if value:
                        params.append(key)
                elif value:
                    params.append(f"{key}={value}")
            if params:
                url += "?" + "&".join(params)
        return url

    async def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise errors if needed."""
        try:
            data = response.json()
        except Exception as e:
            raise HVAKRClientError(
                f"Failed to parse JSON response",
                status_code=response.status_code,
                metadata={"error": str(e)},
            ) from e

        if not response.is_success:
            raise HVAKRClientError(
                f"API request failed",
                status_code=response.status_code,
                metadata=data,
            )
        return data

    async def close(self) -> None:
        """Close the async HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncHVAKRClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()

    # Project methods

    async def create_project(
        self,
        project_data: ExpandedProjectPost | RevitData | dict,
        revit_payload: bool = False,
    ) -> dict[str, str]:
        """Create a new HVAKR project."""
        url = self._create_url("/projects", {"revitPayload": revit_payload})

        if isinstance(project_data, dict):
            body = project_data
        else:
            body = project_data.model_dump(by_alias=True, exclude_none=True)

        response = await self._http_client.post(
            url,
            headers={
                **self._get_auth_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=body,
        )
        return await self._handle_response(response)

    async def list_projects(self) -> dict[str, list[str]]:
        """List all projects accessible to the authenticated user."""
        url = self._create_url("/projects")
        response = await self._http_client.get(url, headers=self._get_auth_headers())
        return await self._handle_response(response)

    @overload
    async def get_project(self, project_id: str) -> Project: ...

    @overload
    async def get_project(self, project_id: str, expand: Literal[False]) -> Project: ...

    @overload
    async def get_project(self, project_id: str, expand: Literal[True]) -> ExpandedProject: ...

    async def get_project(
        self,
        project_id: str,
        expand: bool = False,
    ) -> Project | ExpandedProject:
        """Retrieve a project by ID."""
        url = self._create_url(f"/projects/{project_id}", {"expand": expand})
        response = await self._http_client.get(url, headers=self._get_auth_headers())
        data = await self._handle_response(response)
        if expand:
            return ExpandedProject.model_validate(data)
        return Project.model_validate(data)

    async def update_project(
        self,
        project_id: str,
        project_data: ExpandedProjectPatch | RevitData | dict,
        revit_payload: bool = False,
    ) -> dict:
        """Update an existing HVAKR project."""
        url = self._create_url(f"/projects/{project_id}", {"revitPayload": revit_payload})

        if isinstance(project_data, dict):
            body = project_data
        else:
            body = project_data.model_dump(by_alias=True, exclude_none=True)

        response = await self._http_client.patch(
            url,
            headers={
                **self._get_auth_headers(),
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json=body,
        )
        return await self._handle_response(response)

    async def delete_project(self, project_id: str) -> dict:
        """Delete an HVAKR project."""
        url = self._create_url(f"/projects/{project_id}")
        response = await self._http_client.delete(url, headers=self._get_auth_headers())
        return await self._handle_response(response)

    # Project outputs

    @overload
    async def get_project_outputs(
        self, project_id: str, output_type: Literal["loads"]
    ) -> APIProjectOutputLoads: ...

    @overload
    async def get_project_outputs(
        self, project_id: str, output_type: Literal["dryside_graph"]
    ) -> APIProjectOutputDrySideGraph: ...

    @overload
    async def get_project_outputs(
        self, project_id: str, output_type: Literal["register_schedule"]
    ) -> APIProjectOutputRegisterSchedule: ...

    async def get_project_outputs(
        self,
        project_id: str,
        output_type: Literal["loads", "dryside_graph", "register_schedule"],
    ) -> APIProjectOutputLoads | APIProjectOutputDrySideGraph | APIProjectOutputRegisterSchedule:
        """Retrieve calculated outputs for a project."""
        url = self._create_url(f"/projects/{project_id}/outputs/{output_type}")
        response = await self._http_client.get(url, headers=self._get_auth_headers())
        data = await self._handle_response(response)

        if output_type == "loads":
            return APIProjectOutputLoads.model_validate(data)
        elif output_type == "dryside_graph":
            return APIProjectOutputDrySideGraph.model_validate(data)
        else:
            return APIProjectOutputRegisterSchedule.model_validate(data)

    # Weather station methods

    async def search_weather_stations(
        self, latitude: float, longitude: float
    ) -> dict[str, list[str]]:
        """Search for weather stations near a geographic location."""
        url = self._create_url(
            "/weather-stations",
            {"latitude": str(latitude), "longitude": str(longitude)},
        )
        response = await self._http_client.get(url, headers=self._get_auth_headers())
        return await self._handle_response(response)

    async def get_weather_station(self, weather_station_id: str) -> WeatherStationData:
        """Retrieve detailed data for a specific weather station."""
        url = self._create_url(f"/weather-stations/{weather_station_id}")
        response = await self._http_client.get(url, headers=self._get_auth_headers())
        data = await self._handle_response(response)
        return WeatherStationData.model_validate(data)
