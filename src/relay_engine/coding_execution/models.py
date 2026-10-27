"""Immutable Slice 3.1 execution bindings and terminal evidence."""

from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime import (
    RuntimeControlAck,
    RuntimeDescriptor,
    RuntimeEventEnvelope,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimePermissionProfileRef,
    RuntimeSessionBinding,
    RuntimeSessionRef,
    RuntimeWorkspaceAttachment,
)
from relay_engine.agent_runtime.boundary import (
    RuntimeEvidenceCompleteness,
    RuntimePermissionAttestation,
    RuntimePermissionAttestationRef,
    RuntimeRequestV2,
)
from relay_engine.domain import ActorRef, ContentDigest, ExecutionId, ProjectId, SliceId
from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.execution_workspace.boundary import (
    RuntimePlacementAttestation,
    RuntimePlacementContinuityEvidence,
    RuntimeProcessTeardownEvidence,
    WorkspaceBoundaryRef,
    placement_attestation_matches_boundary,
)
from relay_engine.execution_workspace.models import (
    WorkspaceChangeManifest,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePlanRef,
    WorkspaceProviderRef,
)
from relay_engine.project_state import ConsumableRef
from relay_engine.role_contracts import RequirementStatus, RoleContractRef
from relay_engine.work_packets import ContextManifestRef, WorkPacket, WorkPacketRef

type StableExecutionKey = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=128),
    Field(pattern=r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$"),
]
type CorrectionScopeEntry = Annotated[
    str,
    StringConstraints(strict=True, min_length=1, max_length=2048),
    AfterValidator(require_nonblank),
]


class AdmissionStatus(StrEnum):
    """Non-lifecycle decision for one final runtime admission check."""

    ADMIT = "ADMIT"
    DENY = "DENY"
    INDETERMINATE = "INDETERMINATE"


class ExecutionTerminalOutcome(StrEnum):
    """Relay-owned terminal result vocabulary for a governed execution."""

    DONE = "DONE"
    BLOCKED_BY_AUTHORITY = "BLOCKED_BY_AUTHORITY"
    BLOCKED_BY_CONTRACT = "BLOCKED_BY_CONTRACT"
    BLOCKED_BY_ENVIRONMENT = "BLOCKED_BY_ENVIRONMENT"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    BACKLOG_EXHAUSTED = "BACKLOG_EXHAUSTED"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"


class HumanGrantBinding(DomainModel):
    """Read-only exact grant projection; it cannot issue or mutate authority."""

    grant_record_id: StableExecutionKey
    grant_record_digest: ContentDigest
    authority_candidate_digest: ContentDigest
    intended_attempt_id: StableExecutionKey
    project_id: ProjectId
    slice_id: SliceId
    valid: bool
    applicable: bool


class ConsumableReservationBinding(DomainModel):
    """Read-only proof of one grant-time reservation."""

    consumable_key: StableExecutionKey
    scope_key: StableExecutionKey
    grant_record_digest: ContentDigest
    authority_candidate_digest: ContentDigest
    intended_attempt_id: StableExecutionKey
    evidence_id: StableExecutionKey
    evidence_digest: ContentDigest
    state: str
    created_atomically_at_grant: bool


class EvaluatorReworkBinding(DomainModel):
    """Read-only exact independent-evaluation REWORK record projection."""

    evaluation_record_id: StableExecutionKey
    registered_record_digest: ContentDigest | None
    projection_digest: ContentDigest
    evaluator_identity: StableExecutionKey | None
    source_role: Literal["INDEPENDENT_EVALUATION"] | None
    provenance_status: RequirementStatus | None
    outcome: Literal["REWORK"]
    reviewed_candidate_digest: ContentDigest
    reviewed_handoff_digest: ContentDigest
    finding_ids: tuple[StableExecutionKey, ...] = ()
    permitted_correction_scope: tuple[CorrectionScopeEntry, ...] = ()

    @field_validator("finding_ids")
    @classmethod
    def finding_ids_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("evaluator finding IDs must be unique and sorted")
        return value

    @field_validator("permitted_correction_scope")
    @classmethod
    def correction_scope_is_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value), key=lambda item: item.encode("utf-8"))):
            raise ValueError("evaluator correction scope must be unique and UTF-8 sorted")
        return value


class PriorExecutionBinding(DomainModel):
    """Exact prior terminal identity and authority scope used for REWORK checks."""

    authority_candidate_digest: ContentDigest
    terminal_candidate_digest: ContentDigest | None
    terminal_result_digest: ContentDigest
    handoff_digest: ContentDigest
    intended_attempt_id: StableExecutionKey
    execution_id: ExecutionId
    project_id: ProjectId
    slice_id: SliceId
    work_packet_ref: WorkPacketRef
    authority_scope: tuple[CorrectionScopeEntry, ...]
    authority_out_of_scope: tuple[CorrectionScopeEntry, ...]

    @field_validator("authority_scope", "authority_out_of_scope")
    @classmethod
    def authority_scopes_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value), key=lambda item: item.encode("utf-8"))):
            raise ValueError("prior authority scopes must be unique and UTF-8 sorted")
        return value

    @model_validator(mode="after")
    def attempt_identity_is_exact(self) -> PriorExecutionBinding:
        if execution_id_for_attempt(self.intended_attempt_id) != self.execution_id:
            raise ValueError("prior attempt and ExecutionId must be an exact pair")
        return self


