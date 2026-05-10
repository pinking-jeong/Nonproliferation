# OS-PM — Academic Collaboration Brief

**Audience:** Prof. Man-Sung Yim (KAIST 핵·양자공학과) · Dr. Lance K. Kim (KAERI / 전 JRC) · 그리고 안전조치 학술 커뮤니티
**Format:** 7-slide markdown deck (Marp / Slidev 호환). PDF 변환은 `marp PI_demo_deck.md -o PI_demo_deck.pdf`
**Last updated:** 2026-05-09
**Status:** v0.1 draft for outreach. PI 정보는 placeholder; 실제 발송 전 확정 필요.

---

## Slide 1 — Title

# OS-PM
### Open-Source Reconstruction of the IAEA Physical Model
### A VLM-native, reproducible, academic system

**[Author 1]** · [Institution]
**[Author 2]** · [Institution]
**Advisory committee:** TBD

📁 GitHub: `[org]/os-pm` (Apache-2.0)
📄 Preprint: `arXiv:[TBD]`
📅 Phase 1 complete (2026-05-09); Phase 2 starting

---

## Slide 2 — Why we built it

> **The IAEA Physical Model is the technical backbone of state-level safeguards, but it is opaque to academia.** Liu & Morsy (1999) defined a 12-volume, 8-element-per-process indicator matrix that informs every Acquisition Path Analysis. The original schema lives in restricted IAEA STR reports; only two academic groups (JRC Ispra under Cojazzi/Renda; FZ-Jülich under Niemeyer) have published partial reconstructions.

### Question
*What can be rebuilt from open-licensed sources alone, and how good is it?*

### Why now
- VLMs (Claude 4.6, GPT-4o, Qwen2.5-VL) make multimodal indicator extraction feasible end-to-end
- OpenAlex / UN COMTRADE / Sentinel-2 all openly licensed
- JRC's Big Table provides a schema target; Sandia / INL provide CV training data

---

## Slide 3 — Architecture (5 layers, 6 modules)

```
┌──────────────────────────────────────────────────┐
│ ① Data ingestion                                  │
│    Sentinel/Landsat │ OpenAlex │ COMTRADE │ EURDEP │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ ② Pre-processing  (COG, STAC, HS-code, OCR)      │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ ③ VLM core    Claude 4.6 ∥ Qwen2.5-VL-72B (RAG)  │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ ④ Indicator extraction (Modules A · B · C · D)   │
│    A image · B doc · C fusion · D strength       │
└────────────────┬─────────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────────┐
│ ⑤ APA Graph (E) + Validator (F) + UI             │
└──────────────────────────────────────────────────┘
```

**All 6 modules implemented and tested in Phase 1** (29 unit tests passing).

---

## Slide 4 — PM Schema (88 / 88 in-scope cells)

| Volume                        | Element coverage | Volume coverage         |
| ----------------------------- | ---------------- | ----------------------- |
| V01 Mining/Milling            | 8/8              | ✅ 9 YAML                |
| V02 Conversion                | 8/8              | ✅ 9 YAML                |
| V03 Enrichment                | 8/8              | ✅ 9 YAML                |
| V04 Fuel Fabrication          | 8/8              | ✅ 9 YAML                |
| V05 Reactor Operation         | 8/8              | ✅ 9 YAML                |
| V06 Heavy Water               | 8/8              | ✅ 9 YAML                |
| V07 Reprocessing              | 8/8              | ✅ 9 YAML                |
| V08 Spent Fuel/Waste          | 8/8              | ✅ 9 YAML                |
| V09 R&D / Hot Cells           | 8/8              | ✅ 9 YAML                |
| V10 Direct handling (limited) | 8/8              | ✅ 9 YAML                |
| **V11 Weaponization**         | **0/8**          | 🚫 **policy stub only** |
| V12 Cross-cutting             | 8/8              | ✅ 9 YAML                |

- **88 / 88 in-scope element cells = 100%**
- All cells YAML-validated, served live via FastAPI
- Vol.~11 permanently excluded; redaction flags in V03/V07/V10

---

## Slide 5 — Phase 1 results (4 historical retrofits)

| Case | Cut-off | Top-1 match | Posterior | Notes |
|------|---------|-------------|-----------|-------|
| Iran-Natanz | 2002-08-14 | ✅ | 0.49 | NCRI disclosure baseline |
| Libya | 2003-12-19 | ✅ | 0.24 | A.Q. Khan procurement bundle |
| Iraq pre-1991 | 1991-04-03 | ✅ | 0.22 | Calutron + centrifuge |
| Syria-Al-Kibar | 2007-09-05 | ✅ | 0.22 | Graphite reactor |
| **Macro** | — | **1.00** | **0.29** | **ECE 0.71** |

### Honest findings
- **Top-1 = 1.0 across all four cases** — heuristic + Bayesian fusion ranks correctly
- **Posteriors stay near prior** — only 1-3 indicators per case, calibration weak
- **GNN-light LOO = 1.0** (gradient boosting), but with synthetic negatives — caveat in §5.4
- **Iran-Natanz heuristic false-positive on geophysical "centrifuge"** — motivates VLM upgrade

