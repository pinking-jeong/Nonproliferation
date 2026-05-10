"""Module F — Historical Retrofit Validator.

Defines four canonical retrofit cases (Iran-Natanz, Libya, Iraq,
Syria-Al-Kibar) with public, post-disclosure ground truth. The
validator runs the OS-PM pipeline restricted to data available before
each disclosure date and reports correctness, calibration, and
lead-time error.

This is the *evaluation harness* for the system paper §5. Phase 1 ships
the framework + Iran-Natanz wired through; Libya/Iraq/Syria are
declared but their per-case literature/imagery loaders are Phase 2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Callable

from ..schemas.indicator import Indicator, ProcessHypothesis
from .fusion_module import fuse


# --------------------------------------------------------------------------- #
#  Case definitions — each carries enough public ground truth for retrofit
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class HistoricalCase:
    name: str
    state: str
    cut_off: date
    public_disclosure_event: str
    expected_top_process: str
    expected_pm_cells: tuple[str, ...]
    minimum_lead_time_years: tuple[int, int]
    notes: str = ""


HISTORICAL_CASES: dict[str, HistoricalCase] = {
    "iran_natanz_2002": HistoricalCase(
        name="iran_natanz_2002",
        state="IR",
        cut_off=date(2002, 8, 14),
        public_disclosure_event="NCRI press conference, 2002-08-14",
        expected_top_process="gas_centrifuge",
        expected_pm_cells=("V03_E01", "V03_E04", "V03_E05", "V03_E08"),
        minimum_lead_time_years=(3, 7),
        notes="Pilot + commercial cascade halls; declared post-disclosure.",
    ),
    "libya_2003": HistoricalCase(
        name="libya_2003",
        state="LY",
        cut_off=date(2003, 12, 19),
        public_disclosure_event="Libya renunciation announcement",
        expected_top_process="gas_centrifuge",
        expected_pm_cells=("V03_E01", "V03_E02", "V03_E04"),
        minimum_lead_time_years=(2, 5),
        notes="Procurement-network supplied centrifuge components (A.Q. Khan link).",
    ),
    "iraq_pre_1991": HistoricalCase(
        name="iraq_pre_1991",
        state="IQ",
        cut_off=date(1991, 4, 3),
        public_disclosure_event="UNSCR 687 and post-Gulf-War IAEA inspections",
        expected_top_process="electromagnetic_calutron",
        expected_pm_cells=("V03_E01", "V03_E05", "V09_E01"),
        minimum_lead_time_years=(5, 10),
        notes="Multi-pronged covert programme; calutron + gas centrifuge research.",
    ),
    "syria_alkibar_2007": HistoricalCase(
        name="syria_alkibar_2007",
        state="SY",
        cut_off=date(2007, 9, 5),
        public_disclosure_event="Israeli airstrike",
        expected_top_process="graphite_moderated_reactor",
        expected_pm_cells=("V05_E01", "V05_E04", "V05_E08"),
        minimum_lead_time_years=(3, 6),
        notes="Yongbyon-type graphite reactor under construction; pre-operational.",
    ),
    # ----- Phase 2 expansion: voluntarily-disclosed historical programmes ----- #
    "south_africa_pre_1991": HistoricalCase(
        name="south_africa_pre_1991",
        state="ZA",
        cut_off=date(1991, 7, 10),
        public_disclosure_event="South Africa NPT accession; subsequent IAEA disclosure of dismantled programme",
        expected_top_process="aerodynamic_jet_nozzle",
        expected_pm_cells=("V03_E01", "V03_E04", "V03_E05"),
        minimum_lead_time_years=(8, 15),
        notes=(
            "Pelindaba aerodynamic-vortex (Helikon) enrichment plant; "
            "weapons programme 1979-1989, voluntarily dismantled under "
            "de Klerk; only state to give up an indigenous weapons "
            "stockpile. Public IAEA disclosure 1993-1995."
        ),
    ),
    "argentina_pre_1991": HistoricalCase(
        name="argentina_pre_1991",
        state="AR",
        cut_off=date(1991, 7, 18),
        public_disclosure_event="Argentina-Brazil ABACC bilateral agreement (Guadalajara Declaration 1990; ABACC 1991)",
        expected_top_process="gaseous_diffusion",
        expected_pm_cells=("V03_E01", "V03_E04", "V03_E05"),
        minimum_lead_time_years=(5, 10),
        notes=(
            "Pilcaniyeu gaseous diffusion plant (CNEA); covert military "
            "programme 1978-1983, declared 1983 under Alfonsin; ABACC "
            "(Brazilian-Argentine Agency) safeguards from 1991. "
            "Publicly documented post-1991."
        ),
    ),
    "brazil_pre_1991": HistoricalCase(
        name="brazil_pre_1991",
        state="BR",
        cut_off=date(1991, 7, 18),
        public_disclosure_event="ABACC bilateral agreement; Brazil parallel-programme disclosure",
        expected_top_process="gas_centrifuge",
        expected_pm_cells=("V03_E01", "V03_E04", "V03_E05"),
        minimum_lead_time_years=(5, 10),
        notes=(
            "Aramar (CTMSP) ultracentrifuge programme — naval-propulsion "
            "cover for parallel military programme during military regime. "
            "Civilian re-direction post-1985; ABACC safeguards from 1991. "
            "Iperó facility publicly known."
        ),
    ),
    "taiwan_pre_1988": HistoricalCase(
        name="taiwan_pre_1988",
        state="TW",
        cut_off=date(1988, 1, 9),
        public_disclosure_event="Chang Hsien-yi defection to USA (1988-01); INER programme exposure",
        expected_top_process="research_reactor",
        expected_pm_cells=("V05_E01", "V05_E05", "V09_E01"),
        minimum_lead_time_years=(4, 8),
        notes=(
            "INER (Institute of Nuclear Energy Research) covert "
            "plutonium-route programme using TRR (Taiwan Research "
            "Reactor) heavy-water-moderated reactor + hot-cell research. "
            "Programme dismantled 1988 under US pressure following "
            "Chang Hsien-yi disclosure to CIA."
        ),
    ),
}


# --------------------------------------------------------------------------- #
#  Result + metrics
# --------------------------------------------------------------------------- #


@dataclass
class CaseResult:
    case_name: str
    hypotheses: list[ProcessHypothesis]
    top_process_match: bool
    top3_match: bool
    populated_cells: set[str]
    expected_cells: set[str]
    cells_recall: float
    posterior_top1: float
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "case": self.case_name,
            "top_process_match": self.top_process_match,
            "top3_match": self.top3_match,
            "cells_recall": round(self.cells_recall, 3),
            "posterior_top1": round(self.posterior_top1, 3),
            "populated_cells": sorted(self.populated_cells),
            "expected_cells": sorted(self.expected_cells),
            "n_hypotheses": len(self.hypotheses),
            "notes": self.notes,
        }


@dataclass
class ValidationMetrics:
    """Aggregate metrics across one or more cases."""
    top1_accuracy: float
    top3_accuracy: float
    mean_cells_recall: float
    mean_posterior_top1: float
    expected_calibration_error: float
    n_cases: int

    def to_dict(self) -> dict:
        return {k: (round(v, 4) if isinstance(v, float) else v)
                for k, v in self.__dict__.items()}


# --------------------------------------------------------------------------- #
#  Runner
# --------------------------------------------------------------------------- #


# Indicator collector signature: a function taking a HistoricalCase and
# returning a list of indicators. Phase 1 plugs in the literature
# heuristic; Phase 2 will plug in the VLM pipeline.
IndicatorCollector = Callable[[HistoricalCase], list[Indicator]]


def run_case(
    case: HistoricalCase,
    collector: IndicatorCollector,
    *,
    prior: float = 0.05,
    posterior_pass_threshold: float = 0.40,
) -> CaseResult:
    """Execute the pipeline on one case and report results."""
    indicators = list(collector(case))
    hypotheses = fuse(indicators, prior=prior)

    top_process = hypotheses[0].process if hypotheses else None
    top3 = {h.process for h in hypotheses[:3]}

    populated: set[str] = {ind.cell_id for ind in indicators}
    expected = set(case.expected_pm_cells)
    cells_recall = len(populated & expected) / len(expected) if expected else 0.0

    return CaseResult(
        case_name=case.name,
        hypotheses=hypotheses,
        top_process_match=top_process == case.expected_top_process,
        top3_match=case.expected_top_process in top3,
        populated_cells=populated,
        expected_cells=expected,
        cells_recall=cells_recall,
        posterior_top1=hypotheses[0].posterior if hypotheses else 0.0,
        notes=(
            "PASS" if hypotheses and hypotheses[0].posterior >= posterior_pass_threshold
            else "BELOW_THRESHOLD"
        ),
    )


def run_all(
    collector: IndicatorCollector,
    *,
    cases: list[HistoricalCase] | None = None,
    prior: float = 0.05,
) -> tuple[list[CaseResult], ValidationMetrics]:
    cases = cases if cases is not None else list(HISTORICAL_CASES.values())
    results = [run_case(c, collector, prior=prior) for c in cases]
    metrics = compute_metrics(results)
    return results, metrics


def compute_metrics(results: list[CaseResult]) -> ValidationMetrics:
    """Aggregate metrics over a set of case results."""
    if not results:
        return ValidationMetrics(0, 0, 0, 0, 0, 0)

    n = len(results)
    top1 = sum(1 for r in results if r.top_process_match) / n
    top3 = sum(1 for r in results if r.top3_match) / n
    recall = sum(r.cells_recall for r in results) / n
    post = sum(r.posterior_top1 for r in results) / n

    # Simple ECE: |posterior_top1 - top1_match| averaged across cases.
    # This is a 1-bin reliability estimate; finer binning in Phase 2.
    ece = sum(abs(r.posterior_top1 - (1.0 if r.top_process_match else 0.0))
              for r in results) / n

    return ValidationMetrics(
        top1_accuracy=top1,
        top3_accuracy=top3,
        mean_cells_recall=recall,
        mean_posterior_top1=post,
        expected_calibration_error=ece,
        n_cases=n,
    )


# --------------------------------------------------------------------------- #
#  Built-in collector — heuristic literature wrapper for Iran-Natanz
# --------------------------------------------------------------------------- #


def _heuristic_keyword_collector(
    case: HistoricalCase,
) -> list[Indicator]:
    """Phase-1 heuristic: query OpenAlex and run keyword strength rules.

    This delegates to ``scripts.natanz_retrofit`` helpers when run from a
    real environment. Falls back to an empty list when the script cannot
    be imported (e.g., in a test sandbox without network access).
    """
    if case.name != "iran_natanz_2002":
        # Phase-1 only wires Natanz; others return empty.
        return []
    try:
        from scripts.natanz_retrofit import (  # type: ignore[import-not-found]
            _heuristic_literature,
            query_iran_nuclear_papers,
        )
    except Exception:
        return []
    from pathlib import Path
    out_dir = Path("./data/natanz")
    out_dir.mkdir(parents=True, exist_ok=True)
    papers = query_iran_nuclear_papers(out_dir, 1990, case.cut_off.year)
    return _heuristic_literature(papers)


def heuristic_collector() -> IndicatorCollector:
    return _heuristic_keyword_collector


# --------------------------------------------------------------------------- #
#  Convenience: stub collector for tests
# --------------------------------------------------------------------------- #


def synthetic_collector(per_case_indicators: dict[str, list[Indicator]]) -> IndicatorCollector:
    """Build a collector that returns hard-coded indicators per case_name."""
    def _coll(case: HistoricalCase) -> list[Indicator]:
        return list(per_case_indicators.get(case.name, []))
    return _coll
