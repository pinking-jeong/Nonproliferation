# OS-PM — Open-Source Reconstruction of the IAEA Physical Model

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/pinking-jeong/Nonproliferation/actions/workflows/test.yml/badge.svg)](https://github.com/pinking-jeong/Nonproliferation/actions/workflows/test.yml)
[![pytest 57/57](https://img.shields.io/badge/pytest-57%2F57-brightgreen)](tests/)
[![PM cells 88/88](https://img.shields.io/badge/PM%20cells-88%2F88%20in--scope-brightgreen)](pm_schema/)
[![arXiv](https://img.shields.io/badge/arXiv-pending-lightgrey.svg)](paper/main.tex)

> **OS-PM is an open-source academic reconstruction of the IAEA Physical Model.** It populates 88 in-scope element cells from publicly licensed data (Sentinel-2/Landsat imagery, OpenAlex literature, UN COMTRADE trade flows, EURDEP environmental sampling) and runs the full Acquisition Path Analysis pipeline as a graph. Volume 11 (weaponization) is **permanently excluded** by schema-level policy.

> ⚠️ **Academic / detection-only use.** This system does not produce operational safeguards conclusions. Weaponization indicators (PM Vol. 11) are out of scope by design and oversight.

🇰🇷 [한국어 README](README.ko.md)

---

## What this is

The IAEA Physical Model (PM), developed by Liu & Morsy (1999) under Programme 93+2, is the technical backbone of state-level nuclear safeguards: a 12-volume × 8-element-per-process matrix mapping observable indicators (equipment, materials, R&D, environmental signatures, auxiliary infrastructure) to fuel-cycle processes. The PM itself remains in restricted IAEA technical-report distribution. Only two academic groups — JRC Ispra (Cojazzi/Renda) and Forschungszentrum Jülich (Niemeyer) — have published partial reconstructions.

OS-PM is the first end-to-end, multimodal, reproducible academic system that re-creates the PM from open-licensed sources alone, with a vision-language model layer (Claude via OpenRouter or Anthropic direct) for indicator extraction.

## Why open source

Detection-side methodology should be auditable. Operational details should not be. OS-PM threads this needle:

- **In scope** ✅ — detection of state-level fuel-cycle activity from open sources, historical retrofit cases, advisory-committee oversight, Apache-2.0 release
- **Out of scope** 🚫 — Volume 11 weaponization, operational sanctions/strikes, classified data, in-progress / undisclosed cases

See [`pm_schema/V11_weaponization_excluded/_volume_overview.yaml`](pm_schema/V11_weaponization_excluded/_volume_overview.yaml) for the formal exclusion stub and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the scope policy.

## At a glance

| Layer | Component | Status |
|-------|-----------|--------|
| Schema | 88 in-scope element cells across 11 volumes | ✅ 100 % |
| Module A | Image understanding (VLM, RAG-augmented) | ✅ live |
| Module B | Document mining (OpenAlex + VLM classification) | ✅ live |
| Module C | Confidence-weighted Bayesian fusion | ✅ live |
| Module D | Strength estimator (Cooke method + baseline) | ✅ live |
| Module E | APA graph (NetworkX, k-shortest path, risk score) | ✅ live |
| Module F | Historical retrofit validator (4 canonical cases) | ✅ live |
| Backend | FastAPI, 13 endpoints | ✅ live |
| Frontend | Streamlit, 3-tab demo | ✅ live |
| Tests | pytest | ✅ 57 / 57 |
| Imagery | Sentinel-2 / Landsat / Sentinel-3 SLSTR (STAC) | ✅ live |
| VLM | OpenRouter primary, Anthropic direct fallback | ✅ live |

## Quick start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/pinking-jeong/Nonproliferation.git
cd Nonproliferation

# 2. Install
python -m venv .venv && .venv/bin/activate          # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env and set ONE of:
#   OPENROUTER_API_KEY=sk-or-v1-...   (recommended — single key, no console.anthropic.com)
#   ANTHROPIC_API_KEY=sk-ant-api03-... (direct path; supports prompt caching)

# 4. Test (no key required)
pytest tests/ -v

# 5. Run live retrofit on Iran-Natanz
python -m scripts.natanz_retrofit --vlm        # with VLM (~$0.20)
python -m scripts.natanz_retrofit --no-vlm     # heuristic only (free)

# 6. (Optional) launch FastAPI + Streamlit demo
bash scripts/launch_demo.sh
# → backend at http://127.0.0.1:8000  (docs at /docs)
# → frontend at http://127.0.0.1:8501
```

See [`docs/API_key_setup_guide.md`](docs/API_key_setup_guide.md) for the full credential decision tree (OpenRouter / Anthropic / Claude for Science).

## Headline result

Phase 1, four-case historical retrofit (Iran-Natanz 2002, Libya 2003, Iraq pre-1991, Syria-Al-Kibar 2007):

| Mode | Top-1 acc. | Mean post. | Iran-Natanz post. |
|------|-----------|-----------|-------------------|
| Heuristic only | 1.00 | 0.291 | 0.492 (false-positive driven) |
| **VLM live (OpenRouter)** | **1.00** | **0.182** | **0.058** (calibrated) |

The VLM upgrade correctly removed the heuristic's geocentrifuge false positive — a textbook demonstration of why semantic, abstract-level filtering matters. See `paper/main.tex` §5 for the full ablation.

## Repository layout

```
ospm/
├── backend/app/                  FastAPI + 6 modules + Pydantic schemas
├── frontend/app.py               Streamlit demo
├── pm_schema/                    100 YAML cells (V01-V12; V11 = exclusion stub)
├── scripts/                      runners (retrofit, ablation, imagery, gnn-lite)
├── tests/                        57 pytest tests
├── docs/
│   ├── API_key_setup_guide.md           OpenRouter / Anthropic / C4S decision tree
│   ├── Claude_for_Science_application.md
│   ├── IRB_application_draft.md
│   ├── PI_demo_deck.md                  7-slide outreach
│   ├── outreach/                        per-PI email templates (en + ko)
│   └── advisory/                        committee charter + agenda + recruitment
├── paper/                        arXiv preprint LaTeX (11 pages)
├── arxiv_submission/             built tarballs ready to upload
├── .github/                      CI workflow + issue/PR templates
├── LICENSE                       Apache-2.0
├── NOTICE                        attribution + V11 exclusion notice
├── CITATION.cff                  citation metadata (CFF 1.2)
├── CHANGELOG.md
├── CONTRIBUTING.md               scope policy
└── CODE_OF_CONDUCT.md            Contributor Covenant 2.1
```

## Roadmap

- ✅ **Phase 1** (released v0.1.0, 2026-05-11) — schema, six modules, four-case retrofit, dual-VLM backend, arXiv preprint draft
- ⏳ **Phase 2** — full-resolution Sentinel-2 COG pipeline, expanded retrofit set with realistic peaceful-programme negatives, Cooke-method expert elicitation
- ⏳ **Phase 3** — community contributions, additional volumes (V01/V02/V08/V10 already shipped, deeper coverage), translation to other PM-rooted methodologies

## How to cite

If you use OS-PM in your work, please cite both the system and the upcoming preprint. Machine-readable metadata is in [`CITATION.cff`](CITATION.cff).

```bibtex
@software{os_pm_2026,
  title        = {{OS-PM}: Open-Source Reconstruction of the {IAEA} Physical Model},
  author       = {OS-PM Authors},
  year         = {2026},
  url          = {https://github.com/pinking-jeong/Nonproliferation},
  version      = {0.1.0},
  license      = {Apache-2.0},
}
```

The companion preprint (arXiv ID forthcoming) is in `paper/main.tex`.

## Contributing

We welcome contributions that respect the scope policy. See [`CONTRIBUTING.md`](CONTRIBUTING.md). All changes touching the schema, the V11 exclusion stub, or the validator's case definitions require advisory-committee review.

## License

[Apache-2.0](LICENSE) — see also [`NOTICE`](NOTICE) for the attribution and V11 exclusion clause.

## Acknowledgments

Methodological foundations: Liu & Morsy (1999); JRC Ispra (Renda, Kim, Jungwirth, Cojazzi, 2014/2015); Forschungszentrum Jülich (Listner, Niemeyer, Rezniczek, 2013; Allen et al., 2021); Sandia (Gastelum, 2024); INL (Elliott et al., 2023). Full bibliography in [`paper/references.bib`](paper/references.bib).

The advisory committee (Chair / AI / GIS / Policy / Ethics) is being formed; see [`docs/advisory/charter.md`](docs/advisory/charter.md).

---

**This project is for academic detection-side research only. Volume 11 (weaponization) is permanently excluded.**
