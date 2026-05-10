# OS-PM arXiv 제출 체크리스트

**대상:** v1 첫 제출 (Phase 1 system paper)
**작성:** 2026-05-09

본 문서는 사용자가 arXiv 제출 직전 점검할 항목을 한 자리에 모은 것입니다. 모든 ☐ 가 ✅ 가 되었을 때 제출하십시오.

---

## A. 콘텐츠 (저자가 직접 검토)

### A1. 저자 정보 (필수)

- ☐ Author 1: 성명·소속·이메일·ORCID 확정
- ☐ Author 2 (해당 시): 동일
- ☐ Author 3 (해당 시): 동일
- ☐ Corresponding author 지정
- ☐ 저자 순서 모든 공저자 합의
- ☐ ORCID 등록 (각 저자마다 최소 1회 — arXiv → ORCID 연동)

> **주의:** 현재 `main.tex` Lines 47-52 에 `[Author 1] / [Institution 1]` 등 placeholder 있음.

### A2. 어드바이저리·자문 절차

- ☐ 자문위원회 위원장 사전 검토 완료 (이메일 확보)
- ☐ 기관 IRB 또는 책임자에 사전 통지 (DURC 검토는 system paper 단계에서는 면제 가능 — 기관 정책 확인)
- ☐ KOSTI (전략물자관리원) 사전 의견조회 (선택; 코드 공개 직전이 더 적절)
- ☐ Anthropic AUP 준수 자기점검 (V11 weaponization 콘텐츠 부재 확인)

### A3. 동료 사전 검토 (강력 권고)

- ☐ Yim 교수 (KAIST) 사전 의견 (`PI_demo_deck.md` 와 PDF 첨부)
- ☐ Lance Kim 박사 사전 의견 (JRC Big Table 호환성 측면)
- ☐ 외부 1인 추가 (예: Princeton SGS 그룹, Niemeyer 그룹 등)
- ☐ 응답 받은 코멘트 main.tex 에 반영

---

## B. 매니페스트 (자동 검증 가능)

### B1. main.tex 정합성

- ☐ 남은 `\todo{}` 매크로 정의 외 0건 (`grep -c "\\todo{" main.tex` ≤ 1)
- ☐ 저자 자리 placeholder 확정 (`[Author 1]` → 실명)
- ☐ 기관 자리 placeholder 확정 (`[Institution 1]` → 실 기관)
- ☐ 이메일 자리 확정
- ☐ GitHub URL 확정 (`[org]/os-pm` → 실 GitHub)
- ☐ Zenodo DOI 확정 (`[zenodo-doi]` → 실 DOI; 미발급 시 `(reservation pending)`)

### B2. 빌드

- ☐ `cd paper && latexmk -C` 후 깨끗하게 재컴파일
- ☐ `latexmk -pdf -xelatex main.tex` 0 error
- ☐ Total page count 7-10 (현재 8 페이지)
- ☐ 모든 cross-reference 해결 (`Reference '...' undefined` 메시지 없음)
- ☐ 모든 citation 해결 (`Citation '...' undefined` 메시지 없음)
- ☐ Bibliography 모든 entry DOI 검증 (가능한 경우)
- ☐ 인쇄 미리보기에서 표·그림 잘리지 않음 확인

### B3. 번들 생성

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm\paper"
python build_arxiv_bundle.py --version v1
```

- ☐ `arxiv_submission/os-pm-arxiv-v1-YYYY-MM-DD.tar.gz` 생성
- ☐ 동일 버전의 `.zip`도 생성
- ☐ `manifest.txt` 내용 확인 (예상 파일만 포함)
- ☐ 사이드 PDF 확인 (`os-pm-arxiv-v1-YYYY-MM-DD.pdf`)

### B4. 메타데이터

- ☐ `ARXIV_METADATA.md` 의 Title 복사
- ☐ Authors 복사 (실 정보로 대체)
- ☐ Abstract 복사 (1875 chars / 1920 limit)
- ☐ Subject classes 복사 (`cs.CY` primary, 4 cross-lists)
- ☐ Comments 복사

### B5. 라이센스

- ☐ arXiv 라이센스 선택: NLD (권장) 또는 CC-BY-4.0
- ☐ 기관 정책과 일치 (소속 기관에 따라 NLD 외 라이센스 불가능할 수 있음)
- ☐ 코드 라이센스 (Apache-2.0) 와 별개임을 인지

---

## C. 제출 직전 dry-run (5 분)

```powershell
# 1. 모든 todo 제거 확인
grep -c "\\\\todo{" "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm\paper\main.tex"

