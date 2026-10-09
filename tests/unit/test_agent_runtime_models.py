"""Validation and canonical request identity tests for AgentRuntime values."""

import hashlib
import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from relay_engine.agent_runtime.models import (
    CredentialRef,
    RuntimeCapability,
    RuntimeExecutionBasis,
    RuntimeExecutionRequest,
    RuntimePermissionProfileRef,
    RuntimeSelection,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeWorkspaceAttachment,
    canonical_execution_basis_json,
    digest_execution_basis,
)
from relay_engine.domain import CommitRef, RepositoryRef

EXECUTION_ID = "exec_018f47c1-7b2c-7abc-8def-123456789001"
SLICE_ID = "slc_018f47c1-7b2c-7abc-8def-123456789002"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789003"
REPOSITORY_ID = "repo_018f47c1-7b2c-7abc-8def-123456789004"
COMMIT_SHA = "e8598ae5ffb046d4131e04655a0c063ff1e41ccc"
DIGEST = "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"


def repository() -> RepositoryRef:
    return RepositoryRef(id=REPOSITORY_ID, host="github.com", path="team/project")


def basis(**updates: object) -> RuntimeExecutionBasis:
    repo = repository()
    values: dict[str, object] = {
        "execution_id": EXECUTION_ID,
        "slice_id": SLICE_ID,
        "source_baseline_id": BASELINE_ID,
        "workspace": RuntimeWorkspaceAttachment(
            workspace_id="workspace-main",
            root="/tmp/relay-workspace",
            repository=repo,
            source_commit=CommitRef(repository=repo, sha=COMMIT_SHA),
        ),
        "input_payload": {
            "text": "Review the changes.",
            "payload_digest": DIGEST,
            "attachment_refs": (),
        },
        "runtime_selection": RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="provider-a",
            requested_model_id="model-a",
        ),
        "permission_profile_ref": RuntimePermissionProfileRef(
            profile_id="noninteractive",
            content_digest=DIGEST,
        ),
        "credential_refs": (),
        "required_capabilities": (RuntimeCapability.EVENT_STREAM,),
        "limits": {"max_duration_seconds": 120, "max_tool_calls": 20},
    }
    values.update(updates)
    return RuntimeExecutionBasis(**values)  # type: ignore[arg-type]


def test_runtime_values_are_frozen_extra_forbid_and_versioned() -> None:
    request_basis = basis()
    assert request_basis.model_config["frozen"] is True
    assert request_basis.model_config["extra"] == "forbid"
    assert request_basis.model_dump(mode="json")["schema_version"] == 1

    with pytest.raises(ValidationError):
        request_basis.execution_id = "exec_018f47c1-7b2c-7abc-8def-123456789009"

    with pytest.raises(ValidationError):
        RuntimeSessionRef(runtime_id="opencode", session_id="session-1", token="secret")


@pytest.mark.parametrize("value", ["", "   ", "x" * 129])
def test_runtime_identifiers_must_be_nonblank_and_bounded(value: str) -> None:
    with pytest.raises(ValidationError):
        RuntimeSessionRef(runtime_id="opencode", session_id=value)


def test_workspace_is_explicit_and_exact_commit_matches_repository() -> None:
    request_basis = basis()
    assert request_basis.workspace.root == "/tmp/relay-workspace"
    with pytest.raises(ValidationError):
        RuntimeWorkspaceAttachment(
            workspace_id="workspace-main",
            root="../outside",
            repository=repository(),
            source_commit=CommitRef(repository=repository(), sha=COMMIT_SHA),
        )

    other_repository = RepositoryRef(
        id="repo_018f47c1-7b2c-7abc-8def-123456789005",
        host="github.com",
        path="team/other",
    )
    with pytest.raises(ValidationError):
        RuntimeWorkspaceAttachment(
            workspace_id="workspace-main",
            root="/tmp/relay-workspace",
            repository=repository(),
            source_commit=CommitRef(repository=other_repository, sha=COMMIT_SHA),
        )


def test_credential_refs_are_identifiers_only_and_unique() -> None:
    with pytest.raises(ValidationError, match="must not contain duplicates"):
        basis(credential_refs=(CredentialRef(credential_id="provider-key"),) * 2)

    assert set(CredentialRef.model_fields) == {"schema_version", "credential_id"}
    with pytest.raises(ValidationError):
        CredentialRef.model_validate(
            {"credential_id": "provider-key", "access_token": "never-store"}
        )


