"""Regression coverage for Relay's repository-side registry contract."""

import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from relay_engine.domain import Artifact, CommitRef, ProjectId, RepositoryRef
from relay_engine.repository_contract import (
    ArtifactIntegrityError,
    ArtifactRevisionRef,
    CanonicalPointer,
    CanonicalResolutionError,
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryContractInvalid,
    RepositoryRegistry,
    ResolvedRepositoryArtifact,
    parse_repository_registry,
    resolve_artifact_revision,
    resolve_canonical_artifact,
    serialize_repository_registry,
    validate_registry_transition,
    validate_repository_contract,
)

PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="github.com",
    path="cschrupp/relay",
)
OTHER_REPOSITORY_SAME_ID = RepositoryRef(
    id=REPOSITORY.id,
    host="git.example.com",
    path="other/relay",
)
UPDATED_AT = datetime(2026, 9, 26, tzinfo=UTC)


def _artifact(
    path: str,
    raw: bytes = b"registered bytes\n",
    *,
    number: int = 1,
    revision: int = 1,
    artifact_class: RepositoryArtifactClass = RepositoryArtifactClass.LIVING_PROJECTION,
    state: RepositoryArtifactState = RepositoryArtifactState.CURRENT,
    supersedes: ArtifactRevisionRef | None = None,
    superseded_by: ArtifactRevisionRef | None = None,
    title: str | None = None,
    digest: str | None = None,
) -> RepositoryArtifactRevision:
    return RepositoryArtifactRevision(
        artifact_id=f"art_018f47c1-7b2c-7abc-8def-123456789{number:03d}",
        revision=revision,
        title=title or f"Artifact {number}",
        artifact_type="DOCUMENT",
        artifact_class=artifact_class,
        artifact_state=state,
        path=path,
        content_digest=digest or f"sha256:{sha256(raw).hexdigest()}",
        human_version=None,
        updated_at=UPDATED_AT,
        scope="Repository contract test artifact",
        supersedes=supersedes,
        superseded_by=superseded_by,
    )


def _ref(artifact: RepositoryArtifactRevision) -> ArtifactRevisionRef:
    return ArtifactRevisionRef(artifact_id=artifact.artifact_id, revision=artifact.revision)


def _registry(
    artifacts: tuple[RepositoryArtifactRevision, ...],
    canonical: tuple[CanonicalPointer, ...] = (),
    *,
    repository: RepositoryRef = REPOSITORY,
) -> RepositoryRegistry:
    return RepositoryRegistry(
        schema_version=1,
        project_id=PROJECT_ID,
        repository=repository,
        artifacts=tuple(sorted(artifacts, key=lambda item: (item.path, item.artifact_id))),
        canonical=tuple(sorted(canonical, key=lambda item: item.canonical_key)),
    )


def _living_registry(
    *,
    artifact_id_number: int = 1,
    revision: int = 1,
    digest: str | None = None,
    path: str = "docs/current.md",
    raw: bytes = b"registered bytes\n",
    key: str = "current-doc",
    repository: RepositoryRef = REPOSITORY,
) -> RepositoryRegistry:
    artifact = _artifact(
        path,
        raw,
        number=artifact_id_number,
        revision=revision,
        digest=digest,
    )
    return _registry(
        (artifact,),
        (CanonicalPointer(canonical_key=key, target=_ref(artifact)),),
        repository=repository,
    )


def _write_registered_file(root: Path, artifact: RepositoryArtifactRevision, raw: bytes) -> None:
    target = root / artifact.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def _write_contract(root: Path, registry: RepositoryRegistry) -> None:
    relay_dir = root / ".relay"
    relay_dir.mkdir(exist_ok=True)
    (relay_dir / "registry.json").write_bytes(serialize_repository_registry(registry))


def test_registry_round_trip_and_deterministic_serialization() -> None:
    registry = _living_registry()
    serialized = serialize_repository_registry(registry)
    assert parse_repository_registry(serialized) == registry
    assert serialize_repository_registry(parse_repository_registry(serialized)) == serialized


