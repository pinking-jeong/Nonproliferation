# OS-PM — IAEA Physical Model 의 공개정보 기반 학술 재구성

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/pinking-jeong/Nonproliferation/actions/workflows/test.yml/badge.svg)](https://github.com/pinking-jeong/Nonproliferation/actions/workflows/test.yml)
[![pytest 57/57](https://img.shields.io/badge/pytest-57%2F57-brightgreen)](tests/)
[![PM cells 88/88](https://img.shields.io/badge/PM%20cells-88%2F88%20in--scope-brightgreen)](pm_schema/)

> **OS-PM 은 IAEA Physical Model 의 학술적 공개 재구성 시스템입니다.** Sentinel-2/Landsat 위성영상, OpenAlex 학술문헌, UN COMTRADE 무역데이터, EURDEP 환경방사선 데이터 등 100% 공개 라이센스 데이터로 88개 in-scope 셀을 채우고, Acquisition Path Analysis (APA) 파이프라인을 그래프 기반으로 실행합니다. **Volume 11 (weaponization) 은 schema 차원에서 영구 제외**됩니다.

> ⚠️ **학술·detection-only 목적.** 본 시스템은 운영적 사찰결정을 산출하지 않으며 weaponization 지표 (PM Vol. 11) 는 의도적으로 범위 밖입니다.

🇬🇧 [English README](README.md)

---

## 무엇인가

IAEA Physical Model (PM) 은 1999년 Liu & Morsy 가 Programme 93+2 의 일환으로 개발한 핵 안전조치의 기술적 backbone 입니다. 12 volumes × 8 elements per process 매트릭스로 핵연료주기의 모든 관측 가능한 indicator (장비, 재료, R&D, 환경 시그니처, 보조 인프라) 를 process 에 매핑합니다. PM 원본은 IAEA 의 비공개 STR (Safeguards Technical Report) 시리즈에 머물러 있으며, JRC Ispra (Cojazzi/Renda) 와 Forschungszentrum Jülich (Niemeyer) 두 학술 그룹만이 부분적 재구성을 발표한 바 있습니다.

OS-PM 은 공개 라이센스 데이터만으로 PM 을 end-to-end 재구성하는 **최초의 멀티모달·재현가능 학술 시스템**입니다. Vision-language model (Claude via OpenRouter / Anthropic 직접) 이 indicator 추출을 담당합니다.

## 왜 오픈소스인가

Detection 측면 방법론은 검증가능해야 하며, operational 디테일은 그래선 안 됩니다. OS-PM 은 두 원칙을 동시에 만족시킵니다:

- **In scope ✅** — 공개 정보로부터의 국가단위 핵연료주기 활동 detection, 역사적 retrofit 사례, 자문위원회 감독, Apache-2.0 공개
- **Out of scope 🚫** — Vol. 11 weaponization, 운영적 제재·타격, 분류 자료, 진행 중·미공개 사례

상세는 [`pm_schema/V11_weaponization_excluded/_volume_overview.yaml`](pm_schema/V11_weaponization_excluded/_volume_overview.yaml) 의 공식 제외 stub 과 [`CONTRIBUTING.md`](CONTRIBUTING.md) 의 scope policy 를 참조하십시오.

## 한눈에 보는 진행상황

| 계층 | 구성요소 | 상태 |
|-----|---------|-----|
| 스키마 | 11 volumes × 8 elements = 88 in-scope 셀 | ✅ 100 % |
| Module A | Image understanding (VLM, RAG-augmented) | ✅ live |
| Module B | Document mining (OpenAlex + VLM 분류) | ✅ live |
| Module C | Confidence-weighted Bayesian fusion | ✅ live |
| Module D | Strength estimator (Cooke method + baseline) | ✅ live |
| Module E | APA graph (NetworkX, k-shortest path, risk score) | ✅ live |
| Module F | 역사적 retrofit validator (4 case) | ✅ live |
| 백엔드 | FastAPI, 13 endpoints | ✅ live |
| 프런트 | Streamlit, 3-tab demo | ✅ live |
| 테스트 | pytest | ✅ 57 / 57 |
| 위성영상 | Sentinel-2 / Landsat / Sentinel-3 SLSTR (STAC) | ✅ live |
| VLM | OpenRouter 우선, Anthropic 직접 fallback | ✅ live |

## 5분 빠른 시작

```bash
# 1. 클론
git clone https://github.com/pinking-jeong/Nonproliferation.git
cd Nonproliferation

# 2. 의존성
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt

# 3. 환경설정
cp .env.example .env
# .env 편집하여 다음 중 하나 등록:
#   OPENROUTER_API_KEY=sk-or-v1-...   (권장 — 단일 키, 별도 console.anthropic.com 불필요)
#   ANTHROPIC_API_KEY=sk-ant-api03-... (직접 — prompt caching 90% 절감)

# 4. 테스트 (키 불필요)
pytest tests/ -v

# 5. Iran-Natanz 라이브 retrofit
python -m scripts.natanz_retrofit --vlm        # VLM 모드 (~$0.20)
python -m scripts.natanz_retrofit --no-vlm     # 휴리스틱 모드 (무료)

# 6. (선택) FastAPI + Streamlit 데모
bash scripts/launch_demo.sh
# → 백엔드 http://127.0.0.1:8000  (docs at /docs)
# → 프런트 http://127.0.0.1:8501
```

API 키 발급·등록 절차는 [`docs/API_key_setup_guide.md`](docs/API_key_setup_guide.md) (OpenRouter / Anthropic / Claude for Science 의사결정 트리) 참조.

## 핵심 결과

Phase 1, 4-case 역사 retrofit (이란-나탄즈 2002, 리비아 2003, 이라크 pre-1991, 시리아-알키바르 2007):

| 모드 | Top-1 정확도 | 평균 posterior | Iran-Natanz posterior |
|------|-----------|------------|------------------|
| 휴리스틱 단독 | 1.00 | 0.291 | 0.492 (false-positive 인플레) |
| **VLM 라이브 (OpenRouter)** | **1.00** | **0.182** | **0.058** (calibrated) |

VLM 활성화로 휴리스틱의 *geocentrifuge* false-positive (지질공학 논문 오매칭) 가 정확히 제거되었습니다 — 이는 abstract-level 의미 분류가 왜 필요한지의 교과서적 사례입니다. 상세는 `paper/main.tex` §5.

## 디렉토리 구조

```
ospm/
├── backend/app/                  FastAPI + 6개 모듈 + Pydantic 스키마
├── frontend/app.py               Streamlit 데모
├── pm_schema/                    100 YAML 셀 (V01-V12, V11 = 정책 stub)
├── scripts/                      runner (retrofit, ablation, imagery, gnn-lite)
├── tests/                        57 pytest 테스트
├── docs/
│   ├── API_key_setup_guide.md           OpenRouter / Anthropic / C4S
│   ├── Claude_for_Science_application.md 학술 크레딧 신청서 초안
│   ├── IRB_application_draft.md          기관 윤리위 신청 양식
│   ├── PI_demo_deck.md                   7-slide 학술 협력 brief
│   ├── outreach/                         PI 별 이메일 템플릿 (한·영)
│   └── advisory/                         자문위 charter + 첫 회의 의제 + 영입 템플릿
├── paper/                        arXiv preprint LaTeX (11페이지)
├── arxiv_submission/             빌드된 tar.gz (제출 대기)
├── outreach_pkg/                 사적 회람 패키지 (Yim 교수 / Lance Kim 박사)
├── .github/                      CI workflow + issue/PR templates
├── LICENSE                       Apache-2.0
├── NOTICE                        attribution + V11 제외 명시
├── CITATION.cff                  citation 메타데이터 (CFF 1.2)
├── CHANGELOG.md
├── CONTRIBUTING.md               scope policy
└── CODE_OF_CONDUCT.md            Contributor Covenant 2.1
```

## 로드맵

- ✅ **Phase 1** (v0.1.0 출시, 2026-05-11) — 스키마, 6개 모듈, 4-case retrofit, dual-VLM 백엔드, arXiv preprint 초안
- ⏳ **Phase 2** — 풀-해상도 Sentinel-2 COG 파이프라인, 실제 평화이용 국가 negative 확대 retrofit, Cooke method 전문가 elicitation
- ⏳ **Phase 3** — 커뮤니티 기여, 추가 PM 변형 (V01/V02/V08/V10 이미 구현, 깊이 확장), 다른 PM-rooted 방법론으로 이식

## 인용 방법

OS-PM 을 사용하시는 경우 시스템과 곧 발표될 preprint 모두 인용해 주십시오. 기계 가독 메타데이터는 [`CITATION.cff`](CITATION.cff) 에 있습니다.

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

동반 preprint (arXiv ID 추후 부여) 는 `paper/main.tex` 에 있습니다.

## 기여 안내

scope policy 를 존중하는 기여를 환영합니다. [`CONTRIBUTING.md`](CONTRIBUTING.md) 참조. 스키마, V11 제외 stub, validator 의 case 정의를 변경하는 PR 은 자문위 검토가 필요합니다.

## 라이센스

[Apache-2.0](LICENSE) — attribution 과 V11 제외 조항은 [`NOTICE`](NOTICE) 도 참조.

## 감사의 말

방법론적 토대: Liu & Morsy (1999); JRC Ispra (Renda, Kim, Jungwirth, Cojazzi, 2014/2015); Forschungszentrum Jülich (Listner, Niemeyer, Rezniczek, 2013; Allen et al., 2021); Sandia (Gastelum, 2024); INL (Elliott et al., 2023). 전체 참고문헌은 [`paper/references.bib`](paper/references.bib).

자문위원회 (Chair / AI / GIS / Policy / Ethics) 는 구성 중 — [`docs/advisory/charter.md`](docs/advisory/charter.md) 참조.

---

**본 프로젝트는 학술 detection-only 연구 전용입니다. Volume 11 (weaponization) 은 영구 제외됩니다.**
