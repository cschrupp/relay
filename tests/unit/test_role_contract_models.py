"""Structural and canonical identity tests for Role Contract values."""

import hashlib
import json

import pytest
from pydantic import ValidationError

from relay_engine.agent_runtime import RuntimeCapability
from relay_engine.domain import ActorKind
from relay_engine.role_contracts import (
    RoleAction,
    RoleClass,
    RoleContract,
    RoleContractRef,
    RoleInputRequirement,
    RoleOutputRequirement,
    VerificationAssetPermission,
    canonical_role_contract_json,
    digest_role_contract,
    role_contract_ref,
    role_contract_ref_matches,
)


def contract(**updates: object) -> RoleContract:
    values: dict[str, object] = {
        "role_key": "implementer",
        "revision": 1,
        "role_class": RoleClass.IMPLEMENTER,
        "allowed_actor_kinds": (ActorKind.AGENT,),
        "allowed_actions": (RoleAction.CONTEXT_READ,),
        "prohibited_actions": tuple(
            action for action in RoleAction if action is not RoleAction.CONTEXT_READ
        ),
        "required_inputs": (RoleInputRequirement.AUTHORIZED_WORK_BASIS,),
        "required_outputs": (RoleOutputRequirement.ENGINEERING_RESULT,),
        "verification_asset_permissions": (VerificationAssetPermission.READ,),
        "required_runtime_capabilities": (RuntimeCapability.EXECUTE,),
        "required_assurance_properties": ("RELAY_ACTOR_IDENTITY_BOUND",),
    }
    values.update(updates)
    return RoleContract(**values)  # type: ignore[arg-type]


def test_contract_is_frozen_versioned_strict_and_has_no_role_uuid() -> None:
    value = contract()
    assert value.model_config["frozen"] is True
    assert value.model_config["extra"] == "forbid"
    assert value.model_dump(mode="json")["schema_version"] == 1
    assert "id" not in RoleContract.model_fields
    with pytest.raises(ValidationError):
        value.role_key = "another-role"
    with pytest.raises(ValidationError):
        RoleContract.model_validate({**value.model_dump(), "unexpected": True})


@pytest.mark.parametrize("role_key", ["", "Upper", "-bad", "a--b", "a_underscore", "a" * 65])
def test_role_key_must_be_lowercase_stable_and_bounded(role_key: str) -> None:
    with pytest.raises(ValidationError):
        contract(role_key=role_key)


def test_contract_validates_revision_actor_and_complete_action_partition() -> None:
    with pytest.raises(ValidationError):
        contract(revision=0)
    with pytest.raises(ValidationError, match="must not be empty"):
        contract(allowed_actor_kinds=())
    with pytest.raises(ValidationError, match="classify every RoleAction"):
        contract(prohibited_actions=(RoleAction.IMPLEMENTATION_MUTATE,))
    with pytest.raises(ValidationError, match="disjoint"):
        contract(prohibited_actions=tuple(RoleAction))
    assert set(contract().allowed_actions) | set(contract().prohibited_actions) == set(RoleAction)


def test_contract_rejects_duplicate_or_noncanonical_enum_tuples() -> None:
    with pytest.raises(ValidationError, match="unique"):
        contract(allowed_actions=(RoleAction.CONTEXT_READ, RoleAction.CONTEXT_READ))
    with pytest.raises(ValidationError, match="declaration order"):
        contract(allowed_actions=(RoleAction.IMPLEMENTATION_MUTATE, RoleAction.CONTEXT_READ))
    with pytest.raises(ValidationError, match="unique"):
        contract(required_inputs=(RoleInputRequirement.AUTHORIZED_WORK_BASIS,) * 2)
    with pytest.raises(ValidationError, match="declaration order"):
        contract(required_outputs=tuple(reversed(tuple(RoleOutputRequirement))))
    with pytest.raises(ValidationError, match="unique"):
        contract(required_runtime_capabilities=(RuntimeCapability.EXECUTE,) * 2)


def test_assurance_properties_are_unique_and_lexically_ordered() -> None:
    with pytest.raises(ValidationError, match="unique"):
        contract(required_assurance_properties=("RELAY_A", "RELAY_A"))
    with pytest.raises(ValidationError, match="lexical order"):
        contract(required_assurance_properties=("RELAY_Z", "RELAY_A"))


def test_human_authority_role_allows_only_human_actor_kind() -> None:
    with pytest.raises(ValidationError, match="only HUMAN"):
        contract(role_class=RoleClass.HUMAN_AUTHORITY)
    assert contract(
        role_class=RoleClass.HUMAN_AUTHORITY,
        allowed_actor_kinds=(ActorKind.HUMAN,),
    ).allowed_actor_kinds == (ActorKind.HUMAN,)


def test_canonical_json_digest_and_reference_are_deterministic() -> None:
    value = contract(
        role_key="evaluator",
        required_inputs=(RoleInputRequirement.AUTHORIZED_WORK_BASIS,),
        required_outputs=(RoleOutputRequirement.ENGINEERING_RESULT,),
    )
    canonical = canonical_role_contract_json(value)
    assert json.loads(canonical)["schema_version"] == 1
    assert '"role_key":"evaluator"' in canonical
    expected_canonical = (
        '{"allowed_actions":["CONTEXT_READ"],"allowed_actor_kinds":["AGENT"],'
        '"prohibited_actions":["IMPLEMENTATION_MUTATE","IMPLEMENTATION_TEST_MUTATE",'
        '"VERIFICATION_EXECUTE","EVALUATE_RESULT","AUTHORIZE_WORK","ACCEPT_RESULT",'
        '"PROMOTE_RESULT","DECOMPOSE_AUTHORIZED_WORK","PROPOSE_FUTURE_WORK"],'
        '"required_assurance_properties":["RELAY_ACTOR_IDENTITY_BOUND"],'
        '"required_inputs":["AUTHORIZED_WORK_BASIS"],'
        '"required_outputs":["ENGINEERING_RESULT"],'
        '"required_runtime_capabilities":["EXECUTE"],"revision":1,'
        '"role_class":"IMPLEMENTER","role_key":"evaluator","schema_version":1,'
        '"verification_asset_permissions":["READ"]}'
    )
    expected_digest = "sha256:0eec7837c01d917fa4b5cc85c23f4d76e4eb9d6f876ee7d7b812df80c0f3714e"
    assert canonical == expected_canonical
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == expected_digest.removeprefix(
        "sha256:"
    )
    assert digest_role_contract(value) == expected_digest
    assert role_contract_ref(value) == RoleContractRef(
        role_key="evaluator",
        revision=1,
        content_digest=expected_digest,
    )
    assert role_contract_ref_matches(value, role_contract_ref(value))


def test_each_normative_field_changes_contract_digest() -> None:
    original = contract()
    changed = contract(
        required_outputs=(
            RoleOutputRequirement.ENGINEERING_RESULT,
            RoleOutputRequirement.WORK_DISPOSITION,
        )
    )
    assert digest_role_contract(changed) != digest_role_contract(original)
    wrong_ref = role_contract_ref(original).model_copy(
        update={"content_digest": "sha256:" + "0" * 64}
    )
    assert not role_contract_ref_matches(original, wrong_ref)
