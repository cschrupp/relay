"""Immutable exact inputs and derived values for Slice 2.5 project state."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, field_validator, model_validator

from relay_engine.domain import ActorRef, CommitRef, ContentDigest, ProjectId
from relay_engine.domain._base import DomainModel, require_nonblank

type StableKey = Annotated[
    str,
    StringConstraints(
        strict=True,
        min_length=1,
        max_length=128,
        pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$",
    ),
]
type PredicateKey = StableKey


def _require_sorted_unique[T](
    values: tuple[T, ...], key: Callable[[T], str | tuple[str, ...]], label: str
) -> tuple[T, ...]:
    if len(values) != len({key(value) for value in values}):
        raise ValueError(f"{label} must be unique")
    if values != tuple(sorted(values, key=key)):
        raise ValueError(f"{label} must use canonical ordering")
    return values


def canonical_json(value: DomainModel) -> str:
    """Serialize a validated model with Relay's fixed schema-v1 JSON rules."""

    validated = type(value).model_validate(value.model_dump(mode="python"))
    payload = validated.model_dump(mode="json")
    for digest_field in ("content_digest", "snapshot_digest", "candidate_digest"):
        payload.pop(digest_field, None)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def canonical_json_bytes(value: DomainModel) -> bytes:
    """Return the canonical UTF-8 identity bytes for a model."""

    return canonical_json(value).encode("utf-8")


def digest_model(value: DomainModel) -> ContentDigest:
    """Return the SHA-256 identity of a model's canonical content."""

    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def digest_authority_content(value: DomainModel) -> ContentDigest:
    """Digest the exact normative payload while excluding its provenance links."""

    validated = type(value).model_validate(value.model_dump(mode="python"))
    payload = validated.model_dump(mode="json", exclude={"provenance"})
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def digest_source_coverage(value: SourceCoverageDeclaration) -> ContentDigest:
    """Digest a coverage declaration payload without its self-reference."""

    payload = value.model_dump(mode="json", exclude={"declaration"})
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class SourceRole(StrEnum):
    AUTHORITY = "AUTHORITY"
    HUMAN_ACCEPTANCE = "HUMAN_ACCEPTANCE"
    INDEPENDENT_EVALUATION = "INDEPENDENT_EVALUATION"
    TECHNICAL_ACCEPTANCE = "TECHNICAL_ACCEPTANCE"
    SOURCE_COVERAGE = "SOURCE_COVERAGE"
    QUALIFICATION = "QUALIFICATION"
    EVIDENCE = "EVIDENCE"
    DOMAIN = "DOMAIN"
    POLICY = "POLICY"
    SUMMARY = "SUMMARY"
    EXTERNAL_AUTHORIZATION = "EXTERNAL_AUTHORIZATION"
    EXTERNAL_FACT = "EXTERNAL_FACT"


class SourceKind(StrEnum):
    ACCEPTED_RECORD = "ACCEPTED_RECORD"
    LIVING_POLICY = "LIVING_POLICY"
    LIVING_SUMMARY = "LIVING_SUMMARY"
    GOVERNED_DOMAIN_RECORD = "GOVERNED_DOMAIN_RECORD"
    AUTHORIZED_EXTERNAL_FACT = "AUTHORIZED_EXTERNAL_FACT"


class SourceDisposition(StrEnum):
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    PROPOSED = "PROPOSED"
    REWORK = "REWORK"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN = "UNKNOWN"


class SourceAcceptance(StrEnum):
    ACCEPTED = "ACCEPTED"
    NOT_REQUIRED = "NOT_REQUIRED"
    MISSING = "MISSING"
    UNKNOWN = "UNKNOWN"


class PredicateResult(StrEnum):
    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    INDETERMINATE = "INDETERMINATE"


