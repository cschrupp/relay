"""Integrity, workflow, and output-safety tests for B1 Human intake."""

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any

import pytest

from relay_engine.bootstrap_discovery.cli import main
from relay_engine.bootstrap_discovery.intake_models import (
    AdoptionManifestV1,
    ConstraintAnswer,
    ConstraintState,
    HumanConfirmedConstraints,
    HumanConfirmedText,
    HumanConfirmedWorkFocusKind,
    HumanFacts,
    ManifestStatus,
    UnresolvedFact,
    WorkFocusKind,
)
from relay_engine.bootstrap_discovery.intake_service import (
    IntakeError,
    LoadedReport,
    add_context_reference,
    add_review_note,
    canonical_manifest_bytes,
    checkpoint_draft,
    documentation_groups,
    initial_manifest,
    load_report,
    parse_manifest,
    read_existing_draft,
    update_human_fact,
    validate_manifest,
    write_new_draft,
)
from relay_engine.bootstrap_discovery.models import (
    InspectionState,
)
from relay_engine.bootstrap_discovery.models import (
    canonical_json_bytes as canonical_report_bytes,
)
from relay_engine.bootstrap_discovery.service import inspect_repository

FIXED_TIME = datetime(2026, 10, 17, 12, 30, tzinfo=UTC)


def _git(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    return completed.stdout


def _repository(root: Path, *, oversized_readme: bool = False) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    readme = b"relay intake fixture\n"
    if oversized_readme:
        readme = b"x" * (1024 * 1024 + 1)
    files = {
        "README.md": readme,
        "CONTRIBUTING.md": b"contribution guide\n",
        "docs/guide/overview.md": b"overview\n",
        "pyproject.toml": b"[project]\nname = 'fixture'\n",
        ".github/workflows/ci.yml": b"name: CI\n",
        "src/app.py": b"print('observed')\n",
    }
    for relative_path, content in files.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=Relay Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "fixture",
    )
    return root


def _loaded_report(tmp_path: Path, *, oversized_readme: bool = False) -> LoadedReport:
    repository = _repository(tmp_path / "repo", oversized_readme=oversized_readme)
    report = inspect_repository(repository, FIXED_TIME)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.parent.mkdir()
    report_path.write_bytes(canonical_report_bytes(report))
    return load_report(report_path, repository)


def _complete_manifest(loaded: LoadedReport) -> AdoptionManifestV1:
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
                origin="HUMAN_CONFIRMED", value="Build a fixture.", captured_at=FIXED_TIME
            ),
        ),
        (
            "current_status",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="In progress.", captured_at=FIXED_TIME
            ),
        ),
        (
            "human_objective",
            HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Make progress.", captured_at=FIXED_TIME
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
                origin="HUMAN_CONFIRMED", value="Review the first task.", captured_at=FIXED_TIME
            ),
        ),
    )
    for field_name, fact in answers:
        manifest = update_human_fact(
            manifest,
            field_name,
            fact,  # type: ignore[arg-type]
            FIXED_TIME,
            loaded,
        )
    return manifest


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _read_only_snapshot(repository: Path) -> tuple[str, str, tuple[tuple[str, str], ...]]:
    git_dir = repository / ".git"
    metadata = []
    for name in ("HEAD", "config", "index"):
        target = git_dir / name
        digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else "absent"
        metadata.append((name, digest))
    tracked_paths = _git(repository, "ls-files", "-z").decode().split("\0")
    tracked = tuple(
        (path, hashlib.sha256((repository / path).read_bytes()).hexdigest())
        for path in tracked_paths
        if path
    )
    return (
        _git(repository, "rev-parse", "HEAD").decode().strip(),
        repr(metadata),
        tracked,
    )


