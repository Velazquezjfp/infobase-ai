"""Pytest configuration for S001-F-008 tests.

Per the slash-command convention, test files are named
``TC-{requirement-id}-{NN}.py`` rather than the default ``test_*.py`` pattern.
This file overrides ``python_files`` for the directory so pytest will collect
them when invoked as ``pytest docs/tests/S001-F-008/``.
"""


def pytest_collectstart(collector):
    pass


def pytest_configure(config):
    config.addinivalue_line("python_files", "TC-*.py")