def test_registry_rejects_duplicate_json_key() -> None:
    serialized = serialize_repository_registry(_living_registry())
    duplicate = serialized.replace(b"{", b'{"schema_version":1,', 1)
    with pytest.raises(RepositoryContractInvalid, match="duplicate JSON object key"):
        parse_repository_registry(duplicate)


def test_registry_rejects_unknown_schema_and_extra_fields() -> None:
    payload = json.loads(serialize_repository_registry(_living_registry()))
    payload["schema_version"] = 2
    with pytest.raises(RepositoryContractInvalid):
        parse_repository_registry(json.dumps(payload).encode())
    payload["schema_version"] = 1
    payload["surprise"] = True
    with pytest.raises(RepositoryContractInvalid):
        parse_repository_registry(json.dumps(payload).encode())


def test_registry_rejects_wrong_project_identity(tmp_path: Path) -> None:
    artifact = _artifact("docs/current.md")
    _write_contract(tmp_path, _registry((artifact,)))
    _write_registered_file(tmp_path, artifact, b"registered bytes\n")
    with pytest.raises(RepositoryContractInvalid, match="project identity"):
        validate_repository_contract(
            tmp_path,
            cast(ProjectId, "prj_018f47c1-7b2c-7abc-8def-123456789009"),
            REPOSITORY,
        )


def test_registry_rejects_repositoryref_mismatch_with_same_repository_id(
    tmp_path: Path,
) -> None:
    artifact = _artifact("docs/current.md")
    bad_registry = _registry((artifact,), repository=OTHER_REPOSITORY_SAME_ID)
    _write_contract(tmp_path, bad_registry)
    _write_registered_file(tmp_path, artifact, b"registered bytes\n")
    with pytest.raises(RepositoryContractInvalid, match="RepositoryRef"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)
    assert bad_registry.repository.id == REPOSITORY.id
    assert bad_registry.repository != REPOSITORY


def test_registry_rejects_noncanonical_artifact_order() -> None:
    first = _artifact("a.md", number=1)
    second = _artifact("b.md", number=2)
    with pytest.raises(ValidationError, match="artifacts must use normative"):
        RepositoryRegistry(
            project_id=PROJECT_ID,
            repository=REPOSITORY,
            artifacts=(second, first),
            canonical=(),
        )


def test_registry_rejects_noncanonical_canonical_order() -> None:
    first = _artifact("a.md", number=1)
    second = _artifact("b.md", number=2)
    with pytest.raises(ValidationError, match="canonical pointers must use"):
        RepositoryRegistry(
            project_id=PROJECT_ID,
            repository=REPOSITORY,
            artifacts=(first, second),
            canonical=(
                CanonicalPointer(canonical_key="z-key", target=_ref(second)),
                CanonicalPointer(canonical_key="a-key", target=_ref(first)),
            ),
        )


def test_registry_rejects_duplicate_artifact_ids_and_paths() -> None:
    first = _artifact("docs/first.md", number=1)
    same_id = _artifact("docs/second.md", number=1)
    same_path = _artifact("docs/first.md", number=2)
    with pytest.raises(ValidationError, match="artifact IDs must be unique"):
        _registry((first, same_id))
    with pytest.raises(ValidationError, match="artifact paths must be unique"):
        _registry((first, same_path))


def test_registry_rejects_invalid_artifact_class_state_pair() -> None:
    with pytest.raises(ValidationError, match="state is not valid for its class"):
        _artifact(
            "docs/draft.md",
            artifact_class=RepositoryArtifactClass.LIVING_PROJECTION,
            state=RepositoryArtifactState.DRAFT,
        )


def test_registry_rejects_broken_canonical_pointer() -> None:
    artifact = _artifact("docs/current.md")
    wrong_revision = ArtifactRevisionRef(artifact_id=artifact.artifact_id, revision=2)
    with pytest.raises(ValidationError, match="exact registered revision"):
        _registry(
            (artifact,), (CanonicalPointer(canonical_key="current-doc", target=wrong_revision),)
        )