class InvariantDisposition(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    PROHIBITED_UNLESS_REAUTHORIZED = "PROHIBITED_UNLESS_REAUTHORIZED"


class QualificationResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ApplicabilityResult(StrEnum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INDETERMINATE = "INDETERMINATE"


class RequirementRelationKind(StrEnum):
    REQUIRES = "REQUIRES"
    FORBIDS = "FORBIDS"
    CONSUMES = "CONSUMES"
    PRODUCES = "PRODUCES"


class NegativeDisposition(StrEnum):
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    PROHIBITED_UNLESS_REAUTHORIZED = "PROHIBITED_UNLESS_REAUTHORIZED"


class ResponsibilityCollisionResult(StrEnum):
    NO_COLLISION = "NO_COLLISION"
    COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY = "COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY"
    INDETERMINATE = "INDETERMINATE"


class ConsumableState(StrEnum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    CONSUMED = "CONSUMED"
    INDETERMINATE = "INDETERMINATE"


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    BLOCKED = "BLOCKED"
    INDETERMINATE = "INDETERMINATE"


class CompilationStatus(StrEnum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    INDETERMINATE = "INDETERMINATE"


class ReasonSeverity(StrEnum):
    BLOCKER = "BLOCKER"
    UNKNOWN = "UNKNOWN"
    INFO = "INFO"


class ResolutionReasonCode(StrEnum):
    SOURCE_COVERAGE_MISSING = "SOURCE_COVERAGE_MISSING"
    SOURCE_COVERAGE_INCOMPLETE = "SOURCE_COVERAGE_INCOMPLETE"
    SOURCE_REFERENCE_MISSING = "SOURCE_REFERENCE_MISSING"
    SOURCE_REFERENCE_CONFLICT = "SOURCE_REFERENCE_CONFLICT"
    SOURCE_NOT_ACCEPTED = "SOURCE_NOT_ACCEPTED"
    BACKING_PROVENANCE_MISSING = "BACKING_PROVENANCE_MISSING"
    BACKING_PROVENANCE_INVALID = "BACKING_PROVENANCE_INVALID"
    SUMMARY_BACKING_CONFLICT = "SUMMARY_BACKING_CONFLICT"
    POLICY_SCOPE_UNAUTHORIZED = "POLICY_SCOPE_UNAUTHORIZED"
    SUBJECT_UNKNOWN = "SUBJECT_UNKNOWN"
    APPLICABILITY_MISMATCH = "APPLICABILITY_MISMATCH"
    QUALIFICATION_MISSING = "QUALIFICATION_MISSING"
    QUALIFICATION_FAILED = "QUALIFICATION_FAILED"
    QUALIFICATION_ACCEPTANCE_MISSING = "QUALIFICATION_ACCEPTANCE_MISSING"
    PREDECESSOR_MISSING = "PREDECESSOR_MISSING"
    PREDECESSOR_UNSATISFIED = "PREDECESSOR_UNSATISFIED"
    UNKNOWN_RELATION = "UNKNOWN_RELATION"
    PROHIBITED_SUBJECT = "PROHIBITED_SUBJECT"
    REAUTHORIZATION_MISSING = "REAUTHORIZATION_MISSING"
    RESPONSIBILITY_COLLISION = "RESPONSIBILITY_COLLISION"
    RESPONSIBILITY_INCOMPLETE = "RESPONSIBILITY_INCOMPLETE"
    CONSUMABLE_UNAVAILABLE = "CONSUMABLE_UNAVAILABLE"
    CONSUMPTION_UNKNOWN = "CONSUMPTION_UNKNOWN"
    EVIDENCE_LINEAGE_INCOMPLETE = "EVIDENCE_LINEAGE_INCOMPLETE"
    CONTRADICTORY_FACTS = "CONTRADICTORY_FACTS"
    REQUEST_INCOMPLETE = "REQUEST_INCOMPLETE"
    CANDIDATE_SNAPSHOT_STALE = "CANDIDATE_SNAPSHOT_STALE"
    CANDIDATE_SNAPSHOT_UNKNOWN = "CANDIDATE_SNAPSHOT_UNKNOWN"
    WORK_CONTRACT_UNREPRESENTABLE = "WORK_CONTRACT_UNREPRESENTABLE"


class SourceIdentity(DomainModel):
    """Exact stable source identity and registered content digest."""

    source_key: StableKey
    content_digest: ContentDigest


class PredicateAssertion(DomainModel):
    """One exact predicate/value assertion carried by its owning source record."""

    predicate_key: PredicateKey
    value_digest: ContentDigest


class SourceRecordRef(DomainModel):
    """Already-materialized source metadata; never discovers or reads source bytes."""

    identity: SourceIdentity
    role: SourceRole
    kind: SourceKind
    disposition: SourceDisposition
    acceptance: SourceAcceptance
    scope_key: StableKey
    assertions: tuple[PredicateAssertion, ...] = ()
    policy_key: StableKey | None = None
    policy_contract_ref: SourceIdentity | None = None
    policy_scope_keys: tuple[StableKey, ...] = ()
    delegated_policy_keys: tuple[StableKey, ...] = ()
    delegated_scope_keys: tuple[StableKey, ...] = ()
    external_authorization_ref: SourceIdentity | None = None
    authorized_external_source_keys: tuple[StableKey, ...] = ()
    authorized_predicate_keys: tuple[PredicateKey, ...] = ()

    @field_validator("assertions")
    @classmethod
    def assertions_are_canonical(
        cls, value: tuple[PredicateAssertion, ...]
    ) -> tuple[PredicateAssertion, ...]:
        return _require_sorted_unique(value, lambda item: item.predicate_key, "assertions")

    @field_validator(
        "policy_scope_keys",
        "delegated_policy_keys",
        "delegated_scope_keys",
        "authorized_external_source_keys",
        "authorized_predicate_keys",
    )
    @classmethod
    def key_tuples_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "source keys")

    @model_validator(mode="after")
    def source_kind_is_complete(self) -> SourceRecordRef:
        if self.kind is SourceKind.LIVING_SUMMARY and self.assertions:
            raise ValueError("living summaries cannot own authority assertions")
        if self.kind is SourceKind.LIVING_POLICY and (
            self.policy_key is None or self.policy_contract_ref is None
        ):
            raise ValueError("living policy requires exact policy and owner-contract refs")
        if self.kind is SourceKind.AUTHORIZED_EXTERNAL_FACT and (
            self.external_authorization_ref is None
        ):
            raise ValueError("external fact requires an exact authorization ref")
        return self


class BackingProvenanceRef(DomainModel):
    """Exact owner record and value binding for one authority-bearing predicate."""

    predicate_key: PredicateKey
    source: SourceIdentity
    value_digest: ContentDigest


class CanonicalPointer(DomainModel):
    """A pinned registry key selecting one exact current projection."""

    canonical_key: StableKey
    target: SourceIdentity


class SourceCoverageItem(DomainModel):
    """One exact required source in an accepted outcome-coverage declaration."""

    source: SourceIdentity
    role: SourceRole
    disposition: SourceDisposition
    acceptance_required: bool = True
    required_predicate_keys: tuple[PredicateKey, ...] = ()

    @field_validator("required_predicate_keys")
    @classmethod
    def predicates_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "required predicate keys")


class SourceCoverageDeclaration(DomainModel):
    """Accepted, explicit completeness declaration for one normalized outcome."""

    declaration: SourceIdentity
    outcome_key: StableKey
    scope_key: StableKey
    required_canonical_keys: tuple[StableKey, ...]
    required_sources: tuple[SourceCoverageItem, ...]
    admissible_roles: tuple[SourceRole, ...]
    authority_predicate_keys: tuple[PredicateKey, ...]
    relation_closure_complete: bool
    source_collection_complete: bool
    responsibility_inventory_complete: bool

    @field_validator("required_canonical_keys", "authority_predicate_keys")
    @classmethod
    def keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "coverage keys")

    @field_validator("required_sources")
    @classmethod
    def sources_are_canonical(
        cls, value: tuple[SourceCoverageItem, ...]
    ) -> tuple[SourceCoverageItem, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "sources")

    @field_validator("admissible_roles")
    @classmethod
    def roles_are_canonical(cls, value: tuple[SourceRole, ...]) -> tuple[SourceRole, ...]:
        return _require_sorted_unique(value, lambda item: item.value, "admissible roles")

    @property
    def content_digest(self) -> ContentDigest:
        """Return the canonical identity of this accepted declaration value."""

        return digest_source_coverage(self)


class ResolutionSnapshot(DomainModel):
    """Immutable exact source set observed by one pure resolution operation."""

    snapshot_key: StableKey
    project_id: ProjectId
    source_commit: CommitRef
    registry_digest: ContentDigest
    request_key: StableKey
    scope_key: StableKey
    canonical_pointers: tuple[CanonicalPointer, ...]
    source_refs: tuple[SourceIdentity, ...]
    authorized_observation_refs: tuple[SourceIdentity, ...] = ()
    source_collection_complete: bool

    @field_validator("canonical_pointers")
    @classmethod
    def pointers_are_canonical(
        cls, value: tuple[CanonicalPointer, ...]
    ) -> tuple[CanonicalPointer, ...]:
        return _require_sorted_unique(value, lambda item: item.canonical_key, "canonical pointers")

    @field_validator("source_refs", "authorized_observation_refs")
    @classmethod
    def refs_are_canonical(cls, value: tuple[SourceIdentity, ...]) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "source refs")

    @property
    def content_digest(self) -> ContentDigest:
        """Return the canonical identity of this exact snapshot."""

        return digest_model(self)


