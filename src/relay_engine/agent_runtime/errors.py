"""Safe exceptions raised by AgentRuntime adapters."""

from __future__ import annotations

from relay_engine.agent_runtime.models import (
    RuntimeFailure,
    RuntimeFailureCategory,
    RuntimeSessionRef,
)
from relay_engine.domain import ExecutionId


class AgentRuntimeError(Exception):
    """Exception wrapper whose public message is a normalized safe failure."""

    def __init__(self, failure: RuntimeFailure) -> None:
        self.failure = failure
        super().__init__(failure.message)


def fail(
    category: RuntimeFailureCategory,
    message: str,
    *,
    retryable: bool = False,
    runtime_code: str | None = None,
    execution_id: ExecutionId | None = None,
    runtime_session: RuntimeSessionRef | None = None,
) -> AgentRuntimeError:
    """Build an exception with only bounded, redacted public failure data."""

    return AgentRuntimeError(
        RuntimeFailure(
            category=category,
            message=message,
            retryable=retryable,
            runtime_code=runtime_code,
            execution_id=execution_id,
            runtime_session=runtime_session,
        )
    )
