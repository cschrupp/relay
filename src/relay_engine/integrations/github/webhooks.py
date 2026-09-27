"""Signed GitHub App webhook verification and semantic normalization."""

import hashlib
import hmac
import json
from collections.abc import Mapping
from typing import cast

from pydantic import SecretStr, ValidationError

from relay_engine.integrations.github.errors import GitHubWebhookInvalid
from relay_engine.integrations.github.models import (
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubWebhookEnvelope,
)

_INSTALLATION_ACTIONS = frozenset(
    {"created", "new_permissions_accepted", "suspend", "unsuspend", "deleted"}
)
_REPOSITORY_ACTIONS = frozenset({"added", "removed"})


def _header(headers: Mapping[str, str], name: str) -> str | None:
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def verify_webhook_signature(
    *,
    headers: Mapping[str, str],
    raw_body: bytes,
    webhook_secret: SecretStr,
) -> None:
    """Verify X-Hub-Signature-256 before any body parsing."""

    supplied = _header(headers, "X-Hub-Signature-256")
    if supplied is None or not supplied.startswith("sha256="):
        raise GitHubWebhookInvalid("missing or invalid webhook signature")
    expected = "sha256=" + hmac.new(
        webhook_secret.get_secret_value().encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(supplied, expected):
        raise GitHubWebhookInvalid("webhook signature verification failed")


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise GitHubWebhookInvalid(f"{label} must be a positive integer")
    return value


def _permissions(value: object) -> tuple[GitHubPermissionGrant, ...]:
    if value is None:
        return ()
    if not isinstance(value, dict):
        raise GitHubWebhookInvalid("installation permissions must be an object")
    grants: list[GitHubPermissionGrant] = []
    try:
        for name, level in sorted(value.items()):
            if not isinstance(name, str) or not isinstance(level, str):
                raise GitHubWebhookInvalid("installation permission entries must be strings")
            grants.append(
                GitHubPermissionGrant(name=name, level=GitHubPermissionLevel(level.lower()))
            )
    except (ValueError, ValidationError) as error:
        raise GitHubWebhookInvalid("installation permissions are invalid") from error
    return tuple(grants)


def _repository_ids(value: object) -> tuple[int, ...]:
    if not isinstance(value, list):
        raise GitHubWebhookInvalid("repository change payload must be a list")
    ids: list[int] = []
    for item in value:
        if not isinstance(item, dict):
            raise GitHubWebhookInvalid("repository change entry must be an object")
        ids.append(_positive_int(item.get("id"), "repository id"))
    return tuple(sorted(set(ids)))


def parse_supported_webhook(
    *,
    headers: Mapping[str, str],
    raw_body: bytes,
    webhook_secret: SecretStr,
) -> GitHubWebhookEnvelope:
    """Verify, parse, and normalize one supported GitHub installation webhook."""

    event_name = _header(headers, "X-GitHub-Event")
    delivery_id = _header(headers, "X-GitHub-Delivery")
    if not event_name or not delivery_id:
        raise GitHubWebhookInvalid("supported webhook requires event and delivery headers")

    verify_webhook_signature(headers=headers, raw_body=raw_body, webhook_secret=webhook_secret)

    try:
        payload = json.loads(raw_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GitHubWebhookInvalid("webhook body is not valid JSON") from error
    if not isinstance(payload, dict):
        raise GitHubWebhookInvalid("webhook body must be a JSON object")

    action = payload.get("action")
    if not isinstance(action, str) or not action:
        raise GitHubWebhookInvalid("webhook action is missing")
    installation = payload.get("installation")
    if not isinstance(installation, dict):
        raise GitHubWebhookInvalid("webhook installation object is missing")
    installation_id = _positive_int(installation.get("id"), "installation id")

    permissions: tuple[GitHubPermissionGrant, ...] = ()
    repository_ids: tuple[int, ...] = ()
    if event_name == "installation":
        if action not in _INSTALLATION_ACTIONS:
            raise GitHubWebhookInvalid("unsupported installation webhook action")
        if action == "new_permissions_accepted":
            permissions = _permissions(installation.get("permissions"))
    elif event_name == "installation_repositories":
        if action not in _REPOSITORY_ACTIONS:
            raise GitHubWebhookInvalid("unsupported installation_repositories action")
        key = "repositories_added" if action == "added" else "repositories_removed"
        repository_ids = _repository_ids(payload.get(key))
    else:
        raise GitHubWebhookInvalid("unsupported GitHub webhook event")

    try:
        return GitHubWebhookEnvelope(
            event_name=event_name,
            delivery_id=delivery_id,
            action=action,
            installation_id=installation_id,
            repository_ids=repository_ids,
            permissions=permissions,
        )
    except ValidationError as error:
        raise GitHubWebhookInvalid("webhook semantic envelope is invalid") from error


def webhook_delivery_digest(envelope: GitHubWebhookEnvelope) -> str:
    """Fingerprint only the validated semantic provider event."""

    encoded = json.dumps(
        cast(object, envelope.model_dump(mode="json")),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"
