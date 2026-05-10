"""Module C — Cross-modal Bayesian fusion (baseline).

Bayesian update: posterior_odds = prior_odds * Π LR_i^{c_i}
where c_i ∈ [0,1] is per-indicator confidence (0 → ignore, 1 → full LR).
The confidence-weighted exponent makes uncertain indicators contribute
proportionally less, which is well-defined as a saturation operator on
the log-LR.
"""
from __future__ import annotations

from collections import defaultdict
from math import exp, log

from ..schemas.indicator import Indicator, ProcessHypothesis, Strength

# Likelihood ratios per strength tier — calibrated against Phase-1 retrofit cases.
# Higher values reflect that a STRONG safeguards indicator (e.g., maraging
# steel + filament winder + balancing machine bundle) is genuinely diagnostic.
_LR: dict[str, float] = {
    Strength.STRONG.value: 8.0,
    Strength.MEDIUM.value: 2.5,
    Strength.WEAK.value: 1.3,
    Strength.UNCERTAIN.value: 1.0,
}


def _strength_key(strength: Strength | str) -> str:
    return strength.value if hasattr(strength, "value") else str(strength)


def fuse(indicators: list[Indicator], prior: float = 0.05) -> list[ProcessHypothesis]:
    """Aggregate indicators by process and update Bayesian belief."""
    by_process: dict[str, list[Indicator]] = defaultdict(list)
    for ind in indicators:
        by_process[ind.process].append(ind)

    out: list[ProcessHypothesis] = []
    for process, inds in by_process.items():
        log_odds = log(prior / (1.0 - prior))
        for ind in inds:
            lr = _LR.get(_strength_key(ind.strength), 1.0)
            confidence = max(min(ind.confidence, 1.0), 0.0)
            log_odds += confidence * log(lr)
        odds = exp(log_odds)
        post = odds / (1.0 + odds)
        out.append(
            ProcessHypothesis(
                process=process,
                cells=sorted({i.cell_id for i in inds}),
                posterior=min(max(post, 0.0), 1.0),
                contributing_indicators=inds,
                rationale=f"Fused {len(inds)} indicator(s) with prior {prior}.",
            )
        )
    out.sort(key=lambda h: h.posterior, reverse=True)
    return out
