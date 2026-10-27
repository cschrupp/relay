"""Runtime-neutral interface for observing an already-authorized execution."""

from collections.abc import AsyncIterator
from typing import Protocol

from relay_engine.agent_runtime.boundary import (
    RuntimePermissionAttestation,
    RuntimeRequestV2,
)
from relay_engine.agent_runtime.models import (
    EventContinuity,
    RuntimeCancelRequest,
    RuntimeControlAck,
    RuntimeDescriptor,
    RuntimeEventEnvelope,
    RuntimeExecutionHandle,
    RuntimeExecutionInspection,
    RuntimeExecutionRequest,
    RuntimeSessionBinding,
)


class AgentRuntime(Protocol):
    """Observe and control a runtime session without owning Relay authority."""

    async def describe(self) -> RuntimeDescriptor:
        """Return the adapter profile and supported capabilities."""
        ...

    async def create_session(self, request: RuntimeExecutionRequest) -> RuntimeSessionBinding:
        """Create and bind a session without admitting the request prompt."""
        ...

    async def open_execution(
        self,
        request: RuntimeExecutionRequest,
        binding: RuntimeSessionBinding,
    ) -> RuntimeExecutionHandle:
        """Observe first, admit one prompt, and return an exact handle for recovery.

        If the prompt response is uncertain, the handle still identifies the bound
        session so callers can inspect or cancel it without retrying admission.
        """
        ...

    def events(self, handle: RuntimeExecutionHandle) -> AsyncIterator[RuntimeEventEnvelope]:
        """Consume observations from an already-open adapter event buffer."""
        ...

    async def cancel(self, request: RuntimeCancelRequest) -> RuntimeControlAck:
        """Request idempotent runtime cancellation without changing Relay lifecycle."""
        ...

    async def inspect(self, handle: RuntimeExecutionHandle) -> RuntimeExecutionInspection:
        """Return runtime observation only; never construct an engineering result."""
        ...


class ContinuityInspectable(Protocol):
    """Optional adapter detail for retrieving current event continuity."""

    def continuity(self, handle: RuntimeExecutionHandle) -> EventContinuity:
        """Return current continuity for an active or completed event stream."""
        ...


class BoundaryManagedAgentRuntime(Protocol):
    """V2 session and prompt operations bound to verified placement evidence."""

    async def create_session_v2(self, request: RuntimeRequestV2) -> RuntimeSessionBinding:
        """Create exactly one prompt-free session for the placement-bound request."""
        ...

    async def attest_permissions_v2(
        self,
        request: RuntimeRequestV2,
        binding: RuntimeSessionBinding,
    ) -> RuntimePermissionAttestation:
        """Attest actual effective permissions of that exact prompt-free session."""
        ...

    async def open_execution_v2(
        self,
        request: RuntimeRequestV2,
        binding: RuntimeSessionBinding,
        permission_attestation: RuntimePermissionAttestation,
    ) -> RuntimeExecutionHandle:
        """Admit one prompt only after Relay's final V2 admission decision."""
        ...