class SubjectValue(DomainModel):
    """One exact dimension supplied for deterministic applicability comparison."""

    dimension: StableKey
    value: str | None

    @field_validator("value")
    @classmethod
    def value_is_nonblank(cls, value: str | None) -> str | None:
        return None if value is None else require_nonblank(value)


class ProjectStateRequest(DomainModel):
    """Normalized exact request resolved without planning or authority side effects."""

    request_key: StableKey
    outcome_key: StableKey
    scope_key: StableKey
    action_key: StableKey
    actor: ActorRef
    subject: tuple[SubjectValue, ...]
    requested_predicate_keys: tuple[PredicateKey, ...] = ()
    requested_subject_keys: tuple[StableKey, ...] = ()
    responsibility_keys: tuple[StableKey, ...] = ()
    proposed_owner_key: StableKey | None = None
    intended_attempt_id: StableKey | None = None

    @field_validator("subject")
    @classmethod
    def subject_is_canonical(cls, value: tuple[SubjectValue, ...]) -> tuple[SubjectValue, ...]:
        return _require_sorted_unique(value, lambda item: item.dimension, "subject dimensions")

    @field_validator("requested_predicate_keys", "requested_subject_keys", "responsibility_keys")
    @classmethod
    def request_keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "request keys")


class ApplicabilityBinding(DomainModel):
    """Expected value and requirement flag for one applicability dimension."""

    dimension: StableKey
    expected_value: str | None
    required: bool = True

    @field_validator("expected_value")
    @classmethod
    def expected_value_is_nonblank(cls, value: str | None) -> str | None:
        return None if value is None else require_nonblank(value)


