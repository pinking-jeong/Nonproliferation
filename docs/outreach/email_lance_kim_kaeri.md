# Outreach Email — Dr. Lance K. Kim (KAERI / 전 JRC)

**Status:** Draft v0.1. Edit highlighted blocks before sending.
**Special considerations:**
- Lance Kim의 현 KAERI 소속·연락처는 공개정보로 정확히 확인되지 않으므로, **KAERI 학술협력실 또는 개인 LinkedIn 통한 인사 문의 필요**
- 주요 인용: Renda·Kim·Jungwirth·Cojazzi (2014, IAEA-CN-220) 및 Renda·Kim·Cojazzi (2015, JRC)

**Suggested send channel (in order of preference):**
1. KAERI 학술협력실 통한 공식 introduction
2. Lance Kim의 LinkedIn 직접 메시지 (있을 시)
3. JRC 시절 동료 (Cojazzi 그룹) 통한 referral
4. 학회 (INMM Korea Chapter 등) 행사 후 직접 명함 교환

**Subject (English):** `OS-PM — open-source PM reconstruction; would value your JRC perspective`

---

## Suggested attachment package

1. `os-pm-arxiv-v1-2026-05-09.pdf` (8-page preprint, 100 KB)
2. `PI_demo_deck.md` rendered to PDF
3. **JRC Big Table compatibility note** (1-page PDF, to be drafted — see template below)

---

## Email body — English first, optional Korean translation

```
Dear Dr. Kim,

I am writing as [name, affiliation]. Your 2014 IAEA-CN-220 paper with
Cojazzi, Jungwirth and Renda — *The potential of open source
information in supporting Acquisition Pathway Analysis to design IAEA
State Level Approaches* — and the 2015 JRC follow-up on methodological
aspects of the State Level Concept have been the foundation of an
academic project we have just completed Phase 1 of, and I would value
your perspective.

The project, *OS-PM*, is a vision-language-model-driven reconstruction
of the IAEA Physical Model that populates 88 of the 88 in-scope element
cells from open-licensed data alone. Volume 11 (weaponization) is
permanently excluded by schema-level policy. The system implements six
analysis modules (image understanding, document mining, Bayesian
fusion, Cooke-method strength elicitation, a NetworkX-based APA graph,
and a four-case historical retrofit validator) with 41 unit tests
passing. Code, prompts, and the PM-cell schema are released under
Apache-2.0; an 8-page preprint is attached.

Our work is best understood as a VLM-native successor to your Big Table
programme, and we would be honoured to:

  1. Have you review the schema for compatibility with the JRC tabular
     structure. Is there a path to publishing a mapping between OS-PM's
     YAML cells and the JRC representation?

  2. Discuss potential collaboration as a senior advisor / co-author,
     particularly for the V09 R&D / Hot Cells cells (where KAERI's
     PRIDE programme is one of the publicly cited civilian R&D
     references).

  3. Identify cases for a Phase 2 evaluation — declared peaceful
     programmes that would give us realistic negatives for the
     state-level classifier.

I would welcome a 30-minute conversation at your convenience, online
or at KAERI Daejeon. Suggested windows: [date 1] or [date 2].

Honesty about what OS-PM is *not*: this is a detection-oriented
academic system, not a sanctions or operational tool. Volume 11
content is out of scope by design.

Thank you for your consideration.

Best regards,

[Name]
[Title, Affiliation]
[Email] · ORCID: [orcid]
GitHub: github.com/[org]/os-pm    (release imminent)
arXiv: arXiv:[TBD]
```

---

## JRC Big Table compatibility note (1-page draft to attach)

```
OS-PM ↔ JRC Big Table — preliminary mapping note

OS-PM YAML schema field        →  JRC Big Table column (estimated)
──────────────────────────────────────────────────────────────────
cell_id (V<NN>_E<n>)           →  Volume × Element grid coordinate
processes[].id                  →  process row identifier
processes[].materials_required  →  Materials (HS-coded) column block
processes[].rd_keywords         →  R&D / Training keyword column
processes[].visual_signatures   →  Imagery signature column
processes[].auxiliary_indicators→  Auxiliary infrastructure column
processes[].confidence_rules    →  Strength tier rule (s/m/w)

Open questions for Dr. Kim:
- Does the Big Table use a single-axis or multi-axis indicator
  weighting?
- Is the strength tier (strong/medium/weak) compatible with the
  JRC conventions, or do you use a different ladder?
- Are HS codes resolved to the 6-digit, 8-digit, or finer level?
- Is the data licensed for academic re-use, or is a redacted
  derivative needed?

We would be happy to publish the mapping table as a joint
methodological note if you are interested.
```

---

## Pre-send checklist

- [ ] Lance Kim 현 소속·연락처 확인 (LinkedIn / KAERI 사이트 / 학회 명단)
- [ ] 정확한 호칭 (Dr. / Prof. / 박사님)
- [ ] 인용 논문 제목·연도 확인
- [ ] JRC 1-page note 첨부 시 정확한 용어 사용
- [ ] 첨부파일 3개 동봉
- [ ] 미팅 후보일 2개 제시
