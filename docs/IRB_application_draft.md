# OS-PM 연구윤리·이중용도 검토 신청서 (Draft)

**과제명:** Open-Source Physical Model (OS-PM): VLM 기반 핵 안전조치 보조 시스템의 학술적 가능성 검증

**책임연구자(PI):** [기재 필요 — 인선 후보 풀은 별첨 참조]
**소속기관:** [기재 필요 — KAERI / KAIST / KINAC / 대학 등]
**연구기간:** 2026-MM-DD ~ 2027-MM-DD (12개월)
**제출일:** 2026-05-08

> **인선 별첨 (Attachment-1):** `PI_candidates_open_source_research.md`
> 공개정보 기반 PI · 자문위원 · 협력기관 후보 풀이 정리되어 있음.
> 본 양식의 PI / 자문위 항목은 자문위 사전회의 후 v1.0에서 확정 예정.

> 이 문서는 다음 세 가지 검토 트랙을 동시에 충족하기 위한 **통합 양식**:
> (A) 기관 연구윤리위원회(IRB), (B) 이중용도 연구 검토위원회(DURC), (C) 수출통제·내부심의위원회

---

## 0. 요약 (한 페이지)

| 항목 | 내용 |
|------|------|
| 연구목적 | IAEA Physical Model의 공개정보 기반 부분 복제 가능성을 학술적으로 검증 |
| 핵심방법 | 위성영상(Sentinel-2/Landsat) + OpenAlex 학술문헌 + UN COMTRADE + Claude VLM |
| 연구결과물 | 학술논문, 오픈소스 코드(Apache-2.0), 재현 가능한 데이터셋(Zenodo) |
| **명시적 비목표** | 운영적 사찰결정, weaponization 지표 (PM Vol.11), 분류영상 사용, 특정국가 ad hominem 평가 |
| 위험완화 | (i) 연구자 직접 평가 결과는 비공개 검토위 사전심사, (ii) 출판 시 redaction protocol, (iii) NPT/MTCR 준수 자체점검표 |
| 데이터 사용 | 100% 공개 라이센스 데이터에 한정. 분류·내부 IAEA 자료 일체 미사용 |
| 인간대상 연구 | 해당 없음 (인간 피험자 없음). 단, 전문가 elicitation 단계는 별도 IRB 검토 |

---

## 1. 연구 배경 및 목적

### 1.1 학술적 동기

IAEA Physical Model (PM)은 1999년 Liu & Morsy에 의해 Programme 93+2의 일환으로 개발된 핵연료주기 indicator 매핑 체계로, 12 volumes × 8 elements per process 구조를 갖는다. 그러나 PM의 원본은 IAEA 내부 STR(Safeguards Technical Report) 시리즈로 비공개이며, 학계는 JRC (Renda·Cojazzi 2014–2015), Forschungszentrum Jülich (Niemeyer·Listner 2013), 미국 국립연구소(Sandia·INL·ORNL) 등에서 부분적으로 공개정보 기반 보완 연구를 수행해 왔다.

본 연구는 **"공개 라이센스 데이터와 최신 VLM(Vision-Language Model)을 결합하면 PM의 어느 부분까지 학술적으로 재구성할 수 있는가?"** 라는 질문에 답하는 **방법론적·시스템 페이퍼**를 목표로 한다.

### 1.2 사회·정책적 의의

- **검증 투명성** 향상: 학계의 독립적 OS-PM 도구는 IAEA의 권위에 의존하지 않는 보완적 검증을 가능케 함
- **Capacity building**: 한국·동북아 학계의 안전조치 분석 역량 강화
- **IAEA·JRC와의 학술 협력** 기반 마련

---

## 2. 연구 방법

### 2.1 데이터 소스 (전부 공개·합법)

| 종류 | 소스 | 라이센스 |
|------|------|---------|
| 위성영상 | Sentinel-2/3, Landsat-7/8/9 | CC BY / Public Domain |
| 위성영상 (보조) | Planet Labs (학술 라이센스 신청) | Academic NC |
| 학술문헌 | OpenAlex, Semantic Scholar, arXiv, OSTI | CC0 / CC BY |
| 무역데이터 | UN COMTRADE, Eurostat, US Census | Open |
| 환경 시그니처 | EURDEP, Sentinel-3 SLSTR, NOAA HYSPLIT | Open |
| 수출통제 | NSG/EU/US 공시 목록 | Public |

