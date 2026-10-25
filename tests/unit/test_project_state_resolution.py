"""Deterministic source resolution, provenance, and applicability tests."""

from __future__ import annotations

import hashlib
import inspect

import pytest
from pydantic import ValidationError

from relay_engine.domain import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.domain._base import DomainModel
from relay_engine.domain.ids import new_id
from relay_engine.project_state import (
    ApplicabilityBinding,
    ApplicabilityEnvelope,
    BackingProvenanceRef,
    CanonicalPointer,
    ConsumableFact,
    ConsumableRef,
    ConsumableState,
    Invariant,
    InvariantDisposition,
    KnowledgeDeltaKind,
    KnowledgeDeltaProposal,
    NegativeDecision,
    NegativeDisposition,
    PredicateAssertion,
    PredicateFact,
    PredicateResult,
    ProducedExpectation,
    ProjectionClaim,
    ProjectionClaimKind,
    ProjectStateRequest,
    QualificationFact,
    QualificationResult,
    RequirementEdge,
    ResolutionSnapshot,
    ResolutionStatus,
    ResolvedProjectState,
    ResponsibilityClaim,
    SourceAcceptance,
    SourceCoverageDeclaration,
    SourceCoverageItem,
    SourceDisposition,
    SourceIdentity,
    SourceKind,
    SourceRecordRef,
    SourceRole,
    SubjectValue,
    digest_authority_content,
    evaluate_applicability,
    resolve_project_state,
)

_A = "sha256:" + "a" * 64
_B = "sha256:" + "b" * 64


def _identity(key: str, digest: str = _A) -> SourceIdentity:
    return SourceIdentity(source_key=key, content_digest=digest)


def _case(
    *,
    requested: tuple[str, ...] = (),
    subject: tuple[SubjectValue, ...] = (),
    source_complete: bool = True,
) -> tuple[
    ProjectStateRequest,
    ResolutionSnapshot,
    SourceCoverageDeclaration,
    tuple[SourceRecordRef, ...],
    SourceRecordRef,
]:
    request = ProjectStateRequest(
        request_key="request-a",
        outcome_key="live-confirmation",
        scope_key="wellplot",
        action_key="confirm-live",
        actor=ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN),
        subject=subject,
        requested_predicate_keys=tuple(sorted(requested)),
        intended_attempt_id="attempt-a",
    )
    summary = SourceRecordRef(
        identity=_identity("baseline"),
        role=SourceRole.SUMMARY,
        kind=SourceKind.LIVING_SUMMARY,
        disposition=SourceDisposition.ACTIVE,
        acceptance=SourceAcceptance.NOT_REQUIRED,
        scope_key="wellplot",
    )
    assertions = tuple(
        PredicateAssertion(predicate_key=key, value_digest=_B)
        for key in sorted(
            set(requested)
            | {
                "invariant-live",
                "requirement-edge-a",
                "requirement-produce-edge",
                "requirement-consume-edge",
                "qualification-smoke-qualification",
                "negative-decision-ban-fallback",
                "responsibility-runtime-owner",
                "consumable-one-shot",
                "deployment",
            }
        )
    )
    authority = SourceRecordRef(
        identity=_identity("authority"),
        role=SourceRole.AUTHORITY,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=assertions,
    )
    coverage_source = _identity("coverage")
    coverage = SourceCoverageDeclaration(
        declaration=coverage_source,
        outcome_key="live-confirmation",
        scope_key="wellplot",
        required_canonical_keys=("current-baseline",),
        required_sources=(
            SourceCoverageItem(
                source=authority.identity,
                role=SourceRole.AUTHORITY,
                disposition=SourceDisposition.ACCEPTED,
                required_predicate_keys=(),
            ),
        ),
        admissible_roles=(SourceRole.AUTHORITY, SourceRole.SOURCE_COVERAGE),
        authority_predicate_keys=tuple(sorted(requested)),
        relation_closure_complete=True,
        source_collection_complete=source_complete,
        responsibility_inventory_complete=True,
    )
    coverage_identity = _identity("coverage", _coverage_digest(coverage))
    coverage = coverage.model_copy(update={"declaration": coverage_identity})
    coverage_record = SourceRecordRef(
        identity=coverage_identity,
        role=SourceRole.SOURCE_COVERAGE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
    )
    records = (summary, authority, coverage_record)
    repository = RepositoryRef(id=new_id("repo_"), host="example.test", path="relay")
    snapshot = ResolutionSnapshot(
        snapshot_key="snapshot-a",
        project_id=new_id("prj_"),
        source_commit=CommitRef(repository=repository, sha="1" * 40),
        registry_digest=_A,
        request_key=request.request_key,
        scope_key=request.scope_key,
        canonical_pointers=(
            CanonicalPointer(canonical_key="current-baseline", target=summary.identity),
        ),
        source_refs=tuple(
            sorted((item.identity for item in records), key=lambda item: item.source_key)
        ),
        source_collection_complete=source_complete,
    )
    return request, snapshot, coverage, records, authority


