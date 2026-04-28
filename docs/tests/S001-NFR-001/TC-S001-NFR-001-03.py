"""TC-S001-NFR-001-03 — no secret values baked into any image layer."""
import subprocess


def test_no_secrets_in_layers(built_image):
    result = subprocess.run(
        ["docker", "history", "--no-trunc", built_image],
        capture_output=True,
        text=True,
        check=True,
    )
    history = result.stdout
    assert "GEMINI_API_KEY=" not in history, "GEMINI_API_KEY baked into a layer"
    assert "LITELLM_TOKEN=" not in history, "LITELLM_TOKEN baked into a layer"
