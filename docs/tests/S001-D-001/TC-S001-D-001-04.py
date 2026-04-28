"""TC-S001-D-001-04: sectioning — exactly five `# Section:` headers, in order.

Spec: the file contains exactly the five `# Section:` headers in the
documented order; awk over `# Section:` lines returns them in order.
"""

from __future__ import annotations


# Documented order from the requirement Description (sections 1–5).
EXPECTED_SECTION_HEADERS: tuple[str, ...] = (
    "# Section: Registry & package sources",
    "# Section: LLM backend",
    "# Section: Feature flags for stubbed-out subsystems",
    "# Section: Session lifecycle",
    "# Section: Ports & paths",
)


def _section_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("# Section:")]


def test_exactly_five_section_headers(env_example_text: str) -> None:
    headers = _section_lines(env_example_text)
    assert len(headers) == 5, f"expected 5 `# Section:` lines, found {len(headers)}: {headers}"


def test_section_headers_match_documented_order(env_example_text: str) -> None:
    headers = _section_lines(env_example_text)
    assert headers == list(EXPECTED_SECTION_HEADERS), (
        f"section headers do not match documented order.\n"
        f"  expected: {EXPECTED_SECTION_HEADERS}\n"
        f"  got:      {headers}"
    )
