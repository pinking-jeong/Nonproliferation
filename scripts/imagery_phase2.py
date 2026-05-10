"""Phase 2 imagery retrofit — STAC discovery for all 4 historical cases.

For each case:
- Query Landsat C2 L2 over the case AOI for the year-window ending at
  the cut-off (these are the scenes that would have been visible to
  any analyst pre-disclosure).
- Query Sentinel-2 (where applicable) for a modern reference.
- Optionally query Sentinel-3 SLSTR for thermal IR.

Output: ``data/retrofit/imagery_phase2.json`` summarising scene counts
per case. No COGs are downloaded — that is a Phase 2.5 task with
storage budget.
"""
from __future__ import annotations

import json
import logging
import sys
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.imagery_module import (  # noqa: E402
    search_landsat,
    search_sentinel2,
    search_sentinel3_slstr,
    thermal_anomaly_indicator_stub,
)
from backend.app.modules.validator import HISTORICAL_CASES  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("imagery-phase2")

# Public, well-documented coordinates for each historical case.
CASE_AOI: dict[str, tuple[str, float, float]] = {
    "iran_natanz_2002":      ("Natanz FEP",            33.7244,  51.7264),
    "libya_2003":            ("Tajura Nuclear Centre", 32.8869,  13.3503),
    "iraq_pre_1991":         ("Tuwaitha (Tarmiya AOI)",33.4011,  44.4561),
    "syria_alkibar_2007":    ("Al-Kibar",              35.7077,  39.8367),
}


def _scene_dict(scene) -> dict:
    return {
        "id": scene.id,
        "collection": scene.collection,
        "datetime": scene.datetime,
        "cloud_cover": scene.cloud_cover,
        "platform": scene.platform,
    }


def main():
    out: dict = {"cases": {}, "stub_indicators": []}
    for case_name, case in HISTORICAL_CASES.items():
        if case_name not in CASE_AOI:
            log.warning("No AOI registered for %s", case_name)
            continue
        facility, lat, lon = CASE_AOI[case_name]
        cut = case.cut_off
        start = date(cut.year - 2, 1, 1)
        log.info("[%s] AOI %s @ %.4f,%.4f, window %s..%s",
                 case_name, facility, lat, lon, start, cut)

        landsat = search_landsat(lat, lon, start=start, end=cut, max_items=10)
        sentinel2 = (
            search_sentinel2(lat, lon, start=date(2023, 1, 1), end=date(2024, 12, 31),
                             max_items=5)
            if cut.year < 2015
            else search_sentinel2(lat, lon, start=start, end=cut, max_items=10)
        )
        slstr = search_sentinel3_slstr(
            lat, lon,
            start=date(max(start.year, 2018), 1, 1),
            end=cut + timedelta(days=1),
            max_items=5,
        )

        out["cases"][case_name] = {
            "facility": facility,
            "lat": lat,
            "lon": lon,
            "cut_off": cut.isoformat(),
            "landsat_scenes_pre_cut_off": [_scene_dict(s) for s in landsat],
            "sentinel2_modern_reference": [_scene_dict(s) for s in sentinel2],
            "sentinel3_slstr_thermal": [_scene_dict(s) for s in slstr],
        }

        # Phase-1 stub indicator if any thermal scenes
        if slstr:
            stub = thermal_anomaly_indicator_stub(
                facility_name=facility, lat=lat, lon=lon,
                n_thermal_scenes=len(slstr),
            )
            if stub is not None:
                out["stub_indicators"].append({"case": case_name, **stub})

    out_dir = Path("./data/retrofit")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "imagery_phase2.json"
    out_path.write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False),
                        encoding="utf-8")

    print("\n" + "=" * 70)
    print("IMAGERY PHASE 2 - STAC discovery summary")
    print("=" * 70)
    for c, info in out["cases"].items():
        print(f"\n[{c}] {info['facility']}")
        print(f"  Landsat pre-cut-off  : {len(info['landsat_scenes_pre_cut_off'])} scenes")
        print(f"  Sentinel-2 reference : {len(info['sentinel2_modern_reference'])} scenes")
        print(f"  Sentinel-3 SLSTR     : {len(info['sentinel3_slstr_thermal'])} scenes")
    print(f"\nReport: {out_path}")


if __name__ == "__main__":
    main()
