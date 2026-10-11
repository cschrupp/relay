"""Strict value and canonical-identity tests for Decision Support models."""

import pytest
from pydantic import ValidationError

from relay_engine.decision_support.models import (
    DecisionBasisIdentityV1,
    DecisionCardState,
    DecisionKind,
    DecisionStatement,
    DecisionStatementBasis,
)
from relay_engine.governance.models import GateRevisionRef
from relay_engine.human_control.models import HumanActionBasis
from relay_engine.lifecycle.models import LifecyclePhase

SLICE_ID = "slc_018f47c1-7b2c-7abc-8def-123456789006"
BASELINE_ID = "base_018f47c1-7b2c-7abc-8def-123456789003"
GATE_ID = "gate_018f47c1-7b2c-7abc-8def-123456789020"
EVALUATION_RECORD_ID = "geval_018f47c1-7b2c-7abc-8def-123456789030"


def _basis(**changes: object) -> HumanActionBasis:
    values: dict[str, object] = {
        "evaluation_record_id": EVALUATION_RECORD_ID,
        "slice_id": SLICE_ID,
        "baseline_id": BASELINE_ID,
        "lifecycle_revision": 2,
        "governance_revision": 3,
        "gate_refs": (GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
    }
    values.update(changes)
    return HumanActionBasis.model_validate(values)


def _identity(basis: HumanActionBasis | None = None) -> DecisionBasisIdentityV1:
    exact_basis = basis or _basis()
    return DecisionBasisIdentityV1(
        decision_kind=DecisionKind.GATE_APPROVAL,
        slice_id=exact_basis.slice_id,
        gate_ref=GateRevisionRef(gate_id=GATE_ID, gate_revision=1),
        target_phase=LifecyclePhase.IMPLEMENTING,
        human_action_basis=exact_basis,
        decision_state=DecisionCardState.PENDING_REQUIRED,
    )


def test_canonical_digest_has_frozen_vector_and_is_repeatable() -> None:
    identity = _identity()
    assert (
        identity.digest()
        == "sha256:ffed51f0ff60997772916e0467c023e6467a03bf1567bab83834092942aa34e1"
    )
    assert identity.digest() == _identity().digest()


def test_every_mutable_human_action_basis_field_rotates_digest() -> None:
    mutations = (
        {"evaluation_record_id": "geval_018f47c1-7b2c-7abc-8def-123456789031"},
        {"slice_id": "slc_018f47c1-7b2c-7abc-8def-123456789007"},
        {"baseline_id": "base_018f47c1-7b2c-7abc-8def-123456789004"},
        {"lifecycle_revision": 4},
        {"governance_revision": 4},
        {
            "gate_refs": (
                GateRevisionRef(
                    gate_id="gate_018f47c1-7b2c-7abc-8def-123456789021",
                    gate_revision=2,
                ),
            )
        },
        {
            "current_approval_decision_ids": (
                {
                    "gate_id": GATE_ID,
                    "decision_id": "hdec_018f47c1-7b2c-7abc-8def-123456789032",
                },
            )
        },
        {"current_choice_decision_id": "hdec_018f47c1-7b2c-7abc-8def-123456789033"},
        {
            "current_result_id": "res_018f47c1-7b2c-7abc-8def-123456789034",
            "current_result_baseline_id": BASELINE_ID,
        },
        {
            "current_result_id": "res_018f47c1-7b2c-7abc-8def-123456789034",
            "current_result_baseline_id": "base_018f47c1-7b2c-7abc-8def-123456789004",
        },
        {
            "current_result_id": "res_018f47c1-7b2c-7abc-8def-123456789034",
            "current_result_baseline_id": BASELINE_ID,
            "current_manual_evaluation_id": "eval_018f47c1-7b2c-7abc-8def-123456789035",
        },
    )
    original = _identity().digest()
    for mutation in mutations:
        assert _identity(_basis(**mutation)).digest() != original


def test_decision_specific_selectors_rotate_digest() -> None:
    identity = _identity()
    approval = identity.model_copy(
        update={
            "expected_current_approval_decision_id": "hdec_018f47c1-7b2c-7abc-8def-123456789032"
        }
    )
    assert approval.digest() != identity.digest()
    choice_base = DecisionBasisIdentityV1(
        decision_kind=DecisionKind.GATE_PATH_CHOICE,
        slice_id=SLICE_ID,
        gate_ref=None,
        target_phase=None,
        human_action_basis=_basis(),
        decision_state=DecisionCardState.PENDING_REQUIRED,
        eligible_choice_gate_refs=(GateRevisionRef(gate_id=GATE_ID, gate_revision=1),),
    )
    choice_id = choice_base.model_copy(
        update={"expected_current_choice_decision_id": "hdec_018f47c1-7b2c-7abc-8def-123456789033"}
    )
    choice_set = choice_base.model_copy(
        update={
            "eligible_choice_gate_refs": (
                GateRevisionRef(gate_id=GATE_ID, gate_revision=1),
                GateRevisionRef(
                    gate_id="gate_018f47c1-7b2c-7abc-8def-123456789021",
                    gate_revision=1,
                ),
            )
        }
    )
    assert choice_id.digest() != choice_base.digest()
    assert choice_set.digest() != choice_base.digest()
    technical_basis = _basis(
        current_result_id="res_018f47c1-7b2c-7abc-8def-123456789034",
        current_result_baseline_id=BASELINE_ID,
        current_manual_evaluation_id="eval_018f47c1-7b2c-7abc-8def-123456789035",
    )
    technical = DecisionBasisIdentityV1(
        decision_kind=DecisionKind.TECHNICAL_ACCEPTANCE,
        slice_id=SLICE_ID,
        gate_ref=GateRevisionRef(gate_id=GATE_ID, gate_revision=1),
        target_phase=LifecyclePhase.ACCEPTED,
        human_action_basis=technical_basis,
        decision_state=DecisionCardState.PENDING_REQUIRED,
        expected_result_id=technical_basis.current_result_id,
        expected_manual_evaluation_id=technical_basis.current_manual_evaluation_id,
    )
    assert (
        technical.model_copy(
            update={"expected_result_id": "res_018f47c1-7b2c-7abc-8def-123456789036"}
        ).digest()
        != technical.digest()
    )
    assert (
        technical.model_copy(
            update={"expected_manual_evaluation_id": "eval_018f47c1-7b2c-7abc-8def-123456789037"}
        ).digest()
        != technical.digest()
    )
    assert (
        technical.model_copy(
            update={
                "expected_current_approval_decision_id": "hdec_018f47c1-7b2c-7abc-8def-123456789032"
            }
        ).digest()
        != technical.digest()
    )


def test_presentation_wording_is_not_in_digest_and_statements_are_non_inferential() -> None:
    identity = _identity()
    first = DecisionStatement(text="First wording", basis=DecisionStatementBasis.CANONICAL_FACT)
    second = DecisionStatement(
        text="Different wording", basis=DecisionStatementBasis.CANONICAL_FACT
    )
    assert first.text != second.text
    assert identity.digest() == _identity().digest()
    with pytest.raises(ValidationError):
        DecisionStatement(text="Inference", basis=DecisionStatementBasis.MODEL_INFERENCE)


def test_models_are_frozen_and_extra_forbid() -> None:
    statement = DecisionStatement(text="A fact", basis=DecisionStatementBasis.CANONICAL_FACT)
    with pytest.raises(ValidationError):
        statement.text = "Changed"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        DecisionStatement(text="A fact", basis=DecisionStatementBasis.CANONICAL_FACT, invented=True)
