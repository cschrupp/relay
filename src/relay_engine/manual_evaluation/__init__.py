"""Human-authored Slice result evaluation and acceptance projections."""

from relay_engine.manual_evaluation.errors import (
    ManualEvaluationConflict,
    ManualEvaluationError,
    ManualEvaluationForbidden,
    ManualEvaluationInvalid,
    ManualEvaluationNotAvailable,
    ManualEvaluationStale,
)
from relay_engine.manual_evaluation.models import (
    AcceptedSliceResult,
    DevelopmentMemoryProjection,
    EvaluationEvidenceSubmission,
    ManualEvaluationActionBasis,
    ManualEvaluationActionKind,
    ManualEvaluationProjection,
    ManualEvaluationRecord,
    SliceResultRecord,
)

_SERVICE_EXPORTS = frozenset(
    {
        "attach_result",
        "project_development_memory",
        "project_manual_evaluation",
        "promote_accepted_result",
        "record_manual_evaluation",
        "record_technical_acceptance",
        "record_technical_rejection",
    }
)


def __getattr__(name: str):
    if name not in _SERVICE_EXPORTS:
        raise AttributeError(name)
    from relay_engine.manual_evaluation import service

    return getattr(service, name)


__all__ = [
    "AcceptedSliceResult",
    "DevelopmentMemoryProjection",
    "EvaluationEvidenceSubmission",
    "ManualEvaluationActionBasis",
    "ManualEvaluationActionKind",
    "ManualEvaluationConflict",
    "ManualEvaluationError",
    "ManualEvaluationForbidden",
    "ManualEvaluationInvalid",
    "ManualEvaluationNotAvailable",
    "ManualEvaluationProjection",
    "ManualEvaluationRecord",
    "ManualEvaluationStale",
    "SliceResultRecord",
]
