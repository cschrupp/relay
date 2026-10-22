"""Behavior and safety tests for the read-only B0-F discovery command."""

import hashlib
import json
import os
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from relay_engine.bootstrap_discovery import local_git, service
from relay_engine.bootstrap_discovery.cli import main
from relay_engine.bootstrap_discovery.models import (
    BootstrapDiscoveryReportV1,
    DiscoveryStatus,
    Ecosystem,
    InspectionState,
    Language,
    RelayContractStatus,
    canonical_json_bytes,
)
from relay_engine.bootstrap_discovery.service import BootstrapDiscoveryError, inspect_repository
from relay_engine.domain import ProjectId, RepositoryRef
from relay_engine.repository_contract import (
    RepositoryArtifactClass,
    RepositoryArtifactRevision,
    RepositoryArtifactState,
    RepositoryRegistry,
    serialize_repository_registry,
)

FIXED_TIME = datetime(2026, 10, 17, 12, 30, tzinfo=UTC)
PROJECT_ID: ProjectId = "prj_018f47c1-7b2c-7abc-8def-123456789001"
REPOSITORY = RepositoryRef(
    id="repo_018f47c1-7b2c-7abc-8def-123456789002",
    host="example.test",
    path="owner/project",
)


def _git(repository: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    )
    return completed.stdout


