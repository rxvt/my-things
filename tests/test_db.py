"""Tests for lib/db.py — database connection, migrations, and schema."""

import sqlite3
from pathlib import Path

import pytest
from xdg_base_dirs import xdg_data_home

from lib.db import (
    MIGRATIONS,
    get_connection,
    get_current_version,
    get_db_path,
    init_db,
    run_migrations,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MEMORY = Path(":memory:")


def _memory_conn() -> sqlite3.Connection:
    """Return a fresh in-memory database connection."""
    return get_connection(_MEMORY)


# ---------------------------------------------------------------------------
# get_db_path
# ---------------------------------------------------------------------------


def test_get_db_path_returns_entries_db() -> None:
    """Path should end with entries.db under the XDG data directory."""
    path = get_db_path()
    assert path == xdg_data_home() / "my-things" / "entries.db"


def test_get_db_path_creates_parent_directory() -> None:
    """Calling get_db_path should ensure the parent directory exists."""
    path = get_db_path()
    assert path.parent.is_dir()


# ---------------------------------------------------------------------------
# get_connection
# ---------------------------------------------------------------------------


def test_get_connection_returns_connection() -> None:
    """get_connection should return a sqlite3.Connection."""
    conn = _memory_conn()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_get_connection_enables_foreign_keys() -> None:
    """Foreign keys should be ON by default."""
    conn = _memory_conn()
    row = conn.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1
    conn.close()


# ---------------------------------------------------------------------------
# get_current_version
# ---------------------------------------------------------------------------


def test_get_current_version_fresh_db_is_zero() -> None:
    """A new database should report user_version == 0."""
    conn = _memory_conn()
    assert get_current_version(conn) == 0
    conn.close()


def test_get_current_version_after_init_is_one() -> None:
    """After init_db, user_version should equal the latest migration version."""
    conn = init_db(_MEMORY)
    assert get_current_version(conn) == max(MIGRATIONS)
    conn.close()


# ---------------------------------------------------------------------------
# run_migrations / idempotency
# ---------------------------------------------------------------------------


def test_migrations_idempotent() -> None:
    """Calling run_migrations twice should not raise or change version."""
    conn = _memory_conn()
    run_migrations(conn)
    version_after_first = get_current_version(conn)
    run_migrations(conn)
    version_after_second = get_current_version(conn)
    assert version_after_first == version_after_second
    conn.close()


def test_run_migrations_explicit_registry() -> None:
    """run_migrations should use the provided registry instead of the global one."""
    applied: list[int] = []

    def fake_migration(conn: sqlite3.Connection) -> None:
        applied.append(99)

    conn = _memory_conn()
    run_migrations(conn, migrations={99: fake_migration})
    assert applied == [99]
    assert get_current_version(conn) == 99
    conn.close()


def test_run_migrations_empty_registry_is_noop() -> None:
    """Passing an empty registry should leave the database untouched."""
    conn = _memory_conn()
    run_migrations(conn, migrations={})
    assert get_current_version(conn) == 0
    conn.close()


# ---------------------------------------------------------------------------
# init_db — tables exist
# ---------------------------------------------------------------------------


def _table_names(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    return {row[0] for row in rows}


def test_init_db_creates_all_tables() -> None:
    """All four required tables should exist after init_db."""
    conn = init_db(_MEMORY)
    tables = _table_names(conn)
    assert {"developers", "platform", "list_index", "games"}.issubset(tables)
    conn.close()


# ---------------------------------------------------------------------------
# Schema correctness
# ---------------------------------------------------------------------------


def _column_names(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()  # noqa: S608
    return [row[1] for row in rows]


def test_developers_schema() -> None:
    conn = init_db(_MEMORY)
    cols = _column_names(conn, "developers")
    assert cols == ["id", "name"]
    conn.close()


def test_platform_schema() -> None:
    conn = init_db(_MEMORY)
    cols = _column_names(conn, "platform")
    assert cols == ["id", "name"]
    conn.close()


def test_list_index_schema() -> None:
    conn = init_db(_MEMORY)
    cols = _column_names(conn, "list_index")
    assert cols == ["id", "name"]
    conn.close()


def test_games_schema() -> None:
    conn = init_db(_MEMORY)
    cols = _column_names(conn, "games")
    assert cols == [
        "id",
        "game",
        "date_finished",
        "platform_id",
        "comments",
        "developer_id",
    ]
    conn.close()


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------


def test_migration_v1_seeds_games_in_list_index() -> None:
    """list_index should contain a 'Games' row after the initial migration."""
    conn = init_db(_MEMORY)
    row = conn.execute("SELECT name FROM list_index WHERE name = 'Games'").fetchone()
    assert row is not None
    assert row[0] == "Games"
    conn.close()


# ---------------------------------------------------------------------------
# Foreign key enforcement
# ---------------------------------------------------------------------------


def test_foreign_key_violation_raises_integrity_error() -> None:
    """Inserting a game with a non-existent platform_id should raise IntegrityError."""
    conn = init_db(_MEMORY)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO games (game, platform_id) VALUES (?, ?)",
            ("Hollow Knight", 9999),
        )
        conn.commit()
    conn.close()


def test_date_finished_is_nullable() -> None:
    """Inserting a game with date_finished=NULL should succeed."""
    conn = init_db(_MEMORY)
    conn.execute(
        "INSERT INTO games (game, date_finished) VALUES (?, NULL)",
        ("Elden Ring",),
    )
    conn.commit()
    row = conn.execute(
        "SELECT date_finished FROM games WHERE game = 'Elden Ring'"
    ).fetchone()
    assert row[0] is None
    conn.close()
