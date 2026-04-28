"""TC-S001-NFR-002-02 — running container serves Vite-built index.html.

Acceptance criterion: GET / returns 200 and the body contains `<div id="root">`.
"""

from __future__ import annotations

import urllib.request


def test_root_returns_html(running_container):
    _name, port = running_container
    with urllib.request.urlopen(f"http://localhost:{port}/", timeout=10) as resp:
        assert resp.status == 200
        body = resp.read().decode("utf-8", errors="replace")
    assert '<div id="root">' in body, f"Expected <div id=\"root\"> in response body; got: {body[:500]}"