def _repository(root: Path, files: dict[str, bytes] | None = None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for relative_path, content in (files or {"README.md": b"observed\n"}).items():
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


def _add_contract(repository: Path) -> None:
    content = b"registered exact bytes\n"
    artifact = RepositoryArtifactRevision(
        artifact_id="art_018f47c1-7b2c-7abc-8def-123456789001",
        revision=1,
        title="Contract fixture",
        artifact_type="DOCUMENT",
        artifact_class=RepositoryArtifactClass.LIVING_PROJECTION,
        artifact_state=RepositoryArtifactState.CURRENT,
        path="docs/contract-fixture.md",
        content_digest="sha256:" + hashlib.sha256(content).hexdigest(),
        human_version=None,
        updated_at=FIXED_TIME,
        scope="Discovery test fixture.",
    )
    target = repository / artifact.path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    registry = RepositoryRegistry(
        project_id=PROJECT_ID,
        repository=REPOSITORY,
        artifacts=(artifact,),
        canonical=(),
    )
    relay_dir = repository / ".relay"
    relay_dir.mkdir()
    (relay_dir / "registry.json").write_bytes(serialize_repository_registry(registry))
    _git(repository, "add", "-A")
    _git(
        repository,
        "-c",
        "user.name=Relay Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "add Relay contract",
    )


def test_clean_repository_reports_branch_head_and_tracked_count(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo", {"README.md": b"hello"})

    report = inspect_repository(repository, FIXED_TIME)

    assert report.git.head_sha == _git(repository, "rev-parse", "HEAD").decode().strip()
    assert report.git.branch is not None
    assert report.git.detached_head is False
    assert report.git.dirty is False
    assert report.git.tracked_file_count == 1
    assert report.observation.discovery_status is DiscoveryStatus.COMPLETE


def test_detached_and_dirty_repository_are_observed(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "checkout", "--detach", "HEAD")
    (repository / "README.md").write_bytes(b"changed\n")

    report = inspect_repository(repository, FIXED_TIME)
    diagnostic_codes = {item.code.value for item in report.observation.diagnostics}

    assert report.git.branch is None
    assert report.git.detached_head is True
    assert report.git.dirty is True
    assert {"DETACHED_HEAD", "DIRTY_WORKTREE"} <= diagnostic_codes


def test_no_remote_is_reported_without_inference(tmp_path: Path) -> None:
    report = inspect_repository(_repository(tmp_path / "repo"), FIXED_TIME)

    assert report.git.remotes == ()
    assert any(item.code.value == "NO_REMOTES" for item in report.observation.diagnostics)


def test_multiple_remotes_have_stable_order_and_exact_urls(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "remote", "add", "zeta", "https://example.test/zeta.git")
    _git(repository, "remote", "add", "origin", "git@example.test:owner/project.git")

    report = inspect_repository(repository, FIXED_TIME)

    assert [remote.name for remote in report.git.remotes] == ["origin", "zeta"]
    assert report.git.remotes[0].fetch_url == "git@example.test:owner/project.git"
    assert report.git.remotes[0].push_url == "git@example.test:owner/project.git"
    assert report.git.remotes[1].fetch_url == "https://example.test/zeta.git"


def test_credential_bearing_remote_is_not_serialized(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "remote", "add", "origin", "https://user:secret@example.test/project.git")

    report = inspect_repository(repository, FIXED_TIME)
    serialized = canonical_json_bytes(report)

    assert report.git.remotes[0].fetch_url is None
    assert b"secret" not in serialized
    assert any(
        item.code.value == "REMOTE_URL_CREDENTIALS_OMITTED"
        for item in report.observation.diagnostics
    )


def test_credential_bearing_scp_remote_is_not_serialized(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "remote", "add", "origin", "user:secret@example.test:owner/project.git")

    report = inspect_repository(repository, FIXED_TIME)

    assert report.git.remotes[0].fetch_url is None
    assert b"secret" not in canonical_json_bytes(report)


def test_manifest_and_language_signals_are_path_derived(tmp_path: Path) -> None:
    files = {
        "pyproject.toml": b"[project]\n",
        "requirements-dev.txt": b"pytest\n",
        "package.json": b"{}\n",
        "pnpm-lock.yaml": b"lockfileVersion: 9\n",
        "Cargo.toml": b"[package]\n",
        "go.mod": b"module sample\n",
        "pom.xml": b"<project/>\n",
        "app.csproj": b"<Project/>\n",
        "src/main.py": b"pass\n",
        "src/client.ts": b"export {}\n",
        "src/lib.rs": b"fn main() {}\n",
        "cmd/main.go": b"package main\n",
        "src/Main.java": b"class Main {}\n",
        "src/Program.cs": b"class Program {}\n",
    }
    report = inspect_repository(_repository(tmp_path / "repo", files), FIXED_TIME)

    ecosystems = {signal.ecosystem for signal in report.manifests}
    languages = {signal.language for signal in report.language_signals}
    assert {
        Ecosystem.PYTHON,
        Ecosystem.JAVASCRIPT_TYPESCRIPT,
        Ecosystem.RUST,
        Ecosystem.GO,
        Ecosystem.JVM,
        Ecosystem.DOTNET,
    } <= ecosystems
    assert {
        Language.PYTHON,
        Language.TYPESCRIPT,
        Language.RUST,
        Language.GO,
        Language.JAVA,
        Language.CSHARP,
    } <= languages


def test_ci_and_documentation_inventory_is_bounded_and_sorted(tmp_path: Path) -> None:
    files = {
        ".github/workflows/ci.yml": b"name: CI\n",
        ".gitlab-ci.yml": b"stages: []\n",
        ".circleci/config.yml": b"version: 2.1\n",
        "Jenkinsfile": b"pipeline {}\n",
        "azure-pipelines.yml": b"trigger: none\n",
        "README.md": b"read me\n",
        "CONTRIBUTING.md": b"contribute\n",
        "docs/architecture.md": b"architecture\n",
    }
    report = inspect_repository(_repository(tmp_path / "repo", files), FIXED_TIME)

    assert [item.relative_path for item in report.ci_files] == sorted(
        [
            ".github/workflows/ci.yml",
            ".gitlab-ci.yml",
            ".circleci/config.yml",
            "Jenkinsfile",
            "azure-pipelines.yml",
        ]
    )
    assert [item.relative_path for item in report.documentation_files] == sorted(
        ["README.md", "CONTRIBUTING.md", "docs/architecture.md"]
    )


def test_valid_relay_contract_is_reported_from_existing_validator(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    _add_contract(repository)

    report = inspect_repository(repository, FIXED_TIME)

    assert report.relay_contract.status is RelayContractStatus.VALID
    assert report.relay_contract.project_id == PROJECT_ID
    assert report.relay_contract.repository == REPOSITORY
    assert report.relay_contract.artifact_count == 1
    assert report.relay_contract.canonical_keys == ()


def test_invalid_relay_contract_is_a_soft_diagnostic(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo", {"README.md": b"still observed\n"})
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
        "bad contract",
    )

    report = inspect_repository(repository, FIXED_TIME)

    assert report.relay_contract.status is RelayContractStatus.INVALID
    assert report.documentation_files[0].relative_path == "README.md"
    assert report.observation.discovery_status is DiscoveryStatus.PARTIAL
    assert any(
        item.code.value == "RELAY_CONTRACT_INVALID" for item in report.observation.diagnostics
    )


def test_absent_relay_contract_is_distinct_from_invalid(tmp_path: Path) -> None:
    report = inspect_repository(_repository(tmp_path / "repo"), FIXED_TIME)

    assert report.relay_contract.status is RelayContractStatus.ABSENT


def test_symlinked_relay_directory_is_invalid_without_reading_target(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    outside = tmp_path / "outside-relay"
    outside.mkdir()
    (outside / "registry.json").write_text("not read", encoding="utf-8")
    (repository / ".relay").symlink_to(outside, target_is_directory=True)
    _git(repository, "add", ".relay")
    _git(
        repository,
        "-c",
        "user.name=Relay Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "symlink Relay contract",
    )

    report = inspect_repository(repository, FIXED_TIME)

    assert report.relay_contract.status is RelayContractStatus.INVALID
    assert any(
        item.code.value == "RELAY_CONTRACT_INVALID" for item in report.observation.diagnostics
    )


def test_symlink_evidence_is_reported_without_reading_target(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo")
    outside = tmp_path / "private-content"
    outside.write_bytes(b"must not appear")
    (repository / "README-secret.md").symlink_to(outside)
    _git(repository, "add", "README-secret.md")
    _git(
        repository,
        "-c",
        "user.name=Relay Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "add symlink",
    )

    report = inspect_repository(repository, FIXED_TIME)
    evidence = next(
        item for item in report.documentation_files if item.relative_path == "README-secret.md"
    )

    assert evidence.inspection_state is InspectionState.SYMLINK_NOT_FOLLOWED
    assert evidence.sha256 is None
    assert b"must not appear" not in canonical_json_bytes(report)


def test_per_file_read_limit_keeps_large_file_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(service, "MAX_EVIDENCE_FILE_BYTES", 5)
    repository = _repository(tmp_path / "repo", {"README.md": b"123456"})

    report = inspect_repository(repository, FIXED_TIME)
    evidence = report.documentation_files[0]

    assert evidence.inspection_state is InspectionState.SKIPPED_TOO_LARGE
    assert evidence.size_bytes == 6
    assert evidence.sha256 is None
    assert any(item.code.value == "FILE_TOO_LARGE" for item in report.observation.diagnostics)


def test_aggregate_read_limit_is_respected_in_path_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(service, "MAX_EVIDENCE_FILE_BYTES", 10)
    monkeypatch.setattr(service, "MAX_EVIDENCE_TOTAL_BYTES", 5)
    repository = _repository(
        tmp_path / "repo",
        {
            "ARCHITECTURE.md": b"1234",
            "CONTRIBUTING.md": b"5",
            "README.md": b"6789",
        },
    )

    report = inspect_repository(repository, FIXED_TIME)
    states = {item.relative_path: item.inspection_state for item in report.documentation_files}

    assert states["ARCHITECTURE.md"] is InspectionState.READ
    assert states["CONTRIBUTING.md"] is InspectionState.READ
    assert states["README.md"] is InspectionState.SKIPPED_TOO_LARGE
    assert (
        sum(
            item.size_bytes or 0
            for item in report.documentation_files
            if item.inspection_state is InspectionState.READ
        )
        == 5
    )


def test_canonical_json_is_byte_stable_for_same_observations(tmp_path: Path) -> None:
    repository = _repository(tmp_path / "repo", {"README.md": b"same\n", "pyproject.toml": b""})

    first = canonical_json_bytes(inspect_repository(repository, FIXED_TIME))
    second = canonical_json_bytes(inspect_repository(repository, FIXED_TIME))

    assert first == second
    parsed = json.loads(first)
    assert parsed["format"] == "relay-bootstrap-discovery"
    assert parsed["schema_version"] == 1


def test_cli_stdout_mode_uses_canonical_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repository = _repository(tmp_path / "repo")

    result = main(
        ["inspect", "--repository", str(repository), "--output", "-"],
        observed_at=FIXED_TIME,
    )

    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    parsed = json.loads(captured.out)
    canonical = json.dumps(parsed, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    assert captured.out == canonical
    assert parsed["format"] == "relay-bootstrap-discovery"
    assert parsed["observation"]["observed_at"] == FIXED_TIME.isoformat().replace("+00:00", "Z")


def test_cli_maps_report_serialization_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository(tmp_path / "repo")

    def fail_serialization(report: BootstrapDiscoveryReportV1) -> bytes:
        raise ValueError("injected serializer failure")

    monkeypatch.setattr(service, "canonical_json_bytes", fail_serialization)
    result = main(
        ["inspect", "--repository", str(repository), "--output", "-"],
        observed_at=FIXED_TIME,
    )

    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert "REPORT_SERIALIZATION_FAILED" in captured.err


def test_cli_exclusive_create_and_existing_output_refusal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repository = _repository(tmp_path / "repo")
    output = tmp_path / "discovery.json"
    args = ["inspect", "--repository", str(repository), "--output", str(output)]

    assert main(args, observed_at=FIXED_TIME) == 0
    original = output.read_bytes()
    assert main(args, observed_at=FIXED_TIME) == 2
    assert output.read_bytes() == original
    assert "OUTPUT_EXISTS" in capsys.readouterr().err


def test_cli_refuses_existing_broken_symlink_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository = _repository(tmp_path / "repo")
    output = tmp_path / "discovery.json"
    output.symlink_to(tmp_path / "missing-target.json")

    result = main(
        ["inspect", "--repository", str(repository), "--output", str(output)],
        observed_at=FIXED_TIME,
    )

    assert result == 2
    assert output.is_symlink()
    assert not output.resolve().exists()
    assert "OUTPUT_EXISTS" in capsys.readouterr().err


def test_cli_refuses_filesystem_output_inside_inspected_repository(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repository = _repository(tmp_path / "repo")
    output = repository / "report.json"

    result = main(
        ["inspect", "--repository", str(repository), "--output", str(output)],
        observed_at=FIXED_TIME,
    )

    assert result == 2
    assert not output.exists()
    assert "OUTPUT_INSIDE_REPOSITORY" in capsys.readouterr().err


def test_git_failure_mapping_for_non_repository_and_unavailable_git(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    non_repository = tmp_path / "not-a-repo"
    non_repository.mkdir()
    with pytest.raises(BootstrapDiscoveryError, match="path is not inside a Git") as error:
        inspect_repository(non_repository, FIXED_TIME)
    assert error.value.code == "NOT_GIT_REPOSITORY"


def test_git_unavailable_maps_to_explicit_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = _repository(tmp_path / "repo")

    def fail_to_start(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        raise FileNotFoundError

    monkeypatch.setattr(local_git.subprocess, "Popen", fail_to_start)

    with pytest.raises(BootstrapDiscoveryError) as error:
        inspect_repository(repository, FIXED_TIME)

    assert error.value.code == "GIT_UNAVAILABLE"


def test_head_resolution_failure_maps_to_explicit_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository(tmp_path / "repo")
    (repository / ".git" / "HEAD").write_text(
        "ref: refs/heads/missing\n",
        encoding="ascii",
    )
    with pytest.raises(BootstrapDiscoveryError) as error:
        inspect_repository(repository, FIXED_TIME)

    assert error.value.code == "HEAD_UNRESOLVABLE"


def test_git_adapter_invokes_only_fixed_read_only_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = _repository(tmp_path / "repo")
    _git(repository, "remote", "add", "origin", "https://example.test/project.git")
    original_popen = subprocess.Popen
    commands: list[tuple[str, ...]] = []

    def recording_popen(
        args: Sequence[str],
        *positional: Any,
        **kwargs: Any,
    ) -> subprocess.Popen[Any]:
        commands.append(tuple(args))
        assert kwargs["shell"] is False
        return original_popen(args, *positional, **kwargs)

    monkeypatch.setattr(local_git.subprocess, "Popen", recording_popen)
    inspect_repository(repository, FIXED_TIME)

    allowed = {
        ("rev-parse", "--show-toplevel"),
        ("rev-parse", "HEAD"),
        ("symbolic-ref", "--quiet", "--short", "HEAD"),
        ("status", "--porcelain=v1"),
        ("ls-files", "-z"),
        ("remote",),
        ("remote", "get-url", "--", "origin"),
        ("remote", "get-url", "--push", "--", "origin"),
    }
    for command in commands:
        assert command[:3] == ("git", "-C", str(repository))
        assert command[3:] in allowed


def test_repository_is_unchanged_after_inspection(tmp_path: Path) -> None:
    repository = _repository(
        tmp_path / "repo", {"README.md": b"unchanged\n", "src/main.py": b"print(1)\n"}
    )

    def tree_state() -> dict[str, str]:
        state: dict[str, str] = {}
        for path in sorted(repository.rglob("*")):
            relative_path = path.relative_to(repository).as_posix()
            if path.is_symlink():
                state[relative_path] = "symlink:" + os.readlink(path)
            elif path.is_file():
                state[relative_path] = hashlib.sha256(path.read_bytes()).hexdigest()
        return state

    before_state = tree_state()
    before_status = _git(repository, "status", "--porcelain=v1")

    inspect_repository(repository, FIXED_TIME)

    assert tree_state() == before_state
    assert _git(repository, "status", "--porcelain=v1") == before_status
