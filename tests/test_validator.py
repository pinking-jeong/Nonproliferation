"""Tests for the Module F historical retrofit validator."""
from datetime import date

import pytest

from backend.app.modules.validator import (
    HISTORICAL_CASES,
    HistoricalCase,
    compute_metrics,
    run_all,
    run_case,
    synthetic_collector,
)
from backend.app.schemas.indicator import Indicator, Modality, Strength


def _ind(cell, process, strength=Strength.STRONG, conf=0.85):
    return Indicator(
        cell_id=cell, process=process, modality=Modality.TEXT,
        strength=strength, confidence=conf,
    )


def test_canonical_cases_are_defined():
    """Phase 1 + Phase 2 disclosed-historical cases."""
    expected = {
        "iran_natanz_2002", "libya_2003", "iraq_pre_1991", "syria_alkibar_2007",
        # Phase 2 expansion (voluntarily-disclosed programmes)
        "south_africa_pre_1991", "argentina_pre_1991", "brazil_pre_1991",
        "taiwan_pre_1988",
    }
    assert set(HISTORICAL_CASES.keys()) == expected
    for c in HISTORICAL_CASES.values():
        assert isinstance(c.cut_off, date)
        assert c.expected_top_process
        assert c.expected_pm_cells


def test_run_case_with_correct_indicators_passes():
    case = HISTORICAL_CASES["iran_natanz_2002"]
    indicators = [
        _ind("V03_E01", "gas_centrifuge"),
        _ind("V03_E04", "gas_centrifuge", Strength.MEDIUM, 0.7),
        _ind("V03_E08", "gas_centrifuge"),
    ]
    coll = synthetic_collector({case.name: indicators})
    result = run_case(case, coll)
    assert result.top_process_match
    assert result.top3_match
    assert result.cells_recall > 0
    assert result.posterior_top1 > 0.4


def test_run_case_with_irrelevant_indicators_fails():
    case = HISTORICAL_CASES["iran_natanz_2002"]
    indicators = [_ind("V09_E05", "actinide_chemistry_general", Strength.WEAK, 0.4)]
    coll = synthetic_collector({case.name: indicators})
    result = run_case(case, coll)
    assert not result.top_process_match
    assert not result.top3_match


def test_run_all_aggregates_metrics():
    """Phase 1 4-case sub-aggregate (explicit cases= argument)."""
    inds = {
        "iran_natanz_2002": [_ind("V03_E01", "gas_centrifuge"),
                             _ind("V03_E08", "gas_centrifuge")],
        "libya_2003": [_ind("V03_E01", "gas_centrifuge"),
                       _ind("V03_E04", "gas_centrifuge")],
        "iraq_pre_1991": [_ind("V03_E01", "electromagnetic_calutron"),
                          _ind("V03_E05", "electromagnetic_calutron")],
        "syria_alkibar_2007": [_ind("V05_E01", "graphite_moderated_reactor"),
                                _ind("V05_E08", "graphite_moderated_reactor")],
    }
    phase1_cases = [HISTORICAL_CASES[name] for name in inds]
    results, metrics = run_all(synthetic_collector(inds), cases=phase1_cases)
    assert metrics.n_cases == 4
    assert metrics.top1_accuracy == 1.0
    assert metrics.mean_cells_recall > 0


def test_compute_metrics_handles_mixed_results():
    case_iran = HISTORICAL_CASES["iran_natanz_2002"]
    case_libya = HISTORICAL_CASES["libya_2003"]

    # Iran correct, Libya wrong
    inds = {
        "iran_natanz_2002": [_ind("V03_E01", "gas_centrifuge"),
                             _ind("V03_E08", "gas_centrifuge")],
        "libya_2003": [_ind("V09_E05", "irrelevant", Strength.WEAK, 0.3)],
    }
    coll = synthetic_collector(inds)
    results, metrics = run_all(coll, cases=[case_iran, case_libya])
    assert metrics.top1_accuracy == 0.5
    assert metrics.expected_calibration_error >= 0


def test_natanz_case_metadata_correct():
    case = HISTORICAL_CASES["iran_natanz_2002"]
    assert case.cut_off == date(2002, 8, 14)
    assert case.expected_top_process == "gas_centrifuge"
    assert "V03_E01" in case.expected_pm_cells


def test_metrics_to_dict_serialises():
    inds = {"iran_natanz_2002": [_ind("V03_E01", "gas_centrifuge")]}
    coll = synthetic_collector(inds)
    results, metrics = run_all(coll, cases=[HISTORICAL_CASES["iran_natanz_2002"]])
    d = metrics.to_dict()
    assert "top1_accuracy" in d
    assert "n_cases" in d
    rd = results[0].to_dict()
    assert rd["case"] == "iran_natanz_2002"
