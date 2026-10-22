"""Disposable end-to-end tests for B2 existing-project adoption."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path

import pytest

from relay_engine.adoption import persistence as adoption_persistence
from relay_engine.adoption import service as adoption_service
from relay_engine.adoption.models import ProjectAdoptionRecordV1
from relay_engine.adoption.persistence import load_project_adoption
from relay_engine.board import project_board, project_index
from relay_engine.board.render import render_project_board, render_project_index
from relay_engine.bootstrap_discovery.cli import main as bootstrap_main
from relay_engine.bootstrap_discovery.intake_models import (
    ConstraintAnswer,
    ConstraintState,
    HumanConfirmedConstraints,
    HumanConfirmedText,
    HumanConfirmedWorkFocusKind,
    WorkFocusKind,
)
from relay_engine.bootstrap_discovery.intake_service import (
    add_context_reference,
    canonical_manifest_bytes,
    initial_manifest,
    load_report,
    parse_manifest,
    update_human_fact,
)
from relay_engine.bootstrap_discovery.models import (
    BootstrapDiscoveryReportV1,
    RelayContractStatus,
    canonical_json_bytes,
)
from relay_engine.bootstrap_discovery.service import inspect_repository
from relay_engine.domain import ActorKind, ActorRef, ProjectId, RepositoryRef, ScopeSpec, Slice
from relay_engine.persistence import open_database
from relay_engine.persistence.errors import PersistenceIntegrityError
from relay_engine.project_slice import MutationMetadata, create_slice
from relay_engine.project_slice.origin import OriginResolutionState
from relay_engine.project_slice.service import resolve_project_origin, resolve_slice_origin
from relay_engine.repository_contract import (
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryRegistry,
    serialize_repository_registry,
)

FIXED_TIME = datetime(2026, 10, 18, 12, 0, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="example.test",
    path="owner/fixture",
)


def _git(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    return completed.stdout


def _repository(root: Path, relay_contract: str = "ABSENT") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "README.md").write_text("B2 disposable adoption fixture\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "[project]\nname = 'b2-fixture'\nversion = '0.1.0'\n", encoding="utf-8"
    )
    source = root / "src" / "fixture.py"
    source.parent.mkdir()
    source.write_text("VALUE = 1\n", encoding="utf-8")
    workflow = root / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("name: CI\n", encoding="utf-8")
    documentation = root / "docs" / "overview.md"
    documentation.parent.mkdir()
    documentation.write_text("B2 fixture documentation.\n", encoding="utf-8")
    if relay_contract == "INVALID":
        relay_dir = root / ".relay"
        relay_dir.mkdir()
        (relay_dir / "registry.json").write_text("{invalid", encoding="utf-8")
    elif relay_contract == "VALID":
        content = b"registered exact bytes\n"
        artifact_path = "docs/registered.md"
        target = root / artifact_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        artifact = RepositoryArtifactRevision(
            artifact_id="art_018f47c1-7b2c-7abc-8def-123456789003",
            revision=1,
            title="Registered fixture",
            artifact_type="DOCUMENT",
            artifact_class=RepositoryArtifactClass.LIVING_PROJECTION,
            artifact_state=RepositoryArtifactState.CURRENT,
            path=artifact_path,
            content_digest="sha256:" + hashlib.sha256(content).hexdigest(),
            human_version=None,
            updated_at=FIXED_TIME,
            scope="B2 fixture contract.",
        )
        relay_dir = root / ".relay"
        relay_dir.mkdir()
        registry = RepositoryRegistry(
            project_id=PROJECT_ID,
            repository=REPOSITORY,
            artifacts=(artifact,),
            canonical=(),
        )
        (relay_dir / "registry.json").write_bytes(serialize_repository_registry(registry))
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=Relay B2 Test",
        "-c",
        "user.email=b2-test@example.invalid",
        "commit",
        "-m",
        "fixture",
    )
    return root


def _inputs(tmp_path: Path, repository: Path) -> tuple[Path, Path]:
    report = inspect_repository(repository, FIXED_TIME)
    report_path = tmp_path / "discovery.json"
    report_path.write_bytes(canonical_json_bytes(report))
    loaded = load_report(report_path, repository)
    manifest = initial_manifest(loaded, FIXED_TIME)
    answers: tuple[tuple[str, object], ...] = (
        (
            "project_name",
            HumanConfirmedText(origin="HUMAN_CONFIRMED", value="Fixture", captured_at=FIXED_TIME),
        ),
        (
            "canonical_repository",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED",
                value="https://example.test/owner/fixture",
                captured_at=FIXED_TIME,
            ),
        ),
        (
            "project_objective",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Build the fixture.", captured_at=FIXED_TIME
            ),
        ),
        (
            "current_status",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Under development.", captured_at=FIXED_TIME
            ),
        ),
        (
            "human_objective",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Improve the fixture.", captured_at=FIXED_TIME
            ),
        ),
        (
            "constraints",
            HumanConfirmedConstraints(
                origin="HUMAN_CONFIRMED",
                value=ConstraintAnswer(state=ConstraintState.EXPLICIT_NONE, items=()),
                captured_at=FIXED_TIME,
            ),
        ),
        (
            "work_focus_kind",
            HumanConfirmedWorkFocusKind(
                origin="HUMAN_CONFIRMED",
                value=WorkFocusKind.FIRST_GOVERNED_WORK,
                captured_at=FIXED_TIME,
            ),
        ),
        (
            "work_focus",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Establish B2 coverage.", captured_at=FIXED_TIME
            ),
        ),
    )
    for name, answer in answers:
        manifest = update_human_fact(manifest, name, answer, FIXED_TIME, loaded)  # type: ignore[arg-type]
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_bytes(canonical_manifest_bytes(manifest, loaded))
    return report_path, manifest_path


def _clock() -> Callable[[], datetime]:
    values = (FIXED_TIME + timedelta(minutes=index) for index in range(10))
    iterator = iter(values)
    return lambda: next(iterator)


def _repository_state(repository: Path) -> tuple[object, ...]:
    git_directory = repository / ".git"
    tracked = _git(repository, "ls-files", "-z").decode().split("\0")
    tracked_hashes = tuple(
        (relative, hashlib.sha256((repository / relative).read_bytes()).hexdigest())
        for relative in tracked
        if relative
    )
    metadata = tuple(
        (
            name,
            hashlib.sha256((git_directory / name).read_bytes()).hexdigest()
            if (git_directory / name).exists()
            else None,
        )
        for name in ("HEAD", "config", "index")
    )
    return (
        _git(repository, "rev-parse", "HEAD"),
        _git(repository, "status", "--porcelain=v1"),
        metadata,
        tracked_hashes,
    )


def _run_adoption(
    repository: Path,
    report_path: Path,
    manifest_path: Path,
    database_path: Path,
    *,
    answers: tuple[str, ...] = ("Carlos", "ADOPT"),
) -> ProjectAdoptionRecordV1:
    answer_iterator = iter(answers)
    return adoption_service.adopt_project(
        repository=repository,
        report_path=report_path,
        manifest_path=manifest_path,
        database_path=database_path,
        input_fn=lambda _prompt: next(answer_iterator),
        output=StringIO(),
        clock=_clock(),
        allow_test_injected_input=True,
    )


def test_adoption_materializes_verified_v8_database_and_board(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    before = _repository_state(repository)

    adoption = _run_adoption(repository, report_path, manifest_path, database_path)

    assert database_path.is_file()
    assert adoption.t1 == FIXED_TIME + timedelta(minutes=1)
    assert adoption.recorded_at == adoption.t1
    assert adoption.post_adopt_report_sha256 != adoption.fresh_report_sha256
    assert adoption.post_adopt_report_state_sha256 == adoption.fresh_report_state_sha256
    with open_database(database_path, apply_migrations=False) as database:
        assert (
            database.connection.execute(
                "SELECT max(version) FROM relay_schema_migrations"
            ).fetchone()[0]
            == 8
        )
        assert load_project_adoption(database, adoption.project_id) == adoption
        for table in (
            "project_adoptions",
            "project_operational_epochs",
            "project_operational_origin_records",
        ):
            with pytest.raises(sqlite3.IntegrityError):
                database.connection.execute(f"UPDATE {table} SET payload_json = payload_json")
            with pytest.raises(sqlite3.IntegrityError):
                database.connection.execute(f"DELETE FROM {table}")
        index = project_index(database)
        assert len(index.projects) == 1
        assert index.projects[0].adoption_record == adoption
        assert "Adopted at T1" in render_project_index(index)
        board = project_board(database, adoption.project_id)
        assert board.project_origin_resolution is not None
        assert board.project_origin_resolution.origin is not None
        assert board.project_origin_resolution.origin.value == "PRE_GENESIS"
        assert len(board.cards) == 1
        assert board.cards[0].lifecycle is None
        assert board.cards[0].lane is not None
        assert board.cards[0].lane.value == "NOT_STARTED"
        assert board.cards[0].origin_resolution.origin is not None
        assert board.cards[0].origin_resolution.origin.value == "NATIVE_RELAY"
        rendered = render_project_board(board)
        assert "CURRENT" in rendered
        assert "NEXT" in rendered
        assert "LATER" in rendered
        assert "BLOCKED" in rendered
        assert "none established at T1" in rendered
        assert "B3 refinement required before lifecycle" in rendered
        later_slice = Slice(
            id="slc_018f47c1-7b2c-7abc-8def-123456789008",
            project_id=adoption.project_id,
            title="Later governed work",
            scope=ScopeSpec(in_scope=("Continue after adoption.",), out_of_scope=()),
            acceptance_criteria=(),
        )
        actor = ActorRef(
            id="act_018f47c1-7b2c-7abc-8def-123456789009",
            kind=ActorKind.HUMAN,
            display_name="Carlos",
        )
        create_slice(
            database,
            later_slice,
            MutationMetadata(
                actor=actor,
                occurred_at=adoption.t1 + timedelta(minutes=5),
                reason="Normal post-T1 Slice creation.",
            ),
        )
        later_origin = resolve_slice_origin(database, later_slice.id, adoption.project_id)
        assert later_origin.origin is not None
        assert later_origin.origin.value == "NATIVE_RELAY"
    assert _repository_state(repository) == before


def test_relay_bootstrap_adopt_cli_publishes_only_after_exact_confirmation(
    tmp_path: Path,
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    answers = iter(("Carlos", "ADOPT"))
    prompts: list[str] = []
    output = StringIO()
    errors = StringIO()

    def input_answer(prompt: str) -> str:
        prompts.append(prompt)
        return next(answers)

    result = bootstrap_main(
        [
            "adopt",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--manifest",
            str(manifest_path),
            "--database",
            str(database_path),
        ],
        input_fn=input_answer,
        output_stream=output,
        error_stream=errors,
        clock=_clock(),
    )

    assert result == 0
    assert database_path.is_file()
    assert any("Type exactly ADOPT" in prompt for prompt in prompts)
    rendered = output.getvalue()
    assert "Project objective: Build the fixture." in rendered
    assert "Human-confirmed current status: Under development." in rendered
    assert "Manifest signals:" in rendered
    assert "Language signals:" in rendered
    assert "PYTHON: 1 tracked source file(s)" in rendered
    assert "CI configuration:" in rendered
    assert ".github/workflows/ci.yml" in rendered
    assert "Documentation signals:" in rendered
    assert "docs/overview.md" in rendered
    assert (
        "I attest that the software project represented by example.test/owner/fixture" in rendered
    )
    assert "existed as a project before this ADOPT decision" in rendered
    assert "Adoption database published:" in rendered
    assert errors.getvalue() == ""


def test_valid_relay_contract_reuses_project_and_repository_identity(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout", relay_contract="VALID")
    report_path, manifest_path = _inputs(tmp_path, repository)
    report = inspect_repository(repository, FIXED_TIME)
    assert report.relay_contract.status is RelayContractStatus.VALID

    adoption = _run_adoption(repository, report_path, manifest_path, tmp_path / "relay.sqlite")

    assert adoption.project_id == PROJECT_ID
    assert adoption.repository == REPOSITORY


def test_repository_ref_normalization_is_deterministic_and_rejects_unsafe_forms() -> None:
    normalized = adoption_service.normalize_repository_ref(
        "https://EXAMPLE.test/Owner/Fixture.git",
        "repo_018f47c1-7b2c-7abc-8def-123456789002",
    )

    assert normalized.host == "example.test"
    assert normalized.path == "Owner/Fixture"
    for locator in (
        "https://user:secret@example.test/owner/fixture",
        "https://example.test/owner/../fixture",
        "https://example.test/owner/fixture?ref=main",
        "https://example.test:/owner/fixture",
        "https://[2001:db8::1/owner/fixture",
        "example.test:8443/owner/fixture",
        "git@example.test:owner/fixture.git",
    ):
        with pytest.raises(adoption_service.AdoptionError) as error:
            adoption_service.normalize_repository_ref(
                locator,
                "repo_018f47c1-7b2c-7abc-8def-123456789002",
            )
        assert error.value.code == "ADOPTION_CANONICAL_REPOSITORY_INVALID"


@pytest.mark.parametrize(
    ("locator", "expected_code"),
    (
        ("https:/example.test/owner/fixture", "ADOPTION_CANONICAL_REPOSITORY_INVALID"),
        ("https://example.test:not-a-port/owner/fixture", "ADOPTION_CANONICAL_REPOSITORY_INVALID"),
        ("https://example.test:/owner/fixture", "ADOPTION_CANONICAL_REPOSITORY_INVALID"),
        ("https://[2001:db8::1/owner/fixture", "ADOPTION_MANIFEST_INVALID"),
        ("example.test:8443/owner/fixture", "ADOPTION_CANONICAL_REPOSITORY_INVALID"),
    ),
)
def test_malformed_repository_locator_fails_before_human_adoption_or_publication(
    tmp_path: Path, locator: str, expected_code: str
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    manifest_payload = json.loads(manifest_path.read_bytes())
    manifest_payload["human_facts"]["canonical_repository"]["value"] = locator
    manifest_path.write_text(
        json.dumps(manifest_payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    database_path = tmp_path / "relay.sqlite"
    prompts: list[str] = []

    def unexpected_human_input(prompt: str) -> str:
        prompts.append(prompt)
        raise AssertionError("invalid repository locator reached Human adoption")

    with pytest.raises(adoption_service.AdoptionError) as error:
        adoption_service.adopt_project(
            repository=repository,
            report_path=report_path,
            manifest_path=manifest_path,
            database_path=database_path,
            input_fn=unexpected_human_input,
            output=StringIO(),
            clock=_clock(),
            allow_test_injected_input=True,
        )

    assert error.value.code == expected_code
    assert prompts == []
    assert not database_path.exists()
    assert not tuple(tmp_path.glob(".relay.sqlite.adoption-*"))


def test_valid_relay_contract_conflict_is_rejected(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout", relay_contract="VALID")
    report_path, manifest_path = _inputs(tmp_path, repository)
    payload = json.loads(manifest_path.read_bytes())
    payload["human_facts"]["canonical_repository"]["value"] = "https://example.test/owner/other"
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, tmp_path / "relay.sqlite")

    assert error.value.code == "ADOPTION_IDENTITY_CONFLICT"


def test_clean_head_drift_is_disclosed_and_human_adopted(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    (repository / "README.md").write_text("a newer clean state\n", encoding="utf-8")
    _git(repository, "add", "README.md")
    _git(
        repository,
        "-c",
        "user.name=Relay B2 Test",
        "-c",
        "user.email=b2-test@example.invalid",
        "commit",
        "-m",
        "clean drift",
    )

    adoption = _run_adoption(repository, report_path, manifest_path, tmp_path / "relay.sqlite")

    assert adoption.drift
    assert any(item.pointer == "/git" for item in adoption.drift)
    assert adoption.fresh_repository_fingerprint.dirty is False
    assert (
        adoption.fresh_repository_fingerprint.head_sha
        == _git(repository, "rev-parse", "HEAD").decode().strip()
    )


def test_invalid_relay_contract_fails_without_database(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout", relay_contract="INVALID")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_RELAY_CONTRACT_INVALID"
    assert not database_path.exists()


def test_dirty_repository_fails_before_human_adopt(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    (repository / "README.md").write_text("dirty\n", encoding="utf-8")
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_REPOSITORY_DIRTY"
    assert not database_path.exists()


def test_non_exact_adopt_token_publishes_nothing(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(
            repository,
            report_path,
            manifest_path,
            database_path,
            answers=("Carlos", "adopt"),
        )

    assert error.value.code == "ADOPTION_NOT_CONFIRMED"
    assert not database_path.exists()


@pytest.mark.parametrize("interrupt_at", (0, 1))
@pytest.mark.parametrize("interrupt_type", (EOFError, KeyboardInterrupt))
def test_interrupted_human_decision_publishes_nothing(
    tmp_path: Path,
    interrupt_at: int,
    interrupt_type: type[EOFError] | type[KeyboardInterrupt],
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    prompt_index = 0

    def interrupted_input(_prompt: str) -> str:
        nonlocal prompt_index
        current_index = prompt_index
        prompt_index += 1
        if current_index == interrupt_at:
            raise interrupt_type
        return "Carlos"

    with pytest.raises(adoption_service.AdoptionError) as error:
        adoption_service.adopt_project(
            repository=repository,
            report_path=report_path,
            manifest_path=manifest_path,
            database_path=database_path,
            input_fn=interrupted_input,
            output=StringIO(),
            clock=_clock(),
            allow_test_injected_input=True,
        )

    assert error.value.code == "ADOPTION_NOT_CONFIRMED"
    assert not database_path.exists()
    assert not tuple(tmp_path.glob(".relay.sqlite.adoption-*"))


def test_noninteractive_adoption_cli_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    errors = StringIO()

    monkeypatch.setattr(adoption_service, "_stdin_is_interactive", lambda: False)
    result = bootstrap_main(
        [
            "adopt",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--manifest",
            str(manifest_path),
            "--database",
            str(database_path),
        ],
        error_stream=errors,
        clock=_clock(),
    )

    assert result == 2
    assert "ADOPTION_NOT_CONFIRMED" in errors.getvalue()
    assert not database_path.exists()


def test_b1_report_digest_mismatch_is_rejected_before_human_decision(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    payload = json.loads(manifest_path.read_bytes())
    payload["input_report"]["sha256"] = "sha256:" + "0" * 64
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_REPORT_MISMATCH"
    assert not database_path.exists()


def test_b1_context_reference_tampering_is_rejected_before_adoption(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    loaded = load_report(report_path, repository)
    manifest = parse_manifest(manifest_path.read_bytes(), loaded)
    entry_index = next(
        index
        for index, entry in enumerate(loaded.report.documentation_files)
        if entry.sha256 is not None and entry.inspection_state.value == "READ"
    )
    pointer = f"/documentation_files/{entry_index}"
    selected = add_context_reference(manifest, pointer, FIXED_TIME, loaded)
    payload = json.loads(canonical_manifest_bytes(selected, loaded))
    payload["context_references"][0]["sha256"] = "sha256:" + "0" * 64
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_REPORT_MISMATCH"
    assert not database_path.exists()


def test_complete_post_adopt_report_change_aborts_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    original_inspect = adoption_service.inspect_repository
    calls = 0

    def changed_second_report(root: Path, observed_at: datetime):
        nonlocal calls
        calls += 1
        report = original_inspect(root, observed_at)
        if calls == 2:
            return report.model_copy(update={"language_signals": ()})
        return report

    monkeypatch.setattr(adoption_service, "inspect_repository", changed_second_report)
    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert calls == 2
    assert error.value.code == "ADOPTION_STATE_CHANGED"
    assert not database_path.exists()


def test_final_repository_identity_change_discards_staged_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"

    def reject_final_check(_root: Path, _report: BootstrapDiscoveryReportV1) -> bool:
        return False

    monkeypatch.setattr(adoption_service, "_final_repository_check", reject_final_check)

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_STATE_CHANGED"
    assert not database_path.exists()
    assert not tuple(tmp_path.glob(".relay.sqlite.adoption-*"))


def test_b1_observed_value_tampering_is_rejected_before_adopt(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    payload = json.loads(manifest_path.read_bytes())
    payload["observed"]["dirty"]["value"] = True
    manifest_path.write_text(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    database_path = tmp_path / "relay.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_MANIFEST_INVALID"
    assert not database_path.exists()


@pytest.mark.parametrize(
    "stage",
    (
        "_insert_initial_project",
        "_insert_initial_slice",
        "_insert_adoption_from_connection",
        "_insert_project_epoch_from_connection",
        "_insert_project_origin_from_connection",
        "append_project_native_origin_from_connection",
        "_verify_materialized_database",
        "_consolidate_sqlite",
    ),
)
def test_materialization_failure_at_each_stage_publishes_nothing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"

    def fail(*_args: object, **_kwargs: object) -> None:
        raise PersistenceIntegrityError("injected disposable failure")

    monkeypatch.setattr(adoption_persistence, stage, fail)
    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_MATERIALIZATION_FAILED"
    assert not database_path.exists()
    assert not tuple(tmp_path.glob(".relay.sqlite.adoption-*"))


def test_publication_collision_preserves_existing_target_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"

    def collide(
        _source: os.PathLike[str] | str,
        target: os.PathLike[str] | str,
    ) -> None:
        Path(target).write_bytes(b"concurrent target")
        raise FileExistsError

    monkeypatch.setattr(adoption_persistence.os, "link", collide)
    with pytest.raises(adoption_service.AdoptionError) as error:
        _run_adoption(repository, report_path, manifest_path, database_path)

    assert error.value.code == "ADOPTION_DATABASE_EXISTS"
    assert database_path.read_bytes() == b"concurrent target"


def test_sidecar_collision_is_rejected_before_decision(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    Path(str(database_path) + "-wal").write_bytes(b"keep")

    with pytest.raises(adoption_service.AdoptionError) as error:
        adoption_service.prepare_adoption_plan(
            repository=repository,
            report_path=report_path,
            manifest_path=manifest_path,
            database_path=database_path,
            observed_at=FIXED_TIME,
        )

    assert error.value.code == "ADOPTION_DATABASE_UNSAFE"
    assert Path(str(database_path) + "-wal").read_bytes() == b"keep"


def test_strict_and_adoption_origin_modes_never_fall_back_or_mix(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    database_path = tmp_path / "relay.sqlite"
    adoption = _run_adoption(repository, report_path, manifest_path, database_path)

    with open_database(database_path, apply_migrations=False) as database:
        connection = database.connection
        strict_epoch_id = "ohe_018f47c1-7b2c-7abc-8def-123456789004"
        digest = "sha256:" + "a" * 64
        connection.execute(
            """INSERT INTO operational_history_epochs(
                epoch_slot, epoch_id, genesis_cut_at, source_commit_sha,
                genesis_package_artifact_id, genesis_package_path,
                genesis_package_digest, package_acceptance_artifact_id,
                package_acceptance_digest, epoch_digest, payload_json
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                strict_epoch_id,
                adoption.t1.isoformat().replace("+00:00", "Z"),
                adoption.fresh_repository_fingerprint.head_sha,
                "art_018f47c1-7b2c-7abc-8def-123456789005",
                "docs/genesis.json",
                digest,
                "art_018f47c1-7b2c-7abc-8def-123456789006",
                digest,
                digest,
                "{}",
            ),
        )
        connection.execute(
            """INSERT INTO operational_origin_records(
                record_id, subject_type, subject_id, project_id, record_kind,
                origin, epoch_id, epoch_digest, supersedes_record_id,
                supersedes_record_digest, recorded_at, recorded_by_json,
                establishing_authority_id, correction_authorization_id,
                correction_authorization_digest, rationale, record_digest, payload_json
            ) VALUES (?, 'PROJECT', ?, ?, 'INITIAL', 'PRE_GENESIS', ?, ?,
                NULL, NULL, ?, '{}', 'fixture', NULL, NULL, NULL, ?, '{}')""",
            (
                "oor_018f47c1-7b2c-7abc-8def-123456789007",
                adoption.project_id,
                adoption.project_id,
                strict_epoch_id,
                digest,
                adoption.t1.isoformat().replace("+00:00", "Z"),
                digest,
            ),
        )

        mixed = resolve_project_origin(database, adoption.project_id)
        assert mixed.state is OriginResolutionState.NOT_ESTABLISHED
        assert mixed.diagnostic is not None
        assert mixed.diagnostic.code.value == "INVALID_ORIGIN_CHAIN"

        connection.execute("PRAGMA foreign_keys = OFF")
        connection.execute("DROP TRIGGER project_operational_epochs_no_delete")
        connection.execute(
            "DELETE FROM project_operational_epochs WHERE project_id = ?",
            (adoption.project_id,),
        )
        missing_epoch = resolve_project_origin(database, adoption.project_id)
        assert missing_epoch.state is OriginResolutionState.NOT_ESTABLISHED
        assert missing_epoch.diagnostic is not None
        assert missing_epoch.diagnostic.code.value == "EPOCH_NOT_ESTABLISHED"


def test_existing_output_and_inside_repository_paths_are_rejected(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "checkout")
    report_path, manifest_path = _inputs(tmp_path, repository)
    inside = repository / "adoption.sqlite"

    with pytest.raises(adoption_service.AdoptionError) as inside_error:
        adoption_service.prepare_adoption_plan(
            repository=repository,
            report_path=report_path,
            manifest_path=manifest_path,
            database_path=inside,
            observed_at=FIXED_TIME,
        )
    assert inside_error.value.code == "ADOPTION_DATABASE_UNSAFE"

    existing = tmp_path / "existing.sqlite"
    existing.write_bytes(b"preserve me")
    with pytest.raises(adoption_service.AdoptionError) as exists_error:
        adoption_service.prepare_adoption_plan(
            repository=repository,
            report_path=report_path,
            manifest_path=manifest_path,
            database_path=existing,
            observed_at=FIXED_TIME,
        )
    assert exists_error.value.code == "ADOPTION_DATABASE_EXISTS"
    assert existing.read_bytes() == b"preserve me"