# 2. 모든 placeholder 제거 확인
grep -E "\[Author|\[Institution|\[email|\[org\]|\[TBD\]|\[zenodo" "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm\paper\main.tex"

# 3. 깨끗 빌드
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm\paper"
latexmk -C
latexmk -pdf -xelatex -interaction=nonstopmode -halt-on-error main.tex

# 4. 번들
python build_arxiv_bundle.py --version v1

# 5. PDF 한 번 더 시각 검토
start arxiv_submission/*.pdf
```

---

## D. arXiv 웹 제출 단계 (실제 제출일)

1. **로그인**: https://arxiv.org/user/login (ORCID 연동 권장)
2. **Submit** → "Start a new submission"
3. **License**: NLD 선택
4. **Archive/Subject**: cs.CY primary; cross-list physics.soc-ph, cs.AI, cs.LG, eess.IV
5. **Metadata**:
   - Title: `ARXIV_METADATA.md` 복사
   - Authors: 본 체크리스트 A1 확정값
   - Abstract: `ARXIV_METADATA.md` 복사
   - Comments: `ARXIV_METADATA.md` 복사
   - MSC class / ACM class: 선택 사항
6. **Files**: `os-pm-arxiv-v1-YYYY-MM-DD.tar.gz` 업로드
7. **Process**: arXiv 자체 빌드 시도 → AutoTeX 결과 PDF 검토
8. **Preview**: 시각 검토. 이상 시 수정 → 재업로드
9. **Submit**: 확정 클릭

> **48시간 hold:** 첫 제출은 moderator review 거침. announcement 시점은 다음 영업일 화요일/목요일 18:00 EST 직후가 보통.

### 제출 후 의무

- ☐ arXiv 발행 후 ID (`arXiv:YYMM.NNNNN`) 기록
- ☐ GitHub repo README 에 arXiv 링크 추가
- ☐ Zenodo DOI 발급 후 v2 metadata에 반영 (선택)
- ☐ Yim 교수 / Lance Kim / 자문위원에게 발행 알림
- ☐ 30 일 후 리비전 결정 (코멘트 반영 / Phase 2 결과 추가 시점)

---

## E. 문제 발생 시 대응

| 문제 | 대응 |
|-----|------|
| arXiv가 첫 제출자 endorsement 요구 | 기관 동료에게 endorse 요청 (자문위 위원장 또는 Yim 교수 후보) |
| AutoTeX 빌드 실패 (xelatex vs pdflatex) | `\usepackage{fontspec}` 사용 시 `latexmk -pdf` 가 아닌 `-xelatex` 강제. arXiv는 default xelatex 지원함 |
| PDF 페이지 수 ≠ 로컬 빌드 | bundle에서 누락 파일 확인 — `manifest.txt` 와 비교 |
| 저자 ORCID 미연동 → submission 거부 | ORCID 등록 후 arXiv 계정에 연결 (5분) |
| 카테고리 reject (cs.CY 부적합 평가) | physics.soc-ph 를 primary로, cs.CY 를 cross-list 로 전환 |
| 모더레이터 hold 길어짐 (>72h) | arXiv help@ 문의. 일반적으로 2-3일이면 통과 |

---

**문서 종료. ☐ 모두 ✅ 되면 제출 준비 완료.**
