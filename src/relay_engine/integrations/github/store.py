"""Transactional SQLite storage for project-scoped GitHub integration state."""

import json
import sqlite3
from dataclasses import dataclass
from typing import cast

from pydantic import BaseModel, ValidationError

from relay_engine.domain.ids import ProjectId
from relay_engine.integrations.github.errors import (
    GitHubIntegrationConcurrencyConflict,
    GitHubIntegrationIntegrityError,
)
from relay_engine.integrations.github.models import (
    GitHubInstallationEvent,
    GitHubInstallationState,
    GitHubRepositorySnapshot,
)
from relay_engine.persistence.database import RelayDatabase, write_transaction


def _canonical_json(model: BaseModel) -> str:
    return json.dumps(
        model.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


@dataclass(frozen=True, slots=True)
class GitHubMutationResult:
    applied: bool
    state: GitHubInstallationState


class GitHubIntegrationStore:
    def __init__(self, database: RelayDatabase) -> None:
        self._database = database

    @staticmethod
    def _parse_state(row: sqlite3.Row) -> GitHubInstallationState:
        try:
            state = GitHubInstallationState.model_validate_json(cast(str, row["payload_json"]))
        except (ValidationError, ValueError, TypeError) as error:
            raise GitHubIntegrationIntegrityError(
                "stored GitHub installation state is invalid"
            ) from error
        if (
            row["project_id"] != state.project_id
            or int(row["installation_id"]) != state.installation_id
            or int(row["state_revision"]) != state.state_revision
        ):
            raise GitHubIntegrationIntegrityError(
                "GitHub installation indexed columns disagree with typed payload"
            )
        return state

    @staticmethod
    def _parse_repository(row: sqlite3.Row) -> GitHubRepositorySnapshot:
        try:
            repository = GitHubRepositorySnapshot.model_validate_json(
                cast(str, row["payload_json"])
            )
        except (ValidationError, ValueError, TypeError) as error:
            raise GitHubIntegrationIntegrityError(
                "stored GitHub repository state is invalid"
            ) from error
        if int(row["github_repository_id"]) != repository.github_repository_id:
            raise GitHubIntegrationIntegrityError(
                "GitHub repository indexed identity disagrees with typed payload"
            )
        return repository

    @staticmethod
    def _parse_event(row: sqlite3.Row) -> GitHubInstallationEvent:
        try:
            event = GitHubInstallationEvent.model_validate_json(cast(str, row["payload_json"]))
        except (ValidationError, ValueError, TypeError) as error:
            raise GitHubIntegrationIntegrityError(
                "stored GitHub integration event is invalid"
            ) from error
        if row["event_id"] != event.event_id:
            raise GitHubIntegrationIntegrityError("GitHub event identity disagrees with payload")
        return event

    def load_state(
        self, project_id: ProjectId, installation_id: int
    ) -> GitHubInstallationState | None:
        row = self._database.connection.execute(
            "SELECT * FROM github_installations WHERE project_id = ? AND installation_id = ?",
            (project_id, installation_id),
        ).fetchone()
        return None if row is None else self._parse_state(row)

    def list_repositories(
        self, project_id: ProjectId, installation_id: int
    ) -> tuple[GitHubRepositorySnapshot, ...]:
        rows = self._database.connection.execute(
            """SELECT * FROM github_installation_repositories
               WHERE project_id = ? AND installation_id = ?
               ORDER BY github_repository_id""",
            (project_id, installation_id),
        ).fetchall()
        return tuple(self._parse_repository(row) for row in rows)

    def list_events(
        self, project_id: ProjectId, installation_id: int
    ) -> tuple[GitHubInstallationEvent, ...]:
        rows = self._database.connection.execute(
            """SELECT * FROM github_installation_events
               WHERE project_id = ? AND installation_id = ?
               ORDER BY sequence""",
            (project_id, installation_id),
        ).fetchall()
        return tuple(self._parse_event(row) for row in rows)

    def project_bindings_for_installation(self, installation_id: int) -> tuple[ProjectId, ...]:
        rows = self._database.connection.execute(
            """SELECT project_id FROM github_installations
               WHERE installation_id = ? ORDER BY project_id""",
            (installation_id,),
        ).fetchall()
        return tuple(str(row["project_id"]) for row in rows)

    def apply_mutation(
        self,
        *,
        expected_revision: int | None,
        state: GitHubInstallationState,
        repositories: tuple[GitHubRepositorySnapshot, ...] | None,
        event: GitHubInstallationEvent,
    ) -> GitHubMutationResult:
        """Apply state, optional repository set, event, and delivery evidence atomically."""

        if event.project_id != state.project_id or event.installation_id != state.installation_id:
            raise GitHubIntegrationIntegrityError("event and state identify different bindings")
        expected_prior = 0 if expected_revision is None else expected_revision
        if (
            event.prior_state_revision != expected_prior
            or event.resulting_state_revision != state.state_revision
        ):
            raise GitHubIntegrationIntegrityError("event revisions disagree with target state")
        if state.state_revision != expected_prior + 1:
            raise GitHubIntegrationIntegrityError("target state must advance revision by one")
        if repositories is not None:
            ids = tuple(item.github_repository_id for item in repositories)
            if ids != tuple(sorted(set(ids))):
                raise GitHubIntegrationIntegrityError(
                    "repository replacement set must be unique and sorted by provider ID"
                )

        try:
            with write_transaction(self._database) as connection:
                if event.delivery_id is not None:
                    duplicate = connection.execute(
                        """SELECT * FROM github_installation_events
                           WHERE project_id = ? AND delivery_id = ?""",
                        (state.project_id, event.delivery_id),
                    ).fetchone()
                    if duplicate is not None:
                        prior_event = self._parse_event(duplicate)
                        if prior_event.delivery_digest != event.delivery_digest:
                            raise GitHubIntegrationIntegrityError(
                                "GitHub delivery ID was reused with conflicting semantic content"
                            )
                        current = connection.execute(
                            """SELECT * FROM github_installations
                               WHERE project_id = ? AND installation_id = ?""",
                            (state.project_id, state.installation_id),
                        ).fetchone()
                        if current is None:
                            raise GitHubIntegrationIntegrityError(
                                "delivery evidence exists without current installation state"
                            )
                        return GitHubMutationResult(False, self._parse_state(current))

                current = connection.execute(
                    """SELECT * FROM github_installations
                       WHERE project_id = ? AND installation_id = ?""",
                    (state.project_id, state.installation_id),
                ).fetchone()
                if expected_revision is None:
                    if current is not None:
                        raise GitHubIntegrationConcurrencyConflict(
                            "GitHub integration binding appeared during operation"
                        )
                    connection.execute(
                        """INSERT INTO github_installations(
                               project_id, installation_id, state_revision, payload_json
                           ) VALUES (?, ?, ?, ?)""",
                        (
                            state.project_id,
                            state.installation_id,
                            state.state_revision,
                            _canonical_json(state),
                        ),
                    )
                else:
                    if current is None or int(current["state_revision"]) != expected_revision:
                        raise GitHubIntegrationConcurrencyConflict(
                            "GitHub integration state changed during operation"
                        )
                    cursor = connection.execute(
                        """UPDATE github_installations
                           SET state_revision = ?, payload_json = ?
                           WHERE project_id = ? AND installation_id = ? AND state_revision = ?""",
                        (
                            state.state_revision,
                            _canonical_json(state),
                            state.project_id,
                            state.installation_id,
                            expected_revision,
                        ),
                    )
                    if cursor.rowcount != 1:
                        raise GitHubIntegrationConcurrencyConflict(
                            "GitHub integration state changed during operation"
                        )

                if repositories is not None:
                    connection.execute(
                        """DELETE FROM github_installation_repositories
                           WHERE project_id = ? AND installation_id = ?""",
                        (state.project_id, state.installation_id),
                    )
                    for repository in repositories:
                        connection.execute(
                            """INSERT INTO github_installation_repositories(
                                   project_id, installation_id, github_repository_id, payload_json
                               ) VALUES (?, ?, ?, ?)""",
                            (
                                state.project_id,
                                state.installation_id,
                                repository.github_repository_id,
                                _canonical_json(repository),
                            ),
                        )

                connection.execute(
                    """INSERT INTO github_installation_events(
                           event_id, project_id, installation_id,
                           prior_state_revision, resulting_state_revision,
                           event_type, observed_at, delivery_id, delivery_digest, payload_json
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        event.event_id,
                        event.project_id,
                        event.installation_id,
                        event.prior_state_revision,
                        event.resulting_state_revision,
                        event.event_type.value,
                        event.observed_at.isoformat(),
                        event.delivery_id,
                        event.delivery_digest,
                        _canonical_json(event),
                    ),
                )
            return GitHubMutationResult(True, state)
        except sqlite3.IntegrityError as error:
            raise GitHubIntegrationIntegrityError(
                "GitHub integration durable uniqueness or reference constraint failed"
            ) from error
