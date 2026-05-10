"""Phase 2 ablation runner: heuristic vs VLM, side-by-side report.

When ANTHROPIC_API_KEY is set, this runs both modes and emits a
comparison JSON suitable for paper §5.4. Without the key, it runs only
the heuristic and labels the VLM column as ``api_key_pending``.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.config import get_settings  # noqa: E402
from backend.app.modules.case_collectors import combined_collector  # noqa: E402
from backend.app.modules.case_collectors_vlm import (  # noqa: E402
    _vlm_available,
    vlm_collector,
)
from backend.app.modules.validator import run_all  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("phase2-ablation")


def main():
    s = get_settings()
    get_settings.cache_clear()
    s = get_settings()
    has_key = _vlm_available()
    backend = ("openrouter" if s.openrouter_api_key
               else "anthropic" if s.anthropic_api_key
               else "none")
    log.info("VLM credential present: %s (backend=%s)", has_key, backend)

    log.info("Running heuristic mode ...")
    h_results, h_metrics = run_all(combined_collector)

    if has_key:
        log.info("Running VLM mode ...")
        v_results, v_metrics = run_all(vlm_collector)
        vlm_out = {
            "results": [r.to_dict() for r in v_results],
            "metrics": v_metrics.to_dict(),
        }
    else:
        log.warning("VLM mode skipped - no OPENROUTER_API_KEY or ANTHROPIC_API_KEY.")
        vlm_out = {"status": "api_key_pending"}

    out = {
        "heuristic": {
            "results": [r.to_dict() for r in h_results],
            "metrics": h_metrics.to_dict(),
        },
        "vlm": vlm_out,
        "vlm_available": has_key,
    }
    out_dir = Path("./data/retrofit")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "phase2_ablation.json").write_text(
        json.dumps(out, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("PHASE 2 ABLATION SUMMARY")
    print("=" * 70)
    print(f"Heuristic top1={h_metrics.top1_accuracy:.3f}  ECE={h_metrics.expected_calibration_error:.3f}")
    if has_key:
        print(f"VLM       top1={v_metrics.top1_accuracy:.3f}  "
              f"ECE={v_metrics.expected_calibration_error:.3f}")
    else:
        print("VLM       <pending API key>")
    print(f"\nReport: {out_dir / 'phase2_ablation.json'}")


if __name__ == "__main__":
    main()
