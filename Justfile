set quiet

# List available commands
default:
    just --list

# Run the test suite
test:
    uv run pytest tests/ -v
