"""Narrow public errors for durable engineering state."""


class PersistenceError(Exception):
    """Base class for persistence operation failures."""


class PersistenceIntegrityError(PersistenceError):
    """Stored data or an immutable identity violates its durable contract."""


class ConcurrencyConflict(PersistenceError):
    """A caller's expected current revision is no longer durable current state."""


class MigrationError(PersistenceError):
    """Database migration definitions, checksums, or schema are incompatible."""


class DatabaseUnavailable(PersistenceError):
    """SQLite could not open or operate on the requested database."""
