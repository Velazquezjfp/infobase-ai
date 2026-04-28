"""Pytest configuration for S001-F-003 tests.

Per the slash-command convention, test files are named
``TC-{requirement-id}-{NN}.py`` rather than the default ``test_*.py`` pattern.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `backend.*` importable regardless of where pytest is invoked from.
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")
