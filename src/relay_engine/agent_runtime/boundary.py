"""Versioned runtime-boundary request and attestation contracts."""

from __future__ import annotations

import hashlib
import ipaddress
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import StringConstraints, field_validator, model_validator

from relay_engine.agent_runtime.models import (
    RuntimeExecutionRequest,
    RuntimePermissionProfileRef,
    RuntimeSessionBinding,
)
from relay_engine.domain import ContentDigest, ExecutionId
from relay_engine.domain._base import DomainModel, require_nonblank

type BoundaryText = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=512)]
type BoundaryIdentity = Annotated[str, StringConstraints(strict=True, min_length=1, max_length=256)]


def _canonical_json(model: DomainModel) -> str:
    validated = type(model).model_validate(model.model_dump(mode="python"))
    return json.dumps(
        validated.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(model: DomainModel) -> ContentDigest:
    return "sha256:" + hashlib.sha256(_canonical_json(model).encode("utf-8")).hexdigest()


class RuntimeLaunchSubject(DomainModel):
    """Exact runtime and execution inputs handed to one boundary launcher."""

    execution_id: ExecutionId
    intended_attempt_id: BoundaryIdentity
    authority_candidate_digest: ContentDigest
    human_grant_digest: ContentDigest
    work_packet_ref_digest: ContentDigest
    context_manifest_ref_digest: ContentDigest
    workspace_plan_ref_digest: ContentDigest
    workspace_instance_digest: ContentDigest
    workspace_boundary_digest: ContentDigest
    runtime_descriptor_digest: ContentDigest
    runtime_id: BoundaryIdentity
    runtime_version: BoundaryIdentity
    adapter_id: BoundaryIdentity
    adapter_version: BoundaryIdentity
    challenge_or_launch_nonce: BoundaryIdentity
    executable_identity: BoundaryText
    runtime_configuration_digest: ContentDigest
    runtime_api_generation: BoundaryIdentity
    endpoint_allocation_policy: BoundaryText
    requested_provider_id: BoundaryIdentity
    requested_model_id: BoundaryIdentity
    permission_profile_ref: RuntimePermissionProfileRef
    credential_reference_ids: tuple[BoundaryIdentity, ...] = ()
    runtime_request_payload_digest: ContentDigest
    runtime_limits_digest: ContentDigest

    @field_validator("credential_reference_ids")
    @classmethod
    def credential_ids_are_canonical(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != tuple(sorted(set(value))):
            raise ValueError("credential reference identities must be unique and sorted")
        return value

    @field_validator("executable_identity", "endpoint_allocation_policy")
    @classmethod
    def text_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @property
    def content_digest(self) -> ContentDigest:
        return _digest(self)


class RuntimePlacementAttestationRef(DomainModel):
    """Immutable exact reference to one placement-attestation payload."""

    attestation_id: BoundaryIdentity
    content_digest: ContentDigest


class RuntimeRequestV2(DomainModel):
    """A V1 runtime request bound to exact launch and placement evidence."""

    contract_version: str = "runtime-execution-request-v2"
    request: RuntimeExecutionRequest
    launch_subject: RuntimeLaunchSubject
    workspace_boundary_digest: ContentDigest
    placement_attestation_ref: RuntimePlacementAttestationRef
    placement_attestation_digest: ContentDigest
    endpoint_identity: BoundaryText
    request_digest_v2: ContentDigest

    @field_validator("endpoint_identity")
    @classmethod
    def endpoint_is_explicit_and_credential_free(cls, value: str) -> str:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https", "unix"}
            or not parsed.netloc
            and parsed.scheme != "unix"
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("endpoint identity must be explicit and contain no credentials")
        if parsed.scheme == "unix":
            if parsed.netloc or not parsed.path.startswith("/"):
                raise ValueError("Unix control endpoint must use an absolute socket path")
            return value
        hostname = parsed.hostname
        try:
            is_loopback = hostname is not None and ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = hostname == "localhost"
        if not is_loopback or parsed.port is None:
            raise ValueError("HTTP runtime endpoint must be explicit loopback with a port")
        return value

    @model_validator(mode="after")
    def exact_launch_and_placement_bindings(self) -> RuntimeRequestV2:
        if self.contract_version != "runtime-execution-request-v2":
            raise ValueError("unsupported runtime request version")
        if self.request.basis.execution_id != self.launch_subject.execution_id:
            raise ValueError("V2 request and launch subject must bind the same ExecutionId")
        if self.request.basis.runtime_selection.runtime_id == "":
            raise ValueError("runtime selection identity is required")
        if self.request.basis.runtime_selection.runtime_id != self.launch_subject.runtime_id:
            raise ValueError("launch subject must bind the exact runtime identity")
        if self.launch_subject.requested_provider_id != (
            self.request.basis.runtime_selection.requested_provider_id
        ) or self.launch_subject.requested_model_id != (
            self.request.basis.runtime_selection.requested_model_id
        ):
            raise ValueError("launch subject must bind the exact requested provider and model")
        if self.launch_subject.permission_profile_ref != self.request.basis.permission_profile_ref:
            raise ValueError("launch subject must bind the exact permission profile")
        if self.workspace_boundary_digest != self.launch_subject.workspace_boundary_digest:
            raise ValueError("V2 request must bind the exact workspace boundary")
        if self.placement_attestation_digest != self.placement_attestation_ref.content_digest:
            raise ValueError("placement ref and digest must match")
        if self.request_digest_v2 != digest_runtime_request_v2(self):
            raise ValueError("V2 request digest does not match canonical request content")
        return self


def canonical_runtime_request_v2_json(request: RuntimeRequestV2) -> str:
    """Canonical V2 request bytes, excluding only the derived digest field."""

    values = request.model_dump(mode="json", exclude={"request_digest_v2"})
    return json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest_runtime_request_v2(request: RuntimeRequestV2) -> ContentDigest:
    payload = request.model_dump(mode="json", exclude={"request_digest_v2"})
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


class RuntimeEvidenceCompleteness(StrEnum):
    """Stable completeness vocabulary for runtime permission observations."""

    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    INDETERMINATE = "INDETERMINATE"


class RuntimePermissionAttestation(DomainModel):
    """Exact immutable effective-permission observation for one prompt-free session."""

    attestation_id: BoundaryIdentity
    contract_version: str = "runtime-permission-attestation-v1"
    execution_id: ExecutionId
    request_digest_v2: ContentDigest
    session_binding: RuntimeSessionBinding
    runtime_descriptor_digest: ContentDigest
    launch_subject_digest: ContentDigest
    placement_attestation_digest: ContentDigest
    expected_permission_profile_ref: RuntimePermissionProfileRef
    observed_effective_profile_digest: ContentDigest | None
    effective_tool_exposure: tuple[BoundaryIdentity, ...] | None
    unknown_tool_identity: bool = False
    effective_shell_exposure: bool | None
    actual_provider_id: BoundaryIdentity | None = None
    actual_model_id: BoundaryIdentity | None = None
    completeness: RuntimeEvidenceCompleteness
    observation_provenance_digest: ContentDigest
    adapter_identity: BoundaryIdentity
    adapter_version: BoundaryIdentity
    observed_from: datetime
    observed_until: datetime

    @field_validator("effective_tool_exposure")
    @classmethod
    def exposed_tools_are_canonical(cls, value: tuple[str, ...] | None) -> tuple[str, ...] | None:
        if value is not None and value != tuple(sorted(set(value))):
            raise ValueError("effective tool exposure must be unique and sorted")
        return value

    @field_validator("observed_from", "observed_until")
    @classmethod
    def timestamps_are_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("permission observation timestamps must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def evidence_is_exact(self) -> RuntimePermissionAttestation:
        if self.contract_version != "runtime-permission-attestation-v1":
            raise ValueError("unsupported permission attestation version")
        if self.session_binding.execution_id != self.execution_id:
            raise ValueError("permission attestation must bind the exact ExecutionId")
        if self.session_binding.request_digest_v2 != self.request_digest_v2:
            raise ValueError("permission attestation must bind the exact V2 session request")
        if self.observed_until < self.observed_from:
            raise ValueError("permission observation interval is reversed")
        if self.completeness not in {
            RuntimeEvidenceCompleteness.SATISFIED,
            RuntimeEvidenceCompleteness.UNSATISFIED,
            RuntimeEvidenceCompleteness.INDETERMINATE,
        }:
            raise ValueError("unknown permission-attestation completeness")
        if self.completeness is RuntimeEvidenceCompleteness.SATISFIED and (
            self.observed_effective_profile_digest is None
            or self.effective_tool_exposure is None
            or self.unknown_tool_identity
            or self.effective_shell_exposure is None
            or self.actual_provider_id is None
            or self.actual_model_id is None
        ):
            raise ValueError(
                "complete permission evidence requires exact profile, exposure and route"
            )
        return self

    @property
    def content_digest(self) -> ContentDigest:
        return digest_runtime_permission_attestation(self)

    @property
    def ref(self) -> RuntimePermissionAttestationRef:
        return RuntimePermissionAttestationRef(
            attestation_id=self.attestation_id,
            content_digest=self.content_digest,
        )


class RuntimePermissionAttestationRef(DomainModel):
    """Immutable exact reference to one permission-attestation payload."""

    attestation_id: BoundaryIdentity
    content_digest: ContentDigest


def canonical_runtime_permission_attestation_json(
    attestation: RuntimePermissionAttestation,
) -> str:
    """Serialize validated fields, including stable ID and excluding derived ref/digest."""

    values = attestation.model_dump(mode="json", exclude={"content_digest", "ref"})
    return json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest_runtime_permission_attestation(
    attestation: RuntimePermissionAttestation,
) -> ContentDigest:
    encoded = canonical_runtime_permission_attestation_json(attestation).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def verify_runtime_permission_attestation_ref(
    attestation: RuntimePermissionAttestation,
    reference: RuntimePermissionAttestationRef,
) -> bool:
    return attestation.ref == reference


def build_runtime_request_v2(
    *,
    request: RuntimeExecutionRequest,
    launch_subject: RuntimeLaunchSubject,
    placement_attestation_ref: RuntimePlacementAttestationRef,
    endpoint_identity: str,
) -> RuntimeRequestV2:
    """Build a V2 request and calculate its digest from the exact payload."""

    values: dict[str, object] = {
        "schema_version": 1,
        "contract_version": "runtime-execution-request-v2",
        "request": request.model_dump(mode="python"),
        "launch_subject": launch_subject.model_dump(mode="python"),
        "workspace_boundary_digest": launch_subject.workspace_boundary_digest,
        "placement_attestation_ref": placement_attestation_ref.model_dump(mode="python"),
        "placement_attestation_digest": placement_attestation_ref.content_digest,
        "endpoint_identity": endpoint_identity,
    }
    encoded = json.dumps(
        values,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    values["request_digest_v2"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
    return RuntimeRequestV2.model_validate(values)