class ApplicabilityEnvelope(DomainModel):
    """Exact subset of subject dimensions that controls historical evidence use."""

    bindings: tuple[ApplicabilityBinding, ...] = ()

    @field_validator("bindings")
    @classmethod
    def bindings_are_canonical(
        cls, value: tuple[ApplicabilityBinding, ...]
    ) -> tuple[ApplicabilityBinding, ...]:
        return _require_sorted_unique(value, lambda item: item.dimension, "applicability bindings")


class ApplicabilityEvaluation(DomainModel):
    """Current applicability result while preserving the historical result."""

    result: ApplicabilityResult
    mismatched_dimensions: tuple[StableKey, ...] = ()
    unknown_dimensions: tuple[StableKey, ...] = ()

    @field_validator("mismatched_dimensions", "unknown_dimensions")
    @classmethod
    def dimensions_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "applicability dimensions")


class PredicateFact(DomainModel):
    """A supplied, exact predicate result with its owning provenance."""

    predicate_key: PredicateKey
    scope_key: StableKey
    result: PredicateResult
    value_digest: ContentDigest | None = None
    provenance: tuple[BackingProvenanceRef, ...] = ()

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(
            value, lambda item: item.source.source_key, "predicate provenance"
        )


class Invariant(DomainModel):
    """Accepted inherited rule with rationale, scope, and exact ownership refs."""

    invariant_key: StableKey
    predicate_key: PredicateKey
    statement: str
    scope_key: StableKey
    applicability: ApplicabilityEnvelope
    rationale: str
    protects_against: str
    disposition: InvariantDisposition
    provenance: tuple[BackingProvenanceRef, ...]
    supersedes_key: StableKey | None = None
    reauthorization_refs: tuple[SourceIdentity, ...] = ()

    @field_validator("statement", "rationale", "protects_against")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")

    @field_validator("reauthorization_refs")
    @classmethod
    def reauthorization_is_canonical(
        cls, value: tuple[SourceIdentity, ...]
    ) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "reauthorization refs")


class QualificationFact(DomainModel):
    """Historical qualification result plus exact subject and acceptance lineage."""

    qualification_key: StableKey
    qualification_kind: StableKey
    result: QualificationResult
    scope_key: StableKey
    applicability: ApplicabilityEnvelope
    provenance: tuple[BackingProvenanceRef, ...]
    evidence_refs: tuple[SourceIdentity, ...] = ()
    acceptance_refs: tuple[SourceIdentity, ...] = ()
    acceptance_required: bool = False
    invalidation_keys: tuple[StableKey, ...] = ()

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")

    @field_validator("evidence_refs", "acceptance_refs")
    @classmethod
    def refs_are_canonical(cls, value: tuple[SourceIdentity, ...]) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "fact refs")

    @field_validator("invalidation_keys")
    @classmethod
    def invalidations_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "invalidation keys")


