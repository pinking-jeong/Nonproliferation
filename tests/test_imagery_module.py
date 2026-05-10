"""Tests for the imagery STAC module — graceful fallback when offline."""
from datetime import date
from unittest.mock import patch

from backend.app.modules.imagery_module import (
    _bbox_around,
    search_landsat,
    search_sentinel2,
    search_sentinel3_slstr,
    thermal_anomaly_indicator_stub,
)


def test_bbox_around_centered_correctly():
    lo, la, hi_lo, hi_la = _bbox_around(33.7244, 51.7264, half_deg=0.05)
    # lon_min, lat_min, lon_max, lat_max
    assert abs(lo - 51.6764) < 1e-6
    assert abs(la - 33.6744) < 1e-6
    assert abs(hi_lo - 51.7764) < 1e-6
    assert abs(hi_la - 33.7744) < 1e-6


def test_pystac_missing_returns_empty():
    """When pystac is missing the searches return [] and warn."""
    with patch("backend.app.modules.imagery_module._get_pystac", return_value=None):
        s = search_sentinel2(33.0, 51.0, start=date(2024, 1, 1), end=date(2024, 1, 31))
        assert s == []
        s = search_landsat(33.0, 51.0, start=date(2000, 1, 1), end=date(2002, 1, 1))
        assert s == []
        s = search_sentinel3_slstr(33.0, 51.0, start=date(2024, 1, 1), end=date(2024, 1, 31))
        assert s == []


def test_thermal_stub_zero_scenes_returns_none():
    out = thermal_anomaly_indicator_stub(
        facility_name="X", lat=33.0, lon=51.0, n_thermal_scenes=0,
    )
    assert out is None


def test_thermal_stub_with_scenes_yields_indicator_dict():
    out = thermal_anomaly_indicator_stub(
        facility_name="Bushehr", lat=28.83, lon=50.89, n_thermal_scenes=4,
    )
    assert out is not None
    assert out["cell_id"] == "V05_E07"
    assert out["modality"] == "env_signal"
    assert out["strength"] == "weak"
    assert out["evidence"]["n_thermal_scenes"] == 4


def test_search_handles_network_failure_gracefully():
    """If Client.open or the search throws, function returns []."""
    class _FakeClient:
        @staticmethod
        def open(_url):
            raise RuntimeError("simulated network down")

    with patch("backend.app.modules.imagery_module._get_pystac",
               return_value=_FakeClient):
        out = search_sentinel2(33.0, 51.0, start=date(2024, 1, 1),
                               end=date(2024, 1, 31))
        assert out == []
