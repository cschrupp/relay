"""Exact-subject and materialization conformance tests for Slice 2.3."""

from __future__ import annotations

import pytest
from test_work_packet_models import D1, D2, D3, artifact, manifest, packet

from relay_engine.domain import CommitRef
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleApplicabilityEvaluation,
    RoleContractApplicability,
    RoleReason,
    VerificationAssetPermission,
)
from relay_engine.work_packets.evaluation import (
    control_subject_digest,
    evaluate_context_conformance,
    evaluate_work_packet_conformance,
)
from relay_engine.work_packets.models import (
    AcceptedDesignFact,
    ArtifactMaterialRef,
    AuthorityBasisFact,
    AuthorityBasisRef,
    AuthorityReferenceType,
    ContextManifest,
    ContextManifestFact,
    ContextMaterializationFact,
    ContextSourceKind,
    ContextSourceRef,
    ControlMirrorBinding,
    ControlMirrorKind,
    GovernanceProfileFact,
    GovernanceProfileRef,
    PolicyBasisFact,
    ProtectedVerificationAuthorityFact,
    ProtectedVerificationRequirement,
    SliceDefinitionFact,
    SourceBaselineFact,
    WorkPacket,
    WorkPacketConformanceFacts,
    WorkPacketReason,
    context_manifest_ref,
    material_digests,
    protected_verification_requirement_ref,
    work_packet_ref,
)


def materialization_facts_for(
    current_packet: WorkPacket, current_manifest: ContextManifest
) -> tuple[ContextMaterializationFact, ...]:
    values: list[ContextMaterializationFact] = []
    for key in current_packet.required_context_keys:
        entry = next(item for item in current_manifest.entries if item.entry_key == key)
        content_digest, provenance_digest = material_digests(entry.source.material_ref)
        values.append(
            ContextMaterializationFact(
                evaluated_material_ref=entry.source.material_ref,
                material_status=RequirementStatus.SATISFIED,
                observed_content_digest=content_digest,
                observed_provenance_digest=provenance_digest,
            )
        )
    return tuple(values)


def conforming_facts(
    current_packet: WorkPacket, current_manifest: ContextManifest
) -> WorkPacketConformanceFacts:
    return WorkPacketConformanceFacts(
        evaluated_work_packet_ref=work_packet_ref(current_packet),
        evaluated_context_manifest_ref=context_manifest_ref(current_manifest),
        slice_definition_fact=SliceDefinitionFact(
            evaluated_ref=current_packet.slice_definition_ref,
            status=RequirementStatus.SATISFIED,
        ),
        source_baseline_fact=SourceBaselineFact(
            evaluated_ref=current_packet.source_baseline_ref,
            status=RequirementStatus.SATISFIED,
        ),
        authority_facts=tuple(
            AuthorityBasisFact(evaluated_ref=ref, status=RequirementStatus.SATISFIED)
            for ref in current_packet.authority_refs
        ),
        policy_basis_fact=PolicyBasisFact(
            evaluated_ref=current_packet.policy_basis_ref,
            status=RequirementStatus.SATISFIED,
        ),
        governance_profile_fact=GovernanceProfileFact(
            evaluated_policy_basis_ref=current_packet.policy_basis_ref,
            evaluated_profile_ref=current_packet.governance_profile_ref,
            profile_requirement_status=RequirementStatus.SATISFIED,
            profile_status=RequirementStatus.SATISFIED,
        ),
        role_contract_applicability=RoleApplicabilityEvaluation(
            role_contract_ref=current_packet.role_contract_ref,
            status=RoleContractApplicability.APPLICABLE,
            reason=None,
        ),
        accepted_design_facts=tuple(
            AcceptedDesignFact(evaluated_artifact=item, status=RequirementStatus.SATISFIED)
            for item in current_packet.accepted_design_artifacts
        ),
        context_manifest_fact=ContextManifestFact(
            evaluated_ref=current_packet.context_manifest_ref,
            status=RequirementStatus.SATISFIED,
        ),
        protected_verification_authority_facts=tuple(
            ProtectedVerificationAuthorityFact(
                evaluated_requirement_ref=protected_verification_requirement_ref(requirement),
                evaluated_authority_ref=requirement.separate_authority_ref,
                status=RequirementStatus.SATISFIED,
            )
            for requirement in current_packet.protected_verification_requirements
            if requirement.separate_authority_ref is not None
        ),
        materialization_facts=materialization_facts_for(current_packet, current_manifest),
    )


