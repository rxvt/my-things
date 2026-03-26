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
    get_developer_names,
    get_game_by_id,
    get_or_create_developer,
    get_platforms,
    init_db,
    insert_game,
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


# ---------------------------------------------------------------------------
# Migration v2 — platform seed data
# ---------------------------------------------------------------------------


def test_migration_v2_seeds_platform_table() -> None:
    """The platform table should contain all 10 seeded entries after init."""
    conn = init_db(_MEMORY)
    rows = conn.execute("SELECT name FROM platform ORDER BY name").fetchall()
    names = {row["name"] for row in rows}
    expected = {
        "Switch",
        "PS3",
        "PS4",
        "PS5",
        "PC",
        "Xbox360",
        "3DS",
        "Dolphin",
        "Xbox",
        "NES",
    }
    assert names == expected
    conn.close()


def test_migration_v2_platform_count() -> None:
    """The platform table should have exactly 10 entries."""
    conn = init_db(_MEMORY)
    row = conn.execute("SELECT COUNT(*) FROM platform").fetchone()
    assert row[0] == 10
    conn.close()


# ---------------------------------------------------------------------------
# get_developer_names
# ---------------------------------------------------------------------------


def test_get_developer_names_empty() -> None:
    """get_developer_names returns an empty list when no developers exist."""
    conn = init_db(_MEMORY)
    assert get_developer_names(conn) == []
    conn.close()


def test_get_developer_names_returns_sorted_names() -> None:
    """get_developer_names returns names in alphabetical order."""
    conn = init_db(_MEMORY)
    conn.executemany(
        "INSERT INTO developers (name) VALUES (?)",
        [("Zelda Studio",), ("Argonaut",), ("Midway",)],
    )
    conn.commit()
    assert get_developer_names(conn) == ["Argonaut", "Midway", "Zelda Studio"]
    conn.close()


# ---------------------------------------------------------------------------
# get_platforms
# ---------------------------------------------------------------------------


def test_get_platforms_returns_name_id_tuples() -> None:
    """get_platforms returns (name, id) tuples for each platform."""
    conn = init_db(_MEMORY)
    result = get_platforms(conn)
    assert all(len(t) == 2 for t in result)
    names = [name for name, _ in result]
    assert "Switch" in names
    assert "PC" in names
    conn.close()


def test_get_platforms_returns_sorted_by_name() -> None:
    """get_platforms returns platforms in alphabetical order."""
    conn = init_db(_MEMORY)
    result = get_platforms(conn)
    names = [name for name, _ in result]
    assert names == sorted(names)
    conn.close()


def test_get_platforms_ids_are_ints() -> None:
    """get_platforms returns integer ids."""
    conn = init_db(_MEMORY)
    result = get_platforms(conn)
    assert all(isinstance(pid, int) for _, pid in result)
    conn.close()


# ---------------------------------------------------------------------------
# get_or_create_developer
# ---------------------------------------------------------------------------


def test_get_or_create_developer_creates_new() -> None:
    """get_or_create_developer inserts a new row when the name is unknown."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    row = conn.execute(
        "SELECT id, name FROM developers WHERE name = 'Team Cherry'"
    ).fetchone()
    assert row is not None
    assert row["id"] == dev_id
    conn.close()


def test_get_or_create_developer_returns_existing_id() -> None:
    """get_or_create_developer returns the existing id without inserting a duplicate."""
    conn = init_db(_MEMORY)
    first_id = get_or_create_developer(conn, "FromSoftware")
    second_id = get_or_create_developer(conn, "FromSoftware")
    assert first_id == second_id
    count = conn.execute(
        "SELECT COUNT(*) FROM developers WHERE name = 'FromSoftware'"
    ).fetchone()[0]
    assert count == 1
    conn.close()


def test_get_or_create_developer_returns_int() -> None:
    """get_or_create_developer always returns an int."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Nintendo")
    assert isinstance(dev_id, int)
    conn.close()


