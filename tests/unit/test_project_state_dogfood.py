"""End-to-end synthetic dogfood through project-state resolution and compilation."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from relay_engine.domain import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.domain.ids import new_id
from relay_engine.project_state import (
    ApplicabilityBinding,
    ApplicabilityEnvelope,
    AuthorityCompilation,
    BackingProvenanceRef,
    CanonicalPointer,
    CompilationStatus,
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
    ProjectStateRequest,
    QualificationFact,
    QualificationResult,
    RequirementEdge,
    ResolutionSnapshot,
    ResolutionStatus,
    ResponsibilityClaim,
    RoleContractReference,
    SourceAcceptance,
    SourceCoverageDeclaration,
    SourceCoverageItem,
    SourceDisposition,
    SourceIdentity,
    SourceKind,
    SourceRecordRef,
    SourceRole,
    SubjectValue,
    compile_authority,
    digest_authority_content,
    digest_source_coverage,
    resolve_project_state,
)

_A = "sha256:" + "a" * 64
_B = "sha256:" + "b" * 64


@dataclass(frozen=True)
class Scenario:
    request: ProjectStateRequest
    snapshot: ResolutionSnapshot
    coverage: SourceCoverageDeclaration
    records: tuple[SourceRecordRef, ...]

    @property
    def authority(self) -> SourceRecordRef:
        return next(item for item in self.records if item.identity.source_key == "authority")


def _identity(key: str, digest: str = _A) -> SourceIdentity:
    return SourceIdentity(source_key=key, content_digest=digest)


def _subject(**dimensions: str | None) -> tuple[SubjectValue, ...]:
    return tuple(
        SubjectValue(dimension=key, value=value) for key, value in sorted(dimensions.items())
    )


def _envelope(**dimensions: str) -> ApplicabilityEnvelope:
    return ApplicabilityEnvelope(
        bindings=tuple(
            ApplicabilityBinding(dimension=key, expected_value=value)
            for key, value in sorted(dimensions.items())
        )
    )


def _scenario(
    *,
    scope: str,
    outcome: str = "live-confirmation",
    requested: tuple[str, ...] = (),
    subject: tuple[SubjectValue, ...] = (),
    attempt: str | None = "attempt-a",
    responsibilities: tuple[str, ...] = (),
    proposed_owner: str | None = None,
) -> Scenario:
    request = ProjectStateRequest(
        request_key="scenario-request",
        outcome_key=outcome,
        scope_key=scope,
        action_key="resolve-authority",
        actor=ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN),
        subject=subject,
        requested_predicate_keys=tuple(sorted(requested)),
        responsibility_keys=tuple(sorted(responsibilities)),
        proposed_owner_key=proposed_owner,
        intended_attempt_id=attempt,
    )
    projection = SourceRecordRef(
        identity=_identity("baseline"),
        role=SourceRole.SUMMARY,
        kind=SourceKind.LIVING_SUMMARY,
        disposition=SourceDisposition.ACTIVE,
        acceptance=SourceAcceptance.NOT_REQUIRED,
        scope_key=scope,
    )
    authority = SourceRecordRef(
        identity=_identity("authority"),
        role=SourceRole.AUTHORITY,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key=scope,
    )
    coverage_placeholder = _identity("coverage")
    coverage = SourceCoverageDeclaration(
        declaration=coverage_placeholder,
        outcome_key=outcome,
        scope_key=scope,
        required_canonical_keys=("current-baseline",),
        required_sources=(
            SourceCoverageItem(
                source=authority.identity,
                role=SourceRole.AUTHORITY,
                disposition=SourceDisposition.ACCEPTED,
                required_predicate_keys=(),
            ),
        ),
        admissible_roles=tuple(sorted(tuple(SourceRole), key=lambda item: item.value)),
        authority_predicate_keys=tuple(sorted(requested)),
        relation_closure_complete=True,
        source_collection_complete=True,
        responsibility_inventory_complete=True,
    )
    coverage_identity = SourceIdentity(
        source_key="coverage", content_digest=digest_source_coverage(coverage)
    )
    coverage = coverage.model_copy(update={"declaration": coverage_identity})
    coverage_record = SourceRecordRef(
        identity=coverage_identity,
        role=SourceRole.SOURCE_COVERAGE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key=scope,
    )
    records = (projection, authority, coverage_record)
    snapshot = ResolutionSnapshot(
        snapshot_key="scenario-snapshot",
        project_id=new_id("prj_"),
        source_commit=CommitRef(
            repository=RepositoryRef(id=new_id("repo_"), host="example.test", path="relay"),
            sha="3" * 40,
        ),
        registry_digest=_A,
        request_key=request.request_key,
        scope_key=scope,
        canonical_pointers=(
            CanonicalPointer(canonical_key="current-baseline", target=projection.identity),
        ),
        source_refs=tuple(
            sorted((item.identity for item in records), key=lambda item: item.source_key)
        ),
        source_collection_complete=True,
    )
    return Scenario(request=request, snapshot=snapshot, coverage=coverage, records=records)


def _replace_record(scenario: Scenario, replacement: SourceRecordRef) -> Scenario:
    records = tuple(
        replacement if item.identity.source_key == replacement.identity.source_key else item
        for item in scenario.records
    )
    return Scenario(
        request=scenario.request,
        snapshot=scenario.snapshot,
        coverage=scenario.coverage,
        records=records,
    )


def _bind(
    scenario: Scenario,
    record: SourceRecordRef,
    predicate_key: str,
    value: BaseModel,
) -> tuple[Scenario, BaseModel]:
    value_digest = digest_authority_content(value)
    assertions = {item.predicate_key: item for item in record.assertions}
    assertions[predicate_key] = PredicateAssertion(
        predicate_key=predicate_key,
        value_digest=value_digest,
    )
    updated_record = record.model_copy(
        update={"assertions": tuple(assertions[key] for key in sorted(assertions))}
    )
    bound_value = value.model_copy(
        update={
            "provenance": (
                BackingProvenanceRef(
                    predicate_key=predicate_key,
                    source=updated_record.identity,
                    value_digest=value_digest,
                ),
            )
        }
    )
    return _replace_record(scenario, updated_record), bound_value


def _add_record(scenario: Scenario, record: SourceRecordRef) -> Scenario:
    refs = tuple(
        sorted(
            scenario.snapshot.source_refs + (record.identity,),
            key=lambda item: item.source_key,
        )
    )
    snapshot = scenario.snapshot.model_copy(update={"source_refs": refs})
    return Scenario(
        request=scenario.request,
        snapshot=snapshot,
        coverage=scenario.coverage,
        records=scenario.records + (record,),
    )


def _fact(scenario: Scenario, key: str, result: PredicateResult = PredicateResult.SATISFIED):
    fact = PredicateFact(
        predicate_key=key,
        scope_key=scenario.request.scope_key,
        result=result,
        value_digest=_B,
    )
    scenario, fact = _bind(scenario, scenario.authority, key, fact)
    return scenario, fact


def _qualification(
    scenario: Scenario,
    key: str,
    *,
    applicability: ApplicabilityEnvelope,
    acceptance_required: bool = False,
    result: QualificationResult = QualificationResult.PASS,
) -> tuple[Scenario, QualificationFact]:
    evidence_identity = _identity(f"{key}-evidence", _B)
    acceptance_identity = _identity(f"{key}-acceptance", _A) if acceptance_required else None
    qualification = QualificationFact(
        qualification_key=key,
        qualification_kind="synthetic-qualification",
        result=result,
        scope_key=scenario.request.scope_key,
        applicability=applicability,
        provenance=(),
        evidence_refs=(evidence_identity,),
        acceptance_refs=() if acceptance_identity is None else (acceptance_identity,),
        acceptance_required=acceptance_required,
    )
    digest = digest_authority_content(qualification)
    evidence = SourceRecordRef(
        identity=evidence_identity,
        role=SourceRole.EVIDENCE,
        kind=SourceKind.ACCEPTED_RECORD,
        disposition=SourceDisposition.ACCEPTED,
        acceptance=SourceAcceptance.ACCEPTED,
        scope_key=scenario.request.scope_key,
        assertions=(
            PredicateAssertion(
                predicate_key=f"evidence-for-{key}", value_digest=evidence_identity.content_digest
            ),
        ),
    )
    scenario, qualification = _bind(
        scenario,
        scenario.authority,
        f"qualification-{key}",
        qualification,
    )
    scenario = _add_record(scenario, evidence)
    if acceptance_identity is not None:
        acceptance = SourceRecordRef(
            identity=acceptance_identity,
            role=SourceRole.HUMAN_ACCEPTANCE,
            kind=SourceKind.ACCEPTED_RECORD,
            disposition=SourceDisposition.ACCEPTED,
            acceptance=SourceAcceptance.ACCEPTED,
            scope_key=scenario.request.scope_key,
            assertions=(PredicateAssertion(predicate_key=f"accepts-{key}", value_digest=digest),),
        )
        scenario = _add_record(scenario, acceptance)
    return scenario, qualification


def _resolve(scenario: Scenario, **kwargs):
    return resolve_project_state(
        scenario.request,
        scenario.snapshot,
        scenario.coverage,
        source_records=scenario.records,
        **kwargs,
    )


def _compile(scenario: Scenario, resolution) -> AuthorityCompilation:
    return compile_authority(
        scenario.request,
        resolution,
        role_contract_ref=RoleContractReference(
            role_key="synthetic-reviewer", revision=1, content_digest=_A
        ),
        role_contract_applicability=PredicateResult.SATISFIED,
        work_contract_result=PredicateResult.SATISFIED,
    )


def _consume(scenario: Scenario, key: str, state: ConsumableState, complete: bool):
    consumable = ConsumableFact(
        ref=ConsumableRef(consumable_key=key, scope_key=scenario.request.scope_key),
        state=state,
        ledger_complete=complete,
    )
    scenario, consumable = _bind(scenario, scenario.authority, f"consumable-{key}", consumable)
    edge = RequirementEdge(
        edge_key=f"consume-{key}",
        relation="CONSUMES",
        source_key=scenario.request.outcome_key,
        target_key=key,
        scope_key=scenario.request.scope_key,
    )
    scenario, edge = _bind(
        scenario,
        scenario.authority,
        f"requirement-consume-{key}",
        edge,
    )
    return scenario, consumable, edge


@pytest.mark.parametrize("qualification_key", ("environment-qualified", "live-smoke"))
def test_wellplot_known_missing_prerequisites_block(qualification_key: str) -> None:
    scenario = _scenario(scope="wellplot", requested=(qualification_key,))
    resolution = _resolve(scenario)
    assert resolution.status is ResolutionStatus.BLOCKED
    assert _compile(scenario, resolution).status is CompilationStatus.BLOCKED


def test_wellplot_historical_smoke_mismatch_retains_pass_and_blocks_live_request() -> None:
    scenario = _scenario(
        scope="wellplot",
        requested=("live-smoke",),
        subject=_subject(
            executable="build-current",
            runtime="runtime-current",
            provider="provider-a",
            endpoint="endpoint-a",
            environment="environment-current",
            fixture="fixture-a",
            predecessor="campaign-current",
        ),
    )
    scenario, smoke = _qualification(
        scenario,
        "live-smoke",
        applicability=_envelope(
            executable="build-old",
            runtime="runtime-old",
            provider="provider-a",
            endpoint="endpoint-a",
            environment="environment-old",
            fixture="fixture-a",
            predecessor="campaign-current",
        ),
        acceptance_required=True,
    )
    resolution = _resolve(scenario, qualification_facts=(smoke,))
    assert resolution.status is ResolutionStatus.BLOCKED
    assert resolution.qualifications[0].fact.result is QualificationResult.PASS
    assert resolution.qualifications[0].applicability.result.value == "NOT_APPLICABLE"
    assert resolution.qualifications[0].accepted is PredicateResult.UNSATISFIED
    assert _compile(scenario, resolution).status is CompilationStatus.BLOCKED


def test_wellplot_unknown_runtime_identity_is_indeterminate() -> None:
    scenario = _scenario(
        scope="wellplot",
        requested=("live-smoke",),
        subject=_subject(runtime=None, environment="environment-a"),
    )
    scenario, smoke = _qualification(
        scenario,
        "live-smoke",
        applicability=_envelope(runtime="runtime-a", environment="environment-a"),
    )
    resolution = _resolve(scenario, qualification_facts=(smoke,))
    assert resolution.status is ResolutionStatus.INDETERMINATE
    assert resolution.qualifications[0].applicability.result.value == "INDETERMINATE"
    assert _compile(scenario, resolution).status is CompilationStatus.INDETERMINATE


def test_wellplot_second_harness_responsibility_collision_blocks() -> None:
    scenario = _scenario(
        scope="wellplot",
        responsibilities=("campaign-smoke-runner",),
        proposed_owner="second-harness",
    )
    claim = ResponsibilityClaim(
        claim_key="accepted-smoke-runner",
        responsibility_key="campaign-smoke-runner",
        owner_key="campaign-runner",
        scope_key="wellplot",
        provenance=(),
    )
    scenario, claim = _bind(
        scenario,
        scenario.authority,
        "responsibility-accepted-smoke-runner",
        claim,
    )
    resolution = _resolve(scenario, responsibility_claims=(claim,))
    assert resolution.status is ResolutionStatus.BLOCKED
    assert resolution.responsibility.result.value == "COLLISION_REQUIRES_ARCHITECTURE_AUTHORITY"


def test_wellplot_rejected_fallback_path_blocks() -> None:
    scenario = _scenario(scope="wellplot")
    scenario = Scenario(
        request=scenario.request.model_copy(
            update={"requested_subject_keys": ("semantic-fallback",)}
        ),
        snapshot=scenario.snapshot,
        coverage=scenario.coverage,
        records=scenario.records,
    )
    decision = NegativeDecision(
        decision_key="rejected-fallback",
        disposition=NegativeDisposition.REJECTED,
        target_keys=("semantic-fallback",),
        scope_key="wellplot",
        rationale="Fallback changes the governed semantic engine.",
        provenance=(),
    )
    scenario, decision = _bind(
        scenario,
        scenario.authority,
        "negative-decision-rejected-fallback",
        decision,
    )
    resolution = _resolve(scenario, negative_decisions=(decision,))
    assert resolution.status is ResolutionStatus.BLOCKED
    assert _compile(scenario, resolution).status is CompilationStatus.BLOCKED


@pytest.mark.parametrize(
    ("state", "ledger_complete", "expected"),
    [
        (ConsumableState.CONSUMED, True, ResolutionStatus.BLOCKED),
        (ConsumableState.INDETERMINATE, False, ResolutionStatus.INDETERMINATE),
    ],
)
def test_wellplot_campaign_namespace_state_is_fail_closed(
    state: ConsumableState, ledger_complete: bool, expected: ResolutionStatus
) -> None:
    scenario = _scenario(scope="wellplot")
    scenario, consumable, edge = _consume(scenario, "campaign-namespace", state, ledger_complete)
    resolution = _resolve(
        scenario,
        consumable_facts=(consumable,),
        requirement_edges=(edge,),
    )
    assert resolution.status is expected
    assert _compile(scenario, resolution).status.value == expected.value


def test_tension_attempt_namespace_is_exact_and_not_reusable() -> None:
    scenario = _scenario(
        scope="tension",
        subject=_subject(level="level-3", fixture="mesh-a", oracle="oracle-a"),
        attempt="fem-attempt-17",
    )
    scenario, consumable, edge = _consume(
        scenario, "fem-namespace", ConsumableState.AVAILABLE, True
    )
    available = _resolve(
        scenario,
        consumable_facts=(consumable,),
        requirement_edges=(edge,),
    )
    assert available.status is ResolutionStatus.RESOLVED
    assert available.consumption_requirements[0].intended_attempt_id == "fem-attempt-17"

    scenario, consumed, edge = _consume(scenario, "fem-namespace", ConsumableState.CONSUMED, True)
    blocked = _resolve(
        scenario,
        consumable_facts=(consumed,),
        requirement_edges=(edge,),
    )
    assert blocked.status is ResolutionStatus.BLOCKED


def test_tension_oracle_mismatch_and_unknown_ledger_are_not_transferred() -> None:
    scenario = _scenario(
        scope="tension",
        requested=("fem-oracle-qualified",),
        subject=_subject(level="level-3", fixture="mesh-current", oracle="oracle-current"),
        attempt="fem-attempt-18",
    )
    scenario, oracle = _qualification(
        scenario,
        "fem-oracle-qualified",
        applicability=_envelope(level="level-3", fixture="mesh-old", oracle="oracle-current"),
    )
    mismatch = _resolve(scenario, qualification_facts=(oracle,))
    assert mismatch.status is ResolutionStatus.BLOCKED
    assert mismatch.qualifications[0].fact.result is QualificationResult.PASS
    assert mismatch.qualifications[0].applicability.result.value == "NOT_APPLICABLE"

    unknown_scenario = _scenario(
        scope="tension",
        subject=_subject(level="level-3", fixture="mesh-current", oracle="oracle-current"),
        attempt="fem-attempt-18",
    )
    unknown_scenario, consumable, edge = _consume(
        unknown_scenario, "fem-namespace", ConsumableState.INDETERMINATE, False
    )
    unknown = _resolve(
        unknown_scenario,
        consumable_facts=(consumable,),
        requirement_edges=(edge,),
    )
    assert unknown.status is ResolutionStatus.INDETERMINATE


@pytest.mark.parametrize(
    ("subject", "expected"),
    [
        (
            _subject(backend="gpu-b", runtime="solver-a", environment="env-a"),
            ResolutionStatus.BLOCKED,
        ),
        (
            _subject(backend="gpu-a", runtime=None, environment="env-a"),
            ResolutionStatus.INDETERMINATE,
        ),
    ],
)
def test_seneca_backend_and_environment_qualification_resolution(
    subject: tuple[SubjectValue, ...], expected: ResolutionStatus
) -> None:
    scenario = _scenario(
        scope="seneca",
        requested=("seneca-qualified",),
        subject=subject,
    )
    scenario, qualification = _qualification(
        scenario,
        "seneca-qualified",
        applicability=_envelope(backend="gpu-a", runtime="solver-a", environment="env-a"),
    )
    resolution = _resolve(scenario, qualification_facts=(qualification,))
    assert resolution.status is expected
    if expected is ResolutionStatus.BLOCKED:
        assert resolution.qualifications[0].fact.result is QualificationResult.PASS
        assert resolution.qualifications[0].applicability.result.value == "NOT_APPLICABLE"


def test_relay_accepted_governance_chain_reconstructs_without_chat() -> None:
    chain = (
        "accepted-predecessor",
        "design-accepted",
        "implementation-accepted",
        "human-accepted",
        "closure-accepted",
    )
    scenario = _scenario(scope="relay", outcome="slice-closure", requested=chain)
    facts: list[PredicateFact] = []
    chain_edges: list[RequirementEdge] = []
    for key in chain:
        role = SourceRole.HUMAN_ACCEPTANCE if key == "human-accepted" else SourceRole.AUTHORITY
        identity = _identity(f"source-{key}", _B)
        source = SourceRecordRef(
            identity=identity,
            role=role,
            kind=SourceKind.ACCEPTED_RECORD,
            disposition=SourceDisposition.ACCEPTED,
            acceptance=SourceAcceptance.ACCEPTED,
            scope_key="relay",
        )
        scenario = _add_record(scenario, source)
        fact = PredicateFact(
            predicate_key=key,
            scope_key="relay",
            result=PredicateResult.SATISFIED,
            value_digest=_B,
        )
        scenario, fact = _bind(scenario, source, key, fact)
        facts.append(fact)

    for predecessor, target in zip(chain, chain[1:], strict=False):
        edge = RequirementEdge(
            edge_key=f"requires-{target}",
            relation="REQUIRES",
            source_key=predecessor,
            target_key=target,
            scope_key="relay",
        )
        scenario, edge = _bind(
            scenario,
            scenario.authority,
            f"requirement-{edge.edge_key}",
            edge,
        )
        chain_edges.append(edge)

    invariant = Invariant(
        invariant_key="inherited-no-runtime",
        predicate_key="runtime-execution-prohibited",
        statement="This synthetic governance chain has no runtime authority.",
        scope_key="relay",
        applicability=ApplicabilityEnvelope(),
        rationale="Keep reconstruction non-executing.",
        protects_against="implicit execution authority",
        disposition=InvariantDisposition.ACTIVE,
        provenance=(),
    )
    scenario, invariant = _bind(
        scenario,
        scenario.authority,
        "runtime-execution-prohibited",
        invariant,
    )
    resolution = _resolve(
        scenario,
        predicate_facts=tuple(facts),
        invariants=(invariant,),
        requirement_edges=tuple(chain_edges),
    )
    assert resolution.status is ResolutionStatus.RESOLVED
    assert tuple(item.predicate_key for item in resolution.predicate_facts) == tuple(sorted(chain))
    assert resolution.invariants == (invariant,)
    assert (
        _resolve(
            scenario,
            predicate_facts=tuple(facts),
            invariants=(invariant,),
            requirement_edges=tuple(chain_edges),
        ).content_digest
        == resolution.content_digest
    )


def test_relay_proposed_work_is_not_authority_and_exhaustion_has_no_successor() -> None:
    scenario = _scenario(scope="relay", outcome="backlog-exhausted")
    proposal = KnowledgeDeltaProposal(
        delta_key="proposed-work-successor",
        kind=KnowledgeDeltaKind.PREREQUISITE,
        exact_subject_key="proposed-work",
        scope_key="relay",
        proposed_content_digest=_B,
        affected_scope_keys=("relay",),
        evidence_refs=(),
        provenance=(),
    )
    resolution = _resolve(scenario, knowledge_delta_proposals=(proposal,))
    compilation = _compile(scenario, resolution)
    assert compilation.status is CompilationStatus.READY
    assert compilation.candidate is not None
    assert compilation.candidate.request.outcome_key == "backlog-exhausted"
    assert compilation.candidate.work_packet_constraints == ()
    assert compilation.candidate.resolution.knowledge_delta_proposals == (proposal,)
    assert not hasattr(compilation.candidate, "successor")
