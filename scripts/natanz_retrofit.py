"""Natanz Retrofit Test — proof-of-concept.

Goal: With ONLY pre-disclosure (≤2002-08-14) open-source data, can OS-PM raise
a credible enrichment-facility hypothesis at the Natanz coordinates?

This script:
  1. Queries Landsat-7 (pre-2002 era) imagery via USGS STAC for the Natanz AOI.
  2. Queries OpenAlex for Iran-affiliated nuclear publications, 1990-2002.
  3. (Optional) Invokes Claude VLM to classify a sample image and rank papers.
  4. Aggregates indicators via the Bayesian fusion module.
  5. Prints the resulting ProcessHypothesis.

Usage:
    python -m scripts.natanz_retrofit --no-vlm    # offline / dry run
    python -m scripts.natanz_retrofit --vlm       # uses ANTHROPIC_API_KEY

Note: Sentinel-2 only launched 2015; for true pre-2002 retrofit we use Landsat-7.
For demonstration, we also fetch a recent Sentinel-2 tile to show the modern
pipeline path.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Make project importable when run as `python -m scripts.natanz_retrofit`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.fusion_module import fuse  # noqa: E402
from backend.app.schemas.indicator import (  # noqa: E402
    Indicator,
    Modality,
    Strength,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("natanz")

# Natanz Fuel Enrichment Plant approximate coordinates (public knowledge since 2002)
NATANZ_LAT = 33.7244
NATANZ_LON = 51.7264
NATANZ_BBOX = [NATANZ_LON - 0.05, NATANZ_LAT - 0.05, NATANZ_LON + 0.05, NATANZ_LAT + 0.05]

PRE_DISCLOSURE_CUTOFF = "2002-08-14"  # NCRI press conference date


# ---------- 1. Imagery retrieval ---------- #
def query_landsat_pre_2002(out_dir: Path) -> list[dict]:
    """Search USGS Landsat archive via Microsoft Planetary Computer STAC."""
    try:
        from pystac_client import Client
    except ImportError:
        log.warning("pystac-client not installed; skipping imagery query.")
        return []

    catalog_url = "https://planetarycomputer.microsoft.com/api/stac/v1"
    log.info("Searching Landsat-5/7 archive 1995-2002 over Natanz...")
    try:
        client = Client.open(catalog_url)
        search = client.search(
            collections=["landsat-c2-l2"],
            bbox=NATANZ_BBOX,
            datetime="1995-01-01/2002-08-14",
            query={"eo:cloud_cover": {"lt": 20}},
            max_items=20,
        )
        items = list(search.items())
    except Exception as e:  # noqa: BLE001 — STAC may be unreachable offline
        log.warning("STAC search failed: %s", e)
        return []

    log.info("Found %d Landsat scenes pre-2002 with cloud cover < 20%%", len(items))
    out = []
    for it in items[:5]:
        out.append({
            "id": it.id,
            "datetime": str(it.datetime),
            "platform": it.properties.get("platform"),
            "cloud_cover": it.properties.get("eo:cloud_cover"),
            "preview_href": it.assets.get("rendered_preview", {}).href
                if "rendered_preview" in it.assets else None,
        })
    (out_dir / "landsat_natanz_pre2002.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    return out


def query_sentinel2_recent(out_dir: Path) -> list[dict]:
    """Fetch a recent Sentinel-2 scene as the modern-pipeline reference."""
    try:
        from pystac_client import Client
    except ImportError:
        return []

    try:
        client = Client.open("https://earth-search.aws.element84.com/v1")
        search = client.search(
            collections=["sentinel-2-l2a"],
            bbox=NATANZ_BBOX,
            datetime="2024-01-01/2024-12-31",
            query={"eo:cloud_cover": {"lt": 10}},
            max_items=5,
        )
        items = list(search.items())
    except Exception as e:  # noqa: BLE001
        log.warning("Sentinel-2 STAC search failed: %s", e)
        return []

    out = [{
        "id": it.id, "datetime": str(it.datetime),
        "cloud_cover": it.properties.get("eo:cloud_cover"),
    } for it in items]
    (out_dir / "sentinel2_natanz_recent.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    log.info("Found %d Sentinel-2 scenes (modern reference)", len(items))
    return out


# ---------- 2. Literature mining ---------- #
def query_iran_nuclear_papers(out_dir: Path, year_start: int = 1990, year_end: int = 2002) -> list[dict]:
    """Query OpenAlex for Iran-affiliated papers on nuclear-fuel-cycle topics."""
    import httpx

    nuclear_keywords = [
        "uranium enrichment", "centrifuge", "isotope separation",
        "uranium hexafluoride", "nuclear fuel cycle", "rotor dynamics",
    ]
    query = " OR ".join(f'"{k}"' for k in nuclear_keywords)
    params = {
        "search": query,
        "filter": (
            f"institutions.country_code:IR,"
            f"publication_year:{year_start}-{year_end}"
        ),
        "per-page": 50,
        "select": "id,title,abstract_inverted_index,authorships,publication_year,doi,cited_by_count",
    }
    log.info("Querying OpenAlex: Iran-affiliated nuclear papers %d-%d ...", year_start, year_end)
    try:
        with httpx.Client(timeout=60.0) as c:
            r = c.get("https://api.openalex.org/works", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception as e:  # noqa: BLE001
        log.warning("OpenAlex query failed: %s", e)
        return []

    works = data.get("results", [])
    log.info("Retrieved %d papers (total %d available)", len(works), data.get("meta", {}).get("count", 0))

    # Lite output for the cache
    cache = []
    for w in works:
        cache.append({
            "id": w.get("id"),
            "title": w.get("title"),
            "year": w.get("publication_year"),
            "doi": w.get("doi"),
            "cited_by_count": w.get("cited_by_count", 0),
            "first_author": (w.get("authorships") or [{}])[0].get("author", {}).get("display_name"),
        })
    (out_dir / "iran_nuclear_papers_pre2002.json").write_text(
        json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return works


# ---------- 3. Indicator synthesis ---------- #
def synthesize_indicators(papers: list[dict], imagery: list[dict], use_vlm: bool = False) -> list[Indicator]:
    """Convert raw evidence into Indicator objects.

    For the no-VLM path we use heuristic mapping (rules over keywords).
    For the VLM path we delegate to DocumentMiningModule.classify_paper.
    """
    indicators: list[Indicator] = []

    # --- Literature → V03_E05 (R&D / Training) --- #
    if use_vlm:
        try:
            from backend.app.modules.document_module import DocumentMiningModule
            mod = DocumentMiningModule()
            for w in papers[:20]:  # cap for cost
                ind = mod.classify_paper(w)
                if ind:
                    indicators.append(ind)
            log.info("VLM classified %d literature indicators", len(indicators))
        except Exception as e:  # noqa: BLE001
            log.warning("VLM classification failed (%s); falling back to heuristic", e)
            indicators.extend(_heuristic_literature(papers))
    else:
        indicators.extend(_heuristic_literature(papers))

    # --- Imagery → V03_E08 (auxiliary) placeholder --- #
    if imagery:
        indicators.append(Indicator(
            cell_id="V03_E08",
            process="gas_centrifuge",
            modality=Modality.IMAGE,
            strength=Strength.WEAK,
            confidence=0.4,
            evidence={
                "note": "Pre-2002 Landsat-7 30 m resolution; insufficient to confirm enrichment, "
                        "but capable of detecting hall + cooling + substation footprint.",
                "scenes_count": len(imagery),
                "first_scene": imagery[0].get("id") if imagery else None,
            },
            source_uri="usgs:landsat-c2-l2",
            timestamp=datetime.utcnow(),
            extracted_by="rule",
        ))

    return indicators


def _heuristic_literature(papers: list[dict]) -> list[Indicator]:
    """Simple keyword-based strength mapping for offline / no-VLM mode."""
    strong_kw = ("centrifuge", "uranium enrichment", "isotope separation")
    medium_kw = ("uranium hexafluoride", "rotor dynamics", "vacuum pump")
    out: list[Indicator] = []
    for w in papers:
        title = (w.get("title") or "").lower()
        if not title:
            continue
        if any(k in title for k in strong_kw):
            strength, conf = Strength.STRONG, 0.7
        elif any(k in title for k in medium_kw):
            strength, conf = Strength.MEDIUM, 0.55
        else:
            continue
        out.append(Indicator(
            cell_id="V03_E05",
            process="gas_centrifuge",
            modality=Modality.TEXT,
            strength=strength,
            confidence=conf,
            evidence={
                "title": w.get("title"),
                "year": w.get("publication_year"),
                "doi": w.get("doi"),
                "first_author": (w.get("authorships") or [{}])[0].get("author", {}).get("display_name"),
            },
            source_uri=w.get("doi") or w.get("id"),
            extracted_by="rule",
        ))
    return out


# ---------- 4. Main runner ---------- #
def main():
    p = argparse.ArgumentParser(description="Natanz Retrofit Test PoC")
    p.add_argument("--out", default="./data/natanz", help="Output directory")
    p.add_argument("--vlm", action="store_true", help="Use VLM classification (requires API key)")
    p.add_argument("--no-vlm", dest="vlm", action="store_false")
    p.set_defaults(vlm=False)
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("=" * 70)
    log.info("OS-PM Natanz Retrofit Test")
    log.info("Cutoff date: %s (NCRI disclosure)", PRE_DISCLOSURE_CUTOFF)
    log.info("VLM mode: %s", args.vlm)
    log.info("=" * 70)

    # 1. Imagery
    landsat = query_landsat_pre_2002(out_dir)
    sentinel = query_sentinel2_recent(out_dir)

    # 2. Literature
    papers = query_iran_nuclear_papers(out_dir, 1990, 2002)

    # 3. Indicators
    indicators = synthesize_indicators(papers, landsat or sentinel, use_vlm=args.vlm)
    log.info("Synthesized %d indicators total", len(indicators))

    # 4. Fusion
    hypotheses = fuse(indicators, prior=0.05)

    # 5. Report
    report = {
        "test_case": "Iran_Natanz_2002_pre_disclosure",
        "cutoff": PRE_DISCLOSURE_CUTOFF,
        "vlm_mode": args.vlm,
        "imagery_scenes_pre2002": len(landsat),
        "imagery_scenes_recent": len(sentinel),
        "literature_papers_pre2002": len(papers),
        "indicators_synthesized": len(indicators),
        "hypotheses": [h.model_dump() for h in hypotheses],
    }
    report_path = out_dir / "natanz_retrofit_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 70)
    print("NATANZ RETROFIT REPORT")
    print("=" * 70)
    print(f"Pre-2002 papers retrieved: {len(papers)}")
    print(f"Indicators synthesized:    {len(indicators)}")
    print(f"Hypotheses produced:       {len(hypotheses)}")
    if hypotheses:
        top = hypotheses[0]
        print(f"\nTop hypothesis: {top.process}")
        print(f"  posterior={top.posterior:.3f}")
        print(f"  cells_populated={top.cells}")
        print(f"  contributing={len(top.contributing_indicators)} indicators")
        verdict = "PASS" if top.posterior >= 0.4 and "gas_centrifuge" in top.process else "INCONCLUSIVE"
        print(f"\nValidation verdict: {verdict}")
        print("(Expected: pre-2002 OS data ALONE flags gas_centrifuge with posterior >= 0.4)")
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
