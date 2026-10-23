"""Provider-neutral workspace API and normalized operational failures."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from relay_engine.execution_workspace.models import (
    WorkspaceChangeManifest,
    WorkspaceInspection,
    WorkspaceInstanceRef,
    WorkspacePlan,
    WorkspaceProviderDescriptor,
    WorkspaceProvisionResult,
    WorkspaceTeardownEvidence,
)


class WorkspaceProviderErrorCode(StrEnum):
    INVALID_PLAN = "INVALID_PLAN"
    UNSUPPORTED_POLICY = "UNSUPPORTED_POLICY"
    SOURCE_NOT_AVAILABLE = "SOURCE_NOT_AVAILABLE"
    SOURCE_COMMIT_NOT_AVAILABLE = "SOURCE_COMMIT_NOT_AVAILABLE"
    PROVISION_FAILED = "PROVISION_FAILED"
    INSPECTION_FAILED = "INSPECTION_FAILED"
    CHANGESET_FAILED = "CHANGESET_FAILED"
    TEARDOWN_FAILED = "TEARDOWN_FAILED"
    ENVIRONMENT_ERROR = "ENVIRONMENT_ERROR"


class WorkspaceProviderError(RuntimeError):
    """Safe provider failure without native output or credential material."""

    def __init__(self, code: WorkspaceProviderErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


class WorkspaceProvider(Protocol):
    """Explicit provider contract; calling it is not execution authorization."""

    def describe(self) -> WorkspaceProviderDescriptor: ...

    def provision(self, plan: WorkspacePlan) -> WorkspaceProvisionResult: ...

    def inspect(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceInspection: ...

    def extract_changes(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceChangeManifest: ...

    def teardown(self, instance_ref: WorkspaceInstanceRef) -> WorkspaceTeardownEvidence: ...


__all__ = ["WorkspaceProvider", "WorkspaceProviderError", "WorkspaceProviderErrorCode"]
