"""My Things — a TUI app for managing personal lists."""

import sqlite3
from pathlib import Path

from textual.app import App

from lib.config import AppConfig
from lib.config import load_config
from lib.db import init_db
from lib.screens.index import IndexScreen


class MyThingsApp(App):
    """A Textual app that displays an index of available lists."""

    CSS_PATH = "main.tcss"

    def __init__(
        self,
        db_path: Path | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialise the app.

        Args:
            db_path: Optional database path override. Defaults to the XDG
                data directory. Pass ``Path(":memory:")`` in tests.
            config: Optional config override. Defaults to loading from the
                XDG config file. Pass an :class:`~lib.config.AppConfig`
                instance in tests to avoid touching the filesystem.
        """
        super().__init__()
        self._db_path = db_path
        self._config = config if config is not None else load_config()
        self._conn: sqlite3.Connection | None = None

    def on_mount(self) -> None:
        """Initialise the database, apply config, and push the index screen."""
        self.theme = self._config.theme
        self._conn = init_db(self._db_path)
        self.push_screen(IndexScreen(self._conn))

    def on_unmount(self) -> None:
        """Close the database connection on shutdown."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None


if __name__ == "__main__":
    MyThingsApp().run()
