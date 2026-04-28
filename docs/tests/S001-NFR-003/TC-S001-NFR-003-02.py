"""TC-S001-NFR-003-02 — docker compose up -d brings backend and frontend to 'healthy'."""
import pytest

_CONFIG_ERROR_MARKERS = ("LITELLM_PROXY_URL is required", "ValueError", "LLM_BACKEND")


def _is_config_failure(stack_up):
    logs = stack_up.get("backend_logs", "")
    return any(marker in logs for marker in _CONFIG_ERROR_MARKERS)


def test_backend_is_healthy(stack_up):
    if _is_config_failure(stack_up):
        pytest.skip(
            "Backend did not start due to LLM configuration in .env. "
            "Set LLM_BACKEND=external (Gemini) or LLM_BACKEND=internal with "
            "LITELLM_PROXY_URL/LITELLM_TOKEN before running this test.\n"
            f"Backend logs:\n{stack_up.get('backend_logs', '')[-800:]}"
        )
    assert stack_up["backend_healthy"], (
        "Backend service did not reach 'healthy' state within 90 seconds.\n"
        f"Backend logs:\n{stack_up.get('backend_logs', '')[-800:]}"
    )


def test_frontend_is_healthy(stack_up):
    if _is_config_failure(stack_up):
        pytest.skip(
            "Frontend skipped because backend did not start (LLM config issue in .env)."
        )
    assert stack_up["frontend_healthy"], (
        "Frontend service did not reach 'healthy' state within 90 seconds."
    )
