"""Games screen — displays the list of finished games."""

import sqlite3

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView

from lib.screens.confirm import ConfirmDeleteScreen


class GamesScreen(Screen):
    """Screen showing the list of finished games."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("a", "add", "Add"),
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
    ]

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialise the games screen.

        Args:
            conn: An open database connection.
        """
        super().__init__()
        self._conn = conn

    def compose(self) -> ComposeResult:
        """Create the layout with a ListView and Footer."""
        yield ListView(id="games-list")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the ListView with games from the database."""
        self._refresh_list()

    def _refresh_list(self) -> None:
        """Reload game entries from the database into the ListView."""
        list_view = self.query_one("#games-list", ListView)
        list_view.clear()
        rows = self._conn.execute(
            "SELECT id, game, date_finished FROM games ORDER BY date_finished ASC"
        ).fetchall()
        for row in rows:
            item = ListItem(
                Label(f"{row['game']}  {row['date_finished']}"),
            )
            item.data = {"id": row["id"]}  # type: ignore[attr-defined]
            list_view.append(item)
        if rows:
            list_view.index = 0

    def action_go_back(self) -> None:
        """Return to the index screen."""
        self.app.pop_screen()

    def action_add(self) -> None:
        """Placeholder for adding a game entry."""

    def action_edit(self) -> None:
        """Placeholder for editing a game entry."""

    def action_delete(self) -> None:
        """Delete the currently selected game after confirmation."""
        list_view = self.query_one("#games-list", ListView)
        if list_view.highlighted_child is None:
            return
        self.app.push_screen(
            ConfirmDeleteScreen(),
            callback=self._handle_delete_confirm,
        )

    def _handle_delete_confirm(self, confirmed: bool | None) -> None:
        """Process the result of the delete confirmation dialog.

        Args:
            confirmed: True if the user confirmed the deletion.
        """
        if not confirmed:
            return
        list_view = self.query_one("#games-list", ListView)
        item = list_view.highlighted_child
        if item is None:
            return
        game_id = item.data["id"]  # type: ignore[attr-defined]
        self._conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
        self._conn.commit()
        self._refresh_list()