class RequirementEdge(DomainModel):
    """One typed relation; raw strings preserve unknown kinds for fail-closed results."""

    edge_key: StableKey
    relation: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=1,
            max_length=64,
            pattern=r"^[A-Z][A-Z0-9_]*$",
        ),
    ]
    source_key: StableKey
    target_key: StableKey
    scope_key: StableKey
    applicability: ApplicabilityEnvelope = ApplicabilityEnvelope()
    provenance: tuple[BackingProvenanceRef, ...] = ()
    acceptance_required: bool = True
    required: bool = True
    produced_subject_digest: ContentDigest | None = None
    produced_evidence_roles: tuple[SourceRole, ...] = ()

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")

    @field_validator("produced_evidence_roles")
    @classmethod
    def produced_roles_are_canonical(cls, value: tuple[SourceRole, ...]) -> tuple[SourceRole, ...]:
        return _require_sorted_unique(value, lambda item: item.value, "produced evidence roles")


class NegativeDecision(DomainModel):
    """Exact negative disposition scoped to subjects and explicit reauthorization."""

    decision_key: StableKey
    disposition: NegativeDisposition
    target_keys: tuple[StableKey, ...]
    scope_key: StableKey
    rationale: str
    provenance: tuple[BackingProvenanceRef, ...]
    superseding_key: StableKey | None = None
    reauthorization_ref: SourceIdentity | None = None

    @field_validator("target_keys")
    @classmethod
    def targets_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "negative targets")

    @field_validator("rationale")
    @classmethod
    def rationale_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")


class ResponsibilityClaim(DomainModel):
    """Accepted owner for one normalized responsibility key and exact scope."""

    claim_key: StableKey
    responsibility_key: StableKey
    owner_key: StableKey
    scope_key: StableKey
    delegated_to: tuple[StableKey, ...] = ()
    supersedes_key: StableKey | None = None
    provenance: tuple[BackingProvenanceRef, ...]

    @field_validator("delegated_to")
    @classmethod
    def delegates_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "delegated owners")

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")


class ResponsibilityEvaluation(DomainModel):
    """Complete deterministic ownership comparison for the requested key set."""

    result: ResponsibilityCollisionResult
    proposed_keys: tuple[StableKey, ...]
    matched_claims: tuple[ResponsibilityClaim, ...] = ()
    collision_claim_keys: tuple[StableKey, ...] = ()
    unresolved_keys: tuple[StableKey, ...] = ()

    @field_validator("proposed_keys", "collision_claim_keys", "unresolved_keys")
    @classmethod
    def responsibility_keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "responsibility keys")

    @field_validator("matched_claims")
    @classmethod
    def claims_are_canonical(
        cls, value: tuple[ResponsibilityClaim, ...]
    ) -> tuple[ResponsibilityClaim, ...]:
        return _require_sorted_unique(value, lambda item: item.claim_key, "responsibility claims")


class ConsumableRef(DomainModel):
    """Exact consumable identity and scope."""

    consumable_key: StableKey
    scope_key: StableKey


class ConsumableFact(DomainModel):
    """Supplied exact consumable state; this package never mutates it."""

    ref: ConsumableRef
    state: ConsumableState
    ledger_complete: bool
    attempt_id: StableKey | None = None
    provenance: tuple[BackingProvenanceRef, ...] = ()
    evidence_refs: tuple[SourceIdentity, ...] = ()

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")

    @field_validator("evidence_refs")
    @classmethod
    def evidence_is_canonical(cls, value: tuple[SourceIdentity, ...]) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "evidence refs")


class ConsumptionRequirement(DomainModel):
    """One exact intended attempt's use of a one-shot or bounded resource."""

    consumable: ConsumableRef
    intended_attempt_id: StableKey
    provenance: tuple[BackingProvenanceRef, ...] = ()

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")


class ProducedExpectation(DomainModel):
    """Expected output identity without accepting or promoting its future result."""

    output_key: StableKey
    subject_digest: ContentDigest
    required_evidence_roles: tuple[SourceRole, ...] = ()

    @field_validator("required_evidence_roles")
    @classmethod
    def roles_are_canonical(cls, value: tuple[SourceRole, ...]) -> tuple[SourceRole, ...]:
        return _require_sorted_unique(value, lambda item: item.value, "evidence roles")


