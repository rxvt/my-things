"""Tests for lib/config.py — TOML configuration loading."""

from pathlib import Path

import pytest

from lib.config import AppConfig
from lib.config import load_config


# ---------------------------------------------------------------------------
# AppConfig defaults
# ---------------------------------------------------------------------------


def test_app_config_default_theme() -> None:
    """AppConfig should default to the textual-dark theme."""
    config = AppConfig()
    assert config.theme == "textual-dark"


# ---------------------------------------------------------------------------
# load_config — missing file
# ---------------------------------------------------------------------------


def test_load_config_missing_file_returns_defaults(tmp_path: Path) -> None:
    """load_config returns defaults when the config file does not exist."""
    config = load_config(config_path=tmp_path / "nonexistent.toml")
    assert config.theme == "textual-dark"


# ---------------------------------------------------------------------------
# load_config — valid TOML
# ---------------------------------------------------------------------------


def test_load_config_reads_theme(tmp_path: Path) -> None:
    """load_config reads the theme value from the TOML file."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('theme = "catppuccin-macchiato"\n')
    config = load_config(config_path=config_file)
    assert config.theme == "catppuccin-macchiato"


def test_load_config_missing_theme_key_uses_default(tmp_path: Path) -> None:
    """load_config falls back to the default theme when the key is absent."""
    config_file = tmp_path / "config.toml"
    config_file.write_text("# no theme key\n")
    config = load_config(config_path=config_file)
    assert config.theme == "textual-dark"


def test_load_config_ignores_unknown_keys(tmp_path: Path) -> None:
    """load_config silently ignores unrecognised keys in the file."""
    config_file = tmp_path / "config.toml"
    config_file.write_text('theme = "catppuccin-macchiato"\nunknown_key = "whatever"\n')
    config = load_config(config_path=config_file)
    assert config.theme == "catppuccin-macchiato"


# ---------------------------------------------------------------------------
# load_config — applied to app
# ---------------------------------------------------------------------------


async def test_app_uses_theme_from_config() -> None:
    """MyThingsApp should apply the theme from the config on mount."""
    from main import MyThingsApp

    app = MyThingsApp(
        db_path=Path(":memory:"),
        config=AppConfig(theme="catppuccin-macchiato"),
    )
    async with app.run_test():
        assert app.theme == "catppuccin-macchiato"


def test_app_defaults_to_textual_dark_without_config_file(tmp_path: Path) -> None:
    """MyThingsApp uses textual-dark when no config file exists."""
    config = load_config(config_path=tmp_path / "nonexistent.toml")
    assert config.theme == "textual-dark"
