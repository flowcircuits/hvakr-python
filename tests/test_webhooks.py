"""Tests for HVAKR webhook signature verification and event parsing."""

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import pytest

from hvakr import (
    HVAKRWebhookError,
    KnownWebhookEvent,
    ProjectCreatedEvent,
    WebhookEvent,
    construct_webhook_event,
)

SECRET = "whsec_test_abc123"


def _sign(body: str, secret: str = SECRET) -> str:
    return (
        "sha256="
        + hmac.new(secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    )


def _build_body(event: str, data: object, timestamp: str | None = None) -> str:
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    return json.dumps({"event": event, "timestamp": timestamp, "data": data})


def test_verifies_valid_signature_and_returns_event() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    event = construct_webhook_event(payload=body, signature=_sign(body), secret=SECRET)
    assert event.event == "project.created"
    assert isinstance(event, ProjectCreatedEvent)
    assert event.data.id == "proj_123"
    assert event.data.organization_id == "org_1"


def test_accepts_bytes_payload() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    event = construct_webhook_event(
        payload=body.encode("utf-8"), signature=_sign(body), secret=SECRET
    )
    assert event.event == "project.created"


def test_rejects_mutated_body() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    signature = _sign(body)
    tampered = body.replace("proj_123", "proj_456")
    with pytest.raises(HVAKRWebhookError):
        construct_webhook_event(payload=tampered, signature=signature, secret=SECRET)


def test_rejects_wrong_secret() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    with pytest.raises(HVAKRWebhookError, match="Invalid webhook signature"):
        construct_webhook_event(
            payload=body, signature=_sign(body, "whsec_wrong"), secret=SECRET
        )


def test_rejects_malformed_signature() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    with pytest.raises(HVAKRWebhookError, match="Invalid webhook signature"):
        construct_webhook_event(
            payload=body, signature="not-a-valid-signature", secret=SECRET
        )


def test_rejects_invalid_json() -> None:
    body = "{ not json"
    with pytest.raises(HVAKRWebhookError, match="not valid JSON"):
        construct_webhook_event(payload=body, signature=_sign(body), secret=SECRET)


def test_rejects_payload_missing_required_fields() -> None:
    body = json.dumps({"hello": "world"})
    with pytest.raises(HVAKRWebhookError, match="missing required fields"):
        construct_webhook_event(payload=body, signature=_sign(body), secret=SECRET)


def test_rejects_known_event_with_bad_data() -> None:
    body = _build_body("project.created", {"id": 123, "organizationId": "org_1"})
    with pytest.raises(HVAKRWebhookError, match="does not match the event schema"):
        construct_webhook_event(payload=body, signature=_sign(body), secret=SECRET)


def test_rejects_event_outside_tolerance() -> None:
    old = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
        timestamp=old,
    )
    with pytest.raises(HVAKRWebhookError, match="tolerance window"):
        construct_webhook_event(
            payload=body, signature=_sign(body), secret=SECRET, tolerance=300
        )


def test_accepts_old_event_when_tolerance_disabled() -> None:
    old = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
        timestamp=old,
    )
    event = construct_webhook_event(
        payload=body, signature=_sign(body), secret=SECRET, tolerance=0
    )
    assert event.event == "project.created"


def test_rejects_invalid_timestamp_even_with_tolerance_disabled() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
        timestamp="not-a-timestamp",
    )
    with pytest.raises(HVAKRWebhookError, match="timestamp is not a valid date"):
        construct_webhook_event(
            payload=body, signature=_sign(body), secret=SECRET, tolerance=0
        )


def test_rejects_unknown_event_types_by_default() -> None:
    body = _build_body("future.event.added.later", {"foo": "bar"})
    with pytest.raises(HVAKRWebhookError, match="Unsupported webhook event type"):
        construct_webhook_event(payload=body, signature=_sign(body), secret=SECRET)


def test_accepts_unknown_event_types_when_allowed() -> None:
    body = _build_body("future.event.added.later", {"foo": "bar"})
    event: WebhookEvent = construct_webhook_event(
        payload=body,
        signature=_sign(body),
        secret=SECRET,
        allow_unknown_events=True,
    )
    assert event.event == "future.event.added.later"
    assert event.data == {"foo": "bar"}


def test_returns_typed_event_for_known_events() -> None:
    body = _build_body(
        "project.created",
        {"id": "proj_123", "name": "Test", "organizationId": "org_1"},
    )
    event: KnownWebhookEvent = construct_webhook_event(
        payload=body, signature=_sign(body), secret=SECRET
    )
    assert isinstance(event, ProjectCreatedEvent)
    assert event.data.organization_id == "org_1"
