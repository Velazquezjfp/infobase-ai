"""TC-S001-NFR-003-06 — docker-compose.yml contains no hard-coded secret values."""
import pathlib
import re

COMPOSE_FILE = pathlib.Path(__file__).parents[3] / "docker-compose.yml"

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),   # Google API keys
    re.compile(r"sk-[A-Za-z0-9]{20,}"),        # OpenAI-style keys
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*"),  # Bearer tokens
]


def test_compose_file_exists():
    assert COMPOSE_FILE.exists(), f"{COMPOSE_FILE} does not exist"


def test_no_google_api_key(request):
    content = COMPOSE_FILE.read_text()
    matches = SECRET_PATTERNS[0].findall(content)
    assert not matches, f"Google API key pattern found in docker-compose.yml: {matches}"


def test_no_openai_style_key():
    content = COMPOSE_FILE.read_text()
    matches = SECRET_PATTERNS[1].findall(content)
    assert not matches, f"OpenAI-style key pattern found in docker-compose.yml: {matches}"


def test_no_bearer_tokens():
    content = COMPOSE_FILE.read_text()
    matches = SECRET_PATTERNS[2].findall(content)
    assert not matches, f"Bearer token found in docker-compose.yml: {matches}"