# ---------------------------------------------------------------------------
# insert_game
# ---------------------------------------------------------------------------


def _platform_id(conn: sqlite3.Connection) -> int:
    """Return the id of the first platform in the database."""
    return int(conn.execute("SELECT id FROM platform LIMIT 1").fetchone()["id"])


def test_insert_game_creates_row() -> None:
    """insert_game inserts a row into the games table."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    plat_id = _platform_id(conn)
    insert_game(
        conn,
        title="Hollow Knight",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments=None,
    )
    conn.commit()
    row = conn.execute("SELECT game FROM games WHERE game = 'Hollow Knight'").fetchone()
    assert row is not None
    conn.close()


def test_insert_game_returns_int_id() -> None:
    """insert_game returns the integer id of the new row."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    plat_id = _platform_id(conn)
    game_id = insert_game(
        conn,
        title="Hollow Knight",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments=None,
    )
    conn.commit()
    assert isinstance(game_id, int)
    conn.close()


def test_insert_game_stores_comments() -> None:
    """insert_game persists the comments value."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "FromSoftware")
    plat_id = _platform_id(conn)
    insert_game(
        conn,
        title="Elden Ring",
        developer_id=dev_id,
        date_finished="2024-01-20",
        platform_id=plat_id,
        comments="Incredible open world.",
    )
    conn.commit()
    row = conn.execute(
        "SELECT comments FROM games WHERE game = 'Elden Ring'"
    ).fetchone()
    assert row["comments"] == "Incredible open world."
    conn.close()


def test_insert_game_null_comments_when_empty() -> None:
    """insert_game stores NULL when an empty string is passed for comments."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    plat_id = _platform_id(conn)
    insert_game(
        conn,
        title="Hollow Knight",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments="",
    )
    conn.commit()
    row = conn.execute(
        "SELECT comments FROM games WHERE game = 'Hollow Knight'"
    ).fetchone()
    assert row["comments"] is None
    conn.close()


def test_insert_game_upsert_updates_existing_row() -> None:
    """Passing game_id to insert_game updates the row instead of inserting a new one."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    plat_id = _platform_id(conn)
    game_id = insert_game(
        conn,
        title="Hollow Knight",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments=None,
    )
    conn.commit()
    # Update the title via UPSERT
    insert_game(
        conn,
        title="Hollow Knight: Silksong",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments=None,
        game_id=game_id,
    )
    conn.commit()
    # Should still be only one row
    count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    assert count == 1
    # And the title should be updated
    row = conn.execute("SELECT game FROM games WHERE id = ?", (game_id,)).fetchone()
    assert row["game"] == "Hollow Knight: Silksong"
    conn.close()


# ---------------------------------------------------------------------------
# get_game_by_id
# ---------------------------------------------------------------------------


def test_get_game_by_id_returns_row() -> None:
    """get_game_by_id returns correct game data for a known id."""
    conn = init_db(_MEMORY)
    dev_id = get_or_create_developer(conn, "Team Cherry")
    plat_id = _platform_id(conn)
    game_id = insert_game(
        conn,
        title="Hollow Knight",
        developer_id=dev_id,
        date_finished="2023-06-15",
        platform_id=plat_id,
        comments="Great game",
    )
    conn.commit()
    row = get_game_by_id(conn, game_id)
    assert row is not None
    assert row["id"] == game_id
    assert row["game"] == "Hollow Knight"
    assert row["developer_name"] == "Team Cherry"
    assert row["date_finished"] == "2023-06-15"
    assert row["platform_id"] == plat_id
    assert row["comments"] == "Great game"
    conn.close()


def test_get_game_by_id_missing_returns_none() -> None:
    """get_game_by_id returns None when no row with the given id exists."""
    conn = init_db(_MEMORY)
    result = get_game_by_id(conn, 99999)
    assert result is None
    conn.close()