def packet_with_three_plural_subjects() -> tuple[WorkPacket, ContextManifest]:
    base = packet()
    current_manifest = manifest(all_materials=True)

    authorities = tuple(
        base.authority_refs[0].model_copy(
            update={
                "authority_key": f"slice-authorization-{letter}",
                "record_digest": digest,
            }
        )
        for letter, digest in (("a", D1), ("b", D2), ("c", D3))
    )
    artifacts = tuple(
        artifact().model_copy(
            update={
                "id": f"art_00000000-0000-4000-8000-00000000000{number}",
                "path": f"docs/design-{letter}.md",
                "content_digest": digest,
            }
        )
        for letter, number, digest in (("a", 6, D1), ("b", 7, D2), ("c", 8, D3))
    )
    protected_requirements = tuple(
        base.protected_verification_requirements[0].model_copy(
            update={
                "artifact": artifact_item,
                "required_operation": VerificationAssetPermission.MODIFY,
                "separate_authority_ref": AuthorityBasisRef(
                    authority_type=AuthorityReferenceType.REPOSITORY_MUTATION_AUTHORIZATION,
                    authority_key=f"mutation-{letter}",
                    record_digest=digest,
                    subject_digest=D1,
                ),
            }
        )
        for letter, artifact_item, digest in zip(
            ("a", "b", "c"), artifacts, (D1, D2, D3), strict=True
        )
    )
    current_packet = type(base).model_validate(
        {
            **base.model_dump(),
            "authority_refs": authorities,
            "accepted_design_artifacts": artifacts,
            "protected_verification_requirements": protected_requirements,
            "context_manifest_ref": context_manifest_ref(current_manifest),
            "required_context_keys": ("entry-1", "entry-2", "entry-3"),
        }
    )
    return current_packet, current_manifest


def test_exact_fact_set_satisfies_without_authority_semantics() -> None:
    current_packet = packet()
    current_manifest = manifest()
    result = evaluate_work_packet_conformance(
        current_packet,
        current_manifest,
        conforming_facts(current_packet, current_manifest),
    )
    assert result.status is RequirementStatus.SATISFIED
    assert "AUTHORIZED" not in {item.value for item in RequirementStatus}


def test_packet_a_facts_cannot_satisfy_packet_b_or_new_revision() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    other_packet = packet(packet_key="packet-other")
    other_revision = packet(packet_revision=2)
    for subject in (other_packet, other_revision):
        result = evaluate_work_packet_conformance(subject, current_manifest, facts)
        assert result.status is RequirementStatus.UNSATISFIED
        assert WorkPacketReason.WORK_PACKET_REF_MISMATCH in result.reasons