def _coverage_digest(coverage: SourceCoverageDeclaration) -> str:
    payload = coverage.model_dump(mode="json", exclude={"declaration"})
    import json

    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _proof(record: SourceRecordRef, key: str) -> BackingProvenanceRef:
    return BackingProvenanceRef(predicate_key=key, source=record.identity, value_digest=_B)


def _bind(record: SourceRecordRef, key: str, value: DomainModel):
    digest = digest_authority_content(value)
    assertions = {item.predicate_key: item for item in record.assertions}
    assertions[key] = PredicateAssertion(predicate_key=key, value_digest=digest)
    updated_record = record.model_copy(
        update={"assertions": tuple(assertions[name] for name in sorted(assertions))}
    )
    proof = BackingProvenanceRef(
        predicate_key=key,
        source=updated_record.identity,
        value_digest=digest,
    )
    return updated_record, value.model_copy(update={"provenance": (proof,)})


def _replace_authority(records, authority):
    return records[0], authority, *records[2:]


def _add_source(snapshot, records, source):
    updated_snapshot = snapshot.model_copy(
        update={
            "source_refs": tuple(
                sorted(
                    snapshot.source_refs + (source.identity,),
                    key=lambda item: item.source_key,
                )
            )
        }
    )
    return updated_snapshot, records + (source,)


def _resolve(request, snapshot, coverage, records, **kwargs):
    return resolve_project_state(
        request,
        snapshot,
        coverage,
        source_records=records,
        **kwargs,
    )


def test_closed_exact_source_set_resolves_and_is_deterministic() -> None:
    request, snapshot, coverage, records, _ = _case()
    first = _resolve(request, snapshot, coverage, records)
    second = _resolve(request, snapshot, coverage, records)
    assert first.status is ResolutionStatus.RESOLVED
    assert first.content_digest == second.content_digest
    assert first.snapshot == snapshot


def test_missing_coverage_and_source_refs_are_indeterminate() -> None:
    request, snapshot, coverage, records, _ = _case()
    absent = _resolve(request, snapshot, coverage, records[:-1])
    assert absent.status is ResolutionStatus.INDETERMINATE
    assert any(reason.code == "SOURCE_COVERAGE_MISSING" for reason in absent.reasons)

    incomplete = _resolve(
        request,
        snapshot.model_copy(update={"source_collection_complete": False}),
        coverage.model_copy(update={"source_collection_complete": False}),
        records,
    )
    assert incomplete.status is ResolutionStatus.INDETERMINATE
    assert any(reason.code == "SOURCE_COVERAGE_INCOMPLETE" for reason in incomplete.reasons)


def test_pointer_is_selection_only_and_summary_needs_exact_backing() -> None:
    request, snapshot, coverage, records, _ = _case(requested=("live-accepted",))
    claim = ProjectionClaim(
        canonical_key="current-baseline",
        projection=snapshot.canonical_pointers[0].target,
        claim_kind=ProjectionClaimKind.AUTHORITY_SUMMARY,
        predicate_key="live-accepted",
        value_digest=_B,
    )
    unresolved = _resolve(
        request,
        snapshot,
        coverage.model_copy(update={"source_collection_complete": False}),
        records,
        projection_claims=(claim,),
    )
    assert unresolved.status is ResolutionStatus.INDETERMINATE
    assert any(reason.code == "BACKING_PROVENANCE_MISSING" for reason in unresolved.reasons)

    backing = _proof(records[1], "live-accepted")
    conflicted = claim.model_copy(update={"value_digest": _A, "backing": backing})
    contradiction = _resolve(
        request,
        snapshot,
        coverage.model_copy(update={"source_collection_complete": False}),
        records,
        projection_claims=(conflicted,),
    )
    assert contradiction.status is ResolutionStatus.INDETERMINATE
    assert any(reason.code == "SUMMARY_BACKING_CONFLICT" for reason in contradiction.reasons)
    conflict_reason = next(
        reason for reason in contradiction.reasons if reason.code == "SUMMARY_BACKING_CONFLICT"
    )
    assert {ref.source_key for ref in conflict_reason.source_refs} == {"baseline", "authority"}


