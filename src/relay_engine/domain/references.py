"""Provider-neutral identity and immutable commit references."""

import re
from enum import StrEnum

from pydantic import Field, field_validator

from relay_engine.domain._base import (
    DomainModel,
    require_nonblank,
    require_repository_relative_path,
)
from relay_engine.domain.ids import ActorId, RepositoryId


class ActorKind(StrEnum):
    HUMAN = "HUMAN"
    SYSTEM = "SYSTEM"
    AGENT = "AGENT"


class ActorRef(DomainModel):
    """Minimal stable identity for a human, system, or agent actor."""

    id: ActorId
    kind: ActorKind
    display_name: str | None = None

    @field_validator("display_name")
    @classmethod
    def display_name_is_nonblank(cls, value: str | None) -> str | None:
        return None if value is None else require_nonblank(value)


class RepositoryRef(DomainModel):
    """Provider-neutral Git repository identity, without credentials."""

    id: RepositoryId
    host: str = Field(min_length=1)
    path: str = Field(min_length=1)

    @field_validator("host")
    @classmethod
    def host_is_an_authority_only(cls, value: str) -> str:
        if (
            not value.strip()
            or any(character.isspace() for character in value)
            or any(token in value for token in ("://", "/", "@", "?", "#"))
        ):
            raise ValueError("host must be an authority name without scheme or credentials")
        return value

    @field_validator("path")
    @classmethod
    def path_is_repository_relative(cls, value: str) -> str:
        if value.endswith("/"):
            raise ValueError("repository path must identify a repository")
        return require_repository_relative_path(value)


class CommitRef(DomainModel):
    """Immutable identity of one exact commit in a repository."""

    repository: RepositoryRef
    sha: str = Field(pattern=r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")

    @field_validator("sha")
    @classmethod
    def sha_is_canonical(cls, value: str) -> str:
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
            raise ValueError("commit SHA must be a lowercase canonical 40- or 64-hex hash")
        return value
