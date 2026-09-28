"""Atomic persistence for verified repository snapshots and Relay Baselines."""

import json
import sqlite3
from collections.abc import Sequence
from typing import cast

from pydantic import BaseModel, ValidationError

from relay_engine.domain.ids import BaselineId, DecisionId
from relay_engine.domain.models import Artifact, Baseline, Project
from relay_engine.domain.references import CommitRef
from relay_engine.integrations.github.models import GitHubRepositoryAccessSelection
from relay_engine.integrations.github.store import GitHubIntegrationStore
from relay_engine.persistence.database import RelayDatabase, write_transaction
from relay_engine.repository_baseline.errors import (
    RepositoryAccessChanged,
    RepositoryBaselinePersistenceError,
    RepositoryProjectMismatch,
)
from relay_engine.repository_contract.models import RepositoryRegistry


def _canonical_json(model: BaseModel) -> str:
    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _parse_project(payload_json: object) -> Project:
    try:
        return Project.model_validate_json(cast(str, payload_json))
    except (ValidationError, TypeError, ValueError) as error:
        raise RepositoryBaselinePersistenceError("stored Project payload is invalid") from error


def _parse_artifact(payload_json: object) -> Artifact:
    try:
        return Artifact.model_validate_json(cast(str, payload_json))
    except (ValidationError, TypeError, ValueError) as error:
        raise RepositoryBaselinePersistenceError("stored Artifact payload is invalid") from error


def persist_verified_baseline(
    *,
    database: RelayDatabase,
    selection: GitHubRepositoryAccessSelection,
    registry: RepositoryRegistry,
    commit: CommitRef,
    baseline_id: BaselineId,
    decision_ids: Sequence[DecisionId],
) -> Baseline:
    """Re-check local access authority and atomically bind Artifacts plus one Baseline."""

    if commit.repository != selection.repository:
        raise RepositoryProjectMismatch("verified commit repository differs from selection")
    if registry.project_id != selection.project_id or registry.repository != selection.repository:
        raise RepositoryProjectMismatch("verified registry identity differs from selection")

    artifact_ids = tuple(item.artifact_id for item in registry.artifacts)
    baseline = Baseline(
        id=baseline_id,
        project_id=selection.project_id,
        commit=commit,
        artifact_ids=artifact_ids,
        decision_ids=tuple(decision_ids),
    )
    store = GitHubIntegrationStore(database)

    try:
        with write_transaction(database) as connection:
            project_row = connection.execute(
                "SELECT payload_json FROM projects WHERE id = ?", (selection.project_id,)
            ).fetchone()
            if project_row is None:
                raise RepositoryProjectMismatch("Relay project does not exist")
            project = _parse_project(project_row["payload_json"])
            if project.id != selection.project_id or project.primary_repository != selection.repository:
                raise RepositoryProjectMismatch(
                    "Project.primary_repository changed or differs from selection"
                )

            state = store.load_state(selection.project_id, selection.installation_id)
            if (
                state is None
                or state.state_revision != selection.expected_state_revision
                or not state.usable
            ):
                raise RepositoryAccessChanged(
                    "GitHub access authority changed during baseline resolution"
                )
            repositories = store.list_repositories(
                selection.project_id, selection.installation_id
            )
            selected = next(
                (
                    item
                    for item in repositories
                    if item.github_repository_id == selection.github_repository_id
                ),
                None,
            )
            if (
                selected is None
                or selected.node_id != selection.github_node_id
                or selected.full_name != selection.repository.path
            ):
                raise RepositoryAccessChanged(
                    "GitHub repository membership or provider identity changed"
                )

            for revision in registry.artifacts:
                candidate = Artifact(
                    id=revision.artifact_id,
                    artifact_type=revision.artifact_type,
                    path=revision.path,
                    commit=commit,
                    content_digest=revision.content_digest,
                )
                row = connection.execute(
                    "SELECT payload_json FROM artifacts WHERE id = ?",
                    (candidate.id,),
                ).fetchone()
                if row is None:
                    connection.execute(
                        "INSERT INTO artifacts(id, payload_json) VALUES (?, ?)",
                        (candidate.id, _canonical_json(candidate)),
                    )
                    continue
                existing = _parse_artifact(row["payload_json"])
                if (
                    existing.id != candidate.id
                    or existing.artifact_type != candidate.artifact_type
                    or existing.path != candidate.path
                    or existing.content_digest != candidate.content_digest
                    or existing.commit.repository != candidate.commit.repository
                ):
                    raise RepositoryBaselinePersistenceError(
                        "existing Artifact binding conflicts with verified registry revision"
                    )

            for decision_id in baseline.decision_ids:
                row = connection.execute(
                    "SELECT id FROM decisions WHERE id = ?", (decision_id,)
                ).fetchone()
                if row is None:
                    raise RepositoryBaselinePersistenceError(
                        f"referenced Decision does not exist: {decision_id}"
                    )

            duplicate = connection.execute(
                "SELECT id FROM baselines WHERE id = ?", (baseline.id,)
            ).fetchone()
            if duplicate is not None:
                raise RepositoryBaselinePersistenceError("BaselineId already exists")
            connection.execute(
                "INSERT INTO baselines(id, project_id, payload_json) VALUES (?, ?, ?)",
                (baseline.id, baseline.project_id, _canonical_json(baseline)),
            )
    except sqlite3.IntegrityError as error:
        raise RepositoryBaselinePersistenceError(
            "verified baseline violates durable uniqueness or reference integrity"
        ) from error

    return baseline