@pytest.mark.parametrize(
    ("expected", "actual", "result"),
    [
        ("linux", "linux", "APPLICABLE"),
        ("linux", "windows", "NOT_APPLICABLE"),
        ("linux", None, "INDETERMINATE"),
    ],
)
def test_applicability_distinguishes_match_mismatch_and_unknown(expected, actual, result) -> None:
    envelope = ApplicabilityEnvelope(
        bindings=(ApplicabilityBinding(dimension="runtime", expected_value=expected),)
    )
    subject = () if actual is None else (SubjectValue(dimension="runtime", value=actual),)
    assert evaluate_applicability(envelope, subject).result.value == result


def test_required_predicate_requires_accepted_exact_backing() -> None:
    request, snapshot, coverage, records, authority = _case(requested=("smoke-accepted",))
    fact = PredicateFact(
        predicate_key="smoke-accepted",
        scope_key="wellplot",
        result=PredicateResult.SATISFIED,
        value_digest=_B,
    )
    authority, fact = _bind(authority, "smoke-accepted", fact)
    records = _replace_authority(records, authority)
    resolved = _resolve(request, snapshot, coverage, records, predicate_facts=(fact,))
    assert resolved.status is ResolutionStatus.RESOLVED
    assert resolved.predicate_facts == (fact,)

    bad_fact = fact.model_copy(update={"result": PredicateResult.UNSATISFIED})
    rejected = _resolve(request, snapshot, coverage, records, predicate_facts=(bad_fact,))
    assert rejected.status is ResolutionStatus.INDETERMINATE


def test_conflicting_exact_facts_are_unknown_not_known_absent() -> None:
    request, snapshot, coverage, records, authority = _case(requested=("smoke-accepted",))
    first = PredicateFact(
        predicate_key="smoke-accepted",
        scope_key="wellplot",
        result=PredicateResult.SATISFIED,
        value_digest=_B,
    )
    authority, first = _bind(authority, "smoke-accepted", first)
    records = _replace_authority(records, authority)
    second = first.model_copy(update={"result": PredicateResult.UNSATISFIED})
    result = _resolve(
        request,
        snapshot,
        coverage,
        records,
        predicate_facts=(first, second),
    )
    assert result.status is ResolutionStatus.INDETERMINATE
    assert any(reason.code == "CONTRADICTORY_FACTS" for reason in result.reasons)
    assert not any(reason.code == "PREDECESSOR_MISSING" for reason in result.reasons)


def test_backing_source_from_another_scope_cannot_establish_a_required_fact() -> None:
    request, snapshot, coverage, records, authority = _case(requested=("smoke-accepted",))
    foreign_authority = authority.model_copy(update={"scope_key": "tension"})
    records = records[:1] + (foreign_authority,) + records[2:]
    fact = PredicateFact(
        predicate_key="smoke-accepted",
        scope_key="wellplot",
        result=PredicateResult.SATISFIED,
        value_digest=_B,
    )
    foreign_authority, fact = _bind(foreign_authority, "smoke-accepted", fact)
    records = _replace_authority(records, foreign_authority)
    result = _resolve(request, snapshot, coverage, records, predicate_facts=(fact,))
    assert result.status is ResolutionStatus.INDETERMINATE
    assert any(
        reason.code == "BACKING_PROVENANCE_INVALID" and "exact requested scope" in reason.detail
        for reason in result.reasons
    )