### 2.2 분석 모델

- **Primary VLM**: Claude 4.6 Sonnet (학술 API 라이센스, 출력 비훈련 보장)
- **Secondary VLM (재현성)**: Qwen2.5-VL-72B (Apache-2.0, 자체 호스팅)
- 두 모델 disagreement 시 보수적(conservative) 출력 채택

### 2.3 검증 사례

이미 공개된 역사적 사례에 한정:
- 이라크 (1991 발견)
- 리비아 (2003 자진 포기)
- 시리아 Al-Kibar (2007 파괴)
- 이란 Natanz (2002 NCRI 폭로)

**현재 진행 중인 미해결 사안에 대한 평가는 본 연구 범위에서 제외.**

---

## 3. 이중용도(Dual-Use) 위험 평가

### 3.1 NIH-DURC 7대 카테고리 자체 평가

| 카테고리 | 해당여부 | 비고 |
|---------|---------|------|
| 1. 백신·치료법 무력화 | ❌ | 핵분야 |
| 2. 병원체 transmissibility 증대 | ❌ | |
| 3. 병원체 host range 확대 | ❌ | |
| 4. 병원체 detection evasion | ❌ | |
| 5. **무기화 기술 개량** | ⚠️ **PM Vol.11 명시적 제외** | 본 시스템은 detection 측면만 다룸 |
| 6. **분류 정보 재구성** | ⚠️ 평가 필요 | 공개정보만 사용; 분류정보 재구성 가능성 ↓ |
| 7. **국가안보 직접 영향** | ⚠️ 평가 필요 | mitigation 절차 적용 |

### 3.2 본 연구가 의도적으로 다루지 않는 것

- 핵무기 설계, 임계량, 펌핑 시스템 등 **weaponization** (PM Vol.11)
- 회피·기만(deception) 효과적 설계 가이드
- 특정국가 원자력 시설의 **공격 좌표** 또는 **취약점**
- **분류영상**, **분류문서**, **내부 IAEA 자료**

### 3.3 출력 redaction 프로토콜

학술 출판 시 다음을 자동 redact:
- 임계량 관련 수치
- 무기-사용 가능 농축도 (>20% U-235) 정량 분석
- 특정 시설의 보안 perimeter 약점
- 미공개·진행 중인 사례 분석 결과

---

## 4. NPT 및 수출통제 준수

### 4.1 NPT 조항별 자체 점검

- **Article I**: 핵보유국이 비핵보유국에 핵무기·관련기술 이전 금지 → **본 연구는 어떠한 transfer도 수반하지 않음**
- **Article II**: 비핵보유국의 핵무기 획득·제조 금지 → **본 연구는 detection 측면만 다룸**
- **Article III**: 안전조치 의무 → **본 연구는 안전조치 보완을 목적**
- **Article IV**: 평화적 이용 권리 → 본 연구는 정상 평화적 활동 식별을 통해 false positive 최소화에 기여

### 4.2 수출통제 (Wassenaar / NSG / EU Dual-Use / 한국 전략물자)

- 본 시스템 자체는 **소프트웨어**이며 ECCN/EAR 분류 자체검토 필요
- VLM 모델 가중치 자체는 controlled item 아님
- 그러나 시스템 산출물(특정국가 평가) 공개 시 한국 전략물자관리원(KOSTI) 사전 의견조회

### 4.3 한국법 준수

- **국가핵심기술 보호법**: 해당 없음 (본 연구는 detection에 한정)
- **방위사업법**, **무역법 19조** 사전 적용대상 여부 검토 필요
- **개인정보보호법**: 인적 자본 분석 시 공저자명 노출 → 익명화 또는 집계 처리

---

## 5. 데이터 라이센스 추적표

