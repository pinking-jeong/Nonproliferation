"""End-to-end imagery + VLM smoke test on a single Natanz tile.

This is the Phase 2 sanity check that the image-side pipeline works:

1. Find a recent Sentinel-2 scene over Natanz (33.7244 N, 51.7264 E)
   with low cloud cover.
2. Download the rendered RGB preview asset (a small JPEG, typically
   100--500 KB; no full COG needed for this smoke test).
3. Send the image through Module A's coarse-detect prompt via the
   active VLM backend (OpenRouter is the default in our .env).
4. Print the structured indicator and persist it to JSON.

Usage:

    python -m scripts.imagery_vlm_test
    python -m scripts.imagery_vlm_test --aoi natanz   # default
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.imagery_module import search_sentinel2  # noqa: E402
from backend.app.modules.image_module import (  # noqa: E402
    ImageUnderstandingModule,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("imagery-vlm")

AOIS = {
    "natanz":   ("Natanz FEP",            33.7244,  51.7264),
    "tajura":   ("Tajura Nuclear Centre", 32.8869,  13.3503),
    "tuwaitha": ("Tuwaitha (Tarmiya AOI)",33.4011,  44.4561),
    "alkibar":  ("Al-Kibar",              35.7077,  39.8367),
}


def download_preview(href: str, dest: Path) -> bool:
    """Download a small JPEG preview from a STAC asset URL."""
    if dest.exists():
        log.info("  preview cached: %s (%d bytes)", dest, dest.stat().st_size)
        return True
    try:
        with httpx.Client(timeout=60.0, follow_redirects=True) as c:
            r = c.get(href)
            r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.content)
        log.info("  preview saved: %s (%d bytes)", dest, dest.stat().st_size)
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("  preview download failed: %s", e)
        return False


def _thumbnail_href_via_stac(lat: float, lon: float, year: int,
                              cloud_lt: float) -> tuple[str, str, str, float | None] | None:
    """Re-query STAC and pull the ``thumbnail`` asset href directly.

    Element84's Sentinel-2 collection exposes a small JPEG ``thumbnail``
    rather than the ``rendered_preview`` Microsoft Planetary Computer
    uses. We bypass our own light wrapper here to access the full
    ``it.assets`` map.
    """
    try:
        from pystac_client import Client  # type: ignore[import-not-found]
    except ImportError:
        return None
    bbox = (lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05)
    client = Client.open("https://earth-search.aws.element84.com/v1")
    search = client.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=f"{year}-01-01/{year}-12-31",
        query={"eo:cloud_cover": {"lt": cloud_lt}},
        max_items=5,
    )
    for it in search.items():
        for key in ("thumbnail", "rendered_preview", "preview"):
            if key in it.assets:
                a = it.assets[key]
                # Skip non-image previews
                if (a.media_type or "").startswith("image/"):
                    return it.id, str(it.datetime), a.href, it.properties.get("eo:cloud_cover")
    return None


def main():
    p = argparse.ArgumentParser(description="Imagery + VLM smoke test")
    p.add_argument("--aoi", choices=list(AOIS.keys()), default="natanz")
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--cloud", type=float, default=10.0,
                   help="max cloud cover %% (default 10)")
    p.add_argument("--out", default="./data/imagery_vlm")
    args = p.parse_args()

    facility, lat, lon = AOIS[args.aoi]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("AOI: %s (%.4f, %.4f)  cloud_cover<%g%%", facility, lat, lon, args.cloud)
    found = _thumbnail_href_via_stac(lat, lon, args.year, args.cloud)
    if found is None:
        log.error("No Sentinel-2 scene with a thumbnail asset found.")
        return 1
    scene_id, scene_dt, thumb_href, cc = found
    log.info("Scene: %s  (%s, cc=%s%%)", scene_id, scene_dt[:10], cc)

    img_path = out_dir / f"{args.aoi}_{scene_id}.jpg"
    if not download_preview(thumb_href, img_path):
        return 1
    sc_id, sc_dt, sc_cc = scene_id, scene_dt, cc

    log.info("Calling VLM (Module A coarse detect) ...")
    mod = ImageUnderstandingModule()
    raw = mod.coarse_detect(img_path, geo_ctx={
        "facility": facility, "lat": lat, "lon": lon,
        "scene_id": sc_id, "datetime": sc_dt,
    })

    out = {
        "aoi": args.aoi,
        "facility": facility,
        "lat": lat,
        "lon": lon,
        "scene_id": sc_id,
        "scene_datetime": sc_dt,
        "scene_cloud_cover": sc_cc,
        "image_path": str(img_path),
        "vlm_raw": raw,
    }
    out_path = out_dir / f"{args.aoi}_vlm_result.json"
    out_path.write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False),
                        encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"IMAGERY + VLM RESULT - {facility}")
    print("=" * 70)
    print(f"Scene: {sc_id}  cloud={sc_cc}%  date={sc_dt[:10]}")
    print(f"Image: {img_path} ({img_path.stat().st_size} bytes)")
    print(f"VLM output keys: {list(raw.keys())}")
    if "facility_type" in raw:
        print(f"  facility_type   : {raw.get('facility_type')}")
        print(f"  confidence      : {raw.get('confidence')}")
        print(f"  pm_volume       : {raw.get('pm_volume')}")
        print(f"  visual_evidence : {raw.get('visual_evidence', [])[:5]}")
        print(f"  alternatives    : {raw.get('alternative_hypotheses', [])[:3]}")
    elif "raw_text" in raw:
        print(f"  raw_text (truncated): {raw['raw_text'][:300]}")
    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
