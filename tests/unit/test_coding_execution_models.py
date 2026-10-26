"""Exact identities and immutable result boundaries for Slice 3.1."""

from __future__ import annotations

import pytest

from relay_engine.coding_execution.models import (
    ConsumableReservationBinding,
    ExecutionTerminalOutcome,
    HumanGrantBinding,
    ProposedWorkObservation,
    attempt_id_for_execution,
    execution_id_for_attempt,
)

_A = "sha256:" + "a" * 64


def test_attempt_mapping_is_reversible_and_preserves_uuid() -> None:
    attempt = "exec-018f47c1-7b2c-7abc-8def-123456789008"
    execution = "exec_018f47c1-7b2c-7abc-8def-123456789008"

    assert execution_id_for_attempt(attempt) == execution
    assert attempt_id_for_execution(execution) == attempt


@pytest.mark.parametrize(
    "value",
    (
        "attempt-018f47c1-7b2c-7abc-8def-123456789008",
        "exec-018F47C1-7B2C-7ABC-8DEF-123456789008",
        "exec-018f47c1-7b2c-7abc-8def-12345678900",
    ),
)
def test_malformed_attempt_identity_fails_closed(value: str) -> None:
    with pytest.raises(ValueError, match="canonical"):
        execution_id_for_attempt(value)


def test_terminal_vocabulary_excludes_proposed_work() -> None:
    assert {item.value for item in ExecutionTerminalOutcome} == {
        "DONE",
        "BLOCKED_BY_AUTHORITY",
        "BLOCKED_BY_CONTRACT",
        "BLOCKED_BY_ENVIRONMENT",
        "BUDGET_EXHAUSTED",
        "BACKLOG_EXHAUSTED",
        "CANCELLED",
        "INTERRUPTED",
    }


def test_reservation_is_bound_to_grant_candidate_and_attempt() -> None:
    grant = HumanGrantBinding(
        grant_record_id="grant-record-1",
        grant_record_digest=_A,
        authority_candidate_digest=_A,
        intended_attempt_id="exec-018f47c1-7b2c-7abc-8def-123456789008",
        project_id="prj_018f47c1-7b2c-7abc-8def-123456789008",
        slice_id="slc_018f47c1-7b2c-7abc-8def-123456789008",
        valid=True,
        applicable=True,
    )
    reservation = ConsumableReservationBinding(
        consumable_key="attempt-namespace",
        scope_key="wellplot-project",
        grant_record_digest=grant.grant_record_digest,
        authority_candidate_digest=grant.authority_candidate_digest,
        intended_attempt_id=grant.intended_attempt_id,
        evidence_id="reservation-evidence-1",
        evidence_digest=_A,
        state="RESERVED",
        created_atomically_at_grant=True,
    )
    assert reservation.created_atomically_at_grant

    with pytest.raises(ValueError, match="canonical"):
        execution_id_for_attempt("exec-018f47c1-7b2c-7abc-8def-123456789008\n")


def test_proposed_work_is_evidence_with_hard_stop_not_a_terminal_outcome() -> None:
    observation = ProposedWorkObservation(
        source_execution_id="exec_018f47c1-7b2c-7abc-8def-123456789008",
        summary="Additional migration work",
        rationale="The discovered work exceeds this packet.",
        evidence_refs=("finding-1",),
        proposal_digest=_A,
        applicable_hard_stop_key="out-of-scope-change",
    )
    assert observation.applicable_hard_stop_key == "out-of-scope-change"
    assert "PROPOSED_WORK" not in {item.value for item in ExecutionTerminalOutcome}
