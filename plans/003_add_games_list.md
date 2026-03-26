# Plan: Add Games List

Spec: specs/003_add_games_list.md
Status: in-progress

## Overview

Add a Games screen accessible by selecting "Games" from the index. Refactor
the app to use Textual Screens for navigation, create a Games screen with a
ListView of game entries, and add key bindings for add/edit/delete (only delete
with confirmation dialog is functional).

## Decisions

- Screens live under `lib/screens/` (index.py, games.py) to keep main.py clean.
- Screens receive the DB connection from the app rather than managing their own.
- `a` and `e` key bindings are bound but are no-ops for now.
- Delete confirmation uses a Textual `ModalScreen` that returns True/False.
- Only finished games appear, so `date_finished` is always populated (yyyy-mm-dd).
- Games listed in ascending order by `date_finished`.
- Max 20 entries visible before scrolling.
- First entry highlighted by default.

## Steps

### 1. Create plan and mark spec in-progress

- [x] Create `plans/003_add_games_list.md`
- [x] Mark spec 003 as `in-progress`

### 2. Create `lib/screens/` package

- [x] `lib/screens/__init__.py`

### 3. Create `IndexScreen` in `lib/screens/index.py`

- [x] Extract current index ListView logic from `main.py` into `IndexScreen(Screen)`
- [x] Handle `ListView.Selected` — when "Games" is selected, push `GamesScreen`

### 4. Create `GamesScreen` in `lib/screens/games.py`

- [x] Query `games` table ordered by `date_finished ASC`
- [x] Display each entry as `ListItem` with game title and date
- [x] First entry highlighted by default
- [x] Key bindings: `a` (no-op), `e` (no-op), `d` (delete), `escape` (back)
- [x] Delete: show confirmation modal, if Yes remove from DB and ListView

### 5. Create delete confirmation modal

- [x] `ConfirmDeleteScreen(ModalScreen)` with Yes/No buttons
- [x] No button focused by default
- [x] Returns True (Yes) or False (No)

### 6. Refactor `main.py`

- [x] `MyThingsApp` owns DB connection, pushes `IndexScreen` as default
- [x] Pass connection to screens

### 7. Update CSS

- [x] Games ListView: centered, max-height for 20 entries
- [x] Confirmation dialog styling

### 8. Write tests

- [x] Update existing index tests for screen architecture
- [x] Games screen tests (footer, list view, ordering, highlighting, delete flow, escape)

### 9. Run tests and verify

- [x] All tests pass

### 10. Display format amendment

Spec updated to require the format `{game title} - {date finished} - {platform}`
rather than the original `{game title}  {date finished}`.

#### Modified files

- `lib/screens/games.py` — update `_refresh_list()` to JOIN `platform` table
  and use new label format `f"{row['game']} - {row['date_finished']} - {row['platform_name']}"`
- `tests/test_games.py` — update `_seed_games()` to include `platform_id`
  and `developer_id`; update `test_games_display_date_format` to assert full
  format including platform; add `test_games_display_platform` to assert platform
  name appears in labels
- `tests/test_add_game.py` — update `test_saved_game_appears_in_list` to assert
  platform name is visible in the label

#### Steps

- [x] Update plan
- [x] Update `_refresh_list()` in `lib/screens/games.py`: JOIN platform, new label format
- [x] Update `_seed_games()` in `tests/test_games.py`: add `platform_id` and `developer_id`
- [x] Update `test_games_display_date_format` to assert full `{title} - {date} - {platform}` format
- [x] Add `test_games_display_platform` asserting platform name in labels
- [x] Update `test_saved_game_appears_in_list` in `tests/test_add_game.py`
- [x] Run all tests and verify

### 11. Mark spec as implemented

- [ ] `in-progress` → `implemented` (after user confirmation)
