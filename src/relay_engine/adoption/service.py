"""B2 admission, Human decision, fresh-state validation, and adoption planning."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, TextIO, cast
from urllib.parse import unquote, urlsplit

from pydantic import ValidationError

from relay_engine.adoption.models import (
    AdoptionDriftV1,
    AdoptionFingerprintV1,
    AdoptionPlanV1,
    ProjectAdoptionRecordV1,
    build_adoption_record,
    digest_json_value,
    fingerprint_digest,
)
from relay_engine.adoption.persistence import (
    AdoptionPersistenceError,
    publish_adoption_database,
)
from relay_engine.bootstrap_discovery.intake_models import (
    AdoptionManifestV1,
    ConstraintState,
    HumanConfirmedConstraints,
    HumanConfirmedText,
    HumanConfirmedWorkFocusKind,
    ManifestStatus,
    WorkFocusKind,
)
from relay_engine.bootstrap_discovery.intake_service import (
    IntakeError,
    LoadedReport,
    canonical_manifest_bytes,
    load_report,
    parse_manifest,
)
from relay_engine.bootstrap_discovery.local_git import (
    LocalGitError,
    inspect_local_git,
)
from relay_engine.bootstrap_discovery.models import (
    BootstrapDiscoveryReportV1,
    RelayContractStatus,
    canonical_json_bytes,
)
from relay_engine.bootstrap_discovery.service import (
    BootstrapDiscoveryError,
    inspect_repository,
)
from relay_engine.domain import (
    ActorKind,
    ActorRef,
    Baseline,
    CommitRef,
    Project,
    RepositoryRef,
    ScopeSpec,
    Slice,
    new_id,
)
from relay_engine.domain._base import require_repository_relative_path
from relay_engine.project_slice.models import MutationMetadata
from relay_engine.project_slice.origin import (
    AdoptionPreGenesisProjectProofV1,
    NativeRelayOriginProofV1,
    OperationalOrigin,
    OriginRecordKind,
    OriginSubjectType,
    build_project_operational_epoch,
    build_project_operational_origin_record,
    definition_payload_digest,
)

type Clock = Callable[[], datetime]
type InputFunction = Callable[[str], str]


class AdoptionError(RuntimeError):
    """Typed B2 input, decision, provenance, or safety failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def normalize_repository_ref(locator: str, repository_id: str) -> RepositoryRef:
    """Resolve the accepted credential-free B1 repository locator exactly."""

    candidate = locator.strip()
    invalid_locator = "ADOPTION_CANONICAL_REPOSITORY_INVALID"
    if not candidate or candidate.startswith("git@"):
        raise AdoptionError(
            invalid_locator,
            "canonical repository must be a credential-free HTTPS or host/path locator",
        )
    if any(character.isspace() for character in candidate):
        raise AdoptionError(invalid_locator, "canonical repository contains whitespace")
    if "\\" in candidate:
        raise AdoptionError(invalid_locator, "canonical repository contains a backslash")

    scheme_separator = candidate.find(":")
    has_scheme_prefix = (
        scheme_separator > 0
        and re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*", candidate[:scheme_separator]) is not None
    )
    if has_scheme_prefix:
        scheme = candidate[:scheme_separator].lower()
        if scheme != "https" or not candidate[scheme_separator + 1 :].startswith("//"):
            raise AdoptionError(
                invalid_locator,
                "canonical repository must use HTTPS or the host/path form",
            )
        try:
            parsed = urlsplit(candidate)
            parsed_host = parsed.hostname
            parsed_port = parsed.port
        except ValueError as error:
            raise AdoptionError(
                invalid_locator, "canonical repository HTTPS authority is malformed"
            ) from error
        if (
            parsed.scheme.lower() != "https"
            or not parsed_host
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or parsed_port is not None
            or parsed.netloc.endswith(":")
        ):
            raise AdoptionError(
                invalid_locator,
                "canonical repository URI must use HTTPS without credentials, "
                "port, query, or fragment",
            )
        host = parsed_host.lower()
        path = parsed.path.lstrip("/")
    else:
        if any(character in candidate for character in ("?", "#", "@")):
            raise AdoptionError(
                invalid_locator,
                "canonical repository locator is unsupported",
            )
        host, separator, path = candidate.partition("/")
        if not separator:
            raise AdoptionError(invalid_locator, "canonical repository path is missing")
        if any(character in host for character in (":", "[", "]")):
            raise AdoptionError(
                invalid_locator,
                "bare canonical repository authority must be a host name without a port",
            )
        host = host.lower()
    path = path.removesuffix(".git")
    decoded_segments = tuple(unquote(segment) for segment in path.split("/"))
    if (
        not host
        or not path
        or any(segment in {"", ".", ".."} for segment in decoded_segments)
        or any("/" in segment or "\\" in segment for segment in decoded_segments)
    ):
        raise AdoptionError(
            invalid_locator,
            "canonical repository host/path is incomplete or unsafe",
        )
    try:
        safe_path = require_repository_relative_path(path)
        return RepositoryRef(id=repository_id, host=host, path=safe_path)
    except (ValidationError, ValueError) as error:
        raise AdoptionError(
            invalid_locator,
            "canonical repository cannot be represented as a RepositoryRef",
        ) from error


