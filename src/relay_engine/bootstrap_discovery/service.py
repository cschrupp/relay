"""Deterministic, read-only repository discovery and report assembly."""

import errno
import hashlib
import os
import stat
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath

from relay_engine.bootstrap_discovery.local_git import (
    LocalGitError,
    RemoteObservationData,
    inspect_local_git,
)
from relay_engine.bootstrap_discovery.models import (
    BootstrapDiscoveryReportV1,
    ConfiguredRemote,
    DiagnosticCode,
    DiagnosticSeverity,
    DiscoveryDiagnostic,
    DiscoveryStatus,
    Ecosystem,
    GitObservation,
    HumanQuestionKey,
    InspectionState,
    Language,
    LanguageSignal,
    ManifestSignal,
    ObservationEnvelope,
    RelayContractObservation,
    RelayContractStatus,
    TrackedEvidenceFile,
    canonical_json_bytes,
)
from relay_engine.repository_contract import (
    RepositoryContractError,
    parse_repository_registry,
    validate_repository_contract,
)

MAX_EVIDENCE_FILE_BYTES = 1024 * 1024
MAX_EVIDENCE_TOTAL_BYTES = 16 * 1024 * 1024

_MANIFESTS: dict[str, Ecosystem] = {
    "pyproject.toml": Ecosystem.PYTHON,
    "setup.cfg": Ecosystem.PYTHON,
    "tox.ini": Ecosystem.PYTHON,
    "uv.lock": Ecosystem.PYTHON,
    "package.json": Ecosystem.JAVASCRIPT_TYPESCRIPT,
    "package-lock.json": Ecosystem.JAVASCRIPT_TYPESCRIPT,
    "pnpm-lock.yaml": Ecosystem.JAVASCRIPT_TYPESCRIPT,
    "yarn.lock": Ecosystem.JAVASCRIPT_TYPESCRIPT,
    "cargo.toml": Ecosystem.RUST,
    "cargo.lock": Ecosystem.RUST,
    "go.mod": Ecosystem.GO,
    "go.sum": Ecosystem.GO,
    "pom.xml": Ecosystem.JVM,
    "build.gradle": Ecosystem.JVM,
    "build.gradle.kts": Ecosystem.JVM,
    "settings.gradle": Ecosystem.JVM,
    "settings.gradle.kts": Ecosystem.JVM,
}

_EXTENSION_LANGUAGES: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".pyi": Language.PYTHON,
    ".js": Language.JAVASCRIPT,
    ".jsx": Language.JAVASCRIPT,
    ".mjs": Language.JAVASCRIPT,
    ".cjs": Language.JAVASCRIPT,
    ".ts": Language.TYPESCRIPT,
    ".tsx": Language.TYPESCRIPT,
    ".mts": Language.TYPESCRIPT,
    ".cts": Language.TYPESCRIPT,
    ".rs": Language.RUST,
    ".go": Language.GO,
    ".java": Language.JAVA,
    ".kt": Language.KOTLIN,
    ".kts": Language.KOTLIN,
    ".scala": Language.SCALA,
    ".groovy": Language.GROOVY,
    ".cs": Language.CSHARP,
    ".fs": Language.FSHARP,
    ".fsi": Language.FSHARP,
    ".fsx": Language.FSHARP,
    ".vb": Language.VISUAL_BASIC,
    ".c": Language.C,
    ".h": Language.C,
    ".cc": Language.CPP,
    ".cpp": Language.CPP,
    ".cxx": Language.CPP,
    ".hpp": Language.CPP,
    ".hh": Language.CPP,
    ".hxx": Language.CPP,
}

_CI_ROOT_FILES = {
    ".gitlab-ci.yml",
    "jenkinsfile",
    "azure-pipelines.yml",
}
_DOCUMENT_PREFIXES = ("readme", "contributing", "architecture", "roadmap")
_PARTIAL_DIAGNOSTICS = {
    DiagnosticCode.FILE_TOO_LARGE,
    DiagnosticCode.FILE_UNREADABLE,
    DiagnosticCode.SYMLINK_NOT_FOLLOWED,
    DiagnosticCode.RELAY_CONTRACT_INVALID,
    DiagnosticCode.REMOTE_URL_AMBIGUOUS,
    DiagnosticCode.REMOTE_URL_CREDENTIALS_OMITTED,
}


