"""Tests for the Bayesian fusion module."""
from backend.app.modules.fusion_module import fuse
from backend.app.schemas.indicator import Indicator, Modality, Strength


def _ind(cell, process, strength, conf):
    return Indicator(
        cell_id=cell, process=process, modality=Modality.IMAGE,
        strength=strength, confidence=conf,
    )


def test_strong_indicators_increase_posterior():
    """Strong + medium indicators should lift posterior well above the 0.05 prior."""
    indicators = [
        _ind("V03_E01", "gas_centrifuge", Strength.STRONG, 0.9),
        _ind("V03_E04", "gas_centrifuge", Strength.MEDIUM, 0.7),
    ]
    out = fuse(indicators, prior=0.05)
    assert len(out) == 1
    # With LR_strong=8, LR_medium=2.5 and the prior 0.05 we expect ~0.30.
    assert out[0].posterior > 0.20, (
        f"Expected posterior >> prior, got {out[0].posterior:.3f}"
    )


def test_two_strong_indicators_cross_50pct():
    """Two strong indicators with high confidence should cross 50%."""
    indicators = [
        _ind("V03_E01", "gas_centrifuge", Strength.STRONG, 0.95),
        _ind("V03_E08", "gas_centrifuge", Strength.STRONG, 0.9),
    ]
    out = fuse(indicators, prior=0.05)
    assert out[0].posterior > 0.5


def test_weak_indicator_low_posterior():
    indicators = [_ind("V03_E08", "gas_centrifuge", Strength.WEAK, 0.4)]
    out = fuse(indicators, prior=0.05)
    assert out[0].posterior < 0.2


def test_multiple_processes_separated():
    indicators = [
        _ind("V03_E01", "gas_centrifuge", Strength.STRONG, 0.9),
        _ind("V07_E01", "reprocessing", Strength.STRONG, 0.9),
    ]
    out = fuse(indicators)
    procs = {h.process for h in out}
    assert procs == {"gas_centrifuge", "reprocessing"}
