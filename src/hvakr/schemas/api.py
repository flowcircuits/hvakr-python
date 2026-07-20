"""Schemas for public HVAKR v0 API resources."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from hvakr.schemas.common import DisplayUnitSystemId
from hvakr.schemas.project import FirebaseUID, ProjectType, ProjectUserData


class ProjectListItem(BaseModel):
    """A project returned by the paginated list endpoint."""

    id: str
    name: str | None = None
    number: str | None = None
    address: str | None = None
    status: Literal["new", "inProgress", "inReview", "done", "archived"] | None = None
    project_type: ProjectType | None = Field(default=None, alias="projectType")
    timestamp: float | None = None
    last_open_time: float | None = Field(default=None, alias="lastOpenTime")
    users: dict[FirebaseUID, ProjectUserData]

    model_config = {"populate_by_name": True}


class ProjectListResponse(BaseModel):
    """A page of project summaries."""

    projects: list[ProjectListItem]
    has_more: bool = Field(alias="hasMore")
    next_cursor: str | None = Field(alias="nextCursor")

    model_config = {"populate_by_name": True}


class APIJobCreate(BaseModel):
    """Parameters for a report, auto-group, check, or auto-takeoff job."""

    type: Literal["report", "auto-group", "check", "auto-takeoff"]
    template: str | None = None
    name: str | None = None
    display_unit_system_id: DisplayUnitSystemId | None = Field(
        default=None, alias="displayUnitSystemId"
    )
    scope: Literal["spaces", "zones"] | None = None
    entity_ids: list[str] | None = Field(default=None, alias="entityIds")
    confidence: float | None = None
    levels: list[float] | None = None
    roof_type_id: str | None = Field(default=None, alias="roofTypeId")
    slab_type_id: str | None = Field(default=None, alias="slabTypeId")
    wall_type_id: str | None = Field(default=None, alias="wallTypeId")
    window_type_id: str | None = Field(default=None, alias="windowTypeId")

    model_config = {"populate_by_name": True}


class APIJob(BaseModel):
    """An asynchronous or synchronous job returned by the API."""

    job_id: str = Field(alias="jobId")
    type: Literal["report", "auto-group", "check", "auto-takeoff"]
    status: Literal["queued", "running", "completed", "failed"]
    result: dict[str, Any] | None = None
    error: str | None = None

    model_config = {"populate_by_name": True}


class APIProductFile(BaseModel):
    """A file attached to a catalog product."""

    name: str
    url: str


class APIProduct(BaseModel):
    """A product available to the authenticated organization."""

    id: str
    name: str
    manufacturer: str | None = None
    model: str | None = None
    description: str | None = None
    type: str | None = None
    price: float | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    specifications: dict[str, Any] | None = None
    files: dict[str, APIProductFile] | None = None

    model_config = {"populate_by_name": True}


class ProductListResponse(BaseModel):
    """A page of products."""

    products: list[APIProduct]
    has_more: bool = Field(alias="hasMore")
    next_cursor: str | None = Field(alias="nextCursor")

    model_config = {"populate_by_name": True}


class APIMeUser(BaseModel):
    """The authenticated API caller."""

    id: str
    email: str
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    license: Literal["enterprise", "payPerProject", "solo", "team", "university"]

    model_config = {"populate_by_name": True}


class APIMeOrganization(BaseModel):
    """An organization membership of the authenticated caller."""

    id: str
    name: str | None = None
    domain: str | None = None
    role: Literal[1, 7, 10]


class APIMePlan(BaseModel):
    """Plan entitlements for the caller."""

    license: Literal["enterprise", "payPerProject", "solo", "team", "university"]
    api_access: bool = Field(alias="apiAccess")

    model_config = {"populate_by_name": True}


class APIMeRateLimit(BaseModel):
    """Rate-limit budget for the caller."""

    limit_per_minute: float = Field(alias="limitPerMinute")

    model_config = {"populate_by_name": True}


class APIMe(BaseModel):
    """Authenticated user, organization, plan, and rate-limit information."""

    user: APIMeUser
    organizations: list[APIMeOrganization]
    plan: APIMePlan
    rate_limit: APIMeRateLimit = Field(alias="rateLimit")

    model_config = {"populate_by_name": True}
