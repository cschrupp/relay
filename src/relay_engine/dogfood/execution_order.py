"""Deterministic dependency ordering dogfood target."""


class UnknownNodeError(ValueError):
    pass


class DependencyCycleError(ValueError):
    pass


def resolve_execution_order(
    requested: tuple[str, ...],
    prerequisites: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    raise NotImplementedError
