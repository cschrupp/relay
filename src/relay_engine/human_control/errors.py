"""Typed failures at the Human Authority command boundary."""


class HumanActionError(Exception):
    """Base class for a rejected or unavailable Human action."""


class HumanActionNotAvailable(HumanActionError):
    """The requested action is not available for current durable state."""


class HumanActionBasisStale(HumanActionError):
    """The submitted action basis no longer matches durable state."""


class HumanActionConflict(HumanActionError):
    """A competing durable action won optimistic concurrency."""


class HumanActionRequiresEvaluation(HumanActionError):
    """A fresh durable gate evaluation is required before the action."""


class HumanActionInvalidChoice(HumanActionError):
    """The chosen gate is not in the exact current choice set."""


class HumanActionForbidden(HumanActionError):
    """The command actor is not a server-bound Human Authority."""


__all__ = [
    "HumanActionBasisStale",
    "HumanActionConflict",
    "HumanActionError",
    "HumanActionForbidden",
    "HumanActionInvalidChoice",
    "HumanActionNotAvailable",
    "HumanActionRequiresEvaluation",
]
