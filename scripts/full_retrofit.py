"""Run the full 4-case historical retrofit and report metrics.

Usage:
    python -m scripts.full_retrofit              # heuristic mode (no API)
    python -m scripts.full_retrofit --vlm        # VLM mode (requires key)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make project importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.case_collectors import combined_collector  # noqa: E402
from backend.app.modules.validator import (  # noqa: E402
    HISTORICAL_CASES,
    run_all,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("retrofit")


def main():
    p = argparse.ArgumentParser(description="Full 4-case retrofit")
    p.add_argument("--out", default="./data/retrofit", help="Output directory")
    p.add_argument("--vlm", action="store_true",
                   help="Use VLM mode (requires ANTHROPIC_API_KEY); not yet wired")
    p.add_argument("--prior", type=float, default=0.05)
    args = p.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    log.info("=" * 70)
    log.info("OS-PM Full Retrofit (4 cases)")
    log.info("VLM mode: %s", args.vlm)
    log.info("Prior: %.3f", args.prior)
    log.info("=" * 70)

    if args.vlm:
        log.warning("--vlm flag set but VLM-side collectors are not yet wired; "
                    "falling back to heuristic.")

    results, metrics = run_all(combined_collector, prior=args.prior)

    # Per-case detail
    print("\n" + "=" * 70)
    print("PER-CASE RESULTS")
    print("=" * 70)
    for r in results:
        case = HISTORICAL_CASES[r.case_name]
        print(f"\n[{r.case_name}] expected: {case.expected_top_process}")
        print(f"  top1_match : {r.top_process_match}")
        print(f"  top3_match : {r.top3_match}")
        print(f"  cells_recall : {r.cells_recall:.2f}")
        print(f"  posterior  : {r.posterior_top1:.3f}")
        print(f"  notes      : {r.notes}")
        if r.hypotheses:
            top = r.hypotheses[0]
            print(f"  top hypothesis : {top.process} (cells {top.cells})")

    print("\n" + "=" * 70)
    print("AGGREGATE METRICS (4 cases)")
    print("=" * 70)
    for k, v in metrics.to_dict().items():
        print(f"  {k:32s} : {v}")

    # JSON output
    report = {
        "vlm_mode": args.vlm,
        "prior": args.prior,
        "results": [r.to_dict() for r in results],
        "metrics": metrics.to_dict(),
    }
    report_path = out_dir / "full_retrofit_report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False),
                           encoding="utf-8")
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()
