"""Validation, projection, and safe persistence for B1 Human intake."""

import hashlib
import json
import math
import os
import stat
import tempfile
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, cast

from pydantic import ValidationError

from relay_engine.bootstrap_discovery.intake_models import (
    AdoptionManifestV1,
    ContextReference,
    HumanConfirmedConstraints,
    HumanConfirmedText,
    HumanConfirmedWorkFocusKind,
    HumanFacts,
    ManifestStatus,
    ObservedFact,
    ObservedProjection,
    ReportBinding,
    ReviewNote,
    UnresolvedFact,
    UnresolvedKey,
    unresolved_items_for,
)
from relay_engine.bootstrap_discovery.local_git import LocalGitError, resolve_repository_root
from relay_engine.bootstrap_discovery.models import (
    BootstrapDiscoveryReportV1,
    InspectionState,
    TrackedEvidenceFile,
)
from relay_engine.bootstrap_discovery.models import (
    canonical_json_bytes as canonical_report_json_bytes,
)


class IntakeError(RuntimeError):
    """A typed B1 validation, workflow, or output-safety failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class LoadedReport:
    """The exact report bytes, validated report model, value tree, and checkout root."""

    report: BootstrapDiscoveryReportV1
    raw_bytes: bytes
    sha256: str
    value: dict[str, Any]
    repository_root: Path


@dataclass(frozen=True)
class DocumentationGroup:
    """One stable, Human-navigable group in the report's documentation catalog."""

    key: str
    title: str
    files: tuple[tuple[str, str], ...]

    @property
    def count(self) -> int:
        """Return the number of reported paths in the group."""

        return len(self.files)

    @property
    def preview(self) -> tuple[str, ...]:
        """Return the first three paths for a concise initial view."""

        return tuple(path for path, _ in self.files[:3])


_OBSERVED_POINTERS = {
    "repository_path": "/observation/repository_path",
    "observed_at": "/observation/observed_at",
    "discovery_status": "/observation/discovery_status",
    "diagnostics": "/observation/diagnostics",
    "head_sha": "/git/head_sha",
    "branch": "/git/branch",
    "detached_head": "/git/detached_head",
    "dirty": "/git/dirty",
    "tracked_file_count": "/git/tracked_file_count",
    "remotes": "/git/remotes",
    "manifests": "/manifests",
    "language_signals": "/language_signals",
    "ci_files": "/ci_files",
    "relay_contract": "/relay_contract/status",
    "unresolved_human_questions": "/unresolved_human_questions",
}

_HUMAN_KEYS = (
    ("project_name", UnresolvedKey.PROJECT_NAME),
    ("canonical_repository", UnresolvedKey.CANONICAL_REPOSITORY),
    ("project_objective", UnresolvedKey.PROJECT_OBJECTIVE),
    ("current_status", UnresolvedKey.CURRENT_STATUS),
    ("human_objective", UnresolvedKey.HUMAN_OBJECTIVE),
    ("constraints", UnresolvedKey.CONSTRAINTS),
    ("work_focus_kind", UnresolvedKey.WORK_FOCUS_KIND),
    ("work_focus", UnresolvedKey.WORK_FOCUS),
)


def load_report(report_path: Path, repository: Path) -> LoadedReport:
    """Read and strictly validate an exact canonical B0-F report for a real checkout."""

    raw_bytes = _read_regular_non_symlink(report_path, "REPORT_UNSAFE", "report")
    parsed_value: Any = _parse_unique_json(raw_bytes, "REPORT_INVALID", "report")
    try:
        report = BootstrapDiscoveryReportV1.model_validate_json(raw_bytes)
    except ValidationError as error:
        raise IntakeError(
            "REPORT_INVALID", "B0-F report does not match schema version 1"
        ) from error
    if canonical_report_json_bytes(report) != raw_bytes:
        raise IntakeError("REPORT_NOT_CANONICAL", "B0-F report is not canonical JSON")
    if not isinstance(parsed_value, dict):
        raise IntakeError("REPORT_INVALID", "B0-F report root must be a JSON object")

    try:
        repository_root = resolve_repository_root(repository)
    except LocalGitError as error:
        raise IntakeError(error.code, str(error)) from error
    try:
        recorded_root = Path(report.observation.repository_path).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise IntakeError(
            "REPORT_REPOSITORY_MISMATCH",
            "report repository path does not resolve to an existing checkout",
        ) from error
    if recorded_root != repository_root:
        raise IntakeError(
            "REPORT_REPOSITORY_MISMATCH",
            "report describes a different repository root",
        )

    _validate_unique_evidence_paths(report)
    return LoadedReport(
        report=report,
        raw_bytes=raw_bytes,
        sha256="sha256:" + hashlib.sha256(raw_bytes).hexdigest(),
        value=cast(dict[str, Any], parsed_value),
        repository_root=repository_root,
    )