def _read_external_input(path: Path, label: str, repository_root: Path) -> bytes:
    requested = path.expanduser().absolute()
    try:
        resolved_parent = requested.parent.resolve(strict=True)
        resolved = resolved_parent / requested.name
        resolved.relative_to(repository_root.resolve(strict=True))
    except ValueError:
        pass
    except (OSError, RuntimeError) as error:
        raise AdoptionError("ADOPTION_MANIFEST_INVALID", f"{label} path is unavailable") from error
    else:
        raise AdoptionError(
            "ADOPTION_MANIFEST_INVALID", f"{label} must be outside the target repository"
        )
    try:
        descriptor = os.open(requested, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as error:
        raise AdoptionError(
            "ADOPTION_MANIFEST_INVALID", f"{label} cannot be read safely"
        ) from error
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise AdoptionError("ADOPTION_MANIFEST_INVALID", f"{label} must be a regular file")
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _human_text(manifest: AdoptionManifestV1, field_name: str) -> str:
    fact = getattr(manifest.human_facts, field_name)
    if not isinstance(fact, HumanConfirmedText):
        raise AdoptionError(
            "ADOPTION_MANIFEST_NOT_READY", f"manifest field {field_name} is not Human-confirmed"
        )
    return fact.value


def _report_state_tree(report: BootstrapDiscoveryReportV1) -> dict[str, Any]:
    value = report.model_dump(mode="json")
    value["observation"].pop("observed_at")
    return value


def report_state_digest(report: BootstrapDiscoveryReportV1) -> str:
    """Hash a canonical report while excluding only its observation timestamp."""

    return digest_json_value(_report_state_tree(report))


def _fingerprint(report: BootstrapDiscoveryReportV1) -> AdoptionFingerprintV1:
    return AdoptionFingerprintV1(
        repository_root=report.observation.repository_path,
        head_sha=report.git.head_sha,
        branch=report.git.branch,
        detached_head=report.git.detached_head,
        dirty=report.git.dirty,
        tracked_file_count=report.git.tracked_file_count,
        remotes=report.git.remotes,
        relay_contract=report.relay_contract,
    )


def _changed_leaf_count(before: Any, after: Any) -> int:
    if type(before) is not type(after):
        return 1
    if isinstance(before, dict):
        before_dict = cast(dict[str, Any], before)
        after_dict = cast(dict[str, Any], after)
        return sum(
            _changed_leaf_count(before_dict[key], after_dict[key])
            if key in before_dict and key in after_dict
            else 1
            for key in sorted(before_dict.keys() | after_dict.keys())
        )
    if isinstance(before, list):
        before_list = cast(list[Any], before)
        after_list = cast(list[Any], after)
        shared = min(len(before_list), len(after_list))
        changes = sum(
            _changed_leaf_count(before_list[index], after_list[index]) for index in range(shared)
        )
        return changes + abs(len(before_list) - len(after_list))
    return 0 if before == after else 1


def _drift_entries(
    original: dict[str, Any], fresh: BootstrapDiscoveryReportV1
) -> tuple[AdoptionDriftV1, ...]:
    before_tree = dict(original)
    after_tree = fresh.model_dump(mode="json")
    before_observation = dict(cast(dict[str, Any], before_tree["observation"]))
    after_observation = dict(cast(dict[str, Any], after_tree["observation"]))
    before_observation.pop("observed_at", None)
    after_observation.pop("observed_at", None)
    before_tree["observation"] = before_observation
    after_tree["observation"] = after_observation
    entries: list[AdoptionDriftV1] = []
    for key in sorted(before_tree.keys() | after_tree.keys()):
        before = before_tree.get(key)
        after = after_tree.get(key)
        changed = _changed_leaf_count(before, after)
        if changed:
            entries.append(
                AdoptionDriftV1(
                    pointer=f"/{key}",
                    before_sha256=digest_json_value(before),
                    after_sha256=digest_json_value(after),
                    changed_item_count=changed,
                )
            )
    return tuple(entries)


def prepare_adoption_plan(
    *,
    repository: Path,
    report_path: Path,
    manifest_path: Path,
    database_path: Path,
    observed_at: datetime,
) -> tuple[AdoptionPlanV1, AdoptionManifestV1, LoadedReport, BootstrapDiscoveryReportV1, Path]:
    """Validate B1 inputs, re-observe a clean checkout, and prepare the exact plan."""

    try:
        loaded = load_report(report_path, repository)
        raw_manifest = _read_external_input(manifest_path, "manifest", loaded.repository_root)
        manifest = parse_manifest(raw_manifest, loaded)
    except IntakeError as error:
        code = (
            "ADOPTION_REPORT_MISMATCH"
            if error.code.startswith("REPORT") or error.code.startswith("CONTEXT")
            else "ADOPTION_MANIFEST_INVALID"
        )
        if error.code == "REPORT_REPOSITORY_MISMATCH":
            code = "ADOPTION_REPOSITORY_MISMATCH"
        raise AdoptionError(code, str(error)) from error
    if manifest.preparation_status is not ManifestStatus.READY_FOR_B2_REVIEW:
        raise AdoptionError("ADOPTION_MANIFEST_NOT_READY", "B1 manifest is not READY_FOR_B2_REVIEW")
    try:
        canonical_manifest_bytes(manifest, loaded)
    except IntakeError as error:
        raise AdoptionError("ADOPTION_MANIFEST_INVALID", str(error)) from error

    root = loaded.repository_root
    output_database = _validate_database_target_path(database_path, root)
    timestamp = _normalize_time(observed_at)
    try:
        fresh = inspect_repository(root, timestamp)
    except (BootstrapDiscoveryError, LocalGitError) as error:
        code = getattr(error, "code", "ADOPTION_REPOSITORY_MISMATCH")
        raise AdoptionError(code, "fresh read-only repository inspection failed") from error
    if Path(fresh.observation.repository_path).resolve(strict=True) != root:
        raise AdoptionError(
            "ADOPTION_REPOSITORY_MISMATCH", "fresh observation resolved a different repository root"
        )
    if fresh.git.dirty:
        raise AdoptionError("ADOPTION_REPOSITORY_DIRTY", "target repository must be clean")
    if fresh.relay_contract.status is RelayContractStatus.INVALID:
        raise AdoptionError("ADOPTION_RELAY_CONTRACT_INVALID", "local Relay contract is invalid")

    locator = _human_text(manifest, "canonical_repository")
    contract = fresh.relay_contract
    selected_repository_id = (
        contract.repository.id
        if contract.status is RelayContractStatus.VALID and contract.repository is not None
        else new_id("repo_")
    )
    repository_ref = normalize_repository_ref(locator, selected_repository_id)
    if (
        contract.status is RelayContractStatus.VALID
        and contract.project_id is not None
        and contract.repository is not None
    ):
        observed_repository = contract.repository
        if (
            observed_repository.host.lower(),
            observed_repository.path,
        ) != (repository_ref.host, repository_ref.path):
            raise AdoptionError(
                "ADOPTION_IDENTITY_CONFLICT",
                "Human-confirmed canonical repository conflicts with the valid local "
                "Relay contract",
            )
        repository_ref = observed_repository
        project_id = contract.project_id
    else:
        project_id = new_id("prj_")

    fingerprint = _fingerprint(fresh)
    original_value = loaded.value
    plan = AdoptionPlanV1(
        manifest_sha256="sha256:" + hashlib.sha256(raw_manifest).hexdigest(),
        input_report_sha256=loaded.sha256,
        fresh_report_sha256="sha256:" + hashlib.sha256(canonical_json_bytes(fresh)).hexdigest(),
        fresh_report_state_sha256=report_state_digest(fresh),
        fresh_repository_fingerprint_sha256=fingerprint_digest(fingerprint),
        fresh_fingerprint=fingerprint,
        repository=repository_ref,
        project_id=project_id,
        baseline_id=new_id("base_"),
        initial_slice_id=new_id("slc_"),
        adoption_id=new_id("adopt_"),
        epoch_id=new_id("ohe_"),
        project_name=_human_text(manifest, "project_name"),
        project_objective=_human_text(manifest, "project_objective"),
        current_status=_human_text(manifest, "current_status"),
        human_objective=_human_text(manifest, "human_objective"),
        constraints=_confirmed_constraints(manifest),
        work_focus_kind=_confirmed_focus_kind(manifest),
        work_focus=_human_text(manifest, "work_focus"),
        context_references=manifest.context_references,
        drift=_drift_entries(original_value, fresh),
    )
    if plan.fresh_fingerprint.dirty:
        raise AdoptionError("ADOPTION_REPOSITORY_DIRTY", "target repository must be clean")
    return plan, manifest, loaded, fresh, output_database


def adopt_project(
    *,
    repository: Path,
    report_path: Path,
    manifest_path: Path,
    database_path: Path,
    input_fn: InputFunction,
    output: TextIO,
    clock: Clock,
    allow_test_injected_input: bool = False,
) -> ProjectAdoptionRecordV1:
    """Run an exact Human ADOPT decision and publish one disposable-compatible DB."""

    if not allow_test_injected_input and not _stdin_is_interactive():
        raise AdoptionError(
            "ADOPTION_NOT_CONFIRMED", "B2 adoption requires an interactive Human decision"
        )
    plan, _manifest, loaded, fresh, output_database = prepare_adoption_plan(
        repository=repository,
        report_path=report_path,
        manifest_path=manifest_path,
        database_path=database_path,
        observed_at=clock(),
    )
    _print_plan(plan, fresh, output)
    try:
        display_name = input_fn("Human adopter display name for the audit record: ")
    except (EOFError, KeyboardInterrupt) as error:
        raise AdoptionError(
            "ADOPTION_NOT_CONFIRMED", "Human input ended before adoption"
        ) from error
    display_name = display_name.strip()
    if not display_name:
        raise AdoptionError("ADOPTION_NOT_CONFIRMED", "Human actor display name is required")
    output.write(
        "\nI attest that the software project represented by "
        f"{plan.repository.host}/{plan.repository.path}, identified by fresh B0-F report "
        f"SHA-256 {plan.fresh_report_sha256}, existed as a project before this ADOPT decision. "
        "This attestation establishes no pre-T1 Relay lifecycle or other Relay-governed history.\n"
    )
    try:
        confirmation = input_fn("Type exactly ADOPT to confirm this plan and attestation: ")
    except (EOFError, KeyboardInterrupt) as error:
        raise AdoptionError(
            "ADOPTION_NOT_CONFIRMED", "Human input ended before adoption"
        ) from error
    if confirmation != "ADOPT":
        raise AdoptionError("ADOPTION_NOT_CONFIRMED", "exact ADOPT confirmation was not supplied")

    t1 = _normalize_time(clock())
    actor = ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN, display_name=display_name)
    try:
        post = inspect_repository(Path(fresh.observation.repository_path), _normalize_time(clock()))
    except (BootstrapDiscoveryError, LocalGitError) as error:
        raise AdoptionError(
            "ADOPTION_STATE_CHANGED", "repository could not be re-observed after ADOPT"
        ) from error
    post_raw = canonical_json_bytes(post)
    post_digest = "sha256:" + hashlib.sha256(post_raw).hexdigest()
    post_state_digest = report_state_digest(post)
    post_fingerprint_digest = fingerprint_digest(_fingerprint(post))
    if (
        post_fingerprint_digest != plan.fresh_repository_fingerprint_sha256
        or post_state_digest != plan.fresh_report_state_sha256
    ):
        raise AdoptionError(
            "ADOPTION_STATE_CHANGED",
            "complete post-ADOPT repository observation differs from the reviewed plan",
        )

    if plan.fresh_report_sha256 != (
        "sha256:" + hashlib.sha256(canonical_json_bytes(fresh)).hexdigest()
    ):
        raise AdoptionError(
            "ADOPTION_REPORT_MISMATCH", "reviewed fresh report bytes changed before materialization"
        )
    project = Project(
        id=plan.project_id,
        name=plan.project_name,
        primary_repository=plan.repository,
    )
    baseline = Baseline(
        id=plan.baseline_id,
        project_id=plan.project_id,
        commit=CommitRef(repository=plan.repository, sha=fresh.git.head_sha),
        artifact_ids=(),
        decision_ids=(),
    )
    initial_slice = Slice(
        id=plan.initial_slice_id,
        project_id=plan.project_id,
        title=plan.work_focus,
        scope=ScopeSpec(in_scope=(plan.work_focus,), out_of_scope=()),
        acceptance_criteria=(),
        parent_slice_id=None,
        dependency_ids=(),
    )
    attestation = (
        f"I attest that the software project represented by {plan.repository.host}/"
        f"{plan.repository.path}, identified by fresh B0-F report SHA-256 "
        f"{plan.fresh_report_sha256}, existed as a project before this ADOPT decision. "
        "This attestation establishes no pre-T1 Relay lifecycle or other Relay-governed history."
    )
    adoption = build_adoption_record(
        adoption_id=plan.adoption_id,
        project_id=plan.project_id,
        repository_id=plan.repository.id,
        repository=plan.repository,
        t1=t1,
        human_actor=actor,
        manifest_sha256=plan.manifest_sha256,
        input_report_sha256=plan.input_report_sha256,
        fresh_report_sha256=plan.fresh_report_sha256,
        fresh_report_state_sha256=plan.fresh_report_state_sha256,
        fresh_repository_fingerprint=plan.fresh_fingerprint,
        fresh_repository_fingerprint_sha256=plan.fresh_repository_fingerprint_sha256,
        post_adopt_report_sha256=post_digest,
        post_adopt_report_state_sha256=post_state_digest,
        post_adopt_fingerprint_sha256=post_fingerprint_digest,
        baseline_id=plan.baseline_id,
        initial_slice_id=plan.initial_slice_id,
        project_name=plan.project_name,
        project_objective=plan.project_objective,
        current_status=plan.current_status,
        human_objective=plan.human_objective,
        constraints=plan.constraints,
        work_focus_kind=plan.work_focus_kind,
        work_focus=plan.work_focus,
        context_references=plan.context_references,
        drift=plan.drift,
        attestation_id="B2_PRE_T1_EXISTENCE_ATTESTATION_V1",
        attestation_statement=attestation,
        recorded_at=t1,
    )
    epoch = build_project_operational_epoch(
        project_id=project.id,
        epoch_id=plan.epoch_id,
        genesis_cut_at=t1,
        basis_kind="EXISTING_PROJECT_ADOPTION",
        adoption_id=adoption.adoption_id,
        adoption_record_digest=adoption.record_digest,
        recorded_at=t1,
    )
    project_proof = AdoptionPreGenesisProjectProofV1(
        proof_type="ADOPTION_PRE_GENESIS_PROJECT",
        project_id=project.id,
        repository=project.primary_repository,
        adoption_id=adoption.adoption_id,
        adoption_record_digest=adoption.record_digest,
        manifest_sha256=adoption.manifest_sha256,
        input_report_sha256=adoption.input_report_sha256,
        fresh_report_sha256=adoption.fresh_report_sha256,
        fresh_report_state_sha256=adoption.fresh_report_state_sha256,
        fresh_repository_fingerprint_sha256=adoption.fresh_repository_fingerprint_sha256,
        repository_root=adoption.fresh_repository_fingerprint.repository_root,
        relay_contract_status=cast(
            Literal["ABSENT", "VALID"],
            adoption.fresh_repository_fingerprint.relay_contract.status.value,
        ),
        fresh_head=baseline.commit,
        attestation_id=adoption.attestation_id,
        assertion="REPRESENTED_PROJECT_EXISTED_BEFORE_T1",
        actor=actor,
        decided_at=t1,
    )
    project_origin = build_project_operational_origin_record(
        record_id=new_id("oor_"),
        subject_type=OriginSubjectType.PROJECT,
        subject_id=project.id,
        project_id=project.id,
        record_kind=OriginRecordKind.INITIAL,
        origin=OperationalOrigin.PRE_GENESIS,
        epoch_id=epoch.epoch_id,
        epoch_digest=epoch.epoch_digest,
        proof=project_proof,
        recorded_at=t1,
        recorded_by=actor,
        establishing_authority_id=adoption.adoption_id,
    )
    slice_created_at = _normalize_time(clock())
    if slice_created_at <= t1:
        raise AdoptionError(
            "ADOPTION_MATERIALIZATION_FAILED",
            "clock did not advance beyond T1 for the new Relay Slice identity",
        )
    project_mutation = MutationMetadata(
        actor=actor,
        occurred_at=t1,
        reason="Project established by explicit B2 Human adoption at T1.",
    )
    slice_mutation = MutationMetadata(
        actor=actor,
        occurred_at=slice_created_at,
        reason="Initial adoption-frontier Slice created after Project T1.",
    )
    slice_proof = NativeRelayOriginProofV1(
        proof_type="NATIVE_RELAY",
        subject_type=OriginSubjectType.SLICE,
        subject_id=initial_slice.id,
        definition_revision=1,
        operation="CREATE",
        creation_payload_digest=definition_payload_digest(initial_slice),
        actor=actor,
        created_at=slice_created_at,
        reason=slice_mutation.reason,
    )
    slice_origin = build_project_operational_origin_record(
        record_id=new_id("oor_"),
        subject_type=OriginSubjectType.SLICE,
        subject_id=initial_slice.id,
        project_id=project.id,
        record_kind=OriginRecordKind.INITIAL,
        origin=OperationalOrigin.NATIVE_RELAY,
        epoch_id=epoch.epoch_id,
        epoch_digest=epoch.epoch_digest,
        proof=slice_proof,
        recorded_at=slice_created_at,
        recorded_by=actor,
        establishing_authority_id=f"slice_definition_revisions/{initial_slice.id}/1",
    )

    try:
        publish_adoption_database(
            database_path=output_database,
            repository_root=loaded.repository_root,
            project=project,
            baseline=baseline,
            initial_slice=initial_slice,
            project_mutation=project_mutation,
            slice_mutation=slice_mutation,
            adoption=adoption,
            epoch=epoch,
            project_origin=project_origin,
            slice_origin=slice_origin,
            migration_applied_at=_normalize_time(clock()),
            final_repository_check=lambda: _final_repository_check(
                Path(fresh.observation.repository_path), fresh
            ),
        )
    except AdoptionPersistenceError as error:
        raise AdoptionError(error.code, str(error)) from error
    return adoption


