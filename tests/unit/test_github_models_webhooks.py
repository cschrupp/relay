from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import SecretStr, ValidationError

from relay_engine.integrations.github import (
    GitHubAccessReadiness,
    GitHubAccountType,
    GitHubAppConfig,
    GitHubInstallationSnapshot,
    GitHubInstallationState,
    GitHubInstallationStatus,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
    GitHubWebhookInvalid,
    create_app_jwt,
    parse_supported_webhook,
    repository_ref_from_github,
    webhook_delivery_digest,
)

PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789002"
NOW = datetime(2026, 9, 27, 17, 0, tzinfo=UTC)


def _private_key() -> SecretStr:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return SecretStr(pem.decode("ascii"))


def _permissions() -> tuple[GitHubPermissionGrant, ...]:
    return (
        GitHubPermissionGrant(name="contents", level=GitHubPermissionLevel.READ),
        GitHubPermissionGrant(name="metadata", level=GitHubPermissionLevel.READ),
    )


def _snapshot() -> GitHubInstallationSnapshot:
    return GitHubInstallationSnapshot(
        project_id=PROJECT_ID,
        installation_id=1001,
        app_id=77,
        account_id=9,
        account_login="relay-test",
        account_type=GitHubAccountType.ORGANIZATION,
        repository_selection=GitHubRepositorySelectionMode.SELECTED,
        status=GitHubInstallationStatus.ACTIVE,
        permissions=_permissions(),
        observed_at=NOW,
    )


def _repository() -> GitHubRepositorySnapshot:
    return GitHubRepositorySnapshot(
        github_repository_id=501,
        node_id="R_501",
        full_name="cschrupp/relay",
        owner_login="cschrupp",
        private=False,
        archived=False,
        default_branch="main",
        observed_at=NOW,
    )


def _signed_headers(body: bytes, *, event: str, delivery: str, secret: str) -> dict[str, str]:
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return {
        "X-GitHub-Event": event,
        "X-GitHub-Delivery": delivery,
        "X-Hub-Signature-256": f"sha256={digest}",
    }


def test_github_jwt_uses_rs256_and_explicit_clock() -> None:
    private_key = _private_key()
    token = create_app_jwt(
        config=GitHubAppConfig(client_id="Iv1.test-client"),
        private_key_pem=private_key,
        now=NOW,
    )
    raw = token.get_secret_value()
    assert jwt.get_unverified_header(raw)["alg"] == "RS256"
    claims = jwt.decode(raw, options={"verify_signature": False})
    assert claims["iss"] == "Iv1.test-client"
    assert claims["iat"] == int((NOW - timedelta(seconds=60)).timestamp())
    assert claims["exp"] == int((NOW + timedelta(minutes=9)).timestamp())
    assert claims["exp"] - int(NOW.timestamp()) <= 600
    assert raw not in repr(token)
    assert private_key.get_secret_value() not in repr(private_key)


def test_installation_state_requires_active_for_ready() -> None:
    snapshot = _snapshot().model_copy(update={"status": GitHubInstallationStatus.SUSPENDED})
    with pytest.raises(ValidationError):
        GitHubInstallationState(
            installation=snapshot,
            readiness=GitHubAccessReadiness.READY,
            state_revision=1,
        )


def test_repository_ref_requires_active_ready_and_explicit_relay_id() -> None:
    repository = _repository()
    state = GitHubInstallationState(
        installation=_snapshot(),
        readiness=GitHubAccessReadiness.READY,
        state_revision=1,
    )
    value = repository_ref_from_github(
        relay_repository_id=REPOSITORY_ID,
        state=state,
        repository=repository,
        current_repositories=(repository,),
    )
    assert value.id == REPOSITORY_ID
    assert value.host == "github.com"
    assert value.path == "cschrupp/relay"

    blocked = state.model_copy(update={"readiness": GitHubAccessReadiness.RESYNC_REQUIRED})
    with pytest.raises(ValueError, match="ACTIVE / READY"):
        repository_ref_from_github(
            relay_repository_id=REPOSITORY_ID,
            state=blocked,
            repository=repository,
            current_repositories=(repository,),
        )


def test_webhook_rejects_invalid_signature_before_parse() -> None:
    headers = {
        "X-GitHub-Event": "installation",
        "X-GitHub-Delivery": "delivery-1",
        "X-Hub-Signature-256": "sha256=" + "0" * 64,
    }
    with pytest.raises(GitHubWebhookInvalid, match="signature"):
        parse_supported_webhook(
            headers=headers,
            raw_body=b"not-json",
            webhook_secret=SecretStr("secret"),
        )


def test_webhook_requires_event_and_delivery_headers() -> None:
    body = b'{"action":"suspend","installation":{"id":1001}}'
    secret = "secret"
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    with pytest.raises(GitHubWebhookInvalid, match="event and delivery"):
        parse_supported_webhook(
            headers={"X-Hub-Signature-256": f"sha256={digest}"},
            raw_body=body,
            webhook_secret=SecretStr(secret),
        )


def test_webhook_semantic_digest_is_stable_and_excludes_irrelevant_fields() -> None:
    secret = "secret"
    base = {
        "action": "removed",
        "installation": {"id": 1001},
        "repositories_removed": [{"id": 9}, {"id": 8}],
    }
    body_a = json.dumps({**base, "sender": {"login": "a"}}, separators=(",", ":")).encode()
    body_b = json.dumps({**base, "sender": {"login": "b"}}, separators=(",", ":")).encode()
    envelope_a = parse_supported_webhook(
        headers=_signed_headers(
            body_a, event="installation_repositories", delivery="d1", secret=secret
        ),
        raw_body=body_a,
        webhook_secret=SecretStr(secret),
    )
    envelope_b = parse_supported_webhook(
        headers=_signed_headers(
            body_b, event="installation_repositories", delivery="d1", secret=secret
        ),
        raw_body=body_b,
        webhook_secret=SecretStr(secret),
    )
    assert envelope_a.repository_ids == (8, 9)
    assert envelope_a == envelope_b
    assert webhook_delivery_digest(envelope_a) == webhook_delivery_digest(envelope_b)


def test_new_permissions_webhook_normalizes_sorted_permission_grants() -> None:
    secret = "secret"
    body = json.dumps(
        {
            "action": "new_permissions_accepted",
            "installation": {
                "id": 1001,
                "permissions": {"metadata": "read", "contents": "read"},
            },
        },
        separators=(",", ":"),
    ).encode()
    envelope = parse_supported_webhook(
        headers=_signed_headers(body, event="installation", delivery="d2", secret=secret),
        raw_body=body,
        webhook_secret=SecretStr(secret),
    )
    assert tuple(item.name for item in envelope.permissions) == ("contents", "metadata")
