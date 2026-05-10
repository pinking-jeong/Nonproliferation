"""Run GNN-light leave-one-out evaluation on the 4 historical cases.

Uses the case_collectors module to gather real (heuristic) indicators
per case, builds a graph per case, and runs LOO cross-validation.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.modules.apa_graph import build_default_graph  # noqa: E402
from backend.app.modules.case_collectors import combined_collector  # noqa: E402
from backend.app.modules.gnn_lite import train_evaluate_loo  # noqa: E402
from backend.app.modules.validator import HISTORICAL_CASES  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("gnn-lite")


def main():
    cases = []
    for case in HISTORICAL_CASES.values():
        log.info("Collecting indicators for %s", case.name)
        indicators = combined_collector(case)
        log.info("  → %d indicators", len(indicators))
        graph = build_default_graph()
        cases.append((graph, f"State_{case.state}_{case.name}", indicators))

    print("\n" + "=" * 70)
    print("GNN-LIGHT LEAVE-ONE-OUT EVALUATION (logistic regression)")
    print("=" * 70)
    out_lr = train_evaluate_loo(cases, classifier="logreg")
    for k, v in out_lr.items():
        if k == "fold_results":
            print(f"  {k}:")
            for f in v:
                print(f"    held-out {f['held_out_state'][:30]:30s}  "
                      f"p_pos={f['p_positive_pos']:.3f}  "
                      f"p_neg={f['p_positive_neg']:.3f}  "
                      f"correct: {f['correct_pos'] and f['correct_neg']}")
        elif k == "feature_names":
            print(f"  {k}: {v}")
        else:
            print(f"  {k}: {v}")

    print("\n" + "=" * 70)
    print("GNN-LIGHT LEAVE-ONE-OUT EVALUATION (gradient boosting)")
    print("=" * 70)
    out_gbm = train_evaluate_loo(cases, classifier="gbm")
    for k, v in out_gbm.items():
        if k == "fold_results":
            continue
        if k == "feature_names":
            continue
        print(f"  {k}: {v}")

    out_path = Path("./data/retrofit/gnn_lite_loo.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"logreg": out_lr, "gbm": out_gbm}, indent=2),
                        encoding="utf-8")
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
