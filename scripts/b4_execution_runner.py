"""Prepare, validate, and seal deterministic evidence for B4 Revision 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

QUESTION_SET_ID = "B4-R2-QSET-001"
QUESTION_CONTRACT_RELATIVE_PATH = Path("scripts/b4_question_contract_v1.json")
REGISTRY_RELATIVE_PATH = Path(".relay/registry.json")
HARNESS_RELATIVE_PATH = Path("scripts/b4_readonly_harness.py")
HARNESS_TEST_RELATIVE_PATH = Path("tests/integration/test_b4_readonly_harness.py")
CHILD_REAP_TIMEOUT_SECONDS = 5
PREPARE_OUTCOMES = {
    "PREPARED",
    "INVALID_PRECHECK",
    "INVALID_CAPTURE_SETUP",
    "INVALID_HARNESS_SPAWN",
    "INVALID_HARNESS_EXIT",
    "INVALID_HARNESS_OUTPUT",
    "INVALID_HARNESS_PROTOCOL",
    "INVALID_PREPARE_EVIDENCE",
}
ANSWER_TOP_LEVEL_FIELDS = {
    "schema_version",
    "authority_id",
    "run_id",
    "question_set_id",
    "question_contract_sha256",
    "cold_start_declaration",
    "operator_identity",
    "runtime_identity",
    "model_identity",
    "inspected_sources",
    "prohibited_sources_accessed",
    "answers",
    "completed_at",
}
ANSWER_FIELDS = {
    "question_id",
    "question_text",
    "answer",
    "source_class",
    "source_locators",
    "relevant_fields_or_records",
    "not_determinable",
}
RESPONSE_SCHEMA_FIELDS = {
    "answer",
    "source_class",
    "source_locators",
    "relevant_fields_or_records",
    "not_determinable",
}
ANSWER_SCHEMA = {
    "schema_version": 1,
    "fields": {
        "schema_version": "integer: 1",
        "authority_id": "nonblank string",
        "run_id": "nonblank string",
        "question_set_id": "nonblank string",
        "question_contract_sha256": "64-character lowercase SHA-256 string",
        "cold_start_declaration": "nonblank string",
        "operator_identity": "nonblank string",
        "runtime_identity": "nonblank string",
        "model_identity": "nonblank string or null",
        "inspected_sources": "non-empty array of nonblank strings",
        "prohibited_sources_accessed": "array of nonblank strings; may be empty",
        "answers": "array of exactly ten answer objects in Q1 through Q10 order",
        "completed_at": "nonblank UTC timestamp string",
    },
    "answer_fields": {
        "question_id": "canonical Q1 through Q10 identifier",
        "question_text": "exact text from B4QuestionContractV1",
        "answer": "nonblank string",
        "source_class": "array of nonblank strings",
        "source_locators": "array of nonblank strings",
        "relevant_fields_or_records": "array of nonblank strings",
        "not_determinable": "boolean",
    },
    "required_top_level_fields": sorted(ANSWER_TOP_LEVEL_FIELDS),
    "required_answer_fields": sorted(ANSWER_FIELDS),
    "answer_count": 10,
    "instructions": [
        "Answer Q1 through Q10 using the pinned repository and captured read-only projection.",
        "Record source classes, source locators, and relevant fields or records for each answer.",
        (
            "Set not_determinable to true only when the answer is not established by the "
            "permitted durable state."
        ),
        "Declare inspected and prohibited sources in this answer set.",
        "Do not include semantic scores or evaluator judgments.",
    ],
}
COLD_START_DECLARATION = (
    "I am a fresh operator who did not participate in the prior Relay planning conversation. "
    "I have not received prior B4 answers, evaluations, expected factual answers, or private "
    "evaluator notes. I will use only the permitted sources at the pinned checkout and record "
    "the sources I inspect."
)
SOURCE_PRECEDENCE = [
    "Pinned operational database and existing read models establish current runtime state.",
    "Accepted immutable governance records establish prior authority and decisions.",
    (
        "Registry-resolved canonical repository projections establish recorded governance "
        "and roadmap context."
    ),
    "Repository code and product help explain behavior and field meaning only.",
    "Captured harness JSON is an allowed current-state projection.",
    (
        "External evidence is allowed only when a permitted pinned record names its exact "
        "path and digest."
    ),
]
ALLOWED_SOURCE_RULES = [
    "The pinned repository registry and its registry-resolved canonical documents.",
    "Accepted immutable governance records discoverable from allowed canonical records.",
    "Repository code and product help for behavior and field meaning only.",
    "The exact captured read-only harness JSON.",
    "External evidence only when a permitted record names its exact path and digest.",
]
PROHIBITED_SOURCE_RULES = [
    "Prior Relay or ChatGPT conversation history.",
    "Prior B4 answers, evidence packets, evaluations, or question outcomes.",
    (
        "Reconstructed project summaries, evaluator answer keys, expected factual answers, "
        "or private evaluator notes."
    ),
    "Repository state later than the pinned execution checkout.",
]


class RunnerFailure(Exception):
    """A controlled fail-closed protocol error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize runner-owned JSON in the one canonical representation."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json_bytes(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
        raise RunnerFailure(
            "INVALID_JSON", f"{label} is not valid duplicate-free UTF-8 JSON"
        ) from error


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _resolve_path(value: str | Path, root: Path) -> Path:
    candidate = Path(value).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    return candidate.resolve(strict=False)


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RunnerFailure("GIT_OBSERVATION_FAILED", "a required Git observation failed")
    return result.stdout.strip()


def _empty_file_record(path: Path | None) -> dict[str, Any]:
    return {
        "path": None if path is None else str(path),
        "exists": False,
        "size": None,
        "sha256": None,
    }


def _file_record(path: Path) -> dict[str, Any]:
    if not os.path.lexists(path):
        return _empty_file_record(path)
    raw = path.read_bytes()
    return {"path": str(path), "exists": True, "size": len(raw), "sha256": _sha256_bytes(raw)}


