"""TC-S001-NFR-002-04 — final image size is under 200 MiB.

Acceptance criterion: `docker images bamf-frontend:dev --format '{{.Size}}'`
reports a value that parses to < 200 MiB.
"""

from __future__ import annotations

import subprocess


def _parse_mib(size_str: str) -> float:
    """Parse a Docker size string like '182MB' or '1.23GB' into MiB."""
    s = size_str.strip()
    if s.endswith("GB"):
        return float(s[:-2]) * 1024
    if s.endswith("MB"):
        return float(s[:-2])
    if s.endswith("kB") or s.endswith("KB"):
        return float(s[:-2]) / 1024
    if s.endswith("B"):
        return float(s[:-1]) / (1024 * 1024)
    raise ValueError(f"Unknown size unit: {s!r}")


def test_image_size_under_200_mib(built_image):
    result = subprocess.run(
        ["docker", "images", built_image, "--format", "{{.Size}}"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    size_str = result.stdout.strip()
    assert size_str, "docker images returned no output — image may not exist"

    size_mib = _parse_mib(size_str)
    assert size_mib < 200, f"Image size {size_str} ({size_mib:.1f} MiB) exceeds 200 MiB limit"
