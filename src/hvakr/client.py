"""Synchronous and asynchronous clients for the HVAKR v0 API."""

import logging
from collections.abc import Mapping, Sequence
from typing import Any, Literal, overload
from urllib.parse import quote

import httpx
from pydantic import BaseModel

from hvakr.exceptions import HVAKRClientError
from hvakr.schemas.api import (
    APIJob,
    APIJobCreate,
    APIMe,
    APIProduct,
    ProductListResponse,
    ProjectListResponse,
)
from hvakr.schemas.outputs import APIProjectCalculations
from hvakr.schemas.project import (
    ExpandedProject,
    ExpandedProjectPatch,
    ExpandedProjectPost,
    Project,
    ProjectPost,
)

__version__ = "1.0.0"
_LOGGER = logging.getLogger(__name__)
_WARNED_CLIENT_MESSAGES: set[str] = set()
_ProjectSubcollectionKey = Literal[
    "branchTypes",
    "deadlines",
    "doorTypes",
    "ductTypes",
    "graph",
    "pipeTypes",
    "registerTypes",
    "roofTypes",
    "sheetFiles",
    "sheets",
    "slabTypes",
    "spaceTypes",
    "spaces",
    "systems",
    "wallTypes",
    "windowTypes",
    "zones",
    "reports",
]
_CalculationSection = Literal[
    "loads",
    "register_schedule",
    "dryside_graph",
    "ventilation",
    "equipment",
    "checksums",
    "airflows",
]
_ProjectPayload = ExpandedProjectPost | ProjectPost | ExpandedProjectPatch | Mapping[str, Any]
_JobPayload = APIJobCreate | Mapping[str, Any]
_QueryValue = str | int | float | bool