def test_registry_rejects_noncurrent_canonical_target() -> None:
    draft = _artifact(
        "docs/draft.md",
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.DRAFT,
    )
    with pytest.raises(ValidationError, match="canonical pointer target must be"):
        _registry((draft,), (CanonicalPointer(canonical_key="draft-doc", target=_ref(draft)),))


def test_contract_rejects_symlink_artifact(tmp_path: Path) -> None:
    target = tmp_path / "real.md"
    target.write_bytes(b"registered bytes\n")
    link = tmp_path / "linked.md"
    link.symlink_to(target)
    artifact = _artifact("linked.md")
    _write_contract(tmp_path, _registry((artifact,)))
    with pytest.raises(ArtifactIntegrityError, match="symlink"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)


def test_contract_rejects_symlinked_parent_directory(tmp_path: Path) -> None:
    external = tmp_path / "external"
    external.mkdir()
    (external / "current.md").write_bytes(b"registered bytes\n")
    (tmp_path / "docs").symlink_to(external, target_is_directory=True)
    artifact = _artifact("docs/current.md")
    _write_contract(tmp_path, _registry((artifact,)))
    with pytest.raises(ArtifactIntegrityError, match="symlink"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)


def test_contract_rejects_path_escape_and_missing_artifact(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        _artifact("../outside.md")
    missing = _artifact("missing.md")
    _write_contract(tmp_path, _registry((missing,)))
    with pytest.raises(ArtifactIntegrityError, match="missing"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)


def test_contract_rejects_digest_mismatch(tmp_path: Path) -> None:
    artifact = _artifact("docs/current.md", digest=f"sha256:{'0' * 64}")
    _write_registered_file(tmp_path, artifact, b"different bytes\n")
    _write_contract(tmp_path, _registry((artifact,)))
    with pytest.raises(ArtifactIntegrityError, match="digest mismatch"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)


def test_contract_rejects_unknown_dot_relay_entry(tmp_path: Path) -> None:
    _write_contract(tmp_path, _living_registry())
    (tmp_path / ".relay" / "notes.txt").write_text("unexpected", encoding="utf-8")
    with pytest.raises(RepositoryContractInvalid, match="only .relay/registry.json"):
        validate_repository_contract(tmp_path, PROJECT_ID, REPOSITORY)


def test_registry_rejects_self_registration() -> None:
    with pytest.raises(ValidationError, match="registry cannot register itself"):
        _artifact(".relay/registry.json")


def test_resolution_exposes_observation_commit_explicitly(tmp_path: Path) -> None:
    registry = _living_registry()
    artifact = registry.artifacts[0]
    _write_registered_file(tmp_path, artifact, b"registered bytes\n")
    commit = CommitRef(repository=REPOSITORY, sha="a" * 40)
    resolved = resolve_canonical_artifact(tmp_path, registry, "current-doc", commit)
    assert resolved.revision == artifact
    assert resolved.observed_at_commit == commit
    assert resolved.canonical_status == "CURRENT"
    assert "commit" not in ResolvedRepositoryArtifact.model_fields
    assert "observed_at_commit" in ResolvedRepositoryArtifact.model_fields


def test_resolution_preserves_registry_identity_across_snapshot_commits(tmp_path: Path) -> None:
    registry = _living_registry()
    artifact = registry.artifacts[0]
    _write_registered_file(tmp_path, artifact, b"registered bytes\n")
    first = CommitRef(repository=REPOSITORY, sha="a" * 40)
    later = CommitRef(repository=REPOSITORY, sha="b" * 40)
    observed_first = resolve_artifact_revision(tmp_path, registry, _ref(artifact), first)
    observed_later = resolve_artifact_revision(tmp_path, registry, _ref(artifact), later)
    assert observed_first.revision == observed_later.revision == artifact
    assert observed_first.observed_at_commit != observed_later.observed_at_commit
    assert not isinstance(observed_first, Artifact)
    assert "commit" not in ResolvedRepositoryArtifact.model_fields


def test_resolution_does_not_rebind_core_artifact_commit_under_same_artifact_id(
    tmp_path: Path,
) -> None:
    registry = _living_registry()
    artifact = registry.artifacts[0]
    _write_registered_file(tmp_path, artifact, b"registered bytes\n")
    first_commit = CommitRef(repository=REPOSITORY, sha="a" * 40)
    second_commit = CommitRef(repository=REPOSITORY, sha="b" * 40)
    first = resolve_artifact_revision(tmp_path, registry, _ref(artifact), first_commit)
    second = resolve_artifact_revision(tmp_path, registry, _ref(artifact), second_commit)
    assert first.revision.artifact_id == second.revision.artifact_id == artifact.artifact_id
    assert first.observed_at_commit == first_commit
    assert second.observed_at_commit == second_commit
    assert "id" not in ResolvedRepositoryArtifact.model_fields
    assert "commit" not in ResolvedRepositoryArtifact.model_fields
    assert "revision" in ResolvedRepositoryArtifact.model_fields
    assert "id" in Artifact.model_fields and "commit" in Artifact.model_fields


def test_resolution_rejects_full_repositoryref_mismatch(tmp_path: Path) -> None:
    registry = _living_registry()
    wrong_commit = CommitRef(repository=OTHER_REPOSITORY_SAME_ID, sha="a" * 40)
    with pytest.raises(CanonicalResolutionError, match="full registry RepositoryRef"):
        resolve_canonical_artifact(tmp_path, registry, "current-doc", wrong_commit)


def test_resolution_rejects_missing_canonical_key(tmp_path: Path) -> None:
    registry = _living_registry()
    commit = CommitRef(repository=REPOSITORY, sha="a" * 40)
    with pytest.raises(CanonicalResolutionError, match="not registered"):
        resolve_canonical_artifact(tmp_path, registry, "missing-key", commit)


def test_registry_accepts_multihop_mature_supersession_chain() -> None:
    first_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
    )
    third_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789003", revision=3
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        supersedes=first_ref,
        superseded_by=third_ref,
    )
    third = _artifact(
        "records/third.md",
        number=3,
        revision=3,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
        supersedes=second_ref,
    )
    assert _registry((first, second, third)).artifacts


