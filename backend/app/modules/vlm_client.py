"""Unified VLM client supporting Anthropic direct *or* OpenRouter.

Backend selection is driven by ``Settings.vlm_backend``:

- ``"auto"``       — pick whichever credential is set (openrouter > anthropic)
- ``"anthropic"``  — force the Anthropic SDK
- ``"openrouter"`` — force the OpenAI-compatible OpenRouter endpoint

Both backends produce the same JSON-shaped output. The OpenRouter path
costs roughly +5% vs Anthropic direct but does not require a separate
console.anthropic.com account; the Anthropic path supports prompt
caching natively.

Model aliases (e.g., ``claude-sonnet-4-6``) are translated per backend
inside ``_resolve_model_id``.
"""
from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import get_settings

log = logging.getLogger(__name__)


class VLMClient:
    """Unified VLM interface across Anthropic and OpenRouter backends."""

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, model: str | None = None, *, backend: str | None = None) -> None:
        s = get_settings()
        self.model = model or s.primary_vlm
        self._cache_enabled = s.enable_prompt_caching
        self._kind = self._select_backend(s, backend)
        self._client = self._build_client(s)

    # ----- backend selection ----- #
    @staticmethod
    def _select_backend(s, requested: str | None) -> str:
        choice = (requested or s.vlm_backend or "auto").lower()
        if choice == "auto":
            if s.openrouter_api_key:
                return "openrouter"
            if s.anthropic_api_key:
                return "anthropic"
            raise RuntimeError(
                "No VLM credential found. Set OPENROUTER_API_KEY (preferred) "
                "or ANTHROPIC_API_KEY in .env."
            )
        if choice in {"anthropic", "openrouter"}:
            return choice
        raise ValueError(f"Unknown vlm_backend: {choice}")

    def _build_client(self, s):
        if self._kind == "anthropic":
            from anthropic import Anthropic
            if not s.anthropic_api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is empty for backend 'anthropic'.")
            return Anthropic(api_key=s.anthropic_api_key)
        if self._kind == "openrouter":
            from openai import OpenAI
            if not s.openrouter_api_key:
                raise RuntimeError("OPENROUTER_API_KEY is empty for backend 'openrouter'.")
            return OpenAI(
                base_url=self.OPENROUTER_BASE_URL,
                api_key=s.openrouter_api_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/[org]/os-pm",
                    "X-Title": "OS-PM Phase 1",
                },
            )
        raise RuntimeError(f"Unsupported backend: {self._kind}")

    # ----- public API ----- #
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def analyze_image(
        self,
        image_path: Path | str,
        system_prompt: str,
        user_prompt: str,
        cache_system: bool = True,
    ) -> dict[str, Any]:
        """Send an image + prompt to the VLM, return parsed JSON answer."""
        image_b64 = base64.standard_b64encode(Path(image_path).read_bytes()).decode("utf-8")
        media_type = self._media_type(Path(image_path).suffix)

        if self._kind == "anthropic":
            return self._analyze_image_anthropic(
                image_b64, media_type, system_prompt, user_prompt, cache_system
            )
        return self._analyze_image_openrouter(
            image_b64, media_type, system_prompt, user_prompt
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def analyze_text(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if self._kind == "anthropic":
            return self._analyze_text_anthropic(system_prompt, user_prompt)
        return self._analyze_text_openrouter(system_prompt, user_prompt)

    # ----- Anthropic-direct path ----- #
    def _analyze_image_anthropic(
        self,
        image_b64: str,
        media_type: str,
        system_prompt: str,
        user_prompt: str,
        cache_system: bool,
    ) -> dict[str, Any]:
        system_blocks: list[dict[str, Any]] = [{"type": "text", "text": system_prompt}]
        if cache_system and self._cache_enabled:
            system_blocks[0]["cache_control"] = {"type": "ephemeral"}

        msg = self._client.messages.create(
            model=self._resolve_model_id(),
            max_tokens=2048,
            system=system_blocks,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": user_prompt},
                    ],
                }
            ],
        )
        text = msg.content[0].text if msg.content else ""
        return self._extract_json(text)

    def _analyze_text_anthropic(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        msg = self._client.messages.create(
            model=self._resolve_model_id(),
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = msg.content[0].text if msg.content else ""
        return self._extract_json(text)

    # ----- OpenRouter path (OpenAI-compatible) ----- #
    def _analyze_image_openrouter(
        self,
        image_b64: str,
        media_type: str,
        system_prompt: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        # OpenRouter passes through Claude-style image messages encoded as the
        # OpenAI 'image_url' content type with a base64 data URI.
        resp = self._client.chat.completions.create(
            model=self._resolve_model_id(),
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_b64}",
                            },
                        },
                    ],
                },
            ],
        )
        text = resp.choices[0].message.content or ""
        return self._extract_json(text)

    def _analyze_text_openrouter(
        self, system_prompt: str, user_prompt: str
    ) -> dict[str, Any]:
        resp = self._client.chat.completions.create(
            model=self._resolve_model_id(),
            max_tokens=2048,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = resp.choices[0].message.content or ""
        return self._extract_json(text)

    # ----- helpers ----- #
    @staticmethod
    def _media_type(suffix: str) -> str:
        m = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".webp": "image/webp", ".gif": "image/gif"}
        return m.get(suffix.lower(), "image/jpeg")

    def _resolve_model_id(self) -> str:
        """Translate the project's model alias to the backend-specific id."""
        if self._kind == "anthropic":
            aliases = {
                "claude-sonnet-4-6": "claude-sonnet-4-6",
                "claude-opus-4-7":   "claude-opus-4-7",
                "claude-haiku-4-5":  "claude-haiku-4-5-20251001",
            }
            return aliases.get(self.model, self.model)
        if self._kind == "openrouter":
            # OpenRouter uses provider-prefixed ids. We map our aliases to the
            # most current Claude generation OpenRouter exposes; if the alias
            # already contains "/", we honour it verbatim.
            if "/" in self.model:
                return self.model
            aliases = {
                "claude-sonnet-4-6": "anthropic/claude-sonnet-4.6",
                "claude-sonnet-4-7": "anthropic/claude-sonnet-4.7",
                "claude-opus-4-7":   "anthropic/claude-opus-4.7",
                "claude-haiku-4-5":  "anthropic/claude-haiku-4.5",
            }
            return aliases.get(self.model, f"anthropic/{self.model}")
        return self.model

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        """Robust JSON extraction — handles markdown fences."""
        candidates = []
        if "```json" in text:
            candidates.append(text.split("```json", 1)[1].split("```", 1)[0])
        if "```" in text and not candidates:
            candidates.append(text.split("```", 1)[1].split("```", 1)[0])
        candidates.append(text)
        for c in candidates:
            try:
                return json.loads(c.strip())
            except json.JSONDecodeError:
                continue
        log.warning("Could not parse JSON from VLM response; returning raw")
        return {"raw_text": text, "parse_error": True}
