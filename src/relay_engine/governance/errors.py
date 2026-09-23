"""Narrow public errors for handover governance."""


class GovernanceError(Exception):
    """Base class for governance operation failures."""


class InvalidGateSet(GovernanceError):
    """The supplied gates do not form one structurally valid outgoing set."""


class InvalidHandoverContext(GovernanceError):
    """Current context facts are ambiguous and cannot be interpreted deterministically."""


class HandoverNotExecutable(GovernanceError):
    """A selected handover is not GREEN or its authority is not yet causally valid."""
