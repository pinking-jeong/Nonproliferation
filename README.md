# OS-PM: Open-Source Physical Model

VLM-based prototype implementing IAEA Physical Model from open sources for academic research on nuclear safeguards.

> ⚠️ **Academic / research use only.** This system does not produce operational safeguards conclusions. Weaponization indicators (PM Vol. 11) are intentionally out of scope.

## Quick Start

```bash
# 1. Install
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# edit .env, add ANTHROPIC_API_KEY

# 3. Run backend
uvicorn backend.app.main:app --reload --port 8000

# 4. Run frontend (new terminal)
streamlit run frontend/app.py
```

## Architecture

```
ospm/
├── backend/                 FastAPI server
│   └── app/
│       ├── main.py          API entry point
│       ├── config.py        env / settings
│       ├── schemas/         Pydantic models
│       └── modules/
│           ├── vlm_client.py        Claude / GPT-4o / Qwen wrapper
│           ├── pm_loader.py         load PM YAML schema
│           ├── image_module.py      Module A: image understanding
│           ├── document_module.py   Module B: lit + trade mining
│           ├── fusion_module.py     Module C: cross-modal Bayesian
│           ├── strength_module.py   Module D: strength estimator
│           ├── apa_graph.py         Module E: APA graph
│           └── validator.py         Module F: historical retrofit
├── frontend/                Streamlit demo
├── pm_schema/               PM 12×8 cell YAMLs
├── scripts/                 PoC notebooks / runners
├── tests/                   pytest
├── docs/                    additional docs
└── paper/                   arXiv preprint LaTeX
```

## Status

- [x] Phase 0: project skeleton
- [ ] Phase 1: MVP (Natanz retrofit)
- [ ] Phase 2: Beta (5 processes)
- [ ] Phase 3: v1.0 (12 volumes)

See `../VLM 기반 OS-PM 프로토타입 설계안.md` for full design.

## License

Apache 2.0 (placeholder — confirm with PI before publishing)