def test_manifest_binds_exact_report_and_starts_incomplete(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)

    manifest = initial_manifest(loaded, FIXED_TIME)
    decoded = json.loads(canonical_manifest_bytes(manifest, loaded))

    assert manifest.preparation_status is ManifestStatus.INCOMPLETE
    assert len(manifest.unresolved_items) == 8
    assert decoded["input_report"]["sha256"] == loaded.sha256
    assert decoded["observed"]["dirty"]["value"] is False
    assert decoded["observed"]["dirty"]["report_pointer"] == "/git/dirty"
    assert decoded["observed"]["relay_contract"]["value"] == "ABSENT"
    assert decoded["observed"]["relay_contract"]["report_pointer"] == "/relay_contract/status"
    assert canonical_manifest_bytes(manifest, loaded) == canonical_manifest_bytes(
        initial_manifest(loaded, FIXED_TIME), loaded
    )


def test_all_explicit_human_facts_derive_ready_status(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)

    manifest = _complete_manifest(loaded)

    assert manifest.preparation_status is ManifestStatus.READY_FOR_B2_REVIEW
    assert not manifest.unresolved_items
    assert manifest.human_facts.constraints.value.state is ConstraintState.EXPLICIT_NONE  # type: ignore[union-attr]


def test_blank_constraints_remain_unresolved_but_explicit_none_resolves(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)

    unresolved = update_human_fact(
        manifest,
        "constraints",
        UnresolvedFact(origin="UNRESOLVED", reason="Need to ask the Human."),
        FIXED_TIME,
        loaded,
    )
    resolved = update_human_fact(
        unresolved,
        "constraints",
        HumanConfirmedConstraints(
            origin="HUMAN_CONFIRMED",
            value=ConstraintAnswer(state=ConstraintState.EXPLICIT_NONE, items=()),
            captured_at=FIXED_TIME,
        ),
        FIXED_TIME,
        loaded,
    )
    with_items = update_human_fact(
        resolved,
        "constraints",
        HumanConfirmedConstraints(
            origin="HUMAN_CONFIRMED",
            value=ConstraintAnswer(
                state=ConstraintState.ITEMS,
                items=("No network calls", "No database writes"),
            ),
            captured_at=FIXED_TIME,
        ),
        FIXED_TIME,
        loaded,
    )

    assert unresolved.preparation_status is ManifestStatus.INCOMPLETE
    assert resolved.preparation_status is ManifestStatus.INCOMPLETE
    assert all(item.key.value != "CONSTRAINTS" for item in resolved.unresolved_items)
    assert with_items.human_facts.constraints.value.items == (  # type: ignore[union-attr]
        "No network calls",
        "No database writes",
    )


def test_canonical_repository_is_semantic_and_rejects_uri_credentials() -> None:
    with pytest.raises(ValueError):
        HumanFacts(
            project_name=HumanConfirmedText(
                origin="HUMAN_CONFIRMED", value="Name", captured_at=FIXED_TIME
            ),
            canonical_repository=HumanConfirmedText(
                origin="HUMAN_CONFIRMED",
                value="https://user:secret@example.test/repo",
                captured_at=FIXED_TIME,
            ),
            project_objective=UnresolvedFact(origin="UNRESOLVED", reason="x"),
            current_status=UnresolvedFact(origin="UNRESOLVED", reason="x"),
            human_objective=UnresolvedFact(origin="UNRESOLVED", reason="x"),
            constraints=UnresolvedFact(origin="UNRESOLVED", reason="x"),
            work_focus_kind=UnresolvedFact(origin="UNRESOLVED", reason="x"),
            work_focus=UnresolvedFact(origin="UNRESOLVED", reason="x"),
        )


def test_documentation_groups_are_stable_and_expand_all_paths(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)

    groups = documentation_groups(loaded)

    assert [group.key for group in groups] == ["orientation", "docs/guide"]
    assert groups[0].preview == ("CONTRIBUTING.md", "README.md")
    assert groups[1].files[0][0] == "docs/guide/overview.md"


