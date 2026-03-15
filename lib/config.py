"""Application configuration loaded from a TOML file in the XDG config dir.

The config file lives at ``$XDG_CONFIG_HOME/my-things/config.toml``
(typically ``~/.config/my-things/config.toml``).  If the file does not exist
all settings fall back to their defaults.

Typical usage::

    from lib.config import load_config

    config = load_config()
    print(config.theme)
"""

import logging
import tomllib
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from xdg_base_dirs import xdg_config_home

logger = logging.getLogger(__name__)

_DEFAULT_THEME = "textual-dark"


def get_config_path() -> Path:
    """Return the path to the config file, creating parent dirs if needed.

    The config file is stored under the XDG config home directory:
    ``~/.config/my-things/config.toml``.

    Returns:
        A :class:`Path` pointing to the config file.
    """
    config_dir = xdg_config_home() / "my-things"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


@dataclass
class AppConfig:
    """Parsed application configuration.

    Attributes:
        theme: The Textual theme name to apply on startup.
    """

    theme: str = field(default=_DEFAULT_THEME)


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load and return the application configuration from a TOML file.

    Reads the config file at *config_path* (defaulting to the XDG config
    location).  If the file does not exist, returns an :class:`AppConfig`
    with all default values.  Unknown keys are silently ignored.

    Args:
        config_path: Optional path override for the config file. Defaults
            to the result of :func:`get_config_path`.

    Returns:
        An :class:`AppConfig` populated from the file, or all defaults if
        the file is absent.
    """
    path = config_path if config_path is not None else get_config_path()

    if not path.exists():
        logger.debug("Config file not found at %s, using defaults", path)
        return AppConfig()

    with path.open("rb") as f:
        data = tomllib.load(f)

    logger.debug("Loaded config from %s", path)
    return AppConfig(
        theme=data.get("theme", _DEFAULT_THEME),
    )
