"""Schema, canonical identity, and non-authority tests for Slice 2.4."""

from __future__ import annotations

import hashlib

import pytest
from pydantic import ValidationError

from relay_engine.domain import RepositoryRef
from relay_engine.execution_workspace.evaluation import (
    canonical_workspace_policy_json,
    digest_workspace_policy,
    path_has_prefix,
)
from relay_engine.execution_workspace.models import (
    ControlStrength,
    ExternalSideEffectMode,
    ExternalSideEffectPolicy,
    FilesystemAccess,
    FilesystemPolicy,
    NetworkMode,
    NetworkPolicy,
    RepositoryMetadataAccess,
    RepositoryMetadataPolicy,
    RepositoryPathPrefix,
    ShellMode,
    ShellPolicy,
    ToolDecision,
    ToolPolicy,
    WorkspaceCredentialPolicy,
    WorkspacePlan,
    WorkspacePolicyDefinition,
    WorkspaceProperty,
    WorkspacePropertyRequirement,
    WorkspaceResourceLimits,
    WorkspaceRetentionMode,
    WorkspaceRetentionPolicy,
)
from relay_engine.work_packets import PolicyBasisRef


def policy() -> WorkspacePolicyDefinition:
    return WorkspacePolicyDefinition(
        policy_key="workspace-default",
        policy_basis_ref=PolicyBasisRef(
            policy_key="engineering-policy",
            policy_version=1,
            policy_digest="sha256:" + "1" * 64,
            effective_scope_digest="sha256:" + "2" * 64,
        ),
        governance_profile_ref=None,
        property_requirements=(
            WorkspacePropertyRequirement(
                key="exact-source",
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
        ),
        filesystem_policy=FilesystemPolicy(
            default_access=FilesystemAccess.READ_ONLY,
            writable_prefixes=(RepositoryPathPrefix(value="src"),),
            denied_prefixes=(RepositoryPathPrefix(value="src/private"),),
        ),
        repository_metadata_policy=RepositoryMetadataPolicy(
            access=RepositoryMetadataAccess.READ_ONLY
        ),
        tool_policy=ToolPolicy(default_decision=ToolDecision.DENY, rules=()),
        shell_policy=ShellPolicy(mode=ShellMode.DENY),
        network_policy=NetworkPolicy(mode=NetworkMode.DENY_ALL, allowed_endpoints=()),
        external_side_effect_policy=ExternalSideEffectPolicy(
            mode=ExternalSideEffectMode.DENY_MUTATING_EFFECTS,
            allowed_effects=(),
        ),
        credential_policy=WorkspaceCredentialPolicy(grants=()),
        resource_limits=WorkspaceResourceLimits(),
        retention_policy=WorkspaceRetentionPolicy(mode=WorkspaceRetentionMode.DELETE_ON_TERMINAL),
        provider_injected_files=(),
    )


def test_workspace_policy_canonical_json_and_digest_are_exact() -> None:
    value = policy()
    canonical = canonical_workspace_policy_json(value)
    expected_canonical = (
        '{"credential_policy":{"grants":[],"schema_version":1},'
        '"external_side_effect_policy":{"allowed_effects":[],"mode":"DENY_MUTATING_EFFECTS",'
        '"schema_version":1},"filesystem_policy":{"default_access":"READ_ONLY",'
        '"denied_prefixes":[{"schema_version":1,"value":"src/private"}],"schema_version":1,'
        '"writable_prefixes":[{"schema_version":1,"value":"src"}]},'
        '"governance_profile_ref":null,"network_policy":{"allowed_endpoints":[],"mode":"DENY_ALL",'
        '"schema_version":1},"policy_basis_ref":{"effective_scope_digest":"sha256:'
        + "2" * 64
        + '","policy_digest":"sha256:'
        + "1" * 64
        + '","policy_key":"engineering-policy","policy_version":1,"schema_version":1},'
        '"policy_key":"workspace-default","property_requirements":[{"key":"exact-source",'
        '"minimum_strength":"DETECTIVE","property":"EXACT_SOURCE_BASELINE","schema_version":1}],'
        '"provider_injected_files":[],"repository_metadata_policy":{"access":"READ_ONLY",'
        '"schema_version":1},"resource_limits":{"max_cpu_seconds":null,"max_disk_bytes":null,'
        '"max_memory_bytes":null,"max_open_files":null,"max_processes":null,"schema_version":1},'
        '"retention_policy":{"max_retention_seconds":null,"mode":"DELETE_ON_TERMINAL",'
        '"schema_version":1},"schema_version":1,"shell_policy":{"mode":"DENY","schema_version":1},'
        '"tool_policy":{"default_decision":"DENY","rules":[],"schema_version":1}}'
    )
    expected_digest = "sha256:eb3d725815b9de3d6fe0d9b581e14b4310a0da30c4749fff4a9c51c108dae567"
    assert canonical == expected_canonical
    assert digest_workspace_policy(value) == expected_digest
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == expected_digest.removeprefix(
        "sha256:"
    )
    assert digest_workspace_policy(value) == digest_workspace_policy(value.model_copy(deep=True))


def test_path_prefix_uses_segments_and_path_escape_is_rejected() -> None:
    assert path_has_prefix("src/package/file.py", "src")
    assert not path_has_prefix("src-old/file.py", "src")
    with pytest.raises(ValidationError):
        RepositoryPathPrefix(value="../outside")


def test_network_policy_rejects_endpoint_without_allowlist() -> None:
    with pytest.raises(ValidationError):
        NetworkPolicy(mode=NetworkMode.ALLOWLIST, allowed_endpoints=())


def test_workspace_models_do_not_define_authority_or_acceptance_fields() -> None:
    for model in (WorkspacePlan, WorkspacePolicyDefinition):
        assert "authorized" not in model.model_fields
        assert "human_accepted" not in model.model_fields


def test_repository_identity_is_an_existing_domain_type() -> None:
    assert RepositoryRef.__module__ == "relay_engine.domain.references"
