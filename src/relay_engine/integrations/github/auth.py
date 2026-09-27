"""Ephemeral GitHub App authentication helpers."""

from datetime import UTC, datetime, timedelta

import jwt
from pydantic import SecretStr

from relay_engine.integrations.github.models import GitHubAppConfig


def create_app_jwt(
    *,
    config: GitHubAppConfig,
    private_key_pem: SecretStr,
    now: datetime,
) -> SecretStr:
    """Create a short-lived RS256 GitHub App JWT from an explicit clock."""

    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    current = now.astimezone(UTC)
    issued_at = current - timedelta(seconds=60)
    expires_at = current + timedelta(minutes=9)
    token = jwt.encode(
        {
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "iss": config.client_id,
        },
        private_key_pem.get_secret_value(),
        algorithm="RS256",
    )
    return SecretStr(token)
