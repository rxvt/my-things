"""Database connection, path management, and schema migrations for My Things.

This module provides the core database layer built on SQLite. It uses
``PRAGMA user_version`` to implement a simple hand-rolled migration system.

Typical usage:

    from lib.db import init_db

    conn = init_db()
    # use conn ...
    conn.close()
"""

import logging
import sqlite3
from collections.abc import Callable
from pathlib import Path

from xdg_base_dirs import xdg_data_home

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Return the path to the database file, creating parent dirs if needed.

    The database is stored under the XDG data home directory:
    ``~/.local/share/my-things/entries.db``.

    Returns:
        A :class:`Path` pointing to the database file.
    """
    data_dir = xdg_data_home() / "my-things"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "entries.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open and return a SQLite connection with foreign keys enabled.

    Args:
        db_path: Path to the database file. Defaults to the result of
            :func:`get_db_path`. Pass ``Path(":memory:")`` in tests to use an
            in-memory database.

    Returns:
        An open :class:`sqlite3.Connection` with ``PRAGMA foreign_keys = ON``.
    """
    path = db_path if db_path is not None else get_db_path()
    # sqlite3 accepts ":memory:" as a string, not a Path
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    logger.debug("Opened database connection: %s", path)
    return conn


# ---------------------------------------------------------------------------
# Migration helpers
# ---------------------------------------------------------------------------


def get_current_version(conn: sqlite3.Connection) -> int:
    """Return the current schema version from ``PRAGMA user_version``.

    Args:
        conn: An open database connection.

    Returns:
        The integer value of ``user_version`` (0 for a fresh database).
    """
    row = conn.execute("PRAGMA user_version").fetchone()
    return int(row[0])


def _set_version(conn: sqlite3.Connection, version: int) -> None:
    """Set ``PRAGMA user_version`` to *version*.

    Args:
        conn: An open database connection.
        version: The new schema version to record.
    """
    # user_version cannot be set via parameter substitution
    conn.execute(f"PRAGMA user_version = {version:d}")


# ---------------------------------------------------------------------------
# Individual migrations
# ---------------------------------------------------------------------------


def _migrate_v1(conn: sqlite3.Connection) -> None:
    """Apply migration v1: create initial schema and seed reference data.

    Creates the ``developers``, ``platform``, ``list_index``, and ``games``
    tables, then seeds ``list_index`` with a "Games" entry.

    Args:
        conn: An open database connection.
    """
    conn.executescript(
        """
        CREATE TABLE developers (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE platform (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE list_index (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE games (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            game          TEXT    NOT NULL,
            date_finished TEXT,
            platform_id   INTEGER,
            comments      TEXT,
            developer_id  INTEGER,
            FOREIGN KEY (platform_id)  REFERENCES platform(id),
            FOREIGN KEY (developer_id) REFERENCES developers(id)
        );

        INSERT INTO list_index (name) VALUES ('Games');
        """
    )
    logger.info("Applied migration v1: initial schema")


# ---------------------------------------------------------------------------
# Migration registry and runner
# ---------------------------------------------------------------------------

#: Mapping of schema version → migration function.
#: Add new migrations here in ascending order.
MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {
    1: _migrate_v1,
}


def run_migrations(
    conn: sqlite3.Connection,
    migrations: dict[int, Callable[[sqlite3.Connection], None]] | None = None,
) -> None:
    """Apply all pending migrations to the database.

    Compares the database's current ``user_version`` against *migrations* and
    applies any migrations with a version number higher than the current
    version, in ascending order.  Updates ``user_version`` after each
    successful migration.

    Args:
        conn: An open database connection.
        migrations: Mapping of schema version to migration function. Defaults
            to the module-level :data:`MIGRATIONS` registry.
    """
    pending = MIGRATIONS if migrations is None else migrations
    current = get_current_version(conn)
    logger.debug("Current schema version: %d", current)

    for version in sorted(pending):
        if version <= current:
            continue
        logger.info("Running migration to version %d", version)
        pending[version](conn)
        _set_version(conn, version)
        conn.commit()
        logger.info("Schema now at version %d", version)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def init_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Initialise the database and return a ready-to-use connection.

    Opens (or creates) the database, runs any pending migrations, and returns
    the connection.  Callers are responsible for closing the connection when
    finished.

    Args:
        db_path: Optional path override. Defaults to the XDG data directory.
            Pass ``Path(":memory:")`` in tests to use an in-memory database.

    Returns:
        An open, migrated :class:`sqlite3.Connection`.
    """
    conn = get_connection(db_path)
    run_migrations(conn)
    return conn