def _sidecar_records(database_path: Path) -> list[dict[str, Any]]:
    records = []
    for suffix in ("-wal", "-shm"):
        path = Path(f"{database_path}{suffix}")
        if not os.path.lexists(path):
            records.append(
                {"path": str(path), "exists": False, "size": None, "mtime_ns": None, "sha256": None}
            )
            continue
        stat = path.stat()
        records.append(
            {
                "path": str(path),
                "exists": True,
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "sha256": _sha256_file(path),
            }
        )
    return records


def _base_result(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.execution_root).expanduser().resolve(strict=False)

    def resolved_argument(name: str) -> str | None:
        value = getattr(args, name, None)
        if value is None:
            return None
        return str(_resolve_path(value, root))

    return {
        "schema_version": 1,
        "authority_id": args.authority_id,
        "run_id": args.run_id,
        "attempt_number": args.attempt_number,
        "execution_root": str(root),
        "expected_head": args.expected_head,
        "observed_git_root": None,
        "project_id": args.project_id,
        "slice_id": args.slice_id,
        "observed_head": None,
        "worktree_clean": None,
        "harness_path": resolved_argument("harness_path"),
        "expected_harness_blob": args.expected_harness_blob,
        "observed_harness_blob": None,
        "harness_test_path": resolved_argument("harness_test_path"),
        "expected_harness_test_blob": args.expected_harness_test_blob,
        "observed_harness_test_blob": None,
        "database_path": resolved_argument("database_path"),
        "expected_db_sha256": args.expected_db_sha256,
        "db_sha256_before": None,
        "sidecars_before": [],
        "question_contract_path": resolved_argument("question_contract_path"),
        "question_set_id": QUESTION_SET_ID,
        "expected_question_contract_sha256": args.expected_question_contract_sha256,
        "question_contract_sha256": None,
        "registry_path": None,
        "registry_sha256": None,
        "current_living_projections": [],
        "prepare_result_path": resolved_argument("prepare_result_path"),
        "prepare_manifest_path": resolved_argument("prepare_manifest_path"),
        "operator_input_path": resolved_argument("operator_input_path"),
        "answer_set_path": resolved_argument("answer_set_path"),
        "terminal_evidence_path": resolved_argument("terminal_evidence_path"),
        "execution_started": False,
        "harness_invocation_count": 0,
        "harness_exit_code": None,
        "harness_command": None,
        "stdout_capture_exclusive_created": None,
        "stderr_capture_exclusive_created": None,
        "observed_query_only": None,
        "observed_relay_schema_version": None,
        "stdout": _empty_file_record(resolved_argument("stdout_path")),
        "stderr": _empty_file_record(resolved_argument("stderr_path")),
        "validation": {
            "stdout_nonempty": "NOT_PERFORMED",
            "stdout_json_valid": "NOT_PERFORMED",
            "query_only_valid": "NOT_PERFORMED",
            "relay_schema_version_valid": "NOT_PERFORMED",
        },
        "failure_stage": None,
        "failure_code": None,
        "prepare_outcome": None,
        "recorded_at": None,
    }


def _validate_question_contract(raw: bytes, expected_digest: str) -> tuple[dict[str, Any], str]:
    digest = _sha256_bytes(raw)
    if digest != expected_digest:
        raise RunnerFailure("QUESTION_CONTRACT_DIGEST_MISMATCH", "question contract digest differs")
    contract = _read_json_bytes(raw, "question contract")
    if not isinstance(contract, dict) or set(contract) != {
        "schema_version",
        "question_set_id",
        "questions",
    }:
        raise RunnerFailure(
            "INVALID_QUESTION_CONTRACT", "question contract top-level fields are invalid"
        )
    if (
        type(contract["schema_version"]) is not int
        or contract["schema_version"] != 1
        or contract["question_set_id"] != QUESTION_SET_ID
    ):
        raise RunnerFailure("INVALID_QUESTION_CONTRACT", "question contract identity is invalid")
    questions = contract["questions"]
    if not isinstance(questions, list) or len(questions) != 10:
        raise RunnerFailure(
            "INVALID_QUESTION_CONTRACT", "question contract must contain ten questions"
        )
    expected_ids = [f"Q{index}" for index in range(1, 11)]
    for question, expected_id in zip(questions, expected_ids, strict=True):
        if not isinstance(question, dict) or set(question) != {
            "question_id",
            "question_text",
            "required_dimensions",
            "response_schema",
        }:
            raise RunnerFailure("INVALID_QUESTION_CONTRACT", "question entry fields are invalid")
        if question["question_id"] != expected_id:
            raise RunnerFailure(
                "INVALID_QUESTION_CONTRACT", "question IDs must be ordered Q1 through Q10"
            )
        if not isinstance(question["question_text"], str) or not question["question_text"].strip():
            raise RunnerFailure("INVALID_QUESTION_CONTRACT", "question text must be nonblank")
        dimensions = question["required_dimensions"]
        if (
            not isinstance(dimensions, list)
            or not dimensions
            or any(
                not isinstance(dimension, str) or not dimension.strip() for dimension in dimensions
            )
        ):
            raise RunnerFailure(
                "INVALID_QUESTION_CONTRACT", "required dimensions must be non-empty strings"
            )
        response_schema = question["response_schema"]
        if not isinstance(response_schema, dict) or set(response_schema) != RESPONSE_SCHEMA_FIELDS:
            raise RunnerFailure("INVALID_QUESTION_CONTRACT", "response schema fields are invalid")
        for field, schema in response_schema.items():
            if not isinstance(schema, dict) or schema.get("required") is not True:
                raise RunnerFailure("INVALID_QUESTION_CONTRACT", "response schema field is invalid")
            if field in {"source_class", "source_locators", "relevant_fields_or_records"}:
                if schema.get("type") != "array" or schema.get("items") != {"type": "string"}:
                    raise RunnerFailure(
                        "INVALID_QUESTION_CONTRACT", "response list schema is invalid"
                    )
            elif schema.get("type") != ("boolean" if field == "not_determinable" else "string"):
                raise RunnerFailure(
                    "INVALID_QUESTION_CONTRACT", "response scalar schema is invalid"
                )
    if canonical_json_bytes(contract) != raw:
        raise RunnerFailure(
            "NONCANONICAL_QUESTION_CONTRACT", "question contract bytes are not canonical"
        )
    return contract, digest