@dataclass(frozen=True)
class _EvidenceRead:
    evidence: TrackedEvidenceFile
    bytes_read: int
    diagnostic: DiscoveryDiagnostic | None


class _SymlinkPath(Exception):
    def __init__(self, size_bytes: int | None) -> None:
        self.size_bytes = size_bytes


def inspect_repository(repository: Path, observed_at: datetime) -> BootstrapDiscoveryReportV1:
    """Inspect one local Git repository without modifying it or inferring semantics."""

    try:
        git_state = inspect_local_git(repository)
    except LocalGitError as error:
        raise BootstrapDiscoveryError(error.code, str(error)) from error

    diagnostics: list[DiscoveryDiagnostic] = []
    if git_state.branch is None:
        diagnostics.append(
            _diagnostic(
                DiagnosticCode.DETACHED_HEAD,
                "HEAD is detached.",
                DiagnosticSeverity.INFO,
            )
        )
    if git_state.dirty:
        diagnostics.append(
            _diagnostic(
                DiagnosticCode.DIRTY_WORKTREE,
                "The working tree has tracked or untracked changes.",
                DiagnosticSeverity.INFO,
            )
        )
    if not git_state.remotes:
        diagnostics.append(
            _diagnostic(
                DiagnosticCode.NO_REMOTES,
                "No Git remotes are configured.",
                DiagnosticSeverity.INFO,
            )
        )
    _append_remote_diagnostics(git_state.remotes, diagnostics)

    manifest_paths: dict[str, Ecosystem] = {}
    ci_paths: set[str] = set()
    documentation_paths: set[str] = set()
    relay_paths: set[str] = set()
    selected_paths: set[str] = set()
    for tracked_path in git_state.tracked_paths:
        ecosystem = _manifest_ecosystem(tracked_path)
        if ecosystem is not None:
            manifest_paths[tracked_path] = ecosystem
            selected_paths.add(tracked_path)
        if _is_ci_file(tracked_path):
            ci_paths.add(tracked_path)
            selected_paths.add(tracked_path)
        if _is_documentation_file(tracked_path):
            documentation_paths.add(tracked_path)
            selected_paths.add(tracked_path)
        if tracked_path.startswith(".relay/"):
            relay_paths.add(tracked_path)
            selected_paths.add(tracked_path)

    evidence_by_path: dict[str, TrackedEvidenceFile] = {}
    total_read = 0
    for relative_path in sorted(selected_paths):
        result = _read_evidence_file(
            git_state.repository_root,
            relative_path,
            MAX_EVIDENCE_TOTAL_BYTES - total_read,
        )
        total_read += result.bytes_read
        evidence_by_path[relative_path] = result.evidence
        if result.diagnostic is not None:
            diagnostics.append(result.diagnostic)

    manifests = tuple(
        ManifestSignal(ecosystem=ecosystem, evidence=evidence_by_path[path])
        for path, ecosystem in sorted(manifest_paths.items())
    )
    language_signals = _language_signals(git_state.tracked_paths, manifest_paths)
    ci_files = tuple(evidence_by_path[path] for path in sorted(ci_paths))
    documentation_files = tuple(evidence_by_path[path] for path in sorted(documentation_paths))
    relay_files = tuple(evidence_by_path[path] for path in sorted(relay_paths))
    relay_contract, contract_diagnostic = _inspect_relay_contract(git_state.repository_root)
    if contract_diagnostic is not None:
        diagnostics.append(contract_diagnostic)

    diagnostics_tuple = tuple(
        sorted(
            diagnostics,
            key=lambda item: (item.code.value, item.path or "", item.remote_name or ""),
        )
    )
    discovery_status = (
        DiscoveryStatus.PARTIAL
        if any(item.code in _PARTIAL_DIAGNOSTICS for item in diagnostics_tuple)
        else DiscoveryStatus.COMPLETE
    )
    return BootstrapDiscoveryReportV1(
        observation=ObservationEnvelope(
            observed_at=observed_at,
            repository_path=str(git_state.repository_root),
            discovery_status=discovery_status,
            diagnostics=diagnostics_tuple,
        ),
        git=GitObservation(
            head_sha=git_state.head_sha,
            branch=git_state.branch,
            detached_head=git_state.branch is None,
            dirty=git_state.dirty,
            tracked_file_count=len(git_state.tracked_paths),
            remotes=tuple(
                ConfiguredRemote(
                    name=item.name,
                    fetch_url=item.fetch_url,
                    push_url=item.push_url,
                )
                for item in git_state.remotes
            ),
        ),
        manifests=manifests,
        language_signals=language_signals,
        ci_files=ci_files,
        documentation_files=documentation_files,
        relay_files=relay_files,
        relay_contract=relay_contract,
        unresolved_human_questions=tuple(sorted(HumanQuestionKey, key=lambda item: item.value)),
    )


