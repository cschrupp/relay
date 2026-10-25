"""Pure deterministic resolution over exact, already-materialized Slice 2.5 inputs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from relay_engine.project_state.models import (
    ApplicabilityEnvelope,
    ApplicabilityEvaluation,
    ApplicabilityResult,
    BackingProvenanceRef,
    ConsumableFact,
    ConsumableState,
    ConsumptionRequirement,
    Invariant,
    InvariantDisposition,
    KnowledgeDeltaProposal,
    NegativeDecision,
    NegativeDisposition,
    PredicateFact,
    PredicateResult,
    ProducedExpectation,
    ProjectionClaim,
    ProjectionClaimKind,
    ProjectStateRequest,
    QualificationFact,
    QualificationResult,
    ReasonSeverity,
    RequirementEdge,
    RequirementRelationKind,
    ResolutionReason,
    ResolutionReasonCode,
    ResolutionSnapshot,
    ResolutionStatus,
    ResolvedProjectState,
    ResolvedQualification,
    ResolvedRequirement,
    ResponsibilityClaim,
    ResponsibilityCollisionResult,
    ResponsibilityEvaluation,
    SourceAcceptance,
    SourceCoverageDeclaration,
    SourceDisposition,
    SourceIdentity,
    SourceKind,
    SourceRecordRef,
    SourceRole,
    SubjectValue,
    digest_authority_content,
)


def evaluate_applicability(
    envelope: ApplicabilityEnvelope,
    subject: tuple[SubjectValue, ...],
) -> ApplicabilityEvaluation:
    """Compare only declared dimensions, preserving mismatch versus unknown."""

    current = {item.dimension: item.value for item in subject}
    mismatched: list[str] = []
    unknown: list[str] = []
    for binding in envelope.bindings:
        if not binding.required:
            continue
        actual = current.get(binding.dimension)
        if binding.expected_value is None or actual is None:
            unknown.append(binding.dimension)
        elif actual != binding.expected_value:
            mismatched.append(binding.dimension)

    if mismatched:
        result = ApplicabilityResult.NOT_APPLICABLE
    elif unknown:
        result = ApplicabilityResult.INDETERMINATE
    else:
        result = ApplicabilityResult.APPLICABLE
    return ApplicabilityEvaluation(
        result=result,
        mismatched_dimensions=tuple(sorted(mismatched)),
        unknown_dimensions=tuple(sorted(unknown)),
    )


def _identity_matches(left: SourceIdentity, right: SourceIdentity) -> bool:
    return left.source_key == right.source_key and left.content_digest == right.content_digest


def _add_reason(
    reasons: list[ResolutionReason],
    code: ResolutionReasonCode | str,
    severity: ReasonSeverity,
    subject_key: str,
    detail: str,
    source_refs: tuple[SourceIdentity, ...] = (),
) -> None:
    canonical_refs = tuple(sorted(set(source_refs), key=lambda item: item.source_key))
    reasons.append(
        ResolutionReason(
            code=code.value if isinstance(code, ResolutionReasonCode) else code,
            severity=severity,
            subject_key=subject_key,
            detail=detail,
            source_refs=canonical_refs,
        )
    )


def _deduplicate_records[T](
    values: tuple[T, ...],
    identity: Callable[[T], str],
    *,
    label: str,
    reasons: list[ResolutionReason],
) -> tuple[tuple[T, ...], frozenset[str]]:
    grouped: dict[str, T] = {}
    conflicts: set[str] = set()
    for value in values:
        key = identity(value)
        existing = grouped.get(key)
        if existing is None:
            grouped[key] = value
        elif existing != value:
            conflicts.add(key)
    for key in sorted(conflicts):
        grouped.pop(key, None)
        _add_reason(
            reasons,
            ResolutionReasonCode.CONTRADICTORY_FACTS,
            ReasonSeverity.UNKNOWN,
            key,
            f"conflicting {label} records share one stable identity",
        )
    return tuple(grouped[key] for key in sorted(grouped)), frozenset(conflicts)


def _build_source_index(
    snapshot: ResolutionSnapshot,
    source_records: tuple[SourceRecordRef, ...],
    reasons: list[ResolutionReason],
) -> dict[str, SourceRecordRef]:
    groups: dict[str, list[SourceRecordRef]] = defaultdict(list)
    for record in source_records:
        groups[record.identity.source_key].append(record)

    index: dict[str, SourceRecordRef] = {}
    for source_key, records in groups.items():
        if len(records) != 1:
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
                ReasonSeverity.UNKNOWN,
                source_key,
                "multiple materialized records share one source identity",
                tuple(item.identity for item in records),
            )
            continue
        index[source_key] = records[0]

    expected = {item.source_key: item for item in snapshot.source_refs}
    for source_key, identity in expected.items():
        record = index.get(source_key)
        if record is None:
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_MISSING,
                ReasonSeverity.UNKNOWN,
                source_key,
                "snapshot source is absent from the materialized source records",
                (identity,),
            )
        elif not _identity_matches(record.identity, identity):
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
                ReasonSeverity.UNKNOWN,
                source_key,
                "materialized source digest differs from the pinned snapshot",
                (identity, record.identity),
            )
            index.pop(source_key, None)

    for source_key, record in index.copy().items():
        if source_key not in expected:
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_MISSING,
                ReasonSeverity.UNKNOWN,
                source_key,
                "materialized source is not part of the pinned snapshot",
                (record.identity,),
            )
            index.pop(source_key, None)
    return index


def _source_is_accepted(record: SourceRecordRef) -> bool:
    return record.disposition in {SourceDisposition.ACCEPTED, SourceDisposition.ACTIVE} and (
        record.acceptance in {SourceAcceptance.ACCEPTED, SourceAcceptance.NOT_REQUIRED}
    )


def _verify_policy_owner(
    record: SourceRecordRef,
    source_index: dict[str, SourceRecordRef],
    scope_key: str,
    predicate_key: str,
) -> bool:
    if record.kind is not SourceKind.LIVING_POLICY or record.policy_contract_ref is None:
        return False
    owner = source_index.get(record.policy_contract_ref.source_key)
    if owner is None or not _identity_matches(owner.identity, record.policy_contract_ref):
        return False
    return (
        owner.kind is SourceKind.ACCEPTED_RECORD
        and owner.role is SourceRole.AUTHORITY
        and record.role is SourceRole.POLICY
        and _source_is_accepted(owner)
        and record.policy_key in owner.delegated_policy_keys
        and predicate_key in owner.authorized_predicate_keys
        and scope_key in record.policy_scope_keys
        and scope_key in owner.delegated_scope_keys
    )


def _verify_external_authorization(
    record: SourceRecordRef,
    predicate_key: str,
    source_index: dict[str, SourceRecordRef],
) -> bool:
    if (
        record.kind is not SourceKind.AUTHORIZED_EXTERNAL_FACT
        or record.external_authorization_ref is None
    ):
        return False
    authorization = source_index.get(record.external_authorization_ref.source_key)
    if authorization is None:
        return False
    return (
        _identity_matches(authorization.identity, record.external_authorization_ref)
        and authorization.kind is SourceKind.ACCEPTED_RECORD
        and authorization.role is SourceRole.EXTERNAL_AUTHORIZATION
        and _source_is_accepted(authorization)
        and record.identity.source_key in authorization.authorized_external_source_keys
        and predicate_key in authorization.authorized_predicate_keys
    )


def _verify_backing(
    backing: BackingProvenanceRef,
    *,
    scope_key: str,
    authority_required: bool,
    source_index: dict[str, SourceRecordRef],
    snapshot: ResolutionSnapshot,
    coverage: SourceCoverageDeclaration,
) -> tuple[bool, str]:
    pinned = next(
        (item for item in snapshot.source_refs if item.source_key == backing.source.source_key),
        None,
    )
    record = source_index.get(backing.source.source_key)
    if (
        pinned is None
        or record is None
        or not _identity_matches(pinned, backing.source)
        or not _identity_matches(record.identity, backing.source)
    ):
        return False, "backing source is absent or differs from the exact snapshot"
    if record.role not in coverage.admissible_roles:
        return False, "backing source role is not admitted by source coverage"
    if record.scope_key != scope_key:
        return False, "backing source does not cover the exact requested scope"
    assertion = next(
        (item for item in record.assertions if item.predicate_key == backing.predicate_key),
        None,
    )
    if assertion is None or assertion.value_digest != backing.value_digest:
        return False, "backing source does not establish the exact predicate value"
    if record.kind is SourceKind.LIVING_SUMMARY or record.role is SourceRole.SUMMARY:
        return False, "summary projection cannot establish an authority-bearing predicate"
    if record.kind is SourceKind.LIVING_POLICY:
        if not _verify_policy_owner(record, source_index, scope_key, backing.predicate_key):
            return False, "living policy exceeds its accepted owner or scope"
    elif record.kind is SourceKind.AUTHORIZED_EXTERNAL_FACT:
        if record.role is not SourceRole.EXTERNAL_FACT or not _verify_external_authorization(
            record, backing.predicate_key, source_index
        ):
            return False, "external fact is not covered by its exact accepted authorization"
    elif authority_required:
        authority_roles = {
            SourceRole.AUTHORITY,
            SourceRole.HUMAN_ACCEPTANCE,
            SourceRole.INDEPENDENT_EVALUATION,
            SourceRole.TECHNICAL_ACCEPTANCE,
            SourceRole.QUALIFICATION,
        }
        if record.kind is not SourceKind.ACCEPTED_RECORD or record.role not in authority_roles:
            return False, "authority-bearing predicate lacks its exact owning accepted record"
    if not _source_is_accepted(record):
        return False, "backing source is not accepted and active for this predicate"
    return True, ""


def _verify_provenance(
    provenance: tuple[BackingProvenanceRef, ...],
    *,
    predicate_key: str,
    scope_key: str,
    authority_required: bool,
    subject_key: str,
    source_index: dict[str, SourceRecordRef],
    snapshot: ResolutionSnapshot,
    coverage: SourceCoverageDeclaration,
    reasons: list[ResolutionReason],
    expected_value_digest: str | None = None,
) -> bool:
    matching = tuple(item for item in provenance if item.predicate_key == predicate_key)
    if not matching:
        _add_reason(
            reasons,
            ResolutionReasonCode.BACKING_PROVENANCE_MISSING,
            ReasonSeverity.UNKNOWN,
            subject_key,
            f"predicate {predicate_key} has no exact owning provenance",
        )
        return False
    if expected_value_digest is not None and any(
        item.value_digest != expected_value_digest for item in matching
    ):
        _add_reason(
            reasons,
            ResolutionReasonCode.BACKING_PROVENANCE_INVALID,
            ReasonSeverity.UNKNOWN,
            subject_key,
            "backing assertion digest does not bind the exact normative typed content",
            tuple(item.source for item in matching),
        )
        return False
    valid = True
    for backing in matching:
        ok, detail = _verify_backing(
            backing,
            scope_key=scope_key,
            authority_required=authority_required,
            source_index=source_index,
            snapshot=snapshot,
            coverage=coverage,
        )
        if not ok:
            valid = False
            code = (
                ResolutionReasonCode.POLICY_SCOPE_UNAUTHORIZED
                if "policy" in detail
                else ResolutionReasonCode.BACKING_PROVENANCE_INVALID
            )
            _add_reason(
                reasons,
                code,
                ReasonSeverity.UNKNOWN,
                subject_key,
                detail,
                (backing.source,),
            )
    return valid


def _verify_coverage(
    request: ProjectStateRequest,
    snapshot: ResolutionSnapshot,
    coverage: SourceCoverageDeclaration,
    source_index: dict[str, SourceRecordRef],
    reasons: list[ResolutionReason],
) -> None:
    if snapshot.request_key != request.request_key or snapshot.scope_key != request.scope_key:
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
            ReasonSeverity.UNKNOWN,
            request.request_key,
            "snapshot is bound to a different request or scope",
        )
    if coverage.outcome_key != request.outcome_key or coverage.scope_key != request.scope_key:
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_COVERAGE_MISSING,
            ReasonSeverity.UNKNOWN,
            request.outcome_key,
            "source-coverage declaration does not cover the exact requested outcome and scope",
            (coverage.declaration,),
        )
    if not snapshot.source_collection_complete or not coverage.source_collection_complete:
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_COVERAGE_INCOMPLETE,
            ReasonSeverity.UNKNOWN,
            request.outcome_key,
            "the exact source collection is not declared complete",
            (coverage.declaration,),
        )
    if not coverage.relation_closure_complete:
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_COVERAGE_INCOMPLETE,
            ReasonSeverity.UNKNOWN,
            request.outcome_key,
            "predecessor/evidence/qualification/prohibition/responsibility closure is incomplete",
            (coverage.declaration,),
        )

    declaration_record = source_index.get(coverage.declaration.source_key)
    if coverage.content_digest != coverage.declaration.content_digest:
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
            ReasonSeverity.UNKNOWN,
            request.outcome_key,
            "coverage declaration payload does not match its exact self-excluding digest",
            (coverage.declaration,),
        )
    if (
        declaration_record is None
        or not _identity_matches(declaration_record.identity, coverage.declaration)
        or declaration_record.role is not SourceRole.SOURCE_COVERAGE
        or declaration_record.kind is not SourceKind.ACCEPTED_RECORD
        or not _source_is_accepted(declaration_record)
    ):
        _add_reason(
            reasons,
            ResolutionReasonCode.SOURCE_COVERAGE_MISSING,
            ReasonSeverity.UNKNOWN,
            request.outcome_key,
            "coverage declaration lacks its exact accepted owning record",
            (coverage.declaration,),
        )

    pointer_by_key = {item.canonical_key: item for item in snapshot.canonical_pointers}
    for canonical_key in coverage.required_canonical_keys:
        pointer = pointer_by_key.get(canonical_key)
        if pointer is None:
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_MISSING,
                ReasonSeverity.UNKNOWN,
                canonical_key,
                "required canonical pointer is absent from the pinned registry snapshot",
            )
            continue
        record = source_index.get(pointer.target.source_key)
        if (
            record is None
            or not _identity_matches(record.identity, pointer.target)
            or record.kind not in {SourceKind.LIVING_POLICY, SourceKind.LIVING_SUMMARY}
        ):
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_MISSING,
                ReasonSeverity.UNKNOWN,
                canonical_key,
                "canonical pointer does not select an exact materialized living projection",
                (pointer.target,),
            )

    for item in coverage.required_sources:
        record = source_index.get(item.source.source_key)
        if record is None or not _identity_matches(record.identity, item.source):
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_MISSING,
                ReasonSeverity.UNKNOWN,
                item.source.source_key,
                "required source is missing or differs from the pinned exact reference",
                (item.source,),
            )
            continue
        if record.role is not item.role or record.disposition is not item.disposition:
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
                ReasonSeverity.UNKNOWN,
                item.source.source_key,
                "required source role or disposition differs from its coverage declaration",
                (item.source,),
            )
        if item.acceptance_required and record.acceptance not in {
            SourceAcceptance.ACCEPTED,
            SourceAcceptance.NOT_REQUIRED,
        }:
            severity = (
                ReasonSeverity.BLOCKER
                if record.acceptance is SourceAcceptance.MISSING
                else ReasonSeverity.UNKNOWN
            )
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_NOT_ACCEPTED,
                severity,
                item.source.source_key,
                "required source acceptance is absent or cannot be established",
                (item.source,),
            )


def _reason_for_applicability(
    reasons: list[ResolutionReason],
    evaluation: ApplicabilityEvaluation,
    subject_key: str,
    source_refs: tuple[SourceIdentity, ...],
    *,
    required: bool,
) -> None:
    if not required or evaluation.result is ApplicabilityResult.APPLICABLE:
        return
    if evaluation.result is ApplicabilityResult.NOT_APPLICABLE:
        _add_reason(
            reasons,
            ResolutionReasonCode.APPLICABILITY_MISMATCH,
            ReasonSeverity.BLOCKER,
            subject_key,
            "required evidence applies to a different exact subject",
            source_refs,
        )
    else:
        _add_reason(
            reasons,
            ResolutionReasonCode.SUBJECT_UNKNOWN,
            ReasonSeverity.UNKNOWN,
            subject_key,
            "a required applicability dimension is unknown",
            source_refs,
        )


def _verify_qualification_evidence(
    fact: QualificationFact,
    *,
    source_index: dict[str, SourceRecordRef],
    snapshot: ResolutionSnapshot,
    reasons: list[ResolutionReason],
) -> bool:
    if not fact.evidence_refs:
        _add_reason(
            reasons,
            ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
            ReasonSeverity.UNKNOWN,
            fact.qualification_key,
            "qualification has no exact supporting evidence references",
            tuple(item.source for item in fact.provenance),
        )
        return False

    valid = True
    pinned_refs = {item.source_key: item for item in snapshot.source_refs}
    for evidence_ref in fact.evidence_refs:
        record = source_index.get(evidence_ref.source_key)
        assertion = (
            None
            if record is None
            else next(
                (
                    item
                    for item in record.assertions
                    if item.predicate_key == f"evidence-for-{fact.qualification_key}"
                ),
                None,
            )
        )
        if (
            record is None
            or pinned_refs.get(evidence_ref.source_key) != evidence_ref
            or record.identity != evidence_ref
            or record.role is not SourceRole.EVIDENCE
            or record.scope_key != fact.scope_key
            or not _source_is_accepted(record)
            or assertion is None
            or assertion.value_digest != evidence_ref.content_digest
        ):
            valid = False
            _add_reason(
                reasons,
                ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                ReasonSeverity.UNKNOWN,
                fact.qualification_key,
                "qualification evidence is absent, out of scope, or not bound to its exact subject",
                (evidence_ref,),
            )
    return valid


def _verify_qualification_acceptance(
    fact: QualificationFact,
    *,
    source_index: dict[str, SourceRecordRef],
    snapshot: ResolutionSnapshot,
) -> bool:
    pinned_refs = {item.source_key: item for item in snapshot.source_refs}
    expected_digest = digest_authority_content(fact)
    if not fact.acceptance_refs:
        return False
    for acceptance_ref in fact.acceptance_refs:
        record = source_index.get(acceptance_ref.source_key)
        assertion = (
            None
            if record is None
            else next(
                (
                    item
                    for item in record.assertions
                    if item.predicate_key == f"accepts-{fact.qualification_key}"
                ),
                None,
            )
        )
        if (
            record is None
            or pinned_refs.get(acceptance_ref.source_key) != acceptance_ref
            or record.identity != acceptance_ref
            or record.role
            not in {
                SourceRole.HUMAN_ACCEPTANCE,
                SourceRole.TECHNICAL_ACCEPTANCE,
                SourceRole.INDEPENDENT_EVALUATION,
            }
            or record.scope_key != fact.scope_key
            or not _source_is_accepted(record)
            or assertion is None
            or assertion.value_digest != expected_digest
        ):
            return False
    return True


def _evaluate_responsibility(
    request: ProjectStateRequest,
    claims: tuple[ResponsibilityClaim, ...],
    coverage: SourceCoverageDeclaration,
    source_index: dict[str, SourceRecordRef],
    snapshot: ResolutionSnapshot,
    reasons: list[ResolutionReason],
) -> ResponsibilityEvaluation:
    if not request.responsibility_keys:
        return ResponsibilityEvaluation(
            result=ResponsibilityCollisionResult.NO_COLLISION, proposed_keys=()
        )

    if not coverage.responsibility_inventory_complete or request.proposed_owner_key is None:
        _add_reason(
            reasons,
            ResolutionReasonCode.RESPONSIBILITY_INCOMPLETE,
            ReasonSeverity.UNKNOWN,
            request.request_key,
            "proposed responsibility keys, owner, or accepted owner inventory is incomplete",
        )
        return ResponsibilityEvaluation(
            result=ResponsibilityCollisionResult.INDETERMINATE,
            proposed_keys=request.responsibility_keys,
            unresolved_keys=request.responsibility_keys,
        )

    accepted_claims: list[ResponsibilityClaim] = []
    unresolved: list[str] = []
    collisions: list[str] = []
    for claim in claims:
        if claim.responsibility_key not in request.responsibility_keys:
            continue
        if claim.scope_key != request.scope_key:
            continue
        valid = _verify_provenance(
            claim.provenance,
            predicate_key=f"responsibility-{claim.claim_key}",
            scope_key=claim.scope_key,
            authority_required=True,
            subject_key=claim.claim_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(claim),
        )
        if not valid:
            unresolved.append(claim.responsibility_key)
            continue
        accepted_claims.append(claim)
        if (
            claim.owner_key != request.proposed_owner_key
            and request.proposed_owner_key not in claim.delegated_to
        ):
            collisions.append(claim.claim_key)

    known_keys = {claim.responsibility_key for claim in accepted_claims}
    for key in request.responsibility_keys:
        if key not in known_keys:
            unresolved.append(key)

    if collisions:
        result = ResponsibilityCollisionResult.COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY
        _add_reason(
            reasons,
            ResolutionReasonCode.RESPONSIBILITY_COLLISION,
            ReasonSeverity.BLOCKER,
            request.request_key,
            "an accepted owner conflicts with the proposed owner for an overlapping responsibility",
            tuple(
                ref
                for claim in accepted_claims
                if claim.claim_key in collisions
                for item in claim.provenance
                for ref in (item.source,)
            ),
        )
    elif unresolved:
        result = ResponsibilityCollisionResult.INDETERMINATE
        _add_reason(
            reasons,
            ResolutionReasonCode.RESPONSIBILITY_INCOMPLETE,
            ReasonSeverity.UNKNOWN,
            request.request_key,
            "accepted responsibility ownership is incomplete for the proposed key set",
        )
    else:
        result = ResponsibilityCollisionResult.NO_COLLISION

    return ResponsibilityEvaluation(
        result=result,
        proposed_keys=request.responsibility_keys,
        matched_claims=tuple(sorted(accepted_claims, key=lambda item: item.claim_key)),
        collision_claim_keys=tuple(sorted(collisions)),
        unresolved_keys=tuple(sorted(set(unresolved))),
    )


def resolve_project_state(
    request: ProjectStateRequest,
    snapshot: ResolutionSnapshot,
    source_coverage: SourceCoverageDeclaration,
    *,
    source_records: tuple[SourceRecordRef, ...],
    predicate_facts: tuple[PredicateFact, ...] = (),
    invariants: tuple[Invariant, ...] = (),
    qualification_facts: tuple[QualificationFact, ...] = (),
    requirement_edges: tuple[RequirementEdge, ...] = (),
    negative_decisions: tuple[NegativeDecision, ...] = (),
    responsibility_claims: tuple[ResponsibilityClaim, ...] = (),
    consumable_facts: tuple[ConsumableFact, ...] = (),
    knowledge_delta_proposals: tuple[KnowledgeDeltaProposal, ...] = (),
    projection_claims: tuple[ProjectionClaim, ...] = (),
) -> ResolvedProjectState:
    """Resolve a closed exact input set without discovery, I/O, or authority effects."""

    reasons: list[ResolutionReason] = []
    invariants, _ = _deduplicate_records(
        invariants,
        lambda item: item.invariant_key,
        label="invariant",
        reasons=reasons,
    )
    qualification_facts, conflicting_qualifications = _deduplicate_records(
        qualification_facts,
        lambda item: item.qualification_key,
        label="qualification",
        reasons=reasons,
    )
    requirement_edges, _ = _deduplicate_records(
        requirement_edges,
        lambda item: item.edge_key,
        label="requirement edge",
        reasons=reasons,
    )
    negative_decisions, _ = _deduplicate_records(
        negative_decisions,
        lambda item: item.decision_key,
        label="negative decision",
        reasons=reasons,
    )
    responsibility_claims, _ = _deduplicate_records(
        responsibility_claims,
        lambda item: item.claim_key,
        label="responsibility claim",
        reasons=reasons,
    )
    knowledge_delta_proposals, _ = _deduplicate_records(
        knowledge_delta_proposals,
        lambda item: item.delta_key,
        label="Knowledge Delta proposal",
        reasons=reasons,
    )
    projection_claims, _ = _deduplicate_records(
        projection_claims,
        lambda item: f"{item.canonical_key}:{item.predicate_key}",
        label="projection claim",
        reasons=reasons,
    )
    consumable_facts, _ = _deduplicate_records(
        consumable_facts,
        lambda item: item.ref.consumable_key,
        label="consumable",
        reasons=reasons,
    )
    source_index = _build_source_index(snapshot, source_records, reasons)
    _verify_coverage(request, snapshot, source_coverage, source_index, reasons)

    required_predicates = set(source_coverage.authority_predicate_keys)
    required_predicates.update(request.requested_predicate_keys)
    for item in source_coverage.required_sources:
        required_predicates.update(item.required_predicate_keys)

    pointer_targets = {
        pointer.canonical_key: pointer.target for pointer in snapshot.canonical_pointers
    }
    for claim in projection_claims:
        source = source_index.get(claim.projection.source_key)
        selected = pointer_targets.get(claim.canonical_key)
        if (
            source is None
            or selected is None
            or not _identity_matches(source.identity, claim.projection)
            or not _identity_matches(selected, claim.projection)
            or source.kind not in {SourceKind.LIVING_SUMMARY, SourceKind.LIVING_POLICY}
        ):
            _add_reason(
                reasons,
                ResolutionReasonCode.SOURCE_REFERENCE_CONFLICT,
                ReasonSeverity.UNKNOWN,
                claim.predicate_key,
                "projection claim is not from the exact pointer-selected living source",
                (claim.projection,),
            )
            continue
        if claim.claim_kind is ProjectionClaimKind.AUTHORITY_SUMMARY:
            if claim.backing is None:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.BACKING_PROVENANCE_MISSING,
                    ReasonSeverity.UNKNOWN,
                    claim.predicate_key,
                    "authority-bearing summary claim has no exact backing record",
                    (claim.projection,),
                )
                continue
            if claim.backing.value_digest != claim.value_digest:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.SUMMARY_BACKING_CONFLICT,
                    ReasonSeverity.UNKNOWN,
                    claim.predicate_key,
                    "summary value contradicts its exact backing record",
                    (claim.projection, claim.backing.source),
                )
            _verify_provenance(
                (claim.backing,),
                predicate_key=claim.predicate_key,
                scope_key=request.scope_key,
                authority_required=claim.predicate_key in required_predicates,
                subject_key=claim.predicate_key,
                source_index=source_index,
                snapshot=snapshot,
                coverage=source_coverage,
                reasons=reasons,
            )

    resolved_negative_decisions: list[NegativeDecision] = []
    superseded_targets: dict[str, str | None] = {}
    for decision in negative_decisions:
        if (
            decision.disposition is not NegativeDisposition.SUPERSEDED
            or decision.scope_key != request.scope_key
            or not set(decision.target_keys).intersection(request.requested_subject_keys)
        ):
            continue
        valid = _verify_provenance(
            decision.provenance,
            predicate_key=f"negative-decision-{decision.decision_key}",
            scope_key=decision.scope_key,
            authority_required=True,
            subject_key=decision.decision_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(decision),
        )
        if not valid:
            continue
        resolved_negative_decisions.append(decision)
        for target_key in decision.target_keys:
            superseded_targets[target_key] = decision.superseding_key

    facts_by_key: dict[str, PredicateFact] = {}
    conflicting_fact_keys: set[str] = set()
    for fact in predicate_facts:
        existing = facts_by_key.get(fact.predicate_key)
        if existing is None:
            facts_by_key[fact.predicate_key] = fact
        elif existing != fact:
            conflicting_fact_keys.add(fact.predicate_key)
    for key in sorted(conflicting_fact_keys):
        facts_by_key.pop(key, None)
        _add_reason(
            reasons,
            ResolutionReasonCode.CONTRADICTORY_FACTS,
            ReasonSeverity.UNKNOWN,
            key,
            "conflicting predicate facts share one stable identity",
        )

    resolved_facts: list[PredicateFact] = []
    for key, fact in sorted(facts_by_key.items()):
        if fact.scope_key != request.scope_key:
            _add_reason(
                reasons,
                ResolutionReasonCode.BACKING_PROVENANCE_INVALID,
                ReasonSeverity.UNKNOWN,
                key,
                "predicate fact scope differs from the exact requested scope",
            )
            continue
        valid = _verify_provenance(
            fact.provenance,
            predicate_key=fact.predicate_key,
            scope_key=fact.scope_key,
            authority_required=key in required_predicates,
            subject_key=key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(fact),
        )
        if key in required_predicates and fact.value_digest is None:
            valid = False
            _add_reason(
                reasons,
                ResolutionReasonCode.BACKING_PROVENANCE_INVALID,
                ReasonSeverity.UNKNOWN,
                key,
                "predicate value does not match its exact backing value digest",
                tuple(item.source for item in fact.provenance),
            )
        if not valid:
            continue
        if key in superseded_targets:
            continue
        if key in required_predicates:
            if fact.result is PredicateResult.UNSATISFIED:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_UNSATISFIED,
                    ReasonSeverity.BLOCKER,
                    key,
                    "required predicate is known unsatisfied",
                    tuple(item.source for item in fact.provenance),
                )
            elif fact.result is PredicateResult.INDETERMINATE:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    key,
                    "required predicate is unresolved",
                    tuple(item.source for item in fact.provenance),
                )
        resolved_facts.append(fact)

    resolved_facts_by_key = {fact.predicate_key: fact for fact in resolved_facts}

    for key in sorted(required_predicates):
        if key in superseded_targets:
            if key in request.requested_predicate_keys:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_UNSATISFIED,
                    ReasonSeverity.BLOCKER,
                    key,
                    "the exact requested prior subject is superseded and cannot be current",
                )
            continue
        if (
            key not in facts_by_key
            and key not in conflicting_fact_keys
            and key not in conflicting_qualifications
            and not any(item.qualification_key == key for item in qualification_facts)
        ):
            if source_coverage.source_collection_complete and snapshot.source_collection_complete:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_MISSING,
                    ReasonSeverity.BLOCKER,
                    key,
                    "complete declared source closure establishes the required predicate is absent",
                )
            else:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    key,
                    "required predicate is absent from an incomplete source closure",
                )

    resolved_invariants: list[Invariant] = []
    for invariant in invariants:
        if invariant.scope_key != request.scope_key:
            continue
        valid = _verify_provenance(
            invariant.provenance,
            predicate_key=invariant.predicate_key,
            scope_key=invariant.scope_key,
            authority_required=True,
            subject_key=invariant.invariant_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(invariant),
        )
        if not valid:
            continue
        applicability = evaluate_applicability(invariant.applicability, request.subject)
        _reason_for_applicability(
            reasons,
            applicability,
            invariant.invariant_key,
            tuple(item.source for item in invariant.provenance),
            required=invariant.predicate_key in required_predicates,
        )
        if applicability.result is ApplicabilityResult.INDETERMINATE:
            continue
        if applicability.result is ApplicabilityResult.NOT_APPLICABLE:
            continue
        if invariant.disposition is InvariantDisposition.ACTIVE:
            resolved_invariants.append(invariant)
        elif (
            invariant.disposition
            in {
                InvariantDisposition.REJECTED,
                InvariantDisposition.PROHIBITED_UNLESS_REAUTHORIZED,
            }
            and invariant.predicate_key in request.requested_predicate_keys
        ):
            _add_reason(
                reasons,
                ResolutionReasonCode.PROHIBITED_SUBJECT,
                ReasonSeverity.BLOCKER,
                invariant.invariant_key,
                "matching invariant disposition prohibits the requested predicate",
                tuple(item.source for item in invariant.provenance),
            )

    resolved_qualifications: list[ResolvedQualification] = []
    qualification_by_key = {item.qualification_key: item for item in qualification_facts}
    for fact in qualification_facts:
        valid = fact.scope_key == request.scope_key and _verify_provenance(
            fact.provenance,
            predicate_key=f"qualification-{fact.qualification_key}",
            scope_key=fact.scope_key,
            authority_required=True,
            subject_key=fact.qualification_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(fact),
        )
        if fact.scope_key != request.scope_key:
            _add_reason(
                reasons,
                ResolutionReasonCode.BACKING_PROVENANCE_INVALID,
                ReasonSeverity.UNKNOWN,
                fact.qualification_key,
                "qualification scope differs from the exact requested scope",
            )
        evidence_valid = _verify_qualification_evidence(
            fact,
            source_index=source_index,
            snapshot=snapshot,
            reasons=reasons,
        )
        valid = valid and evidence_valid
        applicability = evaluate_applicability(fact.applicability, request.subject)
        applicable_required = (
            fact.qualification_key in required_predicates
            or any(
                edge.target_key == fact.qualification_key
                and edge.relation == RequirementRelationKind.REQUIRES.value
                for edge in requirement_edges
            )
            or fact.qualification_key in superseded_targets.values()
        )
        _reason_for_applicability(
            reasons,
            applicability,
            fact.qualification_key,
            tuple(item.source for item in fact.provenance),
            required=applicable_required,
        )
        acceptance_result = PredicateResult.SATISFIED
        if fact.acceptance_required:
            if not fact.acceptance_refs:
                acceptance_result = (
                    PredicateResult.UNSATISFIED
                    if source_coverage.source_collection_complete
                    else PredicateResult.INDETERMINATE
                )
            elif _verify_qualification_acceptance(
                fact,
                source_index=source_index,
                snapshot=snapshot,
            ):
                acceptance_result = PredicateResult.SATISFIED
            else:
                acceptance_result = PredicateResult.INDETERMINATE
        if not valid:
            acceptance_result = PredicateResult.INDETERMINATE
        if applicable_required:
            if applicability.result is ApplicabilityResult.NOT_APPLICABLE:
                acceptance_result = PredicateResult.UNSATISFIED
            elif applicability.result is ApplicabilityResult.INDETERMINATE:
                acceptance_result = PredicateResult.INDETERMINATE
            elif fact.result is QualificationResult.FAIL:
                acceptance_result = PredicateResult.UNSATISFIED
            elif fact.result is QualificationResult.UNKNOWN:
                acceptance_result = PredicateResult.INDETERMINATE
            elif acceptance_result is PredicateResult.UNSATISFIED:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.QUALIFICATION_ACCEPTANCE_MISSING,
                    ReasonSeverity.BLOCKER,
                    fact.qualification_key,
                    "required qualification acceptance is known absent",
                    fact.acceptance_refs,
                )
            elif acceptance_result is PredicateResult.INDETERMINATE:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.QUALIFICATION_ACCEPTANCE_MISSING,
                    ReasonSeverity.UNKNOWN,
                    fact.qualification_key,
                    "required qualification acceptance cannot be established",
                    fact.acceptance_refs,
                )
            elif not valid:
                acceptance_result = PredicateResult.INDETERMINATE
            elif fact.result is QualificationResult.PASS:
                acceptance_result = PredicateResult.SATISFIED
        resolved = ResolvedQualification(
            fact=fact,
            applicability=applicability,
            accepted=acceptance_result,
        )
        resolved_qualifications.append(resolved)
        if applicable_required and acceptance_result is PredicateResult.UNSATISFIED:
            _add_reason(
                reasons,
                ResolutionReasonCode.QUALIFICATION_FAILED,
                ReasonSeverity.BLOCKER,
                fact.qualification_key,
                "required qualification is absent, failed, stale, or unaccepted",
                tuple(item.source for item in fact.provenance) + fact.acceptance_refs,
            )
        elif applicable_required and acceptance_result is PredicateResult.INDETERMINATE:
            _add_reason(
                reasons,
                ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                ReasonSeverity.UNKNOWN,
                fact.qualification_key,
                "required qualification result or provenance is unresolved",
                tuple(item.source for item in fact.provenance) + fact.acceptance_refs,
            )

    resolved_consumables: list[ConsumableFact] = []
    consumable_by_key = {fact.ref.consumable_key: fact for fact in consumable_facts}
    for key, fact in sorted(consumable_by_key.items()):
        if fact.ref.scope_key != request.scope_key:
            _add_reason(
                reasons,
                ResolutionReasonCode.BACKING_PROVENANCE_INVALID,
                ReasonSeverity.UNKNOWN,
                key,
                "consumable scope differs from the exact requested scope",
            )
            continue
        valid = _verify_provenance(
            fact.provenance,
            predicate_key=f"consumable-{key}",
            scope_key=fact.ref.scope_key,
            authority_required=True,
            subject_key=key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(fact),
        )
        if not valid:
            continue
        if not fact.ledger_complete or fact.state is ConsumableState.INDETERMINATE:
            _add_reason(
                reasons,
                ResolutionReasonCode.CONSUMPTION_UNKNOWN,
                ReasonSeverity.UNKNOWN,
                key,
                "consumption ledger or state is incomplete",
                tuple(item.source for item in fact.provenance),
            )
        resolved_consumables.append(fact)
    resolved_consumables_by_key = {fact.ref.consumable_key: fact for fact in resolved_consumables}

    resolved_requirements: list[ResolvedRequirement] = []
    consumption_requirements_by_key: dict[str, ConsumptionRequirement] = {}
    conflicting_consumption_keys: set[str] = set()
    produced_by_key: dict[str, ProducedExpectation] = {}
    conflicting_output_keys: set[str] = set()
    produced_edge_indexes: dict[str, int] = {}
    for edge in requirement_edges:
        if edge.scope_key != request.scope_key:
            continue
        relation = None
        try:
            relation = RequirementRelationKind(edge.relation)
        except ValueError:
            _add_reason(
                reasons,
                ResolutionReasonCode.UNKNOWN_RELATION,
                ReasonSeverity.UNKNOWN,
                edge.edge_key,
                f"unsupported requirement relation: {edge.relation}",
                tuple(item.source for item in edge.provenance),
            )
            resolved_requirements.append(
                ResolvedRequirement(
                    edge=edge,
                    result=PredicateResult.INDETERMINATE,
                    reason_codes=(ResolutionReasonCode.UNKNOWN_RELATION.value,),
                    provenance=edge.provenance,
                )
            )
            continue

        edge_provenance_ok = _verify_provenance(
            edge.provenance,
            predicate_key=f"requirement-{edge.edge_key}",
            scope_key=edge.scope_key,
            authority_required=True,
            subject_key=edge.edge_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(edge),
        )
        applicability = evaluate_applicability(edge.applicability, request.subject)
        _reason_for_applicability(
            reasons,
            applicability,
            edge.edge_key,
            tuple(item.source for item in edge.provenance),
            required=edge.required,
        )
        if applicability.result is ApplicabilityResult.NOT_APPLICABLE:
            resolved_requirements.append(
                ResolvedRequirement(
                    edge=edge,
                    result=PredicateResult.SATISFIED,
                    provenance=edge.provenance,
                )
            )
            continue
        if applicability.result is ApplicabilityResult.INDETERMINATE or not edge_provenance_ok:
            resolved_requirements.append(
                ResolvedRequirement(
                    edge=edge,
                    result=PredicateResult.INDETERMINATE,
                    provenance=edge.provenance,
                )
            )
            continue

        result = PredicateResult.SATISFIED
        reason_codes: tuple[str, ...] = ()
        if relation is RequirementRelationKind.REQUIRES:
            superseded_target = edge.target_key in superseded_targets
            predecessor_key = (
                superseded_targets.get(edge.target_key) if superseded_target else edge.target_key
            )
            fact = None if predecessor_key is None else resolved_facts_by_key.get(predecessor_key)
            qualification = (
                None if predecessor_key is None else qualification_by_key.get(predecessor_key)
            )
            if fact is not None:
                result = fact.result
            elif qualification is not None:
                resolved_qualification = next(
                    item
                    for item in resolved_qualifications
                    if item.fact.qualification_key == predecessor_key
                )
                result = resolved_qualification.accepted
            elif predecessor_key in conflicting_qualifications or superseded_target:
                result = PredicateResult.INDETERMINATE
            elif snapshot.source_collection_complete and source_coverage.source_collection_complete:
                result = PredicateResult.UNSATISFIED
                reason_codes = (ResolutionReasonCode.PREDECESSOR_MISSING.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_MISSING,
                    ReasonSeverity.BLOCKER,
                    edge.target_key,
                    "complete source closure establishes the required predecessor is absent",
                    tuple(item.source for item in edge.provenance),
                )
            else:
                result = PredicateResult.INDETERMINATE
                reason_codes = (ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE.value,)
            if result is PredicateResult.UNSATISFIED and not reason_codes:
                reason_codes = (ResolutionReasonCode.PREDECESSOR_UNSATISFIED.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_UNSATISFIED,
                    ReasonSeverity.BLOCKER,
                    edge.target_key,
                    "required predecessor is known unsatisfied or unaccepted",
                    tuple(item.source for item in edge.provenance),
                )
            elif result is PredicateResult.INDETERMINATE:
                reason_codes = (ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    edge.target_key,
                    "required predecessor cannot be established",
                    tuple(item.source for item in edge.provenance),
                )
        elif relation is RequirementRelationKind.FORBIDS:
            if edge.target_key in request.requested_subject_keys:
                result = PredicateResult.UNSATISFIED
                reason_codes = (ResolutionReasonCode.PROHIBITED_SUBJECT.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PROHIBITED_SUBJECT,
                    ReasonSeverity.BLOCKER,
                    edge.target_key,
                    "requested subject matches an active FORBIDS edge",
                    tuple(item.source for item in edge.provenance),
                )
        elif relation is RequirementRelationKind.CONSUMES:
            fact = resolved_consumables_by_key.get(edge.target_key)
            if (
                fact is None
                or not fact.ledger_complete
                or fact.state is ConsumableState.INDETERMINATE
            ):
                result = PredicateResult.INDETERMINATE
                reason_codes = (ResolutionReasonCode.CONSUMPTION_UNKNOWN.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.CONSUMPTION_UNKNOWN,
                    ReasonSeverity.UNKNOWN,
                    edge.target_key,
                    "required consumable has no complete exact state",
                    () if fact is None else tuple(item.source for item in fact.provenance),
                )
            elif fact.state is not ConsumableState.AVAILABLE:
                result = PredicateResult.UNSATISFIED
                reason_codes = (ResolutionReasonCode.CONSUMABLE_UNAVAILABLE.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.CONSUMABLE_UNAVAILABLE,
                    ReasonSeverity.BLOCKER,
                    edge.target_key,
                    "required consumable is reserved or already consumed",
                    tuple(item.source for item in fact.provenance),
                )
            elif request.intended_attempt_id is None:
                result = PredicateResult.INDETERMINATE
                reason_codes = (ResolutionReasonCode.REQUEST_INCOMPLETE.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.REQUEST_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    edge.target_key,
                    "consumption requires an exact intended attempt identity",
                )
            else:
                consumption = ConsumptionRequirement(
                    consumable=fact.ref,
                    intended_attempt_id=request.intended_attempt_id,
                    provenance=edge.provenance,
                )
                existing = consumption_requirements_by_key.get(edge.target_key)
                if edge.target_key in conflicting_consumption_keys:
                    result = PredicateResult.INDETERMINATE
                elif existing is None:
                    consumption_requirements_by_key[edge.target_key] = consumption
                elif existing != consumption:
                    consumption_requirements_by_key.pop(edge.target_key)
                    conflicting_consumption_keys.add(edge.target_key)
                    result = PredicateResult.INDETERMINATE
                    _add_reason(
                        reasons,
                        ResolutionReasonCode.CONSUMPTION_UNKNOWN,
                        ReasonSeverity.UNKNOWN,
                        edge.target_key,
                        "conflicting consumption requirements share one exact consumable",
                        tuple(item.source for item in edge.provenance),
                    )
        elif relation is RequirementRelationKind.PRODUCES:
            if edge.produced_subject_digest is None:
                result = PredicateResult.INDETERMINATE
                reason_codes = (ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE.value,)
                _add_reason(
                    reasons,
                    ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    edge.edge_key,
                    "PRODUCES edge lacks an exact output subject digest",
                    tuple(item.source for item in edge.provenance),
                )
            else:
                result = PredicateResult.SATISFIED
                expected_output = ProducedExpectation(
                    output_key=edge.target_key,
                    subject_digest=edge.produced_subject_digest,
                    required_evidence_roles=edge.produced_evidence_roles,
                )
                existing_output = produced_by_key.get(edge.target_key)
                if edge.target_key in conflicting_output_keys:
                    result = PredicateResult.INDETERMINATE
                elif existing_output is None:
                    produced_by_key[edge.target_key] = expected_output
                elif existing_output != expected_output:
                    produced_by_key.pop(edge.target_key)
                    conflicting_output_keys.add(edge.target_key)
                    result = PredicateResult.INDETERMINATE
                    previous_index = produced_edge_indexes.pop(edge.target_key, None)
                    if previous_index is not None:
                        previous = resolved_requirements[previous_index]
                        resolved_requirements[previous_index] = previous.model_copy(
                            update={
                                "result": PredicateResult.INDETERMINATE,
                                "reason_codes": (ResolutionReasonCode.CONTRADICTORY_FACTS.value,),
                            }
                        )
                    _add_reason(
                        reasons,
                        ResolutionReasonCode.CONTRADICTORY_FACTS,
                        ReasonSeverity.UNKNOWN,
                        edge.target_key,
                        "conflicting production expectations share one output identity",
                        tuple(item.source for item in edge.provenance),
                    )

        resolved_requirements.append(
            ResolvedRequirement(
                edge=edge,
                result=result,
                reason_codes=reason_codes,
                provenance=edge.provenance,
            )
        )
        if relation is RequirementRelationKind.PRODUCES and result is PredicateResult.SATISFIED:
            produced_edge_indexes[edge.target_key] = len(resolved_requirements) - 1

    for decision in negative_decisions:
        if decision.scope_key != request.scope_key:
            continue
        if not set(decision.target_keys).intersection(request.requested_subject_keys):
            continue
        if decision.disposition is NegativeDisposition.SUPERSEDED:
            if decision not in resolved_negative_decisions:
                continue
            successor_fact = (
                None
                if decision.superseding_key is None
                else resolved_facts_by_key.get(decision.superseding_key)
            )
            successor_qualification = next(
                (
                    item
                    for item in resolved_qualifications
                    if item.fact.qualification_key == decision.superseding_key
                ),
                None,
            )
            if successor_fact is not None and successor_fact.result is PredicateResult.UNSATISFIED:
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_UNSATISFIED,
                    ReasonSeverity.BLOCKER,
                    decision.superseding_key or decision.decision_key,
                    "the exact accepted successor is known unsatisfied",
                    tuple(item.source for item in decision.provenance),
                )
            elif successor_qualification is not None and (
                successor_qualification.accepted is PredicateResult.UNSATISFIED
            ):
                _add_reason(
                    reasons,
                    ResolutionReasonCode.PREDECESSOR_UNSATISFIED,
                    ReasonSeverity.BLOCKER,
                    decision.superseding_key or decision.decision_key,
                    "the exact accepted successor qualification is known unsatisfied",
                    tuple(item.source for item in decision.provenance),
                )
            elif not (
                successor_fact is not None and successor_fact.result is PredicateResult.SATISFIED
            ) and not (
                successor_qualification is not None
                and successor_qualification.accepted is PredicateResult.SATISFIED
            ):
                _add_reason(
                    reasons,
                    ResolutionReasonCode.EVIDENCE_LINEAGE_INCOMPLETE,
                    ReasonSeverity.UNKNOWN,
                    decision.decision_key,
                    "the exact accepted successor for this superseded subject is unresolved",
                    tuple(item.source for item in decision.provenance),
                )
            continue
        valid = _verify_provenance(
            decision.provenance,
            predicate_key=f"negative-decision-{decision.decision_key}",
            scope_key=decision.scope_key,
            authority_required=True,
            subject_key=decision.decision_key,
            source_index=source_index,
            snapshot=snapshot,
            coverage=source_coverage,
            reasons=reasons,
            expected_value_digest=digest_authority_content(decision),
        )
        if not valid:
            continue
        resolved_negative_decisions.append(decision)
        if decision.reauthorization_ref is None:
            _add_reason(
                reasons,
                ResolutionReasonCode.PROHIBITED_SUBJECT,
                ReasonSeverity.BLOCKER,
                decision.decision_key,
                "matching rejected/prohibited subject lacks exact reauthorization",
                tuple(item.source for item in decision.provenance),
            )
        else:
            reauthorization = source_index.get(decision.reauthorization_ref.source_key)
            if (
                reauthorization is None
                or not _identity_matches(reauthorization.identity, decision.reauthorization_ref)
                or reauthorization.role is not SourceRole.HUMAN_ACCEPTANCE
                or not _source_is_accepted(reauthorization)
                or reauthorization.scope_key != request.scope_key
                or not any(
                    assertion.predicate_key == f"reauthorize-{decision.decision_key}"
                    and assertion.value_digest == digest_authority_content(decision)
                    for assertion in reauthorization.assertions
                )
            ):
                _add_reason(
                    reasons,
                    ResolutionReasonCode.REAUTHORIZATION_MISSING,
                    ReasonSeverity.BLOCKER,
                    decision.decision_key,
                    "explicit reauthorization is not an exact accepted Human authority record",
                    (decision.reauthorization_ref,),
                )

    responsibility = _evaluate_responsibility(
        request,
        responsibility_claims,
        source_coverage,
        source_index,
        snapshot,
        reasons,
    )

    for delta in knowledge_delta_proposals:
        _add_reason(
            reasons,
            "KNOWLEDGE_DELTA_PROPOSAL_ONLY",
            ReasonSeverity.INFO,
            delta.delta_key,
            "proposal is retained as evidence and is not an active constraint",
            delta.evidence_refs,
        )

    if any(item.severity is ReasonSeverity.BLOCKER for item in reasons):
        status = ResolutionStatus.BLOCKED
    elif any(item.severity is ReasonSeverity.UNKNOWN for item in reasons):
        status = ResolutionStatus.INDETERMINATE
    else:
        status = ResolutionStatus.RESOLVED

    return ResolvedProjectState(
        request=request,
        snapshot=snapshot,
        source_coverage=source_coverage,
        status=status,
        predicate_facts=tuple(sorted(resolved_facts, key=lambda item: item.predicate_key)),
        invariants=tuple(sorted(resolved_invariants, key=lambda item: item.invariant_key)),
        qualifications=tuple(
            sorted(resolved_qualifications, key=lambda item: item.fact.qualification_key)
        ),
        requirements=tuple(sorted(resolved_requirements, key=lambda item: item.edge.edge_key)),
        negative_decisions=tuple(
            sorted(resolved_negative_decisions, key=lambda item: item.decision_key)
        ),
        responsibility=responsibility,
        consumables=tuple(sorted(resolved_consumables, key=lambda item: item.ref.consumable_key)),
        consumption_requirements=tuple(
            consumption_requirements_by_key[key] for key in sorted(consumption_requirements_by_key)
        ),
        produced_expectations=tuple(produced_by_key[key] for key in sorted(produced_by_key)),
        knowledge_delta_proposals=tuple(
            sorted(knowledge_delta_proposals, key=lambda item: item.delta_key)
        ),
        projection_claims=tuple(
            sorted(projection_claims, key=lambda item: (item.canonical_key, item.predicate_key))
        ),
        reasons=tuple(
            sorted(
                set(reasons),
                key=lambda item: (
                    item.severity.value,
                    item.code,
                    item.subject_key,
                    item.detail,
                ),
            )
        ),
    )


__all__ = ["evaluate_applicability", "resolve_project_state"]
