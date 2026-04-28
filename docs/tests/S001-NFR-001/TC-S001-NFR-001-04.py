"""TC-S001-NFR-001-04 — default user is non-root 'app'."""
import subprocess


def test_runs_as_app_user(built_image):
    result = subprocess.run(
        ["docker", "run", "--rm", built_image, "whoami"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "app"
