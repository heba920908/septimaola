"""Pytest configuration and fixtures."""

from pathlib import Path

import pytest
from dotenv import load_dotenv


# Load environment variables from .env file.
# override=True ensures automation/.env is authoritative even when the shell
# already exports same-named variables (e.g. CODEMIE_BASE_URL) from an
# unrelated tool such as a coding-agent CLI session.
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)


# Configure pytest-asyncio mode
pytest_plugins = ["pytest_asyncio"]


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Run live integration tests against real LLM providers",
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "live: mark test as requiring live LLM access (run with --live)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip live tests unless --live flag is provided."""
    if not config.getoption("--live"):
        skip_live = pytest.mark.skip(
            reason="Need --live flag to run live integration tests"
        )
        for item in items:
            if "live" in item.keywords:
                item.add_marker(skip_live)
