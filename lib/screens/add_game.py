"""Add game modal screen — form for adding a new game entry."""

import re
import sqlite3
from datetime import date

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Select

from lib.db import get_developer_names
from lib.db import get_or_create_developer
from lib.db import get_platforms
from lib.db import insert_game
from lib.screens.comments_editor import CommentsEditorScreen

_PREVIEW_MAX_LEN = 60


def _comments_preview(text: str, max_len: int = _PREVIEW_MAX_LEN) -> str:
    """Return a single-line preview of multi-line comments text.

    Takes the first line of the text and truncates it to ``max_len``
    characters, appending '…' if truncated.

    Args:
        text: The full comments text.
        max_len: Maximum number of characters to show before truncating.

    Returns:
        A single-line preview string.
    """
    first_line = text.split("\n")[0]
    if len(first_line) > max_len:
        return first_line[:max_len] + "…"
    return first_line


class AddGameScreen(ModalScreen[bool]):
    """A modal form for adding a new game to the list.

    Returns True if a game was saved, False if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialise the add game screen.

        Args:
            conn: An open database connection.
        """
        super().__init__()
        self._conn = conn
        self._full_comments: str = ""
        self._updating_preview: bool = False

    def compose(self) -> ComposeResult:
        """Build the form layout."""
        dev_names = get_developer_names(self._conn)
        platform_options = get_platforms(self._conn)

        with Vertical(id="add-game-form"):
            yield Label("Add Game", id="add-game-title")

            yield Label("Title")
            yield Input(placeholder="Game title", id="input-title")

            yield Label("Developer")
            yield Input(
                placeholder="Developer name",
                id="input-developer",
                suggester=SuggestFromList(dev_names, case_sensitive=False)
                if dev_names
                else None,
            )

            yield Label("Date Finished")
            yield Input(
                value=date.today().isoformat(),
                placeholder="yyyy-mm-dd",
                id="input-date-finished",
                restrict=r"[\d\-]*",
                max_length=10,
            )

            yield Label("Platform")
            yield Select[int](
                platform_options,
                id="select-platform",
                allow_blank=False,
            )

            yield Label("Comments")
            with Horizontal(id="comments-row"):
                yield Input(
                    placeholder="Optional comments",
                    id="input-comments",
                )
                yield Button("Expand", id="btn-expand-comments", variant="default")

            yield Label("", id="validation-error")

            yield Horizontal(
                Button("Save", id="btn-save", variant="primary"),
                Button("Cancel", id="btn-cancel"),
                id="add-game-buttons",
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Sync _full_comments when the user types directly in the comments Input.

        Skipped once after a programmatic preview update (after editor save) so
        that the full multi-line text is not overwritten by the truncated preview.
        The flag is consumed and cleared on the first event it suppresses.

        Args:
            event: The input changed event.
        """
        if event.input.id == "input-comments":
            if self._updating_preview:
                self._updating_preview = False
                return
            self._full_comments = event.value

    def _open_comments_editor(self) -> None:
        """Open the CommentsEditorScreen modal pre-populated with current text."""
        self.app.push_screen(
            CommentsEditorScreen(self._full_comments),
            callback=self._handle_editor_result,
        )

    def _handle_editor_result(self, text: str | None) -> None:
        """Apply the result from CommentsEditorScreen back to the form.

        Uses _updating_preview to suppress on_input_changed while setting
        the truncated preview so _full_comments is not overwritten.

        Args:
            text: The edited text, or None if the editor was cancelled.
        """
        if text is None:
            return
        self._full_comments = text
        preview = _comments_preview(text)
        self._updating_preview = True
        self.query_one("#input-comments", Input).value = preview

    def _validate_form(self) -> str | None:
        """Validate form fields and return an error message or None.

        Returns:
            An error string if validation fails, None if valid.
        """
        title = self.query_one("#input-title", Input).value.strip()
        if not title:
            return "Title cannot be empty."

        developer = self.query_one("#input-developer", Input).value.strip()
        if not developer:
            return "Developer cannot be empty."

        date_val = self.query_one("#input-date-finished", Input).value.strip()
        if not date_val:
            return "Date Finished cannot be empty."
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_val):
            return "Date Finished must be in yyyy-mm-dd format."

        platform_select = self.query_one("#select-platform", Select)
        if platform_select.is_blank():
            return "Platform cannot be empty."

        return None

    def _save_game(self) -> None:
        """Validate and save the game to the database."""
        error = self._validate_form()
        error_label = self.query_one("#validation-error", Label)
        if error:
            error_label.update(error)
            return

        error_label.update("")

        title = self.query_one("#input-title", Input).value.strip()
        developer_name = self.query_one("#input-developer", Input).value.strip()
        date_finished = self.query_one("#input-date-finished", Input).value.strip()
        platform_id = self.query_one("#select-platform", Select).value
        comments = self._full_comments.strip()

        developer_id = get_or_create_developer(self._conn, developer_name)
        insert_game(
            self._conn,
            title=title,
            developer_id=developer_id,
            date_finished=date_finished,
            platform_id=platform_id,
            comments=comments or None,
        )
        self._conn.commit()
        self.dismiss(True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses for Save, Cancel, and Expand.

        Args:
            event: The button pressed event.
        """
        if event.button.id == "btn-save":
            self._save_game()
        elif event.button.id == "btn-cancel":
            self.dismiss(False)
        elif event.button.id == "btn-expand-comments":
            self._open_comments_editor()

    def action_cancel(self) -> None:
        """Cancel and close the modal."""
        self.dismiss(False)