class CorrectiveSubjectBinding(DomainModel):
    """Immutable lineage and fresh-authority binding for an in-scope correction."""

    prior_authority_candidate_digest: ContentDigest
    prior_terminal_candidate_digest: ContentDigest
    prior_terminal_result_digest: ContentDigest
    prior_handoff_digest: ContentDigest
    prior_work_packet_ref: WorkPacketRef
    evaluation_record_id: StableExecutionKey
    evaluation_record_digest: ContentDigest
    finding_ids: tuple[StableExecutionKey, ...]
    correction_scope: tuple[CorrectionScopeEntry, ...]
    corrective_candidate_digest: ContentDigest
    intended_attempt_id: StableExecutionKey
    execution_id: ExecutionId
    grant: HumanGrantBinding
    reservations: tuple[ConsumableReservationBinding, ...]
    required_reservation_keys: tuple[ConsumableRef, ...]

    @field_validator("finding_ids")
    @classmethod
    def keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("corrective binding keys must be unique and sorted")
        return value

    @field_validator("required_reservation_keys")
    @classmethod
    def required_reservations_are_canonical(
        cls, value: tuple[ConsumableRef, ...]
    ) -> tuple[ConsumableRef, ...]:
        keys = tuple((item.consumable_key, item.scope_key) for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError(
                "required reservation refs must be unique and sorted by consumable and scope"
            )
        return value

    @field_validator("correction_scope")
    @classmethod
    def correction_scope_is_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value), key=lambda item: item.encode("utf-8"))):
            raise ValueError("correction scope must be unique and UTF-8 sorted")
        return value

    @field_validator("reservations")
    @classmethod
    def reservations_are_canonical(
        cls, value: tuple[ConsumableReservationBinding, ...]
    ) -> tuple[ConsumableReservationBinding, ...]:
        keys = tuple((item.consumable_key, item.scope_key) for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError(
                "corrective reservations must be unique and sorted by consumable and scope"
            )
        return value

    @model_validator(mode="after")
    def exact_fresh_attempt_authority(self) -> CorrectiveSubjectBinding:
        if self.corrective_candidate_digest == self.prior_authority_candidate_digest:
            raise ValueError("corrective authority candidate must be new")
        if execution_id_for_attempt(self.intended_attempt_id) != self.execution_id:
            raise ValueError("corrective attempt and ExecutionId must be an exact pair")
        if self.intended_attempt_id != self.grant.intended_attempt_id:
            raise ValueError("grant must bind the corrective attempt")
        if (
            self.grant.authority_candidate_digest != self.corrective_candidate_digest
            or self.grant.intended_attempt_id != self.intended_attempt_id
            or not self.grant.valid
            or not self.grant.applicable
        ):
            raise ValueError("corrective grant must be valid for the exact new candidate/attempt")
        if any(
            item.grant_record_digest != self.grant.grant_record_digest
            or item.authority_candidate_digest != self.corrective_candidate_digest
            or item.intended_attempt_id != self.intended_attempt_id
            or item.state != "RESERVED"
            or not item.created_atomically_at_grant
            for item in self.reservations
        ):
            raise ValueError("corrective reservations must be exact grant-time evidence")
        reservation_refs = tuple(
            ConsumableRef(consumable_key=item.consumable_key, scope_key=item.scope_key)
            for item in self.reservations
        )
        if reservation_refs != self.required_reservation_keys:
            raise ValueError("corrective reservations must exactly match required consumables")
        if not self.finding_ids:
            raise ValueError("corrective subject must bind at least one evaluator finding")
        return self


class ReworkDisposition(StrEnum):
    """Pure classification of one independently evaluated corrective request."""

    IN_SCOPE_REWORK = "IN_SCOPE_REWORK"
    NEW_AUTHORITY_REQUIRED = "NEW_AUTHORITY_REQUIRED"
    INDETERMINATE = "INDETERMINATE"


class EvaluatorReworkEvaluation(DomainModel):
    """Decision result only; it grants no authority and performs no mutation."""

    disposition: ReworkDisposition
    reasons: tuple[str, ...]
    corrective_subject: CorrectiveSubjectBinding | None = None

    @field_validator("reasons")
    @classmethod
    def reasons_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("rework evaluation reasons must be unique and sorted")
        return value

    @model_validator(mode="after")
    def subject_matches_disposition(self) -> EvaluatorReworkEvaluation:
        if (self.disposition is ReworkDisposition.IN_SCOPE_REWORK) != (
            self.corrective_subject is not None
        ):
            raise ValueError("only in-scope REWORK may carry a corrective subject")
        return self


class RuntimePayloadEvidence(DomainModel):
    """Evidence binding the exact prompt payload to permitted packet context."""

    work_packet_ref: WorkPacketRef
    context_manifest_ref: ContextManifestRef
    payload_digest: ContentDigest
    included_context_keys: tuple[StableExecutionKey, ...]
    status: RequirementStatus
    protected_content_exposed: bool | None
    evaluator_only_content_exposed: bool | None
    credential_exposure_status: str
    evidence_digest: ContentDigest

    @field_validator("included_context_keys")
    @classmethod
    def context_keys_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("included context keys must be unique and sorted")
        return value

    @model_validator(mode="after")
    def satisfied_payload_has_clean_exposure(self) -> RuntimePayloadEvidence:
        if self.status is RequirementStatus.SATISFIED and (
            self.protected_content_exposed is not False
            or self.evaluator_only_content_exposed is not False
            or self.credential_exposure_status not in {"CLEAR", "NOT_APPLICABLE"}
        ):
            raise ValueError("satisfied payload evidence requires proven non-exposure")
        return self


class RuntimePermissionEvidence(DomainModel):
    """Effective runtime exposure attestation bound to one governed request."""

    execution_id: ExecutionId
    runtime_id: str
    attestation_id: StableExecutionKey
    evidence_digest: ContentDigest
    effective_profile_ref: RuntimePermissionProfileRef | None
    completeness: RequirementStatus
    exposed_tools: tuple[StableExecutionKey, ...] | None = None
    unknown_tool_identity: bool = False
    shell_exposed: bool | None = None
    actual_provider_id: str | None = None
    actual_model_id: str | None = None
    provenance_status: RequirementStatus

    @field_validator("exposed_tools")
    @classmethod
    def exposed_tools_are_canonical(cls, value: tuple[str, ...] | None) -> tuple[str, ...] | None:
        if value is not None and value != tuple(sorted(set(value))):
            raise ValueError("exposed tool identities must be unique and sorted")
        return value


class ExecutionSubject(DomainModel):
    """Canonical immutable identity envelope for one exact governed attempt."""

    project_id: ProjectId
    slice_id: SliceId
    candidate_digest: ContentDigest
    human_grant: HumanGrantBinding
    intended_attempt_id: StableExecutionKey
    execution_id: ExecutionId
    work_packet: WorkPacket
    work_packet_ref: WorkPacketRef
    context_manifest_ref: ContextManifestRef
    role_contract_ref: RoleContractRef
    actor: ActorRef
    workspace_plan_ref: WorkspacePlanRef
    workspace_instance: WorkspaceInstanceRef
    runtime_workspace_attachment: RuntimeWorkspaceAttachment
    workspace_provider_ref: WorkspaceProviderRef
    runtime_descriptor: RuntimeDescriptor
    runtime_request: RuntimeExecutionRequest
    runtime_request_v2: RuntimeRequestV2 | None = None
    workspace_boundary_ref: WorkspaceBoundaryRef | None = None
    runtime_placement_attestation: RuntimePlacementAttestation | None = None
    runtime_permission_attestation: RuntimePermissionAttestation | None = None
    runtime_permission_attestation_ref: RuntimePermissionAttestationRef | None = None
    runtime_session_binding: RuntimeSessionBinding | None = None
    runtime_payload_evidence: RuntimePayloadEvidence
    runtime_permission_evidence: RuntimePermissionEvidence
    corrective_subject_binding: CorrectiveSubjectBinding | None = None
    actual_provider_id: str | None = None
    actual_model_id: str | None = None
    runtime_session: RuntimeSessionRef | None = None
    runtime_handle: RuntimeExecutionHandle | None = None
    reservations: tuple[ConsumableReservationBinding, ...] = ()
    control_references: tuple[StableExecutionKey, ...] = ()
    resource_references: tuple[StableExecutionKey, ...] = ()
    result_contract_version: StableExecutionKey = "slice-3-1-v1"

    @field_validator("reservations")
    @classmethod
    def reservations_are_canonical(
        cls, value: tuple[ConsumableReservationBinding, ...]
    ) -> tuple[ConsumableReservationBinding, ...]:
        keys = tuple((item.consumable_key, item.scope_key) for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("reservations must be unique and sorted by consumable and scope key")
        return value

    @field_validator("control_references", "resource_references")
    @classmethod
    def references_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("references must be unique and sorted")
        return value

    @model_validator(mode="after")
    def subject_bindings_are_exact(self) -> ExecutionSubject:
        if self.human_grant.authority_candidate_digest != self.candidate_digest:
            raise ValueError("grant must bind the exact AuthorityCandidate digest")
        if self.human_grant.intended_attempt_id != self.intended_attempt_id:
            raise ValueError("grant must bind the exact intended attempt")
        if any(
            reservation.grant_record_digest != self.human_grant.grant_record_digest
            or reservation.authority_candidate_digest != self.candidate_digest
            or reservation.intended_attempt_id != self.intended_attempt_id
            or not reservation.created_atomically_at_grant
            or reservation.state != "RESERVED"
            for reservation in self.reservations
        ):
            raise ValueError("reservation must be exact grant-time evidence for this attempt")
        if self.runtime_request.basis.execution_id != self.execution_id:
            raise ValueError("runtime request must use the exact subject ExecutionId")
        boundary_values = (
            self.runtime_request_v2,
            self.workspace_boundary_ref,
            self.runtime_placement_attestation,
            self.runtime_permission_attestation,
            self.runtime_permission_attestation_ref,
            self.runtime_session_binding,
        )
        if self.runtime_request_v2 is None:
            if any(value is not None for value in boundary_values[1:]):
                raise ValueError("boundary evidence requires an exact V2 runtime request")
        else:
            request_v2 = self.runtime_request_v2
            placement = self.runtime_placement_attestation
            permission_attestation = self.runtime_permission_attestation
            if (
                self.runtime_session is None
                or self.runtime_session_binding is None
                or (
                    request_v2.request != self.runtime_request
                    or request_v2.request_digest_v2
                    != self.runtime_session_binding.request_digest_v2
                )
            ):
                raise ValueError("V2 request and session must bind one exact request digest")
            if (
                self.workspace_boundary_ref is None
                or placement is None
                or permission_attestation is None
                or self.runtime_permission_attestation_ref is None
            ):
                raise ValueError("strong-boundary subject requires complete boundary evidence")
            if (
                request_v2.workspace_boundary_digest != self.workspace_boundary_ref.content_digest
                or request_v2.launch_subject.execution_id != self.execution_id
                or request_v2.launch_subject.intended_attempt_id != self.intended_attempt_id
                or request_v2.launch_subject.authority_candidate_digest != self.candidate_digest
                or request_v2.launch_subject.human_grant_digest
                != self.human_grant.grant_record_digest
                or request_v2.launch_subject.work_packet_ref_digest
                != _digest_canonical_model(self.work_packet_ref)
                or request_v2.launch_subject.context_manifest_ref_digest
                != _digest_canonical_model(self.context_manifest_ref)
                or request_v2.launch_subject.workspace_plan_ref_digest
                != _digest_canonical_model(self.workspace_plan_ref)
                or request_v2.launch_subject.workspace_instance_digest
                != _digest_canonical_model(self.workspace_instance)
                or request_v2.launch_subject.runtime_descriptor_digest
                != _digest_canonical_model(self.runtime_descriptor)
                or request_v2.launch_subject.runtime_id != self.runtime_descriptor.runtime_id
                or request_v2.launch_subject.runtime_version
                != self.runtime_descriptor.runtime_version
                or request_v2.launch_subject.adapter_version
                != self.runtime_descriptor.adapter_version
                or request_v2.launch_subject.runtime_api_generation
                != self.runtime_descriptor.api_generation
                or request_v2.launch_subject.executable_identity
                != (
                    f"{self.runtime_descriptor.runtime_id}@"
                    f"{self.runtime_descriptor.runtime_version}#"
                    f"{self.runtime_descriptor.executable_digest}"
                )
                or request_v2.launch_subject.runtime_configuration_digest
                != self.runtime_descriptor.configuration_digest
                or request_v2.launch_subject.requested_provider_id
                != self.runtime_request.basis.runtime_selection.requested_provider_id
                or request_v2.launch_subject.requested_model_id
                != self.runtime_request.basis.runtime_selection.requested_model_id
                or request_v2.launch_subject.permission_profile_ref
                != self.runtime_request.basis.permission_profile_ref
                or request_v2.launch_subject.credential_reference_ids
                != tuple(
                    sorted(
                        item.credential_id for item in self.runtime_request.basis.credential_refs
                    )
                )
                or request_v2.launch_subject.runtime_request_payload_digest
                != self.runtime_request.basis.input_payload.payload_digest
                or request_v2.launch_subject.runtime_limits_digest
                != _digest_canonical_model(self.runtime_request.basis.limits)
                or self.workspace_boundary_ref.plan_ref != self.workspace_plan_ref
                or self.workspace_boundary_ref.instance_ref != self.workspace_instance
                or self.workspace_boundary_ref.provider_ref != self.workspace_provider_ref
                or request_v2.endpoint_identity != placement.endpoint_identity
                or not placement_attestation_matches_boundary(
                    self.workspace_boundary_ref,
                    placement,
                    launch_subject_digest=request_v2.launch_subject.content_digest,
                    runtime_descriptor_digest=_digest_canonical_model(self.runtime_descriptor),
                    launch_nonce=request_v2.launch_subject.challenge_or_launch_nonce,
                )
                or placement.ref != request_v2.placement_attestation_ref
                or permission_attestation.ref != self.runtime_permission_attestation_ref
                or permission_attestation.session_binding != self.runtime_session_binding
                or self.runtime_session_binding.runtime_session != self.runtime_session
                or permission_attestation.request_digest_v2 != request_v2.request_digest_v2
                or permission_attestation.expected_permission_profile_ref
                != self.runtime_request.basis.permission_profile_ref
                or permission_attestation.completeness is not RuntimeEvidenceCompleteness.SATISFIED
                or permission_attestation.observed_effective_profile_digest
                != self.runtime_request.basis.permission_profile_ref.content_digest
                or permission_attestation.actual_provider_id
                != self.runtime_request.basis.runtime_selection.requested_provider_id
                or permission_attestation.actual_model_id
                != self.runtime_request.basis.runtime_selection.requested_model_id
            ):
                raise ValueError("subject must bind the exact placement and permission evidence")
        if self.corrective_subject_binding is not None:
            correction = self.corrective_subject_binding
            if (
                correction.corrective_candidate_digest != self.candidate_digest
                or correction.intended_attempt_id != self.intended_attempt_id
                or correction.execution_id != self.execution_id
                or correction.grant != self.human_grant
                or correction.reservations != self.reservations
                or not set(self.work_packet.normalized_intent.scope.in_scope).issubset(
                    set(correction.correction_scope)
                )
            ):
                raise ValueError(
                    "corrective execution subject must preserve exact lineage, authority, and scope"
                )
        if self.runtime_session is not None and self.runtime_session.runtime_id != (
            self.runtime_descriptor.runtime_id
        ):
            raise ValueError("runtime session identity must match exact descriptor")
        if (
            self.runtime_handle is not None
            and self.runtime_session is not None
            and self.runtime_handle.runtime_session != self.runtime_session
        ):
            raise ValueError("runtime handle must bind exact session")
        if self.runtime_request.basis.workspace != self.runtime_workspace_attachment:
            raise ValueError("runtime request must use the exact workspace attachment")
        if self.runtime_payload_evidence.payload_digest != (
            self.runtime_request.basis.input_payload.payload_digest
        ):
            raise ValueError("payload evidence must bind exact runtime input digest")
        if self.runtime_payload_evidence.work_packet_ref != self.work_packet_ref:
            raise ValueError("payload evidence must bind exact WorkPacketRef")
        if self.runtime_payload_evidence.context_manifest_ref != self.context_manifest_ref:
            raise ValueError("payload evidence must bind exact ContextManifestRef")
        permission = self.runtime_permission_evidence
        selection = self.runtime_request.basis.runtime_selection
        if (
            permission.execution_id != self.execution_id
            or permission.runtime_id != self.runtime_descriptor.runtime_id
            or permission.effective_profile_ref != self.runtime_request.basis.permission_profile_ref
            or permission.actual_provider_id != selection.requested_provider_id
            or permission.actual_model_id != selection.requested_model_id
            or self.actual_provider_id != permission.actual_provider_id
            or self.actual_model_id != permission.actual_model_id
            or permission.completeness is not RequirementStatus.SATISFIED
            or permission.provenance_status is not RequirementStatus.SATISFIED
        ):
            raise ValueError("subject must bind complete effective runtime permission evidence")
        if self.work_packet_ref != self.workspace_plan_ref.work_packet_ref:
            raise ValueError("workspace plan must derive from exact WorkPacketRef")
        if self.workspace_instance.plan_ref != self.workspace_plan_ref:
            raise ValueError("workspace instance must bind exact plan")
        if self.runtime_workspace_attachment.workspace_id != self.workspace_instance.workspace_id:
            raise ValueError("runtime attachment must bind exact workspace instance")
        if self.work_packet.project_id != self.project_id:
            raise ValueError("packet project must match subject project")
        if self.runtime_request.basis.slice_id != self.slice_id:
            raise ValueError("runtime request slice must match subject slice")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        """Return SHA-256 of canonical schema-v1 JSON for the complete subject."""

        data = json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(data).hexdigest()


class AdmissionEvidence(DomainModel):
    """The exact checks and reasons supporting a fail-closed admission result."""

    status: AdmissionStatus
    reasons: tuple[str, ...] = ()
    checked_candidate_digest: ContentDigest | None = None
    checked_attempt_id: StableExecutionKey | None = None

    @field_validator("reasons")
    @classmethod
    def reasons_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("admission reasons must be unique and sorted")
        return value


class ProposedWorkObservation(DomainModel):
    """Non-authoritative evidence describing work outside the exact packet."""

    source_execution_id: ExecutionId
    summary: str
    rationale: str
    evidence_refs: tuple[StableExecutionKey, ...] = ()
    proposal_digest: ContentDigest
    applicable_hard_stop_key: StableExecutionKey

    @field_validator("summary", "rationale")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @field_validator("evidence_refs")
    @classmethod
    def refs_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("evidence refs must be unique and sorted")
        return value


class InternalProgressObservation(DomainModel):
    """Non-authoritative internal milestone evidence inside one WorkPacket."""

    execution_id: ExecutionId
    milestone_key: StableExecutionKey
    status: str
    evidence_digest: ContentDigest


class ContractGapAnalysis(DomainModel):
    """Exact predecessor contract gap; recording it does not authorize a change."""

    owning_slice: StableExecutionKey
    contract_reference: StableExecutionKey
    required_behavior: str
    failing_scenario: str
    missing_contract_element: str
    composition_failure: str
    minimum_amendment: str
    security_consequences: str
    analysis_digest: ContentDigest


class ExecutionEvidenceBundle(DomainModel):
    """Relay-owned evidence bundle; runtime success alone cannot establish DONE."""

    execution_subject_digest: ContentDigest
    grant: HumanGrantBinding
    reservations: tuple[ConsumableReservationBinding, ...]
    runtime_request: RuntimeExecutionRequest
    runtime_request_v2: RuntimeRequestV2 | None = None
    workspace_boundary_ref: WorkspaceBoundaryRef | None = None
    runtime_placement_attestation: RuntimePlacementAttestation | None = None
    runtime_placement_continuity: RuntimePlacementContinuityEvidence | None = None
    runtime_process_teardown: RuntimeProcessTeardownEvidence | None = None
    runtime_permission_attestation: RuntimePermissionAttestation | None = None
    runtime_permission_attestation_ref: RuntimePermissionAttestationRef | None = None
    runtime_payload_evidence: RuntimePayloadEvidence
    runtime_permission_evidence: RuntimePermissionEvidence
    runtime_session: RuntimeSessionBinding | None
    runtime_handle: RuntimeExecutionHandle | None
    runtime_inspection: RuntimeExecutionInspection | None
    runtime_events: tuple[RuntimeEventEnvelope, ...] = ()
    runtime_event_reasons: tuple[str, ...] = ()
    cancellation_ack: RuntimeControlAck | None = None
    workspace_instance: WorkspaceInstanceRef
    initial_workspace_inspection: WorkspaceInspection
    terminal_workspace_inspection: WorkspaceInspection | None = None
    terminal_workspace_conformance_status: RequirementStatus
    initial_workspace_digest: ContentDigest
    terminal_workspace_digest: ContentDigest | None = None
    changes: WorkspaceChangeManifest | None = None
    validation_evidence_refs: tuple[StableExecutionKey, ...] = ()
    evidence_refs: tuple[StableExecutionKey, ...] = ()
    protected_verification_projection_refs: tuple[StableExecutionKey, ...] = ()
    hard_stop_reasons: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    proposed_work: tuple[ProposedWorkObservation, ...] = ()
    progress_observations: tuple[InternalProgressObservation, ...] = ()
    contract_gaps: tuple[ContractGapAnalysis, ...] = ()
    dirty: bool | None = None
    local_commit: str | None = None
    commit_parent: str | None = None
    external_effects_status: str = "UNKNOWN"
    credential_exposure_status: str = "NOT_APPLICABLE"

    @field_validator(
        "validation_evidence_refs",
        "evidence_refs",
        "protected_verification_projection_refs",
        "runtime_event_reasons",
        "hard_stop_reasons",
        "blockers",
    )
    @classmethod
    def tuples_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("evidence collections must be unique and sorted")
        return value

    @field_validator("proposed_work")
    @classmethod
    def proposed_work_is_canonical(
        cls, value: tuple[ProposedWorkObservation, ...]
    ) -> tuple[ProposedWorkObservation, ...]:
        keys = tuple(item.proposal_digest for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("proposed-work observations must be unique and sorted by digest")
        return value

    @field_validator("progress_observations")
    @classmethod
    def progress_is_canonical(
        cls, value: tuple[InternalProgressObservation, ...]
    ) -> tuple[InternalProgressObservation, ...]:
        keys = tuple(item.milestone_key for item in value)
        if keys != tuple(sorted(set(keys))):
            raise ValueError("progress observations must be unique and sorted by milestone")
        return value

    @model_validator(mode="after")
    def evidence_session_is_bound(self) -> ExecutionEvidenceBundle:
        if (
            self.runtime_session is not None
            and self.runtime_session.request_digest != self.runtime_request.request_digest
        ):
            raise ValueError("session must bind exact runtime request")
        if self.runtime_session is not None and (
            self.runtime_session.execution_id != self.runtime_request.basis.execution_id
        ):
            raise ValueError("session must bind exact ExecutionId")
        if self.runtime_handle is not None:
            if self.runtime_handle.request_digest != self.runtime_request.request_digest:
                raise ValueError("handle must bind exact runtime request")
            if self.runtime_handle.execution_id != self.runtime_request.basis.execution_id:
                raise ValueError("handle must bind exact ExecutionId")
            if self.runtime_session is not None and (
                self.runtime_handle.runtime_session != self.runtime_session.runtime_session
            ):
                raise ValueError("handle must bind exact runtime session")
        if self.runtime_session is not None:
            expected_execution = self.runtime_session.execution_id
            event_sequences: list[int] = []
            for event in self.runtime_events:
                if (
                    event.execution_id != expected_execution
                    or event.runtime_session != self.runtime_session.runtime_session
                ):
                    raise ValueError("events must bind to the exact runtime session")
                event_sequences.append(event.sequence)
            if event_sequences != sorted(set(event_sequences)):
                raise ValueError("runtime evidence events must retain strict sequence order")
        elif self.runtime_events:
            raise ValueError("runtime events require an exact session binding")
        if self.runtime_inspection is not None and (
            self.runtime_session is None
            or self.runtime_inspection.execution_id != self.runtime_session.execution_id
            or self.runtime_inspection.runtime_session != self.runtime_session.runtime_session
        ):
            raise ValueError("runtime inspection must bind exact session and ExecutionId")
        if self.cancellation_ack is not None and (
            self.runtime_session is None
            or self.cancellation_ack.execution_id != self.runtime_session.execution_id
        ):
            raise ValueError("cancellation acknowledgement must bind exact execution")
        if self.initial_workspace_inspection.instance_ref != self.workspace_instance:
            raise ValueError("initial workspace inspection must bind exact instance")
        if self.initial_workspace_digest != _digest_canonical_model(
            self.initial_workspace_inspection
        ):
            raise ValueError("initial workspace digest must match exact inspection")
        if self.runtime_payload_evidence.payload_digest != (
            self.runtime_request.basis.input_payload.payload_digest
        ):
            raise ValueError("evidence must bind exact runtime payload")
        if self.runtime_permission_evidence.execution_id != self.runtime_request.basis.execution_id:
            raise ValueError("permission evidence must bind exact ExecutionId")
        if (
            self.runtime_permission_evidence.effective_profile_ref
            != self.runtime_request.basis.permission_profile_ref
        ):
            raise ValueError("permission evidence must bind exact runtime profile")
        boundary_refs = (
            self.workspace_boundary_ref,
            self.runtime_placement_attestation,
            self.runtime_placement_continuity,
            self.runtime_process_teardown,
            self.runtime_permission_attestation,
            self.runtime_permission_attestation_ref,
        )
        if self.runtime_request_v2 is None:
            if any(value is not None for value in boundary_refs):
                raise ValueError("boundary evidence requires a V2 runtime request")
        else:
            if (
                self.runtime_request_v2.request != self.runtime_request
                or self.runtime_session is None
                or self.runtime_session.request_digest_v2
                != self.runtime_request_v2.request_digest_v2
                or self.workspace_boundary_ref is None
                or self.runtime_placement_attestation is None
                or self.runtime_permission_attestation is None
                or self.runtime_permission_attestation_ref is None
                or self.runtime_placement_continuity is None
                or self.runtime_process_teardown is None
            ):
                raise ValueError("V2 evidence requires complete placement and permission evidence")
            if (
                self.runtime_placement_attestation.ref
                != self.runtime_request_v2.placement_attestation_ref
                or self.runtime_request_v2.workspace_boundary_digest
                != self.workspace_boundary_ref.content_digest
                or self.runtime_placement_attestation.workspace_boundary_ref_digest
                != self.workspace_boundary_ref.content_digest
                or self.runtime_permission_attestation.ref
                != self.runtime_permission_attestation_ref
                or self.runtime_permission_attestation.session_binding != self.runtime_session
                or self.runtime_permission_attestation.request_digest_v2
                != self.runtime_request_v2.request_digest_v2
                or self.runtime_placement_continuity.workspace_boundary_ref_digest
                != self.workspace_boundary_ref.content_digest
                or self.runtime_placement_continuity.placement_attestation_ref
                != self.runtime_placement_attestation.ref
                or self.runtime_placement_continuity.execution_id
                != self.runtime_request.basis.execution_id
                or self.runtime_placement_continuity.request_digest_v2
                != self.runtime_request_v2.request_digest_v2
                or self.runtime_placement_continuity.process_tree_identity
                != self.runtime_placement_attestation.process_tree_identity
                or self.runtime_process_teardown.workspace_boundary_ref_digest
                != self.workspace_boundary_ref.content_digest
                or self.runtime_process_teardown.placement_attestation_ref
                != self.runtime_placement_attestation.ref
                or self.runtime_process_teardown.execution_id
                != self.runtime_request.basis.execution_id
                or self.runtime_process_teardown.process_tree_identity
                != self.runtime_placement_attestation.process_tree_identity
            ):
                raise ValueError("V2 evidence references must bind the exact immutable payloads")
        if (
            self.terminal_workspace_inspection is not None
            and self.terminal_workspace_inspection.instance_ref != self.workspace_instance
        ):
            raise ValueError("terminal workspace inspection must bind exact instance")
        if self.terminal_workspace_inspection is not None:
            if self.terminal_workspace_digest != _digest_canonical_model(
                self.terminal_workspace_inspection
            ):
                raise ValueError("terminal workspace digest must match exact inspection")
            observed_dirty = bool(
                self.terminal_workspace_inspection.tracked_changes
                or self.terminal_workspace_inspection.untracked_paths
            )
            if self.dirty is not observed_dirty:
                raise ValueError("dirty state must match exact terminal workspace inspection")
        if self.changes is not None:
            if (
                self.changes.instance_ref != self.workspace_instance
                or self.changes.source_commit != self.workspace_instance.source_commit
            ):
                raise ValueError("change manifest must bind exact workspace and source commit")
            if self.terminal_workspace_inspection is None:
                raise ValueError("change manifest requires terminal workspace inspection")
        if self.local_commit is not None and (
            self.local_commit == self.workspace_instance.source_commit.sha
            or self.commit_parent != self.workspace_instance.source_commit.sha
            or self.terminal_workspace_inspection is None
            or self.local_commit != self.terminal_workspace_inspection.head_commit.sha
        ):
            raise ValueError("local commit must bind the exact source parent and terminal head")
        if any(
            item.execution_id != self.runtime_request.basis.execution_id
            for item in self.progress_observations
        ):
            raise ValueError("progress observations must remain bound to this execution")
        if any(
            item.source_execution_id != self.runtime_request.basis.execution_id
            for item in self.proposed_work
        ):
            raise ValueError("proposed work must remain evidence for this execution")
        if (self.local_commit is None) != (self.commit_parent is None):
            raise ValueError("local commit and parent must be present together")
        return self


class TerminalExecutionResult(DomainModel):
    """Immutable terminal result and evaluator handoff, never an acceptance."""

    execution_id: ExecutionId
    subject: ExecutionSubject
    outcome: ExecutionTerminalOutcome
    evidence: ExecutionEvidenceBundle
    evaluator_handoff_digest: ContentDigest
    self_acceptance_attempted: bool = False

    @model_validator(mode="after")
    def result_is_bound_and_not_self_accepted(self) -> TerminalExecutionResult:
        if self.execution_id != self.subject.execution_id:
            raise ValueError("result ExecutionId must match subject")
        if self.evidence.execution_subject_digest != self.subject.content_digest:
            raise ValueError("evidence must bind exact subject digest")
        if self.evidence.runtime_permission_evidence != self.subject.runtime_permission_evidence:
            raise ValueError("evidence must preserve the subject's exact permission attestation")
        if self.evaluator_handoff_digest != digest_evaluator_handoff(
            self.subject, self.outcome, self.evidence
        ):
            raise ValueError(
                "evaluator handoff digest must bind exact subject, result, and evidence"
            )
        if self.self_acceptance_attempted:
            raise ValueError("implementer cannot self-accept an execution result")
        if self.outcome is ExecutionTerminalOutcome.DONE and (
            self.evidence.runtime_inspection is None
            or self.evidence.runtime_session is None
            or self.evidence.runtime_handle is None
            or self.evidence.terminal_workspace_digest is None
            or self.evidence.terminal_workspace_inspection is None
            or self.evidence.changes is None
            or self.evidence.runtime_inspection.runtime_status.value != "SUCCEEDED"
            or self.evidence.runtime_inspection.continuity.state.value != "COMPLETE"
            or self.subject.actual_provider_id is None
            or self.subject.actual_model_id is None
            or self.evidence.external_effects_status != "CLEAR"
            or self.evidence.credential_exposure_status not in {"CLEAR", "NOT_APPLICABLE"}
            or self.evidence.terminal_workspace_conformance_status
            is not RequirementStatus.SATISFIED
            or self.evidence.dirty is None
            or self.subject.runtime_permission_evidence.completeness
            is not RequirementStatus.SATISFIED
            or self.subject.runtime_permission_evidence.provenance_status
            is not RequirementStatus.SATISFIED
            or self.subject.runtime_request_v2 is not None
            and (
                self.evidence.runtime_placement_continuity is None
                or self.evidence.runtime_placement_continuity.status
                is not RequirementStatus.SATISFIED
                or self.evidence.runtime_process_teardown is None
                or self.evidence.runtime_process_teardown.process_tree_terminated
                is not RequirementStatus.SATISFIED
                or self.evidence.runtime_process_teardown.credential_cleanup
                is not RequirementStatus.SATISFIED
            )
        ):
            raise ValueError("DONE requires successful runtime and terminal workspace evidence")
        if self.outcome is ExecutionTerminalOutcome.DONE:
            required_evidence = {
                item.key
                for item in (
                    *self.subject.work_packet.evidence_requirements,
                    *self.subject.work_packet.deliverable_requirements,
                )
                if item.required
            }
            supplied_evidence = set(self.evidence.evidence_refs) | set(
                self.evidence.validation_evidence_refs
            )
            if required_evidence - supplied_evidence:
                raise ValueError("DONE requires all packet evidence and deliverable references")
            if (
                self.subject.work_packet.protected_verification_requirements
                and not self.evidence.protected_verification_projection_refs
            ):
                raise ValueError("DONE requires protected verification evidence")
            if (
                self.subject.work_packet.credential_refs
                and self.evidence.credential_exposure_status != "CLEAR"
            ):
                raise ValueError("DONE requires clear credential exposure evidence")
        if (
            self.evidence.grant != self.subject.human_grant
            or self.evidence.reservations != self.subject.reservations
            or self.evidence.runtime_request != self.subject.runtime_request
            or self.evidence.runtime_request_v2 != self.subject.runtime_request_v2
            or self.evidence.workspace_boundary_ref != self.subject.workspace_boundary_ref
            or self.evidence.runtime_placement_attestation
            != self.subject.runtime_placement_attestation
            or self.subject.runtime_request_v2 is not None
            and self.evidence.runtime_session != self.subject.runtime_session_binding
            or self.evidence.runtime_permission_attestation
            != self.subject.runtime_permission_attestation
            or self.evidence.runtime_permission_attestation_ref
            != self.subject.runtime_permission_attestation_ref
            or self.evidence.runtime_payload_evidence != self.subject.runtime_payload_evidence
            or self.evidence.workspace_instance != self.subject.workspace_instance
            or self.evidence.runtime_permission_evidence != self.subject.runtime_permission_evidence
        ):
            raise ValueError("terminal evidence must preserve exact subject bindings")
        if self.evidence.runtime_inspection is not None and (
            self.evidence.runtime_inspection.provenance.actual_provider_id
            != self.subject.actual_provider_id
            or self.evidence.runtime_inspection.provenance.actual_model_id
            != self.subject.actual_model_id
        ):
            raise ValueError("terminal inspection identity must match exact subject")
        if self.subject.runtime_session is not None and (
            self.subject.runtime_session != self.evidence.runtime_session.runtime_session
            if self.evidence.runtime_session is not None
            else True
        ):
            raise ValueError("subject and evidence runtime sessions must match")
        if self.subject.runtime_handle is not None and self.subject.runtime_handle != (
            self.evidence.runtime_handle
        ):
            raise ValueError("subject and evidence runtime handles must match")
        return self


def _digest_canonical_model(model: DomainModel) -> ContentDigest:
    """Return the canonical SHA-256 used for model-bound evidence digests."""

    canonical = json.dumps(
        model.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def execution_id_for_attempt(intended_attempt_id: str) -> ExecutionId:
    """Map canonical ``exec-UUID`` attempt identity to ``exec_UUID`` exactly."""

    match = re.fullmatch(
        r"exec-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        intended_attempt_id,
    )
    if match is None:
        raise ValueError("intended_attempt_id must be canonical exec-<lowercase-uuid>")
    return "exec_" + match.group(1)


def attempt_id_for_execution(execution_id: ExecutionId) -> StableExecutionKey:
    """Reverse the exact one-to-one governed attempt mapping."""

    match = re.fullmatch(
        r"exec_([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        execution_id,
    )
    if match is None:
        raise ValueError("ExecutionId must be canonical exec_<lowercase-uuid>")
    return "exec-" + match.group(1)


def canonical_subject_json(subject: ExecutionSubject) -> str:
    """Serialize subject identity deterministically as compact canonical JSON."""

    return json.dumps(
        subject.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest_evaluator_handoff(
    subject: ExecutionSubject,
    outcome: ExecutionTerminalOutcome,
    evidence: ExecutionEvidenceBundle,
) -> ContentDigest:
    """Hash the immutable subject, terminal disposition and exact evidence bundle."""

    payload = {
        "execution_subject_digest": subject.content_digest,
        "outcome": outcome.value,
        "evidence": evidence.model_dump(mode="json"),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def digest_evaluator_rework_record(binding: EvaluatorReworkBinding) -> ContentDigest:
    """Digest the evaluator projection, excluding source identity and verification state."""

    payload = binding.model_dump(
        mode="json",
        exclude={"registered_record_digest", "projection_digest", "provenance_status"},
    )
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def digest_terminal_candidate(result: TerminalExecutionResult) -> ContentDigest | None:
    """Digest exact terminal workspace changes and commit state for evaluator review."""

    if result.evidence.changes is None:
        return None
    payload = {
        "changes": result.evidence.changes.model_dump(mode="json"),
        "local_commit": result.evidence.local_commit,
        "commit_parent": result.evidence.commit_parent,
        "dirty": result.evidence.dirty,
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()


def digest_terminal_result(result: TerminalExecutionResult) -> ContentDigest:
    """Digest the exact immutable result, including subject, evidence and handoff."""

    canonical = json.dumps(
        result.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