class KnowledgeDeltaKind(StrEnum):
    INVARIANT = "INVARIANT"
    PREREQUISITE = "PREREQUISITE"
    APPLICABILITY_RULE = "APPLICABILITY_RULE"
    PROHIBITION = "PROHIBITION"
    RESPONSIBILITY_CLAIM = "RESPONSIBILITY_CLAIM"
    QUALIFICATION_REQUIREMENT = "QUALIFICATION_REQUIREMENT"
    CONSUMPTION_RULE = "CONSUMPTION_RULE"


class KnowledgeDeltaProposal(DomainModel):
    """Proposal-only knowledge; never an active resolver constraint by itself."""

    delta_key: StableKey
    kind: KnowledgeDeltaKind
    exact_subject_key: StableKey
    scope_key: StableKey
    proposed_content_digest: ContentDigest
    affected_scope_keys: tuple[StableKey, ...]
    evidence_refs: tuple[SourceIdentity, ...]
    provenance: tuple[BackingProvenanceRef, ...]
    invalidation_keys: tuple[StableKey, ...] = ()

    @field_validator("affected_scope_keys", "invalidation_keys")
    @classmethod
    def keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "knowledge delta keys")

    @field_validator("evidence_refs")
    @classmethod
    def evidence_is_canonical(cls, value: tuple[SourceIdentity, ...]) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "evidence refs")

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")


class ProjectionClaimKind(StrEnum):
    NAVIGATION = "NAVIGATION"
    SELECTION = "SELECTION"
    DESCRIPTION = "DESCRIPTION"
    AUTHORITY_SUMMARY = "AUTHORITY_SUMMARY"


class ProjectionClaim(DomainModel):
    """A materialized statement from a living projection, with optional backing."""

    canonical_key: StableKey
    projection: SourceIdentity
    claim_kind: ProjectionClaimKind
    predicate_key: PredicateKey
    value_digest: ContentDigest
    backing: BackingProvenanceRef | None = None


class ResolutionReason(DomainModel):
    """Ordered blocker, unknown, or informational provenance item."""

    code: str
    severity: ReasonSeverity
    subject_key: StableKey
    detail: str
    source_refs: tuple[SourceIdentity, ...] = ()

    @field_validator("code", "detail")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("source_refs")
    @classmethod
    def refs_are_canonical(cls, value: tuple[SourceIdentity, ...]) -> tuple[SourceIdentity, ...]:
        return _require_sorted_unique(value, lambda item: item.source_key, "reason source refs")


class ResolvedRequirement(DomainModel):
    """Evaluation result for one exact typed requirement edge."""

    edge: RequirementEdge
    result: PredicateResult
    reason_codes: tuple[str, ...] = ()
    provenance: tuple[BackingProvenanceRef, ...] = ()

    @field_validator("reason_codes")
    @classmethod
    def codes_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "reason codes")

    @field_validator("provenance")
    @classmethod
    def provenance_is_canonical(
        cls, value: tuple[BackingProvenanceRef, ...]
    ) -> tuple[BackingProvenanceRef, ...]:
        return _require_sorted_unique(value, lambda item: item.source.source_key, "provenance")


class ResolvedQualification(DomainModel):
    """Historical qualification plus independently derived current applicability."""

    fact: QualificationFact
    applicability: ApplicabilityEvaluation
    accepted: PredicateResult


