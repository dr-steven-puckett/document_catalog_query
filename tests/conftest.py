"""conftest.py — ensures CWD is the repo root for all tests.

The catalog_loader enforces path safety by rejecting absolute paths.
Tests that load catalog fixtures via relative paths require CWD to be the repo
root so that e.g. "tests/fixtures/catalog_small.json" resolves correctly.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def _chdir_repo_root():
    """Set CWD to repo root before each test; restore afterward."""
    old = os.getcwd()
    os.chdir(REPO_ROOT)
    yield
    os.chdir(old)