def test_changed_manifest_slice_baseline_or_policy_is_exact_subject_failure() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    wrong_manifest = current_manifest.model_copy(update={"revision": 2})
    assert (
        evaluate_work_packet_conformance(current_packet, wrong_manifest, facts).status
        is RequirementStatus.UNSATISFIED
    )

    changed_slice = current_packet.slice_definition_ref.model_copy(
        update={"definition_revision": 2}
    )
    altered_packet = type(current_packet).model_validate(
        {**current_packet.model_dump(), "slice_definition_ref": changed_slice.model_dump()}
    )
    assert (
        evaluate_work_packet_conformance(altered_packet, current_manifest, facts).status
        is RequirementStatus.UNSATISFIED
    )

    changed_policy = current_packet.policy_basis_ref.model_copy(update={"policy_version": 2})
    altered_facts = facts.model_copy(
        update={
            "policy_basis_fact": PolicyBasisFact(
                evaluated_ref=changed_policy, status=RequirementStatus.SATISFIED
            )
        }
    )
    result = evaluate_work_packet_conformance(current_packet, current_manifest, altered_facts)
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.POLICY_FACT_SUBJECT_MISMATCH in result.reasons

    changed_baseline = current_packet.source_baseline_ref.model_copy(update={"content_digest": D3})
    baseline_facts = facts.model_copy(
        update={
            "source_baseline_fact": SourceBaselineFact(
                evaluated_ref=changed_baseline,
                status=RequirementStatus.SATISFIED,
            )
        }
    )
    baseline_result = evaluate_work_packet_conformance(
        current_packet, current_manifest, baseline_facts
    )
    assert baseline_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.SOURCE_BASELINE_FACT_SUBJECT_MISMATCH in baseline_result.reasons

    changed_manifest_fact = facts.model_copy(
        update={
            "context_manifest_fact": ContextManifestFact(
                evaluated_ref=context_manifest_ref(wrong_manifest),
                status=RequirementStatus.SATISFIED,
            )
        }
    )
    manifest_result = evaluate_work_packet_conformance(
        current_packet, current_manifest, changed_manifest_fact
    )
    assert manifest_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.CONTEXT_MANIFEST_FACT_SUBJECT_MISMATCH in manifest_result.reasons


def test_missing_authority_fact_is_indeterminate_and_wrong_or_extra_is_unsatisfied() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    missing = facts.model_copy(update={"authority_facts": ()})
    assert (
        evaluate_work_packet_conformance(current_packet, current_manifest, missing).status
        is RequirementStatus.INDETERMINATE
    )

    wrong_ref = current_packet.authority_refs[0].model_copy(update={"record_digest": D3})
    wrong = facts.model_copy(
        update={
            "authority_facts": (
                AuthorityBasisFact(evaluated_ref=wrong_ref, status=RequirementStatus.SATISFIED),
            )
        }
    )
    assert (
        evaluate_work_packet_conformance(current_packet, current_manifest, wrong).status
        is RequirementStatus.UNSATISFIED
    )

    extra = facts.model_copy(
        update={"authority_facts": (*facts.authority_facts, facts.authority_facts[0])}
    )
    assert (
        evaluate_work_packet_conformance(current_packet, current_manifest, extra).status
        is RequirementStatus.UNSATISFIED
    )


@pytest.mark.parametrize("fact_family", ("authority", "accepted", "protected", "material"))
@pytest.mark.parametrize("missing_position", (0, 1, 2))
def test_missing_first_middle_or_last_plural_fact_is_indeterminate(
    fact_family: str, missing_position: int
) -> None:
    current_packet, current_manifest = packet_with_three_plural_subjects()
    facts = conforming_facts(current_packet, current_manifest)
    field_by_family = {
        "authority": "authority_facts",
        "accepted": "accepted_design_facts",
        "protected": "protected_verification_authority_facts",
        "material": "materialization_facts",
    }
    field_name = field_by_family[fact_family]
    complete_facts = getattr(facts, field_name)
    assert len(complete_facts) == 3
    incomplete_facts = (*complete_facts[:missing_position], *complete_facts[missing_position + 1 :])
    missing = facts.model_copy(update={field_name: incomplete_facts})

    result = evaluate_work_packet_conformance(current_packet, current_manifest, missing)

    assert result.status is RequirementStatus.INDETERMINATE


