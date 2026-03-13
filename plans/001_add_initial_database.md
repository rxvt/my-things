# Plan: Add Initial Database

Spec: specs/001_add_initial_database.md
Status: complete

## Overview

Implement the initial SQLite database layer for Lister, including a migration
system using `PRAGMA user_version`, the initial schema (games, developers,
platform, list_index tables), and tests.

## Decisions

- Table name `index` from spec renamed to `list_index` to avoid reserved word conflicts.
- Database file stored at `~/.local/share/lister/entries.db` (XDG data directory).
- Migration versioning: `user_version=0` means fresh/empty DB, `user_version=1`
  applies the initial schema.
- `date_finished` in games table is nullable (allows tracking in-progress games).
- Foreign key columns use `_id` suffix (`platform_id`, `developer_id`) and
  reference the `id` column of the referenced table (not `name`).
- Column names use lowercase (e.g., `name` not `Name`).
- UNIQUE constraints on `developers.name` and `platform.name` to enforce
  consistent naming as described in the spec.
- Initial migration seeds a "Games" entry in `list_index`.
- Tests included using pytest.

## Steps

### 1. Create `plans/` directory and write this plan file

- [x] Create `plans/001_add_initial_database.md`

### 2. Create `lib/` package

- [x] Create `lib/__init__.py` (empty)
- [x] Create `lib/db.py` (main database module)

### 3. Implement database connection and path management in `lib/db.py`

- [x] `get_db_path() -> Path` — returns `~/.local/share/lister/entries.db`,
  creating parent directories if needed.
- [x] `get_connection(db_path: Path | None = None) -> sqlite3.Connection` —
  opens a connection with `PRAGMA foreign_keys = ON`. Accepts optional path
  override for testing.

### 4. Implement migration system in `lib/db.py`

- [x] `get_current_version(conn: sqlite3.Connection) -> int` — reads
  `PRAGMA user_version`.
- [x] `MIGRATIONS: dict[int, Callable]` — module-level mapping of version
  numbers to migration functions.
- [x] `run_migrations(conn: sqlite3.Connection) -> None` — applies all
  unapplied migrations in order, updating `user_version` after each.

### 5. Implement migration v1 — initial schema

`migrate_v1(conn)` creates the following tables and seeds data:

```sql
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
```

Seeds `list_index` with: `INSERT INTO list_index (name) VALUES ('Games')`.

### 6. Implement convenience entry point

- [x] `init_db(db_path: Path | None = None) -> sqlite3.Connection` — gets a
  connection, runs migrations, returns the connection. This is the main entry
  point other modules will call.

### 7. Add pytest as a dev dependency

- [x] `uv add --dev pytest`

### 8. Write tests in `tests/test_db.py`

- [x] `tests/__init__.py` (empty)
- [x] `test_get_db_path` — path ends with `entries.db` under the XDG data dir.
- [x] `test_init_db_creates_tables` — all 4 tables exist after `init_db` on
  an in-memory DB.
- [x] `test_migration_v1_schema` — correct column names and types for each table.
- [x] `test_migration_v1_seeds_list_index` — "Games" row present in `list_index`.
- [x] `test_foreign_keys_enforced` — inserting a game with a bad `platform_id`
  raises `IntegrityError`.
- [x] `test_migrations_idempotent` — calling `run_migrations` twice is a no-op.
- [x] `test_get_current_version` — `user_version` is 1 after `init_db`.
- [x] `test_date_finished_is_nullable` — NULL date_finished inserts successfully.

### 9. Add `entries.db` to `.gitignore`

- [x] Append `entries.db` to `.gitignore`.

### 10. Run tests and verify

- [x] `pytest tests/` — 15/15 tests pass.
