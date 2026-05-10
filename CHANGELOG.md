# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Optional Phase 2 imagery pipeline (`scripts/imagery_phase2.py`)
- VLM-mode collectors with mock-tested fallback path

### Changed
- (placeholder for changes pending v0.2.0)

## [0.1.0] — 2026-05-09

First public release of the OS-PM Phase 1 system. Scope: Apache-2.0
academic preprint companion.

### Added
- 88 in-scope PM element cells across 11 volumes (V01–V10, V12) plus
  12 volume-overview YAMLs and 1 V11 exclusion-policy stub
- Six analysis modules:
  - A: Image understanding (VLM-driven, RAG-augmented)
  - B: Document mining (OpenAlex literature classification)
  - C: Cross-modal Bayesian fusion (confidence-weighted log-LR)
  - D: Strength estimator (Cooke method + Bayesian baseline)
  - E: APA graph (NetworkX, k-shortest path, risk score)
  - F: Historical retrofit validator (4 canonical cases)
- 13 FastAPI endpoints: `/health`, `/pm/cells`, `/analyze/image`,
  `/analyze/literature`, `/fuse`, `/apa/stats`, `/apa/paths`,
  `/apa/risk`, `/apa/export/cytoscape`, `/apa/export/graphml`,
  `/validate/cases`, `/validate/run`, `/validate/run_all`
- Streamlit demo UI (`frontend/app.py`) and launch helpers
- 37 unit tests (fusion / strength / APA graph / APA export /
  GNN-light / validator / VLM collector)
- arXiv preprint manuscript (`paper/main.tex`) and submission bundle
  builder (`paper/build_arxiv_bundle.py`)
- IRB application draft, PI candidates research, API key setup guide,
  PI demo deck, submission checklist, cover note
- GNN-light risk scorer with leave-one-out evaluation harness

### Changed
- Bayesian fusion likelihood ratios calibrated against retrofit cases
  (strong $8\!\times$, medium $2.5\!\times$, weak $1.3\!\times$)
- PMCell schema relaxed (`extra='allow'`) to accommodate volume-
  specific dialects in YAML cells

### Excluded (scope policy)
- IAEA Physical Model Volume 11 (Weaponization) — replaced with an
  exclusion-policy stub. See `pm_schema/V11_weaponization_excluded/`.

### Known limitations
- Mean posterior on 4-case retrofit is 0.29 with ECE 0.71. Phase 2
  imagery and trade modalities are designed to lift calibration into
  the decision range.
- GNN-light evaluation uses synthetic indicator-stripped negatives;
  realistic peaceful-programme negatives are a Phase 2 task.
- VLM mode requires `ANTHROPIC_API_KEY`; the heuristic fallback is
  documented as the lower bound in §5.4 of the paper.
