"""Fixed-allowlist, read-only Git subprocess adapter for discovery."""

import os
import re
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from threading import Thread
from typing import BinaryIO
from urllib.parse import parse_qsl, urlsplit

MAX_GIT_STDOUT_BYTES = 64 * 1024 * 1024
MAX_GIT_STDERR_BYTES = 1024 * 1024
GIT_COMMAND_TIMEOUT_SECONDS = 30

_HEAD_SHA = re.compile(rb"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class GitOperation(StrEnum):
    """Closed set of Git operations permitted by this adapter."""

    TOP_LEVEL = "top_level"
    HEAD = "head"
    BRANCH = "branch"
    STATUS = "status"
    TRACKED_FILES = "tracked_files"
    REMOTES = "remotes"
    REMOTE_FETCH_URL = "remote_fetch_url"
    REMOTE_PUSH_URL = "remote_push_url"


class LocalGitError(RuntimeError):
    """A typed failure from the fixed local-Git inspection boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RemoteObservationData:
    name: str
    fetch_url: str | None
    push_url: str | None
    fetch_ambiguous: bool = False
    push_ambiguous: bool = False
    credentials_omitted: bool = False


@dataclass(frozen=True)
class LocalGitState:
    repository_root: Path
    head_sha: str
    branch: str | None
    dirty: bool
    tracked_paths: tuple[str, ...]
    remotes: tuple[RemoteObservationData, ...]


@dataclass(frozen=True)
class _CommandOutput:
    stdout: bytes
    returncode: int


@dataclass
class _ReadResult:
    data: bytearray
    exceeded_limit: bool = False


def inspect_local_git(repository: Path) -> LocalGitState:
    """Read the local repository state using only the fixed Git operation set."""

    repository_root = resolve_repository_root(repository)

    try:
        head_output = _run_git(repository_root, GitOperation.HEAD)
    except (_GitCommandFailure, LocalGitError) as error:
        raise LocalGitError("HEAD_UNRESOLVABLE", "Git HEAD could not be resolved") from error
    head_bytes = head_output.stdout.strip()
    if not _HEAD_SHA.fullmatch(head_bytes):
        raise LocalGitError("HEAD_UNRESOLVABLE", "Git returned a non-canonical HEAD value")
    head_sha = head_bytes.decode("ascii")

    try:
        branch_output = _run_git(repository_root, GitOperation.BRANCH)
        branch = os.fsdecode(branch_output.stdout.rstrip(b"\n"))
    except _GitCommandFailure as error:
        if error.returncode != 1:
            raise LocalGitError("GIT_COMMAND_FAILED", "Git branch observation failed") from error
        branch = None

    try:
        status_output = _run_git(repository_root, GitOperation.STATUS)
        tracked_output = _run_git(repository_root, GitOperation.TRACKED_FILES)
        remote_output = _run_git(repository_root, GitOperation.REMOTES)
    except (_GitCommandFailure, LocalGitError) as error:
        raise LocalGitError("GIT_COMMAND_FAILED", "Git repository observation failed") from error

    tracked_paths = _decode_tracked_paths(tracked_output.stdout)
    remotes = _read_remotes(repository_root, remote_output.stdout)
    return LocalGitState(
        repository_root=repository_root,
        head_sha=head_sha,
        branch=branch,
        dirty=bool(status_output.stdout),
        tracked_paths=tracked_paths,
        remotes=remotes,
    )


def resolve_repository_root(repository: Path) -> Path:
    """Resolve and return the real root of a local Git working tree."""

    try:
        requested_path = repository.expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise LocalGitError("NOT_GIT_REPOSITORY", "repository path is unavailable") from error
    if not requested_path.is_dir():
        raise LocalGitError("NOT_GIT_REPOSITORY", "repository path is not a directory")

    try:
        root_output = _run_git(requested_path, GitOperation.TOP_LEVEL)
    except LocalGitError as error:
        if error.code == "GIT_UNAVAILABLE":
            raise
        raise LocalGitError("NOT_GIT_REPOSITORY", "path is not inside a Git work tree") from error
    except _GitCommandFailure as error:
        raise LocalGitError("NOT_GIT_REPOSITORY", "path is not inside a Git work tree") from error

    root_text = os.fsdecode(root_output.stdout.rstrip(b"\n"))
    try:
        repository_root = Path(root_text).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise LocalGitError(
            "NOT_GIT_REPOSITORY", "Git returned an unavailable work-tree root"
        ) from error
    if not repository_root.is_dir():
        raise LocalGitError("NOT_GIT_REPOSITORY", "Git work-tree root is not a directory")
    return repository_root


class _GitCommandFailure(Exception):
    def __init__(self, returncode: int) -> None:
        super().__init__(f"Git exited with status {returncode}")
        self.returncode = returncode


def _run_git(
    repository_root: Path, operation: GitOperation, remote_name: str | None = None
) -> _CommandOutput:
    """Execute one enumerated Git command without a shell or unbounded capture."""

    args = _arguments(operation, remote_name)
    command = ["git", "-C", os.fspath(repository_root), *args]
    try:
        process = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=_git_environment(),
        )
    except (FileNotFoundError, PermissionError, OSError) as error:
        raise LocalGitError("GIT_UNAVAILABLE", "Git executable could not be started") from error

    if process.stdout is None or process.stderr is None:
        process.kill()
        process.wait()
        raise LocalGitError("GIT_UNAVAILABLE", "Git output streams could not be opened")

    stdout_result = _ReadResult(bytearray())
    stderr_result = _ReadResult(bytearray())
    stdout_thread = Thread(
        target=_drain_stream,
        args=(process.stdout, MAX_GIT_STDOUT_BYTES, stdout_result),
        daemon=True,
    )
    stderr_thread = Thread(
        target=_drain_stream,
        args=(process.stderr, MAX_GIT_STDERR_BYTES, stderr_result),
        daemon=True,
    )
    stdout_thread.start()
    stderr_thread.start()
    try:
        returncode = process.wait(timeout=GIT_COMMAND_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as error:
        process.kill()
        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        raise LocalGitError("GIT_COMMAND_TIMEOUT", "Git inspection command timed out") from error
    stdout_thread.join()
    stderr_thread.join()

    if stdout_result.exceeded_limit or stderr_result.exceeded_limit:
        raise LocalGitError("GIT_OUTPUT_TOO_LARGE", "Git inspection output exceeded its limit")
    if returncode != 0:
        raise _GitCommandFailure(returncode)
    return _CommandOutput(bytes(stdout_result.data), returncode)


def _arguments(operation: GitOperation, remote_name: str | None) -> list[str]:
    if operation is GitOperation.TOP_LEVEL:
        return ["rev-parse", "--show-toplevel"]
    if operation is GitOperation.HEAD:
        return ["rev-parse", "HEAD"]
    if operation is GitOperation.BRANCH:
        return ["symbolic-ref", "--quiet", "--short", "HEAD"]
    if operation is GitOperation.STATUS:
        return ["status", "--porcelain=v1"]
    if operation is GitOperation.TRACKED_FILES:
        return ["ls-files", "-z"]
    if operation is GitOperation.REMOTES:
        return ["remote"]
    if operation in {GitOperation.REMOTE_FETCH_URL, GitOperation.REMOTE_PUSH_URL}:
        if remote_name is None:
            raise ValueError("remote_name is required for remote URL observation")
        if operation is GitOperation.REMOTE_FETCH_URL:
            return ["remote", "get-url", "--", remote_name]
        return ["remote", "get-url", "--push", "--", remote_name]
    raise ValueError(f"unsupported Git operation: {operation}")


def _git_environment() -> dict[str, str]:
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.fsmonitor",
        "GIT_CONFIG_VALUE_0": "false",
        "LC_ALL": "C",
        "LANG": "C",
    }
    for name in ("SYSTEMROOT", "WINDIR", "PATHEXT"):
        value = os.environ.get(name)
        if value is not None:
            environment[name] = value
    return environment


def _drain_stream(stream: BinaryIO, limit: int, result: _ReadResult) -> None:
    while chunk := stream.read(64 * 1024):
        remaining = limit - len(result.data)
        if remaining > 0:
            result.data.extend(chunk[:remaining])
        if len(chunk) > remaining:
            result.exceeded_limit = True


def _decode_tracked_paths(raw: bytes) -> tuple[str, ...]:
    paths: list[str] = []
    for path_bytes in raw.split(b"\0"):
        if not path_bytes:
            continue
        relative_path = os.fsdecode(path_bytes)
        if Path(relative_path).is_absolute() or ".." in Path(relative_path).parts:
            raise LocalGitError("GIT_COMMAND_FAILED", "Git returned an unsafe tracked path")
        paths.append(relative_path.replace(os.sep, "/"))
    return tuple(sorted(set(paths)))


def _read_remotes(repository_root: Path, raw: bytes) -> tuple[RemoteObservationData, ...]:
    try:
        names = [line for line in os.fsdecode(raw).splitlines() if line]
    except UnicodeDecodeError as error:
        raise LocalGitError(
            "GIT_COMMAND_FAILED", "Git remote names could not be decoded"
        ) from error

    remotes: list[RemoteObservationData] = []
    for name in sorted(names):
        if not _safe_remote_name(name):
            remotes.append(
                RemoteObservationData(
                    name=name,
                    fetch_url=None,
                    push_url=None,
                    fetch_ambiguous=True,
                    push_ambiguous=True,
                )
            )
            continue
        fetch_url, fetch_ambiguous, fetch_credentialed = _read_remote_url(
            repository_root, name, GitOperation.REMOTE_FETCH_URL
        )
        push_url, push_ambiguous, push_credentialed = _read_remote_url(
            repository_root, name, GitOperation.REMOTE_PUSH_URL
        )
        remotes.append(
            RemoteObservationData(
                name=name,
                fetch_url=fetch_url,
                push_url=push_url,
                fetch_ambiguous=fetch_ambiguous,
                push_ambiguous=push_ambiguous,
                credentials_omitted=fetch_credentialed or push_credentialed,
            )
        )
    return tuple(remotes)


def _safe_remote_name(name: str) -> bool:
    return bool(name) and not name.startswith("-") and "\0" not in name and "\n" not in name


def _read_remote_url(
    repository_root: Path,
    remote_name: str,
    operation: GitOperation,
) -> tuple[str | None, bool, bool]:
    try:
        output = _run_git(repository_root, operation, remote_name)
    except _GitCommandFailure:
        return None, True, False
    except LocalGitError:
        return None, True, False
    values = [line for line in os.fsdecode(output.stdout).splitlines() if line]
    if len(values) != 1:
        return None, True, False
    url = values[0]
    if _url_may_contain_credentials(url):
        return None, False, True
    return url, False, False


def _url_may_contain_credentials(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        if parsed.scheme and parsed.netloc and parsed.username is not None:
            return True
        if "@" in value and not parsed.netloc:
            authority = value.split("/", 1)[0]
            if ":" in authority.rsplit("@", 1)[0]:
                return True
        sensitive_query_names = {
            "auth",
            "authorization",
            "credential",
            "key",
            "oauth",
            "password",
            "signature",
            "sig",
            "secret",
            "token",
            "access_token",
        }
        return any(name.lower() in sensitive_query_names for name, _ in parse_qsl(parsed.query))
    except ValueError:
        return True