def test_invariants_qualifications_and_invalidation_are_subject_scoped() -> None:
    request, snapshot, coverage, records, authority = _case(
        requested=("live-accepted", "smoke-qualification"),
        subject=(SubjectValue(dimension="runtime", value="r2"),),
    )
    invariant = Invariant(
        invariant_key="live-invariant",
        predicate_key="invariant-live",
        statement="Only accepted live state qualifies.",
        scope_key="wellplot",
        applicability=ApplicabilityEnvelope(
            bindings=(ApplicabilityBinding(dimension="runtime", expected_value="r1"),)
        ),
        rationale="Preserve runtime-specific evidence.",
        protects_against="stale qualification reuse",
        disposition=InvariantDisposition.ACTIVE,
        provenance=(),
    )
    qualification = QualificationFact(
        qualification_key="smoke-qualification",
        qualification_kind="smoke-test",
        result=QualificationResult.PASS,
        scope_key="wellplot",
        applicability=invariant.applicability,
        provenance=(),
        acceptance_required=False,
        invalidation_keys=("runtime",),
    )
    authority, invariant = _bind(authority, "invariant-live", invariant)
    evidence_identity = _identity("smoke-evidence", _B)
    qualification = qualification.model_copy(update={"evidence_refs": (evidence_identity,)})
    evidence_record = SourceRecordRef(
        identity=evidence_identity,
        role=SourceRole.EVIDENCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=(
            PredicateAssertion(
                predicate_key="evidence-for-smoke-qualification",
                value_digest=evidence_identity.content_digest,
            ),
        ),
    )
    authority, qualification = _bind(authority, "qualification-smoke-qualification", qualification)
    records = _replace_authority(records, authority)
    snapshot, records = _add_source(snapshot, records, evidence_record)
    resolved = _resolve(
        request,
        snapshot,
        coverage,
        records,
        invariants=(invariant,),
        qualification_facts=(qualification,),
    )
    assert resolved.status is ResolutionStatus.BLOCKED
    assert not resolved.invariants
    assert resolved.qualifications[0].accepted is PredicateResult.UNSATISFIED
    assert any(reason.code == "APPLICABILITY_MISMATCH" for reason in resolved.reasons)


def test_qualification_requires_exact_evidence_and_acceptance_binding() -> None:
    request, snapshot, coverage, records, authority = _case(
        requested=("smoke-qualification",),
        subject=(SubjectValue(dimension="runtime", value="runtime-a"),),
    )
    evidence_identity = _identity("smoke-evidence", _B)
    acceptance_identity = _identity("smoke-acceptance", _A)
    qualification = QualificationFact(
        qualification_key="smoke-qualification",
        qualification_kind="live-smoke",
        result=QualificationResult.PASS,
        scope_key="wellplot",
        applicability=ApplicabilityEnvelope(
            bindings=(ApplicabilityBinding(dimension="runtime", expected_value="runtime-a"),)
        ),
        provenance=(),
        evidence_refs=(evidence_identity,),
        acceptance_refs=(acceptance_identity,),
        acceptance_required=True,
    )
    exact_subject_digest = digest_authority_content(qualification)
    evidence = SourceRecordRef(
        identity=evidence_identity,
        role=SourceRole.EVIDENCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=(
            PredicateAssertion(
                predicate_key="evidence-for-smoke-qualification",
                value_digest=evidence_identity.content_digest,
            ),
        ),
    )
    acceptance = SourceRecordRef(
        identity=acceptance_identity,
        role=SourceRole.HUMAN_ACCEPTANCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=(
            PredicateAssertion(
                predicate_key="accepts-smoke-qualification",
                value_digest=exact_subject_digest,
            ),
        ),
    )
    authority, qualification = _bind(authority, "qualification-smoke-qualification", qualification)
    records = _replace_authority(records, authority)
    snapshot, records = _add_source(snapshot, records, evidence)
    snapshot, records = _add_source(snapshot, records, acceptance)

    valid = _resolve(
        request,
        snapshot,
        coverage,
        records,
        qualification_facts=(qualification,),
    )
    assert valid.status is ResolutionStatus.RESOLVED
    assert valid.qualifications[0].accepted is PredicateResult.SATISFIED

    unrelated_identity = _identity("unrelated-acceptance", _A)
    unrelated_fact = qualification.model_copy(update={"acceptance_refs": (unrelated_identity,)})
    unrelated_digest = digest_authority_content(unrelated_fact)
    unrelated_authority, unrelated_fact = _bind(
        records[1], "qualification-smoke-qualification", unrelated_fact
    )
    unrelated_evidence = evidence.model_copy(
        update={
            "assertions": (
                PredicateAssertion(
                    predicate_key="evidence-for-smoke-qualification",
                    value_digest=evidence_identity.content_digest,
                ),
            )
        }
    )
    unrelated_acceptance = SourceRecordRef(
        identity=unrelated_identity,
        role=SourceRole.HUMAN_ACCEPTANCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=(
            PredicateAssertion(
                predicate_key="accepts-other-qualification",
                value_digest=unrelated_digest,
            ),
        ),
    )
    unrelated_records = (
        records[0],
        unrelated_authority,
        records[2],
        unrelated_evidence,
        unrelated_acceptance,
    )
    unrelated_snapshot = snapshot.model_copy(
        update={
            "source_refs": tuple(
                sorted(
                    (item.identity for item in unrelated_records),
                    key=lambda item: item.source_key,
                )
            )
        }
    )
    unrelated = _resolve(
        request,
        unrelated_snapshot,
        coverage,
        unrelated_records,
        qualification_facts=(unrelated_fact,),
    )
    assert unrelated.status is ResolutionStatus.INDETERMINATE
    assert unrelated.qualifications[0].accepted is PredicateResult.INDETERMINATE

    missing_evidence_fact = qualification.model_copy(update={"evidence_refs": ()})
    missing_authority, missing_evidence_fact = _bind(
        records[1], "qualification-smoke-qualification", missing_evidence_fact
    )
    missing_evidence_records = _replace_authority(records, missing_authority)
    missing_evidence = _resolve(
        request,
        snapshot,
        coverage,
        missing_evidence_records,
        qualification_facts=(missing_evidence_fact,),
    )
    assert missing_evidence.status is ResolutionStatus.INDETERMINATE

    missing_acceptance_fact = qualification.model_copy(update={"acceptance_refs": ()})
    missing_authority, missing_acceptance_fact = _bind(
        records[1], "qualification-smoke-qualification", missing_acceptance_fact
    )
    missing_acceptance_records = _replace_authority(records, missing_authority)
    missing_acceptance = _resolve(
        request,
        snapshot,
        coverage,
        missing_acceptance_records,
        qualification_facts=(missing_acceptance_fact,),
    )
    assert missing_acceptance.status is ResolutionStatus.BLOCKED