def initial_manifest(loaded: LoadedReport, captured_at: datetime) -> AdoptionManifestV1:
    """Create an incomplete draft whose observed facts are copied directly from the report."""

    now = _normalize_time(captured_at)
    facts = HumanFacts(
        project_name=_unresolved("Not answered yet."),
        canonical_repository=_unresolved("Not answered yet."),
        project_objective=_unresolved("Not answered yet."),
        current_status=_unresolved("Not answered yet."),
        human_objective=_unresolved("Not answered yet."),
        constraints=_unresolved("Not answered yet."),
        work_focus_kind=_unresolved("Not answered yet."),
        work_focus=_unresolved("Not answered yet."),
    )
    binding = ReportBinding(
        sha256=loaded.sha256,
        format=loaded.report.format,
        schema_version=loaded.report.schema_version,
        observed_at=loaded.report.observation.observed_at,
        repository_path=loaded.report.observation.repository_path,
        report_head_sha=loaded.report.git.head_sha,
    )
    manifest = AdoptionManifestV1(
        preparation_status=ManifestStatus.INCOMPLETE,
        created_at=now,
        updated_at=now,
        input_report=binding,
        observed=_observed_projection(loaded.value),
        human_facts=facts,
        context_references=(),
        unresolved_items=unresolved_items_for(facts),
        review_notes=(),
    )
    validate_manifest(manifest, loaded)
    return manifest


def parse_manifest(raw_bytes: bytes, loaded: LoadedReport) -> AdoptionManifestV1:
    """Parse a canonical draft and validate its full provenance against the bound report."""

    parsed_value = _parse_unique_json(raw_bytes, "DRAFT_INVALID", "draft")
    try:
        manifest = AdoptionManifestV1.model_validate_json(raw_bytes)
    except ValidationError as error:
        raise IntakeError(
            "DRAFT_INVALID", "intake draft does not match manifest schema v1"
        ) from error
    if canonical_manifest_bytes(manifest, loaded) != raw_bytes:
        raise IntakeError("DRAFT_NOT_CANONICAL", "intake draft is not canonical JSON")
    if not isinstance(parsed_value, dict):
        raise IntakeError("DRAFT_INVALID", "intake draft root must be a JSON object")
    validate_manifest(manifest, loaded)
    return manifest