def _registry_projections(root: Path) -> tuple[str, list[dict[str, Any]]]:
    registry_path = root / REGISTRY_RELATIVE_PATH
    raw = registry_path.read_bytes()
    registry = _read_json_bytes(raw, "repository registry")
    entries = registry.get("artifacts") if isinstance(registry, dict) else None
    if not isinstance(entries, list):
        raise RunnerFailure("INVALID_REGISTRY", "repository registry artifact list is invalid")
    projections = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if (
            entry.get("artifact_class") == "LIVING_PROJECTION"
            and entry.get("artifact_state") == "CURRENT"
        ):
            projections.append(
                {
                    key: entry.get(key)
                    for key in ("artifact_id", "path", "revision", "content_digest", "title")
                }
            )
    return _sha256_bytes(raw), projections


def _validate_path_inputs(
    args: argparse.Namespace, root: Path, database_path: Path
) -> dict[str, Path]:
    names = (
        "stdout_path",
        "stderr_path",
        "prepare_result_path",
        "prepare_manifest_path",
        "operator_input_path",
        "answer_set_path",
        "terminal_evidence_path",
    )
    lexical_paths: dict[str, Path] = {}
    outputs: dict[str, Path] = {}
    for name in names:
        candidate = Path(getattr(args, name)).expanduser()
        if not candidate.is_absolute():
            candidate = root / candidate
        lexical = Path(os.path.abspath(candidate))
        lexical_paths[name] = lexical
        outputs[name] = candidate.resolve(strict=False)
    if len(set(outputs.values())) != len(outputs):
        raise RunnerFailure(
            "OUTPUT_PATH_COLLISION", "runner output paths must be pairwise distinct"
        )
    forbidden = {
        database_path,
        Path(f"{database_path}-wal"),
        Path(f"{database_path}-shm"),
    }
    for name, path in outputs.items():
        lexical = lexical_paths[name]
        if _path_is_within(path, root) or _path_is_within(lexical, root):
            raise RunnerFailure(
                "OUTPUT_PATH_IN_REPOSITORY", "runner evidence path is inside execution repository"
            )
        if path in forbidden:
            raise RunnerFailure(
                "OUTPUT_PATH_DATABASE_COLLISION", "runner output path collides with DB or sidecar"
            )
        if not path.parent.is_dir():
            raise RunnerFailure(
                "OUTPUT_PARENT_MISSING", "runner evidence parent directory does not exist"
            )
        if os.path.lexists(lexical):
            raise RunnerFailure("OUTPUT_TARGET_EXISTS", "runner output target already exists")
    return outputs


def _preflight(
    args: argparse.Namespace, result: dict[str, Any]
) -> tuple[Path, dict[str, Path], dict[str, Any], list[dict[str, Any]]]:
    root = Path(args.execution_root).expanduser().resolve(strict=True)
    result["execution_root"] = str(root)
    if not root.is_dir():
        raise RunnerFailure("EXECUTION_ROOT_INVALID", "execution root must be a directory")
    observed_root = Path(_git(root, "rev-parse", "--show-toplevel")).resolve(strict=True)
    result["observed_git_root"] = str(observed_root)
    if observed_root != root:
        raise RunnerFailure("EXECUTION_ROOT_MISMATCH", "execution root differs from Git top-level")
    observed_head = _git(root, "rev-parse", "HEAD")
    result["observed_head"] = observed_head
    if observed_head != args.expected_head:
        raise RunnerFailure("HEAD_MISMATCH", "Git HEAD differs from expected head")
    clean = _git(root, "status", "--porcelain") == ""
    result["worktree_clean"] = clean
    if not clean:
        raise RunnerFailure("WORKTREE_DIRTY", "execution worktree is not clean")

    observed_blobs: dict[str, Any] = {}
    for argument_name, expected_name, field_name in (
        ("harness_path", "expected_harness_blob", "observed_harness_blob"),
        ("harness_test_path", "expected_harness_test_blob", "observed_harness_test_blob"),
    ):
        path = _resolve_path(getattr(args, argument_name), root)
        if not _path_is_within(path, root):
            raise RunnerFailure(
                "HARNESS_PATH_OUTSIDE_REPOSITORY", "harness paths must be inside execution root"
            )
        relative = path.relative_to(root).as_posix()
        blob = _git(root, "rev-parse", f"HEAD:{relative}")
        result[field_name] = blob
        observed_blobs[argument_name] = blob
        if blob != getattr(args, expected_name):
            raise RunnerFailure("GIT_BLOB_MISMATCH", f"Git blob identity differs for {relative}")

    database_path = _resolve_path(args.database_path, root)
    result["database_path"] = str(database_path)
    if not database_path.is_file():
        raise RunnerFailure("DATABASE_MISSING", "pinned database path is not an existing file")
    db_digest = _sha256_file(database_path)
    result["db_sha256_before"] = db_digest
    result["sidecars_before"] = _sidecar_records(database_path)
    if db_digest != args.expected_db_sha256:
        raise RunnerFailure(
            "DATABASE_DIGEST_MISMATCH", "database digest differs from expected value"
        )

    contract_path = _resolve_path(args.question_contract_path, root)
    result["question_contract_path"] = str(contract_path)
    if (
        contract_path != root / QUESTION_CONTRACT_RELATIVE_PATH
        or not _path_is_within(contract_path, root)
        or not contract_path.is_file()
    ):
        raise RunnerFailure(
            "QUESTION_CONTRACT_PATH_INVALID", "question contract must be a file in execution root"
        )
    raw_contract = contract_path.read_bytes()
    contract, contract_digest = _validate_question_contract(
        raw_contract, args.expected_question_contract_sha256
    )
    result["question_contract_sha256"] = contract_digest

    registry_sha256, projections = _registry_projections(root)
    result["registry_path"] = str(root / REGISTRY_RELATIVE_PATH)
    result["registry_sha256"] = registry_sha256
    result["current_living_projections"] = projections
    outputs = _validate_path_inputs(args, root, database_path)
    return (
        root,
        outputs,
        contract,
        [{"registry_sha256": registry_sha256, "current_living_projections": projections}],
    )


