"""Tests for the Module D strength estimator."""
from backend.app.modules.strength_module import (
    ExpertAssessment,
    aggregate_expert_strength,
    bayesian_strength_baseline,
    calibration_score,
    estimate_strength,
    expert_weight,
    informativeness_score,
)
from backend.app.schemas.indicator import Strength


def _seeds(eid: str, calls):
    return [
        ExpertAssessment(
            expert_id=eid,
            variable_id=f"seed{i}",
            q05=lo,
            q50=md,
            q95=hi,
            true_value=truth,
        )
        for i, (lo, md, hi, truth) in enumerate(calls)
    ]


def test_calibration_perfect_expert_high_score():
    """Expert whose 90% intervals always contain truth is well-calibrated."""
    seeds = _seeds(
        "E1",
        [
            (0.0, 5.0, 10.0, 5.0),
            (10.0, 20.0, 30.0, 21.0),
            (100.0, 200.0, 300.0, 199.0),
        ],
    )
    score = calibration_score(seeds)
    # 100% in central bins → low chi-square → high score
    assert score > 0.4, f"Expected good calibration, got {score:.3f}"


def test_calibration_poor_expert_low_score():
    """Expert who is always wrong gets a low score."""
    seeds = _seeds(
        "E2",
        [
            (0.0, 5.0, 10.0, 100.0),
            (10.0, 20.0, 30.0, 1000.0),
            (100.0, 200.0, 300.0, 9999.0),
        ],
    )
    score = calibration_score(seeds)
    # 100% in extreme bins → high chi-square → low score
    assert score < 0.2, f"Expected poor calibration, got {score:.3f}"


def test_informativeness_narrow_intervals_higher():
    narrow = _seeds("E_narrow", [(9.0, 10.0, 11.0, 10.0)])
    wide = _seeds("E_wide", [(0.0, 50.0, 100.0, 50.0)])
    bg = (0.0, 1000.0)
    assert informativeness_score(narrow, bg) > informativeness_score(wide, bg)


def test_aggregate_expert_strength_simple():
    tiers = {
        "E1": Strength.STRONG,
        "E2": Strength.MEDIUM,
        "E3": Strength.WEAK,
    }
    weights = {"E1": 1.0, "E2": 1.0, "E3": 1.0}
    tier, conf = aggregate_expert_strength(tiers, weights)
    # Mean score = (3 + 2 + 1) / 3 = 2.0  → MEDIUM
    assert tier == Strength.MEDIUM
    assert 0.5 <= conf <= 1.0


def test_aggregate_with_zero_weights_returns_uncertain():
    tiers = {"E1": Strength.STRONG}
    weights = {"E1": 0.0}
    tier, conf = aggregate_expert_strength(tiers, weights)
    assert tier == Strength.UNCERTAIN
    assert conf == 0.0


def test_bayesian_baseline_three_signals_strong():
    tier, conf = bayesian_strength_baseline(
        indicator_modality="any",
        has_visual_match=True,
        has_trade_bundle=True,
        has_rd_signal=True,
    )
    assert tier == Strength.STRONG
    assert conf >= 0.8


def test_bayesian_baseline_no_signals_uncertain():
    tier, _ = bayesian_strength_baseline(
        indicator_modality="any",
        has_visual_match=False,
        has_trade_bundle=False,
        has_rd_signal=False,
    )
    assert tier == Strength.UNCERTAIN


def test_estimate_strength_falls_back_when_no_expert_data():
    verdict = estimate_strength(fallback_signals=(True, True, False))
    assert verdict.method == "bayesian_baseline"
    assert verdict.strength == Strength.MEDIUM
    assert "2 signal" in verdict.rationale


def test_estimate_strength_uses_cooke_when_expert_data_available():
    seeds_e1 = _seeds(
        "E1",
        [
            (0.0, 5.0, 10.0, 5.0),
            (10.0, 20.0, 30.0, 21.0),
            (100.0, 200.0, 300.0, 199.0),
        ],
    )
    seeds_e2 = _seeds(
        "E2",
        [
            (0.0, 5.0, 10.0, 5.5),
            (10.0, 20.0, 30.0, 22.0),
            (100.0, 200.0, 300.0, 205.0),
        ],
    )
    cooke_inputs = (
        {"E1": seeds_e1, "E2": seeds_e2},
        {"E1": Strength.STRONG, "E2": Strength.STRONG},
        (0.0, 1000.0),
    )
    verdict = estimate_strength(cooke_inputs=cooke_inputs)
    assert verdict.method == "cooke"
    assert verdict.strength == Strength.STRONG
    assert verdict.confidence > 0.5


def test_expert_weight_combines_calibration_and_informativeness():
    seeds = _seeds("E1", [(9.0, 10.0, 11.0, 10.0)])  # narrow + correct
    w_narrow = expert_weight(seeds, background_range=(0.0, 1000.0))
    seeds_wide = _seeds("E2", [(0.0, 50.0, 100.0, 50.0)])
    w_wide = expert_weight(seeds_wide, background_range=(0.0, 1000.0))
    # Narrow + correct should outweigh wide + correct
    assert w_narrow > w_wide