def _final_repository_check(repository_root: Path, reviewed: BootstrapDiscoveryReportV1) -> bool:
    try:
        state = inspect_local_git(repository_root)
    except LocalGitError:
        return False
    try:
        same_root = state.repository_root.resolve(strict=True) == Path(
            reviewed.observation.repository_path
        ).resolve(strict=True)
    except OSError, RuntimeError:
        return False
    return same_root and state.head_sha == reviewed.git.head_sha and not state.dirty


def _validate_database_target_path(database_path: Path, repository_root: Path) -> Path:
    requested = database_path.expanduser().absolute()
    try:
        parent = requested.parent.resolve(strict=True)
        root = repository_root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AdoptionError(
            "ADOPTION_DATABASE_UNSAFE", "database parent must already exist and be resolvable"
        ) from error
    target = parent / requested.name
    try:
        target.relative_to(root)
    except ValueError:
        pass
    else:
        raise AdoptionError(
            "ADOPTION_DATABASE_UNSAFE", "database must be outside the inspected repository"
        )
    if target.is_symlink():
        raise AdoptionError("ADOPTION_DATABASE_UNSAFE", "database target is a symlink")
    if target.exists():
        raise AdoptionError("ADOPTION_DATABASE_EXISTS", "database target already exists")
    if any(Path(str(target) + suffix).exists() for suffix in ("-wal", "-shm", "-journal")):
        raise AdoptionError(
            "ADOPTION_DATABASE_UNSAFE", "database target has a pre-existing SQLite sidecar"
        )
    return target


