"""Pure loading, validation, transition checking, and resolution for schema-v1 registries."""

import hashlib
import json
import stat
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from relay_engine.domain import ArtifactId, CommitRef, ProjectId, RepositoryRef
from relay_engine.repository_contract.errors import (
    ArtifactIntegrityError,
    CanonicalResolutionError,
    RepositoryContractInvalid,
)
from relay_engine.repository_contract.models import (
    ArtifactRevisionRef,
    CanonicalKey,
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryRegistry,
    ResolvedRepositoryArtifact,
)


def parse_repository_registry(raw: bytes) -> RepositoryRegistry:
    """Parse strict UTF-8 JSON and reject duplicate object keys and invalid registry data."""

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
        normalized = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return RepositoryRegistry.model_validate_json(normalized)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as error:
        raise RepositoryContractInvalid(f"invalid repository registry: {error}") from error


def serialize_repository_registry(registry: RepositoryRegistry) -> bytes:
    """Return deterministic UTF-8 JSON for an already canonical registry value."""

    validated = _revalidate_registry(registry)
    text = json.dumps(
        validated.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return text.encode("utf-8")


def validate_repository_contract(
    repository_root: Path,
    expected_project_id: ProjectId,
    expected_repository: RepositoryRef,
) -> RepositoryRegistry:
    """Validate one repository snapshot, including strict registry and exact file digests."""

    root = _require_repository_root(repository_root)
    relay_dir = root / ".relay"
    try:
        relay_stat = relay_dir.lstat()
    except OSError as error:
        raise RepositoryContractInvalid("repository must contain a .relay directory") from error
    if stat.S_ISLNK(relay_stat.st_mode) or not stat.S_ISDIR(relay_stat.st_mode):
        raise RepositoryContractInvalid(".relay must be a real directory")

    try:
        entries = tuple(relay_dir.iterdir())
    except OSError as error:
        raise RepositoryContractInvalid("cannot inspect .relay directory") from error
    if len(entries) != 1 or entries[0].name != "registry.json":
        raise RepositoryContractInvalid("schema v1 permits only .relay/registry.json")
    registry_path = relay_dir / "registry.json"
    try:
        registry_stat = registry_path.lstat()
    except OSError as error:
        raise RepositoryContractInvalid(".relay/registry.json is required") from error
    if stat.S_ISLNK(registry_stat.st_mode) or not stat.S_ISREG(registry_stat.st_mode):
        raise RepositoryContractInvalid(".relay/registry.json must be a regular non-symlink file")

    try:
        registry = parse_repository_registry(registry_path.read_bytes())
    except OSError as error:
        raise RepositoryContractInvalid("cannot read .relay/registry.json") from error
    if registry.project_id != expected_project_id:
        raise RepositoryContractInvalid("registry project identity does not match expected project")
    if registry.repository != expected_repository:
        raise RepositoryContractInvalid("registry RepositoryRef does not match expected repository")

    for artifact in registry.artifacts:
        _verify_artifact_file(root, artifact)
    return registry


def validate_registry_transition(
    previous: RepositoryRegistry,
    current: RepositoryRegistry,
) -> None:
    """Validate a structural registry transition without authorizing or mutating it."""

    previous = _revalidate_registry(previous)
    current = _revalidate_registry(current)
    if previous.project_id != current.project_id:
        raise RepositoryContractInvalid("project identity cannot change across registry transition")
    if previous.repository != current.repository:
        raise RepositoryContractInvalid(
            "full RepositoryRef cannot change across registry transition"
        )

    previous_keys = {pointer.canonical_key: pointer for pointer in previous.canonical}
    current_keys = {pointer.canonical_key: pointer for pointer in current.canonical}
    if not previous_keys.keys() <= current_keys.keys():
        raise RepositoryContractInvalid("existing canonical keys cannot be removed")

    before = {artifact.artifact_id: artifact for artifact in previous.artifacts}
    after = {artifact.artifact_id: artifact for artifact in current.artifacts}
    for artifact_id, old in before.items():
        new = after.get(artifact_id)
        if new is None:
            if _is_historical(old):
                raise RepositoryContractInvalid("historical artifact revisions cannot be removed")
            continue
        if old.content_digest != new.content_digest:
            raise RepositoryContractInvalid("changed exact bytes require a new ArtifactId")
        if old.artifact_state is RepositoryArtifactState.SUPERSEDED and new != old:
            raise RepositoryContractInvalid("already-superseded historical records are immutable")
        if _is_historical(old):
            if new == old:
                continue
            if not _is_allowed_historical_supersession(old, new, after):
                raise RepositoryContractInvalid(
                    "historical artifact revision mutation is forbidden"
                )

    for artifact_id, new in after.items():
        if artifact_id not in before and new.artifact_state is RepositoryArtifactState.SUPERSEDED:
            raise RepositoryContractInvalid("new records cannot begin in SUPERSEDED state")

    for key, old_pointer in previous_keys.items():
        new_pointer = current_keys[key]
        if new_pointer == old_pointer:
            continue
        old_target = before[old_pointer.target.artifact_id]
        new_target = after.get(new_pointer.target.artifact_id)
        if new_target is None or _ref(new_target) != new_pointer.target:
            raise RepositoryContractInvalid(
                "new canonical pointer must target a current registry revision"
            )
        if old_target.artifact_class is RepositoryArtifactClass.LIVING_PROJECTION:
            if (
                new_target.artifact_class is not RepositoryArtifactClass.LIVING_PROJECTION
                or new_target.artifact_state is not RepositoryArtifactState.CURRENT
                or new_target.artifact_id == old_target.artifact_id
                or new_target.revision != old_target.revision + 1
            ):
                raise RepositoryContractInvalid(
                    "living canonical advancement requires a new ID and revision increment"
                )
        else:
            if old_target.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD:
                expected_state = RepositoryArtifactState.LOCKED
            elif old_target.artifact_class is RepositoryArtifactClass.IMMUTABLE_RECORD:
                expected_state = RepositoryArtifactState.IMMUTABLE
            else:
                raise RepositoryContractInvalid("canonical pointer has an unsupported prior target")
            expected_ref = _ref(new_target)
            superseded_old = after.get(old_target.artifact_id)
            if (
                new_target.artifact_class is not old_target.artifact_class
                or new_target.artifact_state is not expected_state
                or new_target.artifact_type != old_target.artifact_type
                or new_target.revision != old_target.revision + 1
                or new_target.supersedes != old_pointer.target
                or superseded_old is None
                or superseded_old.artifact_state is not RepositoryArtifactState.SUPERSEDED
                or superseded_old.superseded_by != expected_ref
            ):
                raise RepositoryContractInvalid(
                    "historical canonical advancement requires the direct mature successor"
                )


def resolve_canonical_artifact(
    repository_root: Path,
    registry: RepositoryRegistry,
    canonical_key: CanonicalKey,
    source_commit: CommitRef,
) -> ResolvedRepositoryArtifact:
    """Resolve a canonical key while carrying explicit snapshot-observation provenance."""

    registry = _revalidate_registry(registry)
    _require_observation_repository(registry, source_commit)
    pointer = next(
        (item for item in registry.canonical if item.canonical_key == canonical_key), None
    )
    if pointer is None:
        raise CanonicalResolutionError(f"canonical key is not registered: {canonical_key}")
    artifact = _find_revision(registry, pointer.target)
    if not _canonical_target(artifact):
        raise CanonicalResolutionError("canonical pointer does not target a current authority")
    _verify_artifact_file(_require_repository_root(repository_root), artifact)
    return ResolvedRepositoryArtifact(
        canonical_key=canonical_key,
        revision=artifact,
        observed_at_commit=source_commit,
        canonical_status="CURRENT",
    )


def resolve_artifact_revision(
    repository_root: Path,
    registry: RepositoryRegistry,
    artifact_ref: ArtifactRevisionRef,
    source_commit: CommitRef,
) -> ResolvedRepositoryArtifact:
    """Resolve any exact registry revision without synthesizing a core Artifact value."""

    registry = _revalidate_registry(registry)
    _require_observation_repository(registry, source_commit)
    try:
        artifact = _find_revision(registry, artifact_ref)
    except RepositoryContractInvalid as error:
        raise CanonicalResolutionError(str(error)) from error
    _verify_artifact_file(_require_repository_root(repository_root), artifact)
    key = next(
        (pointer.canonical_key for pointer in registry.canonical if pointer.target == artifact_ref),
        None,
    )
    return ResolvedRepositoryArtifact(
        canonical_key=key,
        revision=artifact,
        observed_at_commit=source_commit,
        canonical_status="CURRENT" if key is not None else None,
    )


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _require_repository_root(repository_root: Path) -> Path:
    try:
        root = repository_root.resolve(strict=True)
    except OSError as error:
        raise RepositoryContractInvalid("repository root does not exist") from error
    if not root.is_dir():
        raise RepositoryContractInvalid("repository root must be a directory")
    return root


def _verify_artifact_file(repository_root: Path, artifact: RepositoryArtifactRevision) -> None:
    relative = Path(*artifact.path.split("/"))
    current = repository_root
    for part in relative.parts:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise ArtifactIntegrityError(
                f"registered artifact is missing: {artifact.path}"
            ) from error
        if stat.S_ISLNK(mode):
            raise ArtifactIntegrityError(
                f"registered artifact path contains a symlink: {artifact.path}"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise ArtifactIntegrityError(f"registered artifact is not a regular file: {artifact.path}")
    try:
        current.resolve(strict=True).relative_to(repository_root)
    except (OSError, ValueError) as error:
        raise ArtifactIntegrityError(
            f"registered artifact escapes repository root: {artifact.path}"
        ) from error
    try:
        raw = current.read_bytes()
    except OSError as error:
        raise ArtifactIntegrityError(
            f"registered artifact cannot be read: {artifact.path}"
        ) from error
    digest = f"sha256:{hashlib.sha256(raw).hexdigest()}"
    if digest != artifact.content_digest:
        raise ArtifactIntegrityError(f"registered artifact digest mismatch: {artifact.path}")


def _revalidate_registry(registry: RepositoryRegistry) -> RepositoryRegistry:
    try:
        return RepositoryRegistry.model_validate_json(registry.model_dump_json())
    except (ValidationError, TypeError, ValueError) as error:
        raise RepositoryContractInvalid(f"invalid repository registry value: {error}") from error


def _is_historical(artifact: RepositoryArtifactRevision) -> bool:
    return artifact.artifact_class in {
        RepositoryArtifactClass.LOCKABLE_RECORD,
        RepositoryArtifactClass.IMMUTABLE_RECORD,
    } and artifact.artifact_state in {
        RepositoryArtifactState.LOCKED,
        RepositoryArtifactState.IMMUTABLE,
        RepositoryArtifactState.SUPERSEDED,
    }


def _is_allowed_historical_supersession(
    old: RepositoryArtifactRevision,
    new: RepositoryArtifactRevision,
    current: dict[ArtifactId, RepositoryArtifactRevision],
) -> bool:
    if old.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD:
        original_state = RepositoryArtifactState.LOCKED
        successor_state = RepositoryArtifactState.SUPERSEDED
        mature_successor = RepositoryArtifactState.LOCKED
    else:
        original_state = RepositoryArtifactState.IMMUTABLE
        successor_state = RepositoryArtifactState.SUPERSEDED
        mature_successor = RepositoryArtifactState.IMMUTABLE
    if old.artifact_state is not original_state:
        return False
    if new.artifact_state is not successor_state or new.superseded_by is None:
        return False
    if (
        old.artifact_id != new.artifact_id
        or old.revision != new.revision
        or old.title != new.title
        or old.artifact_type != new.artifact_type
        or old.artifact_class != new.artifact_class
        or old.path != new.path
        or old.content_digest != new.content_digest
        or old.human_version != new.human_version
        or old.updated_at != new.updated_at
        or old.scope != new.scope
        or old.supersedes != new.supersedes
    ):
        return False
    successor = current.get(new.superseded_by.artifact_id)
    return (
        successor is not None
        and _ref(successor) == new.superseded_by
        and successor.artifact_class is old.artifact_class
        and successor.artifact_type == old.artifact_type
        and successor.artifact_state is mature_successor
        and successor.supersedes == _ref(old)
        and successor.revision == old.revision + 1
    )


def _find_revision(
    registry: RepositoryRegistry, artifact_ref: ArtifactRevisionRef
) -> RepositoryArtifactRevision:
    for artifact in registry.artifacts:
        if (
            artifact.artifact_id == artifact_ref.artifact_id
            and artifact.revision == artifact_ref.revision
        ):
            return artifact
    raise RepositoryContractInvalid("artifact revision reference is not registered")


def _require_observation_repository(
    registry: RepositoryRegistry,
    source_commit: CommitRef,
) -> None:
    if source_commit.repository != registry.repository:
        raise CanonicalResolutionError(
            "observation CommitRef repository must equal the full registry RepositoryRef"
        )


def _ref(artifact: RepositoryArtifactRevision) -> ArtifactRevisionRef:
    return ArtifactRevisionRef(artifact_id=artifact.artifact_id, revision=artifact.revision)


def _canonical_target(artifact: RepositoryArtifactRevision) -> bool:
    return (
        (
            artifact.artifact_class is RepositoryArtifactClass.LIVING_PROJECTION
            and artifact.artifact_state is RepositoryArtifactState.CURRENT
        )
        or (
            artifact.artifact_class is RepositoryArtifactClass.LOCKABLE_RECORD
            and artifact.artifact_state is RepositoryArtifactState.LOCKED
        )
        or (
            artifact.artifact_class is RepositoryArtifactClass.IMMUTABLE_RECORD
            and artifact.artifact_state is RepositoryArtifactState.IMMUTABLE
        )
    )
