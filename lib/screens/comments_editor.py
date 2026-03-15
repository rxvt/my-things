"""Comments editor modal screen — full-screen TextArea for multi-line markdown notes."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Label

from lib.widgets.text_area import ScrollingTextArea


class CommentsEditorScreen(ModalScreen[str | None]):
    """A modal TextArea editor for writing multi-line markdown comments.

    Returns the edited text string on save, or None if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("ctrl+s", "save", "Save"),
    ]

    def __init__(self, initial_text: str = "") -> None:
        """Initialise the comments editor.

        Args:
            initial_text: The existing comments text to pre-populate the editor.
        """
        super().__init__()
        self._initial_text = initial_text

    def compose(self) -> ComposeResult:
        """Build the editor layout."""
        with Vertical(id="comments-editor-form"):
            yield Label("Comments (Markdown)", id="comments-editor-title")
            yield ScrollingTextArea(
                self._initial_text,
                language="markdown",
                soft_wrap=True,
                show_line_numbers=False,
                id="comments-textarea",
            )
            yield Horizontal(
                Button("Save", id="btn-comments-save", variant="primary"),
                Button("Cancel", id="btn-comments-cancel"),
                id="comments-editor-buttons",
            )

    def action_save(self) -> None:
        """Save the current text and close the modal."""
        text = self.query_one("#comments-textarea", ScrollingTextArea).text
        self.dismiss(text)

    def action_cancel(self) -> None:
        """Discard changes and close the modal."""
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Save and Cancel button presses."""
        if event.button.id == "btn-comments-save":
            self.action_save()
        elif event.button.id == "btn-comments-cancel":
            self.action_cancel()
