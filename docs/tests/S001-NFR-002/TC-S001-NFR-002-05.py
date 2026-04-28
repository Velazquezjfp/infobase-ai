"""TC-S001-NFR-002-05 — runtime image contains no source files or node_modules.

Acceptance criterion: `find /app -name '*.tsx' -o -name 'node_modules'` returns nothing.
"""

from __future__ import annotations

import subprocess


def test_no_source_in_runtime(built_image):
    result = subprocess.run(
        [
            "docker", "run", "--rm", built_image,
            "sh", "-c", "find /app -name '*.tsx' -o -name 'node_modules' 2>/dev/null",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker run failed:\n{result.stderr}"
    output = result.stdout.strip()
    assert output == "", (
        f"Found unexpected source files or node_modules in runtime image:\n{output}"
    )
