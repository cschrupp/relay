"""Provider descriptor canonicality and exact capability tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from relay_engine.execution_workspace.models import (
    ControlStrength,
    CredentialExposureMode,
    ExternalSideEffectMode,
    NetworkMode,
    RepositoryMetadataAccess,
    ShellMode,
    WorkspaceBackendKind,
    WorkspaceBoundaryClass,
    WorkspaceProperty,
    WorkspaceProviderDescriptor,
    WorkspaceProviderPropertyCapability,
)


def descriptor(
    capabilities: tuple[WorkspaceProviderPropertyCapability, ...],
) -> WorkspaceProviderDescriptor:
    return WorkspaceProviderDescriptor(
        provider_id="contract-provider",
        provider_version="1",
        backend_kind=WorkspaceBackendKind.OTHER,
        boundary_class=WorkspaceBoundaryClass.MEDIATED_PROCESS_BOUNDARY,
        property_capabilities=capabilities,
        supported_shell_modes=(ShellMode.DENY,),
        supported_network_modes=(NetworkMode.DENY_ALL,),
        supported_external_side_effect_modes=(ExternalSideEffectMode.DENY_MUTATING_EFFECTS,),
        supported_credential_exposure_modes=(CredentialExposureMode.NONE,),
        supported_resource_dimensions=(),
        supported_repository_metadata_modes=(RepositoryMetadataAccess.READ_ONLY,),
        path_control_capabilities=(),
        provider_injected_file_capabilities=(),
    )


def test_property_capabilities_must_be_unique_and_enum_ordered() -> None:
    cap = WorkspaceProviderPropertyCapability(
        property=WorkspaceProperty.EXACT_SOURCE_BASELINE, maximum_strength=ControlStrength.DETECTIVE
    )
    with pytest.raises(ValidationError):
        descriptor((cap, cap))


def test_local_provider_claims_same_user_boundary_and_no_strong_controls() -> None:
    from relay_engine.execution_workspace.local_clone import LocalCloneWorkspaceProvider

    descriptor_value = LocalCloneWorkspaceProvider(".").describe()
    assert descriptor_value.backend_kind is WorkspaceBackendKind.LOCAL_CLONE
    assert descriptor_value.boundary_class is WorkspaceBoundaryClass.SAME_USER_NO_SECURITY_BOUNDARY
    assert all(
        item.maximum_strength is not ControlStrength.BOUNDARY_ENFORCED
        for item in descriptor_value.property_capabilities
    )
