"""Tests for the dual-backend VLMClient — exercises selection logic without
real network calls.
"""
import pytest

from backend.app.modules.vlm_client import VLMClient


def _settings(monkeypatch, **overrides):
    """Build a fresh Settings with the given fields overridden via env."""
    from backend.app.config import Settings, get_settings

    # Map field name → env var; pydantic-settings reads env case-insensitively
    keys = ("anthropic_api_key", "openrouter_api_key", "vlm_backend",
            "primary_vlm", "enable_prompt_caching")
    for k in keys:
        monkeypatch.delenv(k.upper(), raising=False)
    for k, v in overrides.items():
        monkeypatch.setenv(k.upper(), str(v))

    # Bypass pydantic-settings env parsing on Windows by injecting via init args
    # — the simpler path: clear the lru_cache and let pydantic re-read the env.
    get_settings.cache_clear()
    return get_settings()


def test_select_backend_auto_prefers_openrouter(monkeypatch):
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  anthropic_api_key="sk-ant-test",
                  vlm_backend="auto")
    assert VLMClient._select_backend(s, None) == "openrouter"


def test_select_backend_auto_falls_back_to_anthropic(monkeypatch):
    s = _settings(monkeypatch,
                  openrouter_api_key="",
                  anthropic_api_key="sk-ant-test",
                  vlm_backend="auto")
    assert VLMClient._select_backend(s, None) == "anthropic"


def test_select_backend_auto_no_keys_raises(monkeypatch):
    s = _settings(monkeypatch,
                  openrouter_api_key="",
                  anthropic_api_key="",
                  vlm_backend="auto")
    with pytest.raises(RuntimeError, match="No VLM credential"):
        VLMClient._select_backend(s, None)


def test_select_backend_explicit_overrides_auto(monkeypatch):
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  anthropic_api_key="sk-ant-test",
                  vlm_backend="anthropic")
    assert VLMClient._select_backend(s, None) == "anthropic"
    assert VLMClient._select_backend(s, "openrouter") == "openrouter"


def test_select_backend_unknown_choice_raises(monkeypatch):
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  vlm_backend="auto")
    with pytest.raises(ValueError, match="Unknown vlm_backend"):
        VLMClient._select_backend(s, "nonsense")


def test_resolve_model_id_anthropic_alias(monkeypatch):
    """The Anthropic alias map should translate user-facing names."""
    s = _settings(monkeypatch,
                  anthropic_api_key="sk-ant-test",
                  vlm_backend="anthropic")
    c = VLMClient(model="claude-sonnet-4-6", backend="anthropic")
    assert c._resolve_model_id() == "claude-sonnet-4-6"
    c2 = VLMClient(model="claude-haiku-4-5", backend="anthropic")
    assert c2._resolve_model_id() == "claude-haiku-4-5-20251001"


def test_resolve_model_id_openrouter_prefix(monkeypatch):
    """OpenRouter ids carry an ``anthropic/...`` provider prefix."""
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  vlm_backend="openrouter")
    c = VLMClient(model="claude-sonnet-4-6", backend="openrouter")
    assert c._resolve_model_id() == "anthropic/claude-sonnet-4.6"


def test_resolve_model_id_openrouter_already_prefixed(monkeypatch):
    """Caller-supplied prefixed ids are passed through verbatim."""
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  vlm_backend="openrouter")
    c = VLMClient(model="anthropic/claude-opus-4.7", backend="openrouter")
    assert c._resolve_model_id() == "anthropic/claude-opus-4.7"


def test_init_openrouter_builds_openai_client(monkeypatch):
    """When OPENROUTER key is set, the SDK initialises without error."""
    s = _settings(monkeypatch,
                  openrouter_api_key="sk-or-test",
                  vlm_backend="openrouter")
    c = VLMClient(model="claude-sonnet-4-6", backend="openrouter")
    assert c._kind == "openrouter"
    # Confirm the base_url was set
    assert "openrouter.ai" in str(c._client.base_url)


def test_extract_json_handles_markdown_fences():
    text = '```json\n{"hello": "world", "n": 3}\n```\nextra text'
    assert VLMClient._extract_json(text) == {"hello": "world", "n": 3}


def test_extract_json_falls_back_to_raw_text():
    bogus = "not json at all"
    out = VLMClient._extract_json(bogus)
    assert out["parse_error"] is True
    assert out["raw_text"] == bogus
