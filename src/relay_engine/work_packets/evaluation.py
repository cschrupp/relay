"""Pure exact-subject and context conformance evaluation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable

from relay_engine.domain import ContentDigest
from relay_engine.domain._base import DomainModel
from relay_engine.role_contracts import (
    RequirementStatus,
    RoleContractApplicability,
)
from relay_engine.work_packets.models import (
    ArtifactMaterialRef,
    ContextConformance,
    ContextEntryRef,
    ContextManifest,
    ContextMaterializationFact,
    ContextMaterialRef,
    ControlMirrorKind,
    MaterialKind,
    ProtectedVerificationRequirement,
    ProtectedVerificationRequirementRef,
    RepositoryContentMaterialRef,
    WorkPacket,
    WorkPacketConformance,
    WorkPacketConformanceFacts,
    WorkPacketReason,
    context_manifest_ref,
    material_digests,
    protected_verification_requirement_ref,
    work_packet_ref,
)


def _subject_digest(kind: ControlMirrorKind, subject: DomainModel) -> ContentDigest:
    payload = {"control_kind": kind.value, "subject": subject.model_dump(mode="json")}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def control_subject_digests(
    packet: WorkPacket, kind: ControlMirrorKind
) -> tuple[ContentDigest, ...]:
    """Return digests for exact packet subjects eligible for a context mirror."""
    subjects: tuple[DomainModel, ...]
    if kind is ControlMirrorKind.AUTHORITY_BASIS:
        subjects = packet.authority_refs
    elif kind is ControlMirrorKind.ROLE_CONTRACT:
        subjects = (packet.role_contract_ref,)
    elif kind is ControlMirrorKind.POLICY_BASIS:
        subjects = (packet.policy_basis_ref,)
    elif kind is ControlMirrorKind.GOVERNANCE_PROFILE:
        subjects = () if packet.governance_profile_ref is None else (packet.governance_profile_ref,)
    elif kind is ControlMirrorKind.ACCEPTED_DESIGN:
        subjects = packet.accepted_design_artifacts
    elif kind is ControlMirrorKind.SLICE_DEFINITION:
        subjects = (packet.slice_definition_ref,)
    else:
        subjects = (packet.source_baseline_ref,)
    return tuple(_subject_digest(kind, subject) for subject in subjects)


def _control_subject_content_digests(
    packet: WorkPacket, kind: ControlMirrorKind
) -> tuple[tuple[ContentDigest, ContentDigest], ...]:
    if kind is ControlMirrorKind.AUTHORITY_BASIS:
        return tuple(
            (_subject_digest(kind, item), item.record_digest) for item in packet.authority_refs
        )
    if kind is ControlMirrorKind.ROLE_CONTRACT:
        subject = packet.role_contract_ref
        return ((_subject_digest(kind, subject), subject.content_digest),)
    if kind is ControlMirrorKind.POLICY_BASIS:
        subject = packet.policy_basis_ref
        return ((_subject_digest(kind, subject), subject.policy_digest),)
    if kind is ControlMirrorKind.GOVERNANCE_PROFILE:
        subject = packet.governance_profile_ref
        return (
            () if subject is None else ((_subject_digest(kind, subject), subject.content_digest),)
        )
    if kind is ControlMirrorKind.ACCEPTED_DESIGN:
        return tuple(
            (_subject_digest(kind, item), item.content_digest)
            for item in packet.accepted_design_artifacts
        )
    if kind is ControlMirrorKind.SLICE_DEFINITION:
        subject = packet.slice_definition_ref
        return ((_subject_digest(kind, subject), subject.content_digest),)
    subject = packet.source_baseline_ref
    return ((_subject_digest(kind, subject), subject.content_digest),)


def control_subject_digest(packet: WorkPacket, kind: ControlMirrorKind) -> ContentDigest | None:
    """Return a subject digest only when the packet contains exactly one candidate."""
    values = control_subject_digests(packet, kind)
    return values[0] if len(values) == 1 else None


def _reason_tuple(reasons: Iterable[WorkPacketReason]) -> tuple[WorkPacketReason, ...]:
    unique = set(reasons)
    return tuple(reason for reason in WorkPacketReason if reason in unique)


def _result(reasons: Iterable[WorkPacketReason], *, failed: bool = False) -> RequirementStatus:
    values = tuple(reasons)
    if failed:
        return RequirementStatus.UNSATISFIED
    if values:
        return RequirementStatus.INDETERMINATE
    return RequirementStatus.SATISFIED


def _ordered_subsequence_indices(
    actual: tuple[object, ...], expected: tuple[object, ...]
) -> tuple[int, ...] | None:
    """Locate actual subjects in expected order, allowing omitted evidence."""
    positions: list[int] = []
    expected_position = 0
    for subject in actual:
        while expected_position < len(expected) and expected[expected_position] != subject:
            expected_position += 1
        if expected_position == len(expected):
            return None
        positions.append(expected_position)
        expected_position += 1
    return tuple(positions)


def _material_matches_source_baseline(material: ContextMaterialRef, packet: WorkPacket) -> bool:
    if not isinstance(material, RepositoryContentMaterialRef):
        return True
    baseline_commit = packet.source_baseline_ref.commit
    return material.repository == baseline_commit.repository and material.commit == baseline_commit


def _source_is_exact_control_material(entry: ContextEntryRef, packet: WorkPacket) -> bool:
    material = entry.source.material_ref
    if not isinstance(material, ArtifactMaterialRef):
        return False
    artifact = material.artifact
    return any(artifact == accepted for accepted in packet.accepted_design_artifacts)


def _context_mirror_reasons(entry: ContextEntryRef, packet: WorkPacket) -> list[WorkPacketReason]:
    binding = entry.control_mirror_binding
    if binding is None:
        return []
    subjects = _control_subject_content_digests(packet, binding.mirror_kind)
    expected_content = next(
        (
            content_digest
            for subject_digest, content_digest in subjects
            if subject_digest == binding.control_subject_digest
        ),
        None,
    )
    if expected_content is None:
        return [WorkPacketReason.CONTROL_MIRROR_CONFLICT]
    observed_content, _ = material_digests(entry.source.material_ref)
    if observed_content != expected_content:
        return [WorkPacketReason.CONTROL_MIRROR_CONFLICT]
    if (
        binding.mirror_kind is ControlMirrorKind.ACCEPTED_DESIGN
        and not _source_is_exact_control_material(entry, packet)
    ):
        return [WorkPacketReason.CONTROL_MIRROR_CONFLICT]
    return []


def evaluate_context_conformance(
    packet: WorkPacket,
    manifest: ContextManifest,
    materialization_facts: tuple[ContextMaterializationFact, ...],
) -> ContextConformance:
    """Evaluate exact required context using only supplied immutable facts."""
    reasons: list[WorkPacketReason] = []
    failed = False
    missing_keys: list[str] = []

    try:
        actual_ref = context_manifest_ref(manifest)
    except TypeError, ValueError:
        actual_ref = None
        reasons.append(WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH)
        failed = True
    if (
        manifest.project_id != packet.project_id
        or manifest.slice_definition_ref != packet.slice_definition_ref
    ):
        reasons.append(WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH)
        failed = True
    if actual_ref != packet.context_manifest_ref:
        reasons.append(WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH)
        failed = True

    entries = {entry.entry_key: entry for entry in manifest.entries}
    required_entries: list[ContextEntryRef] = []
    for context_key in packet.required_context_keys:
        entry = entries.get(context_key)
        if entry is None:
            missing_keys.append(context_key)
            reasons.append(WorkPacketReason.REQUIRED_CONTEXT_MISSING)
            continue
        required_entries.append(entry)

    required_material_refs = tuple(entry.source.material_ref for entry in required_entries)
    actual_material_refs = tuple(fact.evaluated_material_ref for fact in materialization_facts)
    material_positions = _ordered_subsequence_indices(actual_material_refs, required_material_refs)
    if material_positions is None:
        reasons.append(WorkPacketReason.MATERIALIZATION_FACT_SET_MISMATCH)
        failed = True
        material_facts_by_position: dict[int, ContextMaterializationFact] = {}
    else:
        material_facts_by_position = dict(
            zip(material_positions, materialization_facts, strict=True)
        )

    for required_position, entry in enumerate(required_entries):
        material = entry.source.material_ref
        if not _material_matches_source_baseline(material, packet):
            reasons.append(WorkPacketReason.CONTEXT_MATERIAL_CONTENT_MISMATCH)
            failed = True
        mirror_reasons = _context_mirror_reasons(entry, packet)
        reasons.extend(mirror_reasons)
        if mirror_reasons:
            failed = True
        fact = material_facts_by_position.get(required_position)
        if fact is None:
            if material.material_kind == MaterialKind.CAPTURED_MATERIAL.value:
                reasons.append(WorkPacketReason.CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED)
            else:
                reasons.append(WorkPacketReason.CONTEXT_MATERIAL_UNAVAILABLE)
            continue
        if fact.evaluated_material_ref != material:
            reasons.append(WorkPacketReason.MATERIALIZATION_FACT_SET_MISMATCH)
            failed = True
            continue
        expected_content, expected_provenance = material_digests(material)
        if (
            fact.observed_content_digest is not None
            and fact.observed_content_digest != expected_content
        ):
            reasons.append(WorkPacketReason.CONTEXT_MATERIAL_CONTENT_MISMATCH)
            failed = True
        if (
            fact.observed_provenance_digest is not None
            and fact.observed_provenance_digest != expected_provenance
        ):
            reasons.append(WorkPacketReason.CONTEXT_MATERIAL_PROVENANCE_MISMATCH)
            failed = True
        if fact.material_status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkPacketReason.REQUIRED_CONTEXT_INVALID)
            failed = True
        elif fact.material_status is RequirementStatus.INDETERMINATE:
            if material.material_kind == MaterialKind.CAPTURED_MATERIAL.value:
                reasons.append(WorkPacketReason.CONTEXT_MATERIAL_RESOLVER_UNSUPPORTED)
            else:
                reasons.append(WorkPacketReason.CONTEXT_MATERIAL_UNAVAILABLE)
        elif (fact.observed_content_digest, fact.observed_provenance_digest) != (
            expected_content,
            expected_provenance,
        ):
            reasons.append(WorkPacketReason.CONTEXT_MATERIAL_UNAVAILABLE)

    status = _result(reasons, failed=failed)
    return ContextConformance(
        status=status,
        reasons=_reason_tuple(reasons),
        missing_context_keys=tuple(sorted(set(missing_keys))),
    )


def _status_reasons(
    status: RequirementStatus,
    stale_reason: WorkPacketReason,
    conflict_reason: WorkPacketReason,
) -> tuple[list[WorkPacketReason], bool]:
    if status is RequirementStatus.SATISFIED:
        return [], False
    if status is RequirementStatus.UNSATISFIED:
        return [conflict_reason], True
    return [stale_reason], False


def _protected_fact_ref(
    requirement: ProtectedVerificationRequirement,
) -> ProtectedVerificationRequirementRef:
    return protected_verification_requirement_ref(requirement)


def evaluate_work_packet_conformance(
    packet: WorkPacket,
    manifest: ContextManifest,
    facts: WorkPacketConformanceFacts,
) -> WorkPacketConformance:
    """Aggregate exact-subject facts without issuing authority or action decisions."""
    reasons: list[WorkPacketReason] = []
    failed = False

    packet_ref = work_packet_ref(packet)
    manifest_ref = context_manifest_ref(manifest)
    if facts.evaluated_work_packet_ref != packet_ref:
        reasons.append(WorkPacketReason.WORK_PACKET_REF_MISMATCH)
        failed = True
    if (
        facts.evaluated_context_manifest_ref != manifest_ref
        or manifest_ref != packet.context_manifest_ref
    ):
        reasons.append(WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH)
        failed = True
    if facts.slice_definition_fact.evaluated_ref != packet.slice_definition_ref:
        reasons.append(WorkPacketReason.SLICE_DEFINITION_FACT_SUBJECT_MISMATCH)
        failed = True
    if facts.source_baseline_fact.evaluated_ref != packet.source_baseline_ref:
        reasons.append(WorkPacketReason.SOURCE_BASELINE_FACT_SUBJECT_MISMATCH)
        failed = True
    if facts.policy_basis_fact.evaluated_ref != packet.policy_basis_ref:
        reasons.append(WorkPacketReason.POLICY_FACT_SUBJECT_MISMATCH)
        failed = True
    if (
        facts.governance_profile_fact.evaluated_policy_basis_ref != packet.policy_basis_ref
        or facts.governance_profile_fact.evaluated_profile_ref != packet.governance_profile_ref
    ):
        reasons.append(WorkPacketReason.GOVERNANCE_PROFILE_FACT_SUBJECT_MISMATCH)
        failed = True
    if facts.role_contract_applicability.role_contract_ref != packet.role_contract_ref:
        reasons.append(WorkPacketReason.ROLE_APPLICABILITY_SUBJECT_MISMATCH)
        failed = True

    authority_refs = tuple(fact.evaluated_ref for fact in facts.authority_facts)
    authority_positions = _ordered_subsequence_indices(authority_refs, packet.authority_refs)
    if authority_positions is None:
        reasons.append(WorkPacketReason.AUTHORITY_FACT_SET_MISMATCH)
        failed = True
    elif len(authority_refs) < len(packet.authority_refs):
        reasons.append(WorkPacketReason.AUTHORITY_BASIS_MISSING)
    accepted_artifacts = tuple(fact.evaluated_artifact for fact in facts.accepted_design_facts)
    accepted_positions = _ordered_subsequence_indices(
        accepted_artifacts, packet.accepted_design_artifacts
    )
    if accepted_positions is None:
        reasons.append(WorkPacketReason.ACCEPTED_DESIGN_FACT_SET_MISMATCH)
        failed = True
    elif len(accepted_artifacts) < len(packet.accepted_design_artifacts):
        reasons.append(WorkPacketReason.ACCEPTED_DESIGN_BASIS_MISSING)
    if facts.context_manifest_fact.evaluated_ref != packet.context_manifest_ref:
        reasons.append(WorkPacketReason.CONTEXT_MANIFEST_FACT_SUBJECT_MISMATCH)
        failed = True
    requirements_requiring_authority = tuple(
        requirement
        for requirement in packet.protected_verification_requirements
        if requirement.separate_authority_ref is not None
    )
    protected_refs = tuple(
        fact.evaluated_requirement_ref for fact in facts.protected_verification_authority_facts
    )
    expected_protected_refs = tuple(
        _protected_fact_ref(requirement) for requirement in requirements_requiring_authority
    )
    protected_positions = _ordered_subsequence_indices(protected_refs, expected_protected_refs)
    if protected_positions is None:
        reasons.append(WorkPacketReason.PROTECTED_VERIFICATION_FACT_SET_MISMATCH)
        failed = True
    elif len(protected_refs) < len(expected_protected_refs):
        reasons.append(WorkPacketReason.PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE)

    status_checks = (
        _status_reasons(
            facts.slice_definition_fact.status,
            WorkPacketReason.SLICE_DEFINITION_STALE,
            WorkPacketReason.SLICE_DEFINITION_CONFLICT,
        ),
        _status_reasons(
            facts.source_baseline_fact.status,
            WorkPacketReason.SOURCE_BASELINE_STALE,
            WorkPacketReason.SOURCE_BASELINE_CONFLICT,
        ),
        _status_reasons(
            facts.policy_basis_fact.status,
            WorkPacketReason.POLICY_BASIS_STALE,
            WorkPacketReason.POLICY_BASIS_CONFLICT,
        ),
        _status_reasons(
            facts.context_manifest_fact.status,
            WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH,
            WorkPacketReason.CONTEXT_MANIFEST_REF_MISMATCH,
        ),
    )
    for additions, is_failure in status_checks:
        reasons.extend(additions)
        failed = failed or is_failure

    if authority_positions is not None:
        for fact in facts.authority_facts:
            additions, is_failure = _status_reasons(
                fact.status,
                WorkPacketReason.AUTHORITY_BASIS_STALE,
                WorkPacketReason.AUTHORITY_BASIS_CONFLICT,
            )
            reasons.extend(additions)
            failed = failed or is_failure
    elif not any(reason is WorkPacketReason.AUTHORITY_FACT_SET_MISMATCH for reason in reasons):
        reasons.append(WorkPacketReason.AUTHORITY_BASIS_MISSING)

    profile_fact = facts.governance_profile_fact
    if profile_fact.profile_requirement_status is RequirementStatus.UNSATISFIED:
        reasons.append(WorkPacketReason.GOVERNANCE_PROFILE_REQUIRED)
        failed = True
    elif profile_fact.profile_requirement_status is RequirementStatus.INDETERMINATE:
        reasons.append(WorkPacketReason.GOVERNANCE_PROFILE_STALE)
    if packet.governance_profile_ref is not None:
        if profile_fact.profile_status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkPacketReason.GOVERNANCE_PROFILE_CONFLICT)
            failed = True
        elif profile_fact.profile_status is RequirementStatus.INDETERMINATE:
            reasons.append(WorkPacketReason.GOVERNANCE_PROFILE_STALE)

    if facts.role_contract_applicability.status is RoleContractApplicability.NOT_APPLICABLE:
        reasons.append(WorkPacketReason.ROLE_CONTRACT_NOT_APPLICABLE)
        failed = True
    elif facts.role_contract_applicability.status is RoleContractApplicability.INDETERMINATE:
        reasons.append(WorkPacketReason.ROLE_CONTRACT_APPLICABILITY_UNKNOWN)

    for fact in facts.accepted_design_facts if accepted_positions is not None else ():
        if fact.status is RequirementStatus.UNSATISFIED:
            reasons.append(WorkPacketReason.ACCEPTED_DESIGN_BASIS_MISSING)
            failed = True
        elif fact.status is RequirementStatus.INDETERMINATE:
            reasons.append(WorkPacketReason.ACCEPTED_DESIGN_BASIS_STALE)

    if protected_positions is not None:
        for fact, requirement_position in zip(
            facts.protected_verification_authority_facts,
            protected_positions,
            strict=True,
        ):
            requirement = requirements_requiring_authority[requirement_position]
            if fact.evaluated_authority_ref != requirement.separate_authority_ref:
                reasons.append(WorkPacketReason.PROTECTED_VERIFICATION_FACT_SET_MISMATCH)
                failed = True
            if requirement.separate_authority_ref is not None:
                if fact.status is RequirementStatus.UNSATISFIED:
                    reasons.append(WorkPacketReason.PROTECTED_VERIFICATION_AUTHORITY_REQUIRED)
                    failed = True
                elif fact.status is RequirementStatus.INDETERMINATE:
                    reasons.append(WorkPacketReason.PROTECTED_VERIFICATION_AUTHORITY_INDETERMINATE)

    context = evaluate_context_conformance(packet, manifest, facts.materialization_facts)
    reasons.extend(context.reasons)
    if context.status is RequirementStatus.UNSATISFIED:
        failed = True

    if packet.normalized_intent.status.value != "COMPLETE":
        reasons.append(WorkPacketReason.NORMALIZED_INTENT_INCOMPLETE)
        failed = True
    if failed:
        status = RequirementStatus.UNSATISFIED
    elif reasons:
        status = RequirementStatus.INDETERMINATE
    else:
        status = RequirementStatus.SATISFIED
    return WorkPacketConformance(status=status, reasons=_reason_tuple(reasons))