def test_session_binding_normalizes_aware_timestamps_to_utc() -> None:
    binding = RuntimeSessionBinding(
        execution_id=EXECUTION_ID,
        runtime_session=RuntimeSessionRef(runtime_id="opencode", session_id="ses_test"),
        request_digest=DIGEST,
        workspace_id="workspace-main",
        created_at=datetime(2026, 1, 1, 12, tzinfo=timezone(timedelta(hours=3))),
    )
    assert binding.created_at == datetime(2026, 1, 1, 9, tzinfo=UTC)

    with pytest.raises(ValidationError, match="timezone"):
        RuntimeSessionBinding(
            execution_id=EXECUTION_ID,
            runtime_session=RuntimeSessionRef(runtime_id="opencode", session_id="ses_test"),
            request_digest=DIGEST,
            workspace_id="workspace-main",
            created_at=datetime(2026, 1, 1),
        )


def test_digest_matches_fixed_schema_v1_canonical_vector() -> None:
    request_basis = basis(
        input_payload={
            "text": "café",
            "payload_digest": DIGEST,
            "attachment_refs": (),
        },
        limits={"max_duration_seconds": 120, "max_tool_calls": 20},
    )
    canonical = canonical_execution_basis_json(request_basis)
    expected_canonical = (
        '{"credential_refs":[],"execution_id":"exec_018f47c1-7b2c-7abc-8def-123456789001",'
        '"input_payload":{"attachment_refs":[],"payload_digest":"sha256:'
        '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",'
        '"schema_version":1,"text":"café"},"limits":{"max_duration_seconds":120,'
        '"max_output_bytes":null,"max_tool_calls":20,"schema_version":1},'
        '"permission_profile_ref":{"content_digest":"sha256:'
        '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",'
        '"profile_id":"noninteractive","schema_version":1},'
        '"required_capabilities":["EVENT_STREAM"],"runtime_selection":{'
        '"requested_model_id":"model-a","requested_provider_id":"provider-a",'
        '"runtime_id":"opencode","schema_version":1},"schema_version":1,'
        '"slice_id":"slc_018f47c1-7b2c-7abc-8def-123456789002",'
        '"source_baseline_id":"base_018f47c1-7b2c-7abc-8def-123456789003",'
        '"workspace":{"repository":{"host":"github.com",'
        '"id":"repo_018f47c1-7b2c-7abc-8def-123456789004",'
        '"path":"team/project","schema_version":1},"root":"/tmp/relay-workspace",'
        '"schema_version":1,"source_commit":{"repository":{"host":"github.com",'
        '"id":"repo_018f47c1-7b2c-7abc-8def-123456789004",'
        '"path":"team/project","schema_version":1},"schema_version":1,'
        '"sha":"e8598ae5ffb046d4131e04655a0c063ff1e41ccc"},'
        '"workspace_id":"workspace-main"}}'
    )
    expected_digest = "03c9676856fcc22625a77da18c43f6d3533a36eeec50ae5c9764d1e6b2c7fba8"

    assert canonical == expected_canonical
    assert hashlib.sha256(expected_canonical.encode("utf-8")).hexdigest() == expected_digest
    assert digest_execution_basis(request_basis) == f"sha256:{expected_digest}"
    assert digest_execution_basis(request_basis) == digest_execution_basis(request_basis)


def test_basis_change_changes_digest_and_wrong_request_digest_is_rejected() -> None:
    original = basis()
    changed = basis(
        runtime_selection=RuntimeSelection(
            runtime_id="opencode",
            requested_provider_id="provider-b",
            requested_model_id="model-a",
        )
    )
    correct_digest = digest_execution_basis(original)
    assert digest_execution_basis(changed) != correct_digest
    assert RuntimeExecutionRequest(basis=original, request_digest=correct_digest)

    with pytest.raises(ValidationError, match="does not match execution basis"):
        RuntimeExecutionRequest(basis=original, request_digest=DIGEST)


def test_canonical_serialization_is_json_compatible_and_unicode_preserving() -> None:
    canonical = canonical_execution_basis_json(basis())
    assert json.loads(canonical)["schema_version"] == 1
    assert "\\u" not in canonical