def _fsync_and_close(handle: Any) -> None:
    if handle.closed:
        return
    handle.flush()
    os.fsync(handle.fileno())
    handle.close()


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive(path: Path, raw: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as target:
            target.write(raw)
            target.flush()
            os.fsync(target.fileno())
    finally:
        os.close(descriptor)
    _fsync_directory(path.parent)


def _write_result_if_safe(args: argparse.Namespace, result: dict[str, Any]) -> bool:
    root = Path(args.execution_root).expanduser().resolve(strict=False)
    candidate = Path(args.prepare_result_path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    lexical_path = Path(os.path.abspath(candidate))
    path = candidate.resolve(strict=False)
    database = _resolve_path(args.database_path, root)
    other_outputs = {
        _resolve_path(getattr(args, name), root)
        for name in (
            "stdout_path",
            "stderr_path",
            "prepare_manifest_path",
            "operator_input_path",
            "answer_set_path",
            "terminal_evidence_path",
        )
    }
    repository_roots = {root}
    if root.is_dir():
        with suppress(OSError, RunnerFailure):
            repository_roots.add(
                Path(_git(root, "rev-parse", "--show-toplevel")).resolve(strict=True)
            )
    if (
        not path.parent.is_dir()
        or any(
            _path_is_within(candidate, repository_root)
            for candidate in (path, lexical_path)
            for repository_root in repository_roots
        )
        or path in {database, Path(f"{database}-wal"), Path(f"{database}-shm")}
        or path in other_outputs
        or os.path.lexists(lexical_path)
    ):
        return False
    result["recorded_at"] = _timestamp()
    try:
        _write_exclusive(path, canonical_json_bytes(result))
    except OSError:
        return False
    return True


def _fail_prepare(
    args: argparse.Namespace, result: dict[str, Any], outcome: str, stage: str, code: str
) -> int:
    result["prepare_outcome"] = outcome
    result["failure_stage"] = stage
    result["failure_code"] = code
    persisted = _write_result_if_safe(args, result)
    if not persisted:
        print(
            canonical_json_bytes(
                {
                    "prepare_outcome": "INVALID_PREPARE_EVIDENCE",
                    "failure_code": "PREPARE_RESULT_WRITE_FAILED",
                    "underlying_failure_code": code,
                }
            ).decode(),
            end="",
            file=sys.stderr,
        )
    else:
        print(
            canonical_json_bytes({"prepare_outcome": outcome, "failure_code": code}).decode(),
            end="",
        )
    return 2


def _capture_handle(path: Path) -> Any:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.fsync(descriptor)
        _fsync_directory(path.parent)
        return os.fdopen(descriptor, "wb")
    except OSError:
        os.close(descriptor)
        raise


def _close_capture_pair(stdout_handle: Any, stderr_handle: Any) -> bool:
    successful = True
    for handle in (stdout_handle, stderr_handle):
        try:
            _fsync_and_close(handle)
        except OSError:
            successful = False
            with suppress(OSError):
                handle.close()
    return successful


def _terminate_and_reap(child: Any) -> tuple[bool, int | None]:
    """Stop and reap a child using one bounded wait after its first wait fails."""
    try:
        return_code = child.poll()
    except OSError:
        return_code = None
    if return_code is not None:
        return True, return_code

    with suppress(OSError):
        child.kill()

    try:
        return True, child.wait(timeout=CHILD_REAP_TIMEOUT_SECONDS)
    except OSError, subprocess.TimeoutExpired:
        try:
            return_code = child.poll()
        except OSError:
            return False, None
        if return_code is None:
            return False, None
        return True, return_code


def _contract_questions(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return contract["questions"]


def _operator_envelope(
    args: argparse.Namespace,
    root: Path,
    contract: dict[str, Any],
    result: dict[str, Any],
    registry: dict[str, Any],
    outputs: dict[str, Path],
) -> dict[str, Any]:
    stdout_record = result["stdout"]
    return {
        "schema_version": 1,
        "authority_id": args.authority_id,
        "run_id": args.run_id,
        "attempt_number": args.attempt_number,
        "cold_start_declaration": COLD_START_DECLARATION,
        "source_precedence": SOURCE_PRECEDENCE,
        "allowed_source_rules": ALLOWED_SOURCE_RULES,
        "prohibited_source_rules": PROHIBITED_SOURCE_RULES,
        "execution_checkout": {
            "execution_root": str(root),
            "head": args.expected_head,
        },
        "harness_capture": {
            "stdout_path": stdout_record["path"],
            "stdout_sha256": stdout_record["sha256"],
            "stderr_path": result["stderr"]["path"],
            "stderr_sha256": result["stderr"]["sha256"],
        },
        "registry": {
            "path": str(root / REGISTRY_RELATIVE_PATH),
            **registry,
        },
        "question_contract": contract,
        "question_contract_path": result["question_contract_path"],
        "question_contract_sha256": result["question_contract_sha256"],
        "answer_set_schema": ANSWER_SCHEMA,
        "answer_set_destination": str(outputs["answer_set_path"]),
    }


def prepare(args: argparse.Namespace) -> int:
    result = _base_result(args)
    try:
        root, outputs, contract, registry_records = _preflight(args, result)
    except (OSError, RunnerFailure, ValueError) as error:
        code = error.code if isinstance(error, RunnerFailure) else "PREFLIGHT_FAILED"
        return _fail_prepare(args, result, "INVALID_PRECHECK", "precheck", code)

    result_path = outputs["prepare_result_path"]
    stdout_handle = None
    stderr_handle = None
    try:
        stdout_handle = _capture_handle(outputs["stdout_path"])
        result["stdout"] = _empty_file_record(outputs["stdout_path"])
        result["stdout_capture_exclusive_created"] = True
        stderr_handle = _capture_handle(outputs["stderr_path"])
        result["stderr"] = _empty_file_record(outputs["stderr_path"])
        result["stderr_capture_exclusive_created"] = True
    except OSError:
        if stdout_handle is not None and stderr_handle is not None:
            _close_capture_pair(stdout_handle, stderr_handle)
        elif stdout_handle is not None:
            try:
                _fsync_and_close(stdout_handle)
            except OSError:
                stdout_handle.close()
        result["stdout"] = _file_record(outputs["stdout_path"])
        result["stderr"] = _file_record(outputs["stderr_path"])
        result["stdout_capture_exclusive_created"] = stdout_handle is not None
        result["stderr_capture_exclusive_created"] = stderr_handle is not None
        return _fail_prepare(
            args, result, "INVALID_CAPTURE_SETUP", "capture_setup", "CAPTURE_CREATE_FAILED"
        )

    harness_path = _resolve_path(args.harness_path, root)
    database_path = _resolve_path(args.database_path, root)
    command = [
        sys.executable,
        str(harness_path),
        "--database",
        str(database_path),
        "--project-id",
        args.project_id,
        "--slice-id",
        args.slice_id,
    ]
    result["harness_command"] = command
    try:
        child = subprocess.Popen(command, cwd=root, stdout=stdout_handle, stderr=stderr_handle)
    except OSError:
        captures_durable = _close_capture_pair(stdout_handle, stderr_handle)
        result["stdout"] = _file_record(outputs["stdout_path"])
        result["stderr"] = _file_record(outputs["stderr_path"])
        if not captures_durable:
            return _fail_prepare(
                args,
                result,
                "INVALID_PREPARE_EVIDENCE",
                "capture_durability",
                "CAPTURE_FSYNC_FAILED",
            )
        return _fail_prepare(
            args,
            result,
            "INVALID_HARNESS_SPAWN",
            "spawn",
            "HARNESS_PROCESS_CREATION_FAILED",
        )

    result["execution_started"] = True
    result["harness_invocation_count"] = 1
    wait_error = False
    try:
        result["harness_exit_code"] = child.wait()
    except OSError:
        wait_error = True
        child_terminated, return_code = _terminate_and_reap(child)
        if child_terminated:
            result["harness_exit_code"] = return_code
        else:
            _close_capture_pair(stdout_handle, stderr_handle)
            result["stdout"] = {
                "path": str(outputs["stdout_path"]),
                "exists": True,
                "size": None,
                "sha256": None,
            }
            result["stderr"] = {
                "path": str(outputs["stderr_path"]),
                "exists": True,
                "size": None,
                "sha256": None,
            }
            return _fail_prepare(
                args,
                result,
                "INVALID_PREPARE_EVIDENCE",
                "wait",
                "CHILD_TERMINATION_UNCONFIRMED",
            )
    captures_durable = _close_capture_pair(stdout_handle, stderr_handle)
    try:
        result["stdout"] = _file_record(outputs["stdout_path"])
        result["stderr"] = _file_record(outputs["stderr_path"])
        stdout_bytes = outputs["stdout_path"].read_bytes()
    except OSError:
        return _fail_prepare(
            args,
            result,
            "INVALID_PREPARE_EVIDENCE",
            "capture_hash",
            "CAPTURE_HASH_FAILED",
        )
    result["validation"]["stdout_nonempty"] = "PASS" if stdout_bytes else "FAIL"
    decoded: Any = None
    try:
        decoded = _read_json_bytes(stdout_bytes, "harness stdout")
        result["validation"]["stdout_json_valid"] = "PASS"
    except RunnerFailure:
        result["validation"]["stdout_json_valid"] = "FAIL"

    query_only_ok = False
    schema_ok = False
    if isinstance(decoded, dict):
        result["observed_query_only"] = decoded.get("query_only")
        result["observed_relay_schema_version"] = decoded.get("schema_version")
        query_only_ok = type(decoded.get("query_only")) is int and decoded.get("query_only") == 1
        schema_ok = (
            type(decoded.get("schema_version")) is int and decoded.get("schema_version") == 8
        )
        result["validation"]["query_only_valid"] = "PASS" if query_only_ok else "FAIL"
        result["validation"]["relay_schema_version_valid"] = "PASS" if schema_ok else "FAIL"

    exit_code = result["harness_exit_code"]
    if wait_error:
        return _fail_prepare(args, result, "INVALID_HARNESS_EXIT", "wait", "HARNESS_WAIT_FAILED")
    if not captures_durable:
        return _fail_prepare(
            args,
            result,
            "INVALID_PREPARE_EVIDENCE",
            "capture_durability",
            "CAPTURE_FSYNC_FAILED",
        )
    if exit_code != 0:
        return _fail_prepare(
            args, result, "INVALID_HARNESS_EXIT", "child_exit", "HARNESS_NONZERO_EXIT"
        )
    if not stdout_bytes or result["validation"]["stdout_json_valid"] != "PASS":
        return _fail_prepare(
            args, result, "INVALID_HARNESS_OUTPUT", "output", "HARNESS_OUTPUT_INVALID"
        )
    if not query_only_ok or not schema_ok:
        return _fail_prepare(
            args, result, "INVALID_HARNESS_PROTOCOL", "protocol", "HARNESS_PROTOCOL_MISMATCH"
        )

    result["prepare_outcome"] = "PREPARED"
    result["recorded_at"] = _timestamp()
    try:
        _write_exclusive(result_path, canonical_json_bytes(result))
    except OSError:
        print(
            canonical_json_bytes(
                {
                    "prepare_outcome": "INVALID_PREPARE_EVIDENCE",
                    "failure_code": "PREPARE_RESULT_WRITE_FAILED",
                }
            ).decode(),
            end="",
            file=sys.stderr,
        )
        return 2
    result_digest = _sha256_file(result_path)
    registry = registry_records[0]
    manifest = {
        "schema_version": 1,
        "authority_id": args.authority_id,
        "run_id": args.run_id,
        "attempt_number": args.attempt_number,
        "execution_root": str(root),
        "prepare_manifest_path": str(outputs["prepare_manifest_path"]),
        "expected_head": args.expected_head,
        "observed_head": result["observed_head"],
        "observed_git_root": result["observed_git_root"],
        "worktree_clean": result["worktree_clean"],
        "harness_path": result["harness_path"],
        "expected_harness_blob": result["expected_harness_blob"],
        "observed_harness_blob": result["observed_harness_blob"],
        "harness_test_path": result["harness_test_path"],
        "expected_harness_test_blob": result["expected_harness_test_blob"],
        "observed_harness_test_blob": result["observed_harness_test_blob"],
        "prepare_result_path": str(result_path),
        "prepare_result_sha256": result_digest,
        "harness_command": result["harness_command"],
        "harness_invocation_count": result["harness_invocation_count"],
        "harness_exit_code": result["harness_exit_code"],
        "stdout_exclusive_create": result["stdout_capture_exclusive_created"],
        "stderr_exclusive_create": result["stderr_capture_exclusive_created"],
        "stdout_path": result["stdout"]["path"],
        "stdout_sha256": result["stdout"]["sha256"],
        "stdout_size": result["stdout"]["size"],
        "stderr_path": result["stderr"]["path"],
        "stderr_sha256": result["stderr"]["sha256"],
        "stderr_size": result["stderr"]["size"],
        "database_path": result["database_path"],
        "expected_db_sha256": result["expected_db_sha256"],
        "db_sha256_before": result["db_sha256_before"],
        "sidecars_before": result["sidecars_before"],
        "project_id": args.project_id,
        "slice_id": args.slice_id,
        "question_contract_path": result["question_contract_path"],
        "question_set_id": QUESTION_SET_ID,
        "question_contract_sha256": result["question_contract_sha256"],
        "registry_path": str(root / REGISTRY_RELATIVE_PATH),
        "registry_sha256": registry["registry_sha256"],
        "current_living_projections": registry["current_living_projections"],
        "stdout_json_valid": result["validation"]["stdout_json_valid"],
        "query_only_valid": result["validation"]["query_only_valid"],
        "relay_schema_version_valid": result["validation"]["relay_schema_version_valid"],
        "query_only": result["observed_query_only"],
        "relay_schema_version": result["observed_relay_schema_version"],
        "prepare_status": result["prepare_outcome"],
        "operator_input_path": str(outputs["operator_input_path"]),
        "answer_set_path": str(outputs["answer_set_path"]),
        "terminal_evidence_path": str(outputs["terminal_evidence_path"]),
        "prepared_at": _timestamp(),
    }
    try:
        _write_exclusive(outputs["prepare_manifest_path"], canonical_json_bytes(manifest))
        envelope = _operator_envelope(args, root, contract, result, registry, outputs)
        _write_exclusive(outputs["operator_input_path"], canonical_json_bytes(envelope))
    except OSError:
        print(
            "B4 prepare stopped after PREPARED; success evidence generation failed", file=sys.stderr
        )
        return 2
    print(
        canonical_json_bytes(
            {
                "prepare_outcome": "PREPARED",
                "prepare_result_path": str(result_path),
                "prepare_result_sha256": result_digest,
                "prepare_manifest_path": str(outputs["prepare_manifest_path"]),
                "operator_input_path": str(outputs["operator_input_path"]),
            }
        ).decode(),
        end="",
    )
    return 0


def _require_string(value: Any, label: str, *, nonblank: bool = True) -> str:
    if not isinstance(value, str) or (nonblank and not value.strip()):
        raise RunnerFailure("INVALID_ANSWER_SET", f"{label} must be a nonblank string")
    return value


def _require_string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        raise RunnerFailure("INVALID_ANSWER_SET", f"{label} must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise RunnerFailure("INVALID_ANSWER_SET", f"{label} entries must be nonblank strings")
    return value


def _load_successful_manifest(
    path_value: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest_path = Path(path_value).expanduser().resolve(strict=True)
    manifest_raw = manifest_path.read_bytes()
    manifest = _read_json_bytes(manifest_raw, "prepare manifest")
    if not isinstance(manifest, dict) or canonical_json_bytes(manifest) != manifest_raw:
        raise RunnerFailure("INVALID_PREPARE_MANIFEST", "prepare manifest is not canonical JSON")
    if manifest.get("schema_version") != 1 or manifest.get("question_set_id") != QUESTION_SET_ID:
        raise RunnerFailure("INVALID_PREPARE_MANIFEST", "prepare manifest identity is invalid")

    result_path = Path(manifest.get("prepare_result_path", "")).expanduser().resolve(strict=True)
    result_raw = result_path.read_bytes()
    if _sha256_bytes(result_raw) != manifest.get("prepare_result_sha256"):
        raise RunnerFailure("INVALID_PREPARE_RESULT", "prepare result digest differs from manifest")
    prepare_result = _read_json_bytes(result_raw, "prepare result")
    if not isinstance(prepare_result, dict) or canonical_json_bytes(prepare_result) != result_raw:
        raise RunnerFailure("INVALID_PREPARE_RESULT", "prepare result is not canonical JSON")
    if prepare_result.get("prepare_outcome") != "PREPARED":
        raise RunnerFailure("PREPARE_NOT_SUCCESSFUL", "prepare result does not record PREPARED")
    if any(state != "PASS" for state in prepare_result.get("validation", {}).values()):
        raise RunnerFailure("INVALID_PREPARE_RESULT", "PREPARED result validations are incomplete")
    if (
        prepare_result.get("execution_started") is not True
        or prepare_result.get("harness_invocation_count") != 1
        or prepare_result.get("harness_exit_code") != 0
        or prepare_result.get("worktree_clean") is not True
    ):
        raise RunnerFailure(
            "INVALID_PREPARE_RESULT", "PREPARED result execution state is inconsistent"
        )
    if prepare_result.get("prepare_result_path") != str(result_path):
        raise RunnerFailure(
            "INVALID_PREPARE_RESULT", "prepare result path identity is inconsistent"
        )
    for key in ("authority_id", "run_id", "attempt_number"):
        if manifest.get(key) != prepare_result.get(key):
            raise RunnerFailure("INVALID_PREPARE_MANIFEST", f"manifest/result {key} mismatch")
    bound_values = {
        "database_path": "database_path",
        "expected_db_sha256": "expected_db_sha256",
        "db_sha256_before": "db_sha256_before",
        "sidecars_before": "sidecars_before",
        "stdout_path": ("stdout", "path"),
        "stdout_sha256": ("stdout", "sha256"),
        "stderr_path": ("stderr", "path"),
        "stderr_sha256": ("stderr", "sha256"),
        "project_id": "project_id",
        "slice_id": "slice_id",
        "question_contract_path": "question_contract_path",
        "question_set_id": "question_set_id",
        "question_contract_sha256": "question_contract_sha256",
        "answer_set_path": "answer_set_path",
        "terminal_evidence_path": "terminal_evidence_path",
        "expected_head": "expected_head",
        "observed_head": "observed_head",
        "expected_harness_blob": "expected_harness_blob",
        "observed_harness_blob": "observed_harness_blob",
        "expected_harness_test_blob": "expected_harness_test_blob",
        "observed_harness_test_blob": "observed_harness_test_blob",
        "execution_root": "execution_root",
        "harness_path": "harness_path",
        "harness_test_path": "harness_test_path",
        "observed_git_root": "observed_git_root",
        "worktree_clean": "worktree_clean",
        "harness_command": "harness_command",
        "harness_invocation_count": "harness_invocation_count",
        "harness_exit_code": "harness_exit_code",
        "stdout_exclusive_create": "stdout_capture_exclusive_created",
        "stderr_exclusive_create": "stderr_capture_exclusive_created",
        "stdout_size": ("stdout", "size"),
        "stderr_size": ("stderr", "size"),
        "stdout_json_valid": ("validation", "stdout_json_valid"),
        "query_only_valid": ("validation", "query_only_valid"),
        "relay_schema_version_valid": ("validation", "relay_schema_version_valid"),
        "query_only": "observed_query_only",
        "relay_schema_version": "observed_relay_schema_version",
        "prepare_status": "prepare_outcome",
        "registry_path": "registry_path",
        "registry_sha256": "registry_sha256",
        "current_living_projections": "current_living_projections",
    }
    for manifest_key, result_key in bound_values.items():
        if isinstance(result_key, tuple):
            value = prepare_result.get(result_key[0], {}).get(result_key[1])
        else:
            value = prepare_result.get(result_key)
        if manifest.get(manifest_key) != value:
            raise RunnerFailure(
                "INVALID_PREPARE_MANIFEST", f"manifest/result {manifest_key} mismatch"
            )
    if manifest.get("prepare_manifest_path") != str(manifest_path):
        raise RunnerFailure("INVALID_PREPARE_MANIFEST", "manifest path identity is inconsistent")

    contract_path = (
        Path(manifest.get("question_contract_path", "")).expanduser().resolve(strict=True)
    )
    if str(contract_path) != manifest.get("question_contract_path"):
        raise RunnerFailure("INVALID_PREPARE_MANIFEST", "question contract path identity changed")
    contract_raw = contract_path.read_bytes()
    contract, digest = _validate_question_contract(
        contract_raw, manifest.get("question_contract_sha256", "")
    )
    if digest != prepare_result.get("question_contract_sha256"):
        raise RunnerFailure(
            "INVALID_PREPARE_MANIFEST", "question contract differs from prepare result"
        )
    for name in ("stdout", "stderr"):
        path_key = f"{name}_path"
        digest_key = f"{name}_sha256"
        capture_path = Path(manifest[path_key]).expanduser().resolve(strict=True)
        if str(capture_path) != manifest[path_key]:
            raise RunnerFailure("INVALID_CAPTURE_EVIDENCE", f"{name} path identity changed")
        capture_raw = capture_path.read_bytes()
        capture_record = prepare_result[name]
        if (
            capture_record.get("path") != manifest[path_key]
            or capture_record.get("sha256") != manifest[digest_key]
            or capture_record.get("size") != len(capture_raw)
            or _sha256_bytes(capture_raw) != manifest[digest_key]
        ):
            raise RunnerFailure("INVALID_CAPTURE_EVIDENCE", f"{name} capture digest differs")
    return manifest, prepare_result, contract


def validate_answer_set(
    answer_path_value: str | Path,
    manifest: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[dict[str, Any], bytes]:
    answer_path = Path(answer_path_value).expanduser().resolve(strict=True)
    pinned_answer_path = Path(manifest["answer_set_path"]).expanduser().resolve(strict=False)
    if answer_path != pinned_answer_path:
        raise RunnerFailure(
            "ANSWER_PATH_MISMATCH", "answer-set path differs from successful manifest"
        )
    raw = answer_path.read_bytes()
    answers = _read_json_bytes(raw, "answer set")
    if not isinstance(answers, dict) or set(answers) != ANSWER_TOP_LEVEL_FIELDS:
        raise RunnerFailure("INVALID_ANSWER_SET", "answer-set top-level fields are invalid")
    if type(answers["schema_version"]) is not int or answers["schema_version"] != 1:
        raise RunnerFailure("INVALID_ANSWER_SET", "answer-set schema version must be 1")
    for field in ("authority_id", "run_id", "question_set_id", "question_contract_sha256"):
        if answers[field] != manifest.get(field):
            raise RunnerFailure("INVALID_ANSWER_SET", f"answer-set {field} differs from manifest")
    for field in (
        "cold_start_declaration",
        "operator_identity",
        "runtime_identity",
        "completed_at",
    ):
        _require_string(answers[field], field)
    if answers["model_identity"] is not None:
        _require_string(answers["model_identity"], "model_identity")
    _require_string_list(answers["inspected_sources"], "inspected_sources", nonempty=True)
    _require_string_list(answers["prohibited_sources_accessed"], "prohibited_sources_accessed")

    answer_items = answers["answers"]
    if not isinstance(answer_items, list) or len(answer_items) != 10:
        raise RunnerFailure("INVALID_ANSWER_SET", "answer set must contain exactly ten answers")
    contract_questions = _contract_questions(contract)
    for index, (answer, question) in enumerate(
        zip(answer_items, contract_questions, strict=True), start=1
    ):
        if not isinstance(answer, dict) or set(answer) != ANSWER_FIELDS:
            raise RunnerFailure("INVALID_ANSWER_SET", f"Q{index} answer fields are invalid")
        if answer["question_id"] != f"Q{index}" or answer["question_id"] != question["question_id"]:
            raise RunnerFailure(
                "INVALID_ANSWER_SET", "answers must contain Q1 through Q10 in order"
            )
        if answer["question_text"] != question["question_text"]:
            raise RunnerFailure(
                "INVALID_ANSWER_SET", f"Q{index} question text differs from contract"
            )
        _require_string(answer["answer"], f"Q{index} answer")
        _require_string_list(answer["source_class"], f"Q{index} source_class")
        _require_string_list(answer["source_locators"], f"Q{index} source_locators")
        _require_string_list(
            answer["relevant_fields_or_records"], f"Q{index} relevant_fields_or_records"
        )
        if type(answer["not_determinable"]) is not bool:
            raise RunnerFailure("INVALID_ANSWER_SET", f"Q{index} not_determinable must be boolean")
        if not answer["not_determinable"] and (
            not answer["source_class"] or not answer["source_locators"]
        ):
            raise RunnerFailure("INVALID_ANSWER_SET", f"Q{index} requires source evidence")
    return answers, raw


def validate_answers(args: argparse.Namespace) -> int:
    manifest, _prepare_result, contract = _load_successful_manifest(args.prepare_manifest_path)
    validate_answer_set(args.answer_set_path, manifest, contract)
    print(
        canonical_json_bytes(
            {"answer_set_valid": True, "question_set_id": QUESTION_SET_ID}
        ).decode(),
        end="",
    )
    return 0


def seal(args: argparse.Namespace) -> int:
    manifest, prepare_result, contract = _load_successful_manifest(args.prepare_manifest_path)
    answer_set, answer_raw = validate_answer_set(args.answer_set_path, manifest, contract)
    terminal_path = Path(manifest["terminal_evidence_path"]).expanduser()
    if not terminal_path.is_absolute():
        raise RunnerFailure("INVALID_PREPARE_MANIFEST", "terminal evidence path must be absolute")
    if os.path.lexists(terminal_path):
        raise RunnerFailure("TERMINAL_TARGET_EXISTS", "terminal evidence target already exists")
    if not terminal_path.parent.is_dir():
        raise RunnerFailure(
            "TERMINAL_PARENT_MISSING", "terminal evidence parent directory does not exist"
        )

    database_path = Path(manifest["database_path"]).expanduser().resolve(strict=True)
    sidecars_after = _sidecar_records(database_path)
    db_after = _sha256_file(database_path)
    db_before = manifest["db_sha256_before"]
    unchanged = db_before == db_after
    terminal = {
        "schema_version": 2,
        "authority_id": manifest["authority_id"],
        "run_id": manifest["run_id"],
        "attempt_number": manifest["attempt_number"],
        "prepare_result_path": manifest["prepare_result_path"],
        "prepare_result_sha256": manifest["prepare_result_sha256"],
        "prepare_manifest_path": str(
            Path(args.prepare_manifest_path).expanduser().resolve(strict=True)
        ),
        "prepare_manifest_sha256": _sha256_file(
            Path(args.prepare_manifest_path).expanduser().resolve(strict=True)
        ),
        "raw_harness": {
            "stdout": {
                "path": manifest["stdout_path"],
                "sha256": manifest["stdout_sha256"],
                "size": prepare_result["stdout"]["size"],
            },
            "stderr": {
                "path": manifest["stderr_path"],
                "sha256": manifest["stderr_sha256"],
                "size": prepare_result["stderr"]["size"],
            },
        },
        "question_contract": {
            "question_set_id": manifest["question_set_id"],
            "path": manifest["question_contract_path"],
            "sha256": manifest["question_contract_sha256"],
        },
        "operator_answer_set": {
            "path": manifest["answer_set_path"],
            "sha256": _sha256_bytes(answer_raw),
            "data": answer_set,
        },
        "database": {
            "path": str(database_path),
            "expected_sha256": manifest["expected_db_sha256"],
            "before_sha256": db_before,
            "after_sha256": db_after,
            "unchanged": unchanged,
        },
        "sidecars": {"before": manifest["sidecars_before"], "after": sidecars_after},
        "custody": {
            "cold_start_declaration": answer_set["cold_start_declaration"],
            "operator_identity": answer_set["operator_identity"],
            "runtime_identity": answer_set["runtime_identity"],
            "model_identity": answer_set["model_identity"],
            "inspected_sources": answer_set["inspected_sources"],
            "prohibited_sources_accessed": answer_set["prohibited_sources_accessed"],
        },
        "protocol_result": (
            "SEALED_READY_FOR_INDEPENDENT_EVALUATION" if unchanged else "INVALID_DB_MUTATION"
        ),
        "sealed_at": _timestamp(),
    }
    _write_exclusive(terminal_path, canonical_json_bytes(terminal))
    terminal_digest = _sha256_file(terminal_path)
    print(
        canonical_json_bytes(
            {
                "protocol_result": terminal["protocol_result"],
                "terminal_evidence_path": str(terminal_path),
                "terminal_evidence_sha256": terminal_digest,
            }
        ).decode(),
        end="",
    )
    return 0 if unchanged else 2


def _add_prepare_arguments(parser: argparse.ArgumentParser) -> None:
    required = (
        "authority-id",
        "run-id",
        "attempt-number",
        "execution-root",
        "expected-head",
        "harness-path",
        "expected-harness-blob",
        "harness-test-path",
        "expected-harness-test-blob",
        "database-path",
        "expected-db-sha256",
        "project-id",
        "slice-id",
        "question-contract-path",
        "expected-question-contract-sha256",
        "stdout-path",
        "stderr-path",
        "prepare-result-path",
        "prepare-manifest-path",
        "operator-input-path",
        "answer-set-path",
        "terminal-evidence-path",
    )
    for name in required:
        parser.add_argument(
            f"--{name}", required=True, type=int if name == "attempt-number" else str
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare_parser = subparsers.add_parser("prepare")
    _add_prepare_arguments(prepare_parser)
    validate_parser = subparsers.add_parser("validate-answers")
    validate_parser.add_argument("--prepare-manifest-path", required=True)
    validate_parser.add_argument("--answer-set-path", required=True)
    seal_parser = subparsers.add_parser("seal")
    seal_parser.add_argument("--prepare-manifest-path", required=True)
    seal_parser.add_argument("--answer-set-path", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "prepare":
            return prepare(args)
        if args.command == "validate-answers":
            return validate_answers(args)
        if args.command == "seal":
            return seal(args)
    except (OSError, RunnerFailure, ValueError, KeyError, TypeError) as error:
        code = error.code if isinstance(error, RunnerFailure) else "RUNNER_INPUT_INVALID"
        print(
            canonical_json_bytes({"failure_code": code, "outcome": "INVALID"}).decode(),
            end="",
            file=sys.stderr,
        )
        return 2
    raise AssertionError("argparse accepted an unknown B4 runner command")


if __name__ == "__main__":
    raise SystemExit(main())