def validate_manifest(manifest: AdoptionManifestV1, loaded: LoadedReport) -> None:
    """Fail closed unless every copied observation and context reference matches the report."""

    expected_binding = ReportBinding(
        sha256=loaded.sha256,
        format=loaded.report.format,
        schema_version=loaded.report.schema_version,
        observed_at=loaded.report.observation.observed_at,
        repository_path=loaded.report.observation.repository_path,
        report_head_sha=loaded.report.git.head_sha,
    )
    if manifest.input_report != expected_binding:
        raise IntakeError("REPORT_DIGEST_MISMATCH", "draft is not bound to the supplied report")

    for field_name, expected_pointer in _OBSERVED_POINTERS.items():
        fact = getattr(manifest.observed, field_name)
        pointer = fact.report_pointer
        if pointer != expected_pointer:
            raise IntakeError(
                "OBSERVED_POINTER_MISMATCH",
                f"observed field {field_name} has an unexpected report pointer",
            )
        try:
            report_value = resolve_json_pointer(loaded.value, pointer)
        except IntakeError as error:
            raise IntakeError(
                "OBSERVED_VALUE_MISMATCH",
                f"observed field {field_name} points to no report value",
            ) from error
        if not _json_structurally_equal(fact.value, report_value):
            raise IntakeError(
                "OBSERVED_VALUE_MISMATCH",
                f"observed field {field_name} does not equal the bound report value",
            )

    documentation_entries = _documentation_entry_map(loaded)
    for reference in manifest.context_references:
        entry = documentation_entries.get(reference.report_pointer)
        if entry is None:
            raise IntakeError(
                "CONTEXT_REFERENCE_MISMATCH",
                "context reference does not point to a reported documentation entry",
            )
        if entry.inspection_state is not InspectionState.READ:
            raise IntakeError(
                "CONTEXT_REFERENCE_MISMATCH",
                "only report entries with READ inspection state may be selected as context",
            )
        if (
            reference.relative_path != entry.relative_path
            or reference.sha256 != entry.sha256
            or reference.inspection_state is not entry.inspection_state
        ):
            raise IntakeError(
                "CONTEXT_REFERENCE_MISMATCH",
                "context path, digest, or inspection state differs from the report entry",
            )

    for note in manifest.review_notes:
        try:
            resolve_json_pointer(loaded.value, note.report_pointer)
        except IntakeError as error:
            raise IntakeError(
                "REVIEW_NOTE_POINTER_INVALID",
                "review note does not point to a value in the bound report",
            ) from error


def update_human_fact(
    manifest: AdoptionManifestV1,
    field_name: str,
    fact: HumanConfirmedText
    | HumanConfirmedConstraints
    | HumanConfirmedWorkFocusKind
    | UnresolvedFact,
    updated_at: datetime,
    loaded: LoadedReport,
) -> AdoptionManifestV1:
    """Return a validated candidate with one Human fact changed and readiness re-derived."""

    if field_name not in {name for name, _ in _HUMAN_KEYS}:
        raise IntakeError("UNKNOWN_HUMAN_FIELD", "requested Human field is not in the B1 schema")
    values = manifest.model_dump(mode="python")
    values["human_facts"][field_name] = fact.model_dump(mode="python")
    return _updated_manifest(values, _normalize_time(updated_at), loaded)


def add_context_reference(
    manifest: AdoptionManifestV1,
    pointer: str,
    selected_at: datetime,
    loaded: LoadedReport,
) -> AdoptionManifestV1:
    """Append a selected READ documentation entry after validating its exact report record."""

    candidates = _documentation_entry_map(loaded)
    entry = candidates.get(pointer)
    if entry is None:
        raise IntakeError("CONTEXT_REFERENCE_MISMATCH", "unknown documentation report pointer")
    if entry.inspection_state is not InspectionState.READ or entry.sha256 is None:
        raise IntakeError(
            "CONTEXT_NOT_READABLE", "only READ documentation can be selected as context"
        )
    if pointer in {reference.report_pointer for reference in manifest.context_references}:
        return manifest
    values = manifest.model_dump(mode="python")
    references = list(values["context_references"])
    references.append(
        ContextReference(
            report_pointer=pointer,
            relative_path=entry.relative_path,
            sha256=entry.sha256,
            inspection_state=entry.inspection_state,
            selected_at=_normalize_time(selected_at),
        ).model_dump(mode="python")
    )
    values["context_references"] = tuple(
        sorted(references, key=lambda item: (item["relative_path"], item["report_pointer"]))
    )
    return _updated_manifest(values, _normalize_time(selected_at), loaded)


def remove_context_reference(
    manifest: AdoptionManifestV1,
    relative_path: str,
    updated_at: datetime,
    loaded: LoadedReport,
) -> AdoptionManifestV1:
    """Remove an optional context reference by its exact report-listed path."""

    values = manifest.model_dump(mode="python")
    references = [
        item for item in values["context_references"] if item["relative_path"] != relative_path
    ]
    values["context_references"] = tuple(
        sorted(references, key=lambda item: (item["relative_path"], item["report_pointer"]))
    )
    return _updated_manifest(values, _normalize_time(updated_at), loaded)


