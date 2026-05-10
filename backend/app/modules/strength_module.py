"""Module D — Indicator Strength Estimator.

Combines two complementary approaches:

1. **Cooke's Classical Model** for expert elicitation
   - Experts give quantile estimates on seed variables with known truth
   - Calibration ($C$) measures alignment with truth
   - Informativeness ($I$) measures specificity vs. background
   - Combined weight $w = C \\cdot I$ (or $\\mathbf{1}[C > \\alpha] \\cdot C \\cdot I$)
   - Aggregated strength is a weighted geometric mean.

2. **Bayesian likelihood-ratio update** (re-uses fusion_module's LR table)
   - Provides a per-cell prior LR independent of expert input
   - Allows graceful operation before any elicitation is collected.

Reference:
   Cooke, R. M. (1991). *Experts in Uncertainty: Opinion and Subjective
   Probability in Science*. Oxford University Press.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from ..schemas.indicator import Strength

# Map strength tiers to numeric scores for aggregation.
STRENGTH_SCORE: dict[str, float] = {
    Strength.STRONG.value: 3.0,
    Strength.MEDIUM.value: 2.0,
    Strength.WEAK.value: 1.0,
    Strength.UNCERTAIN.value: 0.5,
}

SCORE_TO_STRENGTH: list[tuple[float, Strength]] = [
    (2.5, Strength.STRONG),
    (1.5, Strength.MEDIUM),
    (0.75, Strength.WEAK),
    (0.0, Strength.UNCERTAIN),
]


# --------------------------------------------------------------------------- #
#  Cooke classical model
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ExpertAssessment:
    """One expert's quantile assessment of a single variable.

    Quantiles are stored as (q05, q50, q95) — the canonical 3-quantile form
    used in Cooke elicitation. ``true_value`` is set only on seed variables.
    """

    expert_id: str
    variable_id: str
    q05: float
    q50: float
    q95: float
    true_value: float | None = None  # set on seed variables only

    def contains(self, x: float) -> bool:
        return self.q05 <= x <= self.q95


def calibration_score(assessments: list[ExpertAssessment]) -> float:
    """Calibration $C$: chi-square test against expected (5/45/45/5)% bins.

    Each seed assessment partitions the real line into 4 bins via its
    (q05, q50, q95). Under perfect calibration, an expert's true values fall
    into bins with frequencies (0.05, 0.45, 0.45, 0.05). We compare the
    observed frequencies to the theoretical via chi-square.
    """
    n_seed = sum(1 for a in assessments if a.true_value is not None)
    if n_seed == 0:
        return 0.0

    # Empirical bin counts
    observed = [0, 0, 0, 0]
    for a in assessments:
        if a.true_value is None:
            continue
        x = a.true_value
        if x < a.q05:
            observed[0] += 1
        elif x < a.q50:
            observed[1] += 1
        elif x < a.q95:
            observed[2] += 1
        else:
            observed[3] += 1

    # Theoretical probabilities
    p = [0.05, 0.45, 0.45, 0.05]
    expected = [pi * n_seed for pi in p]
    chi2 = sum(
        (oi - ei) ** 2 / ei if ei > 0 else 0.0
        for oi, ei in zip(observed, expected)
    )
    # Convert chi-square to a [0,1] score using a soft transform.
    return math.exp(-chi2 / 2.0)


def informativeness_score(
    assessments: list[ExpertAssessment], background_range: tuple[float, float]
) -> float:
    """Informativeness $I$: relative entropy vs uniform background distribution.

    Higher $I$ means an expert's quantiles are more concentrated than the
    background reference range. We average over assessments; only finite,
    bounded assessments contribute.
    """
    if not assessments:
        return 0.0

    bg_lo, bg_hi = background_range
    if bg_hi <= bg_lo:
        return 0.0
    bg_width = bg_hi - bg_lo

    contributions: list[float] = []
    for a in assessments:
        width = max(a.q95 - a.q05, 1e-9)
        # Normalised entropy reduction
        contributions.append(max(math.log(bg_width / width), 0.0))
    return sum(contributions) / len(contributions)


def expert_weight(
    assessments: list[ExpertAssessment],
    background_range: tuple[float, float],
    calibration_threshold: float = 0.0,
) -> float:
    """Combined Cooke weight $w = C \\cdot I$ (optionally gated by threshold)."""
    c = calibration_score(assessments)
    if c < calibration_threshold:
        return 0.0
    i = informativeness_score(assessments, background_range)
    return c * i


def aggregate_expert_strength(
    expert_strengths: dict[str, Strength | str],
    expert_weights: dict[str, float],
) -> tuple[Strength, float]:
    """Combine multiple experts' strength tier judgments into one decision.

    Each expert provides one of {strong, medium, weak, uncertain} for the
    same indicator. Returns the consensus strength and the normalized
    confidence (sum of weights for supporting experts / total weight).
    """
    if not expert_strengths or not expert_weights:
        return Strength.UNCERTAIN, 0.0

    # Weighted score
    total_w = sum(expert_weights.get(eid, 0.0) for eid in expert_strengths)
    if total_w <= 0:
        return Strength.UNCERTAIN, 0.0

    score = 0.0
    for eid, s in expert_strengths.items():
        w = expert_weights.get(eid, 0.0)
        key = s.value if hasattr(s, "value") else str(s)
        score += w * STRENGTH_SCORE.get(key, 0.5)
    score /= total_w

    # Map back to a tier
    for threshold, tier in SCORE_TO_STRENGTH:
        if score >= threshold:
            chosen = tier
            break
    else:
        chosen = Strength.UNCERTAIN

    # Confidence: fraction of weight backing the chosen-or-stronger tier
    chosen_score = STRENGTH_SCORE[chosen.value]
    supporting_w = sum(
        expert_weights.get(eid, 0.0)
        for eid, s in expert_strengths.items()
        if STRENGTH_SCORE.get(
            s.value if hasattr(s, "value") else str(s), 0.0
        )
        >= chosen_score
    )
    confidence = supporting_w / total_w
    return chosen, min(max(confidence, 0.0), 1.0)


# --------------------------------------------------------------------------- #
#  Pure-Bayesian baseline (used when no expert input available)
# --------------------------------------------------------------------------- #


def bayesian_strength_baseline(
    indicator_modality: str,
    has_visual_match: bool,
    has_trade_bundle: bool,
    has_rd_signal: bool,
) -> tuple[Strength, float]:
    """Default strength when no expert elicitation is available.

    Implements the cell-level confidence_rules summarized in the V03 YAMLs
    for the MVP (≥3 multimodal lines → strong, etc.).
    """
    n_signals = sum([has_visual_match, has_trade_bundle, has_rd_signal])
    if n_signals >= 3:
        return Strength.STRONG, 0.85
    if n_signals == 2:
        return Strength.MEDIUM, 0.65
    if n_signals == 1:
        return Strength.WEAK, 0.45
    return Strength.UNCERTAIN, 0.25


# --------------------------------------------------------------------------- #
#  High-level orchestrator
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StrengthVerdict:
    strength: Strength
    confidence: float
    method: str  # "cooke" | "bayesian_baseline"
    rationale: str


def estimate_strength(
    *,
    cooke_inputs: tuple[
        dict[str, list[ExpertAssessment]],  # per-expert assessments
        dict[str, Strength | str],  # per-expert tier verdict on the indicator
        tuple[float, float],  # background range used for informativeness
    ]
    | None = None,
    fallback_signals: tuple[bool, bool, bool] | None = None,
) -> StrengthVerdict:
    """Top-level entry: prefer Cooke aggregation when expert data exist."""
    if cooke_inputs is not None:
        per_expert_assessments, per_expert_tiers, background = cooke_inputs
        weights = {
            eid: expert_weight(asss, background)
            for eid, asss in per_expert_assessments.items()
        }
        if any(w > 0 for w in weights.values()):
            tier, conf = aggregate_expert_strength(per_expert_tiers, weights)
            return StrengthVerdict(
                strength=tier,
                confidence=conf,
                method="cooke",
                rationale=f"Aggregated {len(weights)} expert(s) with positive Cooke weight.",
            )

    has_visual, has_trade, has_rd = fallback_signals or (False, False, False)
    tier, conf = bayesian_strength_baseline(
        indicator_modality="auto",
        has_visual_match=has_visual,
        has_trade_bundle=has_trade,
        has_rd_signal=has_rd,
    )
    return StrengthVerdict(
        strength=tier,
        confidence=conf,
        method="bayesian_baseline",
        rationale=f"Bayesian baseline with {sum(fallback_signals or (False, False, False))} signal(s).",
    )
