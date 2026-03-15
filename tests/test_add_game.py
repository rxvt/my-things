"""Tests for the add game modal screen."""

import re
from datetime import date
from pathlib import Path

import pytest
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select
from textual.widgets import TextArea

from lib.screens.add_game import AddGameScreen
from lib.screens.add_game import _comments_preview
from lib.screens.comments_editor import CommentsEditorScreen
from lib.screens.games import GamesScreen
from lib.screens.index import IndexScreen
from main import MyThingsApp

_MEMORY = Path(":memory:")


@pytest.fixture
def app() -> MyThingsApp:
    """Return a MyThingsApp instance backed by an in-memory database."""
    return MyThingsApp(db_path=_MEMORY)


async def _navigate_to_games(pilot) -> None:
    """Navigate from index to games screen."""
    await pilot.press("enter")
    await pilot.pause()


# ---------------------------------------------------------------------------
# Modal appearance
# ---------------------------------------------------------------------------


async def test_add_modal_appears_on_a(app: MyThingsApp) -> None:
    """Pressing 'a' on the games screen should show the AddGameScreen modal."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        assert isinstance(pilot.app.screen, GamesScreen)
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(pilot.app.screen, AddGameScreen)


async def test_add_modal_has_title_input(app: MyThingsApp) -> None:
    """The add game modal should have a title input field."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        assert title_input is not None


async def test_add_modal_has_developer_input(app: MyThingsApp) -> None:
    """The add game modal should have a developer input field."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        assert dev_input is not None


async def test_add_modal_has_date_input(app: MyThingsApp) -> None:
    """The add game modal should have a date finished input field."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        assert date_input is not None


async def test_add_modal_has_platform_select(app: MyThingsApp) -> None:
    """The add game modal should have a platform select widget."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        platform_select = pilot.app.screen.query_one("#select-platform", Select)
        assert platform_select is not None


async def test_add_modal_has_comments_input(app: MyThingsApp) -> None:
    """The add game modal should have a comments input field."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        assert comments_input is not None


async def test_date_finished_defaults_to_today(app: MyThingsApp) -> None:
    """The Date Finished field should default to today's date in yyyy-mm-dd format."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        assert date_input.value == date.today().isoformat()
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", date_input.value)


async def test_platform_select_has_first_entry_selected(app: MyThingsApp) -> None:
    """The platform select should have the first entry pre-selected."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        platform_select = pilot.app.screen.query_one("#select-platform", Select)
        assert not platform_select.is_blank()


# ---------------------------------------------------------------------------
# Cancel / escape
# ---------------------------------------------------------------------------


async def test_cancel_button_dismisses_modal(app: MyThingsApp) -> None:
    """Pressing the Cancel button should dismiss the modal."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        cancel_btn = pilot.app.screen.query_one("#btn-cancel", Button)
        cancel_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)


async def test_escape_dismisses_modal(app: MyThingsApp) -> None:
    """Pressing escape should dismiss the add game modal."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(pilot.app.screen, AddGameScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


async def test_save_empty_title_shows_error(app: MyThingsApp) -> None:
    """Saving with an empty title should show a validation error."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        error_label = pilot.app.screen.query_one("#validation-error", Label)
        assert "Title" in error_label.content
        # Should still be on the add game screen
        assert isinstance(pilot.app.screen, AddGameScreen)


async def test_save_empty_developer_shows_error(app: MyThingsApp) -> None:
    """Saving with an empty developer should show a validation error."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Fill in title only
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Test Game"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        error_label = pilot.app.screen.query_one("#validation-error", Label)
        assert "Developer" in error_label.content


async def test_save_empty_date_shows_error(app: MyThingsApp) -> None:
    """Saving with an empty date should show a validation error."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Test Game"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Test Dev"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = ""
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        error_label = pilot.app.screen.query_one("#validation-error", Label)
        assert "Date" in error_label.content


async def test_save_invalid_date_format_shows_error(app: MyThingsApp) -> None:
    """Saving with an invalid date format should show a validation error."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Test Game"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Test Dev"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2024-1-5"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        error_label = pilot.app.screen.query_one("#validation-error", Label)
        assert "yyyy-mm-dd" in error_label.content


