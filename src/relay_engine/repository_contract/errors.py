"""Errors raised at repository-contract validation and resolution boundaries."""


class RepositoryContractError(Exception):
    """Base class for repository-contract failures."""


class RepositoryContractInvalid(RepositoryContractError):
    """The registry or repository snapshot violates the schema-v1 contract."""


class ArtifactIntegrityError(RepositoryContractError):
    """A registered artifact is missing, unsafe, or has different exact bytes."""


class CanonicalResolutionError(RepositoryContractError):
    """A canonical or exact artifact reference cannot be resolved."""
