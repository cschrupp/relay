"""Explicit SQLite database opening and transaction boundaries."""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from relay_engine.persistence.errors import DatabaseUnavailable, MigrationError, PersistenceError
from relay_engine.persistence.migrations import (
    DEFAULT_MIGRATIONS,
    Migration,
    verify_schema,
)
from relay_engine.persistence.migrations import (
    apply_migrations as apply_schema_migrations,
)


@dataclass(slots=True)
class RelayDatabase:
    """One caller-owned SQLite connection with Relay schema verification."""

    path: str
    connection: sqlite3.Connection

    def close(self) -> None:
        """Close the underlying SQLite connection."""

        try:
            self.connection.close()
        except sqlite3.Error as error:
            raise DatabaseUnavailable("could not close SQLite database") from error

    def __enter__(self) -> RelayDatabase:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


def open_database(
    path: str | Path,
    *,
    apply_migrations: bool,
    migration_applied_at: datetime | None = None,
    migrations: tuple[Migration, ...] = DEFAULT_MIGRATIONS,
) -> RelayDatabase:
    """Open the explicit target, enable foreign keys, and verify/apply schema."""

    path_text = str(path)
    if not path_text:
        raise ValueError("database path must be explicit and non-empty")
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(path_text, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        enabled = connection.execute("PRAGMA foreign_keys").fetchone()
        if enabled is None or int(enabled[0]) != 1:
            raise DatabaseUnavailable("SQLite foreign-key enforcement could not be enabled")

        if path_text != ":memory:":
            with suppress(sqlite3.Error):
                connection.execute("PRAGMA journal_mode = WAL").fetchone()

        database = RelayDatabase(path=path_text, connection=connection)
        if apply_migrations:
            if migration_applied_at is None:
                raise MigrationError("migration_applied_at must be supplied explicitly")
            apply_schema_migrations(
                connection,
                migrations,
                applied_at=migration_applied_at,
            )
        verify_schema(connection, migrations)
        return database
    except DatabaseUnavailable, MigrationError:
        if connection is not None:
            connection.close()
        raise
    except sqlite3.OperationalError as error:
        if connection is not None:
            connection.close()
        raise DatabaseUnavailable("could not open or configure SQLite database") from error
    except sqlite3.Error as error:
        if connection is not None:
            connection.close()
        raise DatabaseUnavailable("could not open or configure SQLite database") from error


@contextmanager
def write_transaction(database: RelayDatabase) -> Generator[sqlite3.Connection]:
    """Own one immediate SQLite transaction without implicit nested commits."""

    connection = database.connection
    try:
        connection.execute("BEGIN IMMEDIATE")
        yield connection
        connection.commit()
    except PersistenceError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except sqlite3.IntegrityError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except sqlite3.OperationalError as error:
        if connection.in_transaction:
            connection.rollback()
        if _is_busy(error):
            raise DatabaseUnavailable("SQLite database is busy or locked") from error
        raise DatabaseUnavailable("SQLite operation failed") from error
    except sqlite3.Error as error:
        if connection.in_transaction:
            connection.rollback()
        raise DatabaseUnavailable("SQLite operation failed") from error
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise


def _is_busy(error: sqlite3.OperationalError) -> bool:
    message = str(error).lower()
    return "locked" in message or "busy" in message