def test_configured_remote_does_not_fill_human_canonical_repository(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "remote", "add", "origin", "https://example.test/observed/remote.git")
    report = inspect_repository(repository, FIXED_TIME)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.parent.mkdir()
    report_path.write_bytes(canonical_report_bytes(report))
    loaded = load_report(report_path, repository)
    manifest = initial_manifest(loaded, FIXED_TIME)

    assert isinstance(manifest.human_facts.canonical_repository, UnresolvedFact)
    confirmed = _complete_manifest(loaded)
    serialized = json.loads(canonical_manifest_bytes(confirmed, loaded))
    assert serialized["observed"]["remotes"]["value"][0]["fetch_url"] == (
        "https://example.test/observed/remote.git"
    )
    assert serialized["human_facts"]["canonical_repository"]["value"] == (
        "https://example.test/owner/fixture"
    )


def test_observed_boolean_cannot_be_tampered_even_with_valid_digest_and_pointer(
    tmp_path: Path,
) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    payload = json.loads(canonical_manifest_bytes(manifest, loaded))
    payload["observed"]["dirty"]["value"] = 1

    with pytest.raises(IntakeError, match="does not equal") as error:
        parse_manifest(_canonical_json(payload), loaded)

    assert error.value.code == "OBSERVED_VALUE_MISMATCH"


