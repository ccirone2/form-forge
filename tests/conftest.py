"""Shared test fixtures for FormForge."""

import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = PROJECT_ROOT / "index.html"
SPEC_PATH = PROJECT_ROOT / "schemas" / "_schema.spec.json"


@pytest.fixture(scope="session")
def index_html() -> str:
    """Read index.html once per test session."""
    return INDEX_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def spec() -> dict:
    """Load _schema.spec.json once per test session."""
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))