@pytest.mark.parametrize(
    ("relation", "requested_subject", "fact_result", "expected"),
    [
        ("REQUIRES", (), PredicateResult.SATISFIED, PredicateResult.SATISFIED),
        ("FORBIDS", ("deployment",), PredicateResult.SATISFIED, PredicateResult.UNSATISFIED),
        ("UNKNOWN_RELATION", (), PredicateResult.SATISFIED, PredicateResult.INDETERMINATE),
    ],
)
def test_typed_requirement_edges_fail_closed(
    relation, requested_subject, fact_result, expected
) -> None:
    request, snapshot, coverage, records, authority = _case()
    if requested_subject:
        request = request.model_copy(update={"requested_subject_keys": requested_subject})
    edge = RequirementEdge(
        edge_key="edge-a",
        relation=relation,
        source_key="live-confirmation",
        target_key="deployment",
        scope_key="wellplot",
        provenance=(),
    )
    fact = PredicateFact(
        predicate_key="deployment",
        scope_key="wellplot",
        result=fact_result,
        value_digest=_B,
        provenance=(),
    )
    authority, edge = _bind(authority, "requirement-edge-a", edge)
    authority, fact = _bind(authority, "deployment", fact)
    records = _replace_authority(records, authority)
    result = _resolve(
        request, snapshot, coverage, records, requirement_edges=(edge,), predicate_facts=(fact,)
    )
    assert result.requirements[0].result is expected


def test_produces_consumes_and_consumable_state_are_explicit() -> None:
    request, snapshot, coverage, records, authority = _case()
    produces = RequirementEdge(
        edge_key="produce-edge",
        relation="PRODUCES",
        source_key="smoke",
        target_key="smoke-report",
        scope_key="wellplot",
        provenance=(),
        produced_subject_digest=_B,
        produced_evidence_roles=(SourceRole.EVIDENCE,),
    )
    consumable = ConsumableFact(
        ref=ConsumableRef(consumable_key="one-shot", scope_key="wellplot"),
        state=ConsumableState.AVAILABLE,
        ledger_complete=True,
        provenance=(),
    )
    consumes = RequirementEdge(
        edge_key="consume-edge",
        relation="CONSUMES",
        source_key="live-confirmation",
        target_key="one-shot",
        scope_key="wellplot",
        provenance=(),
    )
    authority, produces = _bind(authority, "requirement-produce-edge", produces)
    authority, consumable = _bind(authority, "consumable-one-shot", consumable)
    authority, consumes = _bind(authority, "requirement-consume-edge", consumes)
    records = _replace_authority(records, authority)
    result = _resolve(
        request,
        snapshot,
        coverage,
        records,
        requirement_edges=(consumes, produces),
        consumable_facts=(consumable,),
    )
    assert result.status is ResolutionStatus.RESOLVED
    assert [item.output_key for item in result.produced_expectations] == ["smoke-report"]
    assert result.consumption_requirements[0].intended_attempt_id == "attempt-a"
    assert "produced_expectations" not in inspect.signature(resolve_project_state).parameters

    forged_payload = result.model_dump(mode="python")
    forged_payload["produced_expectations"] = (
        ProducedExpectation(output_key="caller-injected", subject_digest=_A),
    )
    with pytest.raises(ValidationError, match="derived from resolved PRODUCES edges"):
        ResolvedProjectState.model_validate(forged_payload)


