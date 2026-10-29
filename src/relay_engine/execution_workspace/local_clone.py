"""Disposable local Git clone provider for development/dogfood evidence.

This provider runs as the same user as the host and is not a security sandbox.
It never uses remote Git operations, credential material, or AgentRuntime.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from relay_engine.domain import ContentDigest
from relay_engine.execution_workspace.evaluation import (
    derive_runtime_workspace_attachment,
    workspace_plan_ref,
    workspace_provider_ref,
)
from relay_engine.execution_workspace.models import (
    ControlStrength,
    ProtectedAssetObservation,
    ProviderInjectedFileCapability,
    RepositoryMetadataAccess,
    WorkspaceBackendKind,
    WorkspaceBoundaryClass,
    WorkspaceCandidateCapture,
    WorkspaceChangeEntry,
    WorkspaceChangeManifest,
    WorkspaceEntryKind,
    WorkspaceEntryState,
    WorkspaceEnvironmentProvenance,
    WorkspaceEvidenceSubject,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePlan,
    WorkspaceProperty,
    WorkspacePropertyEvidence,
    WorkspaceProviderDescriptor,
    WorkspaceProviderPropertyCapability,
    WorkspaceProvisionResult,
    WorkspaceRetentionMode,
    WorkspaceTeardownEvidence,
    WorkspaceTerminalDisposition,
    digest_workspace_change_manifest,
)
from relay_engine.execution_workspace.provider import (
    WorkspaceProviderError,
    WorkspaceProviderErrorCode,
)
from relay_engine.role_contracts import RequirementStatus

_LOCAL_STRENGTHS = {
    WorkspaceProperty.EXACT_SOURCE_BASELINE: ControlStrength.DETECTIVE,
    WorkspaceProperty.CLEAN_INITIAL_STATE: ControlStrength.DETECTIVE,
    WorkspaceProperty.REPOSITORY_METADATA_ISOLATED: ControlStrength.DETECTIVE,
    WorkspaceProperty.DIRTY_STATE_INSPECTION: ControlStrength.DETECTIVE,
    WorkspaceProperty.CHANGESET_EXTRACTION: ControlStrength.DETECTIVE,
    WorkspaceProperty.RETENTION_CONTROL: ControlStrength.MEDIATED,
    WorkspaceProperty.TEARDOWN_CONTROL: ControlStrength.MEDIATED,
}


def _sha256(data: bytes) -> ContentDigest:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class LocalCloneWorkspaceProvider:
    """Provision independent local clones with exact commit and change evidence."""

    def __init__(
        self,
        source_repository_path: str | Path,
        *,
        provider_id: str = "relay-local-clone",
        provider_version: str = "1",
        injected_file_materials: dict[str, bytes] | None = None,
        workspace_parent: str | Path | None = None,
    ) -> None:
        self._source = Path(source_repository_path).resolve()
        self._provider_id = provider_id
        self._provider_version = provider_version
        self._materials = dict(injected_file_materials or {})
        self._parent = None if workspace_parent is None else Path(workspace_parent).resolve()
        self._instances: dict[str, WorkspaceInstanceRef] = {}
        self._source_snapshots: dict[str, tuple[str, str, str]] = {}
        self._plans: dict[str, WorkspacePlan] = {}
        self._retention: dict[str, WorkspaceRetentionMode] = {}

    def describe(self) -> WorkspaceProviderDescriptor:
        capabilities = tuple(
            WorkspaceProviderPropertyCapability(
                property=property, maximum_strength=_LOCAL_STRENGTHS[property]
            )
            for property in WorkspaceProperty
            if property in _LOCAL_STRENGTHS
        )
        injected = tuple(
            sorted(
                (
                    ProviderInjectedFileCapability(file_key=key, content_digest=_sha256(value))
                    for key, value in self._materials.items()
                ),
                key=lambda item: item.file_key,
            )
        )
        return WorkspaceProviderDescriptor(
            provider_id=self._provider_id,
            provider_version=self._provider_version,
            backend_kind=WorkspaceBackendKind.LOCAL_CLONE,
            boundary_class=WorkspaceBoundaryClass.SAME_USER_NO_SECURITY_BOUNDARY,
            property_capabilities=capabilities,
            supported_shell_modes=(),
            supported_network_modes=(),
            supported_external_side_effect_modes=(),
            supported_credential_exposure_modes=(),
            supported_resource_dimensions=(),
            supported_repository_metadata_modes=(RepositoryMetadataAccess.READ_ONLY,),
            path_control_capabilities=(),
            provider_injected_file_capabilities=injected,
        )

    def provision(self, plan: WorkspacePlan) -> WorkspaceProvisionResult:
        if not self._source.is_dir():
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.SOURCE_NOT_AVAILABLE,
                "local source repository is unavailable",
            )
        descriptor = self.describe()
        descriptor_ref = workspace_provider_ref(descriptor)
        if plan.provider_ref != descriptor_ref:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.INVALID_PLAN,
                "plan provider identity does not match this provider",
            )
        for requirement in plan.provider_injected_files:
            material = self._materials.get(requirement.provider_file_key)
            if material is None or _sha256(material) != requirement.content_digest:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.UNSUPPORTED_POLICY,
                    "provider-owned material is unavailable or has the wrong digest",
                )
        source_before = self._source_snapshot()
        commit = plan.source_baseline_ref.commit
        if not (self._source / ".git").exists():
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.SOURCE_NOT_AVAILABLE,
                "source path is not a local Git checkout",
            )
        try:
            self._git(self._source, "cat-file", "-e", f"{commit.sha}^{{commit}}")
        except WorkspaceProviderError as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.SOURCE_COMMIT_NOT_AVAILABLE,
                "exact source commit is unavailable locally",
            ) from exc
        if self._parent is not None:
            self._parent.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="relay-workspace-", dir=self._parent))
        try:
            self._git(
                self._source.parent,
                "clone",
                "--no-hardlinks",
                "--no-local",
                "--no-checkout",
                "--",
                str(self._source),
                str(root),
            )
            self._git(root, "remote", "remove", "origin")
            self._git(root, "checkout", "--detach", commit.sha)
            head = self._git(root, "rev-parse", "HEAD").strip()
            if head != commit.sha:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED,
                    "clone did not checkout the exact source commit",
                )
            alternates = root / ".git" / "objects" / "info" / "alternates"
            if alternates.exists() and alternates.read_text(encoding="utf-8").strip():
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED,
                    "clone has an alternate object store",
                )
            status = self._git(root, "status", "--porcelain", "--untracked-files=all").strip()
            if status:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED, "clone initial state is not clean"
                )
            for requirement in plan.provider_injected_files:
                target = root.joinpath(*requirement.path.split("/"))
                if not target.resolve(strict=False).is_relative_to(root.resolve()):
                    raise WorkspaceProviderError(
                        WorkspaceProviderErrorCode.INVALID_PLAN,
                        "injected path resolves outside workspace",
                    )
                if target.exists() or target.is_symlink():
                    raise WorkspaceProviderError(
                        WorkspaceProviderErrorCode.INVALID_PLAN,
                        "provider-injected path already exists in source baseline",
                    )
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(self._materials[requirement.provider_file_key])
            instance = WorkspaceInstanceRef(
                workspace_id=f"local-clone:{root.name}",
                plan_ref=workspace_plan_ref(plan),
                provider_ref=descriptor_ref,
                repository=commit.repository,
                source_commit=commit,
                root=str(root),
            )
            self._instances[instance.workspace_id] = instance
            self._source_snapshots[instance.workspace_id] = source_before
            self._plans[instance.workspace_id] = plan
            self._retention[instance.workspace_id] = plan.retention_policy.mode
            inspection = self._inspect(instance, plan)
            if inspection.head_commit != commit:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED,
                    "initial inspection source commit mismatch",
                )
            if inspection.tracked_changes or inspection.untracked_paths:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED,
                    "initial clone contains unexpected changes",
                )
            observed = self._worktree_states(root)
            for requirement in plan.provider_injected_files:
                state = observed.get(requirement.path)
                if (
                    state is None
                    or state.kind is not WorkspaceEntryKind.REGULAR_FILE
                    or state.content_digest != requirement.content_digest
                ):
                    raise WorkspaceProviderError(
                        WorkspaceProviderErrorCode.PROVISION_FAILED,
                        "injected material did not match its exact planned identity",
                    )
            if self._source_snapshot() != source_before:
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.PROVISION_FAILED,
                    "source repository changed during clone",
                )
            evidence = inspection.property_evidence
            subject = WorkspaceEvidenceSubject(
                plan_ref=instance.plan_ref,
                instance_ref=instance,
                provider_ref=instance.provider_ref,
            )
            environment = WorkspaceEnvironmentProvenance(
                subject=subject,
                boundary_class=WorkspaceBoundaryClass.SAME_USER_NO_SECURITY_BOUNDARY,
                backend_kind=WorkspaceBackendKind.LOCAL_CLONE,
                platform_key="local-platform",
                platform_version=os.name,
                image_digest=None,
                environment_payload_digest=_sha256((os.name + ":local-clone").encode()),
            )
            return WorkspaceProvisionResult(
                instance_ref=instance,
                runtime_attachment=derive_runtime_workspace_attachment(instance),
                environment_provenance=environment,
                initial_inspection=inspection,
                property_evidence=evidence,
            )
        except Exception:
            shutil.rmtree(root, ignore_errors=True)
            raise

    def inspect(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceInspection:
        return self._inspect(instance_ref, self._plans.get(instance_ref.workspace_id))

    def _inspect(
        self, instance_ref: WorkspaceInstanceRef, plan: WorkspacePlan | None
    ) -> WorkspaceInspection:
        self._require_instance(instance_ref)
        root = Path(instance_ref.root)
        if not root.is_dir():
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.INSPECTION_FAILED, "workspace root is unavailable"
            )
        try:
            status = self._git(root, "status", "--porcelain=v1", "--untracked-files=all")
            tracked: list[str] = []
            untracked: list[str] = []
            for line in status.splitlines():
                if len(line) < 4:
                    continue
                path = line[3:]
                if line.startswith("??"):
                    untracked.append(path)
                else:
                    tracked.append(path)
            self._git_tree_states(
                str(root),
                instance_ref.source_commit.sha,
                failure_code=WorkspaceProviderErrorCode.INSPECTION_FAILED,
            )
            expected_injected = (
                () if plan is None else tuple(item.path for item in plan.provider_injected_files)
            )
            if plan is not None:
                untracked = [path for path in untracked if path not in expected_injected]
            current_states = self._worktree_states(root)
            injected = tuple(path for path in expected_injected if path in current_states)
            observations: tuple[ProtectedAssetObservation, ...] = ()
            if plan is not None:
                rows: list[ProtectedAssetObservation] = []
                for binding in plan.protected_asset_bindings:
                    rows.append(
                        ProtectedAssetObservation(
                            requirement_ref=binding.requirement_ref,
                            workspace_path=binding.workspace_path,
                            state=current_states.get(binding.workspace_path),
                        )
                    )
                observations = tuple(
                    sorted(
                        rows,
                        key=lambda item: (
                            item.requirement_ref.artifact_id,
                            item.requirement_ref.artifact_content_digest,
                            item.requirement_ref.required_operation.value,
                            item.requirement_ref.requirement_digest,
                            item.workspace_path,
                        ),
                    )
                )
            property_evidence = ()
            if plan is not None:
                subject = WorkspaceEvidenceSubject(
                    plan_ref=instance_ref.plan_ref,
                    instance_ref=instance_ref,
                    provider_ref=instance_ref.provider_ref,
                )
                property_evidence = tuple(
                    WorkspacePropertyEvidence(
                        subject=subject,
                        property_key=requirement.key,
                        property=requirement.property,
                        established_strength=_LOCAL_STRENGTHS[requirement.property],
                        status=RequirementStatus.SATISFIED,
                        evidence_payload_digest=_sha256(
                            (requirement.key + ":local-observed").encode()
                        ),
                    )
                    for requirement in plan.property_requirements
                    if requirement.property in _LOCAL_STRENGTHS
                )
            return WorkspaceInspection(
                instance_ref=instance_ref,
                inspected_at=datetime.now(UTC).isoformat(),
                head_commit=type(instance_ref.source_commit)(
                    repository=instance_ref.repository,
                    sha=self._git(root, "rev-parse", "HEAD").strip(),
                ),
                tracked_changes=tuple(sorted(tracked)),
                untracked_paths=tuple(sorted(untracked)),
                provider_injected_paths=tuple(sorted(injected)),
                protected_asset_observations=observations,
                property_evidence=property_evidence,
            )
        except WorkspaceProviderError:
            raise
        except Exception as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.INSPECTION_FAILED, "workspace inspection failed"
            ) from exc

    def extract_changes(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceChangeManifest:
        self._require_instance(instance_ref)
        try:
            current = self._worktree_states(
                Path(instance_ref.root),
                failure_code=WorkspaceProviderErrorCode.CHANGESET_FAILED,
            )
            return self._change_manifest_from_states(instance_ref, current)
        except WorkspaceProviderError:
            raise
        except Exception as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.CHANGESET_FAILED, "workspace change extraction failed"
            ) from exc

    def capture_candidate(
        self,
        instance_ref: WorkspaceInstanceRef,
        changes: WorkspaceChangeManifest,
    ) -> WorkspaceCandidateCapture:
        """Write a content-addressed tree object without changing the worktree or real index."""

        self._require_instance(instance_ref)
        if changes.instance_ref != instance_ref:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.CHANGESET_FAILED,
                "candidate changes do not bind the exact workspace",
            )
        root = Path(instance_ref.root)
        git_dir = Path(self._git(root, "rev-parse", "--absolute-git-dir").strip())
        descriptor, index_path = tempfile.mkstemp(prefix="relay-candidate-index-", dir=git_dir)
        os.close(descriptor)
        temporary_index = Path(index_path)
        temporary_index.unlink()
        environment = {"GIT_INDEX_FILE": str(temporary_index)}
        try:
            self._git_bytes(root, "read-tree", "HEAD", extra_env=environment)
            self._git_bytes(
                root,
                "add",
                "--all",
                extra_env=environment,
            )
            tree_object_id = (
                self._git_bytes(root, "write-tree", extra_env=environment).decode("ascii").strip()
            )
            captured_states = self._git_tree_states(
                instance_ref.root,
                tree_object_id,
                failure_code=WorkspaceProviderErrorCode.CHANGESET_FAILED,
            )
            captured_manifest = self._change_manifest_from_states(instance_ref, captured_states)
            captured_manifest_digest = digest_workspace_change_manifest(captured_manifest)
            if captured_manifest_digest != digest_workspace_change_manifest(changes):
                raise WorkspaceProviderError(
                    WorkspaceProviderErrorCode.CHANGESET_FAILED,
                    "workspace changed between manifest extraction and candidate capture",
                )
            object_format = self._git(root, "rev-parse", "--show-object-format").strip()
            return WorkspaceCandidateCapture(
                instance_ref=instance_ref,
                source_commit=instance_ref.source_commit,
                git_object_format=object_format,
                tree_object_id=tree_object_id,
                change_manifest_digest=captured_manifest_digest,
                captured_at=datetime.now(UTC).isoformat(),
            )
        except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.CHANGESET_FAILED,
                "immutable candidate tree capture failed",
            ) from exc
        finally:
            temporary_index.unlink(missing_ok=True)
            temporary_index.with_suffix(temporary_index.suffix + ".lock").unlink(missing_ok=True)

    def _change_manifest_from_states(
        self,
        instance_ref: WorkspaceInstanceRef,
        current: dict[str, WorkspaceEntryState],
    ) -> WorkspaceChangeManifest:
        baseline = self._git_tree_states(
            instance_ref.root,
            instance_ref.source_commit.sha,
            failure_code=WorkspaceProviderErrorCode.CHANGESET_FAILED,
        )
        plan = self._plans[instance_ref.workspace_id]
        for requirement in plan.provider_injected_files:
            baseline[requirement.path] = WorkspaceEntryState(
                kind=WorkspaceEntryKind.REGULAR_FILE,
                content_digest=requirement.content_digest,
                symlink_target_digest=None,
                executable=False,
            )
            state = current.get(requirement.path)
            if (
                state is not None
                and state.kind is WorkspaceEntryKind.REGULAR_FILE
                and state.content_digest == requirement.content_digest
                and state.executable is False
            ):
                baseline.pop(requirement.path)
                current.pop(requirement.path)
        paths = sorted(set(baseline) | set(current))
        entries = tuple(
            WorkspaceChangeEntry(path=path, before=baseline.get(path), after=current.get(path))
            for path in paths
            if baseline.get(path) != current.get(path)
        )
        if self._source_snapshot() != self._source_snapshots[instance_ref.workspace_id]:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.CHANGESET_FAILED,
                "source repository changed after provisioning",
            )
        return WorkspaceChangeManifest(
            instance_ref=instance_ref,
            source_commit=instance_ref.source_commit,
            entries=entries,
        )

    def teardown(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceTeardownEvidence:
        self._require_instance(instance_ref)
        plan_ref = instance_ref.plan_ref
        subject = WorkspaceEvidenceSubject(
            plan_ref=plan_ref, instance_ref=instance_ref, provider_ref=instance_ref.provider_ref
        )
        disposition = WorkspaceTerminalDisposition.DELETED
        absence = RequirementStatus.SATISFIED
        retention = self._retention.get(
            instance_ref.workspace_id, WorkspaceRetentionMode.DELETE_ON_TERMINAL
        )
        if retention is not WorkspaceRetentionMode.DELETE_ON_TERMINAL:
            disposition = WorkspaceTerminalDisposition.RETAINED_BY_POLICY
            absence = RequirementStatus.UNSATISFIED
        else:
            shutil.rmtree(instance_ref.root, ignore_errors=False)
        payload = f"{instance_ref.workspace_id}:{disposition.value}".encode()
        return WorkspaceTeardownEvidence(
            subject=subject,
            disposition=disposition,
            credential_cleanup_status=RequirementStatus.SATISFIED,
            workspace_absence_status=absence,
            retained_until=None,
            evidence_payload_digest=_sha256(payload),
        )

    def _require_instance(self, instance_ref: WorkspaceInstanceRef) -> None:
        if self._instances.get(instance_ref.workspace_id) != instance_ref:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.INVALID_PLAN,
                "workspace instance is not owned by this provider",
            )

    def _source_snapshot(self) -> tuple[str, str, str]:
        head = self._git(self._source, "rev-parse", "HEAD").strip()
        status = self._git(self._source, "status", "--porcelain=v1", "--untracked-files=all")
        refs = self._git(self._source, "for-each-ref", "--format=%(refname) %(objectname)")
        return head, status, refs

    @staticmethod
    def _git(cwd: Path, *args: str) -> str:
        env = {
            "PATH": os.environ.get("PATH", ""),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        }
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                check=True,
                text=True,
                encoding="utf-8",
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.ENVIRONMENT_ERROR, "local Git operation failed"
            ) from exc
        return result.stdout

    def _git_tree_states(
        self,
        root: str,
        commit: str,
        *,
        failure_code: WorkspaceProviderErrorCode,
    ) -> dict[str, WorkspaceEntryState]:
        output = self._git_bytes(Path(root), "ls-tree", "-r", "-z", "--full-tree", commit).decode(
            "utf-8", errors="surrogateescape"
        )
        states: dict[str, WorkspaceEntryState] = {}
        for record in output.split("\0"):
            if not record:
                continue
            metadata, path = record.split("\t", 1)
            mode, kind, object_id = metadata.split(" ")
            if (kind, mode) not in {
                ("blob", "100644"),
                ("blob", "100755"),
                ("blob", "120000"),
            }:
                raise WorkspaceProviderError(
                    failure_code,
                    "Git tree contains an unsupported entry kind",
                )
            raw = self._git_bytes(Path(root), "cat-file", "blob", object_id)
            if mode == "120000":
                states[path] = WorkspaceEntryState(
                    kind=WorkspaceEntryKind.SYMLINK,
                    content_digest=None,
                    symlink_target_digest=_sha256(raw),
                    executable=None,
                )
            else:
                states[path] = WorkspaceEntryState(
                    kind=WorkspaceEntryKind.REGULAR_FILE,
                    content_digest=_sha256(raw),
                    symlink_target_digest=None,
                    executable=mode == "100755",
                )
        return states

    @staticmethod
    def _git_bytes(cwd: Path, *args: str, extra_env: dict[str, str] | None = None) -> bytes:
        env = {
            "PATH": os.environ.get("PATH", ""),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        }
        if extra_env is not None:
            env.update(extra_env)
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise WorkspaceProviderError(
                WorkspaceProviderErrorCode.ENVIRONMENT_ERROR, "local Git operation failed"
            ) from exc
        return result.stdout

    @staticmethod
    def _worktree_states(
        root: Path,
        *,
        failure_code: WorkspaceProviderErrorCode = WorkspaceProviderErrorCode.INSPECTION_FAILED,
    ) -> dict[str, WorkspaceEntryState]:
        states: dict[str, WorkspaceEntryState] = {}
        for path in root.rglob("*"):
            if ".git" in path.relative_to(root).parts:
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                target = os.readlink(path).encode("utf-8", errors="surrogateescape")
                states[relative] = WorkspaceEntryState(
                    kind=WorkspaceEntryKind.SYMLINK,
                    content_digest=None,
                    symlink_target_digest=_sha256(target),
                    executable=None,
                )
            else:
                mode = path.lstat().st_mode
                if stat.S_ISDIR(mode):
                    continue
                if not stat.S_ISREG(mode):
                    raise WorkspaceProviderError(
                        failure_code,
                        "worktree contains an unsupported filesystem node",
                    )
                states[relative] = WorkspaceEntryState(
                    kind=WorkspaceEntryKind.REGULAR_FILE,
                    content_digest=_sha256(path.read_bytes()),
                    symlink_target_digest=None,
                    executable=bool(mode & 0o111),
                )
        return states


__all__ = ["LocalCloneWorkspaceProvider"]
