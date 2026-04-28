"""TC-S001-NFR-001-08 — HEALTHCHECK directive is present and references /health."""
import subprocess


def test_healthcheck_references_health_path(built_image):
    result = subprocess.run(
        ["docker", "inspect", built_image, "--format", "{{.Config.Healthcheck.Test}}"],
        capture_output=True,
        text=True,
        check=True,
    )
    healthcheck_test = result.stdout.strip()
    assert healthcheck_test, "No HEALTHCHECK directive found in image config"
    assert "/health" in healthcheck_test, (
        f"HEALTHCHECK does not reference /health: {healthcheck_test}"
    )