def test_role_applicability_is_bound_to_exact_role_contract_ref() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    other_role = current_packet.role_contract_ref.model_copy(update={"role_key": "reviewer"})
    mismatched = facts.model_copy(
        update={
            "role_contract_applicability": RoleApplicabilityEvaluation(
                role_contract_ref=other_role,
                status=RoleContractApplicability.APPLICABLE,
                reason=None,
            )
        }
    )
    result = evaluate_work_packet_conformance(current_packet, current_manifest, mismatched)
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.ROLE_APPLICABILITY_SUBJECT_MISMATCH in result.reasons

    not_applicable = facts.model_copy(
        update={
            "role_contract_applicability": RoleApplicabilityEvaluation(
                role_contract_ref=current_packet.role_contract_ref,
                status=RoleContractApplicability.NOT_APPLICABLE,
                reason=RoleReason.ROLE_CONTRACT_NOT_APPLICABLE,
            )
        }
    )
    assert (
        evaluate_work_packet_conformance(current_packet, current_manifest, not_applicable).status
        is RequirementStatus.UNSATISFIED
    )

    indeterminate = facts.model_copy(
        update={
            "role_contract_applicability": RoleApplicabilityEvaluation(
                role_contract_ref=current_packet.role_contract_ref,
                status=RoleContractApplicability.INDETERMINATE,
                reason=RoleReason.ROLE_CONTRACT_APPLICABILITY_UNKNOWN,
            )
        }
    )
    assert (
        evaluate_work_packet_conformance(current_packet, current_manifest, indeterminate).status
        is RequirementStatus.INDETERMINATE
    )


def test_missing_profile_not_required_fact_is_indeterminate() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    unknown = facts.model_copy(
        update={
            "governance_profile_fact": GovernanceProfileFact(
                evaluated_policy_basis_ref=current_packet.policy_basis_ref,
                evaluated_profile_ref=None,
                profile_requirement_status=RequirementStatus.INDETERMINATE,
                profile_status=RequirementStatus.INDETERMINATE,
            )
        }
    )
    result = evaluate_work_packet_conformance(current_packet, current_manifest, unknown)
    assert result.status is RequirementStatus.INDETERMINATE
    assert WorkPacketReason.GOVERNANCE_PROFILE_STALE in result.reasons

    other_profile = GovernanceProfileFact(
        evaluated_policy_basis_ref=current_packet.policy_basis_ref,
        evaluated_profile_ref=current_packet.governance_profile_ref,
        profile_requirement_status=RequirementStatus.SATISFIED,
        profile_status=RequirementStatus.SATISFIED,
    )
    current_with_profile = type(current_packet).model_validate(
        {
            **current_packet.model_dump(),
            "governance_profile_ref": {
                "profile_key": "other-profile",
                "profile_version": 1,
                "content_digest": D3,
                "policy_basis_digest": D2,
                "schema_version": 1,
            },
        }
    )
    mismatched = facts.model_copy(update={"governance_profile_fact": other_profile})
    mismatch_result = evaluate_work_packet_conformance(
        current_with_profile, current_manifest, mismatched
    )
    assert mismatch_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.GOVERNANCE_PROFILE_FACT_SUBJECT_MISMATCH in mismatch_result.reasons


@pytest.mark.parametrize(
    "profile_status",
    (RequirementStatus.UNSATISFIED, RequirementStatus.INDETERMINATE),
)
def test_absent_profile_ignores_status_for_nonexistent_profile(
    profile_status: RequirementStatus,
) -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = conforming_facts(current_packet, current_manifest)
    no_profile_fact = GovernanceProfileFact(
        evaluated_policy_basis_ref=current_packet.policy_basis_ref,
        evaluated_profile_ref=None,
        profile_requirement_status=RequirementStatus.SATISFIED,
        profile_status=profile_status,
    )

    result = evaluate_work_packet_conformance(
        current_packet,
        current_manifest,
        facts.model_copy(update={"governance_profile_fact": no_profile_fact}),
    )

    assert result.status is RequirementStatus.SATISFIED


