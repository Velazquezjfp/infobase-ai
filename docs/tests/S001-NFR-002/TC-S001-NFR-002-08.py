"""TC-S001-NFR-002-08 — runtime process runs as non-root user 'app'.

Acceptance criterion: `docker run --rm bamf-frontend:dev whoami` outputs `app`.
"""

from __future__ import annotations

import subprocess


def test_runtime_user_is_app(built_image):
    result = subprocess.run(
        ["docker", "run", "--rm", built_image, "whoami"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker run failed:\n{result.stderr}"
    assert result.stdout.strip() == "app", (
        f"Expected runtime user 'app', got '{result.stdout.strip()}'"
    )
