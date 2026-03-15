# Plan: Add Game to List

Spec: specs/004_add_game_to_list.md
Status: in-progress

## Overview

Add the ability to add a new game to the Games list via a modal form. Pressing
`a` on the GamesScreen opens an `AddGameScreen` modal with fields for Title,
Developer (with autocomplete), Date Finished, Platform (select), and Comments.

## Decisions

- The form is a `ModalScreen` that overlays the Games list, matching the
  pattern established by `ConfirmDeleteScreen`.
- **Developer field** uses a Textual `Input` with a `SuggestFromList` suggester
  built from existing developer names. If the typed name doesn't match an
  existing developer, a new `developers` row is inserted on save.
- **Platform field** uses a Textual `Select` widget populated from the
  `platform` table. `allow_blank=False` so the first entry is pre-selected.
- **Date Finished** uses an `Input` with `restrict` regex to enforce
  `yyyy-mm-dd` format and a `Regex` validator.
- A new migration (v2) seeds the `platform` table with the 10 entries from
  the spec.
- The modal has Save and Cancel buttons. Escape also cancels.
- Validation errors are shown inline when the user attempts to save.

## Steps

### 1. Create plan and mark spec in-progress

- [x] Create `plans/004_add_game_to_list.md`
- [ ] Mark spec 004 as `in-progress`

### 2. Add migration v2: seed platform table

- [ ] Add `_migrate_v2` to `lib/db.py` that inserts the 10 platform entries
- [ ] Register in `MIGRATIONS` dict as `{2: _migrate_v2}`

### 3. Create `AddGameScreen` modal in `lib/screens/add_game.py`

- [ ] `AddGameScreen(ModalScreen)` receives `conn` in constructor
- [ ] Fields: Title (Input), Developer (Input with SuggestFromList),
      Date Finished (Input with restrict/validator), Platform (Select),
      Comments (Input)
- [ ] Save button: validate all required fields, insert into DB, dismiss
- [ ] Cancel button / escape: dismiss without saving
- [ ] On save: look up or create developer, insert game row, commit

### 4. Wire up `action_add()` in GamesScreen

- [ ] Push `AddGameScreen(self._conn)` with callback to refresh list

### 5. Add CSS styling for AddGameScreen

- [x] Style the modal form (width, padding, field layout)

### 6. Write tests

- [x] Migration v2 test: platform table seeded with 10 entries
- [x] AddGameScreen tests: modal appears on `a`, fields present,
      save with valid data creates entry, cancel dismisses,
      validation prevents empty required fields, new developer created,
      date format enforced

### 7. Run tests and verify

- [x] All tests pass

### 8. Expandable comments editor (amendment)

Following user feedback, the Comments field was extended with an "Expand"
button that opens a separate `CommentsEditorScreen` modal backed by a
full `TextArea` with markdown syntax highlighting.

#### Implementation details

- `_full_comments: str` on `AddGameScreen` holds the authoritative text
- `_updating_preview: bool` flag prevents `on_input_changed` from overwriting
  `_full_comments` with the truncated preview after the editor saves
- The flag is consumed (set back to `False`) on the next `Input.Changed` event
  rather than synchronously, because Textual dispatches the event asynchronously

#### New files

- `lib/screens/comments_editor.py` — `CommentsEditorScreen(ModalScreen[str | None])`
  with `TextArea(language="markdown")`, Save/Cancel buttons, ctrl+s and escape bindings

#### Modified files

- `lib/screens/add_game.py` — Expand button, `_full_comments` tracking,
  `_handle_editor_result`, `_comments_preview` helper
- `main.tcss` — `#comments-row`, `CommentsEditorScreen`, `#comments-textarea` styles
- `tests/test_add_game.py` — 13 new tests for editor behaviour and text sync

### 9. Mark spec as implemented

- [ ] `in-progress` → `implemented` (after user confirmation)