def test_fact_tuple_order_is_noncanonical_and_cannot_be_adopted() -> None:
    base = packet()
    second_authority = base.authority_refs[0].model_copy(
        update={"authority_key": "z-authority", "record_digest": D3}
    )
    packet_with_two = type(base).model_validate(
        {
            **base.model_dump(),
            "authority_refs": (base.authority_refs[0].model_dump(), second_authority.model_dump()),
        }
    )
    current_manifest = manifest()
    facts = conforming_facts(packet_with_two, current_manifest)
    reversed_facts = facts.model_copy(
        update={"authority_facts": tuple(reversed(facts.authority_facts))}
    )
    result = evaluate_work_packet_conformance(packet_with_two, current_manifest, reversed_facts)
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.AUTHORITY_FACT_SET_MISMATCH in result.reasons

    partial_failed = facts.model_copy(
        update={
            "authority_facts": (
                AuthorityBasisFact(
                    evaluated_ref=packet_with_two.authority_refs[0],
                    status=RequirementStatus.UNSATISFIED,
                ),
            )
        }
    )
    failed_result = evaluate_work_packet_conformance(
        packet_with_two, current_manifest, partial_failed
    )
    assert failed_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.AUTHORITY_BASIS_CONFLICT in failed_result.reasons


def test_accepted_design_and_protected_requirement_facts_are_exact() -> None:
    base = packet()
    current_manifest = manifest()
    first_artifact = artifact()
    packet_a = type(base).model_validate(
        {**base.model_dump(), "accepted_design_artifacts": (first_artifact.model_dump(),)}
    )
    facts_a = conforming_facts(packet_a, current_manifest)
    other_artifact = first_artifact.model_copy(
        update={
            "content_digest": D3,
            "commit": CommitRef(
                repository=first_artifact.commit.repository,
                sha="b" * 40,
            ),
        }
    )
    packet_b = type(base).model_validate(
        {**packet_a.model_dump(), "accepted_design_artifacts": (other_artifact.model_dump(),)}
    )
    design_result = evaluate_work_packet_conformance(packet_b, current_manifest, facts_a)
    assert design_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.ACCEPTED_DESIGN_FACT_SET_MISMATCH in design_result.reasons

    authority_a = ProtectedVerificationRequirement(
        artifact=artifact(),
        required_operation=VerificationAssetPermission.MODIFY,
        separate_authority_ref=AuthorityBasisRef(
            authority_type=AuthorityReferenceType.REPOSITORY_MUTATION_AUTHORIZATION,
            authority_key="mutation-a",
            record_digest=D2,
            subject_digest=D1,
        ),
    )
    packet_with_auth_a = type(base).model_validate(
        {**base.model_dump(), "protected_verification_requirements": (authority_a.model_dump(),)}
    )
    facts_with_auth_a = conforming_facts(packet_with_auth_a, current_manifest)
    authority_b = ProtectedVerificationRequirement(
        artifact=artifact(),
        required_operation=VerificationAssetPermission.MODIFY,
        separate_authority_ref=AuthorityBasisRef(
            authority_type=AuthorityReferenceType.REPOSITORY_MUTATION_AUTHORIZATION,
            authority_key="mutation-b",
            record_digest=D3,
            subject_digest=D1,
        ),
    )
    packet_with_auth_b = type(base).model_validate(
        {**base.model_dump(), "protected_verification_requirements": (authority_b.model_dump(),)}
    )
    protected_result = evaluate_work_packet_conformance(
        packet_with_auth_b, current_manifest, facts_with_auth_a
    )
    assert protected_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.PROTECTED_VERIFICATION_FACT_SET_MISMATCH in protected_result.reasons


