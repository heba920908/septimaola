---
alwaysApply: false
globs: "automation/**/*.py"
---

# Automation Test Runner

When working on any Python file under `automation/`, always run tests via `uv run` — never with a bare `python -m pytest` call, as that would bypass the `uv`-managed virtual environment and could pick up the wrong interpreter or miss installed dependencies.

## Required command form

```bash
# Run all automation tests
cd automation
uv run pytest

# Run a specific test file verbosely
uv run pytest tests/test_message_generator.py -v

# Run a single test by node ID
uv run pytest tests/test_ai_factory.py::TestCreateProvider::test_factory_returns_deepseek_by_default -v

# Run with coverage (if pytest-cov is added to dev deps)
uv run pytest --cov=septima_automation tests/
```

## Never use

```bash
# These bypass the uv venv — do not use
pytest tests/
python -m pytest tests/
```

## Why

The `automation/` package uses `uv` for dependency and environment management (`pyproject.toml` + `uv.lock`). The active interpreter and all packages (including `pytest`, `pytest-asyncio`, `httpx`, etc.) live inside the `.venv` managed by `uv`. Invoking `pytest` directly will fail or use a mismatched environment unless the venv is explicitly activated.

## Async tests

Tests using `pytest.mark.asyncio` require `pytest-asyncio` (already in `[dependency-groups].dev`). No extra configuration is needed — the marker is sufficient.
