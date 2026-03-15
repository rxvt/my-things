"""Tests for the games list screen."""

from pathlib import Path

import pytest
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView

from lib.screens.confirm import ConfirmDeleteScreen
from lib.screens.games import GamesScreen
from lib.screens.index import IndexScreen
from main import MyThingsApp

_MEMORY = Path(":memory:")


def _seed_games(app: MyThingsApp) -> None:
    """Insert test game entries into the database."""
    conn = app._conn
    assert conn is not None
    conn.execute(
        "INSERT INTO games (game, date_finished) VALUES (?, ?)",
        ("Hollow Knight", "2023-06-15"),
    )
    conn.execute(
        "INSERT INTO games (game, date_finished) VALUES (?, ?)",
        ("Elden Ring", "2024-01-20"),
    )
    conn.execute(
        "INSERT INTO games (game, date_finished) VALUES (?, ?)",
        ("Celeste", "2022-03-10"),
    )
    conn.commit()


@pytest.fixture
def app() -> MyThingsApp:
    """Return a MyThingsApp instance backed by an in-memory database."""
    return MyThingsApp(db_path=_MEMORY)


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


async def test_selecting_games_pushes_games_screen(app: MyThingsApp) -> None:
    """Selecting 'Games' from the index should push the GamesScreen."""
    async with app.run_test() as pilot:
        assert isinstance(pilot.app.screen, IndexScreen)
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)


async def test_escape_returns_to_index(app: MyThingsApp) -> None:
    """Pressing escape on the games screen should return to the index."""
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert isinstance(pilot.app.screen, IndexScreen)


# ---------------------------------------------------------------------------
# Games screen layout
# ---------------------------------------------------------------------------


async def test_games_screen_has_footer(app: MyThingsApp) -> None:
    """The games screen should render a Footer widget."""
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        footer = pilot.app.screen.query(Footer)
        assert len(footer) == 1


async def test_games_screen_has_list_view(app: MyThingsApp) -> None:
    """The games screen should render a ListView widget."""
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        list_view = pilot.app.screen.query(ListView)
        assert len(list_view) == 1


# ---------------------------------------------------------------------------
# Games data
# ---------------------------------------------------------------------------


async def test_games_ordered_by_date(app: MyThingsApp) -> None:
    """Games should be listed in ascending order by date_finished."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        labels = [item.query_one(Label).content for item in list_view.query(ListItem)]
        # Celeste (2022) < Hollow Knight (2023) < Elden Ring (2024)
        assert "Celeste" in labels[0]
        assert "Hollow Knight" in labels[1]
        assert "Elden Ring" in labels[2]


async def test_games_display_date_format(app: MyThingsApp) -> None:
    """Games should display dates in yyyy-mm-dd format."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        first_label = list_view.query(ListItem).first().query_one(Label)
        assert "2022-03-10" in first_label.content


async def test_games_first_item_highlighted(app: MyThingsApp) -> None:
    """The first game entry should be highlighted by default."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        assert list_view.index == 0


async def test_games_empty_list(app: MyThingsApp) -> None:
    """An empty games list should render with no items."""
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        items = list_view.query(ListItem)
        assert len(items) == 0


# ---------------------------------------------------------------------------
# Delete flow
# ---------------------------------------------------------------------------


async def test_delete_confirmation_appears(app: MyThingsApp) -> None:
    """Pressing 'd' should show the confirmation dialog."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        assert isinstance(pilot.app.screen, ConfirmDeleteScreen)


async def test_delete_confirmation_no_is_default(app: MyThingsApp) -> None:
    """The No button should be focused by default in the confirmation dialog."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        no_button = pilot.app.screen.query_one("#confirm-no", Button)
        assert no_button.has_focus


async def test_delete_cancel_keeps_entry(app: MyThingsApp) -> None:
    """Pressing No in the confirmation should keep the game entry."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        # Press enter on the focused No button
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        items = list_view.query(ListItem)
        assert len(items) == 3


async def test_delete_removes_entry(app: MyThingsApp) -> None:
    """Confirming Yes should delete the selected game."""
    async with app.run_test() as pilot:
        _seed_games(app)
        await pilot.press("enter")
        await pilot.pause()
        # First item (Celeste) is highlighted
        await pilot.press("d")
        await pilot.pause()
        # Tab to Yes button and press enter
        yes_button = pilot.app.screen.query_one("#confirm-yes", Button)
        yes_button.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(pilot.app.screen, GamesScreen)
        list_view = pilot.app.screen.query_one("#games-list", ListView)
        items = list_view.query(ListItem)
        assert len(items) == 2
        # Celeste should be gone
        labels = [item.query_one(Label).content for item in list_view.query(ListItem)]
        assert not any("Celeste" in label for label in labels)


async def test_delete_on_empty_list_does_nothing(app: MyThingsApp) -> None:
    """Pressing 'd' with no games should not show the confirmation dialog."""
    async with app.run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("d")
        await pilot.pause()
        # Should still be on the games screen, not the confirm dialog
        assert isinstance(pilot.app.screen, GamesScreen)