def test_registry_rejects_nonreciprocal_supersession() -> None:
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    with pytest.raises(ValidationError, match="reciprocal"):
        _registry((first, second))


def test_registry_rejects_supersession_cycle() -> None:
    first_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    with pytest.raises((ValidationError, ValueError)):
        first = _artifact(
            "records/first.md",
            number=1,
            artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
            state=RepositoryArtifactState.SUPERSEDED,
            supersedes=second_ref,
            superseded_by=second_ref,
        )
        second = _artifact(
            "records/second.md",
            number=2,
            revision=2,
            artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
            state=RepositoryArtifactState.SUPERSEDED,
            supersedes=first_ref,
            superseded_by=first_ref,
        )
        _registry((first, second))


def test_registry_rejects_superseded_historical_record_without_successor() -> None:
    with pytest.raises(ValidationError, match="successor reference must agree"):
        _artifact(
            "records/old.md",
            artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
            state=RepositoryArtifactState.SUPERSEDED,
        )


def test_registry_rejects_historical_successor_with_review_state() -> None:
    old_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    successor_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    old = _artifact(
        "records/old.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=successor_ref,
    )
    with pytest.raises(ValidationError, match="only mature historical records"):
        review = _artifact(
            "records/review.md",
            number=2,
            revision=2,
            artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
            state=RepositoryArtifactState.REVIEW,
            supersedes=old_ref,
        )
        _registry((old, review))


