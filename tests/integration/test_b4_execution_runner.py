"""Protocol tests for the B4 Revision 2 deterministic execution runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

_RUNNER_PATH = Path(__file__).resolve().parents[2] / "scripts" / "b4_execution_runner.py"
_SPEC = importlib.util.spec_from_file_location("b4_execution_runner", _RUNNER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
runner = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(runner)

_QUESTION_CONTRACT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "b4_question_contract_v1.json"
)
_VALID_STDOUT = b'{"query_only":1,"schema_version":8}\n'
_VALID_STDERR = b"harness diagnostic\n"


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _write_canonical(path: Path, value: Any) -> bytes:
    raw = runner.canonical_json_bytes(value)
    path.write_bytes(raw)
    return raw


def _fixture(tmp_path: Path, *, contract_bytes: bytes | None = None) -> dict[str, Any]:
    root = tmp_path / "execution-repo"
    (root / "scripts").mkdir(parents=True)
    (root / "tests/integration").mkdir(parents=True)
    (root / ".relay").mkdir()
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    database_dir = tmp_path / "database"
    database_dir.mkdir()
    database = database_dir / "operational.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE fixture (value TEXT)")
        connection.execute("INSERT INTO fixture VALUES ('disposable')")

    harness_source = (
        b"import json\n"
        b"print(json.dumps({'query_only': 1, 'schema_version': 8}, separators=(',', ':')))\n"
    )
    harness = root / "scripts/b4_readonly_harness.py"
    harness.write_bytes(harness_source)
    harness_test = root / "tests/integration/test_b4_readonly_harness.py"
    harness_test.write_text("# frozen harness test fixture\n", encoding="utf-8")
    contract_raw = (
        contract_bytes if contract_bytes is not None else _QUESTION_CONTRACT_PATH.read_bytes()
    )
    (root / runner.QUESTION_CONTRACT_RELATIVE_PATH).write_bytes(contract_raw)
    registry = {
        "artifacts": [
            {
                "artifact_class": "LIVING_PROJECTION",
                "artifact_id": "art_current_1",
                "artifact_state": "CURRENT",
                "content_digest": "sha256:abc",
                "path": "docs/CURRENT_BASELINE.md",
                "revision": 1,
                "title": "Current Baseline",
            },
            {
                "artifact_class": "IMMUTABLE_RECORD",
                "artifact_id": "art_record_1",
                "artifact_state": "LOCKED",
                "content_digest": "sha256:def",
                "path": "docs/record.md",
                "revision": 1,
                "title": "Record",
            },
        ]
    }
    _write_canonical(root / ".relay/registry.json", registry)

    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "config", "user.name", "B4 Test")
    _git(root, "add", ".")
    _git(root, "commit", "-qm", "fixture")
    head = _git(root, "rev-parse", "HEAD")
    harness_blob = _git(root, "rev-parse", "HEAD:scripts/b4_readonly_harness.py")
    harness_test_blob = _git(
        root, "rev-parse", "HEAD:tests/integration/test_b4_readonly_harness.py"
    )

    args = SimpleNamespace(
        authority_id="RLY-S110-DOGFOOD-B4-R2-IMPL-AUTH-001",
        run_id="run_test_001",
        attempt_number=7,
        execution_root=str(root),
        expected_head=head,
        harness_path="scripts/b4_readonly_harness.py",
        expected_harness_blob=harness_blob,
        harness_test_path="tests/integration/test_b4_readonly_harness.py",
        expected_harness_test_blob=harness_test_blob,
        database_path=str(database),
        expected_db_sha256=_digest(database.read_bytes()),
        project_id="prj_fixture",
        slice_id="slc_fixture",
        question_contract_path="scripts/b4_question_contract_v1.json",
        expected_question_contract_sha256=_digest(contract_raw),
        stdout_path=str(evidence / "harness.stdout.json"),
        stderr_path=str(evidence / "harness.stderr.log"),
        prepare_result_path=str(evidence / "prepare-result.json"),
        prepare_manifest_path=str(evidence / "prepare-manifest.json"),
        operator_input_path=str(evidence / "operator-input.json"),
        answer_set_path=str(evidence / "answers.json"),
        terminal_evidence_path=str(evidence / "terminal-evidence.json"),
    )
    git_values = {
        ("rev-parse", "--show-toplevel"): str(root),
        ("rev-parse", "HEAD"): head,
        ("status", "--porcelain"): "",
        ("rev-parse", "HEAD:scripts/b4_readonly_harness.py"): harness_blob,
        ("rev-parse", "HEAD:tests/integration/test_b4_readonly_harness.py"): harness_test_blob,
    }
    return {
        "root": root,
        "evidence": evidence,
        "database": database,
        "args": args,
        "git_values": git_values,
        "harness": harness,
        "harness_test": harness_test,
        "contract_bytes": contract_raw,
        "registry": root / ".relay/registry.json",
    }


def _mock_git(monkeypatch: pytest.MonkeyPatch, fixture: dict[str, Any]) -> None:
    def observed_git(_root: Path, *arguments: str) -> str:
        return fixture["git_values"][tuple(arguments)]

    monkeypatch.setattr(runner, "_git", observed_git)


def _run_prepare(
    fixture: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
    *,
    stdout: bytes = _VALID_STDOUT,
    stderr: bytes = _VALID_STDERR,
    exit_code: int = 0,
    spawn_error: bool = False,
) -> tuple[int, list[list[str]]]:
    _mock_git(monkeypatch, fixture)
    invocations: list[list[str]] = []

    def fake_popen(command: list[str], **kwargs: Any) -> Any:
        invocations.append(command)
        if spawn_error:
            raise OSError("disposable forced process creation failure")
        kwargs["stdout"].write(stdout)
        kwargs["stderr"].write(stderr)
        return SimpleNamespace(wait=lambda: exit_code)

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    return runner.prepare(fixture["args"]), invocations


def _prepare_success(tmp_path: Path) -> dict[str, Any]:
    fixture = _fixture(tmp_path)
    completed = subprocess.run(
        [
            sys.executable,
            str(_RUNNER_PATH),
            "prepare",
            "--authority-id",
            fixture["args"].authority_id,
            "--run-id",
            fixture["args"].run_id,
            "--attempt-number",
            str(fixture["args"].attempt_number),
            "--execution-root",
            str(fixture["root"]),
            "--expected-head",
            fixture["args"].expected_head,
            "--harness-path",
            fixture["args"].harness_path,
            "--expected-harness-blob",
            fixture["args"].expected_harness_blob,
            "--harness-test-path",
            fixture["args"].harness_test_path,
            "--expected-harness-test-blob",
            fixture["args"].expected_harness_test_blob,
            "--database-path",
            fixture["args"].database_path,
            "--expected-db-sha256",
            fixture["args"].expected_db_sha256,
            "--project-id",
            fixture["args"].project_id,
            "--slice-id",
            fixture["args"].slice_id,
            "--question-contract-path",
            fixture["args"].question_contract_path,
            "--expected-question-contract-sha256",
            fixture["args"].expected_question_contract_sha256,
            "--stdout-path",
            fixture["args"].stdout_path,
            "--stderr-path",
            fixture["args"].stderr_path,
            "--prepare-result-path",
            fixture["args"].prepare_result_path,
            "--prepare-manifest-path",
            fixture["args"].prepare_manifest_path,
            "--operator-input-path",
            fixture["args"].operator_input_path,
            "--answer-set-path",
            fixture["args"].answer_set_path,
            "--terminal-evidence-path",
            fixture["args"].terminal_evidence_path,
        ],
        cwd=fixture["root"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    fixture["manifest_path"] = Path(fixture["args"].prepare_manifest_path)
    fixture["answer_path"] = Path(fixture["args"].answer_set_path)
    fixture["terminal_path"] = Path(fixture["args"].terminal_evidence_path)
    return fixture


def _answer_set(fixture: dict[str, Any]) -> dict[str, Any]:
    contract = json.loads(fixture["contract_bytes"])
    manifest = json.loads(Path(fixture["args"].prepare_manifest_path).read_bytes())
    return {
        "schema_version": 1,
        "authority_id": manifest["authority_id"],
        "run_id": manifest["run_id"],
        "question_set_id": manifest["question_set_id"],
        "question_contract_sha256": manifest["question_contract_sha256"],
        "cold_start_declaration": "I did not receive prior B4 answer material.",
        "operator_identity": "operator-fixture",
        "runtime_identity": "runtime-fixture",
        "model_identity": None,
        "inspected_sources": ["captured harness JSON"],
        "prohibited_sources_accessed": [],
        "answers": [
            {
                "question_id": question["question_id"],
                "question_text": question["question_text"],
                "answer": "Fixture response.",
                "source_class": ["captured harness JSON"],
                "source_locators": ["harness.stdout.json"],
                "relevant_fields_or_records": ["fixture field"],
                "not_determinable": False,
            }
            for question in contract["questions"]
        ],
        "completed_at": "2026-10-21T12:00:00Z",
    }


def test_question_contract_is_canonical_and_has_exact_q1_to_q10_dimensions() -> None:
    raw = _QUESTION_CONTRACT_PATH.read_bytes()
    contract, digest = runner._validate_question_contract(raw, _digest(raw))
    assert contract["question_set_id"] == "B4-R2-QSET-001"
    assert digest == _digest(raw)
    assert [question["question_id"] for question in contract["questions"]] == [
        f"Q{index}" for index in range(1, 11)
    ]
    assert [question["question_text"] for question in contract["questions"]] == [
        "What project is this?",
        "What is the project objective?",
        "What information is contextual or pre-T1 legacy rather than Relay lifecycle?",
        "What is the current governed work frontier?",
        "What exact Slice is current?",
        (
            "What is the current Slice lifecycle state? State its phase, lifecycle revision, "
            "validity, "
            "blockage status, and any recorded blockage reasons."
        ),
        "What is blocked?",
        (
            "According to Relay's durable project and governance state at this pinned checkout, "
            "what is the next governed project action or Human governance decision? Do not "
            "describe the next procedural step of this B4 operator run. If no exact next governed "
            "action or decision is established, say NOT DETERMINABLE FROM CURRENT DURABLE STATE."
        ),
        "What Human decision, if any, is pending?",
        (
            "What current or future work is only proposed/planned and therefore not authorized? "
            "For the current Slice, distinguish whether design/opening authority exists from "
            "whether implementation authority exists, then identify later roadmap work that "
            "remains not open/not authorized."
        ),
    ]
    assert [question["required_dimensions"] for question in contract["questions"]] == [
        ["Project identity", "repository identity"],
        ["represented Project objective", "source/record time scope where material"],
        [
            "what the adoption record establishes about pre-T1 software-project existence",
            "where Relay-governed lifecycle/history begins",
            "explicit avoidance of fabricated pre-T1 Relay lifecycle/history",
        ],
        [
            "exact current frontier Slice set",
            "represented frontier cardinality/completeness",
            "relevant durable incomplete/not-determinable state",
        ],
        ["Slice ID", "title", "definition revision", "parent/dependencies where material"],
        [
            "lifecycle phase",
            "lifecycle revision",
            "lifecycle validity",
            "blockage status",
            "recorded blockage reasons",
        ],
        [
            "explicit current blockers",
            "distinction between current Slice/project blockers and historical/separate blockers",
            (
                "qualification that absence of projected blockers does not prove absence of "
                "undocumented external impediments"
            ),
        ],
        [
            "operational next-work projection",
            "applicable registry-resolved canonical governance action/decision",
            (
                "distinction among currently authorized action, needed Human "
                "authorization/decision, "
                "and merely planned work"
            ),
            "exclusion of B4 operator-procedure steps as the project answer",
        ],
        [
            "only explicit durable pending Human decision",
            "distinction between none recorded and not determinable",
            "available controls/actions are not pending decisions by themselves",
        ],
        [
            "current Slice lifecycle/planned status",
            "current Slice design/opening authority boundary",
            "current Slice implementation authority boundary",
            "later roadmap work remaining not open/not authorized",
            (
                "no authority inference from roadmap order, capability, `PROPOSED`, or document "
                "presence"
            ),
        ],
    ]
    assert all(question["required_dimensions"] for question in contract["questions"])
    assert all(
        set(question["response_schema"])
        == {
            "answer",
            "source_class",
            "source_locators",
            "relevant_fields_or_records",
            "not_determinable",
        }
        for question in contract["questions"]
    )


def test_cli_exposes_only_the_three_authorized_subcommands() -> None:
    parser = runner._parser()
    assert set(parser._subparsers._group_actions[0].choices) == {
        "prepare",
        "validate-answers",
        "seal",
    }


@pytest.mark.parametrize(
    ("observation", "argument", "bad_value"),
    [
        (("rev-parse", "HEAD"), "expected_head", "f" * 40),
        (("status", "--porcelain"), None, " M tracked.py"),
        (("rev-parse", "HEAD:scripts/b4_readonly_harness.py"), "expected_harness_blob", "f" * 40),
        (
            ("rev-parse", "HEAD:tests/integration/test_b4_readonly_harness.py"),
            "expected_harness_test_blob",
            "f" * 40,
        ),
    ],
)
def test_git_preflight_failures_do_not_start_child(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    observation: tuple[str, ...],
    argument: str | None,
    bad_value: str,
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    if argument is not None:
        setattr(fixture["args"], argument, bad_value)
    else:
        fixture["git_values"][observation] = bad_value
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "INVALID_PRECHECK"
    assert result["execution_started"] is False
    assert result["harness_invocation_count"] == 0
    assert result["harness_exit_code"] is None


@pytest.mark.parametrize("field", ["expected_db_sha256", "expected_question_contract_sha256"])
def test_wrong_database_or_contract_digest_is_precheck_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    setattr(fixture["args"], field, "0" * 64)
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []


def test_noncanonical_contract_is_precheck_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = _QUESTION_CONTRACT_PATH.read_bytes() + b" "
    fixture = _fixture(tmp_path, contract_bytes=raw)
    _mock_git(monkeypatch, fixture)
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []


def test_duplicate_key_contract_is_precheck_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw = (
        b'{"schema_version":1,"schema_version":1,"question_set_id":"B4-R2-QSET-001","questions":[]}'
    )
    fixture = _fixture(tmp_path, contract_bytes=raw)
    _mock_git(monkeypatch, fixture)
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []


def test_contract_digest_changes_when_required_dimension_changes(tmp_path: Path) -> None:
    original = json.loads(_QUESTION_CONTRACT_PATH.read_bytes())
    revised = json.loads(_QUESTION_CONTRACT_PATH.read_bytes())
    revised["questions"][0]["required_dimensions"][0] += " revised"
    assert _digest(runner.canonical_json_bytes(original)) != _digest(
        runner.canonical_json_bytes(revised)
    )


@pytest.mark.parametrize("path_mode", ["inside_repo", "collision", "database", "missing_parent"])
def test_invalid_output_paths_fail_before_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path_mode: str
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    if path_mode == "inside_repo":
        fixture["args"].stdout_path = str(fixture["root"] / "stdout.json")
    elif path_mode == "collision":
        fixture["args"].stderr_path = fixture["args"].stdout_path
    elif path_mode == "database":
        fixture["args"].stdout_path = str(fixture["database"])
    else:
        fixture["args"].stdout_path = str(fixture["evidence"] / "missing" / "stdout.json")
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []


@pytest.mark.parametrize(
    "field",
    [
        "stdout_path",
        "stderr_path",
        "prepare_result_path",
        "prepare_manifest_path",
        "operator_input_path",
        "answer_set_path",
        "terminal_evidence_path",
    ],
)
def test_every_preexisting_output_target_fails_without_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    Path(getattr(fixture["args"], field)).write_text("preserve", encoding="utf-8")
    calls: list[Any] = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []


@pytest.mark.parametrize("fail_on", ["stdout", "stderr"])
def test_capture_setup_failure_preserves_created_capture_and_never_spawns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail_on: str
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    original = runner._capture_handle
    calls: list[Any] = []

    def fail_capture(path: Path) -> Any:
        if path == Path(fixture["args"].stdout_path) and fail_on == "stdout":
            raise OSError("forced stdout create failure")
        if path == Path(fixture["args"].stderr_path):
            raise OSError("forced stderr create failure")
        return original(path)

    monkeypatch.setattr(runner, "_capture_handle", fail_capture)
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    assert runner.prepare(fixture["args"]) == 2
    assert calls == []
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "INVALID_CAPTURE_SETUP"
    if fail_on == "stderr":
        assert Path(fixture["args"].stdout_path).exists()
        assert result["stdout"]["exists"] is True
        assert result["stdout"]["size"] == 0


def test_spawn_failure_is_terminal_and_preserves_both_hashed_captures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    status, invocations = _run_prepare(fixture, monkeypatch, spawn_error=True)
    assert status == 2
    assert len(invocations) == 1
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "INVALID_HARNESS_SPAWN"
    assert result["failure_stage"] == "spawn"
    assert result["failure_code"] == "HARNESS_PROCESS_CREATION_FAILED"
    assert result["execution_started"] is False
    assert result["harness_invocation_count"] == 0
    assert result["harness_exit_code"] is None
    for name in ("stdout", "stderr"):
        capture = Path(result[name]["path"])
        assert capture.exists()
        assert result[name]["size"] == 0
        assert result[name]["sha256"] == _digest(b"")
    assert not Path(fixture["args"].prepare_manifest_path).exists()
    assert not Path(fixture["args"].operator_input_path).exists()


def test_spawn_result_persistence_failure_is_reported_without_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    invocations: list[Any] = []

    def fail_spawn(command: list[str], **kwargs: Any) -> Any:
        invocations.append(command)
        raise OSError("forced spawn failure")

    monkeypatch.setattr(runner.subprocess, "Popen", fail_spawn)
    original_write = runner._write_exclusive

    def reject_prepare_result(path: Path, raw: bytes) -> None:
        if path == Path(fixture["args"].prepare_result_path):
            raise OSError("forced evidence write failure")
        original_write(path, raw)

    monkeypatch.setattr(runner, "_write_exclusive", reject_prepare_result)
    assert runner.prepare(fixture["args"]) == 2
    assert len(invocations) == 1
    failure = json.loads(capsys.readouterr().err)
    assert failure["prepare_outcome"] == "INVALID_PREPARE_EVIDENCE"
    assert not Path(fixture["args"].prepare_manifest_path).exists()
    assert not Path(fixture["args"].operator_input_path).exists()


def test_manifest_write_failure_preserves_prepared_result_and_does_not_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    invocation_count = 0

    def fake_popen(command: list[str], **kwargs: Any) -> Any:
        nonlocal invocation_count
        invocation_count += 1
        kwargs["stdout"].write(_VALID_STDOUT)
        kwargs["stderr"].write(_VALID_STDERR)
        return SimpleNamespace(wait=lambda: 0)

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    original_write = runner._write_exclusive

    def reject_manifest(path: Path, raw: bytes) -> None:
        if path == Path(fixture["args"].prepare_manifest_path):
            raise OSError("forced manifest write failure")
        original_write(path, raw)

    monkeypatch.setattr(runner, "_write_exclusive", reject_manifest)
    assert runner.prepare(fixture["args"]) == 2
    assert invocation_count == 1
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "PREPARED"
    assert result["stdout"]["sha256"] == _digest(_VALID_STDOUT)
    assert not Path(fixture["args"].prepare_manifest_path).exists()
    assert not Path(fixture["args"].operator_input_path).exists()


@pytest.mark.parametrize(
    ("stdout", "stderr", "exit_code", "expected"),
    [
        (_VALID_STDOUT, _VALID_STDERR, 9, "INVALID_HARNESS_EXIT"),
        (b"", _VALID_STDERR, 0, "INVALID_HARNESS_OUTPUT"),
        (b"not json", _VALID_STDERR, 0, "INVALID_HARNESS_OUTPUT"),
        (b'{"query_only":0,"schema_version":8}', _VALID_STDERR, 0, "INVALID_HARNESS_PROTOCOL"),
        (b'{"query_only":1,"schema_version":7}', _VALID_STDERR, 0, "INVALID_HARNESS_PROTOCOL"),
    ],
)
def test_child_failures_are_classified_once_and_captures_are_hashed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stdout: bytes,
    stderr: bytes,
    exit_code: int,
    expected: str,
) -> None:
    fixture = _fixture(tmp_path)
    status, invocations = _run_prepare(
        fixture, monkeypatch, stdout=stdout, stderr=stderr, exit_code=exit_code
    )
    assert status == 2
    assert len(invocations) == 1
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == expected
    assert result["execution_started"] is True
    assert result["harness_invocation_count"] == 1
    assert result["stdout"]["sha256"] == _digest(stdout)
    assert result["stderr"]["sha256"] == _digest(stderr)
    if stdout == b"":
        assert result["validation"] == {
            "stdout_nonempty": "FAIL",
            "stdout_json_valid": "FAIL",
            "query_only_valid": "NOT_PERFORMED",
            "relay_schema_version_valid": "NOT_PERFORMED",
        }
    elif stdout == b"not json":
        assert result["validation"] == {
            "stdout_nonempty": "PASS",
            "stdout_json_valid": "FAIL",
            "query_only_valid": "NOT_PERFORMED",
            "relay_schema_version_valid": "NOT_PERFORMED",
        }
    assert not Path(fixture["args"].prepare_manifest_path).exists()
    assert not Path(fixture["args"].operator_input_path).exists()


def test_wait_failure_terminates_and_reaps_before_capture_hashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    invocations: list[list[str]] = []

    class Child:
        wait_calls = 0
        terminated = False
        reaped = False

        def wait(self, timeout: float | None = None) -> int:
            self.wait_calls += 1
            if self.wait_calls == 1:
                assert timeout is None
                raise OSError("forced first wait failure")
            assert timeout == runner.CHILD_REAP_TIMEOUT_SECONDS
            assert self.terminated
            self.reaped = True
            return -9

        def poll(self) -> int | None:
            return -9 if self.reaped else None

        def kill(self) -> None:
            self.terminated = True

    child = Child()

    def fake_popen(command: list[str], **kwargs: Any) -> Child:
        invocations.append(command)
        kwargs["stdout"].write(_VALID_STDOUT)
        kwargs["stderr"].write(_VALID_STDERR)
        return child

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)
    original_file_record = runner._file_record

    def require_reaped_before_hash(path: Path) -> dict[str, Any]:
        assert child.reaped
        return original_file_record(path)

    monkeypatch.setattr(runner, "_file_record", require_reaped_before_hash)
    assert runner.prepare(fixture["args"]) == 2
    assert len(invocations) == 1
    assert child.wait_calls == 2
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "INVALID_HARNESS_EXIT"
    assert result["failure_stage"] == "wait"
    assert result["failure_code"] == "HARNESS_WAIT_FAILED"
    assert result["harness_exit_code"] == -9
    assert result["stdout"]["sha256"] == _digest(_VALID_STDOUT)
    assert result["stderr"]["sha256"] == _digest(_VALID_STDERR)


def test_unconfirmed_child_termination_does_not_claim_capture_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    _mock_git(monkeypatch, fixture)
    invocations: list[list[str]] = []

    class UnreapableChild:
        wait_calls = 0

        def wait(self, timeout: float | None = None) -> int:
            self.wait_calls += 1
            if self.wait_calls == 1:
                assert timeout is None
            else:
                assert timeout == runner.CHILD_REAP_TIMEOUT_SECONDS
            raise OSError("forced persistent wait failure")

        def poll(self) -> None:
            return None

        def kill(self) -> None:
            pass

    child = UnreapableChild()

    def fake_popen(command: list[str], **kwargs: Any) -> UnreapableChild:
        invocations.append(command)
        kwargs["stdout"].write(_VALID_STDOUT)
        kwargs["stderr"].write(_VALID_STDERR)
        return child

    monkeypatch.setattr(runner.subprocess, "Popen", fake_popen)

    def reject_capture_hash(_path: Path) -> dict[str, Any]:
        raise AssertionError("capture bytes cannot be hashed before child termination")

    monkeypatch.setattr(runner, "_file_record", reject_capture_hash)
    assert runner.prepare(fixture["args"]) == 2
    assert len(invocations) == 1
    assert child.wait_calls == 2
    result = json.loads(Path(fixture["args"].prepare_result_path).read_bytes())
    assert result["prepare_outcome"] == "INVALID_PREPARE_EVIDENCE"
    assert result["failure_stage"] == "wait"
    assert result["failure_code"] == "CHILD_TERMINATION_UNCONFIRMED"
    assert result["harness_exit_code"] is None
    for name in ("stdout", "stderr"):
        assert result[name]["exists"] is True
        assert result[name]["size"] is None
        assert result[name]["sha256"] is None


def test_prepare_success_is_exact_once_durable_and_binds_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _fixture(tmp_path)
    writes: list[Path] = []
    original_write = runner._write_exclusive

    def track_write(path: Path, raw: bytes) -> None:
        writes.append(path)
        original_write(path, raw)

    monkeypatch.setattr(runner, "_write_exclusive", track_write)
    status, invocations = _run_prepare(
        fixture, monkeypatch, stdout=b'{ "query_only": 1, "schema_version": 8 }\n'
    )
    assert status == 0
    assert len(invocations) == 1
    assert invocations[0] == [
        sys.executable,
        str(fixture["harness"]),
        "--database",
        str(fixture["database"]),
        "--project-id",
        fixture["args"].project_id,
        "--slice-id",
        fixture["args"].slice_id,
    ]
    args = fixture["args"]
    result_path = Path(args.prepare_result_path)
    manifest_path = Path(args.prepare_manifest_path)
    operator_path = Path(args.operator_input_path)
    result = json.loads(result_path.read_bytes())
    manifest = json.loads(manifest_path.read_bytes())
    envelope = json.loads(operator_path.read_bytes())
    assert result["prepare_outcome"] == "PREPARED"
    assert result["validation"] == {
        "stdout_nonempty": "PASS",
        "stdout_json_valid": "PASS",
        "query_only_valid": "PASS",
        "relay_schema_version_valid": "PASS",
    }
    assert result["stdout"]["sha256"] == _digest(Path(args.stdout_path).read_bytes())
    assert Path(args.stdout_path).read_bytes() == b'{ "query_only": 1, "schema_version": 8 }\n'
    assert result["stderr"]["sha256"] == _digest(Path(args.stderr_path).read_bytes())
    assert writes.index(result_path) < writes.index(manifest_path) < writes.index(operator_path)
    assert manifest["prepare_result_sha256"] == _digest(result_path.read_bytes())
    assert envelope["question_contract"] == json.loads(fixture["contract_bytes"])
    assert envelope["question_contract_path"] == str(
        (Path(fixture["root"]) / args.question_contract_path).resolve()
    )
    assert envelope["question_contract_sha256"] == args.expected_question_contract_sha256
    assert envelope["answer_set_destination"] == args.answer_set_path
    assert (
        envelope["registry"]["current_living_projections"] == manifest["current_living_projections"]
    )
    assert envelope["registry"]["current_living_projections"][0]["artifact_id"] == "art_current_1"


def test_real_git_preflight_uses_git_blob_identity_and_runs_one_child(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    completed = subprocess.run(
        [
            sys.executable,
            str(_RUNNER_PATH),
            "prepare",
            "--authority-id",
            fixture["args"].authority_id,
            "--run-id",
            fixture["args"].run_id,
            "--attempt-number",
            str(fixture["args"].attempt_number),
            "--execution-root",
            str(fixture["root"]),
            "--expected-head",
            fixture["args"].expected_head,
            "--harness-path",
            fixture["args"].harness_path,
            "--expected-harness-blob",
            fixture["args"].expected_harness_blob,
            "--harness-test-path",
            fixture["args"].harness_test_path,
            "--expected-harness-test-blob",
            fixture["args"].expected_harness_test_blob,
            "--database-path",
            fixture["args"].database_path,
            "--expected-db-sha256",
            fixture["args"].expected_db_sha256,
            "--project-id",
            fixture["args"].project_id,
            "--slice-id",
            fixture["args"].slice_id,
            "--question-contract-path",
            fixture["args"].question_contract_path,
            "--expected-question-contract-sha256",
            fixture["args"].expected_question_contract_sha256,
            "--stdout-path",
            fixture["args"].stdout_path,
            "--stderr-path",
            fixture["args"].stderr_path,
            "--prepare-result-path",
            fixture["args"].prepare_result_path,
            "--prepare-manifest-path",
            fixture["args"].prepare_manifest_path,
            "--operator-input-path",
            fixture["args"].operator_input_path,
            "--answer-set-path",
            fixture["args"].answer_set_path,
            "--terminal-evidence-path",
            fixture["args"].terminal_evidence_path,
        ],
        cwd=fixture["root"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    manifest = json.loads(Path(fixture["args"].prepare_manifest_path).read_bytes())
    assert manifest["observed_harness_blob"] == fixture["args"].expected_harness_blob
    assert manifest["observed_harness_test_blob"] == fixture["args"].expected_harness_test_blob


def test_answer_validation_accepts_structure_without_rewriting_bytes(tmp_path: Path) -> None:
    fixture = _prepare_success(tmp_path)
    answer = _answer_set(fixture)
    raw = json.dumps(answer, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    fixture["answer_path"].write_bytes(raw)
    manifest, _result, contract = runner._load_successful_manifest(fixture["manifest_path"])
    validated, exact_raw = runner.validate_answer_set(fixture["answer_path"], manifest, contract)
    assert validated == answer
    assert exact_raw == raw
    assert fixture["answer_path"].read_bytes() == raw


@pytest.mark.parametrize(
    "mutate",
    [
        lambda answer: answer["answers"].pop(),
        lambda answer: answer["answers"].__setitem__(1, answer["answers"][0].copy()),
        lambda answer: answer["answers"].reverse(),
        lambda answer: answer["answers"][0].__setitem__("question_text", "wrong question"),
        lambda answer: answer.__setitem__("question_set_id", "wrong-set"),
        lambda answer: answer.__setitem__("question_contract_sha256", "0" * 64),
        lambda answer: answer.__setitem__("authority_id", "wrong-authority"),
        lambda answer: answer.__setitem__("run_id", "wrong-run"),
        lambda answer: answer.__setitem__("semantic_score", 10),
        lambda answer: answer["answers"][0].pop("source_locators"),
        lambda answer: answer["answers"][0].__setitem__("answer", "  "),
        lambda answer: answer["answers"][0].__setitem__("not_determinable", "false"),
        lambda answer: answer["answers"][0].__setitem__("source_class", "harness"),
        lambda answer: answer["answers"][0].__setitem__("source_locators", []),
    ],
)
def test_answer_validation_rejects_malformed_answer_set(tmp_path: Path, mutate: Any) -> None:
    fixture = _prepare_success(tmp_path)
    answer = _answer_set(fixture)
    mutate(answer)
    fixture["answer_path"].write_bytes(runner.canonical_json_bytes(answer))
    manifest, _result, contract = runner._load_successful_manifest(fixture["manifest_path"])
    with pytest.raises(runner.RunnerFailure):
        runner.validate_answer_set(fixture["answer_path"], manifest, contract)


def test_answer_validation_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    fixture = _prepare_success(tmp_path)
    fixture["answer_path"].write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    manifest, _result, contract = runner._load_successful_manifest(fixture["manifest_path"])
    with pytest.raises(runner.RunnerFailure):
        runner.validate_answer_set(fixture["answer_path"], manifest, contract)


def test_answer_path_must_match_success_manifest(tmp_path: Path) -> None:
    fixture = _prepare_success(tmp_path)
    alternative = fixture["evidence"] / "another-answers.json"
    alternative.write_text("{}", encoding="utf-8")
    manifest, _result, contract = runner._load_successful_manifest(fixture["manifest_path"])
    with pytest.raises(runner.RunnerFailure, match="answer-set path"):
        runner.validate_answer_set(alternative, manifest, contract)


def test_seal_unchanged_db_copies_operator_inventory_and_reports_terminal_digest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = _prepare_success(tmp_path)
    answer = _answer_set(fixture)
    _write_canonical(fixture["answer_path"], answer)
    args = SimpleNamespace(
        prepare_manifest_path=str(fixture["manifest_path"]),
        answer_set_path=str(fixture["answer_path"]),
    )
    assert runner.seal(args) == 0
    evidence = json.loads(fixture["terminal_path"].read_bytes())
    assert evidence["protocol_result"] == "SEALED_READY_FOR_INDEPENDENT_EVALUATION"
    assert evidence["operator_answer_set"]["sha256"] == _digest(fixture["answer_path"].read_bytes())
    assert evidence["custody"]["inspected_sources"] == answer["inspected_sources"]
    assert (
        evidence["custody"]["prohibited_sources_accessed"] == answer["prohibited_sources_accessed"]
    )
    external = json.loads(capsys.readouterr().out)
    assert external["terminal_evidence_sha256"] == _digest(fixture["terminal_path"].read_bytes())
    assert "terminal_evidence_sha256" not in evidence


def test_seal_records_database_mutation_and_returns_nonzero(tmp_path: Path) -> None:
    fixture = _prepare_success(tmp_path)
    _write_canonical(fixture["answer_path"], _answer_set(fixture))
    with sqlite3.connect(fixture["database"]) as connection:
        connection.execute("INSERT INTO fixture VALUES ('mutated')")
    args = SimpleNamespace(
        prepare_manifest_path=str(fixture["manifest_path"]),
        answer_set_path=str(fixture["answer_path"]),
    )
    assert runner.seal(args) == 2
    evidence = json.loads(fixture["terminal_path"].read_bytes())
    assert evidence["protocol_result"] == "INVALID_DB_MUTATION"
    assert evidence["database"]["unchanged"] is False


def test_sidecar_mtime_only_change_is_recorded_but_does_not_invalidate(
    tmp_path: Path,
) -> None:
    fixture = _fixture(tmp_path)
    wal_path = Path(f"{fixture['database']}-wal")
    wal_path.write_bytes(b"sidecar")
    completed = _execute_success(fixture)
    assert completed == 0
    _write_canonical(fixture["answer_path"], _answer_set(fixture))
    before_stat = wal_path.stat()
    wal_path.touch()
    after_stat = wal_path.stat()
    if after_stat.st_mtime_ns == before_stat.st_mtime_ns:
        import os

        os.utime(wal_path, ns=(before_stat.st_atime_ns, before_stat.st_mtime_ns + 1_000_000))
    args = SimpleNamespace(
        prepare_manifest_path=str(fixture["manifest_path"]),
        answer_set_path=str(fixture["answer_path"]),
    )
    assert runner.seal(args) == 0
    evidence = json.loads(fixture["terminal_path"].read_bytes())
    assert evidence["protocol_result"] == "SEALED_READY_FOR_INDEPENDENT_EVALUATION"
    assert (
        evidence["sidecars"]["before"][0]["mtime_ns"]
        != evidence["sidecars"]["after"][0]["mtime_ns"]
    )


def _execute_success(fixture: dict[str, Any]) -> int:
    args = fixture["args"]
    completed = subprocess.run(
        [
            sys.executable,
            str(_RUNNER_PATH),
            "prepare",
            "--authority-id",
            args.authority_id,
            "--run-id",
            args.run_id,
            "--attempt-number",
            str(args.attempt_number),
            "--execution-root",
            str(fixture["root"]),
            "--expected-head",
            args.expected_head,
            "--harness-path",
            args.harness_path,
            "--expected-harness-blob",
            args.expected_harness_blob,
            "--harness-test-path",
            args.harness_test_path,
            "--expected-harness-test-blob",
            args.expected_harness_test_blob,
            "--database-path",
            args.database_path,
            "--expected-db-sha256",
            args.expected_db_sha256,
            "--project-id",
            args.project_id,
            "--slice-id",
            args.slice_id,
            "--question-contract-path",
            args.question_contract_path,
            "--expected-question-contract-sha256",
            args.expected_question_contract_sha256,
            "--stdout-path",
            args.stdout_path,
            "--stderr-path",
            args.stderr_path,
            "--prepare-result-path",
            args.prepare_result_path,
            "--prepare-manifest-path",
            args.prepare_manifest_path,
            "--operator-input-path",
            args.operator_input_path,
            "--answer-set-path",
            args.answer_set_path,
            "--terminal-evidence-path",
            args.terminal_evidence_path,
        ],
        cwd=fixture["root"],
        check=False,
        capture_output=True,
        text=True,
    )
    fixture["manifest_path"] = Path(args.prepare_manifest_path)
    fixture["answer_path"] = Path(args.answer_set_path)
    fixture["terminal_path"] = Path(args.terminal_evidence_path)
    return completed.returncode


def test_terminal_target_no_overwrite(tmp_path: Path) -> None:
    fixture = _prepare_success(tmp_path)
    _write_canonical(fixture["answer_path"], _answer_set(fixture))
    fixture["terminal_path"].write_text("prior evidence", encoding="utf-8")
    args = SimpleNamespace(
        prepare_manifest_path=str(fixture["manifest_path"]),
        answer_set_path=str(fixture["answer_path"]),
    )
    with pytest.raises(runner.RunnerFailure, match="already exists"):
        runner.seal(args)


def test_runner_has_no_product_mutation_or_writable_database_imports() -> None:
    source = _RUNNER_PATH.read_text(encoding="utf-8")
    assert "open_database" not in source
    assert "relay_engine" not in source
    assert "shell=True" not in source
    assert 'question_id": "Q1"' not in source


def test_existing_harness_and_test_are_frozen_by_runner_scope() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    for relative_path in (
        "scripts/b4_readonly_harness.py",
        "tests/integration/test_b4_readonly_harness.py",
    ):
        expected = subprocess.run(
            ["git", "show", f"{runner._git(repository_root, 'rev-parse', 'HEAD')}:{relative_path}"],
            cwd=repository_root,
            check=True,
            capture_output=True,
        ).stdout
        assert (repository_root / relative_path).read_bytes() == expected