---

## Slide 6 — What we want from this collaboration

### From Prof. Yim (KAIST)
- **Methodological review** of the OS-PM schema mapping (does it cover what KAIST's nuclear engineering curriculum considers Phase-1 critical?)
- **Co-author on the system paper** if the project lines up with your group's nonproliferation policy / latency analysis stream
- **KAIST IRB pathway** — would your IRB accept this as a dual-use research project, or do we need an external committee?

### From Dr. Lance Kim (KAERI / 전 JRC)
- **JRC Big Table compatibility** — does the YAML schema interoperate with the JRC tabular structure? Can we publish a mapping?
- **Validation ladder** — your 2014/2015 OSINT-for-APA papers are foundational for this; we cite them and would love a methodological audit
- **KAERI co-PI role** — particularly for the V09 R&D / Hot Cells cells; KAERI PRIDE is one of the publicly-cited civilian R&D references

### From the wider community
- **Negatives** — declared peaceful programmes (KR, JP, EU NPT-AP-BC states) for honest-class GNN training
- **Imagery datasets** — Sandia CGI license, INL change-detection corpus
- **Validation cases** — expanding beyond the canonical four to e.g. Argentina/Brazil 1980s, South Africa pre-1989

---

## Slide 7 — Ethical scope (non-negotiable)

### What OS-PM does
- ✅ **Detection** of state-level fuel-cycle activity from open sources
- ✅ **Reproducible** schema and pipeline (all releases Apache-2.0)
- ✅ **Historical** validation — only on already-disclosed cases

### What OS-PM does NOT do
- 🚫 **Vol.~11 weaponization** — permanently excluded by schema and policy
- 🚫 **Operational sanctions / strikes** — purely academic detection research
- 🚫 **Classified data** — 100% open licenses (Sentinel CC BY, OpenAlex CC0, COMTRADE Open Data)
- 🚫 **In-progress cases** — only post-disclosure analysis

### Oversight
- Advisory committee (5 members; 1 chair + 2 technical + 1 policy + 1 ethics)
- Institutional IRB + DURC (dual-use research of concern) review
- KOSTI (전략물자관리원) sanity check before code release

### Asks
1. 30-min meeting (online or in-person at KAIST/KAERI Daejeon)
2. Optional: review of the arXiv preprint draft (8 pages, attached)
3. Optional: co-PI letter (we can adapt)

---

## Appendix A — Repo and reproducibility

```bash
git clone https://github.com/[org]/os-pm
cd os-pm
pip install -r requirements.txt

# Tests (29/29 PASS, no API key needed)
pytest tests/

# Live demo
bash scripts/launch_demo.sh
# → backend at :8000 (FastAPI docs at /docs)
# → frontend at :8501 (Streamlit)

# 4-case retrofit
python -m scripts.full_retrofit
# → data/retrofit/full_retrofit_report.json
```

## Appendix B — Citations expected from this brief

- Liu Z., Morsy S. (1999). Development of the Physical Model. IAEA-SM-367.
- Renda G., Kim L., Jungwirth R., Cojazzi G.G.M. (2014). The potential of open source information in supporting Acquisition Pathway Analysis to design IAEA State Level Approaches. IAEA-CN-220.
- Renda G., Kim L. K., Cojazzi G. (2015). Methodological aspects on the IAEA State Level Concept and related Acquisition Path Analysis. JRC.
- Listner C., Niemeyer I., Rezniczek A. (2013). Approaching acquisition path analysis formally. INMM/ESARDA.
- Gastelum Z. (2024). Computer-Generated Imagery Dataset for International Nuclear Safeguards. ESARDA Bulletin 2023(5). DOI:10.3011/esarda.ijnsnp.2023.5
- Schoeppner M., Glaser A. (2016). Krypton-85 detection of clandestine reprocessing plants. J. Environ. Radioact.
- IAEA (2014). GOV/2014/41 Supplementary Document on State-Level Safeguards Implementation.
- Cooke R. M. (1991). Experts in Uncertainty. OUP.

## Appendix C — Bilingual abstract (한국어)

본 시스템은 IAEA Physical Model을 공개정보 기반으로 부분 재구성하여 학술 안전조치 연구에 활용 가능한 도구를 제공한다. 88개 셀의 YAML 스키마, 6개 분석 모듈 (이미지·문서·융합·강도·APA·검증), 4개 역사적 사례 (이라크·리비아·시리아·이란-나탄즈) 검증을 Phase 1에서 완료했다. Phase 2에서는 VLM 통합·이미지 모달리티 강화·정상 비교군 확보로 정확도를 정량화한다.

**협력 요청 (요약):**
1. KAIST/KAERI 자문위 참여 가능성 검토
2. JRC Big Table 호환성 의견
3. arXiv preprint 사전 검토 (선택)

---

**문서 종료.** PDF 변환: `marp --html PI_demo_deck.md -o PI_demo_deck.pdf` (Marp Cli 필요).
