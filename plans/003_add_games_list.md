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

- [ ] `lib/screens/__init__.py`

### 3. Create `IndexScreen` in `lib/screens/index.py`

- [ ] Extract current index ListView logic from `main.py` into `IndexScreen(Screen)`
- [ ] Handle `ListView.Selected` — when "Games" is selected, push `GamesScreen`

### 4. Create `GamesScreen` in `lib/screens/games.py`

- [ ] Query `games` table ordered by `date_finished ASC`
- [ ] Display each entry as `ListItem` with game title and date
- [ ] First entry highlighted by default
- [ ] Key bindings: `a` (no-op), `e` (no-op), `d` (delete), `escape` (back)
- [ ] Delete: show confirmation modal, if Yes remove from DB and ListView

### 5. Create delete confirmation modal

- [ ] `ConfirmDeleteScreen(ModalScreen)` with Yes/No buttons
- [ ] No button focused by default
- [ ] Returns True (Yes) or False (No)

### 6. Refactor `main.py`

- [ ] `MyThingsApp` owns DB connection, pushes `IndexScreen` as default
- [ ] Pass connection to screens

### 7. Update CSS

- [ ] Games ListView: centered, max-height for 20 entries
- [ ] Confirmation dialog styling

### 8. Write tests

- [ ] Update existing index tests for screen architecture
- [ ] Games screen tests (footer, list view, ordering, highlighting, delete flow, escape)

### 9. Run tests and verify

- [ ] All tests pass

### 10. Mark spec as implemented

- [ ] `in-progress` → `implemented`