class ResolvedProjectState(DomainModel):
    """Rebuildable result for one request and one exact source snapshot."""

    request: ProjectStateRequest
    snapshot: ResolutionSnapshot
    source_coverage: SourceCoverageDeclaration
    status: ResolutionStatus
    predicate_facts: tuple[PredicateFact, ...] = ()
    invariants: tuple[Invariant, ...] = ()
    qualifications: tuple[ResolvedQualification, ...] = ()
    requirements: tuple[ResolvedRequirement, ...] = ()
    negative_decisions: tuple[NegativeDecision, ...] = ()
    responsibility: ResponsibilityEvaluation
    consumables: tuple[ConsumableFact, ...] = ()
    consumption_requirements: tuple[ConsumptionRequirement, ...] = ()
    produced_expectations: tuple[ProducedExpectation, ...] = ()
    knowledge_delta_proposals: tuple[KnowledgeDeltaProposal, ...] = ()
    projection_claims: tuple[ProjectionClaim, ...] = ()
    reasons: tuple[ResolutionReason, ...] = ()

    @field_validator("predicate_facts")
    @classmethod
    def facts_are_canonical(cls, value: tuple[PredicateFact, ...]) -> tuple[PredicateFact, ...]:
        return _require_sorted_unique(value, lambda item: item.predicate_key, "predicate facts")

    @field_validator("invariants")
    @classmethod
    def invariants_are_canonical(cls, value: tuple[Invariant, ...]) -> tuple[Invariant, ...]:
        return _require_sorted_unique(value, lambda item: item.invariant_key, "invariants")

    @field_validator("qualifications")
    @classmethod
    def qualifications_are_canonical(
        cls, value: tuple[ResolvedQualification, ...]
    ) -> tuple[ResolvedQualification, ...]:
        return _require_sorted_unique(
            value, lambda item: item.fact.qualification_key, "qualifications"
        )

    @field_validator("requirements")
    @classmethod
    def requirements_are_canonical(
        cls, value: tuple[ResolvedRequirement, ...]
    ) -> tuple[ResolvedRequirement, ...]:
        return _require_sorted_unique(value, lambda item: item.edge.edge_key, "requirements")

    @field_validator("negative_decisions")
    @classmethod
    def negative_decisions_are_canonical(
        cls, value: tuple[NegativeDecision, ...]
    ) -> tuple[NegativeDecision, ...]:
        return _require_sorted_unique(value, lambda item: item.decision_key, "negative decisions")

    @field_validator("consumables")
    @classmethod
    def consumables_are_canonical(
        cls, value: tuple[ConsumableFact, ...]
    ) -> tuple[ConsumableFact, ...]:
        return _require_sorted_unique(value, lambda item: item.ref.consumable_key, "consumables")

    @field_validator("consumption_requirements")
    @classmethod
    def consumption_requirements_are_canonical(
        cls, value: tuple[ConsumptionRequirement, ...]
    ) -> tuple[ConsumptionRequirement, ...]:
        return _require_sorted_unique(
            value,
            lambda item: item.consumable.consumable_key,
            "consumption requirements",
        )

    @field_validator("produced_expectations")
    @classmethod
    def produced_expectations_are_canonical(
        cls, value: tuple[ProducedExpectation, ...]
    ) -> tuple[ProducedExpectation, ...]:
        return _require_sorted_unique(value, lambda item: item.output_key, "produced expectations")

    @field_validator("knowledge_delta_proposals")
    @classmethod
    def deltas_are_canonical(
        cls, value: tuple[KnowledgeDeltaProposal, ...]
    ) -> tuple[KnowledgeDeltaProposal, ...]:
        return _require_sorted_unique(value, lambda item: item.delta_key, "knowledge deltas")

    @field_validator("projection_claims")
    @classmethod
    def projection_claims_are_canonical(
        cls, value: tuple[ProjectionClaim, ...]
    ) -> tuple[ProjectionClaim, ...]:
        return _require_sorted_unique(
            value,
            lambda item: (item.canonical_key, item.predicate_key),
            "projection claims",
        )

    @field_validator("reasons")
    @classmethod
    def reasons_are_canonical(
        cls, value: tuple[ResolutionReason, ...]
    ) -> tuple[ResolutionReason, ...]:
        return _require_sorted_unique(
            value,
            lambda item: (item.severity.value, item.code, item.subject_key, item.detail),
            "resolution reasons",
        )

    @model_validator(mode="after")
    def produced_expectations_come_from_edges(self) -> ResolvedProjectState:
        expected_by_key: dict[str, ProducedExpectation] = {}
        for requirement in self.requirements:
            edge = requirement.edge
            if (
                edge.relation != RequirementRelationKind.PRODUCES.value
                or requirement.result is not PredicateResult.SATISFIED
                or edge.produced_subject_digest is None
            ):
                continue
            expectation = ProducedExpectation(
                output_key=edge.target_key,
                subject_digest=edge.produced_subject_digest,
                required_evidence_roles=edge.produced_evidence_roles,
            )
            existing = expected_by_key.get(edge.target_key)
            if existing is not None and existing != expectation:
                raise ValueError(
                    "conflicting PRODUCES edges cannot establish one output expectation"
                )
            expected_by_key[edge.target_key] = expectation
        expected = tuple(expected_by_key[key] for key in sorted(expected_by_key))
        if self.produced_expectations != expected:
            raise ValueError("produced expectations must be derived from resolved PRODUCES edges")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        """Return this exact derived-state identity."""

        return digest_model(self)


class RoleContractReference(DomainModel):
    """Runtime-free exact identity for an applicable accepted RoleContract."""

    role_key: StableKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest


class ContractReference(DomainModel):
    """Exact reference to an existing contract without constructing its work unit."""

    contract_key: StableKey
    revision: int = Field(ge=1)
    content_digest: ContentDigest


