"""Lister — a TUI app for managing personal lists."""

import sqlite3
from pathlib import Path

from textual.app import App
from textual.app import ComposeResult
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView

from lib.db import init_db


class ListerApp(App):
    """A Textual app that displays an index of available lists."""

    CSS_PATH = "main.tcss"

    def __init__(self, db_path: Path | None = None) -> None:
        """Initialise the app.

        Args:
            db_path: Optional database path override. Defaults to the XDG
                data directory. Pass ``Path(":memory:")`` in tests.
        """
        super().__init__()
        self._db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def compose(self) -> ComposeResult:
        """Create the initial layout with a ListView and Footer."""
        yield ListView(id="list-index")
        yield Footer()

    def on_mount(self) -> None:
        """Initialise the database and populate the ListView on mount."""
        self._conn = init_db(self._db_path)
        rows = self._conn.execute("SELECT name FROM list_index").fetchall()
        list_view = self.query_one("#list-index", ListView)
        for row in rows:
            list_view.append(ListItem(Label(row["name"])))
        list_view.index = 0

    def on_unmount(self) -> None:
        """Close the database connection on shutdown."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None


if __name__ == "__main__":
    ListerApp().run()
