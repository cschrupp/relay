"""Explicit, type-readable domain identifier creation and validation types."""

from typing import Annotated, Literal
from uuid import uuid7

from pydantic import Field

type IdPrefix = Literal[
    "prj_",
    "repo_",
    "slc_",
    "base_",
    "art_",
    "dec_",
    "evd_",
    "act_",
]

_UUID_TEXT = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

type ProjectId = Annotated[str, Field(pattern=rf"^prj_{_UUID_TEXT}$")]
type RepositoryId = Annotated[str, Field(pattern=rf"^repo_{_UUID_TEXT}$")]
type SliceId = Annotated[str, Field(pattern=rf"^slc_{_UUID_TEXT}$")]
type BaselineId = Annotated[str, Field(pattern=rf"^base_{_UUID_TEXT}$")]
type ArtifactId = Annotated[str, Field(pattern=rf"^art_{_UUID_TEXT}$")]
type DecisionId = Annotated[str, Field(pattern=rf"^dec_{_UUID_TEXT}$")]
type EvidenceId = Annotated[str, Field(pattern=rf"^evd_{_UUID_TEXT}$")]
type ActorId = Annotated[str, Field(pattern=rf"^act_{_UUID_TEXT}$")]


def new_id(prefix: IdPrefix) -> str:
    """Create a type-readable UUIDv7 identifier explicitly at the call site."""

    if prefix not in ("prj_", "repo_", "slc_", "base_", "art_", "dec_", "evd_", "act_"):
        raise ValueError("unsupported domain identifier prefix")
    return f"{prefix}{uuid7()}"
