"""Exact workspace-boundary and runtime-placement evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Annotated

from pydantic import StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime.boundary import RuntimePlacementAttestationRef
from relay_engine.domain import ContentDigest, ExecutionId
from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.execution_workspace.models import (
    WorkspaceInstanceRef,
    WorkspacePlanRef,
    WorkspaceProviderRef,
)
from relay_engine.role_contracts import RequirementStatus

type BoundaryIdentity = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=256)]
type BoundaryMechanism = Annotated[
    str, StringConstraints(strict=True, min_length=1, max_length=128)
]


def _canonical(model: DomainModel, *, exclude: set[str] | None = None) -> str:
    validated = type(model).model_validate(model.model_dump(mode="python"))
    return json.dumps(
        validated.model_dump(mode="json", exclude=exclude or set()),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


class PlacementAttesterRef(DomainModel):
    """Provider-bound expected placement attester and trust basis."""

    provider_ref: WorkspaceProviderRef
    attester_id: BoundaryIdentity
    attester_version: BoundaryIdentity
    trust_anchor_digest: ContentDigest | None = None
    authenticated_channel_key: BoundaryIdentity | None = None

    @model_validator(mode="after")
    def trust_basis_is_explicit(self) -> PlacementAttesterRef:
        if self.trust_anchor_digest is None and self.authenticated_channel_key is None:
            raise ValueError("placement attester requires an explicit trust basis")
        return self


class WorkspaceBoundaryRef(DomainModel):
    """Immutable identity of one provisioned enforcement boundary."""

    plan_ref: WorkspacePlanRef
    instance_ref: WorkspaceInstanceRef
    provider_ref: WorkspaceProviderRef
    boundary_instance_key: BoundaryIdentity
    boundary_policy_digest: ContentDigest
    boundary_mechanism_key: BoundaryMechanism
    boundary_evidence_digest: ContentDigest
    expected_placement_attester_ref: PlacementAttesterRef
    placement_attestation_contract_version: str = "runtime-placement-attestation-v1"

    @model_validator(mode="after")
    def refs_bind_one_instance(self) -> WorkspaceBoundaryRef:
        if self.instance_ref.plan_ref != self.plan_ref:
            raise ValueError("boundary must bind the exact workspace plan")
        if self.instance_ref.provider_ref != self.provider_ref:
            raise ValueError("boundary must bind the exact workspace provider")
        if self.expected_placement_attester_ref.provider_ref != self.provider_ref:
            raise ValueError("expected placement attester must be bound to the provider")
        if self.placement_attestation_contract_version != "runtime-placement-attestation-v1":
            raise ValueError("unsupported placement-attestation contract version")
        return self

    @property
    def content_digest(self) -> ContentDigest:
        payload = _canonical(self).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()


class RuntimePlacementAttestation(DomainModel):
    """Provider-produced, exact evidence that one runtime tree occupies a boundary."""

    attestation_id: BoundaryIdentity
    contract_version: str = "runtime-placement-attestation-v1"
    launch_subject_digest: ContentDigest
    workspace_boundary_ref_digest: ContentDigest
    runtime_descriptor_digest: ContentDigest
    process_tree_identity: BoundaryIdentity
    runtime_server_identity: BoundaryIdentity
    endpoint_identity: BoundaryIdentity
    observed_boundary_membership: RequirementStatus
    enforcement_evidence_digest: ContentDigest
    credential_separation_status: RequirementStatus
    credential_separation_evidence_digest: ContentDigest
    attester_id: BoundaryIdentity
    attester_version: BoundaryIdentity
    trust_anchor_digest: ContentDigest | None = None
    authenticated_channel_key: BoundaryIdentity | None = None
    trust_evidence_digest: ContentDigest
    challenge_or_launch_nonce: BoundaryIdentity
    observed_from: datetime
    observed_until: datetime
    completeness: RequirementStatus

    @field_validator("observed_from", "observed_until")
    @classmethod
    def timestamps_are_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("placement observation timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def evidence_is_complete_and_bounded(self) -> RuntimePlacementAttestation:
        if self.contract_version != "runtime-placement-attestation-v1":
            raise ValueError("unsupported placement-attestation version")
        if self.observed_until < self.observed_from:
            raise ValueError("placement observation interval is reversed")
        if self.trust_anchor_digest is None and self.authenticated_channel_key is None:
            raise ValueError("placement attestation must identify its authenticated trust basis")
        for field in (
            "process_tree_identity",
            "runtime_server_identity",
            "endpoint_identity",
            "challenge_or_launch_nonce",
        ):
            require_nonblank(getattr(self, field))
        return self

    @property
    def content_digest(self) -> ContentDigest:
        payload = _canonical(self).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()

    @property
    def ref(self) -> RuntimePlacementAttestationRef:
        return RuntimePlacementAttestationRef(
            attestation_id=self.attestation_id,
            content_digest=self.content_digest,
        )


class RuntimePlacementContinuityEvidence(DomainModel):
    """Boundary observer evidence for the exact runtime process tree over time."""

    workspace_boundary_ref_digest: ContentDigest
    placement_attestation_ref: RuntimePlacementAttestationRef
    execution_id: ExecutionId
    request_digest_v2: ContentDigest
    process_tree_identity: BoundaryIdentity
    observer_id: BoundaryIdentity
    observed_from: datetime
    observed_until: datetime
    status: RequirementStatus
    evidence_digest: ContentDigest

    @field_validator("observed_from", "observed_until")
    @classmethod
    def timestamps_are_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("continuity timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def interval_is_valid(self) -> RuntimePlacementContinuityEvidence:
        if self.observed_until < self.observed_from:
            raise ValueError("continuity observation interval is reversed")
        return self


class RuntimeProcessTeardownEvidence(DomainModel):
    """Terminal cleanup evidence for the exact runtime tree and boundary."""

    workspace_boundary_ref_digest: ContentDigest
    placement_attestation_ref: RuntimePlacementAttestationRef
    execution_id: ExecutionId
    process_tree_identity: BoundaryIdentity
    process_tree_terminated: RequirementStatus
    credential_cleanup: RequirementStatus
    evidence_digest: ContentDigest


def placement_attestation_matches_boundary(
    boundary: WorkspaceBoundaryRef,
    attestation: RuntimePlacementAttestation,
    *,
    launch_subject_digest: ContentDigest,
    runtime_descriptor_digest: ContentDigest,
    launch_nonce: str,
) -> bool:
    """Check exact attester, boundary, launch and runtime bindings."""

    expected = boundary.expected_placement_attester_ref
    trust_matches = (
        attestation.trust_anchor_digest == expected.trust_anchor_digest
        and attestation.authenticated_channel_key == expected.authenticated_channel_key
    )
    return all(
        (
            trust_matches,
            attestation.workspace_boundary_ref_digest == boundary.content_digest,
            attestation.launch_subject_digest == launch_subject_digest,
            attestation.runtime_descriptor_digest == runtime_descriptor_digest,
            attestation.challenge_or_launch_nonce == launch_nonce,
            attestation.attester_id == expected.attester_id,
            attestation.attester_version == expected.attester_version,
            attestation.completeness is RequirementStatus.SATISFIED,
            attestation.observed_boundary_membership is RequirementStatus.SATISFIED,
            attestation.credential_separation_status is RequirementStatus.SATISFIED,
        )
    )


__all__ = [
    "PlacementAttesterRef",
    "RuntimePlacementAttestation",
    "RuntimePlacementContinuityEvidence",
    "RuntimeProcessTeardownEvidence",
    "WorkspaceBoundaryRef",
    "placement_attestation_matches_boundary",
]
