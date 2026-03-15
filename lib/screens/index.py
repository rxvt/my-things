"""Index screen — displays the list of available lists."""

import sqlite3

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView


class IndexScreen(Screen):
    """Screen showing the index of all available lists."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        """Initialise the index screen.

        Args:
            conn: An open database connection.
        """
        super().__init__()
        self._conn = conn

    def compose(self) -> ComposeResult:
        """Create the layout with a ListView and Footer."""
        yield ListView(id="list-index")
        yield Footer()

    def on_mount(self) -> None:
        """Populate the ListView with list names from the database."""
        rows = self._conn.execute("SELECT name FROM list_index").fetchall()
        list_view = self.query_one("#list-index", ListView)
        for row in rows:
            list_view.append(ListItem(Label(row["name"])))
        list_view.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a list item."""
        from lib.screens.games import GamesScreen

        label = event.item.query_one(Label)
        if label.content == "Games":
            self.app.push_screen(GamesScreen(self._conn))