| 데이터 | 출처 라이센스 | 본 연구 사용 | 재배포 가능 여부 |
|--------|-------------|------------|----------------|
| Sentinel-2 | CC BY 4.0 (ESA) | 직접 다운로드 | 가능 (출처 표기) |
| Landsat | Public Domain (USGS) | 직접 다운로드 | 가능 |
| Planet Labs | Academic NC | API tasking | 출판 시 thumbnail 한정 |
| OpenAlex | CC0 | API | 가능 |
| Semantic Scholar | API ToS | API | 메타데이터만 가능 |
| UN COMTRADE | Open Data Agreement | API | 집계 결과만 가능 |
| Claude API 출력 | Anthropic ToS (학술 사용) | API | 가능 (출처 표기) |

**누적 라이센스 다이어그램** 작성 → 출판 전 법무 검토 통과 필수.

---

## 6. 연구진 윤리 교육 이수

- 책임연구자 및 모든 연구원: **CITI Program "Responsible Conduct of Research"** 이수 (12개월 유효)
- AI/ML 연구원: **MIT Lincoln Lab Responsible AI Curriculum** 또는 동급 과정
- 핵 안전조치 도메인 자문위원: NSG/IAEA 비공식 가이드라인 숙지 진술서

---

## 7. 자문위원회 구성안

| 역할 | 인원 | 자격 |
|------|-----|------|
| 위원장 | 1 | 안전조치 30년+ 경력 (전직 IAEA inspector 또는 KINAC 임원) |
| 기술 위원 | 2 | (a) AI/VLM 전공 교수 (b) GIS/원격탐사 전공 교수 |
| 정책 위원 | 1 | 핵정책 / 비확산 외교 전문가 |
| 윤리 위원 | 1 | 연구윤리·이중용도 전문가 |
| 외부 옵저버 | 1 | (선택) JRC 또는 ISIS 등 해외 연구기관 |

**회의 주기**: 분기별 (Phase별 결과 검토)
**비공개 사전심사 권한**: 모든 학술 출판물·코드 공개 전 위원회 사전 검토 (≥10일 review window)

---

## 8. 일정·산출물·검토 게이트

| 단계 | 종료 시점 | 산출물 | 게이트 |
|------|---------|-------|--------|
| Phase 0 (현재) | M0 | 본 IRB 신청서 | IRB·DURC 통과 |
| Phase 1 — MVP | M3 | Natanz retrofit + arXiv preprint v0 | 자문위 사전심사 |
| Phase 2 — Beta | M6 | 5 processes + APA graph | 자문위 + 외부 1인 review |
| Phase 3 — v1.0 | M12 | 12 volumes + 4 case 검증 + 코드 공개 | 자문위 + KOSTI 사전 의견 |
| 출판 | M12+ | Science & Global Security 또는 ESARDA Bulletin | journal peer review |

---

## 9. 위험 발생 시 대응 절차

### 9.1 의도치 않은 새로운 indicator 발견
1. 즉시 **출력 격리** (encrypted local store)
2. **위원장 + 윤리위원**에 24시간 내 보고
3. 위원회가 **공개·redact·폐기** 결정
4. 결정 결과 IRB에 30일 내 보고

### 9.2 오용 (third party가 코드 fork하여 악용)
- Apache-2.0 라이센스에 **연구·교육 용도 권고** 명시
- README에 **operational use 금지** 경고 명시
- GitHub repository security policy로 takedown 채널 운영

### 9.3 외교적 항의 / 정부 우려
- 즉시 **연구 일시중단**
- 기관 법무·국제협력처 통한 공식 응대
- 자문위원회 임시소집

---

## 10. 첨부

- [ ] 연구계획서 (별도 파일)
- [ ] 책임연구자 CV
- [ ] 데이터 사용계약서 (Anthropic/Planet 등)
- [ ] 책임연구자 윤리교육 수료증 사본
- [ ] 자문위원 동의서 (각 1부)

---

## 서명

| 역할 | 성명 | 서명 | 날짜 |
|------|-----|-----|------|
| 책임연구자(PI) | | | |
| 기관 연구처장 | | | |
| 기관 IRB 위원장 | | | |
| 자문위 위원장 | | | |

---

**문서버전:** Draft v0.1 — 2026-05-08
**다음 개정:** 자문위 사전회의 후 v1.0
