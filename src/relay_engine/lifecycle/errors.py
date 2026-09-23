"""Typed failures for lifecycle operations and event replay."""


class LifecycleError(Exception):
    """Base class for validly shaped lifecycle requests that cannot be applied."""


class InvalidPhaseTransition(LifecycleError):
    """The requested phase movement violates the lifecycle contract."""


class InvalidLifecycleOperation(LifecycleError):
    """A lifecycle operation is invalid or would be a semantic no-op."""


class LifecycleReplayError(LifecycleError):
    """Lifecycle event history is malformed or internally inconsistent."""
