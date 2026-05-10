# Manual Actions Required — OS-PM v0.1.0 release

**Last updated:** 2026-05-11
**Repository:** https://github.com/pinking-jeong/Nonproliferation
**Local path:** `C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm`
**Local commits:** `d0a3bf9`, `57a7c26` (more pending after the next chore commit)
**arXiv bundle:** `arxiv_submission/os-pm-arxiv-v1-2026-05-11.tar.gz` (16 KB) + cross-check PDF (108 KB, 11 pages)

> **Reading order.** Items are sorted by recommended execution order. Sections marked **AUTO** ✅ have already been completed in this session — they are listed only so you know what NOT to redo. Sections marked **DO** ⏳ require your manual click / login / signature.

---

## 0. Status snapshot

| Layer | State | Notes |
|-------|-------|-------|
| OpenRouter API key (rotation #1) | ✅ AUTO | New key stored only in `.env` (gitignored). Persistent env var refreshed via `setx`. Sanity ping `OK`. |
| `[org]/os-pm` placeholder substitution | ✅ AUTO | All 12 affected files replaced with `pinking-jeong/Nonproliferation`. PDF rebuilt (11 pages, 108 KB). |
| `git init` + 2 commits | ✅ AUTO | `d0a3bf9` (initial release), `57a7c26` (MANUAL_ACTIONS + Phase 2 imagery test). |
| `git remote add origin …` | ✅ AUTO | Pointing at `https://github.com/pinking-jeong/Nonproliferation.git`. |
| Phase 2 imagery VLM smoke test | ✅ AUTO | Sentinel-2 → thumbnail → VLM → JSON, live verified on Natanz. |
| `git push -u origin main` | ⏳ DO | Section 2 below — requires GitHub auth. |
| Author / institution placeholders | ⏳ DO | Section 1 below — requires your real PI info. |
| arXiv submission | ⏳ DO | Section 3 below — web form + login. |
| Zenodo DOI | ⏳ DO | Section 4 below — needs first GitHub release. |
| Claude for Science application | ⏳ DO | Section 5 below — needs PI info + arXiv ID. |
| OpenRouter spend cap | ⏳ DO | One-click setting on openrouter.ai. |

---

## 1. ⏳ Fill author / institution placeholders

Eight files still carry author / institution / email / ORCID placeholders. The substitution map below is what you need to apply with your real values.

### 1.1 Substitution table

| Placeholder | What goes here | Where it lives |
|-------------|---------------|---------------|
| `[Author 1]` | First author's full name (corresponding) | `paper/main.tex:49`, `paper/ARXIV_METADATA.md:23`, `paper/COVER_NOTE.md:50,99` |
| `[Author 2]`, `[Author 3]` | Co-author names (delete if solo) | `paper/main.tex:50–51`, `paper/ARXIV_METADATA.md:23` |
| `[Institution 1, Country]`, `[Institution 2, Country]` | Affiliations | `paper/main.tex:52–53`, `paper/ARXIV_METADATA.md:25–26`, `CITATION.cff:10,14`, `.zenodo.json:7,12` |
| `[Author 1 given names]`, `[Author 1 family name]` | Split form for CFF / Zenodo | `CITATION.cff:8–13,42–43`, `.zenodo.json:6,11` |
| `[email@example.com]`, `[Email]` | Corresponding-author institutional email | `paper/ARXIV_METADATA.md:27`, `paper/COVER_NOTE.md:51,101` |
| `[orcid]`, `0000-0000-0000-0000` | ORCID iD per author | `paper/COVER_NOTE.md:51,101`, `CITATION.cff:11,15`, `.zenodo.json:8,13` |
| `[Title]`, `[Your full name]`, etc. (in `Claude_for_Science_application.md`) | Application form fields | `docs/Claude_for_Science_application.md` Section 1 + 2 |
| `[Your name]` etc. (in outreach emails) | Personalisation | `docs/outreach/email_*.md`, `docs/advisory/recruitment_template.md` |

### 1.2 Quick-fix script (PowerShell)

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"

# Inspect what's left
grep -rnE "\[Author [0-9]+\]|\[Institution [0-9]+|\[email\]|\[Email\]|\[orcid\]|0000-0000-0000-0000|\[Your full name\]|\[Title\]|\[Your name\]" --include="*.md" --include="*.tex" --include="*.cff" --include="*.json" .

# Edit each file in your IDE / VS Code (Find & Replace per placeholder)
# Recommended order:
#   1. paper/main.tex          (the manuscript)
#   2. paper/ARXIV_METADATA.md (form data — copy-paste into arXiv submit page)
#   3. paper/COVER_NOTE.md     (PI outreach emails)
#   4. CITATION.cff            (citation metadata)
#   5. .zenodo.json            (Zenodo deposit metadata)
#   6. docs/Claude_for_Science_application.md
#   7. docs/outreach/email_*.md          (Yim 교수 / Lance Kim 인사말 부분 personalise)
#   8. docs/advisory/recruitment_template.md

# After edits, rebuild the arXiv bundle
cd paper
python build_arxiv_bundle.py --version v1
cd ..

# Commit and push
git add -A
git commit -m "chore: fill author / institution / ORCID placeholders"
git push origin main
```

### 1.3 Verification command (rerun until output is empty)

```powershell
grep -rnE "\[Author [0-9]+\]|\[Institution [0-9]+|\[email\]|\[Email\]|\[orcid\]|0000-0000-0000-0000|\[Your full name\]|\[Title\]" --include="*.md" --include="*.tex" --include="*.cff" --include="*.json" --include="*.bib" .
```

When this command produces no lines, your bundle is "submission-clean".

---

## 2. ⏳ Push to GitHub

The local git repo is fully ready. The remote is registered. You need to do the auth + push.

### 2.1 First-time GitHub CLI auth (one-time, ~2 minutes)

```powershell
# Install gh once (https://cli.github.com/) if not already there
gh auth login
# Choose: GitHub.com → HTTPS → "Login with a web browser" → paste code on github.com
# After success, future git pushes use the cached token automatically.
```

### 2.2 Push the existing commits

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
git push -u origin main
```

If GitHub says the repository is empty, the push will populate it with all 175+ files. If GitHub already has a README.md or other content from the web UI initialisation, see Section 2.3.

### 2.3 Conflict resolution (only if the GitHub repo has prior commits)

If you previously hit "Add a README" on github.com, the remote has a commit you don't have locally. Resolve like this:

```powershell
git pull --rebase origin main
# Resolve any conflicts (likely just README.md), then:
git push -u origin main
```

If you'd rather start fresh and discard the remote's prior content (only do this if you're sure):

```powershell
git push -u origin main --force-with-lease
```

### 2.4 Verify the push

After `git push` completes, open https://github.com/pinking-jeong/Nonproliferation in a browser and confirm:

- All 175+ files are visible
- The README renders properly
- The Apache-2.0 LICENSE is detected (sidebar shows "Apache-2.0")
- The `.github/workflows/test.yml` workflow appears in the **Actions** tab and starts running

### 2.5 Repository settings (recommended, ~5 minutes via web UI)

Go to https://github.com/pinking-jeong/Nonproliferation/settings and apply:

- **Description:** `OS-PM: open-source VLM-based reconstruction of the IAEA Physical Model (academic, Apache-2.0)`
- **Website:** add the arXiv URL once Section 3 produces an ID
- **Topics:** `nuclear-safeguards`, `nonproliferation`, `vlm`, `open-source-intelligence`, `iaea`, `acquisition-path-analysis`, `apache-2-0`, `python`
- **General → Features:** enable Issues, Discussions; disable Wiki and Projects (we use docs/ instead)
- **Branches → Branch protection rule for `main`:**
  - Require a pull request before merging (1 reviewer)
  - Require status checks: `pytest` and `schema-validate`
  - Do not allow bypassing
  - (Optional) require signed commits
- **Pages:** off for now; Phase 2 may host a small docs site
- **Security:** turn on Dependabot alerts and security advisories

---

## 3. ⏳ arXiv submission

The arXiv bundle `arxiv_submission/os-pm-arxiv-v1-2026-05-11.tar.gz` (16 KB) is built. Submission flow:

### 3.1 Pre-submission cleanup

Make sure Section 1 is complete (no placeholders remain). Then **rebuild the bundle once more** so the tarball is up-to-date:

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm\paper"
python build_arxiv_bundle.py --version v1
```

The script overwrites the dated tarball with current content.

### 3.2 arXiv account preparation (once)

1. Create / log into your account at https://arxiv.org/user/login
2. Link your ORCID at https://arxiv.org/user/orcid (if not already linked)
3. Make sure your registered institutional affiliation matches what you put in `paper/main.tex`
4. (If first-time submitter to cs.CY) — request endorsement: https://arxiv.org/auth/need-endorse → ask Yim 교수 (KAIST), Lance Kim 박사 (KAERI), or any cs.CY-published colleague to endorse you (one-line click on the URL arXiv emails them)

### 3.3 Submission flow

1. https://arxiv.org/submit → "New submission"
2. **License:** select **arXiv NLD** (recommended — preserves journal flexibility) or **CC-BY-4.0**
3. **Archive / subject classification:**
   - Primary: `cs.CY` (Computers and Society)
   - Cross-list: `physics.soc-ph`, `cs.AI`, `cs.LG`, `eess.IV`
4. **Metadata** — copy verbatim from `paper/ARXIV_METADATA.md`:
   - Title (one line)
   - Authors (block from §1.1)
   - Abstract (1875 / 1920 chars, already prepared)
   - Comments: "Phase 1 system paper. 11 pages, 5 tables, 1 figure. Code at github.com/pinking-jeong/Nonproliferation."
5. **MSC class / ACM class:** optional; suggested values are in `ARXIV_METADATA.md`
6. **Files:** upload `arxiv_submission/os-pm-arxiv-v1-2026-05-11.tar.gz`
7. **Process:** wait for AutoTeX to compile. Expected output is a **clean 11-page PDF (~108 KB)**. If AutoTeX fails, the most likely cause is a font / package not in arXiv's TeX Live; fall back to `--engine pdflatex` or remove the `pifont` dependency.
8. **Preview:** scroll the rendered PDF, ensure tables and figure are intact
9. **Submit** → arXiv places the submission on a 24–48 hour moderator hold

### 3.4 After acceptance (24–48 hours later)

- Note the arXiv ID, format `arXiv:YYMM.NNNNN` (e.g., `arXiv:2611.12345`)
- Update three places to replace `arXiv:[TBD]`:
  - `CITATION.cff` (line 49)
  - `.zenodo.json` (line ~36)
  - `paper/main.tex` (anywhere "TBD" appears in the `\href{...}` lines — only the line-89 `[TBD]` remains after Section 1)
- Run:

  ```powershell
  cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
  git add -A
  git commit -m "chore: link arXiv:YYMM.NNNNN preprint"
  git push
  ```

- (Optional) email Yim 교수 / Lance Kim with the arXiv link — see `docs/outreach/email_*.md`

---

## 4. ⏳ Zenodo DOI for v0.1.0

A Zenodo DOI gives the codebase a citable identifier independent of GitHub. The flow is:

### 4.1 Connect Zenodo to GitHub (one-time)

1. https://zenodo.org/login (sign in with GitHub OAuth)
2. https://zenodo.org/account/settings/github/ → toggle the `pinking-jeong/Nonproliferation` repository **ON**

This installs a webhook so any GitHub Release auto-deposits to Zenodo.

### 4.2 Create the v0.1.0 GitHub release

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
# Tag the current commit
git tag -a v0.1.0 -m "OS-PM v0.1.0 — Phase 1 release"
git push origin v0.1.0
# Create release via gh CLI
gh release create v0.1.0 --title "OS-PM v0.1.0 — Phase 1 release" --notes-file CHANGELOG.md
```

Or via web: https://github.com/pinking-jeong/Nonproliferation/releases/new → pick tag `v0.1.0` → paste CHANGELOG content → Publish.

### 4.3 Capture the DOI

Within ~10 minutes, Zenodo's webhook deposits a release archive and assigns a DOI. Find it at:

- https://zenodo.org/account/uploads (recent activity)
- The DOI looks like `10.5281/zenodo.NNNNNNN`

### 4.4 Update placeholders

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
# Find remaining [zenodo-doi] / [TBD] strings (should be 4 in main.tex + a couple in CITATION/zenodo)
grep -rnE "\[zenodo-doi\]|\[TBD\]" --include="*.md" --include="*.tex" --include="*.cff" --include="*.json" .

# Replace
$DOI = "10.5281/zenodo.NNNNNNN"     # paste the real DOI you got
Get-ChildItem -Recurse -Include *.md,*.tex,*.cff,*.json | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace '\[zenodo-doi\]', $DOI -replace '\[TBD\]', $DOI | Set-Content $_.FullName -NoNewline
}

# Rebuild + commit + push
cd paper; python build_arxiv_bundle.py --version v1
cd ..
git add -A
git commit -m "chore: link Zenodo DOI for v0.1.0"
git push
```

### 4.5 Add badges to README (optional, ~3 minutes)

Insert near the top of `README.md`:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.NNNNNNN.svg)](https://doi.org/10.5281/zenodo.NNNNNNN)
[![arXiv](https://img.shields.io/badge/arXiv-YYMM.NNNNN-b31b1b.svg)](https://arxiv.org/abs/YYMM.NNNNN)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://github.com/pinking-jeong/Nonproliferation/actions/workflows/test.yml/badge.svg)](https://github.com/pinking-jeong/Nonproliferation/actions)
```

---

## 5. ⏳ Claude for Science application

Already drafted at `docs/Claude_for_Science_application.md` (also packaged as `arxiv_submission/c4s_attachments/OS-PM-c4s-application.md`).

### 5.1 Pre-submit edits

Open `docs/Claude_for_Science_application.md` and replace:

- `[Your full name]`, `[Title]`, `[Institution, Department]`
- `[name@institution.ac.kr]`, `[0000-0000-0000-0000]`
- `arXiv:[ID]` → real arXiv ID (after Section 3)

### 5.2 Submit

1. Search "Anthropic Claude for Science" on https://www.anthropic.com/research (the URL changes; search ensures you find the current form)
2. Open the application form (typically a Google Form or Tally form)
3. Paste sections from `OS-PM-c4s-application.md` into the form fields
4. Attach `arxiv_submission/c4s_attachments/OS-PM-preprint.pdf` (108 KB, 11 pages)
5. Submit

### 5.3 After submit

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
# Save confirmation
mkdir docs\advisory -Force
@"
# Claude for Science application

Submitted: YYYY-MM-DD
Application ID: <paste from confirmation email>
Project: OS-PM (arXiv:YYMM.NNNNN)
Status: pending review (typically 1-4 weeks)
"@ | Out-File docs\advisory\c4s_app.md -Encoding UTF8
git add docs/advisory/c4s_app.md
git commit -m "docs: log Claude for Science submission"
git push
```

### 5.4 If denied / deferred

Anthropic typically gives one-line feedback. Common improvement avenues:

- Letters of support from Yim 교수 / Lance Kim 박사 (after their initial reply)
- Stronger Phase 2 deliverables (e.g., the imagery COG pipeline being live)
- More concrete cost projections from a real Phase 2 batch

Re-apply 30 days later with the revised draft.

---

## 6. Optional — outreach to Yim 교수 / Lance Kim (post-arXiv)

Personalised drafts are at:

- `docs/outreach/email_yim_kaist.md` — Korean + English, citing his 2018/2021 papers
- `docs/outreach/email_lance_kim_kaeri.md` — English, citing his 2014/2015 JRC papers
- `docs/outreach/outreach_tracking.md` — 4-tier matrix to track status

Send only AFTER the arXiv ID is live (otherwise the link is a 404).

---

## 7. Working directory map

```
ospm/                                            ← project root, git repo
├── .git/                                          local commits d0a3bf9, 57a7c26, ...
├── .env                                           OpenRouter key (gitignored)
├── README.md                                      project front-page
├── LICENSE                                        Apache-2.0
├── NOTICE                                         attribution + V11 exclusion
├── CITATION.cff                                   citation metadata (REPLACE PLACEHOLDERS)
├── CHANGELOG.md                                   release notes
├── CONTRIBUTING.md                                contribution policy
├── CODE_OF_CONDUCT.md                             contributor covenant
├── .zenodo.json                                   Zenodo deposit metadata (REPLACE PLACEHOLDERS)
├── .github/                                       CI workflow + issue/PR templates
├── MANUAL_ACTIONS.md                              ← THIS FILE
├── pm_schema/                                     100 YAML cells (12 volumes)
├── backend/app/                                   FastAPI + 6 modules
├── frontend/app.py                                Streamlit demo
├── tests/                                         57 pytest tests
├── scripts/                                       runners (retrofit, ablation, imagery_vlm)
├── paper/                                         arXiv preprint (REPLACE PLACEHOLDERS)
│   ├── main.tex                                   manuscript (Lines 49-53 = author block)
│   ├── ARXIV_METADATA.md                          form-fill source for arXiv
│   ├── COVER_NOTE.md                              outreach emails (en+ko)
│   ├── SUBMISSION_CHECKLIST.md                    tick this as you go
│   ├── references.bib                             BibTeX
│   ├── Makefile, README.md
│   └── build_arxiv_bundle.py                      run after every edit
├── arxiv_submission/                              built tarballs + cross-check PDFs
│   ├── os-pm-arxiv-v1-2026-05-11.tar.gz          ← upload to arXiv
│   ├── os-pm-arxiv-v1-2026-05-11.zip             ← alternative
│   ├── os-pm-arxiv-v1-2026-05-11.pdf             ← cross-check PDF
│   ├── manifest.txt
│   └── c4s_attachments/                           pre-staged for Claude for Science
│       ├── OS-PM-preprint.pdf
│       ├── OS-PM-c4s-application.md
│       └── OS-PM-demo-deck.md
├── docs/
│   ├── API_key_setup_guide.md                     OpenRouter / Anthropic / C4S setup
│   ├── Claude_for_Science_application.md          REPLACE PLACEHOLDERS
│   ├── IRB_application_draft.md                   institutional ethics review
│   ├── PI_candidates_open_source_research.md      open-source PI shortlist
│   ├── PI_demo_deck.md                            7-slide outreach deck
│   ├── outreach/
│   │   ├── email_yim_kaist.md                     bilingual outreach (ko + en)
│   │   ├── email_lance_kim_kaeri.md               outreach with JRC compatibility note
│   │   └── outreach_tracking.md
│   └── advisory/
│       ├── charter.md                             v0.1 — ratify at first meeting
│       ├── recruitment_template.md                bilingual
│       └── first_meeting_agenda.md
└── data/                                          (gitignored; local outputs)
    ├── retrofit/full_retrofit_report.json
    ├── retrofit/phase2_ablation.json              ← live VLM result
    ├── retrofit/imagery_phase2.json
    ├── retrofit/gnn_lite_loo.json
    ├── natanz/natanz_retrofit_report.json
    └── imagery_vlm/                               ← Phase 2 imagery test
        ├── natanz_S2A_39SWT_20241229_0_L2A.jpg    Sentinel-2 thumbnail (70 KB)
        └── natanz_vlm_result.json                 VLM structured output
```

---

## 8. Compact action list (one-page summary)

| # | Action | Time | Tools / URL |
|---|--------|------|-------------|
| 1 | Replace 8 placeholder types in 8 files | 30 min | VS Code Find & Replace |
| 2 | `python paper/build_arxiv_bundle.py --version v1` | 1 min | terminal |
| 3 | `gh auth login` (one-time) | 2 min | https://cli.github.com |
| 4 | `git push -u origin main` | 1 min | terminal |
| 5 | Set GitHub repo description / topics / branch protection | 5 min | https://github.com/pinking-jeong/Nonproliferation/settings |
| 6 | Set OpenRouter daily spend cap to $5 | 1 min | https://openrouter.ai/settings/credits |
| 7 | (If first-time arXiv) request endorsement | 1 day | https://arxiv.org/auth/need-endorse |
| 8 | arXiv submission (web form) | 20 min | https://arxiv.org/submit |
| 9 | Wait for arXiv moderator | 24–48 hr | passive |
| 10 | After arXiv ID live — replace `arXiv:[TBD]` and re-push | 5 min | terminal |
| 11 | Connect Zenodo to GitHub | 3 min | https://zenodo.org/account/settings/github/ |
| 12 | `git tag v0.1.0` + `gh release create` | 5 min | terminal |
| 13 | Capture Zenodo DOI + replace `[zenodo-doi]` placeholders | 5 min | terminal |
| 14 | Apply Claude for Science | 30 min | https://anthropic.com/research |
| 15 | (Optional) send Yim 교수 / Lance Kim outreach emails | 30 min ea | email client |

**Total active time:** ~2.5 hours (excluding the 24–48-hour arXiv moderator wait and 1–4-week C4S processing).

---

**End of document.** When all actions are complete, the project is publicly launched at https://github.com/pinking-jeong/Nonproliferation with arXiv preprint and Zenodo DOI cross-linked.
