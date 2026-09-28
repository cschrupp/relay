"""Strict provider-neutral values for repository baseline resolution."""

import re
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from relay_engine.domain._base import DomainModel, require_nonblank
from relay_engine.domain.ids import ArtifactId, BaselineId, ProjectId
from relay_engine.domain.references import CommitRef, RepositoryRef


class RepositoryRevisionKind(StrEnum):
    BRANCH = "BRANCH"
    TAG = "TAG"
    COMMIT_SHA = "COMMIT_SHA"


class RepositoryRevisionSelector(DomainModel):
    kind: RepositoryRevisionKind
    value: str = Field(min_length=1)

    @field_validator("value")
    @classmethod
    def value_is_nonblank(cls, value: str) -> str:
        return require_nonblank(value)

    @model_validator(mode="after")
    def selector_is_explicit_and_canonical(self) -> "RepositoryRevisionSelector":
        if self.kind is RepositoryRevisionKind.BRANCH:
            if self.value.startswith("refs/heads/"):
                raise ValueError("branch selector must omit refs/heads/ prefix")
        elif self.kind is RepositoryRevisionKind.TAG:
            if self.value.startswith("refs/tags/"):
                raise ValueError("tag selector must omit refs/tags/ prefix")
        elif not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", self.value):
            raise ValueError("commit selector must be a full canonical lowercase SHA")
        return self


class ResolvedBaselineResult(DomainModel):
    project_id: ProjectId
    repository: RepositoryRef
    selector: RepositoryRevisionSelector
    commit: CommitRef
    baseline_id: BaselineId
    artifact_ids: tuple[ArtifactId, ...]

    @field_validator("artifact_ids")
    @classmethod
    def artifact_ids_are_unique(cls, value: tuple[ArtifactId, ...]) -> tuple[ArtifactId, ...]:
        if len(value) != len(set(value)):
            raise ValueError("resolved baseline artifact IDs must be unique")
        return value