class _ClientBase:
    """Shared URL, header, payload, and response handling."""

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.hvakr.com",
        version: str = "v0",
        timeout: float = 30.0,
    ) -> None:
        self._access_token = access_token
        self._base_url = base_url
        self._version = version
        self._timeout = timeout

    def _get_auth_headers(self) -> dict[str, str]:
        """Build headers sent with every request."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "X-HVAKR-Client": f"hvakr-python/{__version__}",
        }

    @staticmethod
    def _encode_path_segment(segment: str) -> str:
        return quote(segment, safe="")

    def _create_url(self, path: str, query_params: Mapping[str, _QueryValue] | None = None) -> str:
        """Construct an API URL, encoding paths and query values safely."""
        url = f"{self._base_url.rstrip('/')}/{self._version}{path}"
        if not query_params:
            return url

        params: list[str] = []
        for key, value in query_params.items():
            if isinstance(value, bool):
                if value:
                    params.append(quote(key, safe=""))
            elif value is not None:
                params.append(f"{quote(key, safe='')}={quote(str(value), safe='')}")
        return f"{url}?{'&'.join(params)}" if params else url

    def _write_headers(self, idempotency_key: str | None = None) -> dict[str, str]:
        headers = {
            **self._get_auth_headers(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    @staticmethod
    def _payload(data: BaseModel | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(data, BaseModel):
            return data.model_dump(by_alias=True, exclude_none=True)
        return dict(data)

    @staticmethod
    def _warn_if_outdated(response: httpx.Response) -> None:
        warning = response.headers.get("X-HVAKR-Client-Warning")
        if warning and warning not in _WARNED_CLIENT_MESSAGES:
            _WARNED_CLIENT_MESSAGES.add(warning)
            _LOGGER.warning("[hvakr] %s", warning)

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        self._warn_if_outdated(response)
        try:
            data = response.json()
        except (ValueError, TypeError) as exc:
            raise HVAKRClientError(
                "Failed to parse JSON response",
                status_code=response.status_code,
                metadata={"error": str(exc)},
            ) from exc

        if not response.is_success:
            raise HVAKRClientError(
                f"Error {response.status_code}",
                status_code=response.status_code,
                metadata=data,
            )
        if not isinstance(data, dict):
            raise HVAKRClientError(
                "Expected an object JSON response",
                status_code=response.status_code,
                metadata=data,
            )
        return data

    @staticmethod
    def _list_params(
        *,
        limit: int | None = None,
        cursor: str | None = None,
        search: str | None = None,
        status: str | None = None,
        project_type: str | None = None,
    ) -> dict[str, _QueryValue]:
        return {
            key: value
            for key, value in {
                "limit": limit,
                "cursor": cursor,
                "search": search,
                "status": status,
                "projectType": project_type,
            }.items()
            if value is not None
        }


class HVAKRClient(_ClientBase):
    """Synchronous client for the HVAKR v0 API."""

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.hvakr.com",
        version: str = "v0",
        timeout: float = 30.0,
    ) -> None:
        super().__init__(access_token, base_url, version, timeout)
        self._client: httpx.Client | None = None

    @property
    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self._timeout)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> "HVAKRClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def list_projects(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        search: str | None = None,
        status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None,
        project_type: Literal["residential", "commercial"] | None = None,
    ) -> ProjectListResponse:
        """Return a paginated page of project summaries."""
        response = self._http_client.get(
            self._create_url(
                "/projects",
                self._list_params(
                    limit=limit,
                    cursor=cursor,
                    search=search,
                    status=status,
                    project_type=project_type,
                ),
            ),
            headers=self._get_auth_headers(),
        )
        return ProjectListResponse.model_validate(self._handle_response(response))

    @overload
    def get_project(self, project_id: str) -> Project: ...

    @overload
    def get_project(self, project_id: str, expand: Literal[False]) -> Project: ...

    @overload
    def get_project(self, project_id: str, expand: Literal[True]) -> ExpandedProject: ...

    @overload
    def get_project(
        self, project_id: str, expand: Sequence[_ProjectSubcollectionKey]
    ) -> ExpandedProject: ...

    def get_project(
        self, project_id: str, expand: bool | Sequence[_ProjectSubcollectionKey] = False
    ) -> Project | ExpandedProject:
        """Get a project; ``expand`` can select all or specific subcollections."""
        expand_value: str | bool
        if isinstance(expand, Sequence) and not isinstance(expand, (str, bytes)):
            expand_value = ",".join(expand)
        else:
            expand_value = bool(expand)
        response = self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}", {"expand": expand_value}
            ),
            headers=self._get_auth_headers(),
        )
        data = self._handle_response(response)
        if expand_value:
            return ExpandedProject.model_validate(data)
        return Project.model_validate(data)

    def create_project(
        self, project_data: _ProjectPayload, *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        """Create a project. Omit ``equipmentModes`` to receive the default modes."""
        response = self._http_client.post(
            self._create_url("/projects"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(project_data),
        )
        return self._handle_response(response)

    def update_project(
        self,
        project_id: str,
        project_data: _ProjectPayload,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Patch a project with canonical v0 fields and subcollections."""
        response = self._http_client.patch(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(project_data),
        )
        return self._handle_response(response)

    def delete_project(self, project_id: str) -> dict[str, Any]:
        response = self._http_client.delete(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}"),
            headers=self._get_auth_headers(),
        )
        return self._handle_response(response)

    def get_project_calculations(
        self, project_id: str, *, include: Sequence[_CalculationSection] | None = None
    ) -> APIProjectCalculations:
        """Run the calculator once and return all requested calculation sections."""
        query = {"include": ",".join(include)} if include else None
        response = self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}/calculations", query
            ),
            headers=self._get_auth_headers(),
        )
        return APIProjectCalculations.model_validate(self._handle_response(response))

    def create_job(
        self,
        project_id: str,
        body: _JobPayload,
        *,
        idempotency_key: str | None = None,
    ) -> APIJob:
        response = self._http_client.post(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}/jobs"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(body),
        )
        return APIJob.model_validate(self._handle_response(response))

    def get_job(self, project_id: str, job_id: str) -> APIJob:
        response = self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}/jobs/"
                f"{self._encode_path_segment(job_id)}"
            ),
            headers=self._get_auth_headers(),
        )
        return APIJob.model_validate(self._handle_response(response))

    def list_products(
        self, *, search: str | None = None, limit: int | None = None, cursor: str | None = None
    ) -> ProductListResponse:
        query_params = {
            key: value
            for key, value in {"search": search, "limit": limit, "cursor": cursor}.items()
            if value is not None
        }
        response = self._http_client.get(
            self._create_url("/products", query_params),
            headers=self._get_auth_headers(),
        )
        return ProductListResponse.model_validate(self._handle_response(response))

    def get_product(self, product_id: str) -> APIProduct:
        response = self._http_client.get(
            self._create_url(f"/products/{self._encode_path_segment(product_id)}"),
            headers=self._get_auth_headers(),
        )
        return APIProduct.model_validate(self._handle_response(response))

    def me(self) -> APIMe:
        response = self._http_client.get(self._create_url("/me"), headers=self._get_auth_headers())
        return APIMe.model_validate(self._handle_response(response))