def _confirmed_constraints(manifest: AdoptionManifestV1):
    value = manifest.human_facts.constraints
    if not isinstance(value, HumanConfirmedConstraints):
        raise AdoptionError("ADOPTION_MANIFEST_NOT_READY", "constraints are unresolved")
    return value.value


def _confirmed_focus_kind(manifest: AdoptionManifestV1) -> WorkFocusKind:
    value = manifest.human_facts.work_focus_kind
    if not isinstance(value, HumanConfirmedWorkFocusKind):
        raise AdoptionError("ADOPTION_MANIFEST_NOT_READY", "work focus kind is unresolved")
    return value.value


def _print_plan(
    plan: AdoptionPlanV1,
    report: BootstrapDiscoveryReportV1,
    output: TextIO,
) -> None:
    output.write("B2 adoption plan\n")
    output.write(f"Project: {plan.project_name} ({plan.project_id})\n")
    output.write(f"Canonical repository: {plan.repository.host}/{plan.repository.path}\n")
    output.write(f"Proposed Baseline: {plan.baseline_id}\n")
    output.write(f"Proposed initial Slice: {plan.initial_slice_id}\n")
    output.write(f"Project objective: {plan.project_objective}\n")
    output.write(f"Human-confirmed current status: {plan.current_status}\n")
    output.write(f"Next-period Human objective: {plan.human_objective}\n")
    if plan.constraints.state is ConstraintState.EXPLICIT_NONE:
        output.write("Human-confirmed constraints: explicitly none\n")
    else:
        output.write("Human-confirmed constraints:\n")
        for constraint in plan.constraints.items:
            output.write(f"  - {constraint}\n")
    output.write(f"First governed focus kind: {plan.work_focus_kind.value}\n")
    output.write(f"First governed focus: {plan.work_focus}\n")
    output.write("Selected legacy context:\n")
    if plan.context_references:
        for reference in plan.context_references:
            output.write(
                f"  {reference.relative_path} — {reference.sha256} "
                f"({reference.inspection_state.value})\n"
            )
    else:
        output.write("  (none selected)\n")
    output.write("Fresh B0-F observation:\n")
    output.write(f"Fresh HEAD: {plan.fresh_fingerprint.head_sha}\n")
    output.write(
        f"Working tree: {'dirty' if plan.fresh_fingerprint.dirty else 'clean'}; "
        f"branch: {plan.fresh_fingerprint.branch or '(detached)'}\n"
    )
    if plan.fresh_fingerprint.remotes:
        output.write("Remotes (observed, not canonical):\n")
        for remote in plan.fresh_fingerprint.remotes:
            output.write(f"  {remote.name}: {remote.fetch_url or '(unavailable)'}\n")
    else:
        output.write("Remotes: none configured\n")
    contract = plan.fresh_fingerprint.relay_contract
    output.write(f"Relay contract: {contract.status.value}\n")
    if (
        contract.status is RelayContractStatus.VALID
        and contract.project_id is not None
        and contract.repository is not None
    ):
        output.write(
            f"  observed Project: {contract.project_id}; "
            f"RepositoryRef: {contract.repository.host}/{contract.repository.path}\n"
        )
    output.write("Manifest signals:\n")
    for signal in report.manifests:
        output.write(f"  {signal.ecosystem.value}: {signal.evidence.relative_path}\n")
    if not report.manifests:
        output.write("  (none)\n")
    output.write("Language signals:\n")
    for signal in report.language_signals:
        output.write(
            f"  {signal.language.value}: {signal.tracked_file_count} tracked source file(s)\n"
        )
    if not report.language_signals:
        output.write("  (none)\n")
    output.write("CI configuration:\n")
    for evidence in report.ci_files:
        output.write(f"  {evidence.relative_path}\n")
    if not report.ci_files:
        output.write("  (none)\n")
    documentation_count = len(report.documentation_files)
    output.write(f"Documentation signals: {documentation_count} tracked file(s)\n")
    for evidence in report.documentation_files[:5]:
        output.write(f"  {evidence.relative_path}\n")
    if documentation_count > 5:
        output.write(f"  ... {documentation_count - 5} more; all are bound by the fresh report\n")
    if report.observation.diagnostics:
        output.write("Fresh observation diagnostics:\n")
        for diagnostic in report.observation.diagnostics:
            location = "" if diagnostic.path is None else f" ({diagnostic.path})"
            output.write(f"  {diagnostic.code.value}{location}: {diagnostic.message}\n")
    output.write(f"Fresh report state SHA-256: {plan.fresh_report_state_sha256}\n")
    output.write(f"Fresh report SHA-256: {plan.fresh_report_sha256}\n")
    output.write(
        f"Reviewed repository fingerprint SHA-256: {plan.fresh_repository_fingerprint_sha256}\n"
    )
    output.write("Proposed T1: actual time of Human ADOPT decision\n")
    if not plan.drift:
        output.write("Drift from the B1 observation: none outside observed_at.\n")
    else:
        output.write("Drift from the B1 observation (all changed report sections):\n")
        for item in plan.drift:
            output.write(
                f"  {item.pointer}: {item.changed_item_count} changed value(s); "
                f"{item.before_sha256[:19]} -> {item.after_sha256[:19]}\n"
            )


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AdoptionError("ADOPTION_MATERIALIZATION_FAILED", "timestamp must be timezone-aware")
    return value.astimezone(UTC)


def _stdin_is_interactive() -> bool:
    import sys

    return bool(sys.stdin.isatty())


__all__ = [
    "AdoptionError",
    "adopt_project",
    "normalize_repository_ref",
    "prepare_adoption_plan",
    "report_state_digest",
]
