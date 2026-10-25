"""Tri-state compilation and exact candidate freshness tests."""

from __future__ import annotations

from relay_engine.domain import ActorKind, ActorRef, CommitRef, RepositoryRef
from relay_engine.domain.ids import new_id
from relay_engine.project_state import (
    AuthorityCandidate,
    CandidateFreshnessStatus,
    CanonicalPointer,
    CompilationStatus,
    ContractReference,
    PredicateResult,
    ProjectStateRequest,
    ResolutionSnapshot,
    ResolutionStatus,
    RoleContractReference,
    SourceAcceptance,
    SourceCoverageDeclaration,
    SourceDisposition,
    SourceIdentity,
    SourceKind,
    SourceRecordRef,
    SourceRole,
    check_candidate_freshness,
    compile_authority,
    digest_source_coverage,
    resolve_project_state,
)

_DIGEST = "sha256:" + "a" * 64


def _inputs():
    request = ProjectStateRequest(
        request_key="request-a",
        outcome_key="release-live",
        scope_key="relay",
        action_key="confirm-release",
        actor=ActorRef(id=new_id("act_"), kind=ActorKind.HUMAN),
        subject=(),
    )
    projection = SourceRecordRef(
        identity=SourceIdentity(source_key="baseline", content_digest=_DIGEST),
        role=SourceRole.SUMMARY,
        kind=SourceKind.LIVING_SUMMARY,
        disposition=SourceDisposition.ACTIVE,
        acceptance=SourceAcceptance.NOT_REQUIRED,
        scope_key="relay",
    )
    placeholder = SourceIdentity(source_key="coverage", content_digest=_DIGEST)
    coverage = SourceCoverageDeclaration(
        declaration=placeholder,
        outcome_key="release-live",
        scope_key="relay",
        required_canonical_keys=("current-baseline",),
        required_sources=(),
        admissible_roles=(SourceRole.SOURCE_COVERAGE,),
        authority_predicate_keys=(),
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
        scope_key="relay",
    )
    commit = CommitRef(
        repository=RepositoryRef(id=new_id("repo_"), host="example.test", path="relay"),
        sha="2" * 40,
    )
    snapshot = ResolutionSnapshot(
        snapshot_key="snapshot-a",
        project_id=new_id("prj_"),
        source_commit=commit,
        registry_digest=_DIGEST,
        request_key=request.request_key,
        scope_key=request.scope_key,
        canonical_pointers=(
            CanonicalPointer(canonical_key="current-baseline", target=projection.identity),
        ),
        source_refs=tuple(
            sorted((projection.identity, coverage_identity), key=lambda item: item.source_key)
        ),
        source_collection_complete=True,
    )
    resolution = resolve_project_state(
        request,
        snapshot,
        coverage,
        source_records=(projection, coverage_record),
    )
    return request, snapshot, resolution


def test_only_ready_compilation_carries_a_candidate() -> None:
    request, _, resolution = _inputs()
    role = RoleContractReference(
        role_key="project-state-reviewer", revision=1, content_digest=_DIGEST
    )
    ready = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        role_contract_applicability=PredicateResult.SATISFIED,
        work_contract_result=PredicateResult.SATISFIED,
    )
    assert resolution.status is ResolutionStatus.RESOLVED
    assert ready.status is CompilationStatus.READY
    assert ready.candidate is not None
    assert not hasattr(ready.candidate, "authorized")
    assert not hasattr(ready.candidate, "grant")

    missing_role = compile_authority(request, resolution, role_contract_ref=None)
    assert missing_role.status is CompilationStatus.INDETERMINATE
    assert missing_role.candidate is None
    missing_contract_evidence = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        role_contract_applicability=PredicateResult.SATISFIED,
    )
    assert missing_contract_evidence.status is CompilationStatus.INDETERMINATE


def test_blockers_unknowns_and_unrepresentable_contracts_are_preserved() -> None:
    request, _, resolution = _inputs()
    role = RoleContractReference(role_key="reviewer", revision=1, content_digest=_DIGEST)

    blocked = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        hard_stops=("accepted-prohibition",),
    )
    assert blocked.status is CompilationStatus.BLOCKED
    assert blocked.candidate is None

    unknown = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        role_contract_applicability=PredicateResult.INDETERMINATE,
    )
    assert unknown.status is CompilationStatus.INDETERMINATE
    assert unknown.candidate is None

    unrepresentable = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        work_contract_result=PredicateResult.UNSATISFIED,
        unrepresentable_constraints=("runtime-constraint",),
    )
    assert unrepresentable.status is CompilationStatus.BLOCKED
    assert unrepresentable.candidate is None


def test_candidate_binds_exact_work_contracts_and_freshness_snapshot() -> None:
    request, snapshot, resolution = _inputs()
    role = RoleContractReference(role_key="reviewer", revision=2, content_digest=_DIGEST)
    contract = ContractReference(
        contract_key="execution-contract", revision=3, content_digest=_DIGEST
    )
    compilation = compile_authority(
        request,
        resolution,
        role_contract_ref=role,
        role_contract_applicability=PredicateResult.SATISFIED,
        work_contract_refs=(contract,),
        work_contract_result=PredicateResult.SATISFIED,
        work_packet_constraints=("deliver-report",),
        out_of_scope_actions=("execute-runtime",),
    )
    candidate = compilation.candidate
    assert candidate is not None
    assert candidate.work_contract_refs == (contract,)
    assert candidate.out_of_scope_actions == ("execute-runtime",)
    assert check_candidate_freshness(candidate, snapshot).status is CandidateFreshnessStatus.CURRENT
    assert (
        check_candidate_freshness(candidate, None).status is CandidateFreshnessStatus.INDETERMINATE
    )
    changed = snapshot.model_copy(update={"registry_digest": "sha256:" + "b" * 64})
    assert check_candidate_freshness(candidate, changed).status is CandidateFreshnessStatus.STALE


def test_candidate_model_rejects_nonresolved_state() -> None:
    request, _, resolution = _inputs()
    blocked = resolution.model_copy(update={"status": ResolutionStatus.BLOCKED})
    try:
        AuthorityCandidate(
            request=request,
            resolution=blocked,
            role_contract_ref=RoleContractReference(
                role_key="reviewer", revision=1, content_digest=_DIGEST
            ),
            work_packet_constraints=(),
            out_of_scope_actions=(),
        )
    except ValueError as error:
        assert "resolved state" in str(error)
    else:
        raise AssertionError("non-resolved state must not produce an authority candidate")
