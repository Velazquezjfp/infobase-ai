"""TC-S001-NFR-003-01 — docker compose config exits 0 and contains expected services."""
import pathlib

from conftest import _compose, COMPOSE_AVAILABLE
import pytest

COMPOSE_FILE = pathlib.Path(__file__).parents[3] / "docker-compose.yml"


def test_compose_config_exits_zero(compose_config):
    assert compose_config.returncode == 0, (
        f"docker compose config exited {compose_config.returncode}.\n"
        f"stderr:\n{compose_config.stderr[-1000:]}"
    )


def test_compose_config_has_backend(compose_config):
    assert "backend" in compose_config.stdout, (
        "Normalized config does not mention 'backend' service."
    )


def test_compose_config_has_frontend(compose_config):
    assert "frontend" in compose_config.stdout, (
        "Normalized config does not mention 'frontend' service."
    )


def test_compose_file_declares_version_39():
    # docker compose config normalizes and drops the `version` field (it is
    # treated as obsolete by Compose v2.x). Check the source file directly.
    content = COMPOSE_FILE.read_text()
    assert 'version: "3.9"' in content or "version: '3.9'" in content, (
        "docker-compose.yml does not declare version: \"3.9\"."
    )
