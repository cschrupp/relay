"""Pure tri-state compilation of a resolved state into a Human-review candidate."""

from __future__ import annotations

from relay_engine.project_state.models import (
    AuthorityCandidate,
    AuthorityCompilation,
    CandidateFreshness,
    CandidateFreshnessStatus,
    CompilationStatus,
    ContractReference,
    PredicateResult,
    ProjectStateRequest,
    ReasonSeverity,
    ResolutionReason,
    ResolutionReasonCode,
    ResolutionSnapshot,
    ResolutionStatus,
    ResolvedProjectState,
    RoleContractReference,
)


def _ordered_reasons(reasons: list[ResolutionReason]) -> tuple[ResolutionReason, ...]:
    return tuple(
        sorted(
            set(reasons),
            key=lambda item: (
                item.severity.value,
                item.code,
                item.subject_key,
                item.detail,
            ),
        )
    )


def compile_authority(
    request: ProjectStateRequest,
    resolution: ResolvedProjectState,
    *,
    role_contract_ref: RoleContractReference | None,
    role_contract_applicability: PredicateResult = PredicateResult.INDETERMINATE,
    work_contract_refs: tuple[ContractReference, ...] = (),
    work_contract_result: PredicateResult = PredicateResult.INDETERMINATE,
    work_packet_constraints: tuple[str, ...] = (),
    hard_stops: tuple[str, ...] = (),
    unrepresentable_constraints: tuple[str, ...] = (),
    out_of_scope_actions: tuple[str, ...] = (),
) -> AuthorityCompilation:
    """Return READY/BLOCKED/INDETERMINATE without issuing or persisting authority."""

    reasons = list(resolution.reasons)
    if request != resolution.request:
        reasons.append(
            ResolutionReason(
                code=ResolutionReasonCode.REQUEST_INCOMPLETE.value,
                severity=ReasonSeverity.UNKNOWN,
                subject_key=request.request_key,
                detail="compiler request differs from the exact request resolved by the resolver",
            )
        )

    if role_contract_ref is None:
        reasons.append(
            ResolutionReason(
                code="ROLE_CONTRACT_REFERENCE_MISSING",
                severity=ReasonSeverity.UNKNOWN,
                subject_key=request.request_key,
                detail="an exact applicable RoleContract reference is required",
            )
        )
    elif role_contract_applicability is PredicateResult.UNSATISFIED:
        reasons.append(
            ResolutionReason(
                code="ROLE_CONTRACT_NOT_APPLICABLE",
                severity=ReasonSeverity.BLOCKER,
                subject_key=role_contract_ref.role_key,
                detail="the exact RoleContract is known not to apply to this request",
            )
        )
    elif role_contract_applicability is PredicateResult.INDETERMINATE:
        reasons.append(
            ResolutionReason(
                code="ROLE_CONTRACT_APPLICABILITY_UNKNOWN",
                severity=ReasonSeverity.UNKNOWN,
                subject_key=role_contract_ref.role_key,
                detail="RoleContract applicability cannot be established",
            )
        )

    if work_contract_result is PredicateResult.UNSATISFIED:
        reasons.append(
            ResolutionReason(
                code=ResolutionReasonCode.WORK_CONTRACT_UNREPRESENTABLE.value,
                severity=ReasonSeverity.BLOCKER,
                subject_key=request.request_key,
                detail=(
                    "a required constraint cannot be represented by existing WorkPacket contracts"
                ),
            )
        )
    elif work_contract_result is PredicateResult.INDETERMINATE:
        reasons.append(
            ResolutionReason(
                code=ResolutionReasonCode.WORK_CONTRACT_UNREPRESENTABLE.value,
                severity=ReasonSeverity.UNKNOWN,
                subject_key=request.request_key,
                detail="WorkPacket/ContextManifest representability is unresolved",
            )
        )

    for hard_stop in hard_stops:
        reasons.append(
            ResolutionReason(
                code="KNOWN_HARD_STOP",
                severity=ReasonSeverity.BLOCKER,
                subject_key=hard_stop,
                detail="an applicable hard stop prevents ordinary authority compilation",
            )
        )
    for constraint in unrepresentable_constraints:
        reasons.append(
            ResolutionReason(
                code=ResolutionReasonCode.WORK_CONTRACT_UNREPRESENTABLE.value,
                severity=ReasonSeverity.BLOCKER,
                subject_key=constraint,
                detail=(
                    "required constraint has no existing WorkPacket/ContextManifest representation"
                ),
            )
        )

    ordered_reasons = _ordered_reasons(reasons)
    has_blocker = resolution.status is ResolutionStatus.BLOCKED or any(
        item.severity is ReasonSeverity.BLOCKER for item in ordered_reasons
    )
    has_unknown = resolution.status is ResolutionStatus.INDETERMINATE or any(
        item.severity is ReasonSeverity.UNKNOWN for item in ordered_reasons
    )
    if has_blocker:
        return AuthorityCompilation(
            status=CompilationStatus.BLOCKED,
            reasons=ordered_reasons,
            resolution_digest=resolution.content_digest,
        )
    if has_unknown or role_contract_ref is None:
        return AuthorityCompilation(
            status=CompilationStatus.INDETERMINATE,
            reasons=ordered_reasons,
            resolution_digest=resolution.content_digest,
        )

    candidate = AuthorityCandidate(
        request=request,
        resolution=resolution,
        role_contract_ref=role_contract_ref,
        work_contract_refs=work_contract_refs,
        work_packet_constraints=work_packet_constraints,
        hard_stops=hard_stops,
        out_of_scope_actions=out_of_scope_actions,
    )
    return AuthorityCompilation(
        status=CompilationStatus.READY,
        reasons=ordered_reasons,
        candidate=candidate,
        resolution_digest=resolution.content_digest,
    )


def check_candidate_freshness(
    candidate: AuthorityCandidate,
    current_snapshot: ResolutionSnapshot | None,
) -> CandidateFreshness:
    """Compare the exact full snapshot; any source identity change makes it stale."""

    if current_snapshot is None:
        return CandidateFreshness(
            status=CandidateFreshnessStatus.INDETERMINATE,
            candidate_digest=candidate.content_digest,
            compared_snapshot_digest=None,
            reason="current exact source snapshot was not supplied",
        )
    current_digest = current_snapshot.content_digest
    if current_digest != candidate.resolution.snapshot.content_digest:
        return CandidateFreshness(
            status=CandidateFreshnessStatus.STALE,
            candidate_digest=candidate.content_digest,
            compared_snapshot_digest=current_digest,
            reason="candidate is bound to a different exact source snapshot",
        )
    return CandidateFreshness(
        status=CandidateFreshnessStatus.CURRENT,
        candidate_digest=candidate.content_digest,
        compared_snapshot_digest=current_digest,
        reason="candidate and current source snapshot identities match exactly",
    )


__all__ = ["check_candidate_freshness", "compile_authority"]
