"""TC-S001-NFR-003-08 — depends_on condition is declared as service_healthy in compose config."""
import pathlib
import yaml

COMPOSE_FILE = pathlib.Path(__file__).parents[3] / "docker-compose.yml"


def _load_compose():
    try:
        import yaml  # noqa: F401
        return yaml.safe_load(COMPOSE_FILE.read_text())
    except ImportError:
        return None


def test_frontend_depends_on_backend_with_service_healthy():
    compose = _load_compose()
    if compose is None:
        # Fallback: grep the raw file when PyYAML is not installed
        content = COMPOSE_FILE.read_text()
        assert "service_healthy" in content, (
            "docker-compose.yml does not declare 'service_healthy' condition. "
            "Install PyYAML for a structured check."
        )
        return

    frontend = compose.get("services", {}).get("frontend", {})
    depends_on = frontend.get("depends_on", {})

    assert "backend" in depends_on, (
        "frontend.depends_on does not reference 'backend'."
    )

    backend_dep = depends_on["backend"]
    assert isinstance(backend_dep, dict), (
        "frontend.depends_on.backend should be a dict with a 'condition' key."
    )
    assert backend_dep.get("condition") == "service_healthy", (
        f"Expected condition 'service_healthy', got {backend_dep.get('condition')!r}."
    )