# ---------------------------------------------------------------------------
# Successful save
# ---------------------------------------------------------------------------


async def test_save_valid_game_creates_entry(app: MyThingsApp) -> None:
    """Saving valid data should insert a game and return to the games screen."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Fill in all required fields
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Hollow Knight"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Team Cherry"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2023-06-15"
        # Platform is pre-selected, so no action needed
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        # Should be back on the games screen
        assert isinstance(pilot.app.screen, GamesScreen)
        # Verify the game was added to the database
        conn = app._conn
        assert conn is not None
        row = conn.execute(
            "SELECT game FROM games WHERE game = ?", ("Hollow Knight",)
        ).fetchone()
        assert row is not None


async def test_save_creates_new_developer(app: MyThingsApp) -> None:
    """Saving with a new developer name should create a developers entry."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Celeste"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Maddy Makes Games"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2022-03-10"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        conn = app._conn
        assert conn is not None
        dev_row = conn.execute(
            "SELECT name FROM developers WHERE name = ?",
            ("Maddy Makes Games",),
        ).fetchone()
        assert dev_row is not None


async def test_save_reuses_existing_developer(app: MyThingsApp) -> None:
    """Saving with an existing developer name should reuse the entry."""
    async with app.run_test() as pilot:
        # Pre-create a developer
        conn = app._conn
        assert conn is not None
        conn.execute("INSERT INTO developers (name) VALUES (?)", ("Team Cherry",))
        conn.commit()
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Hollow Knight"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Team Cherry"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2023-06-15"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        # Should still only have one developer with that name
        dev_count = conn.execute(
            "SELECT COUNT(*) FROM developers WHERE name = ?",
            ("Team Cherry",),
        ).fetchone()
        assert dev_count[0] == 1


async def test_save_with_comments(app: MyThingsApp) -> None:
    """Saving with comments should store them in the database."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Elden Ring"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "FromSoftware"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2024-01-20"
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        comments_input.value = "Amazing game"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        conn = app._conn
        assert conn is not None
        row = conn.execute(
            "SELECT comments FROM games WHERE game = ?", ("Elden Ring",)
        ).fetchone()
        assert row["comments"] == "Amazing game"


async def test_save_without_comments_stores_null(app: MyThingsApp) -> None:
    """Saving without comments should store NULL in the database."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Celeste"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Maddy Makes Games"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2022-03-10"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        conn = app._conn
        assert conn is not None
        row = conn.execute(
            "SELECT comments FROM games WHERE game = ?", ("Celeste",)
        ).fetchone()
        assert row["comments"] is None


async def test_saved_game_appears_in_list(app: MyThingsApp) -> None:
    """After saving, the new game should appear in the games list."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        title_input = pilot.app.screen.query_one("#input-title", Input)
        title_input.value = "Hollow Knight"
        dev_input = pilot.app.screen.query_one("#input-developer", Input)
        dev_input.value = "Team Cherry"
        date_input = pilot.app.screen.query_one("#input-date-finished", Input)
        date_input.value = "2023-06-15"
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        from textual.widgets import ListItem as LI

        list_view = pilot.app.screen.query_one("#games-list")
        items = list_view.query(LI)
        assert len(items) == 1
        label_text = items[0].query_one(Label).content
        assert "Hollow Knight" in label_text
        assert "2023-06-15" in label_text


# ---------------------------------------------------------------------------
# _comments_preview unit tests
# ---------------------------------------------------------------------------


def test_comments_preview_short_single_line() -> None:
    """A short single-line string should be returned unchanged."""
    assert _comments_preview("Great game") == "Great game"


def test_comments_preview_takes_first_line() -> None:
    """Only the first line of multi-line text should be returned."""
    result = _comments_preview("First line\nSecond line\nThird line")
    assert result == "First line"


def test_comments_preview_truncates_long_line() -> None:
    """A line longer than max_len chars should be truncated with ellipsis."""
    long = "x" * 80
    result = _comments_preview(long, max_len=60)
    assert len(result) == 61  # 60 chars + "…"
    assert result.endswith("…")


def test_comments_preview_empty_string() -> None:
    """An empty string should return an empty string."""
    assert _comments_preview("") == ""


# ---------------------------------------------------------------------------
# Expand button presence
# ---------------------------------------------------------------------------


async def test_add_modal_has_expand_button(app: MyThingsApp) -> None:
    """The add game modal should have an Expand button next to Comments."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        assert btn is not None


