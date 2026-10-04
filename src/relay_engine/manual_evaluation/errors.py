"""Typed failures for Slice 1.7 manual evaluation commands."""


class ManualEvaluationError(Exception):
    """Base class for rejected or unavailable manual-evaluation actions."""


class ManualEvaluationNotAvailable(ManualEvaluationError):
    """The requested Slice 1.7 action is unavailable in current durable state."""


class ManualEvaluationStale(ManualEvaluationError):
    """The submitted result, lifecycle, or gate basis is no longer current."""


class ManualEvaluationConflict(ManualEvaluationError):
    """A competing immutable action won optimistic concurrency."""


class ManualEvaluationInvalid(ManualEvaluationError):
    """Caller-supplied evaluator or evidence data is invalid."""


class ManualEvaluationForbidden(ManualEvaluationError):
    """The server-bound command actor is not permitted for this action."""