def test_registry_transition_rejects_historical_revision_mutation() -> None:
    old = _artifact(
        "records/locked.md",
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    changed = _artifact(
        "records/locked.md",
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
        title="Changed historical title",
    )
    previous = _registry((old,), (CanonicalPointer(canonical_key="decision", target=_ref(old)),))
    current = _registry(
        (changed,), (CanonicalPointer(canonical_key="decision", target=_ref(changed)),)
    )
    with pytest.raises(RepositoryContractInvalid, match="historical artifact revision mutation"):
        validate_registry_transition(previous, current)


def test_registry_transition_rejects_historical_record_removal() -> None:
    locked = _artifact(
        "records/locked.md",
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    with pytest.raises(RepositoryContractInvalid, match="cannot be removed"):
        validate_registry_transition(_registry((locked,)), _registry(()))


def test_registry_transition_rejects_immutable_record_mutation() -> None:
    original = _artifact(
        "records/event.md",
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.IMMUTABLE,
    )
    changed = _artifact(
        "records/event.md",
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.IMMUTABLE,
        title="Altered event",
    )
    with pytest.raises(RepositoryContractInvalid, match="historical artifact revision mutation"):
        validate_registry_transition(_registry((original,)), _registry((changed,)))


def test_registry_transition_rejects_historical_class_mutation() -> None:
    original = _artifact(
        "records/locked.md",
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    changed = _artifact(
        "records/locked.md",
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.IMMUTABLE,
    )
    with pytest.raises(RepositoryContractInvalid, match="historical artifact revision mutation"):
        validate_registry_transition(_registry((original,)), _registry((changed,)))


def test_registry_transition_rejects_already_superseded_mutation() -> None:
    first_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
        supersedes=first_ref,
    )
    previous = _registry((first, second))
    mutated = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
        title="Mutated old record",
    )
    current = _registry((mutated, second))
    with pytest.raises(RepositoryContractInvalid, match="already-superseded"):
        validate_registry_transition(previous, current)


def test_registry_transition_rejects_new_already_superseded_record() -> None:
    first_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
        supersedes=first_ref,
    )
    with pytest.raises(RepositoryContractInvalid, match="new records cannot begin"):
        validate_registry_transition(_registry(()), _registry((first, second)))


def test_transition_rejects_canonical_locked_jump_without_supersession() -> None:
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    previous = _registry(
        (first,), (CanonicalPointer(canonical_key="decision", target=_ref(first)),)
    )
    current = _registry(
        (first, second), (CanonicalPointer(canonical_key="decision", target=_ref(second)),)
    )
    with pytest.raises(RepositoryContractInvalid, match="direct mature successor"):
        validate_registry_transition(previous, current)


def test_transition_allows_canonical_locked_direct_successor() -> None:
    first_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    second_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    first = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
    )
    second = _artifact(
        "records/second.md",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.LOCKED,
        supersedes=first_ref,
    )
    old_superseded = _artifact(
        "records/first.md",
        number=1,
        artifact_class=RepositoryArtifactClass.LOCKABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=second_ref,
    )
    previous = _registry((first,), (CanonicalPointer(canonical_key="decision", target=first_ref),))
    current = _registry(
        (old_superseded, second),
        (CanonicalPointer(canonical_key="decision", target=second_ref),),
    )
    validate_registry_transition(previous, current)


def test_transition_allows_canonical_immutable_direct_successor() -> None:
    old_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001", revision=1
    )
    new_ref = ArtifactRevisionRef(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789002", revision=2
    )
    old = _artifact(
        "records/event-v1.json",
        number=1,
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.IMMUTABLE,
    )
    successor = _artifact(
        "records/event-v2.json",
        number=2,
        revision=2,
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.IMMUTABLE,
        supersedes=old_ref,
    )
    superseded = _artifact(
        "records/event-v1.json",
        number=1,
        artifact_class=RepositoryArtifactClass.IMMUTABLE_RECORD,
        state=RepositoryArtifactState.SUPERSEDED,
        superseded_by=new_ref,
    )
    previous = _registry((old,), (CanonicalPointer(canonical_key="event", target=old_ref),))
    current = _registry(
        (superseded, successor),
        (CanonicalPointer(canonical_key="event", target=new_ref),),
    )
    validate_registry_transition(previous, current)