class BootstrapDiscoveryError(RuntimeError):
    """A hard discovery or output-boundary failure with a stable public code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def write_report_exclusive(
    report: BootstrapDiscoveryReportV1,
    output: Path,
    repository_root: Path,
) -> None:
    """Create a canonical report outside the inspected repository exactly once."""

    try:
        requested_output = output.expanduser().absolute()
        already_exists = requested_output.exists() or requested_output.is_symlink()
        resolved_root = repository_root.resolve(strict=True)
        output_path = requested_output.resolve(strict=False)
    except (OSError, RuntimeError) as error:
        raise BootstrapDiscoveryError("OUTPUT_UNWRITABLE", "output path is unavailable") from error
    if (
        requested_output == resolved_root
        or requested_output.is_relative_to(resolved_root)
        or output_path == resolved_root
        or output_path.is_relative_to(resolved_root)
    ):
        raise BootstrapDiscoveryError(
            "OUTPUT_INSIDE_REPOSITORY",
            "filesystem output must be outside the inspected repository",
        )
    if already_exists:
        raise BootstrapDiscoveryError("OUTPUT_EXISTS", "output path already exists")

    payload = canonical_report_bytes(report)
    try:
        descriptor = os.open(
            output_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o644,
        )
    except FileExistsError as error:
        raise BootstrapDiscoveryError("OUTPUT_EXISTS", "output path already exists") from error
    except OSError as error:
        raise BootstrapDiscoveryError(
            "OUTPUT_UNWRITABLE", "output path cannot be created"
        ) from error

    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
    except OSError as error:
        raise BootstrapDiscoveryError(
            "OUTPUT_UNWRITABLE", "report bytes could not be written"
        ) from error


def canonical_report_bytes(report: BootstrapDiscoveryReportV1) -> bytes:
    """Serialize a discovery report through its single canonical JSON function."""
    try:
        return canonical_json_bytes(report)
    except Exception as error:
        raise BootstrapDiscoveryError(
            "REPORT_SERIALIZATION_FAILED",
            "the validated report could not be serialized",
        ) from error


def _manifest_ecosystem(relative_path: str) -> Ecosystem | None:
    path = PurePosixPath(relative_path)
    basename = path.name.lower()
    if basename.startswith("requirements") and basename.endswith(".txt"):
        return Ecosystem.PYTHON
    if basename in _MANIFESTS:
        return _MANIFESTS[basename]
    if path.suffix.lower() in {".sln", ".csproj"}:
        return Ecosystem.DOTNET
    return None


def _is_ci_file(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    if relative_path.startswith(".github/workflows/"):
        return len(path.parts) >= 3
    if relative_path == ".circleci/config.yml":
        return True
    return path.name.lower() in _CI_ROOT_FILES


def _is_documentation_file(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    if len(path.parts) >= 2 and path.parts[0] == "docs" and path.suffix.lower() == ".md":
        return True
    basename = path.name.lower()
    return any(basename.startswith(prefix) for prefix in _DOCUMENT_PREFIXES)


def _language_signals(
    tracked_paths: tuple[str, ...],
    manifest_paths: dict[str, Ecosystem],
) -> tuple[LanguageSignal, ...]:
    paths_by_language: dict[Language, list[str]] = {}
    extensions_by_language: dict[Language, set[str]] = {}
    for relative_path in tracked_paths:
        suffix = PurePosixPath(relative_path).suffix.lower()
        language = _EXTENSION_LANGUAGES.get(suffix)
        if language is not None:
            paths_by_language.setdefault(language, []).append(relative_path)
            extensions_by_language.setdefault(language, set()).add(suffix)

    manifest_paths_by_language: dict[Language, list[str]] = {}
    manifest_language = {
        Ecosystem.PYTHON: Language.PYTHON,
        Ecosystem.JAVASCRIPT_TYPESCRIPT: Language.JAVASCRIPT_TYPESCRIPT,
        Ecosystem.RUST: Language.RUST,
        Ecosystem.GO: Language.GO,
    }
    for path, ecosystem in manifest_paths.items():
        language = manifest_language.get(ecosystem)
        if language is not None:
            manifest_paths_by_language.setdefault(language, []).append(path)

    all_languages = set(paths_by_language) | set(manifest_paths_by_language)
    return tuple(
        LanguageSignal(
            language=language,
            tracked_file_count=len(paths_by_language.get(language, [])),
            source_extensions=tuple(sorted(extensions_by_language.get(language, set()))),
            manifest_paths=tuple(sorted(manifest_paths_by_language.get(language, []))),
        )
        for language in sorted(all_languages, key=lambda item: item.value)
    )


def _read_evidence_file(
    repository_root: Path,
    relative_path: str,
    aggregate_bytes_remaining: int,
) -> _EvidenceRead:
    try:
        file_descriptor, file_stat = _open_evidence_file(repository_root, relative_path)
    except _SymlinkPath as error:
        return _EvidenceRead(
            evidence=TrackedEvidenceFile(
                relative_path=relative_path,
                sha256=None,
                size_bytes=error.size_bytes,
                inspection_state=InspectionState.SYMLINK_NOT_FOLLOWED,
            ),
            bytes_read=0,
            diagnostic=_diagnostic(
                DiagnosticCode.SYMLINK_NOT_FOLLOWED,
                "Tracked evidence is a symlink and was not followed.",
                DiagnosticSeverity.WARNING,
                path=relative_path,
            ),
        )
    except OSError, ValueError:
        return _unreadable_file(relative_path, _safe_lstat_size(repository_root, relative_path))

    try:
        size_bytes = file_stat.st_size
        if size_bytes > MAX_EVIDENCE_FILE_BYTES:
            return _too_large_file(relative_path, size_bytes, "per-file read limit")
        if size_bytes > aggregate_bytes_remaining:
            return _too_large_file(relative_path, size_bytes, "aggregate read limit")

        read_limit = min(MAX_EVIDENCE_FILE_BYTES, aggregate_bytes_remaining)
        with os.fdopen(file_descriptor, "rb") as stream:
            file_descriptor = -1
            raw = stream.read(read_limit)
            post_read_size = os.fstat(stream.fileno()).st_size
        if post_read_size > len(raw):
            return _too_large_file(
                relative_path,
                post_read_size,
                "file changed while evidence was read",
                bytes_read=len(raw),
            )
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        return _EvidenceRead(
            evidence=TrackedEvidenceFile(
                relative_path=relative_path,
                sha256=digest,
                size_bytes=len(raw),
                inspection_state=InspectionState.READ,
            ),
            bytes_read=len(raw),
            diagnostic=None,
        )
    except OSError:
        return _unreadable_file(relative_path, file_stat.st_size)
    finally:
        if file_descriptor >= 0:
            os.close(file_descriptor)


def _open_evidence_file(repository_root: Path, relative_path: str) -> tuple[int, os.stat_result]:
    parts = PurePosixPath(relative_path).parts
    if not parts or PurePosixPath(relative_path).is_absolute() or ".." in parts:
        raise ValueError("tracked path is not repository-relative")
    if os.open in os.supports_dir_fd and os.stat in os.supports_dir_fd:
        return _open_with_directory_descriptors(repository_root, parts)
    return _open_with_path_checks(repository_root, parts)


def _open_with_directory_descriptors(
    repository_root: Path,
    parts: tuple[str, ...],
) -> tuple[int, os.stat_result]:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    root_descriptor = os.open(repository_root, directory_flags)
    current_descriptor = root_descriptor
    try:
        for part in parts[:-1]:
            entry_stat = os.stat(part, dir_fd=current_descriptor, follow_symlinks=False)
            if stat.S_ISLNK(entry_stat.st_mode):
                raise _SymlinkPath(entry_stat.st_size)
            if not stat.S_ISDIR(entry_stat.st_mode):
                raise OSError(errno.ENOTDIR, "tracked path parent is not a directory")
            next_descriptor = os.open(part, directory_flags, dir_fd=current_descriptor)
            if current_descriptor != root_descriptor:
                os.close(current_descriptor)
            current_descriptor = next_descriptor

        final_stat = os.stat(parts[-1], dir_fd=current_descriptor, follow_symlinks=False)
        if stat.S_ISLNK(final_stat.st_mode):
            raise _SymlinkPath(final_stat.st_size)
        if not stat.S_ISREG(final_stat.st_mode):
            raise OSError(errno.EINVAL, "tracked evidence is not a regular file")
        file_descriptor = os.open(
            parts[-1],
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
            dir_fd=current_descriptor,
        )
        opened_stat = os.fstat(file_descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            os.close(file_descriptor)
            raise OSError(errno.EINVAL, "tracked evidence is not a regular file")
        return file_descriptor, opened_stat
    finally:
        if current_descriptor != root_descriptor:
            os.close(current_descriptor)
        os.close(root_descriptor)


def _open_with_path_checks(
    repository_root: Path,
    parts: tuple[str, ...],
) -> tuple[int, os.stat_result]:
    candidate = repository_root
    for part in parts[:-1]:
        candidate = candidate / part
        entry_stat = candidate.lstat()
        if stat.S_ISLNK(entry_stat.st_mode):
            raise _SymlinkPath(entry_stat.st_size)
        if not stat.S_ISDIR(entry_stat.st_mode):
            raise OSError(errno.ENOTDIR, "tracked path parent is not a directory")
    candidate = candidate / parts[-1]
    entry_stat = candidate.lstat()
    if stat.S_ISLNK(entry_stat.st_mode):
        raise _SymlinkPath(entry_stat.st_size)
    if not stat.S_ISREG(entry_stat.st_mode):
        raise OSError(errno.EINVAL, "tracked evidence is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    file_descriptor = os.open(candidate, flags)
    opened_stat = os.fstat(file_descriptor)
    return file_descriptor, opened_stat


def _safe_lstat_size(repository_root: Path, relative_path: str) -> int | None:
    try:
        candidate = repository_root.joinpath(*PurePosixPath(relative_path).parts)
        result = candidate.lstat()
        return result.st_size
    except OSError:
        return None


def _too_large_file(
    relative_path: str,
    size_bytes: int,
    limit_name: str,
    *,
    bytes_read: int = 0,
) -> _EvidenceRead:
    return _EvidenceRead(
        evidence=TrackedEvidenceFile(
            relative_path=relative_path,
            sha256=None,
            size_bytes=size_bytes,
            inspection_state=InspectionState.SKIPPED_TOO_LARGE,
        ),
        bytes_read=bytes_read,
        diagnostic=_diagnostic(
            DiagnosticCode.FILE_TOO_LARGE,
            f"Evidence was not retained because it exceeded the {limit_name}.",
            DiagnosticSeverity.WARNING,
            path=relative_path,
        ),
    )


def _unreadable_file(relative_path: str, size_bytes: int | None) -> _EvidenceRead:
    return _EvidenceRead(
        evidence=TrackedEvidenceFile(
            relative_path=relative_path,
            sha256=None,
            size_bytes=size_bytes,
            inspection_state=InspectionState.UNREADABLE,
        ),
        bytes_read=0,
        diagnostic=_diagnostic(
            DiagnosticCode.FILE_UNREADABLE,
            "Tracked evidence could not be read as a regular file.",
            DiagnosticSeverity.WARNING,
            path=relative_path,
        ),
    )


def _inspect_relay_contract(
    repository_root: Path,
) -> tuple[RelayContractObservation, DiscoveryDiagnostic | None]:
    relay_dir = repository_root / ".relay"
    try:
        relay_dir_stat = relay_dir.lstat()
    except FileNotFoundError:
        return RelayContractObservation(status=RelayContractStatus.ABSENT), None
    except OSError:
        return _invalid_relay_contract()
    if stat.S_ISLNK(relay_dir_stat.st_mode) or not stat.S_ISDIR(relay_dir_stat.st_mode):
        return _invalid_relay_contract()

    registry_path = repository_root / ".relay" / "registry.json"
    try:
        registry_stat = registry_path.lstat()
    except FileNotFoundError:
        return RelayContractObservation(status=RelayContractStatus.ABSENT), None
    except OSError:
        return _invalid_relay_contract()
    if stat.S_ISLNK(registry_stat.st_mode) or not stat.S_ISREG(registry_stat.st_mode):
        return _invalid_relay_contract()

    try:
        parsed = parse_repository_registry(registry_path.read_bytes())
        registry = validate_repository_contract(
            repository_root,
            parsed.project_id,
            parsed.repository,
        )
    except OSError, RepositoryContractError, ValueError:
        return _invalid_relay_contract()
    return (
        RelayContractObservation(
            status=RelayContractStatus.VALID,
            project_id=registry.project_id,
            repository=registry.repository,
            artifact_count=len(registry.artifacts),
            canonical_keys=tuple(sorted(item.canonical_key for item in registry.canonical)),
        ),
        None,
    )


def _invalid_relay_contract() -> tuple[RelayContractObservation, DiscoveryDiagnostic]:
    return (
        RelayContractObservation(status=RelayContractStatus.INVALID),
        _diagnostic(
            DiagnosticCode.RELAY_CONTRACT_INVALID,
            "The local .relay contract did not pass existing repository-contract validation.",
            DiagnosticSeverity.WARNING,
            path=".relay/registry.json",
        ),
    )


def _append_remote_diagnostics(
    remotes: tuple[RemoteObservationData, ...],
    diagnostics: list[DiscoveryDiagnostic],
) -> None:
    for remote in remotes:
        if remote.fetch_ambiguous or remote.push_ambiguous:
            diagnostics.append(
                _diagnostic(
                    DiagnosticCode.REMOTE_URL_AMBIGUOUS,
                    "A configured remote URL could not be represented as one exact value.",
                    DiagnosticSeverity.WARNING,
                    remote_name=remote.name,
                )
            )
        if remote.credentials_omitted:
            diagnostics.append(
                _diagnostic(
                    DiagnosticCode.REMOTE_URL_CREDENTIALS_OMITTED,
                    "A credential-bearing remote URL was omitted from the report.",
                    DiagnosticSeverity.WARNING,
                    remote_name=remote.name,
                )
            )


def _diagnostic(
    code: DiagnosticCode,
    message: str,
    severity: DiagnosticSeverity,
    *,
    path: str | None = None,
    remote_name: str | None = None,
) -> DiscoveryDiagnostic:
    return DiscoveryDiagnostic(
        code=code,
        severity=severity,
        message=message,
        path=path,
        remote_name=remote_name,
    )
