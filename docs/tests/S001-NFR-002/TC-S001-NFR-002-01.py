"""TC-S001-NFR-002-01 — docker build exits 0.

Acceptance criterion: `docker build -t bamf-frontend:dev -f frontend/Dockerfile .`
exits 0 on a clean checkout.
"""

from __future__ import annotations


def test_build_exits_zero(built_image):
    # The session fixture asserts returncode == 0; reaching this line means the
    # build succeeded. We verify the tag is what we expect.
    assert built_image == "bamf-frontend:dev"
