"""TC-S001-F-003-01 — UI: ContextHierarchyDialog renders regulation URLs as
inert text (<span>) and contains no <a> anchor elements for URL values.

This test inspects the TSX source to verify the renderNode function does not
produce <a href=...> for URL-shaped values. It also confirms that the url field
is passed down from buildContextTree to the ContextNode structure.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
COMPONENT = REPO_ROOT / "src" / "components" / "workspace" / "ContextHierarchyDialog.tsx"


def test_render_node_has_no_anchor_for_urls():
    """renderNode must not emit <a href=...> elements."""
    source = COMPONENT.read_text(encoding="utf-8")

    # renderNode function body spans from "const renderNode" to the next top-level const/return
    # We extract the function body and check for <a href patterns
    render_node_match = re.search(
        r"const renderNode\s*=\s*\(.*?\) =>.*?\n  \};",
        source,
        re.DOTALL,
    )
    assert render_node_match, "renderNode function not found in ContextHierarchyDialog.tsx"
    render_node_body = render_node_match.group(0)

    assert '<a ' not in render_node_body, (
        "renderNode must not contain <a> elements — URLs must render as <span>"
    )
    assert 'href=' not in render_node_body, (
        "renderNode must not contain href attributes"
    )


def test_render_node_uses_span_for_url():
    """renderNode must render node.url as a <span> element."""
    source = COMPONENT.read_text(encoding="utf-8")

    render_node_match = re.search(
        r"const renderNode\s*=\s*\(.*?\) =>.*?\n  \};",
        source,
        re.DOTALL,
    )
    assert render_node_match, "renderNode function not found in ContextHierarchyDialog.tsx"
    render_node_body = render_node_match.group(0)

    assert 'node.url' in render_node_body, (
        "renderNode must reference node.url to display regulation URLs"
    )
    assert 'font-mono' in render_node_body, (
        "URL span must use font-mono class per acceptance criteria"
    )


def test_url_field_populated_in_build_context_tree():
    """buildContextTree must pass reg.url to the ContextNode url field."""
    source = COMPONENT.read_text(encoding="utf-8")

    assert 'url: reg.url' in source, (
        "buildContextTree must populate url: reg.url when building regulation nodes"
    )


def test_context_node_interface_has_url_field():
    """ContextNode interface must declare url as optional string."""
    source = COMPONENT.read_text(encoding="utf-8")

    assert 'url?: string' in source, (
        "ContextNode interface must declare url?: string"
    )
