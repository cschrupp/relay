"""Integration tests use only disposable local Git repositories."""

from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from relay_engine.domain import CommitRef, RepositoryRef
from relay_engine.execution_workspace.evaluation import workspace_provider_ref
from relay_engine.execution_workspace.local_clone import LocalCloneWorkspaceProvider
from relay_engine.execution_workspace.models import (
    ControlStrength,
    ExternalSideEffectMode,
    ExternalSideEffectPolicy,
    FilesystemAccess,
    FilesystemPolicy,
    NetworkMode,
    NetworkPolicy,
    ProviderInjectedFileRequirement,
    RepositoryMetadataAccess,
    RepositoryMetadataPolicy,
    RoleContractRef,
    ShellMode,
    ShellPolicy,
    ToolDecision,
    ToolPolicy,
    WorkspaceEntryKind,
    WorkspacePlan,
    WorkspaceProperty,
    WorkspacePropertyRequirement,
    WorkspaceResourceLimits,
    WorkspaceRetentionMode,
    WorkspaceRetentionPolicy,
    workspace_change_manifest_ref,
)
from relay_engine.execution_workspace.provider import (
    WorkspaceProviderError,
    WorkspaceProviderErrorCode,
)
from relay_engine.work_packets import SourceBaselineRef, WorkPacketRef, WorkspacePolicyRef


