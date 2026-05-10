"""Centralised configuration via pydantic-settings."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- VLM credentials (any one of these unlocks Phase 2 VLM mode) ---
    anthropic_api_key: str = ""        # console.anthropic.com direct
    openrouter_api_key: str = ""       # openrouter.ai (recommended path)
    openai_api_key: str = ""           # for cross-provider tests

    # --- VLM backend selection ---
    # "auto"        — pick whichever credential is set (openrouter > anthropic)
    # "anthropic"   — force the Anthropic SDK
    # "openrouter"  — force the OpenAI-compatible OpenRouter endpoint
    vlm_backend: str = "auto"

    primary_vlm: str = "claude-sonnet-4-6"
    secondary_vlm: str = "qwen2.5-vl-72b"

    sentinel_stac_url: str = "https://earth-search.aws.element84.com/v1"
    planetary_computer_key: str = ""

    openalex_email: str = ""
    semantic_scholar_api_key: str = ""

    qdrant_url: str = "http://localhost:6333"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme"

    data_dir: Path = Path("./data")
    cog_dir: Path = Path("./data/cogs")
    cache_dir: Path = Path("./data/cache")
    pm_schema_dir: Path = Path("./pm_schema")

    log_level: str = "INFO"
    enable_prompt_caching: bool = True


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    for d in (s.data_dir, s.cog_dir, s.cache_dir):
        d.mkdir(parents=True, exist_ok=True)
    return s