def add_review_note(
    manifest: AdoptionManifestV1,
    pointer: str,
    note: str,
    captured_at: datetime,
    loaded: LoadedReport,
) -> AdoptionManifestV1:
    """Append non-authoritative commentary on one exact report value."""

    resolve_json_pointer(loaded.value, pointer)
    values = manifest.model_dump(mode="python")
    notes = list(values["review_notes"])
    try:
        review_note = ReviewNote(
            report_pointer=pointer,
            note=note,
            captured_at=_normalize_time(captured_at),
        )
    except ValidationError as error:
        raise IntakeError("REVIEW_NOTE_INVALID", "review note is not valid") from error
    notes.append(review_note.model_dump(mode="python"))
    values["review_notes"] = tuple(
        sorted(notes, key=lambda item: (item["captured_at"], item["report_pointer"], item["note"]))
    )
    return _updated_manifest(values, _normalize_time(captured_at), loaded)


def documentation_groups(loaded: LoadedReport) -> tuple[DocumentationGroup, ...]:
    """Group report-listed documentation paths deterministically without reading prose."""

    orientation: list[tuple[str, str]] = []
    doc_groups: dict[str, list[tuple[str, str]]] = {}
    other: list[tuple[str, str]] = []
    for pointer, entry in _documentation_entry_map(loaded).items():
        path = entry.relative_path
        basename = PurePosixPath(path).name.lower()
        if "/" not in path and basename.startswith(
            ("readme", "contributing", "architecture", "roadmap")
        ):
            orientation.append((path, pointer))
        elif path.startswith("docs/") and path.lower().endswith(".md"):
            parts = PurePosixPath(path).parts
            key = "docs" if len(parts) == 2 else f"docs/{parts[1]}"
            doc_groups.setdefault(key, []).append((path, pointer))
        else:
            other.append((path, pointer))

    groups: list[DocumentationGroup] = []
    if orientation:
        groups.append(
            DocumentationGroup(
                key="orientation",
                title="Root orientation candidates",
                files=tuple(sorted(orientation)),
            )
        )
    for key in sorted(doc_groups):
        groups.append(
            DocumentationGroup(
                key=key,
                title=key,
                files=tuple(sorted(doc_groups[key])),
            )
        )
    if other:
        groups.append(
            DocumentationGroup(
                key="other",
                title="Other documentation",
                files=tuple(sorted(other)),
            )
        )
    return tuple(groups)


def canonical_manifest_bytes(manifest: AdoptionManifestV1, loaded: LoadedReport) -> bytes:
    """Validate all bound observations and return canonical manifest JSON bytes."""

    validate_manifest(manifest, loaded)
    try:
        payload = manifest.model_dump(mode="json")
        return json.dumps(
            payload,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise IntakeError(
            "MANIFEST_SERIALIZATION_FAILED", "manifest cannot be serialized"
        ) from error


def prepare_output_path(output: Path, repository_root: Path) -> Path:
    """Resolve an external output path and refuse repository containment or symlinks."""

    try:
        requested = output.expanduser().absolute()
        root = repository_root.resolve(strict=True)
        requested_parent = requested.parent.resolve(strict=False)
        resolved_output = requested_parent / requested.name
    except (OSError, RuntimeError) as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "output path cannot be resolved") from error

    if _is_inside(requested, root) or _is_inside(resolved_output, root):
        raise IntakeError(
            "OUTPUT_INSIDE_REPOSITORY",
            "manifest output must be outside the inspected repository",
        )
    if requested.is_symlink() or resolved_output.is_symlink():
        raise IntakeError("OUTPUT_UNSAFE", "symlink output paths are refused")

    try:
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        final_parent = resolved_output.parent.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "output directory is unavailable") from error
    resolved_output = final_parent / resolved_output.name
    if _is_inside(resolved_output, root):
        raise IntakeError(
            "OUTPUT_INSIDE_REPOSITORY",
            "manifest output must be outside the inspected repository",
        )
    try:
        target_stat = resolved_output.lstat()
    except FileNotFoundError:
        return resolved_output
    except OSError as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "output path cannot be inspected") from error
    if stat.S_ISLNK(target_stat.st_mode) or not stat.S_ISREG(target_stat.st_mode):
        raise IntakeError("OUTPUT_UNSAFE", "output must be a regular non-symlink file")
    return resolved_output