def test_negative_decision_requires_exact_reauthorization() -> None:
    request, snapshot, coverage, records, authority = _case()
    request = request.model_copy(update={"requested_subject_keys": ("dangerous-fallback",)})
    decision = NegativeDecision(
        decision_key="ban-fallback",
        disposition=NegativeDisposition.PROHIBITED_UNLESS_REAUTHORIZED,
        target_keys=("dangerous-fallback",),
        scope_key="wellplot",
        rationale="Fallback invalidates the evidence boundary.",
        provenance=(),
    )
    authority, decision = _bind(authority, "negative-decision-ban-fallback", decision)
    records = _replace_authority(records, authority)
    result = _resolve(request, snapshot, coverage, records, negative_decisions=(decision,))
    assert result.status is ResolutionStatus.BLOCKED
    assert any(reason.code == "PROHIBITED_SUBJECT" for reason in result.reasons)

    human_identity = _identity("human-reauthorization")
    reauthorized = decision.model_copy(update={"reauthorization_ref": human_identity})
    authority, reauthorized = _bind(records[1], "negative-decision-ban-fallback", reauthorized)
    records = _replace_authority(records, authority)
    human_record = SourceRecordRef(
        identity=human_identity,
        role=SourceRole.HUMAN_ACCEPTANCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key="wellplot",
        assertions=(
            PredicateAssertion(
                predicate_key="reauthorize-ban-fallback",
                value_digest=digest_authority_content(reauthorized),
            ),
        ),
    )
    expanded_snapshot, records = _add_source(snapshot, records, human_record)
    result = _resolve(
        request,
        expanded_snapshot,
        coverage,
        records,
        negative_decisions=(reauthorized,),
    )
    assert result.status is ResolutionStatus.RESOLVED


def test_superseded_subject_is_not_a_blanket_prohibition() -> None:
    request, snapshot, coverage, records, authority = _case(requested=("new-implementation",))
    request = request.model_copy(update={"requested_subject_keys": ("old-implementation",)})
    successor = PredicateFact(
        predicate_key="new-implementation",
        scope_key="wellplot",
        result=PredicateResult.SATISFIED,
        value_digest=_B,
    )
    decision = NegativeDecision(
        decision_key="old-implementation-superseded",
        disposition=NegativeDisposition.SUPERSEDED,
        target_keys=("old-implementation",),
        scope_key="wellplot",
        rationale="A later accepted implementation replaced the old one.",
        provenance=(),
        superseding_key="new-implementation",
    )
    authority, successor = _bind(authority, "new-implementation", successor)
    authority, decision = _bind(
        authority,
        "negative-decision-old-implementation-superseded",
        decision,
    )
    edge = RequirementEdge(
        edge_key="requires-current-implementation",
        relation="REQUIRES",
        source_key="live-confirmation",
        target_key="old-implementation",
        scope_key="wellplot",
    )
    authority, edge = _bind(
        authority,
        "requirement-requires-current-implementation",
        edge,
    )
    records = _replace_authority(records, authority)
    resolved = _resolve(
        request,
        snapshot,
        coverage,
        records,
        predicate_facts=(successor,),
        negative_decisions=(decision,),
        requirement_edges=(edge,),
    )
    assert resolved.status is ResolutionStatus.RESOLVED
    assert resolved.requirements[0].result is PredicateResult.SATISFIED
    assert not any(reason.code == "PROHIBITED_SUBJECT" for reason in resolved.reasons)

    unresolved = _resolve(
        request,
        snapshot.model_copy(update={"source_collection_complete": False}),
        coverage.model_copy(update={"source_collection_complete": False}),
        records,
        negative_decisions=(decision,),
        requirement_edges=(edge,),
    )
    assert unresolved.status is ResolutionStatus.INDETERMINATE
    assert unresolved.requirements[0].result is PredicateResult.INDETERMINATE
    assert any(reason.code == "EVIDENCE_LINEAGE_INCOMPLETE" for reason in unresolved.reasons)

    prior_subject_request = request.model_copy(
        update={"requested_predicate_keys": ("old-implementation",)}
    )
    prior_subject = resolve_project_state(
        prior_subject_request,
        snapshot,
        coverage,
        source_records=records,
        negative_decisions=(decision,),
    )
    assert prior_subject.status is ResolutionStatus.BLOCKED
    assert any(reason.code == "PREDECESSOR_UNSATISFIED" for reason in prior_subject.reasons)
    assert not any(reason.code == "PROHIBITED_SUBJECT" for reason in prior_subject.reasons)


