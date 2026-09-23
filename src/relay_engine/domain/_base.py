"""Shared immutable configuration for serialized domain values."""

from pathlib import PurePosixPath, PureWindowsPath
from typing import Literal

from pydantic import BaseModel, ConfigDict


class DomainModel(BaseModel):
    """Base for versioned, immutable, extra-forbid domain models."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        validate_default=True,
    )

    schema_version: Literal[1] = 1


def require_nonblank(value: str) -> str:
    """Reject empty or whitespace-only domain text without rewriting it."""

    if not value.strip():
        raise ValueError("value must not be blank")
    return value


def require_repository_relative_path(value: str) -> str:
    """Require a canonical POSIX path that cannot escape a repository root."""

    if not value or "\\" in value or any(ord(character) < 32 for character in value):
        raise ValueError("path must be a non-empty repository-relative POSIX path")

    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or not posix_path.parts
        or value != posix_path.as_posix()
        or any(part in {".", ".."} for part in posix_path.parts)
    ):
        raise ValueError("path must be canonical and remain inside the repository")

    return value
