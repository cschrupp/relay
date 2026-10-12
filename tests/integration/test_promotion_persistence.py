"""Migration-v6 contract tests for append-only promotion history."""

import sqlite3
from datetime import UTC, datetime

import pytest

from relay_engine.persistence import DEFAULT_MIGRATIONS, open_database

NOW_VALUE = datetime(2026, 10, 12, tzinfo=UTC)
NOW = NOW_VALUE.isoformat().replace("+00:00", "Z")
PROJECT_ID = "prj_018f47c1-7b2c-7abc-8def-123456789001"


def test_migration_v6_creates_exact_four_append_only_tables(tmp_path) -> None:
    database = open_database(
        tmp_path / "promotion.sqlite",
        apply_migrations=True,
        migration_applied_at=NOW_VALUE,
    )
    try:
        assert [migration.version for migration in DEFAULT_MIGRATIONS] == [1, 2, 3, 4, 5, 6]
        tables = {
            row[0]
            for row in database.connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        promotion_tables = {
            "canonical_promotion_policy_bindings",
            "repository_promotion_intents",
            "repository_promotion_results",
            "repository_promotion_reconciliations",
        }
        assert promotion_tables <= tables
        assert not any("quarantine" in table for table in tables)

        database.connection.execute(
            "INSERT INTO projects(id, payload_json) VALUES (?, ?)", (PROJECT_ID, "{}")
        )
        database.connection.execute(
            "INSERT INTO canonical_promotion_policy_bindings "
            "(binding_id, project_id, repository_id, canonical_ref, revision, state, "
            "policy_digest, authorization_id, supersedes_binding_id, bound_at, payload_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "cpb_018f47c1-7b2c-7abc-8def-123456789010",
                PROJECT_ID,
                "repo_018f47c1-7b2c-7abc-8def-123456789002",
                "refs/heads/main",
                1,
                "UNMANAGED",
                None,
                "rma_018f47c1-7b2c-7abc-8def-123456789011",
                None,
                NOW,
                "{}",
            ),
        )
        database.connection.execute(
            "INSERT INTO repository_promotion_intents "
            "(promotion_id, project_id, repository_id, canonical_ref, subject_digest, "
            "created_at, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "prom_018f47c1-7b2c-7abc-8def-123456789012",
                PROJECT_ID,
                "repo_018f47c1-7b2c-7abc-8def-123456789002",
                "refs/heads/main",
                "sha256:" + "a" * 64,
                NOW,
                "{}",
            ),
        )
        database.connection.execute(
            "INSERT INTO repository_promotion_results "
            "(promotion_id, project_id, repository_id, canonical_ref, outcome, completed_at, "
            "payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "prom_018f47c1-7b2c-7abc-8def-123456789012",
                PROJECT_ID,
                "repo_018f47c1-7b2c-7abc-8def-123456789002",
                "refs/heads/main",
                "VISIBLE_UNVERIFIED",
                NOW,
                "{}",
            ),
        )
        database.connection.execute(
            "INSERT INTO repository_promotion_reconciliations "
            "(reconciliation_id, promotion_id, project_id, repository_id, canonical_ref, "
            "target_sha, authorization_id, reconciled_at, payload_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "recon_018f47c1-7b2c-7abc-8def-123456789013",
                "prom_018f47c1-7b2c-7abc-8def-123456789012",
                PROJECT_ID,
                "repo_018f47c1-7b2c-7abc-8def-123456789002",
                "refs/heads/main",
                "b" * 40,
                "rma_018f47c1-7b2c-7abc-8def-123456789014",
                NOW,
                "{}",
            ),
        )

        for table in sorted(promotion_tables):
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                database.connection.execute(f"UPDATE {table} SET payload_json = ?", ("{}",))
            with pytest.raises(sqlite3.IntegrityError, match="append-only"):
                database.connection.execute(f"DELETE FROM {table}")
    finally:
        database.close()
