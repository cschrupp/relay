"""Narrow GitHub REST client and standard-library HTTPS transport."""

import base64
import binascii
import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol, cast

from pydantic import SecretStr, ValidationError

from relay_engine.domain.ids import ProjectId
from relay_engine.integrations.github.errors import (
    GitHubAuthenticationError,
    GitHubInstallationUnavailable,
    GitHubObjectUnavailable,
    GitHubPermissionError,
    GitHubRateLimited,
    GitHubRefNotFound,
    GitHubRemoteError,
    GitHubRepositoryUnavailable,
)
from relay_engine.integrations.github.models import (
    GitHubAccountType,
    GitHubAppConfig,
    GitHubBlob,
    GitHubCommitObject,
    GitHubCommitResolution,
    GitHubGitObjectType,
    GitHubInstallationSnapshot,
    GitHubInstallationStatus,
    GitHubInstallationToken,
    GitHubPermissionGrant,
    GitHubPermissionLevel,
    GitHubRepositorySelectionMode,
    GitHubRepositorySnapshot,
    GitHubTree,
    GitHubTreeEntry,
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


def _required_nonnegative_int(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise GitHubRemoteError(f"GitHub {label} must be a non-negative integer")
    return value


def _required_str(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GitHubRemoteError(f"GitHub {label} must be a nonblank string")
    return value


def _required_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise GitHubRemoteError(f"GitHub {label} must be boolean")
    return value


def _required_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise GitHubRemoteError(f"GitHub {label} must be an object with string keys")
    mapping = cast(Mapping[object, object], value)
    if any(not isinstance(key, str) for key in mapping):
        raise GitHubRemoteError(f"GitHub {label} must be an object with string keys")
    return cast(Mapping[str, object], mapping)


def _required_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise GitHubRemoteError(f"GitHub {label} must be a list")
    return cast(list[object], value)


def _repository_path(full_name: str) -> str:
    parts = full_name.split("/")
    if len(parts) != 2 or any(not part for part in parts):
        raise ValueError("GitHub repository path must be owner/repository")
    owner, repository = parts
    return f"/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(repository, safe='')}"


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
        not_found: Literal["installation", "repository", "ref", "object"] | None = None,
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
                decoded = cast(object, json.loads(response.body))
                return decoded, response.headers
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise GitHubRemoteError("GitHub returned malformed JSON") from error

        request_id = response.headers.get("x-github-request-id", "unknown")
        remaining = response.headers.get("x-ratelimit-remaining")
        if response.status == 429 or (response.status == 403 and remaining == "0"):
            raise GitHubRateLimited(f"GitHub rate limited request {request_id}")
        if response.status == 401:
            raise GitHubAuthenticationError(
                f"GitHub authentication failed for request {request_id}"
            )
        if response.status == 404:
            if not_found == "installation":
                raise GitHubInstallationUnavailable(
                    f"GitHub installation is unavailable for request {request_id}"
                )
            if not_found == "repository":
                raise GitHubRepositoryUnavailable(
                    f"GitHub repository is unavailable for request {request_id}"
                )
            if not_found == "ref":
                raise GitHubRefNotFound(f"GitHub ref is unavailable for request {request_id}")
            if not_found == "object":
                raise GitHubObjectUnavailable(
                    f"GitHub object is unavailable for request {request_id}"
                )
        if response.status == 403:
            raise GitHubPermissionError(
                f"GitHub denied required permission for request {request_id}"
            )
        raise GitHubRemoteError(f"GitHub returned HTTP {response.status} for request {request_id}")

    def get_installation(
        self,
        *,
        project_id: ProjectId,
        installation_id: int,
        app_jwt: SecretStr,
        observed_at: datetime,
    ) -> GitHubInstallationSnapshot:
        raw_payload, _ = self._request(
            method="GET",
            path=f"/app/installations/{installation_id}",
            credential=app_jwt,
            not_found="installation",
        )
        payload = _required_mapping(raw_payload, "installation payload")
        try:
            provider_id = _required_int(payload.get("id"), "installation id")
            if provider_id != installation_id:
                raise GitHubRemoteError("GitHub installation response changed requested identity")
            account = _required_mapping(payload.get("account"), "installation account")
            permissions = _required_mapping(payload.get("permissions"), "installation permissions")
            grants: list[GitHubPermissionGrant] = []
            for raw_name, raw_level in sorted(permissions.items()):
                name = _required_str(raw_name, "permission name")
                level = _required_str(raw_level, "permission level")
                grants.append(GitHubPermissionGrant(name=name, level=GitHubPermissionLevel(level)))
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
                account_type=GitHubAccountType(_required_str(account.get("type"), "account type")),
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
        raw_payload, _ = self._request(
            method="POST",
            path=f"/app/installations/{installation_id}/access_tokens",
            credential=app_jwt,
            body=body,
            not_found="installation",
        )
        payload = _required_mapping(raw_payload, "installation-token payload")
        try:
            token = _required_str(payload.get("token"), "installation token")
            expires_text = _required_str(payload.get("expires_at"), "token expiration")
            expires_at = datetime.fromisoformat(expires_text.replace("Z", "+00:00"))
            return GitHubInstallationToken(token=SecretStr(token), expires_at=expires_at)
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError(
                "GitHub installation-token payload failed validation"
            ) from error

    def list_installation_repositories(
        self,
        *,
        token: GitHubInstallationToken,
        observed_at: datetime,
    ) -> tuple[GitHubRepositorySnapshot, ...]:
        repositories: dict[int, GitHubRepositorySnapshot] = {}
        page = 1
        while True:
            raw_payload, _ = self._request(
                method="GET",
                path=f"/installation/repositories?per_page=100&page={page}",
                credential=token.token,
            )
            payload = _required_mapping(raw_payload, "repository-list payload")
            page_items = _required_list(payload.get("repositories"), "repository list")
            for raw in page_items:
                repository = _required_mapping(raw, "repository payload")
                item = self._parse_repository(repository, observed_at)
                prior = repositories.get(item.github_repository_id)
                if prior is not None and prior != item:
                    raise GitHubRemoteError(
                        "GitHub pagination returned conflicting repository identity"
                    )
                repositories[item.github_repository_id] = item
            if len(page_items) < 100:
                break
            page += 1
        return tuple(repositories[key] for key in sorted(repositories))

    def get_repository(
        self,
        *,
        token: GitHubInstallationToken,
        repository_path: str,
        observed_at: datetime,
    ) -> GitHubRepositorySnapshot:
        raw_payload, _ = self._request(
            method="GET",
            path=_repository_path(repository_path),
            credential=token.token,
            not_found="repository",
        )
        return self._parse_repository(
            _required_mapping(raw_payload, "repository payload"), observed_at
        )

    def resolve_commit_sha(
        self,
        *,
        token: GitHubInstallationToken,
        repository_path: str,
        ref: str,
    ) -> GitHubCommitResolution:
        encoded_ref = urllib.parse.quote(ref, safe="")
        raw_payload, _ = self._request(
            method="GET",
            path=f"{_repository_path(repository_path)}/commits/{encoded_ref}",
            credential=token.token,
            not_found="ref",
        )
        payload = _required_mapping(raw_payload, "commit-resolution payload")
        try:
            return GitHubCommitResolution(sha=_required_str(payload.get("sha"), "commit SHA"))
        except (ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub commit-resolution payload failed validation") from error

    def get_git_commit(
        self,
        *,
        token: GitHubInstallationToken,
        repository_path: str,
        sha: str,
    ) -> GitHubCommitObject:
        raw_payload, _ = self._request(
            method="GET",
            path=f"{_repository_path(repository_path)}/git/commits/{sha}",
            credential=token.token,
            not_found="object",
        )
        payload = _required_mapping(raw_payload, "Git commit payload")
        tree = _required_mapping(payload.get("tree"), "Git commit tree")
        try:
            return GitHubCommitObject(
                sha=_required_str(payload.get("sha"), "Git commit SHA"),
                tree_sha=_required_str(tree.get("sha"), "Git root tree SHA"),
            )
        except (ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub Git commit payload failed validation") from error

    def get_git_tree(
        self,
        *,
        token: GitHubInstallationToken,
        repository_path: str,
        tree_sha: str,
    ) -> GitHubTree:
        raw_payload, _ = self._request(
            method="GET",
            path=f"{_repository_path(repository_path)}/git/trees/{tree_sha}",
            credential=token.token,
            not_found="object",
        )
        payload = _required_mapping(raw_payload, "Git tree payload")
        raw_entries = _required_list(payload.get("tree"), "Git tree entries")
        entries: list[GitHubTreeEntry] = []
        try:
            for raw in raw_entries:
                item = _required_mapping(raw, "Git tree entry")
                entries.append(
                    GitHubTreeEntry(
                        path=_required_str(item.get("path"), "Git tree path"),
                        mode=_required_str(item.get("mode"), "Git tree mode"),
                        object_type=GitHubGitObjectType(
                            _required_str(item.get("type"), "Git tree object type")
                        ),
                        sha=_required_str(item.get("sha"), "Git tree object SHA"),
                    )
                )
            return GitHubTree(
                sha=_required_str(payload.get("sha"), "Git tree SHA"),
                entries=tuple(entries),
                truncated=_required_bool(payload.get("truncated", False), "Git tree truncated"),
            )
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub Git tree payload failed validation") from error

    def get_git_blob(
        self,
        *,
        token: GitHubInstallationToken,
        repository_path: str,
        blob_sha: str,
    ) -> GitHubBlob:
        raw_payload, _ = self._request(
            method="GET",
            path=f"{_repository_path(repository_path)}/git/blobs/{blob_sha}",
            credential=token.token,
            not_found="object",
        )
        payload = _required_mapping(raw_payload, "Git blob payload")
        try:
            encoding = _required_str(payload.get("encoding"), "Git blob encoding")
            if encoding != "base64":
                raise GitHubRemoteError("GitHub Git blob encoding must be base64")
            content = _required_str(payload.get("content"), "Git blob content")
            expected_size = _required_nonnegative_int(payload.get("size"), "Git blob size")
            compact = "".join(content.split())
            try:
                raw_bytes = base64.b64decode(compact, validate=True)
            except (binascii.Error, ValueError) as error:
                raise GitHubRemoteError("GitHub Git blob content is not valid base64") from error
            if len(raw_bytes) != expected_size:
                raise GitHubRemoteError("GitHub Git blob size disagrees with decoded content")
            return GitHubBlob(
                sha=_required_str(payload.get("sha"), "Git blob SHA"), raw_bytes=raw_bytes
            )
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub Git blob payload failed validation") from error

    @staticmethod
    def _parse_repository(
        repository: Mapping[str, object], observed_at: datetime
    ) -> GitHubRepositorySnapshot:
        try:
            owner = _required_mapping(repository.get("owner"), "repository owner")
            return GitHubRepositorySnapshot(
                github_repository_id=_required_int(repository.get("id"), "repository id"),
                node_id=_required_str(repository.get("node_id"), "repository node id"),
                full_name=_required_str(repository.get("full_name"), "repository full_name"),
                owner_login=_required_str(owner.get("login"), "repository owner login"),
                private=_required_bool(repository.get("private"), "repository private"),
                archived=_required_bool(repository.get("archived", False), "repository archived"),
                default_branch=_required_str(
                    repository.get("default_branch"), "repository default branch"
                ),
                observed_at=observed_at,
            )
        except GitHubRemoteError:
            raise
        except (TypeError, ValueError, ValidationError) as error:
            raise GitHubRemoteError("GitHub repository payload failed validation") from error