def test_protected_mutation_conformance_does_not_issue_authority() -> None:
    base = packet()
    current_manifest = manifest()
    requirement = base.protected_verification_requirements[0].model_copy(
        update={
            "required_operation": VerificationAssetPermission.MODIFY,
            "separate_authority_ref": None,
        }
    )
    no_authority = type(base).model_validate(
        {**base.model_dump(), "protected_verification_requirements": (requirement.model_dump(),)}
    )
    result = evaluate_work_packet_conformance(
        no_authority,
        current_manifest,
        conforming_facts(no_authority, current_manifest),
    )
    assert result.status is RequirementStatus.SATISFIED
    assert not hasattr(result, "authorized")

    separate_ref = AuthorityBasisRef(
        authority_type=AuthorityReferenceType.REPOSITORY_MUTATION_AUTHORIZATION,
        authority_key="protected-mutation",
        record_digest=D3,
        subject_digest=D1,
    )
    authorized_requirement = requirement.model_copy(update={"separate_authority_ref": separate_ref})
    with_authority = type(base).model_validate(
        {
            **base.model_dump(),
            "protected_verification_requirements": (authorized_requirement.model_dump(),),
        }
    )
    good_facts = conforming_facts(with_authority, current_manifest)
    assert (
        evaluate_work_packet_conformance(with_authority, current_manifest, good_facts).status
        is RequirementStatus.SATISFIED
    )
    missing = good_facts.model_copy(update={"protected_verification_authority_facts": ()})
    assert (
        evaluate_work_packet_conformance(with_authority, current_manifest, missing).status
        is RequirementStatus.INDETERMINATE
    )


@pytest.mark.parametrize("material_index", [0, 1, 2])
def test_unavailable_material_variants_are_indeterminate(material_index: int) -> None:
    current_manifest = manifest(all_materials=True)
    entry = current_manifest.entries[material_index]
    current_packet = packet()
    changed_manifest = current_manifest.model_copy(update={"entries": (entry,)})
    changed_packet = type(current_packet).model_validate(
        {
            **current_packet.model_dump(),
            "context_manifest_ref": context_manifest_ref(changed_manifest).model_dump(),
            "required_context_keys": (entry.entry_key,),
        }
    )
    result = evaluate_context_conformance(changed_packet, changed_manifest, ())
    assert result.status is RequirementStatus.INDETERMINATE
    expected_reason = (
        WorkPacketReason.CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED
        if material_index == 2
        else WorkPacketReason.CONTEXT_MATERIAL_UNAVAILABLE
    )
    assert expected_reason in result.reasons


def test_exact_material_is_satisfied_and_content_or_provenance_mismatch_fails() -> None:
    current_packet = packet()
    current_manifest = manifest()
    good_facts = materialization_facts_for(current_packet, current_manifest)
    assert (
        evaluate_context_conformance(current_packet, current_manifest, good_facts).status
        is RequirementStatus.SATISFIED
    )

    material = good_facts[0]
    content_mismatch = material.model_copy(
        update={"material_status": RequirementStatus.UNSATISFIED, "observed_content_digest": D2}
    )
    content_result = evaluate_context_conformance(
        current_packet, current_manifest, (content_mismatch,)
    )
    assert content_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.CONTEXT_MATERIAL_CONTENT_MISMATCH in content_result.reasons

    provenance_mismatch = material.model_copy(
        update={"material_status": RequirementStatus.UNSATISFIED, "observed_provenance_digest": D1}
    )
    provenance_result = evaluate_context_conformance(
        current_packet, current_manifest, (provenance_mismatch,)
    )
    assert provenance_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.CONTEXT_MATERIAL_PROVENANCE_MISMATCH in provenance_result.reasons