def test_unresolved_observed_pointer_fails_closed(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    payload = json.loads(canonical_manifest_bytes(manifest, loaded))
    payload["observed"]["dirty"]["report_pointer"] = "/git/not-a-field"

    with pytest.raises(IntakeError) as error:
        parse_manifest(_canonical_json(payload), loaded)

    assert error.value.code == "OBSERVED_POINTER_MISMATCH"


def test_failed_checkpoint_preserves_existing_tampered_draft_bytes(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    output = tmp_path / "draft.json"
    original_bytes = canonical_manifest_bytes(manifest, loaded)
    output.write_bytes(original_bytes)
    altered_fact = manifest.observed.dirty.model_copy(update={"value": True})
    altered_projection = manifest.observed.model_copy(update={"dirty": altered_fact})
    altered_manifest = manifest.model_copy(update={"observed": altered_projection})

    with pytest.raises(IntakeError) as error:
        checkpoint_draft(output, altered_manifest, loaded)

    assert error.value.code == "OBSERVED_VALUE_MISMATCH"
    assert output.read_bytes() == original_bytes


def test_checkpoint_revalidates_existing_bytes_before_replacement(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    output = tmp_path / "draft.json"
    write_new_draft(output, manifest, loaded)
    edited = json.loads(output.read_bytes())
    edited["observed"]["dirty"]["value"] = True
    tampered_bytes = _canonical_json(edited)
    output.write_bytes(tampered_bytes)
    candidate = update_human_fact(
        manifest,
        "project_name",
        HumanConfirmedText(origin="HUMAN_CONFIRMED", value="Fixture", captured_at=FIXED_TIME),
        FIXED_TIME,
        loaded,
    )

    with pytest.raises(IntakeError) as error:
        checkpoint_draft(output, candidate, loaded)

    assert error.value.code == "OBSERVED_VALUE_MISMATCH"
    assert output.read_bytes() == tampered_bytes


def test_valid_report_resumes_byte_identically(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    output = tmp_path / "draft.json"
    write_new_draft(output, manifest, loaded)

    resumed = read_existing_draft(output, loaded)

    assert canonical_manifest_bytes(resumed, loaded) == output.read_bytes()


def test_report_digest_mismatch_does_not_change_existing_draft(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    output = tmp_path / "draft.json"
    write_new_draft(output, manifest, loaded)
    original = output.read_bytes()
    alternate_report = inspect_repository(loaded.repository_root, FIXED_TIME.replace(minute=31))
    alternate_path = tmp_path / "reports" / "other.json"
    alternate_path.write_bytes(canonical_report_bytes(alternate_report))
    alternate = load_report(alternate_path, loaded.repository_root)

    with pytest.raises(IntakeError) as error:
        read_existing_draft(output, alternate)

    assert error.value.code == "REPORT_DIGEST_MISMATCH"
    assert output.read_bytes() == original


def test_context_reference_matches_report_path_digest_and_read_state(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    read_entry = next(
        entry
        for entry in loaded.report.documentation_files
        if entry.inspection_state is InspectionState.READ
    )
    pointer = f"/documentation_files/{loaded.report.documentation_files.index(read_entry)}"

    selected = add_context_reference(manifest, pointer, FIXED_TIME, loaded)

    assert len(selected.context_references) == 1
    payload = json.loads(canonical_manifest_bytes(selected, loaded))
    payload["context_references"][0]["relative_path"] = "docs/forged.md"
    with pytest.raises(IntakeError) as error:
        parse_manifest(_canonical_json(payload), loaded)
    assert error.value.code == "CONTEXT_REFERENCE_MISMATCH"


def test_context_pointer_digest_and_inspection_state_are_all_bound(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)
    entry = next(
        item
        for item in loaded.report.documentation_files
        if item.inspection_state is InspectionState.READ
    )
    pointer = f"/documentation_files/{loaded.report.documentation_files.index(entry)}"
    selected = add_context_reference(manifest, pointer, FIXED_TIME, loaded)
    reference = selected.context_references[0]

    bad_pointer = selected.model_copy(
        update={
            "context_references": (
                reference.model_copy(update={"report_pointer": "/documentation_files/99"}),
            )
        }
    )
    bad_digest = selected.model_copy(
        update={
            "context_references": (reference.model_copy(update={"sha256": "sha256:" + "0" * 64}),)
        }
    )
    bad_state = selected.model_copy(
        update={
            "context_references": (
                reference.model_copy(update={"inspection_state": InspectionState.UNREADABLE}),
            )
        }
    )

    for candidate in (bad_pointer, bad_digest, bad_state):
        with pytest.raises(IntakeError) as error:
            validate_manifest(candidate, loaded)
        assert error.value.code == "CONTEXT_REFERENCE_MISMATCH"


def test_oversized_documentation_cannot_be_selected_as_read_context(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path, oversized_readme=True)
    manifest = initial_manifest(loaded, FIXED_TIME)
    readme_index = next(
        index
        for index, entry in enumerate(loaded.report.documentation_files)
        if entry.relative_path == "README.md"
    )

    with pytest.raises(IntakeError) as error:
        add_context_reference(
            manifest,
            f"/documentation_files/{readme_index}",
            FIXED_TIME,
            loaded,
        )

    assert error.value.code == "CONTEXT_NOT_READABLE"


def test_review_note_is_commentary_and_does_not_change_readiness(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    manifest = initial_manifest(loaded, FIXED_TIME)

    noted = add_review_note(
        manifest, "/git/dirty", "Please refresh this observation.", FIXED_TIME, loaded
    )

    assert noted.preparation_status is ManifestStatus.INCOMPLETE
    assert noted.unresolved_items == manifest.unresolved_items
    assert len(noted.review_notes) == 1


def test_strict_report_rejects_duplicate_json_keys_and_unknown_fields(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    repository = loaded.repository_root
    report_path = tmp_path / "duplicate.json"
    report_path.write_bytes(b'{"format":"relay-bootstrap-discovery","format":"bad"}')

    with pytest.raises(IntakeError) as duplicate_error:
        load_report(report_path, repository)
    assert duplicate_error.value.code == "REPORT_INVALID"

    report_payload = json.loads(loaded.raw_bytes)
    report_payload["unreviewed"] = True
    report_path.write_bytes(_canonical_json(report_payload))
    with pytest.raises(IntakeError) as unknown_error:
        load_report(report_path, repository)
    assert unknown_error.value.code == "REPORT_INVALID"

    report_payload.pop("unreviewed")
    report_payload["schema_version"] = 2
    report_path.write_bytes(_canonical_json(report_payload))
    with pytest.raises(IntakeError) as version_error:
        load_report(report_path, repository)
    assert version_error.value.code == "REPORT_INVALID"


def test_intake_cli_checkpoints_after_interruption_and_resumes_to_ready(
    tmp_path: Path,
) -> None:
    loaded = _loaded_report(tmp_path)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.write_bytes(loaded.raw_bytes)
    output_path = tmp_path / "external" / "adoption.json"
    output_path.parent.mkdir()
    repository = loaded.repository_root
    before = _read_only_snapshot(repository)
    answers = iter(["Fixture Project"])

    def interrupt_after_first_answer(prompt: str) -> str:
        del prompt
        try:
            return next(answers)
        except StopIteration as error:
            raise EOFError from error

    first_stdout = StringIO()
    first_stderr = StringIO()

    paused_result = main(
        [
            "intake",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
        ],
        input_fn=interrupt_after_first_answer,
        output_stream=first_stdout,
        error_stream=first_stderr,
        clock=lambda: FIXED_TIME,
    )

    assert paused_result == 0
    paused = read_existing_draft(output_path, loaded)
    assert paused.human_facts.project_name.origin == "HUMAN_CONFIRMED"
    assert "INCOMPLETE" in output_path.read_text(encoding="utf-8")

    resume_answers = iter(
        [
            "https://example.test/owner/fixture",
            "A test project.",
            "Prepare a governed backlog.",
            "Existing local repository.",
            "none",
            "2",
            "Review the next task.",
            "orientation",
            "1",
            "",  # Finish optional context selection.
            *([""] * 8),  # Keep all eight answers at review.
            "",  # Skip optional note.
        ]
    )
    second_stdout = StringIO()
    second_stderr = StringIO()
    resumed_result = main(
        [
            "intake",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
            "--resume",
        ],
        input_fn=lambda prompt: next(resume_answers),
        output_stream=second_stdout,
        error_stream=second_stderr,
        clock=lambda: FIXED_TIME,
    )

    assert resumed_result == 0, second_stderr.getvalue()
    final_manifest = read_existing_draft(output_path, loaded)
    assert final_manifest.preparation_status is ManifestStatus.READY_FOR_B2_REVIEW
    assert final_manifest.context_references[0].relative_path == "CONTRIBUTING.md"
    assert "not adopted or operational state" in second_stdout.getvalue()
    assert _read_only_snapshot(repository) == before


def test_intake_cli_keeps_explicit_uncertainty_unresolved(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.write_bytes(loaded.raw_bytes)
    output_path = tmp_path / "external.json"
    responses = iter(["not sure"])

    def answer_then_interrupt(prompt: str) -> str:
        del prompt
        try:
            return next(responses)
        except StopIteration as error:
            raise EOFError from error

    result = main(
        [
            "intake",
            "--repository",
            str(loaded.repository_root),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
        ],
        input_fn=answer_then_interrupt,
        clock=lambda: FIXED_TIME,
    )

    manifest = read_existing_draft(output_path, loaded)
    assert result == 0
    assert isinstance(manifest.human_facts.project_name, UnresolvedFact)
    assert manifest.preparation_status is ManifestStatus.INCOMPLETE


def test_intake_cli_refuses_inside_repository_and_existing_output(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.write_bytes(loaded.raw_bytes)
    repository = loaded.repository_root
    inside = repository / "manifest.json"
    stderr = StringIO()

    result = main(
        [
            "intake",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--output",
            str(inside),
        ],
        input_fn=lambda _: "unused",
        error_stream=stderr,
        clock=lambda: FIXED_TIME,
    )
    assert result == 2
    assert "OUTPUT_INSIDE_REPOSITORY" in stderr.getvalue()
    assert not inside.exists()

    output_path = tmp_path / "external.json"
    output_path.write_bytes(b"preserve me")
    stderr = StringIO()
    collision = main(
        [
            "intake",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
        ],
        input_fn=lambda _: "unused",
        error_stream=stderr,
        clock=lambda: FIXED_TIME,
    )
    assert collision == 2
    assert "OUTPUT_EXISTS" in stderr.getvalue()
    assert output_path.read_bytes() == b"preserve me"


def test_intake_cli_refuses_stdout_manifest_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    loaded = _loaded_report(tmp_path)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.write_bytes(loaded.raw_bytes)
    monkeypatch.chdir(tmp_path)
    stderr = StringIO()

    result = main(
        [
            "intake",
            "--repository",
            str(loaded.repository_root),
            "--report",
            str(report_path),
            "--output",
            "-",
        ],
        error_stream=stderr,
    )

    assert result == 2
    assert "STDOUT_UNSUPPORTED" in stderr.getvalue()
    assert not (tmp_path / "-").exists()


def test_intake_cli_refuses_symlink_output_and_report_root_mismatch(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.write_bytes(loaded.raw_bytes)
    target = tmp_path / "target.json"
    target.write_bytes(b"leave unchanged")
    symlink = tmp_path / "symlink.json"
    symlink.symlink_to(target)
    stderr = StringIO()

    symlink_result = main(
        [
            "intake",
            "--repository",
            str(loaded.repository_root),
            "--report",
            str(report_path),
            "--output",
            str(symlink),
        ],
        error_stream=stderr,
    )
    assert symlink_result == 2
    assert "OUTPUT_UNSAFE" in stderr.getvalue()
    assert target.read_bytes() == b"leave unchanged"

    other = _repository(tmp_path / "other")
    stderr = StringIO()
    mismatch_result = main(
        [
            "intake",
            "--repository",
            str(other),
            "--report",
            str(report_path),
            "--output",
            str(tmp_path / "mismatch.json"),
        ],
        error_stream=stderr,
    )
    assert mismatch_result == 2
    assert "REPORT_REPOSITORY_MISMATCH" in stderr.getvalue()


def test_intake_displays_dirty_and_invalid_relay_contract_observations(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    (repository / "README.md").write_text("uncommitted edit\n", encoding="utf-8")
    relay_dir = repository / ".relay"
    relay_dir.mkdir()
    (relay_dir / "registry.json").write_text("{invalid", encoding="utf-8")
    _git(repository, "add", ".relay/registry.json")
    _git(
        repository,
        "-c",
        "user.name=Relay Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "add invalid contract",
    )
    report = inspect_repository(repository, FIXED_TIME)
    report_path = tmp_path / "reports" / "discovery.json"
    report_path.parent.mkdir()
    report_path.write_bytes(canonical_report_bytes(report))
    output_path = tmp_path / "external.json"
    stdout = StringIO()
    stderr = StringIO()

    result = main(
        [
            "intake",
            "--repository",
            str(repository),
            "--report",
            str(report_path),
            "--output",
            str(output_path),
        ],
        input_fn=lambda _: _raise_eof(),
        output_stream=stdout,
        error_stream=stderr,
        clock=lambda: FIXED_TIME,
    )

    assert result == 0
    assert not stderr.getvalue()
    assert "Working tree: dirty" in stdout.getvalue()
    assert "Relay contract: INVALID" in stdout.getvalue()
    assert "RELAY_CONTRACT_INVALID" in stdout.getvalue()
    assert "Discovery status: PARTIAL" in stdout.getvalue()


def _raise_eof() -> str:
    raise EOFError


def test_b0_inspect_command_remains_available_with_same_report_format(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    output = StringIO()
    error = StringIO()

    result = main(
        ["inspect", "--repository", str(repository), "--output", "-"],
        observed_at=FIXED_TIME,
        output_stream=output,
        error_stream=error,
    )

    assert result == 0
    assert not error.getvalue()
    report = json.loads(output.getvalue())
    assert report["format"] == "relay-bootstrap-discovery"
    assert report["schema_version"] == 1


def test_report_digest_is_exact_input_byte_digest(tmp_path: Path) -> None:
    loaded = _loaded_report(tmp_path)

    assert loaded.sha256 == "sha256:" + hashlib.sha256(loaded.raw_bytes).hexdigest()