def write_new_draft(
    output: Path,
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
) -> None:
    """Publish a complete initial draft at a path that must not already exist."""

    payload = canonical_manifest_bytes(manifest, loaded)
    _publish_new_bytes(output, payload)


def checkpoint_draft(
    output: Path,
    manifest: AdoptionManifestV1,
    loaded: LoadedReport,
) -> None:
    """Atomically replace a validated existing draft with its next checkpoint."""

    payload = canonical_manifest_bytes(manifest, loaded)
    existing_bytes = _read_regular_non_symlink(output, "DRAFT_UNAVAILABLE", "draft")
    parse_manifest(existing_bytes, loaded)
    _replace_bytes_atomically(output, payload)


def read_existing_draft(output: Path, loaded: LoadedReport) -> AdoptionManifestV1:
    """Read an existing regular draft and fail closed before any mutation."""

    raw_bytes = _read_regular_non_symlink(output, "DRAFT_UNAVAILABLE", "draft")
    return parse_manifest(raw_bytes, loaded)


def resolve_json_pointer(value: Any, pointer: str) -> Any:
    """Resolve one strict RFC 6901 JSON Pointer or raise a typed error."""

    if pointer == "":
        return value
    if not pointer.startswith("/"):
        raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer must be empty or start with slash")
    current: Any = value
    for encoded in pointer[1:].split("/"):
        token = _decode_pointer_token(encoded)
        if isinstance(current, dict):
            object_value = cast(dict[str, Any], current)
            if token not in object_value:
                raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer object member is missing")
            current = object_value[token]
        elif isinstance(current, list):
            array_value = cast(list[Any], current)
            if token == "-" or not token.isdigit() or (len(token) > 1 and token[0] == "0"):
                raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer array index is invalid")
            index = int(token)
            if index >= len(array_value):
                raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer array index is missing")
            current = array_value[index]
        else:
            raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer traverses a scalar value")
    return current


def _observed_projection(value: dict[str, Any]) -> ObservedProjection:
    facts = {
        name: ObservedFact(value=resolve_json_pointer(value, pointer), report_pointer=pointer)
        for name, pointer in _OBSERVED_POINTERS.items()
    }
    return ObservedProjection(**facts)


def _updated_manifest(
    values: dict[str, Any], updated_at: datetime, loaded: LoadedReport
) -> AdoptionManifestV1:
    facts = HumanFacts.model_validate(values["human_facts"])
    unresolved = unresolved_items_for(facts)
    values["unresolved_items"] = tuple(item.model_dump(mode="python") for item in unresolved)
    values["preparation_status"] = (
        ManifestStatus.INCOMPLETE if unresolved else ManifestStatus.READY_FOR_B2_REVIEW
    )
    values["updated_at"] = updated_at
    try:
        manifest = AdoptionManifestV1.model_validate(values)
    except ValidationError as error:
        raise IntakeError("MANIFEST_INVALID", "updated intake draft failed validation") from error
    validate_manifest(manifest, loaded)
    return manifest


def _documentation_entry_map(loaded: LoadedReport) -> dict[str, TrackedEvidenceFile]:
    result: dict[str, TrackedEvidenceFile] = {}
    for index, entry in enumerate(loaded.report.documentation_files):
        pointer = f"/documentation_files/{index}"
        result[pointer] = entry
    return result


def _validate_unique_evidence_paths(report: BootstrapDiscoveryReportV1) -> None:
    collections = [
        [item.evidence.relative_path for item in report.manifests],
        [item.relative_path for item in report.ci_files],
        [item.relative_path for item in report.documentation_files],
        [item.relative_path for item in report.relay_files],
    ]
    for paths in collections:
        if len(paths) != len(set(paths)):
            raise IntakeError("REPORT_INVALID", "report contains duplicate evidence paths")


