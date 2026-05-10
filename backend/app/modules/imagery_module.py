"""Imagery retrieval helpers — Sentinel-2 / Sentinel-3 / Landsat via STAC.

The module is intentionally thin: it returns *catalog* records (not the
full COGs) so that downstream code (Module A or notebooks) can decide
whether to download. This keeps the repo and tests offline-friendly.

Two STAC catalogs are supported out of the box:
- Element84 Earth Search (free, AWS-backed)         → Sentinel-2 L2A
- Microsoft Planetary Computer (free, Azure-backed) → Landsat C2 L2,
                                                        Sentinel-3 SLSTR

If ``pystac-client`` is not installed, every function returns an empty
list and emits a single warning. Tests rely on this graceful fallback.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

log = logging.getLogger(__name__)

# Known catalog endpoints
ELEMENT84_URL = "https://earth-search.aws.element84.com/v1"
MS_PLANETARY_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


@dataclass(frozen=True)
class STACScene:
    """Lightweight wrapper around a pystac Item."""
    id: str
    collection: str
    datetime: str
    cloud_cover: float | None
    bbox: tuple[float, float, float, float] | None
    preview_href: str | None
    platform: str | None
    properties: dict


def _get_pystac():
    try:
        from pystac_client import Client  # type: ignore[import-not-found]
        return Client
    except ImportError:
        log.warning("pystac-client not installed; imagery queries return [].")
        return None


def _bbox_around(lat: float, lon: float, half_deg: float = 0.05) -> tuple[float, float, float, float]:
    """Return (lon_min, lat_min, lon_max, lat_max). half_deg ≈ 5 km at equator."""
    return (lon - half_deg, lat - half_deg, lon + half_deg, lat + half_deg)


def _collect(items, max_items: int) -> list[STACScene]:
    out: list[STACScene] = []
    for it in items:
        if len(out) >= max_items:
            break
        bbox = tuple(it.bbox) if it.bbox else None
        cc = it.properties.get("eo:cloud_cover")
        preview = (it.assets.get("rendered_preview").href
                   if "rendered_preview" in it.assets else None)
        out.append(STACScene(
            id=it.id,
            collection=it.collection_id,
            datetime=str(it.datetime),
            cloud_cover=float(cc) if cc is not None else None,
            bbox=bbox,
            preview_href=preview,
            platform=it.properties.get("platform"),
            properties=dict(it.properties),
        ))
    return out


def search_sentinel2(
    lat: float,
    lon: float,
    *,
    start: date,
    end: date,
    max_items: int = 10,
    cloud_cover_lt: float = 20.0,
) -> list[STACScene]:
    """Sentinel-2 L2A over a point."""
    Client = _get_pystac()
    if Client is None:
        return []
    bbox = _bbox_around(lat, lon)
    try:
        client = Client.open(ELEMENT84_URL)
        search = client.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            query={"eo:cloud_cover": {"lt": cloud_cover_lt}},
            max_items=max_items,
        )
        return _collect(search.items(), max_items)
    except Exception as e:  # noqa: BLE001
        log.warning("Sentinel-2 STAC search failed: %s", e)
        return []


def search_landsat(
    lat: float,
    lon: float,
    *,
    start: date,
    end: date,
    max_items: int = 10,
    cloud_cover_lt: float = 30.0,
) -> list[STACScene]:
    """Landsat Collection 2 Level 2 (covers Landsat-5/7/8/9)."""
    Client = _get_pystac()
    if Client is None:
        return []
    bbox = _bbox_around(lat, lon)
    try:
        client = Client.open(MS_PLANETARY_URL)
        search = client.search(
            collections=["landsat-c2-l2"],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            query={"eo:cloud_cover": {"lt": cloud_cover_lt}},
            max_items=max_items,
        )
        return _collect(search.items(), max_items)
    except Exception as e:  # noqa: BLE001
        log.warning("Landsat STAC search failed: %s", e)
        return []


def search_sentinel3_slstr(
    lat: float,
    lon: float,
    *,
    start: date,
    end: date,
    max_items: int = 5,
) -> list[STACScene]:
    """Sentinel-3 SLSTR (thermal IR; useful for V05_E07 / V08_E07)."""
    Client = _get_pystac()
    if Client is None:
        return []
    bbox = _bbox_around(lat, lon, half_deg=0.5)  # SLSTR is 1km, wider tile
    try:
        client = Client.open(MS_PLANETARY_URL)
        search = client.search(
            collections=["sentinel-3-slstr-lst-l2-netcdf"],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            max_items=max_items,
        )
        return _collect(search.items(), max_items)
    except Exception as e:  # noqa: BLE001
        log.debug("Sentinel-3 STAC search failed (collection may not exist): %s", e)
        return []


# --------------------------------------------------------------------------- #
#  Thermal-anomaly heuristic (for V05_E07 / V08_E07)
# --------------------------------------------------------------------------- #


def thermal_anomaly_indicator_stub(
    *,
    facility_name: str,
    lat: float,
    lon: float,
    n_thermal_scenes: int,
) -> Optional[dict]:
    """Produce a stub Indicator dict when at least N thermal scenes exist.

    Real thermal-anomaly extraction would download the SLSTR L2 LST
    product, mask the facility AOI, and compute a delta-T against the
    surrounding background. That is Phase 2 work; here we expose a
    stub so the rest of the pipeline can be exercised end-to-end.
    """
    if n_thermal_scenes < 1:
        return None
    return {
        "cell_id": "V05_E07",
        "process": "light_water_reactor_LWR",
        "modality": "env_signal",
        "strength": "weak",
        "confidence": 0.3,
        "evidence": {
            "facility": facility_name,
            "lat": lat, "lon": lon,
            "n_thermal_scenes": n_thermal_scenes,
            "note": ("Phase-1 stub. Phase 2 will compute background-corrected "
                     "delta-T from SLSTR LST L2 NetCDFs."),
        },
        "source_uri": "sentinel3_slstr_phase1_stub",
        "extracted_by": "rule_phase1_stub",
    }
