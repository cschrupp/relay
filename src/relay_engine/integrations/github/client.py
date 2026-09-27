"""Narrow GitHub REST client and standard-library HTTPS transport."""

import json
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, cast

from pydantic import SecretStr, ValidationError

from relay_engine.domain.ids import ProjectId
from relay_engine.integrations.github.errors import (
    GitHubAuthenticationError,
    GitHubInstallationUnavailable,
    GitHubPermissionError,
    GitHubRateLimited,
    GitHubRemoteError,
)
from relay_engine.integrations.github.models import (
    GitHubAccountType,
    GitHubAppConfig,
    GitHubInstallationSnapshot,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
)


@dataclass(frozen=True, slots=True)
class GitHubRequest:
    method: str
    url: str
    headers: Mapping[str, str]
    body: bytes | None = None
    timeout_seconds: float = 10.0


@dataclass(frozen=True, slots=True)
class GitHubResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes


class GitHubTransport(Protocol):
    def request(self, request: GitHubRequest) -> GitHubResponse: ...


class UrllibGitHubTransport:
    """Minimal production HTTPS transport; policy remains in GitHubClient."""

    def request(self, request: GitHubRequest) -> GitHubResponse:
        outbound = urllib.request.Request(
            request.url,
            data=request.body,
            headers=dict(request.headers),
            method=request.method,
        )
        try:
            with urllib.request.urlopen(outbound, timeout=request.timeout_seconds) as response:
                return GitHubResponse(
                    status=int(response.status),
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=response.read(),
                )
        except urllib.error.HTTPError as error:
            return GitHubResponse(
                status=int(error.code),
                headers={key.lower(): value for key, value in error.headers.items()},
                body=error.read(),
            )
        except urllib.error.URLError as error:
            raise GitHubRemoteError("GitHub request could not reach the remote service") from error


def _required_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise GitHubRemoteError(f"GitHub {label} must be a positive integer")
    return value