class AsyncHVAKRClient(_ClientBase):
    """Asynchronous client for the HVAKR v0 API."""

    def __init__(
        self,
        access_token: str,
        base_url: str = "https://api.hvakr.com",
        version: str = "v0",
        timeout: float = 30.0,
    ) -> None:
        super().__init__(access_token, base_url, version, timeout)
        self._client: httpx.AsyncClient | None = None

    @property
    def _http_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "AsyncHVAKRClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def list_projects(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        search: str | None = None,
        status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None,
        project_type: Literal["residential", "commercial"] | None = None,
    ) -> ProjectListResponse:
        response = await self._http_client.get(
            self._create_url(
                "/projects",
                self._list_params(
                    limit=limit,
                    cursor=cursor,
                    search=search,
                    status=status,
                    project_type=project_type,
                ),
            ),
            headers=self._get_auth_headers(),
        )
        return ProjectListResponse.model_validate(self._handle_response(response))

    @overload
    async def get_project(self, project_id: str) -> Project: ...

    @overload
    async def get_project(self, project_id: str, expand: Literal[False]) -> Project: ...

    @overload
    async def get_project(self, project_id: str, expand: Literal[True]) -> ExpandedProject: ...

    @overload
    async def get_project(
        self, project_id: str, expand: Sequence[_ProjectSubcollectionKey]
    ) -> ExpandedProject: ...

    async def get_project(
        self, project_id: str, expand: bool | Sequence[_ProjectSubcollectionKey] = False
    ) -> Project | ExpandedProject:
        expand_value: str | bool
        if isinstance(expand, Sequence) and not isinstance(expand, (str, bytes)):
            expand_value = ",".join(expand)
        else:
            expand_value = bool(expand)
        response = await self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}", {"expand": expand_value}
            ),
            headers=self._get_auth_headers(),
        )
        data = self._handle_response(response)
        if expand_value:
            return ExpandedProject.model_validate(data)
        return Project.model_validate(data)

    async def create_project(
        self, project_data: _ProjectPayload, *, idempotency_key: str | None = None
    ) -> dict[str, Any]:
        response = await self._http_client.post(
            self._create_url("/projects"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(project_data),
        )
        return self._handle_response(response)

    async def update_project(
        self,
        project_id: str,
        project_data: _ProjectPayload,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        response = await self._http_client.patch(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(project_data),
        )
        return self._handle_response(response)

    async def delete_project(self, project_id: str) -> dict[str, Any]:
        response = await self._http_client.delete(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}"),
            headers=self._get_auth_headers(),
        )
        return self._handle_response(response)

    async def get_project_calculations(
        self, project_id: str, *, include: Sequence[_CalculationSection] | None = None
    ) -> APIProjectCalculations:
        query = {"include": ",".join(include)} if include else None
        response = await self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}/calculations", query
            ),
            headers=self._get_auth_headers(),
        )
        return APIProjectCalculations.model_validate(self._handle_response(response))

    async def create_job(
        self,
        project_id: str,
        body: _JobPayload,
        *,
        idempotency_key: str | None = None,
    ) -> APIJob:
        response = await self._http_client.post(
            self._create_url(f"/projects/{self._encode_path_segment(project_id)}/jobs"),
            headers=self._write_headers(idempotency_key),
            json=self._payload(body),
        )
        return APIJob.model_validate(self._handle_response(response))

    async def get_job(self, project_id: str, job_id: str) -> APIJob:
        response = await self._http_client.get(
            self._create_url(
                f"/projects/{self._encode_path_segment(project_id)}/jobs/"
                f"{self._encode_path_segment(job_id)}"
            ),
            headers=self._get_auth_headers(),
        )
        return APIJob.model_validate(self._handle_response(response))

    async def list_products(
        self, *, search: str | None = None, limit: int | None = None, cursor: str | None = None
    ) -> ProductListResponse:
        query_params = {
            key: value
            for key, value in {"search": search, "limit": limit, "cursor": cursor}.items()
            if value is not None
        }
        response = await self._http_client.get(
            self._create_url("/products", query_params),
            headers=self._get_auth_headers(),
        )
        return ProductListResponse.model_validate(self._handle_response(response))

    async def get_product(self, product_id: str) -> APIProduct:
        response = await self._http_client.get(
            self._create_url(f"/products/{self._encode_path_segment(product_id)}"),
            headers=self._get_auth_headers(),
        )
        return APIProduct.model_validate(self._handle_response(response))

    async def me(self) -> APIMe:
        response = await self._http_client.get(
            self._create_url("/me"), headers=self._get_auth_headers()
        )
        return APIMe.model_validate(self._handle_response(response))
