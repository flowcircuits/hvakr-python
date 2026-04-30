"""Webhook event schema definitions."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class WebhookEventType(str, Enum):
    """Known HVAKR webhook event types."""

    OPPORTUNITY_CREATED = "opportunity.created"
    PROJECT_CREATED = "project.created"


class OpportunityCreatedPayload(BaseModel):
    """Payload for the ``opportunity.created`` webhook event."""

    id: str
    organization_domain: str | None = Field(default=None, alias="organizationDomain")
    email: str | None = None
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    company: str | None = None
    created_at: float = Field(alias="createdAt")
    updated_at: float = Field(alias="updatedAt")
    custom_fields: Any | None = Field(default=None, alias="customFields")

    model_config = {"populate_by_name": True}


class ProjectCreatedPayload(BaseModel):
    """Payload for the ``project.created`` webhook event."""

    id: str
    name: str
    organization_id: str = Field(alias="organizationId")
    address: str | None = None
    created_at: float | None = Field(default=None, alias="createdAt")

    model_config = {"populate_by_name": True}


def _validate_iso_timestamp(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Webhook timestamp must be a string")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Webhook timestamp is not a valid date") from exc
    return value


class OpportunityCreatedEvent(BaseModel):
    """An ``opportunity.created`` webhook event."""

    event: Literal["opportunity.created"]
    timestamp: str
    data: OpportunityCreatedPayload

    _validate_timestamp = field_validator("timestamp")(_validate_iso_timestamp)


class ProjectCreatedEvent(BaseModel):
    """A ``project.created`` webhook event."""

    event: Literal["project.created"]
    timestamp: str
    data: ProjectCreatedPayload

    _validate_timestamp = field_validator("timestamp")(_validate_iso_timestamp)


KnownWebhookEvent = OpportunityCreatedEvent | ProjectCreatedEvent


class UnknownWebhookEvent(BaseModel):
    """A webhook event whose ``event`` type is not recognized by this SDK."""

    event: str
    timestamp: str
    data: Any = None

    _validate_timestamp = field_validator("timestamp")(_validate_iso_timestamp)


WebhookEvent = KnownWebhookEvent | UnknownWebhookEvent
