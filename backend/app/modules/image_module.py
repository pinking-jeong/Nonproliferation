"""Module A — Image Understanding."""
from __future__ import annotations

import logging
from pathlib import Path

from ..schemas.indicator import Indicator, Modality, Strength
from . import prompts
from .vlm_client import VLMClient

log = logging.getLogger(__name__)


class ImageUnderstandingModule:
    def __init__(self, vlm: VLMClient | None = None):
        self.vlm = vlm or VLMClient()

    def coarse_detect(self, image_path: Path, geo_ctx: dict | None = None) -> dict:
        user = (
            f"Geographic context: {geo_ctx or {}}. "
            "Identify the primary facility type. Output JSON only."
        )
        return self.vlm.analyze_image(
            image_path,
            system_prompt=prompts.FACILITY_DETECTION_SYSTEM,
            user_prompt=user,
        )

    def extract_elements(
        self, image_path: Path, candidate_cells: list[dict], geo_ctx: dict | None = None
    ) -> dict:
        user = (
            f"Candidate PM cells (RAG context): {candidate_cells}\n"
            f"Geographic context: {geo_ctx or {}}.\n"
            "Match observed visual features to these cells. Output JSON only."
        )
        return self.vlm.analyze_image(
            image_path,
            system_prompt=prompts.ELEMENT_EXTRACTION_SYSTEM,
            user_prompt=user,
        )

    def to_indicators(self, raw: dict, source_uri: str) -> list[Indicator]:
        out: list[Indicator] = []
        for el in raw.get("observed_elements", []):
            try:
                out.append(
                    Indicator(
                        cell_id=el["cell_id"],
                        process=el.get("process", ""),
                        modality=Modality.IMAGE,
                        strength=Strength(el.get("strength", "weak")),
                        confidence=float(el.get("confidence", 0.5)),
                        evidence={"visual": el.get("evidence", [])},
                        source_uri=source_uri,
                        extracted_by="vlm",
                    )
                )
            except Exception as e:  # noqa: BLE001
                log.warning("Skipping malformed element %s: %s", el, e)
        return out
