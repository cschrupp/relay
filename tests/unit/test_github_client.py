from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr

from relay_engine.integrations.github import (
    GitHubAppConfig,
    GitHubAuthenticationError,
    GitHubClient,
    GitHubGitObjectType,
    GitHubInstallationToken,
    GitHubPermissionError,
    GitHubRateLimited,
    GitHubRefUpdateIndeterminate,
    GitHubRefUpdateRejected,
    GitHubRemoteError,
    GitHubRequest,
    GitHubResponse,
    GitHubTreeEntry,
)

PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"
NOW = datetime(2026, 9, 27, 17, 0, tzinfo=UTC)


class FakeTransport:
    def __init__(self, responses: list[GitHubResponse]):
        self.responses = responses
        self.requests: list[GitHubRequest] = []

    def request(self, request: GitHubRequest) -> GitHubResponse:
        self.requests.append(request)
        return self.responses.pop(0)


def _response(status: int, payload: object, headers=None) -> GitHubResponse:
    return GitHubResponse(
        status=status,
        headers={} if headers is None else headers,
        body=json.dumps(payload, separators=(",", ":")).encode(),
    )


def test_client_sends_required_version_user_agent_and_bearer_headers() -> None:
    transport = FakeTransport(
        [
            _response(
                200,
                {
                    "id": 1001,
                    "app_id": 77,
                    "account": {"id": 9, "login": "relay-test", "type": "Organization"},
                    "repository_selection": "selected",
                    "permissions": {"contents": "read", "metadata": "read"},
                    "suspended_at": None,
                },
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    client.get_installation(
        project_id=PROJECT_ID,
        installation_id=1001,
        app_jwt=SecretStr("jwt-secret-value"),
        observed_at=NOW,
    )
    request = transport.requests[0]
    assert request.headers["Accept"] == "application/vnd.github+json"
    assert request.headers["X-GitHub-Api-Version"] == "2026-03-10"
    assert request.headers["User-Agent"] == "relay-engine"
    assert request.headers["Authorization"] == "Bearer jwt-secret-value"


def test_client_error_text_does_not_expose_bearer_token() -> None:
    transport = FakeTransport([_response(401, {"message": "bad credentials"})])
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    with pytest.raises(GitHubAuthenticationError) as captured:
        client.get_installation(
            project_id=PROJECT_ID,
            installation_id=1001,
            app_jwt=SecretStr("super-secret-jwt"),
            observed_at=NOW,
        )
    assert "super-secret-jwt" not in str(captured.value)


def test_client_403_rate_limit_precedes_permission_classification() -> None:
    transport = FakeTransport(
        [_response(403, {"message": "rate limited"}, {"x-ratelimit-remaining": "0"})]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    with pytest.raises(GitHubRateLimited):
        client.get_installation(
            project_id=PROJECT_ID,
            installation_id=1001,
            app_jwt=SecretStr("jwt"),
            observed_at=NOW,
        )


def test_client_ordinary_403_is_permission_error() -> None:
    transport = FakeTransport([_response(403, {"message": "forbidden"})])
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    with pytest.raises(GitHubPermissionError):
        client.get_installation(
            project_id=PROJECT_ID,
            installation_id=1001,
            app_jwt=SecretStr("jwt"),
            observed_at=NOW,
        )


def test_installation_token_request_scopes_selected_repository_and_read_only_permission() -> None:
    transport = FakeTransport(
        [
            _response(
                201,
                {
                    "token": "installation-token",
                    "expires_at": (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
                },
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    client.create_installation_token(
        installation_id=1001,
        app_jwt=SecretStr("jwt"),
        repository_id=501,
    )
    request = transport.requests[0]
    assert request.body is not None
    body = json.loads(request.body)
    assert body == {"permissions": {"contents": "read"}, "repository_ids": [501]}


def test_installation_token_can_request_only_selected_repository_write_contents() -> None:
    transport = FakeTransport(
        [
            _response(
                201,
                {
                    "token": "installation-token",
                    "expires_at": (NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
                },
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    client.create_installation_token(
        installation_id=1001,
        app_jwt=SecretStr("jwt"),
        repository_id=501,
        contents_permission="write",
    )
    body = json.loads(transport.requests[0].body or b"{}")
    assert body == {"permissions": {"contents": "write"}, "repository_ids": [501]}


def test_git_data_write_calls_create_blobs_tree_commit_and_move_ref_nonforce() -> None:
    token = GitHubInstallationToken(
        token=SecretStr("installation-token"),
        expires_at=NOW + timedelta(hours=1),
    )
    transport = FakeTransport(
        [
            _response(201, {"sha": "a" * 40}),
            _response(201, {"sha": "b" * 40}),
            _response(
                201,
                {
                    "sha": "c" * 40,
                    "tree": {"sha": "d" * 40},
                    "parents": [{"sha": "e" * 40}],
                },
            ),
            _response(
                200,
                {
                    "ref": "refs/heads/main",
                    "object": {"sha": "c" * 40, "type": "commit"},
                },
            ),
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    blob = client.create_git_blob(
        token=token, repository_path="cschrupp/relay", raw_bytes=b"document\n"
    )
    tree = client.create_git_tree(
        token=token,
        repository_path="cschrupp/relay",
        base_tree_sha="f" * 40,
        entries=(
            GitHubTreeEntry(
                path="docs/example.md",
                mode="100644",
                object_type=GitHubGitObjectType.BLOB,
                sha=blob.sha,
            ),
        ),
    )
    commit = client.create_git_commit(
        token=token,
        repository_path="cschrupp/relay",
        message="Relay sync",
        tree_sha=tree.sha,
        parent_sha="e" * 40,
    )
    ref = client.update_git_ref(
        token=token,
        repository_path="cschrupp/relay",
        branch="main",
        commit_sha=commit.sha,
        force=False,
    )
    assert commit.parents == ("e" * 40,)
    assert ref.sha == commit.sha
    assert [request.method for request in transport.requests] == ["POST"] * 3 + ["PATCH"]
    assert json.loads(transport.requests[-1].body or b"{}") == {
        "force": False,
        "sha": commit.sha,
    }


def test_ref_update_distinguishes_rejection_from_indeterminate_response() -> None:
    token = GitHubInstallationToken(
        token=SecretStr("installation-token"),
        expires_at=NOW + timedelta(hours=1),
    )
    rejected = GitHubClient(
        GitHubAppConfig(client_id="Iv1.test"),
        FakeTransport([_response(422, {"message": "protected"})]),
    )
    with pytest.raises(GitHubRefUpdateRejected):
        rejected.update_git_ref(
            token=token,
            repository_path="cschrupp/relay",
            branch="main",
            commit_sha="a" * 40,
        )

    malformed = GitHubClient(
        GitHubAppConfig(client_id="Iv1.test"), FakeTransport([_response(200, {"ref": "bad"})])
    )
    with pytest.raises(GitHubRefUpdateIndeterminate):
        malformed.update_git_ref(
            token=token,
            repository_path="cschrupp/relay",
            branch="main",
            commit_sha="a" * 40,
        )

    failed_after_processing = GitHubClient(
        GitHubAppConfig(client_id="Iv1.test"),
        FakeTransport([_response(500, {"message": "server error"})]),
    )
    with pytest.raises(GitHubRefUpdateIndeterminate):
        failed_after_processing.update_git_ref(
            token=token,
            repository_path="cschrupp/relay",
            branch="main",
            commit_sha="a" * 40,
        )


def test_repository_listing_paginates_before_returning_complete_sorted_set() -> None:
    first_page = []
    for repository_id in range(100, 200):
        first_page.append(
            {
                "id": repository_id,
                "node_id": f"R_{repository_id}",
                "full_name": f"owner/repo-{repository_id}",
                "owner": {"login": "owner"},
                "private": False,
                "archived": False,
                "default_branch": "main",
            }
        )
    second_page = [
        {
            "id": 99,
            "node_id": "R_99",
            "full_name": "owner/repo-99",
            "owner": {"login": "owner"},
            "private": False,
            "archived": False,
            "default_branch": "main",
        }
    ]
    transport = FakeTransport(
        [
            _response(200, {"repositories": first_page}),
            _response(200, {"repositories": second_page}),
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    repositories = client.list_installation_repositories(
        token=type(
            "Token",
            (),
            {"token": SecretStr("token"), "expires_at": NOW + timedelta(hours=1)},
        )(),
        observed_at=NOW,
    )
    assert len(repositories) == 101
    assert repositories[0].github_repository_id == 99
    assert repositories[-1].github_repository_id == 199
    assert len(transport.requests) == 2


def test_repository_provider_types_are_validated_not_truthy_coerced() -> None:
    transport = FakeTransport(
        [
            _response(
                200,
                {
                    "repositories": [
                        {
                            "id": 501,
                            "node_id": "R_501",
                            "full_name": "owner/repo",
                            "owner": {"login": "owner"},
                            "private": "false",
                            "archived": False,
                            "default_branch": "main",
                        }
                    ]
                },
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    token = type(
        "Token",
        (),
        {"token": SecretStr("token"), "expires_at": NOW + timedelta(hours=1)},
    )()
    with pytest.raises(GitHubRemoteError, match="repository private must be boolean"):
        client.list_installation_repositories(token=token, observed_at=NOW)
