"""Tests for GNN-light risk scoring."""
import numpy as np

from backend.app.modules.apa_graph import build_default_graph
from backend.app.modules.gnn_lite import (
    FEATURE_NAMES,
    extract_features,
    train_evaluate_loo,
)
from backend.app.schemas.indicator import Indicator, Modality, Strength


def _ind(cell, process, strength=Strength.STRONG, conf=0.85):
    return Indicator(
        cell_id=cell, process=process, modality=Modality.IMAGE,
        strength=strength, confidence=conf,
    )


def test_extract_features_unknown_state_returns_zeros():
    g = build_default_graph()
    feats = extract_features(g, "UnknownState")
    assert len(feats) == len(FEATURE_NAMES)
    assert np.allclose(feats, 0.0)


def test_extract_features_with_indicators():
    g = build_default_graph()
    g.add_indicator("StateA", _ind("V03_E01", "gas_centrifuge"))
    g.add_indicator("StateA", _ind("V05_E01", "heavy_water_reactor_HWR"))

    feats = extract_features(g, "StateA")
    assert len(feats) == len(FEATURE_NAMES)
    assert feats[0] == 2  # n_evidence
    assert feats[1] == 2  # n_processes


def test_loo_separates_positives_from_negatives():
    """Build 4 mini-graphs each with 2-3 indicators; LOO should recover positives."""
    cases = []
    for state, indicators in [
        ("State_Iran", [_ind("V03_E01", "gas_centrifuge"),
                        _ind("V03_E08", "gas_centrifuge"),
                        _ind("V03_E04", "gas_centrifuge", Strength.MEDIUM, 0.7)]),
        ("State_Libya", [_ind("V03_E01", "gas_centrifuge"),
                         _ind("V03_E04", "gas_centrifuge", Strength.STRONG)]),
        ("State_Iraq", [_ind("V03_E01", "electromagnetic_calutron"),
                        _ind("V03_E05", "electromagnetic_calutron")]),
        ("State_Syria", [_ind("V05_E08", "graphite_moderated_reactor"),
                         _ind("V05_E01", "graphite_moderated_reactor")]),
    ]:
        g = build_default_graph()
        cases.append((g, state, indicators))

    out = train_evaluate_loo(cases, classifier="logreg")
    assert out["n_positive"] == 4
    assert out["n_negative"] == 4
    assert out["loo_accuracy"] >= 0.5  # better than chance
    # Mean probability for positives should exceed mean for negatives
    assert out["mean_p_pos"] > out["mean_p_neg"]


def test_loo_with_gbm_runs():
    cases = [
        (build_default_graph(), "S1",
         [_ind("V03_E01", "gas_centrifuge"),
          _ind("V03_E08", "gas_centrifuge")]),
        (build_default_graph(), "S2",
         [_ind("V03_E01", "gas_centrifuge")]),
        (build_default_graph(), "S3",
         [_ind("V05_E01", "graphite_moderated_reactor")]),
    ]
    out = train_evaluate_loo(cases, classifier="gbm")
    assert "loo_accuracy" in out
    assert 0.0 <= out["loo_accuracy"] <= 1.0