def test_two_required_context_keys_may_share_exact_material_ref() -> None:
    current_packet = packet()
    original_manifest = manifest()
    first_entry = original_manifest.entries[0]
    second_entry = first_entry.model_copy(update={"entry_key": "entry-2"})
    current_manifest = type(original_manifest).model_validate(
        {
            **original_manifest.model_dump(),
            "entries": (first_entry.model_dump(), second_entry.model_dump()),
        }
    )
    current_packet = type(current_packet).model_validate(
        {
            **current_packet.model_dump(),
            "context_manifest_ref": context_manifest_ref(current_manifest),
            "required_context_keys": ("entry-1", "entry-2"),
        }
    )
    duplicate_facts = materialization_facts_for(current_packet, current_manifest)

    result = evaluate_context_conformance(current_packet, current_manifest, duplicate_facts)

    assert len(duplicate_facts) == 2
    assert duplicate_facts[0].evaluated_material_ref == duplicate_facts[1].evaluated_material_ref
    assert result.status is RequirementStatus.SATISFIED

    missing_second_position = evaluate_context_conformance(
        current_packet, current_manifest, duplicate_facts[:1]
    )
    assert missing_second_position.status is RequirementStatus.INDETERMINATE


def test_context_fact_for_different_material_cannot_satisfy_required_entry() -> None:
    current_packet = packet()
    current_manifest = manifest()
    facts = materialization_facts_for(current_packet, current_manifest)
    altered_ref = facts[0].evaluated_material_ref.model_copy(update={"provenance_digest": D3})
    altered_fact = facts[0].model_copy(update={"evaluated_material_ref": altered_ref})
    result = evaluate_context_conformance(current_packet, current_manifest, (altered_fact,))
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.MATERIALIZATION_FACT_SET_MISMATCH in result.reasons


def test_control_mirror_binds_exact_packet_subject_and_mismatch_fails() -> None:
    current_packet = packet()
    current_manifest = manifest()
    entry = current_manifest.entries[0]
    expected_digest = control_subject_digest(current_packet, ControlMirrorKind.ROLE_CONTRACT)
    assert expected_digest is not None
    matching_entry = entry.model_copy(
        update={
            "control_mirror_binding": ControlMirrorBinding(
                mirror_kind=ControlMirrorKind.ROLE_CONTRACT,
                control_subject_digest=expected_digest,
            )
        }
    )
    matching_manifest = current_manifest.model_copy(update={"entries": (matching_entry,)})
    matching_packet = type(current_packet).model_validate(
        {
            **current_packet.model_dump(),
            "context_manifest_ref": context_manifest_ref(matching_manifest).model_dump(),
        }
    )
    good = materialization_facts_for(matching_packet, matching_manifest)
    assert (
        evaluate_context_conformance(matching_packet, matching_manifest, good).status
        is RequirementStatus.SATISFIED
    )

    bad_entry = entry.model_copy(
        update={
            "control_mirror_binding": ControlMirrorBinding(
                mirror_kind=ControlMirrorKind.ROLE_CONTRACT,
                control_subject_digest=D2,
            )
        }
    )
    bad_manifest = current_manifest.model_copy(update={"entries": (bad_entry,)})
    bad_packet = type(current_packet).model_validate(
        {
            **current_packet.model_dump(),
            "context_manifest_ref": context_manifest_ref(bad_manifest).model_dump(),
        }
    )
    result = evaluate_context_conformance(
        bad_packet,
        bad_manifest,
        materialization_facts_for(bad_packet, bad_manifest),
    )
    assert result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.CONTROL_MIRROR_CONFLICT in result.reasons