# ---------------------------------------------------------------------------
# CommentsEditorScreen opens and closes
# ---------------------------------------------------------------------------


async def test_expand_button_opens_editor(app: MyThingsApp) -> None:
    """Clicking the Expand button should open the CommentsEditorScreen."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CommentsEditorScreen)


async def test_editor_has_textarea(app: MyThingsApp) -> None:
    """The CommentsEditorScreen should contain a TextArea widget."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        ta = pilot.app.screen.query_one("#comments-textarea", TextArea)
        assert ta is not None


async def test_editor_cancel_returns_to_add_form(app: MyThingsApp) -> None:
    """Cancelling the editor should return to AddGameScreen without changes."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CommentsEditorScreen)
        cancel_btn = pilot.app.screen.query_one("#btn-comments-cancel", Button)
        cancel_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, AddGameScreen)


async def test_editor_escape_returns_to_add_form(app: MyThingsApp) -> None:
    """Pressing escape in the editor should return to AddGameScreen."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, CommentsEditorScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, AddGameScreen)


async def test_editor_cancel_preserves_existing_comments(app: MyThingsApp) -> None:
    """Cancelling the editor should leave the comments Input unchanged."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Type a short comment directly
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        comments_input.value = "Short note"
        # Open editor and cancel
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        cancel_btn = pilot.app.screen.query_one("#btn-comments-cancel", Button)
        cancel_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        # Comments Input should be unchanged
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        assert comments_input.value == "Short note"


# ---------------------------------------------------------------------------
# Text sync between editor and Input preview
# ---------------------------------------------------------------------------


async def test_editor_save_syncs_preview_to_input(app: MyThingsApp) -> None:
    """Saving in the editor should update the comments Input with a preview."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Open editor
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        # Type in the TextArea
        ta = pilot.app.screen.query_one("#comments-textarea", TextArea)
        ta.load_text("Line one\nLine two")
        # Save
        save_btn = pilot.app.screen.query_one("#btn-comments-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, AddGameScreen)
        # Input should show first-line preview
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        assert comments_input.value == "Line one"


async def test_editor_saves_full_multiline_to_db(app: MyThingsApp) -> None:
    """Multi-line comments entered via the editor should be stored in full."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Fill required fields
        pilot.app.screen.query_one("#input-title", Input).value = "Hollow Knight"
        pilot.app.screen.query_one("#input-developer", Input).value = "Team Cherry"
        pilot.app.screen.query_one("#input-date-finished", Input).value = "2023-06-15"
        # Open editor and enter multi-line text
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        ta = pilot.app.screen.query_one("#comments-textarea", TextArea)
        ta.load_text("Great game\n\nVery challenging boss fights.")
        save_btn = pilot.app.screen.query_one("#btn-comments-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        # Save the game
        save_btn = pilot.app.screen.query_one("#btn-save", Button)
        save_btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        conn = app._conn
        assert conn is not None
        row = conn.execute(
            "SELECT comments FROM games WHERE game = ?", ("Hollow Knight",)
        ).fetchone()
        assert row["comments"] == "Great game\n\nVery challenging boss fights."


async def test_editor_prepopulated_with_existing_text(app: MyThingsApp) -> None:
    """Opening the editor should pre-populate the TextArea with existing comments."""
    async with app.run_test() as pilot:
        await _navigate_to_games(pilot)
        await pilot.press("a")
        await pilot.pause()
        # Enter a comment directly in the Input
        comments_input = pilot.app.screen.query_one("#input-comments", Input)
        comments_input.value = "Existing note"
        # Open editor — it should be pre-populated
        btn = pilot.app.screen.query_one("#btn-expand-comments", Button)
        btn.focus()
        await pilot.press("enter")
        await pilot.pause()
        ta = pilot.app.screen.query_one("#comments-textarea", TextArea)
        assert ta.text == "Existing note"
