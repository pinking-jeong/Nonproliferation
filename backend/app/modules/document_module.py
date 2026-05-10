"""Module B — Document Mining (literature + trade)."""
from __future__ import annotations

import logging
from typing import Iterable

import httpx

from ..config import get_settings
from ..schemas.indicator import Indicator, Modality, Strength
from . import prompts
from .vlm_client import VLMClient

log = logging.getLogger(__name__)

NUCLEAR_TOPIC_KEYWORDS = [
    "uranium enrichment",
    "centrifuge",
    "reprocessing",
    "plutonium",
    "nuclear fuel cycle",
    "heavy water",
    "fast reactor",
    "hot cell",
    "actinide separation",
]


class DocumentMiningModule:
    def __init__(self, vlm: VLMClient | None = None):
        self.vlm = vlm or VLMClient()
        self.s = get_settings()

    def search_openalex(
        self,
        country_code: str,
        year_range: tuple[int, int],
        per_page: int = 25,
    ) -> Iterable[dict]:
        """Yield works from OpenAlex matching country + nuclear topics."""
        kw = " OR ".join(f'"{k}"' for k in NUCLEAR_TOPIC_KEYWORDS)
        params = {
            "search": kw,
            "filter": (
                f"institutions.country_code:{country_code},"
                f"publication_year:{year_range[0]}-{year_range[1]}"
            ),
            "per-page": per_page,
            "select": "id,title,abstract_inverted_index,authorships,publication_year,doi",
        }
        if self.s.openalex_email:
            params["mailto"] = self.s.openalex_email

        with httpx.Client(timeout=30.0) as client:
            r = client.get("https://api.openalex.org/works", params=params)
            r.raise_for_status()
            for w in r.json().get("results", []):
                yield w

    @staticmethod
    def _abstract_from_inverted(idx: dict | None) -> str:
        if not idx:
            return ""
        # OpenAlex returns {word: [positions]}
        positions: list[tuple[int, str]] = []
        for word, locs in idx.items():
            for loc in locs:
                positions.append((loc, word))
        positions.sort()
        return " ".join(w for _, w in positions)

    def classify_paper(self, work: dict) -> Indicator | None:
        abstract = self._abstract_from_inverted(work.get("abstract_inverted_index"))
        if not abstract and not work.get("title"):
            return None
        user = (
            f"Title: {work.get('title','')}\n"
            f"Abstract: {abstract[:2000]}\n"
            f"Year: {work.get('publication_year','')}\n"
            f"Authors: {[a['author']['display_name'] for a in work.get('authorships',[])[:5]]}\n"
            f"Affiliations: {[(i.get('display_name'), i.get('country_code')) for a in work.get('authorships',[])[:5] for i in a.get('institutions',[])][:5]}\n"
            "Classify per the system prompt. JSON only."
        )
        result = self.vlm.analyze_text(prompts.RD_EXTRACT_SYSTEM, user)
        if not result.get("relevant_processes"):
            return None
        return Indicator(
            cell_id=self._infer_cell_id(result.get("relevant_processes", [])),
            process=(result.get("relevant_processes") or ["unknown"])[0],
            modality=Modality.TEXT,
            strength=Strength(result.get("strength", "weak")),
            confidence=0.6,
            evidence={
                "title": work.get("title"),
                "doi": work.get("doi"),
                "key_phrases": result.get("key_phrases", []),
                "justification": result.get("justification", ""),
            },
            source_uri=work.get("doi") or work.get("id"),
        )

    @staticmethod
    def _infer_cell_id(processes: list[str]) -> str:
        # naive mapping; refine with PM schema lookup in production
        for p in processes:
            p_lower = p.lower()
            if "centrifuge" in p_lower or "enrichment" in p_lower:
                return "V03_E05"
            if "reprocess" in p_lower:
                return "V07_E05"
            if "reactor" in p_lower:
                return "V05_E05"
        return "V09_E05"  # R&D fallback
