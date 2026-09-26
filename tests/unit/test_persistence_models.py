"""Validation and deterministic identity tests for persistence-owned records."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from relay_engine.domain.ids import new_id
from relay_engine.domain.references import ActorKind, ActorRef
from relay_engine.governance import (
    ChangeSurfaceStatus,
    GateRevisionRef,
    HandoverContext,
    HandoverGate,
    HandoverPolicy,
    RiskStatus,
    ToolchainChangeStatus,
    evaluate_handover_gates,
)
from relay_engine.lifecycle import (
    Blockage,
    BlockageStatus,
    LifecyclePhase,
    LifecycleValidity,
    SliceLifecycle,
)
from relay_engine.persistence import ExecutionRecord, GateEvaluationRecord, Migration

NOW = datetime(2026, 9, 23, 12, tzinfo=UTC)
ACTOR = ActorRef(id="act_018f47c1-7b2c-7abc-8def-123456789008", kind=ActorKind.HUMAN)
SLICE = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE = "gate_018f47c1-7b2c-7abc-8def-123456789020"


def _record() -> GateEvaluationRecord:
    state = SliceLifecycle(
        slice_id=SLICE,
        phase=LifecyclePhase.READY,
        validity=LifecycleValidity.CURRENT,
        blockage=Blockage(status=BlockageStatus.CLEAR, reasons=()),
        revision=3,
        updated_at=NOW,
        superseded_by_slice_id=None,
    )
    context = HandoverContext(
        baseline_id=BASELINE,
        governance_revision=2,
        lifecycle=state,
        change_surface_status=ChangeSurfaceStatus.WITHIN_DECLARED,
        risk_status=RiskStatus.CLEAR,
        toolchain_change_status=ToolchainChangeStatus.NONE,
    )
    gate = HandoverGate(
        gate_id=GATE,
        revision=1,
        key="implement",
        slice_id=SLICE,
        baseline_id=BASELINE,
        source_phase=LifecyclePhase.READY,
        target_phase=LifecyclePhase.IMPLEMENTING,
        policy=HandoverPolicy.AUTO,
    )
    return GateEvaluationRecord(
        id=new_id("geval_"),
        recorded_at=NOW,
        gate_refs=(GateRevisionRef(gate_id=GATE, gate_revision=1),),
        context=context,
        evaluations=evaluate_handover_gates((gate,), context),
    )


def test_gate_evaluation_record_round_trips_and_is_immutable() -> None:
    record = _record()
    assert GateEvaluationRecord.model_validate_json(record.model_dump_json()) == record
    with pytest.raises(ValidationError):
        record.id = new_id("geval_")  # type: ignore[misc]
    assert record.context.lifecycle.revision == 3


def test_gate_evaluation_record_requires_complete_canonical_gate_set() -> None:
    record = _record()
    with pytest.raises(ValidationError):
        GateEvaluationRecord(
            id=new_id("geval_"),
            recorded_at=NOW,
            gate_refs=record.gate_refs,
            context=record.context,
            evaluations=(),
        )


def test_execution_record_requires_one_revision_advance_and_timezone() -> None:
    with pytest.raises(ValidationError):
        ExecutionRecord(
            execution_id=new_id("exec_"),
            gate_evaluation_record_id=new_id("geval_"),
            slice_id=SLICE,
            baseline_id=BASELINE,
            selected_gate_id=GATE,
            selected_gate_revision=1,
            source_lifecycle_revision=3,
            resulting_lifecycle_revision=5,
            event_id=new_id("evt_"),
            actor=ACTOR,
            occurred_at=NOW,
            reason="Execute.",
        )


def test_migration_checksum_is_stable() -> None:
    migration = Migration(
        1, "initial", ("CREATE TABLE one (id INTEGER)", "CREATE INDEX ix ON one(id)")
    )
    same = Migration(1, "initial", ("CREATE TABLE one (id INTEGER)", "CREATE INDEX ix ON one(id)"))
    assert migration.checksum == same.checksum
    assert migration.checksum.startswith("sha256:")


def test_migration_checksum_changes_with_statement_order_or_content() -> None:
    migration = Migration(
        1, "initial", ("CREATE TABLE one (id INTEGER)", "CREATE INDEX ix ON one(id)")
    )
    reversed_statements = Migration(1, "initial", tuple(reversed(migration.statements)))
    changed = Migration(1, "initial", ("CREATE TABLE one (id TEXT)", "CREATE INDEX ix ON one(id)"))
    assert migration.checksum != reversed_statements.checksum
    assert migration.checksum != changed.checksum


def test_domain_identifier_generation_supports_persistence_records() -> None:
    assert new_id("geval_").startswith("geval_")
    assert new_id("exec_").startswith("exec_")
