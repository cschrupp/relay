from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import SecretStr

from relay_engine.integrations.github import (
    GitHubAppConfig,
    GitHubClient,
    GitHubInstallationToken,
    GitHubRefNotFound,
    GitHubRemoteError,
    GitHubRequest,
    GitHubResponse,
)

NOW = datetime(2026, 9, 28, 1, 0, tzinfo=UTC)
SHA = "1" * 40
TREE_SHA = "2" * 40
BLOB_SHA = "3" * 40


class FakeTransport:
    def __init__(self, responses: list[GitHubResponse]) -> None:
        self.responses = responses
        self.requests: list[GitHubRequest] = []

    def request(self, request: GitHubRequest) -> GitHubResponse:
        self.requests.append(request)
        return self.responses.pop(0)


def _response(status: int, payload: object) -> GitHubResponse:
    return GitHubResponse(
        status=status,
        headers={},
        body=json.dumps(payload, separators=(",", ":")).encode(),
    )


def _token() -> GitHubInstallationToken:
    return GitHubInstallationToken(token=SecretStr("token"), expires_at=NOW + timedelta(hours=1))


def test_commit_resolution_uses_explicit_encoded_ref_once() -> None:
    transport = FakeTransport([_response(200, {"sha": SHA})])
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    result = client.resolve_commit_sha(
        token=_token(), repository_path="owner/repo", ref="heads/main"
    )
    assert result.sha == SHA
    assert transport.requests[0].url.endswith("/repos/owner/repo/commits/heads%2Fmain")


def test_ref_404_is_distinct_from_other_remote_failures() -> None:
    transport = FakeTransport([_response(404, {"message": "not found"})])
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    with pytest.raises(GitHubRefNotFound):
        client.resolve_commit_sha(token=_token(), repository_path="owner/repo", ref="tags/missing")


def test_git_commit_and_tree_are_strictly_parsed() -> None:
    transport = FakeTransport(
        [
            _response(200, {"sha": SHA, "tree": {"sha": TREE_SHA}}),
            _response(
                200,
                {
                    "sha": TREE_SHA,
                    "truncated": False,
                    "tree": [
                        {
                            "path": "file.txt",
                            "mode": "100644",
                            "type": "blob",
                            "sha": BLOB_SHA,
                        }
                    ],
                },
            ),
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    commit = client.get_git_commit(token=_token(), repository_path="owner/repo", sha=SHA)
    tree = client.get_git_tree(token=_token(), repository_path="owner/repo", tree_sha=TREE_SHA)
    assert commit.sha == SHA
    assert commit.tree_sha == TREE_SHA
    assert tree.sha == TREE_SHA
    assert tree.truncated is False
    assert tree.entries[0].sha == BLOB_SHA


def test_git_blob_decodes_exact_bytes_and_validates_declared_size() -> None:
    raw = b"exact blob bytes\n"
    encoded = base64.b64encode(raw).decode()
    transport = FakeTransport(
        [
            _response(
                200,
                {"sha": BLOB_SHA, "encoding": "base64", "size": len(raw), "content": encoded},
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    blob = client.get_git_blob(token=_token(), repository_path="owner/repo", blob_sha=BLOB_SHA)
    assert blob.sha == BLOB_SHA
    assert blob.raw_bytes == raw


def test_git_blob_size_mismatch_fails_closed() -> None:
    raw = b"exact blob bytes\n"
    transport = FakeTransport(
        [
            _response(
                200,
                {
                    "sha": BLOB_SHA,
                    "encoding": "base64",
                    "size": len(raw) + 1,
                    "content": base64.b64encode(raw).decode(),
                },
            )
        ]
    )
    client = GitHubClient(GitHubAppConfig(client_id="Iv1.test"), transport)
    with pytest.raises(GitHubRemoteError, match="size disagrees"):
        client.get_git_blob(token=_token(), repository_path="owner/repo", blob_sha=BLOB_SHA)
