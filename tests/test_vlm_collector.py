"""Tests for the VLM-mode collector — uses mocks since no API key is set."""
from unittest.mock import patch

from backend.app.modules.case_collectors_vlm import (
    _vlm_available,
    vlm_collector,
)
from backend.app.modules.validator import HISTORICAL_CASES
from backend.app.schemas.indicator import Indicator, Modality, Strength


def test_no_key_falls_back_to_heuristic():
    """With no ANTHROPIC_API_KEY, vlm_collector defers to heuristic."""
    case = HISTORICAL_CASES["iran_natanz_2002"]
    with patch("backend.app.modules.case_collectors_vlm._vlm_available",
               return_value=False), \
         patch("backend.app.modules.case_collectors.combined_collector") as fake:
        fake.return_value = [
            Indicator(cell_id="V03_E05", process="gas_centrifuge",
                      modality=Modality.TEXT, strength=Strength.STRONG,
                      confidence=0.7)
        ]
        out = vlm_collector(case)
        assert len(out) == 1
        assert out[0].cell_id == "V03_E05"


def test_vlm_unknown_case_returns_empty():
    """Unknown case name produces an empty result, not a crash."""
    from datetime import date

    from backend.app.modules.validator import HistoricalCase
    fake_case = HistoricalCase(
        name="hypothetical_x",
        state="ZZ",
        cut_off=date(2020, 1, 1),
        public_disclosure_event="hypothetical",
        expected_top_process="gas_centrifuge",
        expected_pm_cells=("V03_E01",),
        minimum_lead_time_years=(1, 2),
    )
    with patch("backend.app.modules.case_collectors_vlm._vlm_available",
               return_value=True):
        out = vlm_collector(fake_case)
        assert out == []


def test_classify_papers_via_vlm_handles_failures():
    """If the VLM client raises, the function returns an empty list."""
    from backend.app.modules.case_collectors_vlm import _classify_papers_via_vlm
    # DocumentMiningModule is imported inside the function; patch at source.
    with patch("backend.app.modules.document_module.DocumentMiningModule",
               side_effect=Exception("forced")):
        # Should fall back to heuristic; no papers in -> no indicators out
        out = _classify_papers_via_vlm([], "iran_natanz_2002")
        assert out == []


def test_vlm_available_reads_settings():
    """Sanity: _vlm_available returns a bool; in tests the key is empty."""
    val = _vlm_available()
    assert isinstance(val, bool)