def _required_str(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GitHubRemoteError(f"GitHub {label} must be a nonblank string")
    return value


def _required_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise GitHubRemoteError(f"GitHub {label} must be boolean")
    return value


class GitHubClient:
    def __init__(self, config: GitHubAppConfig, transport: GitHubTransport) -> None:
        self._config = config
        self._transport = transport

    def _headers(self, credential: SecretStr) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self._config.api_version,
            "User-Agent": self._config.user_agent,
            "Authorization": f"Bearer {credential.get_secret_value()}",
        }

    def _request(
        self,
        *,
        method: str,
        path: str,
        credential: SecretStr,
        body: object | None = None,
        not_found_installation: bool = False,
    ) -> tuple[object, Mapping[str, str]]:
        encoded: bytes | None = None
        headers = self._headers(credential)
        if body is not None:
            encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        response = self._transport.request(
            GitHubRequest(
                method=method,
                url=f"{self._config.api_base_url}{path}",
                headers=headers,
                body=encoded,
                timeout_seconds=self._config.request_timeout_seconds,
            )
        )
        if 200 <= response.status < 300:
            if not response.body:
                return {}, response.headers
            try:
                return json.loads(response.body), response.headers
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise GitHubRemoteError("GitHub returned malformed JSON") from error

        request_id = response.headers.get("x-github-request-id", "unknown")
        remaining = response.headers.get("x-ratelimit-remaining")
        if response.status == 429 or (response.status == 403 and remaining == "0"):
            raise GitHubRateLimited(f"GitHub rate limited request {request_id}")
        if response.status == 401:
            raise GitHubAuthenticationError(f"GitHub authentication failed for request {request_id}")
        if response.status == 404 and not_found_installation:
            raise GitHubInstallationUnavailable(
                f"GitHub installation is unavailable for request {request_id}"
            )
        if response.status == 403:
            raise GitHubPermissionError(f"GitHub denied required permission for request {request_id}")
        raise GitHubRemoteError(
            f"GitHub returned HTTP {response.status} for request {request_id}"
        )

    def get_installation(
        self,
        *,
        project_id: ProjectId,
        installation_id: int,
        app_jwt: SecretStr,
        observed_at: datetime,
    ) -> GitHubInstallationSnapshot:
        payload, _ = self._request(
            method="GET",
            path=f"/app/installations/{installation_id}",
            credential=app_jwt,
            not_found_installation=True,
        )
        if not isinstance(payload, dict):
            raise GitHubRemoteError("GitHub installation payload must be an object")
        try:
            provider_id = _required_int(payload.get("id"), "installation id")
            if provider_id != installation_id:
                raise GitHubRemoteError("GitHub installation response changed requested identity")
            account = payload.get("account")
            permissions = payload.get("permissions")
            if not isinstance(account, dict) or not isinstance(permissions, dict):
                raise GitHubRemoteError("GitHub installation nested payload is invalid")
            grants: list[GitHubPermissionGrant] = []
            for raw_name, raw_level in sorted(permissions.items()):
                name = _required_str(raw_name, "permission name")
                level = _required_str(raw_level, "permission level")
                grants.append(
                    GitHubPermissionGrant(name=name, level=GitHubPermissionLevel(level))
                )
            status = (
                GitHubInstallationStatus.SUSPENDED
                if payload.get("suspended_at") is not None
                else GitHubInstallationStatus.ACTIVE
            )
            return GitHubInstallationSnapshot(
                project_id=project_id,
                installation_id=provider_id,
                app_id=_required_int(payload.get("app_id"), "app id"),
                account_id=_required_int(account.get("id"), "account id"),
                account_login=_required_str(account.get("login"), "account login"),
                account_type=GitHubAccountType(
                    _required_str(account.get("type"), "account type")
                ),
                repository_selection=GitHubRepositorySelectionMode(
                    _required_str(payload.get("repository_selection"), "repository selection")
                ),
                status=status,
                permissions=tuple(grants),
                observed_at=observed_at,
            )
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub installation payload failed validation") from error

    def create_installation_token(
        self,
        *,
        installation_id: int,
        app_jwt: SecretStr,
        repository_id: int | None = None,
    ) -> GitHubInstallationToken:
        body: dict[str, object] = {"permissions": {"contents": "read"}}
        if repository_id is not None:
            if repository_id <= 0:
                raise ValueError("repository_id must be positive")
            body["repository_ids"] = [repository_id]
        payload, _ = self._request(
            method="POST",
            path=f"/app/installations/{installation_id}/access_tokens",
            credential=app_jwt,
            body=body,
            not_found_installation=True,
        )
        if not isinstance(payload, dict):
            raise GitHubRemoteError("GitHub installation-token payload must be an object")
        try:
            token = _required_str(payload.get("token"), "installation token")
            expires_text = _required_str(payload.get("expires_at"), "token expiration")
            expires_at = datetime.fromisoformat(expires_text.replace("Z", "+00:00"))
            return GitHubInstallationToken(token=SecretStr(token), expires_at=expires_at)
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub installation-token payload failed validation") from error

    def list_installation_repositories(
        self,
        *,
        token: GitHubInstallationToken,
        observed_at: datetime,
    ) -> tuple[GitHubRepositorySnapshot, ...]:
        repositories: dict[int, GitHubRepositorySnapshot] = {}
        page = 1
        while True:
            payload, _ = self._request(
                method="GET",
                path=f"/installation/repositories?per_page=100&page={page}",
                credential=token.token,
            )
            if not isinstance(payload, dict) or not isinstance(payload.get("repositories"), list):
                raise GitHubRemoteError("GitHub repository-list payload failed validation")
            page_items = cast(list[object], payload["repositories"])
            for raw in page_items:
                if not isinstance(raw, dict):
                    raise GitHubRemoteError("GitHub repository payload must be an object")
                try:
                    owner = raw.get("owner")
                    if not isinstance(owner, dict):
                        raise GitHubRemoteError("GitHub repository owner payload is invalid")
                    repository_id = _required_int(raw.get("id"), "repository id")
                    item = GitHubRepositorySnapshot(
                        github_repository_id=repository_id,
                        node_id=_required_str(raw.get("node_id"), "repository node id"),
                        full_name=_required_str(raw.get("full_name"), "repository full_name"),
                        owner_login=_required_str(owner.get("login"), "repository owner login"),
                        private=_required_bool(raw.get("private"), "repository private"),
                        archived=_required_bool(raw.get("archived", False), "repository archived"),
                        default_branch=_required_str(
                            raw.get("default_branch"), "repository default branch"
                        ),
                        observed_at=observed_at,
                    )
                except GitHubRemoteError:
                    raise
                except (TypeError, ValueError, ValidationError) as error:
                    raise GitHubRemoteError("GitHub repository payload failed validation") from error
                prior = repositories.get(item.github_repository_id)
                if prior is not None and prior != item:
                    raise GitHubRemoteError("GitHub pagination returned conflicting repository identity")
                repositories[item.github_repository_id] = item
            if len(page_items) < 100:
                break
            page += 1
        return tuple(repositories[key] for key in sorted(repositories))
