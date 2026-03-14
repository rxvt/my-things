# Plan: Create Initial List Index Screen

Spec: specs/002_create_inital_list_index_page.md
Status: complete

## Overview

Replace the stub `main.py` with a Textual app that displays a ListView of all
lists from the `list_index` database table, with a Footer widget.

## Decisions

- The Textual `App` subclass lives in `main.py` as specified.
- `ListerApp` accepts an optional `db_path` parameter for testability, passed
  through to `init_db()`. This follows the same pattern used in `lib/db.py`.
- DB connection is opened on mount, closed on unmount.
- No selection behavior — selecting a list item is a no-op per the spec.
- Tests use an in-memory database via the `db_path` parameter.

## Steps

### 1. Write this plan file

- [x] Create `plans/002_create_initial_list_index_page.md`

### 2. Update `main.py` with Textual App

- [x] Import `App`, `ComposeResult`, `Footer`, `Label`, `ListItem`, `ListView`
  from textual, and `init_db` from `lib.db`.
- [x] Create `ListerApp(App)` class with:
  - `__init__(db_path=None)` storing the path for later use
  - `on_mount()` — calls `init_db(db_path)`, queries `list_index`, populates
    the ListView
  - `compose()` — yields `ListView()` and `Footer()`
  - `on_unmount()` — closes the DB connection
- [x] `if __name__ == "__main__"` block runs the app.

### 3. Write tests in `tests/test_app.py`

- [x] `test_app_has_footer` — Footer widget is present
- [x] `test_app_has_list_view` — ListView widget is present
- [x] `test_list_view_contains_games` — ListView has a "Games" item (seeded)
- [x] `test_list_view_item_count` — correct number of ListItem children

### 4. Run tests and verify

- [x] `pytest tests/` — 21/21 tests pass
