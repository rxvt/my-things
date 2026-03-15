"""Confirmation dialog modal screen."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Label


class ConfirmDeleteScreen(ModalScreen[bool]):
    """A modal dialog asking the user to confirm a deletion.

    Returns True if confirmed, False if cancelled.
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(self, message: str = "Are you sure you want to delete?") -> None:
        """Initialise the confirmation dialog.

        Args:
            message: The confirmation message to display.
        """
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        """Create the dialog layout."""
        yield Label(self._message, id="confirm-message")
        yield Horizontal(
            Button("Yes", id="confirm-yes"),
            Button("No", id="confirm-no"),
            id="confirm-buttons",
        )

    def on_mount(self) -> None:
        """Focus the No button by default."""
        self.query_one("#confirm-no", Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        self.dismiss(event.button.id == "confirm-yes")

    def action_cancel(self) -> None:
        """Cancel the dialog."""
        self.dismiss(False)