def test_tampered_requirement_payload_fails_exact_backing_digest() -> None:
    request, snapshot, coverage, records, authority = _case()
    edge = RequirementEdge(
        edge_key="edge-a",
        relation="PRODUCES",
        source_key="live-confirmation",
        target_key="smoke-report",
        scope_key="wellplot",
        provenance=(),
        produced_subject_digest=_B,
    )
    authority, edge = _bind(authority, "requirement-edge-a", edge)
    records = _replace_authority(records, authority)
    tampered = edge.model_copy(update={"produced_subject_digest": _A})
    resolved = _resolve(request, snapshot, coverage, records, requirement_edges=(tampered,))
    assert resolved.status is ResolutionStatus.INDETERMINATE
    assert any(
        reason.code == "BACKING_PROVENANCE_INVALID" and "normative typed content" in reason.detail
        for reason in resolved.reasons
    )


def test_responsibility_collisions_and_incomplete_inventory_are_distinct() -> None:
    request, snapshot, coverage, records, authority = _case()
    request = request.model_copy(
        update={"responsibility_keys": ("runtime",), "proposed_owner_key": "relay"}
    )
    claim = ResponsibilityClaim(
        claim_key="runtime-owner",
        responsibility_key="runtime",
        owner_key="operator",
        scope_key="wellplot",
        provenance=(),
    )
    authority, claim = _bind(authority, "responsibility-runtime-owner", claim)
    records = _replace_authority(records, authority)
    collision = _resolve(request, snapshot, coverage, records, responsibility_claims=(claim,))
    assert collision.responsibility.result.value == "COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY"
    unknown = _resolve(
        request,
        snapshot,
        coverage.model_copy(update={"responsibility_inventory_complete": False}),
        records,
    )
    assert unknown.responsibility.result.value == "INDETERMINATE"


def test_knowledge_delta_is_retained_as_proposal_without_becoming_active() -> None:
    request, snapshot, coverage, records, _ = _case(requested=("new-rule",))
    proposal = KnowledgeDeltaProposal(
        delta_key="proposal-a",
        kind=KnowledgeDeltaKind.INVARIANT,
        exact_subject_key="smoke-result",
        scope_key="wellplot",
        proposed_content_digest=_B,
        affected_scope_keys=("wellplot",),
        evidence_refs=(),
        provenance=(),
    )
    result = _resolve(request, snapshot, coverage, records, knowledge_delta_proposals=(proposal,))
    assert result.status is ResolutionStatus.BLOCKED
    assert result.knowledge_delta_proposals == (proposal,)
    assert not result.invariants


def test_known_blocker_and_unknown_are_both_preserved() -> None:
    request, snapshot, coverage, records, authority = _case(requested=("known-fact",))
    fact = PredicateFact(
        predicate_key="known-fact",
        scope_key="wellplot",
        result=PredicateResult.UNSATISFIED,
        value_digest=_B,
    )
    authority, fact = _bind(authority, "known-fact", fact)
    records = _replace_authority(records, authority)
    result = _resolve(
        request,
        snapshot,
        coverage.model_copy(update={"relation_closure_complete": False}),
        records,
        predicate_facts=(fact,),
    )
    assert result.status is ResolutionStatus.BLOCKED
    assert any(reason.severity.value == "BLOCKER" for reason in result.reasons)
    assert any(reason.severity.value == "UNKNOWN" for reason in result.reasons)
