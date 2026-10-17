"""Typed, deterministic output models for local repository discovery."""

import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from relay_engine.domain import ProjectId, RepositoryRef

type Sha256Digest = Annotated[str, Field(pattern=r"^sha256:[0-9a-f]{64}$")]
type CommitSha = Annotated[str, Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")]


class DiscoveryModel(BaseModel):
    """Strict immutable base for the versioned discovery report."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
    )


class DiscoveryStatus(StrEnum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"


class InspectionState(StrEnum):
    READ = "READ"
    SKIPPED_TOO_LARGE = "SKIPPED_TOO_LARGE"
    SYMLINK_NOT_FOLLOWED = "SYMLINK_NOT_FOLLOWED"
    UNREADABLE = "UNREADABLE"


class Ecosystem(StrEnum):
    PYTHON = "PYTHON"
    JAVASCRIPT_TYPESCRIPT = "JAVASCRIPT_TYPESCRIPT"
    RUST = "RUST"
    GO = "GO"
    JVM = "JVM"
    DOTNET = "DOTNET"


class Language(StrEnum):
    PYTHON = "PYTHON"
    JAVASCRIPT = "JAVASCRIPT"
    TYPESCRIPT = "TYPESCRIPT"
    JAVASCRIPT_TYPESCRIPT = "JAVASCRIPT_TYPESCRIPT"
    RUST = "RUST"
    GO = "GO"
    JAVA = "JAVA"
    KOTLIN = "KOTLIN"
    SCALA = "SCALA"
    GROOVY = "GROOVY"
    CSHARP = "CSHARP"
    FSHARP = "FSHARP"
    VISUAL_BASIC = "VISUAL_BASIC"
    C = "C"
    CPP = "CPP"


class HumanQuestionKey(StrEnum):
    PROJECT_OBJECTIVE = "PROJECT_OBJECTIVE"
    CURRENT_STATUS = "CURRENT_STATUS"
    HUMAN_OBJECTIVE = "HUMAN_OBJECTIVE"
    CONSTRAINTS = "CONSTRAINTS"
    CURRENT_FRONTIER = "CURRENT_FRONTIER"
    CANONICAL_REPOSITORY_CONFIRMATION = "CANONICAL_REPOSITORY_CONFIRMATION"


class DiagnosticCode(StrEnum):
    DETACHED_HEAD = "DETACHED_HEAD"
    NO_REMOTES = "NO_REMOTES"
    DIRTY_WORKTREE = "DIRTY_WORKTREE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_UNREADABLE = "FILE_UNREADABLE"
    SYMLINK_NOT_FOLLOWED = "SYMLINK_NOT_FOLLOWED"
    RELAY_CONTRACT_INVALID = "RELAY_CONTRACT_INVALID"
    REMOTE_URL_AMBIGUOUS = "REMOTE_URL_AMBIGUOUS"
    REMOTE_URL_CREDENTIALS_OMITTED = "REMOTE_URL_CREDENTIALS_OMITTED"
    TRACKED_PATH_UNSUPPORTED = "TRACKED_PATH_UNSUPPORTED"


class DiagnosticSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"


class DiscoveryDiagnostic(DiscoveryModel):
    code: DiagnosticCode
    severity: DiagnosticSeverity
    message: str
    path: str | None = None
    remote_name: str | None = None


class ObservationEnvelope(DiscoveryModel):
    observed_at: datetime
    repository_path: str
    discovery_status: DiscoveryStatus
    diagnostics: tuple[DiscoveryDiagnostic, ...]

    @field_validator("observed_at")
    @classmethod
    def observed_at_is_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def diagnostics_are_sorted(self) -> ObservationEnvelope:
        expected = tuple(
            sorted(
                self.diagnostics,
                key=lambda item: (item.code.value, item.path or "", item.remote_name or ""),
            )
        )
        if self.diagnostics != expected:
            raise ValueError("diagnostics must use normative code/path/remote ordering")
        return self


class ConfiguredRemote(DiscoveryModel):
    name: str
    fetch_url: str | None
    push_url: str | None


class GitObservation(DiscoveryModel):
    head_sha: CommitSha
    branch: str | None
    detached_head: bool
    dirty: bool
    tracked_file_count: int = Field(ge=0)
    remotes: tuple[ConfiguredRemote, ...]

    @model_validator(mode="after")
    def branch_matches_detached_state(self) -> GitObservation:
        if self.detached_head != (self.branch is None):
            raise ValueError("branch and detached_head must agree")
        if self.remotes != tuple(sorted(self.remotes, key=lambda item: item.name)):
            raise ValueError("remotes must be sorted by name")
        return self


class TrackedEvidenceFile(DiscoveryModel):
    relative_path: str
    sha256: Sha256Digest | None
    size_bytes: int | None = Field(default=None, ge=0)
    inspection_state: InspectionState

    @model_validator(mode="after")
    def digest_matches_inspection_state(self) -> TrackedEvidenceFile:
        if (self.inspection_state is InspectionState.READ) != (self.sha256 is not None):
            raise ValueError("only successfully read evidence may have a content digest")
        return self


class ManifestSignal(DiscoveryModel):
    ecosystem: Ecosystem
    evidence: TrackedEvidenceFile


class LanguageSignal(DiscoveryModel):
    language: Language
    tracked_file_count: int = Field(ge=0)
    source_extensions: tuple[str, ...]
    manifest_paths: tuple[str, ...]

    @model_validator(mode="after")
    def evidence_is_sorted(self) -> LanguageSignal:
        if self.source_extensions != tuple(sorted(set(self.source_extensions))):
            raise ValueError("source_extensions must be unique and sorted")
        if self.manifest_paths != tuple(sorted(set(self.manifest_paths))):
            raise ValueError("manifest_paths must be unique and sorted")
        if self.tracked_file_count == 0 and not self.manifest_paths:
            raise ValueError("a language signal requires an extension or manifest observation")
        return self


class RelayContractStatus(StrEnum):
    ABSENT = "ABSENT"
    VALID = "VALID"
    INVALID = "INVALID"


class RelayContractObservation(DiscoveryModel):
    status: RelayContractStatus
    project_id: ProjectId | None = None
    repository: RepositoryRef | None = None
    artifact_count: int | None = Field(default=None, ge=0)
    canonical_keys: tuple[str, ...] | None = None

    @model_validator(mode="after")
    def contract_details_match_status(self) -> RelayContractObservation:
        has_details = all(
            value is not None
            for value in (
                self.project_id,
                self.repository,
                self.artifact_count,
                self.canonical_keys,
            )
        )
        if (self.status is RelayContractStatus.VALID) != has_details:
            raise ValueError("only a valid Relay contract may expose parsed details")
        if self.canonical_keys is not None and self.canonical_keys != tuple(
            sorted(set(self.canonical_keys))
        ):
            raise ValueError("canonical_keys must be unique and sorted")
        return self


class BootstrapDiscoveryReportV1(DiscoveryModel):
    format: Literal["relay-bootstrap-discovery"] = "relay-bootstrap-discovery"
    schema_version: Literal[1] = 1
    observation: ObservationEnvelope
    git: GitObservation
    manifests: tuple[ManifestSignal, ...]
    language_signals: tuple[LanguageSignal, ...]
    ci_files: tuple[TrackedEvidenceFile, ...]
    documentation_files: tuple[TrackedEvidenceFile, ...]
    relay_files: tuple[TrackedEvidenceFile, ...]
    relay_contract: RelayContractObservation
    unresolved_human_questions: tuple[HumanQuestionKey, ...]

    @model_validator(mode="after")
    def collections_are_sorted(self) -> BootstrapDiscoveryReportV1:
        if self.manifests != tuple(
            sorted(self.manifests, key=lambda item: item.evidence.relative_path)
        ):
            raise ValueError("manifests must be sorted by path")
        if self.language_signals != tuple(
            sorted(self.language_signals, key=lambda item: item.language.value)
        ):
            raise ValueError("language_signals must be sorted by language")
        for name in ("ci_files", "documentation_files", "relay_files"):
            files = getattr(self, name)
            if files != tuple(sorted(files, key=lambda item: item.relative_path)):
                raise ValueError(f"{name} must be sorted by path")
        expected_questions = tuple(
            sorted(self.unresolved_human_questions, key=lambda item: item.value)
        )
        if self.unresolved_human_questions != expected_questions:
            raise ValueError("unresolved_human_questions must be sorted by key")
        return self


def canonical_json_bytes(report: BootstrapDiscoveryReportV1) -> bytes:
    """Serialize a validated report with deterministic UTF-8 JSON bytes."""

    payload = report.model_dump(mode="json")
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
