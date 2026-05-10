"""End-to-end Phase 2 imagery: visual COG → AOI crop → VLM coarse detect.

Versus the thumbnail-based smoke test in `imagery_vlm_test.py`, this
runs on the actual Sentinel-2 RGB COG (TCI.tif, 10 m GSD), crops to a
~5 km × 5 km AOI centred on the facility, and re-runs Module A. The
expectation is a markedly higher VLM confidence than the thumbnail
gave.

Usage:
    python -m scripts.imagery_cog_test --aoi natanz
    python -m scripts.imagery_cog_test --aoi tajura
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.image_module import ImageUnderstandingModule  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("imagery-cog")

AOIS = {
    "natanz":   ("Natanz FEP",            33.7244,  51.7264),
    "tajura":   ("Tajura Nuclear Centre", 32.8869,  13.3503),
    "tuwaitha": ("Tuwaitha (Tarmiya AOI)",33.4011,  44.4561),
    "alkibar":  ("Al-Kibar",              35.7077,  39.8367),
}


def _find_visual_cog(lat: float, lon: float, year: int = 2024,
                     cloud_lt: float = 5.0):
    """Return (scene_id, datetime, visual_href, cloud) or None."""
    from pystac_client import Client  # type: ignore[import-not-found]
    bbox = (lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05)
    client = Client.open("https://earth-search.aws.element84.com/v1")
    search = client.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=f"{year}-01-01/{year}-12-31",
        query={"eo:cloud_cover": {"lt": cloud_lt}},
        max_items=10,
    )
    for it in search.items():
        a = it.assets.get("visual")
        if a is None:
            continue
        return it.id, str(it.datetime), a.href, it.properties.get("eo:cloud_cover")
    return None


def _crop_aoi(visual_url: str, lat: float, lon: float,
              radius_m: float = 2500.0, dest: Path | None = None) -> Path:
    """Read a small AOI window from the COG and write a JPEG."""
    from pyproj import Transformer
    from rasterio.crs import CRS
    from rio_tiler.io import Reader

    if dest is None:
        dest = Path("./data/imagery_cog") / f"aoi_{lat:.4f}_{lon:.4f}.jpg"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        log.info("  cached AOI crop: %s (%d bytes)", dest, dest.stat().st_size)
        return dest

    with Reader(visual_url) as r:
        # Reader requires an explicit CRS for `feature` / `part` queries
        # in EPSG:4326 with the bounding box (minx, miny, maxx, maxy).
        # Approximate degree-equivalent of `radius_m` (latitude-corrected).
        d_lat = radius_m / 111_320.0
        d_lon = radius_m / (111_320.0 * max(0.001, abs(__import__("math").cos(__import__("math").radians(lat)))))
        bbox = (lon - d_lon, lat - d_lat, lon + d_lon, lat + d_lat)
        log.info("  COG bbox (lon/lat): %s", bbox)
        img = r.part(bbox, dst_crs="epsg:4326", max_size=1024)
        # Convert to JPEG and save
        from rio_tiler.utils import render
        png_bytes = render(img.data, img.mask, img_format="JPEG", colormap=None)
        dest.write_bytes(png_bytes)
        log.info("  AOI crop: %s (%d bytes)", dest, dest.stat().st_size)
    return dest


def main():
    p = argparse.ArgumentParser(description="Phase 2 imagery COG → VLM")
    p.add_argument("--aoi", choices=list(AOIS.keys()), default="natanz")
    p.add_argument("--year", type=int, default=2024)
    p.add_argument("--cloud", type=float, default=5.0)
    p.add_argument("--radius", type=float, default=2500.0,
                   help="AOI half-side in metres (default 2500 → 5km × 5km)")
    p.add_argument("--out", default="./data/imagery_cog")
    args = p.parse_args()

    facility, lat, lon = AOIS[args.aoi]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("AOI: %s (%.4f, %.4f)  radius %g m", facility, lat, lon, args.radius)
    found = _find_visual_cog(lat, lon, args.year, args.cloud)
    if not found:
        log.error("No Sentinel-2 visual COG found.")
        return 1
    sc_id, sc_dt, visual_url, cc = found
    log.info("Scene: %s  cloud=%s%%  date=%s", sc_id, cc, sc_dt[:10])

    # Crop and save
    img_path = out_dir / f"{args.aoi}_{sc_id}_aoi.jpg"
    try:
        img_path = _crop_aoi(visual_url, lat, lon, args.radius, dest=img_path)
    except Exception as e:  # noqa: BLE001
        log.exception("COG crop failed: %s", e)
        return 1

    # VLM coarse detect
    log.info("Calling VLM (Module A coarse detect) on %dx%d AOI ...",
             int(2 * args.radius), int(2 * args.radius))
    mod = ImageUnderstandingModule()
    raw = mod.coarse_detect(img_path, geo_ctx={
        "facility": facility, "lat": lat, "lon": lon,
        "scene_id": sc_id, "datetime": sc_dt,
        "aoi_radius_m": args.radius,
    })

    out = {
        "aoi": args.aoi, "facility": facility,
        "lat": lat, "lon": lon,
        "scene_id": sc_id, "scene_datetime": sc_dt,
        "scene_cloud_cover": cc,
        "aoi_radius_m": args.radius,
        "image_path": str(img_path),
        "vlm_raw": raw,
    }
    out_path = out_dir / f"{args.aoi}_cog_vlm_result.json"
    out_path.write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False),
                        encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"PHASE 2 COG IMAGERY VLM - {facility}")
    print("=" * 70)
    print(f"Scene: {sc_id}  cloud={cc}%  date={sc_dt[:10]}")
    print(f"AOI:   {args.radius:.0f} m radius (~{2 * args.radius:.0f} m × {2 * args.radius:.0f} m)")
    print(f"Image: {img_path} ({img_path.stat().st_size} bytes)")
    print(f"VLM output keys: {list(raw.keys())}")
    if "facility_type" in raw:
        print(f"  facility_type   : {raw.get('facility_type')}")
        print(f"  confidence      : {raw.get('confidence')}")
        print(f"  pm_volume       : {raw.get('pm_volume')}")
        print(f"  visual_evidence : {raw.get('visual_evidence', [])[:5]}")
    print(f"\nSaved: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