def test_registry_transition_rejects_canonical_key_removal() -> None:
    artifact = _artifact("docs/current.md")
    previous = _registry(
        (artifact,), (CanonicalPointer(canonical_key="current-doc", target=_ref(artifact)),)
    )
    with pytest.raises(RepositoryContractInvalid, match="canonical keys cannot be removed"):
        validate_registry_transition(previous, _registry((artifact,)))


def test_registry_transition_requires_living_revision_increment() -> None:
    old = _artifact("docs/current.md", number=1)
    new = _artifact("docs/current.md", number=2, revision=1)
    previous = _registry((old,), (CanonicalPointer(canonical_key="current-doc", target=_ref(old)),))
    current = _registry((new,), (CanonicalPointer(canonical_key="current-doc", target=_ref(new)),))
    with pytest.raises(RepositoryContractInvalid, match="revision increment"):
        validate_registry_transition(previous, current)


def test_registry_transition_allows_living_update_with_new_id_and_revision() -> None:
    old = _artifact("docs/current.md", number=1)
    new = _artifact("docs/current.md", number=2, revision=2, raw=b"next bytes\n")
    previous = _registry((old,), (CanonicalPointer(canonical_key="current-doc", target=_ref(old)),))
    current = _registry((new,), (CanonicalPointer(canonical_key="current-doc", target=_ref(new)),))
    validate_registry_transition(previous, current)


def test_registry_transition_allows_new_canonical_key_with_valid_target() -> None:
    existing = _artifact("docs/current.md", number=1)
    added = _artifact("docs/other.md", number=2)
    previous = _registry(
        (existing,), (CanonicalPointer(canonical_key="current-doc", target=_ref(existing)),)
    )
    current = _registry(
        (existing, added),
        (
            CanonicalPointer(canonical_key="current-doc", target=_ref(existing)),
            CanonicalPointer(canonical_key="other-doc", target=_ref(added)),
        ),
    )
    validate_registry_transition(previous, current)


def test_registry_transition_allows_nonhistorical_removal_and_new_identity() -> None:
    old = _artifact(
        "drafts/work.md",
        artifact_class=RepositoryArtifactClass.WORKING,
        state=RepositoryArtifactState.DRAFT,
    )
    new = _artifact(
        "drafts/work.md",
        number=2,
        raw=b"replacement bytes\n",
        artifact_class=RepositoryArtifactClass.WORKING,
        state=RepositoryArtifactState.DRAFT,
    )
    previous = _registry((old,))
    current = _registry((new,))
    validate_registry_transition(previous, current)


def test_registry_transition_rejects_nonhistorical_same_id_byte_replacement() -> None:
    old = _artifact("docs/current.md", raw=b"old bytes")
    new = _artifact("docs/current.md", raw=b"new bytes")
    previous = _registry((old,), (CanonicalPointer(canonical_key="current-doc", target=_ref(old)),))
    current = _registry((new,), (CanonicalPointer(canonical_key="current-doc", target=_ref(new)),))
    with pytest.raises(RepositoryContractInvalid, match="new ArtifactId"):
        validate_registry_transition(previous, current)


def test_relay_repository_registry_validates() -> None:
    dogfood_root = Path(__file__).parents[2]
    registry = validate_repository_contract(
        dogfood_root,
        PROJECT_ID,  # type: ignore[arg-type]
        REPOSITORY,
    )
    assert tuple(pointer.canonical_key for pointer in registry.canonical) == (
        "build-plan",
        "current-baseline",
        "documentation-governance",
        "engineering-simplicity-quality",
        "product-proposal",
    )
    assert registry.project_id == PROJECT_ID
    assert registry.repository == REPOSITORY
