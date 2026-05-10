# Cover Note for OS-PM arXiv Submission

**Title:** OS-PM: A Vision-Language-Model-based, Open-Source Reconstruction of the IAEA Physical Model for Academic Nuclear Safeguards Research

**Submission type:** Preprint (v1)
**Target categories:** cs.CY (primary), physics.soc-ph, cs.AI, cs.LG, eess.IV

> Use this note when (a) emailing the preprint to specific reviewers /
> potential collaborators, or (b) replying to journals after the arXiv
> announcement. Adapt the tone for each audience.

---

## A. Short version (3–4 sentences, Twitter / X / Slack)

> We're releasing OS-PM, an open-source academic reconstruction of the
> IAEA Physical Model. Phase 1 ships 88 in-scope cell schemas, six
> analysis modules, four historical retrofit cases, and an honest
> Volume-11 (weaponization) exclusion. Code, prompts, and PM cells under
> Apache-2.0; arXiv preprint at [link]. Comments and collaborations
> welcome.

## B. Medium version (one paragraph, email body)

> Dear [Name],
>
> I'm writing to share a Phase 1 academic preprint that may be of
> interest given your work on [SLC/APA / safeguards verification /
> open-source intelligence / nuclear nonproliferation policy]. We have
> built OS-PM, a vision-language-model-driven reconstruction of the
> IAEA Physical Model that populates 88 of 88 in-scope element cells
> from open-licensed data (Sentinel-2/Landsat, OpenAlex, UN COMTRADE,
> EURDEP). The system implements six modules (image understanding,
> document mining, Bayesian fusion, expert-elicitation strength
> estimation, an APA graph, and a historical-retrofit validator) and
> reports honest results across four canonical retrofit cases
> (Iran-Natanz, Libya, Iraq pre-1991, Syria-Al-Kibar). Volume 11
> (weaponization) is permanently out of scope. The code and PM-cell
> schema are released under Apache-2.0; the preprint is at [arxiv URL]
> and the repository at [github URL].
>
> Two specific asks if you have time:
> 1. A 30-minute methodological review (online or in person).
> 2. Pointers to declared peaceful programmes we could use as
>    realistic negatives for the GNN-light evaluation.
>
> Thank you for considering.
>
> Best regards,
> [Author 1]
> [Affiliation], [Email]

## C. Long version (formal letter, ~400 words)

> Dear Professor / Dr. [Name],
>
> I am pleased to share with you a Phase 1 academic preprint, *OS-PM:
> A Vision-Language-Model-based, Open-Source Reconstruction of the IAEA
> Physical Model for Academic Nuclear Safeguards Research*, archived at
> [arxiv URL]. The work is, to our knowledge, the first end-to-end,
> publicly reproducible academic system that populates the IAEA
> Physical Model schema from open-licensed sources alone and exercises
> the full Acquisition Path Analysis (APA) pipeline on historical
> retrofit cases.
>
> Briefly, OS-PM combines (i) a YAML-encoded reconstruction of 88 of
> the 88 in-scope element cells of the PM (Volume 11 weaponization is
> permanently excluded by schema-level policy), (ii) six analysis
> modules implemented in Python with 37 unit tests
> (image understanding, document mining, confidence-weighted Bayesian
> fusion, Cooke-method strength elicitation, a NetworkX-based APA
> graph, and a historical-retrofit validator), and (iii) a four-case
> evaluation harness covering Iran-Natanz (2002), Libya (2003),
> Iraq pre-1991, and Syria-Al-Kibar (2007). The Phase 1 results are
> reported honestly: top-1 process identification accuracy is 1.00
> across the four cases, but mean posterior is 0.29 with ECE 0.71,
> indicating that ranking is robust while calibration awaits the
> imagery and trade modalities planned for Phase 2.
>
> The work is positioned as a complement to JRC Ispra's Big Table
> programme (Renda et al. 2014, 2015) and the Forschungszentrum
> Jülich formal-APA framework (Listner et al. 2013;
> Allen et al. 2021). We cite both extensively and would welcome a
> methodological audit, particularly on (a) compatibility of the
> YAML schema with JRC's tabular structure, and (b) the strength-tier
> calibration approach. The advisory committee for Phase 2 is being
> assembled and we would be honoured to discuss whether you might be
> willing to serve on it.
>
> All code and prompts are released under Apache-2.0 at [github URL];
> the PM cell schemas are deposited at [zenodo DOI]. The system is
> exclusively for academic detection research; weaponization
> indicators are out of scope by design and oversight.
>
> Thank you for considering. I would be glad to schedule a 30-minute
> conversation at your convenience.
>
> Sincerely,
> [Author 1]
> [Title, Affiliation]
> [Email] · ORCID: [orcid]

---

## D. Korean version (한국어, IRB / 자문위 / 국내 협력 대상)

존경하는 [성명] 박사님,

저희 연구팀은 IAEA Physical Model을 공개정보 기반으로 부분 재구성하는 학술 시스템 **OS-PM** 의 Phase 1 결과를 arXiv 에 사전 공개하였습니다 ([arxiv URL]).

핵심 내용은 다음과 같습니다.

1. **공개라이센스 데이터만 사용** (Sentinel-2/Landsat, OpenAlex, UN COMTRADE, EURDEP)
2. **PM 88개 in-scope 셀 100% 작성** (V11 weaponization 영구 제외)
3. **6개 분석 모듈 구현** (image · document · fusion · strength · APA graph · validator)
4. **4개 역사적 사례 검증** (이란-나탄즈, 리비아, 이라크, 시리아-알키바르)
5. **재현가능 — Apache-2.0** ([github URL])

특별히 다음 두 가지 측면에서 박사님의 의견을 구하고자 합니다:

- 본 시스템이 한국 (KAERI/KAIST/KINAC) 의 안전조치 연구·교육에 어떤 형태로 활용 가능할지
- 자문위원회 (5인) 참여 가능성

30분 정도의 온라인 또는 대면 미팅을 제안드립니다. 첨부된 PDF (8쪽) 및 7-슬라이드 데모 덱을 함께 검토하실 수 있습니다.

감사합니다.

[저자명 / 소속 / 연락처]

---

**문서 종료.**
