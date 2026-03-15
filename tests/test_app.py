"""Tests for the My Things Textual app — index screen."""

from pathlib import Path

import pytest
from textual.widgets import Footer
from textual.widgets import Label
from textual.widgets import ListItem
from textual.widgets import ListView

from main import MyThingsApp

_MEMORY = Path(":memory:")


@pytest.fixture
def app() -> MyThingsApp:
    """Return a MyThingsApp instance backed by an in-memory database."""
    return MyThingsApp(db_path=_MEMORY)


async def test_app_has_footer(app: MyThingsApp) -> None:
    """The app should render a Footer widget."""
    async with app.run_test() as pilot:
        footer = pilot.app.screen.query(Footer)
        assert len(footer) == 1


async def test_app_has_list_view(app: MyThingsApp) -> None:
    """The app should render a ListView widget."""
    async with app.run_test() as pilot:
        list_view = pilot.app.screen.query(ListView)
        assert len(list_view) == 1


async def test_list_view_contains_games(app: MyThingsApp) -> None:
    """The ListView should contain a 'Games' item from the seeded list_index."""
    async with app.run_test() as pilot:
        list_view = pilot.app.screen.query_one(ListView)
        labels = [item.query_one(Label).content for item in list_view.query(ListItem)]
        assert "Games" in labels


async def test_list_view_item_count(app: MyThingsApp) -> None:
    """The ListView should have exactly one item (the seeded 'Games' entry)."""
    async with app.run_test() as pilot:
        list_view = pilot.app.screen.query_one(ListView)
        items = list_view.query(ListItem)
        assert len(items) == 1


async def test_first_item_is_highlighted(app: MyThingsApp) -> None:
    """The first item in the ListView should be highlighted on mount."""
    async with app.run_test() as pilot:
        list_view = pilot.app.screen.query_one(ListView)
        assert list_view.index == 0