@pytest.mark.parametrize("kind", tuple(ControlMirrorKind))
def test_each_control_mirror_kind_is_bound_to_packet_reference(kind: ControlMirrorKind) -> None:
    base = packet()
    if kind is ControlMirrorKind.GOVERNANCE_PROFILE:
        candidate = type(base).model_validate(
            {
                **base.model_dump(),
                "governance_profile_ref": GovernanceProfileRef(
                    profile_key="profile-main",
                    profile_version=1,
                    content_digest=D3,
                    policy_basis_digest=D2,
                ).model_dump(),
            }
        )
    elif kind is ControlMirrorKind.ACCEPTED_DESIGN:
        candidate = type(base).model_validate(
            {**base.model_dump(), "accepted_design_artifacts": (artifact().model_dump(),)}
        )
    else:
        candidate = base

    expected = control_subject_digest(candidate, kind)
    assert expected is not None
    if kind is ControlMirrorKind.AUTHORITY_BASIS:
        content_digest = candidate.authority_refs[0].record_digest
    elif kind is ControlMirrorKind.ROLE_CONTRACT:
        content_digest = candidate.role_contract_ref.content_digest
    elif kind is ControlMirrorKind.POLICY_BASIS:
        content_digest = candidate.policy_basis_ref.policy_digest
    elif kind is ControlMirrorKind.GOVERNANCE_PROFILE:
        assert candidate.governance_profile_ref is not None
        content_digest = candidate.governance_profile_ref.content_digest
    elif kind is ControlMirrorKind.ACCEPTED_DESIGN:
        content_digest = candidate.accepted_design_artifacts[0].content_digest
    elif kind is ControlMirrorKind.SLICE_DEFINITION:
        content_digest = candidate.slice_definition_ref.content_digest
    else:
        content_digest = candidate.source_baseline_ref.content_digest

    if kind is ControlMirrorKind.ACCEPTED_DESIGN:
        source_artifact = candidate.accepted_design_artifacts[0]
    else:
        source_artifact = artifact().model_copy(update={"content_digest": content_digest})
    material = ArtifactMaterialRef(
        material_kind="RELAY_ARTIFACT",
        artifact=source_artifact,
        provenance_digest=D2,
    )
    current_manifest = manifest()
    entry = current_manifest.entries[0].model_copy(
        update={
            "source": ContextSourceRef(
                source_kind=ContextSourceKind.GOVERNANCE_RECORD,
                source_key="source-1",
                source_version="1",
                material_ref=material,
                locator="immutable control artifact",
            ),
            "control_mirror_binding": ControlMirrorBinding(
                mirror_kind=kind,
                control_subject_digest=expected,
            ),
        }
    )
    mirrored_manifest = type(current_manifest).model_validate(
        {**current_manifest.model_dump(), "entries": (entry.model_dump(),)}
    )
    mirrored_packet = type(candidate).model_validate(
        {
            **candidate.model_dump(),
            "context_manifest_ref": context_manifest_ref(mirrored_manifest).model_dump(),
        }
    )
    content, provenance = material_digests(material)
    fact = ContextMaterializationFact(
        evaluated_material_ref=material,
        material_status=RequirementStatus.SATISFIED,
        observed_content_digest=content,
        observed_provenance_digest=provenance,
    )
    assert (
        evaluate_context_conformance(mirrored_packet, mirrored_manifest, (fact,)).status
        is RequirementStatus.SATISFIED
    )

    bad_binding = ControlMirrorBinding(
        mirror_kind=kind,
        control_subject_digest=D2 if expected != D2 else D3,
    )
    wrong_entry = entry.model_copy(update={"control_mirror_binding": bad_binding})
    wrong_manifest = type(current_manifest).model_validate(
        {**current_manifest.model_dump(), "entries": (wrong_entry.model_dump(),)}
    )
    wrong_packet = type(candidate).model_validate(
        {
            **candidate.model_dump(),
            "context_manifest_ref": context_manifest_ref(wrong_manifest).model_dump(),
        }
    )
    wrong_result = evaluate_context_conformance(wrong_packet, wrong_manifest, (fact,))
    assert wrong_result.status is RequirementStatus.UNSATISFIED
    assert WorkPacketReason.CONTROL_MIRROR_CONFLICT in wrong_result.reasons


def test_unbound_supporting_context_does_not_claim_a_mirror() -> None:
    current_packet = packet()
    current_manifest = manifest()
    result = evaluate_context_conformance(
        current_packet,
        current_manifest,
        materialization_facts_for(current_packet, current_manifest),
    )
    assert result.status is RequirementStatus.SATISFIED
    assert all(entry.control_mirror_binding is None for entry in current_manifest.entries)
