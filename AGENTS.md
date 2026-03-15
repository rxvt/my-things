# Agent instructions for List App

## Development Commands

* Uses `uv` for package and dependency management
* Uses `Just` as the command runner

## Libraries

* Uses Textual for the TUI (https://textual.textualize.io/)

## Plans

* Plans are under `./plans`

## Specifications

* Specifications are under `./specs`
* Specifications should start in `draft`, move to `in-progress` and finish in `implemented`
* Specifications should only be moved to `implemented` _after_ confirmation by the user that
the feature has finished being implemented

## Code Style Guidelines

- **Python version**: 3.14+ minimum
- **Formatting**: ruff (88 char line length)
- **Linting**: ruff with Google docstring convention
- **Type hints**: Required, enforced by ty. Should generally be for function parameters and return types.
- **Imports**: stdlib → third-party → local, one per line
- **Naming**: snake_case functions/variables, PascalCase classes
- **Docstrings**: Google style for all public functions
- **Error handling**: Use custom exceptions from exceptions.py
- **Logging**: logging module with module-level loggers
