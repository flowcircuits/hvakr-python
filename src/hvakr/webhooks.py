"""HVAKR webhook signature verification and event parsing."""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Literal, overload

from pydantic import ValidationError

from hvakr.schemas.webhooks import (
    KnownWebhookEvent,
    OpportunityCreatedEvent,
    ProjectCreatedEvent,
    UnknownWebhookEvent,
    WebhookEvent,
    WebhookEventType,
)

DEFAULT_TOLERANCE_SECONDS = 300

_KNOWN_EVENT_TYPES: dict[str, type[KnownWebhookEvent]] = {
    WebhookEventType.OPPORTUNITY_CREATED.value: OpportunityCreatedEvent,
    WebhookEventType.PROJECT_CREATED.value: ProjectCreatedEvent,
}


class HVAKRWebhookError(Exception):
    """Error raised when an HVAKR webhook cannot be verified or parsed."""


def _verify_signature(payload_bytes: bytes, signature: str, secret: str) -> None:
    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"), payload_bytes, hashlib.sha256
        ).hexdigest()
    )
    if not hmac.compare_digest(expected, signature):
        raise HVAKRWebhookError("Invalid webhook signature")


def _parse_timestamp(value: str) -> float:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError as exc:
        raise HVAKRWebhookError("Webhook timestamp is not a valid date") from exc


@overload
def construct_webhook_event(
    payload: str | bytes,
    signature: str,
    secret: str,
    tolerance: float = ...,
    allow_unknown_events: Literal[False] = ...,
) -> KnownWebhookEvent: ...


@overload
def construct_webhook_event(
    payload: str | bytes,
    signature: str,
    secret: str,
    tolerance: float = ...,
    *,
    allow_unknown_events: Literal[True],
) -> WebhookEvent: ...


def construct_webhook_event(
    payload: str | bytes,
    signature: str,
    secret: str,
    tolerance: float = DEFAULT_TOLERANCE_SECONDS,
    allow_unknown_events: bool = False,
) -> WebhookEvent:
    """Verify an HVAKR webhook signature and return the parsed event.

    Args:
        payload: The raw request body, as bytes or a string. Pass the bytes
            received over the wire — re-stringifying a parsed JSON object will
            change the byte sequence and invalidate the signature.
        signature: Value of the ``X-HVAKR-Signature`` header.
        secret: Webhook signing secret from your HVAKR organization settings.
        tolerance: Maximum allowed age of the webhook timestamp, in seconds.
            Protects against replay attacks. Defaults to 300. Set to 0 to
            disable.
        allow_unknown_events: Whether to accept webhook event types that this
            SDK version does not recognize yet. Defaults to False.

    Returns:
        The parsed webhook event. When ``allow_unknown_events`` is False, the
        event is one of the known event types. When True, it may also be an
        :class:`~hvakr.schemas.webhooks.UnknownWebhookEvent`.

    Raises:
        HVAKRWebhookError: If the signature is malformed or invalid, the
            payload is not valid JSON, the event payload does not match the
            expected schema, or the timestamp is outside the tolerance window.
    """
    payload_bytes = (
        payload if isinstance(payload, bytes) else payload.encode("utf-8")
    )
    payload_string = payload_bytes.decode("utf-8")

    _verify_signature(payload_bytes, signature, secret)

    try:
        parsed = json.loads(payload_string)
    except json.JSONDecodeError as exc:
        raise HVAKRWebhookError("Webhook payload is not valid JSON") from exc

    if (
        not isinstance(parsed, dict)
        or not isinstance(parsed.get("event"), str)
        or not isinstance(parsed.get("timestamp"), str)
        or "data" not in parsed
    ):
        raise HVAKRWebhookError("Webhook payload is missing required fields")

    event_time = _parse_timestamp(parsed["timestamp"])

    event_name = parsed["event"]
    known_cls = _KNOWN_EVENT_TYPES.get(event_name)

    event: WebhookEvent
    if known_cls is not None:
        try:
            event = known_cls.model_validate(parsed)
        except ValidationError as exc:
            raise HVAKRWebhookError(
                "Webhook payload does not match the event schema"
            ) from exc
    else:
        if not allow_unknown_events:
            raise HVAKRWebhookError("Unsupported webhook event type")
        try:
            event = UnknownWebhookEvent.model_validate(parsed)
        except ValidationError as exc:
            raise HVAKRWebhookError(
                "Webhook payload is missing required fields"
            ) from exc

    if tolerance > 0:
        now = datetime.now(timezone.utc).timestamp()
        if abs(now - event_time) > tolerance:
            raise HVAKRWebhookError(
                "Webhook timestamp is outside the tolerance window"
            )

    return event


__all__ = [
    "DEFAULT_TOLERANCE_SECONDS",
    "HVAKRWebhookError",
    "construct_webhook_event",
]
