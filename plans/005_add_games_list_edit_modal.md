# Plan: Add Games List Edit Modal

Spec: specs/005_add_games_list_edit_modal.md
Status: in-progress

## Overview

Add the ability to edit an existing game entry by pressing `e` on the
GamesScreen. The existing `AddGameScreen` modal is reused with pre-populated
fields, an "Edit Game" title, and UPSERT-based save logic.

## Decisions

- **Reuse `AddGameScreen`** rather than creating a separate class. An optional
  `game_data` dict passed to the constructor controls whether the modal is in
  "add" or "edit" mode.
- **UPSERT** (`INSERT ... ON CONFLICT(id) DO UPDATE`) replaces the current
  `INSERT` in the DB helper, so one SQL statement handles both add and edit
  with no branching. The function gains an optional `game_id` parameter;
  `None` means insert (new auto-id), a value means update-on-conflict.
- **Fetch helper** — a new `get_game_by_id()` DB function retrieves the full
  game row (with developer name and platform id) needed to pre-populate the
  form.
- The modal title changes to "Edit Game" when `game_data` is present.
- All existing Add Game behaviour and tests remain unchanged.

## Steps

### 1. Create plan and mark spec in-progress

- [x] Create `plans/005_add_games_list_edit_modal.md`
- [x] Mark spec 005 status as `in-progress`

### 2. Add `get_game_by_id()` DB helper in `lib/db.py`

- [x] New function `get_game_by_id(conn, game_id) -> sqlite3.Row | None`
- [x] Query joins `games` with `developers` to return: `id`, `game` (title),
      `developer_name`, `date_finished`, `platform_id`, `comments`
- [x] Returns `None` if the id doesn't exist

### 3. Convert `insert_game()` to UPSERT in `lib/db.py`

- [x] Add optional `game_id: int | None = None` parameter to `insert_game()`
- [x] Replace the INSERT statement with:
      ```sql
      INSERT INTO games (id, game, date_finished, platform_id, comments, developer_id)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET
        game=excluded.game, date_finished=excluded.date_finished,
        platform_id=excluded.platform_id, comments=excluded.comments,
        developer_id=excluded.developer_id
      ```
- [x] Pass `game_id` (or `None`) as the `id` value
- [x] Existing callers pass no `game_id` so behaviour is unchanged

### 4. Parameterize `AddGameScreen` for edit mode in `lib/screens/add_game.py`

- [x] Add optional `game_data: dict | None = None` parameter to `__init__`
- [x] In `compose()`: if `game_data` is present, set title label text to "Edit Game"
- [x] In `on_mount()` (new): if `game_data` is present, pre-populate all fields:
      - `#input-title` → `game_data["game"]`
      - `#input-developer` → `game_data["developer_name"]`
      - `#input-date-finished` → `game_data["date_finished"]`
      - `#select-platform` → `game_data["platform_id"]`
      - `#input-comments` → preview of `game_data["comments"]`
      - `_full_comments` → `game_data["comments"]`
- [x] In `_save_game()`: pass `game_id=self._game_data["id"]` when in edit mode
      (or `None` when adding) to the UPSERT helper

### 5. Wire up `action_edit()` in `lib/screens/games.py`

- [x] Replace the empty `action_edit()` stub
- [x] Guard: return early if no item is highlighted
- [x] Fetch full game data via `get_game_by_id(self._conn, game_id)`
- [x] Push `AddGameScreen(self._conn, game_data=dict(row))` with callback to
      refresh the list on save

### 6. Write new tests for edit mode in `tests/test_add_game.py`

- [x] `test_edit_modal_appears_on_e` — pressing `e` opens AddGameScreen
- [x] `test_edit_modal_title_is_edit_game` — title label reads "Edit Game"
- [x] `test_edit_modal_prepopulates_title` — Input has existing game title
- [x] `test_edit_modal_prepopulates_developer` — Input has existing developer
- [x] `test_edit_modal_prepopulates_date` — Input has existing date
- [x] `test_edit_modal_prepopulates_platform` — Select has existing platform
- [x] `test_edit_modal_prepopulates_comments` — Input/full_comments has existing comments
- [x] `test_edit_save_updates_existing_game` — DB row updated, no new row created
- [x] `test_edit_cancel_does_not_modify_game` — original data unchanged after cancel
- [x] `test_edit_no_item_highlighted` — pressing `e` with empty list does nothing

### 7. Write new tests for DB helpers in `tests/test_db.py`

- [x] `test_get_game_by_id_returns_row` — returns correct game data
- [x] `test_get_game_by_id_missing` — returns `None` for nonexistent id
- [x] `test_insert_game_upsert_updates` — passing existing `game_id` updates
      the row instead of inserting a new one

### 8. Run tests and verify

- [x] All existing tests pass
- [x] All new tests pass

### 9. Mark spec as implemented

- [ ] `in-progress` → `implemented` (after user confirmation)