class AuthorityCandidate(DomainModel):
    """Complete exact Human-review candidate; it contains no grant or execution state."""

    request: ProjectStateRequest
    resolution: ResolvedProjectState
    role_contract_ref: RoleContractReference
    work_contract_refs: tuple[ContractReference, ...] = ()
    work_packet_constraints: tuple[StableKey, ...]
    hard_stops: tuple[StableKey, ...] = ()
    out_of_scope_actions: tuple[StableKey, ...]

    @field_validator("work_contract_refs")
    @classmethod
    def work_refs_are_canonical(
        cls, value: tuple[ContractReference, ...]
    ) -> tuple[ContractReference, ...]:
        return _require_sorted_unique(value, lambda item: item.contract_key, "work contract refs")

    @field_validator("work_packet_constraints", "hard_stops", "out_of_scope_actions")
    @classmethod
    def candidate_keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _require_sorted_unique(value, str, "candidate keys")

    @model_validator(mode="after")
    def candidate_matches_resolution(self) -> AuthorityCandidate:
        if self.request != self.resolution.request:
            raise ValueError("candidate request must match resolved request")
        if self.resolution.status is not ResolutionStatus.RESOLVED:
            raise ValueError("only a resolved state may produce an authority candidate")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        """Return the stable identity of all exact candidate content."""

        return digest_model(self)


class AuthorityCompilation(DomainModel):
    """Tri-state compiler result; only READY carries an authority candidate."""

    status: CompilationStatus
    reasons: tuple[ResolutionReason, ...] = ()
    candidate: AuthorityCandidate | None = None
    resolution_digest: ContentDigest

    @field_validator("reasons")
    @classmethod
    def reasons_are_canonical(
        cls, value: tuple[ResolutionReason, ...]
    ) -> tuple[ResolutionReason, ...]:
        return _require_sorted_unique(
            value,
            lambda item: (item.severity.value, item.code, item.subject_key, item.detail),
            "compilation reasons",
        )

    @model_validator(mode="after")
    def candidate_matches_status(self) -> AuthorityCompilation:
        if (self.status is CompilationStatus.READY) != (self.candidate is not None):
            raise ValueError("only READY must carry a candidate")
        return self


class CandidateFreshnessStatus(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    INDETERMINATE = "INDETERMINATE"


class CandidateFreshness(DomainModel):
    """Pure comparison result for a candidate and a newly supplied snapshot."""

    status: CandidateFreshnessStatus
    candidate_digest: ContentDigest
    compared_snapshot_digest: ContentDigest | None
    reason: str


__all__ = [
    "ApplicabilityBinding",
    "ApplicabilityEnvelope",
    "ApplicabilityEvaluation",
    "ApplicabilityResult",
    "AuthorityCandidate",
    "AuthorityCompilation",
    "BackingProvenanceRef",
    "CandidateFreshness",
    "CandidateFreshnessStatus",
    "CanonicalPointer",
    "CompilationStatus",
    "ConsumableFact",
    "ConsumableRef",
    "ConsumableState",
    "ConsumptionRequirement",
    "ContractReference",
    "Invariant",
    "InvariantDisposition",
    "KnowledgeDeltaKind",
    "KnowledgeDeltaProposal",
    "NegativeDecision",
    "NegativeDisposition",
    "PredicateAssertion",
    "PredicateFact",
    "PredicateKey",
    "PredicateResult",
    "ProducedExpectation",
    "ProjectStateRequest",
    "ProjectionClaim",
    "ProjectionClaimKind",
    "QualificationFact",
    "QualificationResult",
    "ReasonSeverity",
    "RequirementEdge",
    "RequirementRelationKind",
    "ResolutionReason",
    "ResolutionReasonCode",
    "ResolutionSnapshot",
    "ResolutionStatus",
    "ResolvedProjectState",
    "ResolvedQualification",
    "ResolvedRequirement",
    "ResponsibilityClaim",
    "ResponsibilityCollisionResult",
    "ResponsibilityEvaluation",
    "RoleContractReference",
    "SourceAcceptance",
    "SourceCoverageDeclaration",
    "SourceCoverageItem",
    "SourceDisposition",
    "SourceIdentity",
    "SourceKind",
    "SourceRecordRef",
    "SourceRole",
    "StableKey",
    "SubjectValue",
    "canonical_json",
    "canonical_json_bytes",
    "digest_model",
    "digest_authority_content",
    "digest_source_coverage",
]