def git(path: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=path, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def make_plan(
    source: Path, retention: WorkspaceRetentionMode = WorkspaceRetentionMode.DELETE_ON_TERMINAL
) -> WorkspacePlan:
    git(source, "config", "user.name", "Disposable Test")
    git(source, "config", "user.email", "test@example.invalid")
    (source / "tracked.txt").write_text("before\n", encoding="utf-8")
    (source / "deleted.txt").write_text("remove me\n", encoding="utf-8")
    git(source, "add", "tracked.txt")
    git(source, "add", "deleted.txt")
    git(source, "commit", "-m", "initial")
    repo = RepositoryRef(
        id="repo_00000000-0000-0000-0000-000000000002", host="local", path="disposable"
    )
    commit = CommitRef(repository=repo, sha=git(source, "rev-parse", "HEAD"))
    packet_ref = WorkPacketRef(
        project_id="prj_00000000-0000-0000-0000-000000000002",
        slice_id="slc_00000000-0000-0000-0000-000000000002",
        packet_key="disposable-packet",
        revision=1,
        content_digest="sha256:" + "3" * 64,
    )
    provider = LocalCloneWorkspaceProvider(source)
    provider_ref = workspace_provider_ref(provider.describe())
    return WorkspacePlan(
        plan_key="disposable-plan",
        revision=1,
        work_packet_ref=packet_ref,
        source_baseline_ref=SourceBaselineRef(
            baseline_id="base_00000000-0000-0000-0000-000000000002",
            project_id=packet_ref.project_id,
            commit=commit,
            content_digest="sha256:" + "4" * 64,
        ),
        role_contract_ref=RoleContractRef(
            role_key="implementer", revision=1, content_digest="sha256:" + "5" * 64
        ),
        workspace_policy_ref=WorkspacePolicyRef(
            policy_key="workspace", content_digest="sha256:" + "6" * 64
        ),
        governance_profile_ref=None,
        provider_ref=provider_ref,
        packet_required_property_keys=("clean-state", "exact-source"),
        property_requirements=(
            WorkspacePropertyRequirement(
                key="clean-state",
                property=WorkspaceProperty.CLEAN_INITIAL_STATE,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
            WorkspacePropertyRequirement(
                key="exact-source",
                property=WorkspaceProperty.EXACT_SOURCE_BASELINE,
                minimum_strength=ControlStrength.DETECTIVE,
            ),
        ),
        protected_asset_bindings=(),
        workspace_credential_grants=(),
        provider_injected_files=(),
        filesystem_policy=FilesystemPolicy(
            default_access=FilesystemAccess.READ_WRITE, writable_prefixes=(), denied_prefixes=()
        ),
        repository_metadata_policy=RepositoryMetadataPolicy(
            access=RepositoryMetadataAccess.READ_ONLY
        ),
        tool_policy=ToolPolicy(default_decision=ToolDecision.DENY, rules=()),
        shell_policy=ShellPolicy(mode=ShellMode.DENY),
        network_policy=NetworkPolicy(mode=NetworkMode.DENY_ALL, allowed_endpoints=()),
        external_side_effect_policy=ExternalSideEffectPolicy(
            mode=ExternalSideEffectMode.DENY_MUTATING_EFFECTS, allowed_effects=()
        ),
        resource_limits=WorkspaceResourceLimits(),
        retention_policy=WorkspaceRetentionPolicy(mode=retention),
    )


def test_local_clone_exact_commit_independent_objects_changes_and_teardown(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-b", "main")
    plan = make_plan(source)
    provider = LocalCloneWorkspaceProvider(source, workspace_parent=tmp_path / "workspaces")
    result = provider.provision(plan)
    root = Path(result.instance_ref.root)
    assert result.initial_inspection.head_commit == plan.source_baseline_ref.commit
    assert not result.initial_inspection.tracked_changes
    assert not result.initial_inspection.untracked_paths
    assert not (root / ".git/objects/info/alternates").exists()
    assert git(root, "rev-parse", "--is-shallow-repository") == "false"
    assert git(root, "rev-parse", "--is-inside-work-tree") == "true"

    source_objects = {
        (path.stat().st_dev, path.stat().st_ino)
        for path in (source / ".git/objects").rglob("*")
        if path.is_file()
    }
    workspace_objects = {
        (path.stat().st_dev, path.stat().st_ino)
        for path in (root / ".git/objects").rglob("*")
        if path.is_file()
    }
    assert source_objects.isdisjoint(workspace_objects)

    (root / "tracked.txt").write_text("after\n", encoding="utf-8")
    (root / "tracked.txt").chmod(0o755)
    (root / "added.txt").write_text("new\n", encoding="utf-8")
    (root / "symlink.txt").symlink_to("tracked.txt")
    (root / "deleted.txt").unlink()
    manifest = provider.extract_changes(result.instance_ref)
    assert tuple(entry.path for entry in manifest.entries) == (
        "added.txt",
        "deleted.txt",
        "symlink.txt",
        "tracked.txt",
    )
    capture = provider.capture_candidate(result.instance_ref, manifest)
    captured_tree = capture.tree_object_id
    assert capture.change_manifest_digest == workspace_change_manifest_ref(manifest).content_digest
    assert git(root, "cat-file", "-t", captured_tree) == "tree"
    assert (
        subprocess.run(
            ["git", "show", f"{captured_tree}:tracked.txt"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        == b"after\n"
    )
    git(root, "diff", "--cached", "--quiet")
    (root / "tracked.txt").write_text("later mutation\n", encoding="utf-8")
    assert (
        subprocess.run(
            ["git", "show", f"{captured_tree}:tracked.txt"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        == b"after\n"
    )
    entries = {entry.path: entry for entry in manifest.entries}
    assert entries["deleted.txt"].before is not None
    assert entries["deleted.txt"].after is None
    assert entries["symlink.txt"].after is not None
    assert entries["symlink.txt"].after.kind is WorkspaceEntryKind.SYMLINK
    assert entries["tracked.txt"].before is not None
    assert entries["tracked.txt"].after is not None
    assert entries["tracked.txt"].before.executable is False
    assert entries["tracked.txt"].after.executable is True
    assert workspace_change_manifest_ref(manifest).content_digest.startswith("sha256:")
    assert git(source, "status", "--porcelain") == ""
    teardown = provider.teardown(result.instance_ref)
    assert teardown.disposition.value == "DELETED"
    assert not root.exists()


def test_local_clone_capture_rejects_manifest_when_workspace_changes_after_extraction(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source-capture-race"
    source.mkdir()
    git(source, "init", "-b", "main")
    plan = make_plan(source)
    provider = LocalCloneWorkspaceProvider(source, workspace_parent=tmp_path / "workspaces")
    result = provider.provision(plan)
    root = Path(result.instance_ref.root)
    target = root / "tracked.txt"
    target.write_text("captured version\n", encoding="utf-8")
    extracted = provider.extract_changes(result.instance_ref)

    target.write_text("changed before capture\n", encoding="utf-8")
    with pytest.raises(WorkspaceProviderError, match="changed between manifest extraction"):
        provider.capture_candidate(result.instance_ref, extracted)

    provider.teardown(result.instance_ref)


def test_local_clone_retention_policy_is_observed(tmp_path: Path) -> None:
    source = tmp_path / "source-retained"
    source.mkdir()
    git(source, "init", "-b", "main")
    plan = make_plan(source, WorkspaceRetentionMode.RETAIN_UNTIL_EXPLICIT_RELEASE)
    provider = LocalCloneWorkspaceProvider(source, workspace_parent=tmp_path / "workspaces")
    result = provider.provision(plan)
    teardown = provider.teardown(result.instance_ref)
    assert teardown.disposition.value == "RETAINED_BY_POLICY"
    assert Path(result.instance_ref.root).exists()


def test_provider_injected_file_is_digest_bound_and_tracked_as_change(tmp_path: Path) -> None:
    source = tmp_path / "source-injected"
    source.mkdir()
    git(source, "init", "-b", "main")
    original_plan = make_plan(source)
    content = b"provider-owned helper\n"
    provider = LocalCloneWorkspaceProvider(
        source,
        injected_file_materials={"test-helper": content},
        workspace_parent=tmp_path / "workspaces",
    )
    requirement = ProviderInjectedFileRequirement(
        path="tools/helper.txt",
        provider_file_key="test-helper",
        content_digest="sha256:" + hashlib.sha256(content).hexdigest(),
    )
    wrong_digest_plan = original_plan.model_copy(
        update={
            "provider_ref": workspace_provider_ref(provider.describe()),
            "provider_injected_files": (
                requirement.model_copy(update={"content_digest": "sha256:" + "0" * 64}),
            ),
        }
    )
    with pytest.raises(WorkspaceProviderError):
        provider.provision(wrong_digest_plan)

    plan = original_plan.model_copy(
        update={
            "provider_ref": workspace_provider_ref(provider.describe()),
            "provider_injected_files": (requirement,),
        }
    )
    result = provider.provision(plan)
    root = Path(result.instance_ref.root)
    assert (root / requirement.path).read_bytes() == content
    assert provider.extract_changes(result.instance_ref).entries == ()

    changed_content = b"changed helper\n"
    (root / requirement.path).write_bytes(changed_content)
    change = provider.extract_changes(result.instance_ref).entries
    assert len(change) == 1
    assert change[0].path == requirement.path
    assert change[0].before is not None
    assert change[0].before.content_digest == requirement.content_digest
    assert change[0].after is not None
    assert change[0].after.kind is WorkspaceEntryKind.REGULAR_FILE
    assert change[0].after.content_digest == "sha256:" + hashlib.sha256(changed_content).hexdigest()
    assert git(source, "status", "--porcelain") == ""
    provider.teardown(result.instance_ref)


def test_gitlink_in_source_tree_fails_closed_during_provision(tmp_path: Path) -> None:
    source = tmp_path / "source-gitlink"
    source.mkdir()
    git(source, "init", "-b", "main")
    plan = make_plan(source)

    submodule = tmp_path / "submodule"
    submodule.mkdir()
    git(submodule, "init", "-b", "main")
    git(submodule, "config", "user.name", "Disposable Test")
    git(submodule, "config", "user.email", "test@example.invalid")
    (submodule / "nested.txt").write_text("nested\n", encoding="utf-8")
    git(submodule, "add", "nested.txt")
    git(submodule, "commit", "-m", "nested commit")
    submodule_commit = git(submodule, "rev-parse", "HEAD")

    git(
        source,
        "update-index",
        "--add",
        "--cacheinfo",
        f"160000,{submodule_commit},nested-module",
    )
    git(source, "commit", "-m", "add gitlink")
    plan = plan.model_copy(
        update={
            "source_baseline_ref": plan.source_baseline_ref.model_copy(
                update={
                    "commit": plan.source_baseline_ref.commit.model_copy(
                        update={"sha": git(source, "rev-parse", "HEAD")}
                    )
                }
            )
        }
    )
    provider = LocalCloneWorkspaceProvider(source, workspace_parent=tmp_path / "workspaces")

    with pytest.raises(WorkspaceProviderError) as error:
        provider.provision(plan)

    assert error.value.code is WorkspaceProviderErrorCode.INSPECTION_FAILED


def test_unsupported_worktree_node_fails_closed_for_inspection_and_changes(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source-special-node"
    source.mkdir()
    git(source, "init", "-b", "main")
    plan = make_plan(source)
    provider = LocalCloneWorkspaceProvider(source, workspace_parent=tmp_path / "workspaces")
    result = provider.provision(plan)
    special_node = Path(result.instance_ref.root) / "unsupported-fifo"
    os.mkfifo(special_node)

    with pytest.raises(WorkspaceProviderError) as inspection_error:
        provider.inspect(result.instance_ref)
    assert inspection_error.value.code is WorkspaceProviderErrorCode.INSPECTION_FAILED

    with pytest.raises(WorkspaceProviderError) as changeset_error:
        provider.extract_changes(result.instance_ref)
    assert changeset_error.value.code is WorkspaceProviderErrorCode.CHANGESET_FAILED