def _parse_unique_json(raw_bytes: bytes, code: str, label: str) -> Any:
    try:
        return json.loads(
            raw_bytes.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite_json_number,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise IntakeError(code, f"{label} is not strict UTF-8 JSON") from error


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def _reject_nonfinite_json_number(value: str) -> None:
    raise ValueError(f"non-finite JSON number is forbidden: {value}")


def _decode_pointer_token(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        character = value[index]
        if character != "~":
            result.append(character)
            index += 1
            continue
        if index + 1 >= len(value) or value[index + 1] not in {"0", "1"}:
            raise IntakeError("JSON_POINTER_INVALID", "JSON Pointer escape is malformed")
        result.append("~" if value[index + 1] == "0" else "/")
        index += 2
    return "".join(result)


def _json_structurally_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        left_object = cast(dict[str, Any], left)
        right_object = cast(dict[str, Any], right)
        return left_object.keys() == right_object.keys() and all(
            _json_structurally_equal(left_object[key], right_object[key]) for key in left_object
        )
    if isinstance(left, list):
        left_array = cast(list[Any], left)
        right_array = cast(list[Any], right)
        return len(left_array) == len(right_array) and all(
            _json_structurally_equal(left_item, right_item)
            for left_item, right_item in zip(left_array, right_array, strict=True)
        )
    if isinstance(left, float) and not math.isfinite(left):
        return False
    return left == right


def _read_regular_non_symlink(path: Path, code: str, label: str) -> bytes:
    try:
        requested = path.expanduser().absolute()
        path_stat = requested.lstat()
    except OSError as error:
        raise IntakeError(code, f"{label} path is unavailable") from error
    if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
        raise IntakeError(code, f"{label} must be a regular non-symlink file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(requested, flags)
    except OSError as error:
        raise IntakeError(code, f"{label} could not be opened safely") from error
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise IntakeError(code, f"{label} must be a regular non-symlink file")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            return stream.read()
    except OSError as error:
        raise IntakeError(code, f"{label} could not be read") from error
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _publish_new_bytes(output: Path, payload: bytes) -> None:
    try:
        output_stat = output.lstat()
    except FileNotFoundError:
        output_stat = None
    except OSError as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "output path cannot be inspected") from error
    if output_stat is not None:
        if stat.S_ISLNK(output_stat.st_mode):
            raise IntakeError("OUTPUT_UNSAFE", "symlink output paths are refused")
        raise IntakeError("OUTPUT_EXISTS", "output path already exists")

    _publish_exclusive(output, payload)


def _publish_exclusive(output: Path, payload: bytes) -> None:
    descriptor, temporary_name = _create_temporary(output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, output, follow_symlinks=False)
        except FileExistsError as error:
            raise IntakeError("OUTPUT_EXISTS", "output path already exists") from error
        except OSError as error:
            raise IntakeError(
                "OUTPUT_UNWRITABLE", "output could not be published exclusively"
            ) from error
        _fsync_directory(output.parent)
    except OSError as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "draft bytes could not be written") from error
    finally:
        with suppress(OSError):
            temporary.unlink()


def _replace_bytes_atomically(output: Path, payload: bytes) -> None:
    descriptor, temporary_name = _create_temporary(output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            current_stat = output.lstat()
        except OSError as error:
            raise IntakeError("DRAFT_UNAVAILABLE", "existing draft cannot be inspected") from error
        if stat.S_ISLNK(current_stat.st_mode) or not stat.S_ISREG(current_stat.st_mode):
            raise IntakeError("OUTPUT_UNSAFE", "draft must be a regular non-symlink file")
        os.replace(temporary, output)
        _fsync_directory(output.parent)
    except IntakeError:
        raise
    except OSError as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "draft checkpoint could not be published") from error
    finally:
        with suppress(OSError):
            temporary.unlink()


def _create_temporary(parent: Path) -> tuple[int, str]:
    try:
        return tempfile.mkstemp(prefix=".relay-intake-", dir=parent)
    except OSError as error:
        raise IntakeError("OUTPUT_UNWRITABLE", "temporary draft cannot be created") from error


def _fsync_directory(path: Path) -> None:
    if not hasattr(os, "O_DIRECTORY"):
        return
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _is_inside(path: Path, root: Path) -> bool:
    return path == root or path.is_relative_to(root)


def _normalize_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise IntakeError("CLOCK_INVALID", "intake timestamps must be timezone-aware")
    return value.astimezone(UTC)


def _unresolved(reason: str) -> UnresolvedFact:
    return UnresolvedFact(origin="UNRESOLVED", reason=reason)
