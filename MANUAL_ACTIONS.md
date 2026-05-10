# Manual Actions Required

**Generated:** 2026-05-11
**Context:** Steps 1-4 of the user-requested sequence have been completed locally. The items below are the **manual touchpoints** that require user intervention (PI identity, GitHub auth, Anthropic application click, etc.). Sorted by recommended order.

---

## ⚠️ Security first — rotate the OpenRouter key

The OpenRouter key `sk-or-v1-9e69...c84` was shared in chat earlier in this session. The chat transcript may be retained.

**Recommended actions:**

1. https://openrouter.ai/settings/keys → revoke the current key
2. Create a fresh key
3. Update `ospm/.env` (the file is gitignored, never committed)
4. Set a daily spend cap of $5 at https://openrouter.ai/settings/credits
5. (Optional) Re-run `python -m scripts.imagery_vlm_test --aoi natanz` to confirm the new key works

---

## 1. arXiv submission — fill PI info, then submit

The arXiv bundle `os-pm-arxiv-v1-2026-05-10.tar.gz` (16 KB) is built and ready, but has placeholders. You must replace them before clicking Submit.

### 1.1 Files containing placeholders

| File | Lines / fields |
|------|---------------|
| `paper/main.tex` | Lines 49–51: `[Author 1]`, `[Author 2]`, `[Author 3]`<br>Line 88: `[org]` (GitHub URL)<br>Line 89: `[TBD]` (Zenodo DOI)<br>Line 455: `[zenodo-doi]` (in supplementary text)<br>Line 731: `[org]/os-pm` (in availability section)<br>Lines 732–733: two more `[zenodo-doi]` |
| `paper/references.bib` | (none — all generic) |
| `paper/ARXIV_METADATA.md` | Line 23: `[Author 1]^{1}, ...` (your authoring block)<br>Line 73: `[org]/os-pm` |
| `paper/COVER_NOTE.md` | Lines 50, 99: `[Author 1]` + email + ORCID |
| `CITATION.cff` | Lines 8–14: author names + affiliations + ORCIDs<br>Line 49: `arXiv:[TBD]` |
| `.zenodo.json` | Lines 6–13: author names + affiliations + ORCIDs<br>Line 36: `arXiv:[TBD]` |

### 1.2 Quick-fix script (suggested)

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"

# Open each file in your editor and replace placeholders. Examples:
#   [Author 1]    → Yeon-Hong Jeong
#   [Author 2]    → (collaborator name)
#   [Author 3]    → (collaborator name)
#   [Institution 1] → Sample University
#   [org]         → your-github-handle (e.g., yhjeong)
#   [TBD], [zenodo-doi] → leave as "(reservation pending)" if Zenodo not yet linked

# After edits:
grep -nE "\[Author [0-9]+\]|\[Institution [0-9]+\]|\[org\]|\[TBD\]|\[zenodo|\[orcid|\[email\]" paper/main.tex paper/references.bib paper/ARXIV_METADATA.md paper/COVER_NOTE.md CITATION.cff .zenodo.json
# expected: 0 lines

# Rebuild bundle
cd paper && python build_arxiv_bundle.py --version v1
```

### 1.3 Submission steps (arxiv.org)

1. https://arxiv.org/user/login (Use ORCID-linked account)
2. **Submit** → "Start a new submission"
3. License: NLD (recommended) or CC-BY-4.0
4. Categories:
   - Primary: `cs.CY`
   - Cross-list (in order): `physics.soc-ph`, `cs.AI`, `cs.LG`, `eess.IV`
5. Title / Authors / Abstract / Comments: copy from `paper/ARXIV_METADATA.md`
6. Files: upload `arxiv_submission/os-pm-arxiv-v1-2026-05-10.tar.gz`
7. Process → AutoTeX must produce a clean PDF (≈11 pages, 108 KB)
8. Preview → Submit

### 1.4 Endorsement

cs.CY may require endorsement for first-time submitters. If you're not yet endorsed, ask Yim 교수 (KAIST) or Lance Kim 박사 (KAERI) to endorse you for cs.CY (one-line note from them via the arXiv endorsement URL).

### 1.5 After acceptance

- Note the arXiv ID (`arXiv:YYMM.NNNNN`)
- Update `CITATION.cff` and `.zenodo.json` to replace `arXiv:[TBD]` with the real ID
- Commit + push (see Section 2)

---

## 2. GitHub repo — push to a real organisation

The local Git repo is initialised at `ospm/.git`. Initial commit is `d0a3bf9`. The remote does not yet exist.

### 2.1 Create the GitHub repo (3 minutes)

```powershell
# Option A — using gh CLI (recommended; requires "gh auth login" once)
gh auth login                                    # if not already done
gh repo create yhjeong/os-pm --public --source "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm" --remote origin --push --description "OS-PM: VLM-based open-source IAEA Physical Model reconstruction (academic, Apache-2.0)"

# Option B — manual through web
# 1. https://github.com/new
# 2. Repository name: os-pm
# 3. Public, no README/LICENSE/gitignore (we already have them)
# 4. Create
# 5. Then locally:
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
git remote add origin https://github.com/yhjeong/os-pm.git
git push -u origin main
```

Replace `yhjeong` with your actual GitHub handle.

### 2.2 Update `[org]` placeholders

After the repo URL is fixed, replace all `[org]` strings:

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
# Inspect first
grep -rnE "\[org\]" --include="*.md" --include="*.tex" --include="*.cff" --include="*.json" --include="*.bib" --include="*.yml" --include="*.py" .
# Replace (PowerShell)
Get-ChildItem -Recurse -Include *.md,*.tex,*.cff,*.json,*.bib,*.yml,*.py | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace '\[org\]', 'yhjeong' | Set-Content $_.FullName -NoNewline
}
# Re-build bundle
cd paper; python build_arxiv_bundle.py --version v1
# Commit
cd ..; git add -A; git commit -m "chore: replace [org] placeholder with real GitHub handle"; git push
```

### 2.3 Zenodo DOI for the v0.1.0 release

1. Sign in at https://zenodo.org with GitHub
2. Settings → GitHub → enable webhook on `yhjeong/os-pm`
3. Back in GitHub: Releases → "Create a new release" → tag `v0.1.0` → "OS-PM v0.1.0 — Phase 1 release"
4. Zenodo automatically deposits and assigns a DOI (typically `10.5281/zenodo.NNNNNNN`)
5. Update `[zenodo-doi]` placeholders identically to §2.2

### 2.4 GitHub Actions

`.github/workflows/test.yml` is already in the repo — pushing will trigger it automatically. First green run is the "all tests pass on Linux + Windows" badge for the README.

### 2.5 Repository metadata

After pushing, also set up at https://github.com/yhjeong/os-pm/settings:

- Description: "OS-PM: open-source VLM-based reconstruction of the IAEA Physical Model (academic)"
- Website: arXiv link (after submission)
- Topics: `nuclear-safeguards`, `nonproliferation`, `vlm`, `open-source-intelligence`, `iaea`, `acquisition-path-analysis`
- Enable: Issues, Discussions, Sponsorships (optional)
- Branch protection on `main`: require PR, require status checks (`pytest`, `schema-validate`)

---

## 3. Phase 2 imagery VLM — already validated

This step required no manual action; we ran it live and the pipeline works. The outputs are at:

- `data/imagery_vlm/natanz_S2A_39SWT_20241229_0_L2A.jpg` (Sentinel-2 thumbnail, 70 KB)
- `data/imagery_vlm/natanz_vlm_result.json` (VLM structured output)

### 3.1 What we proved
- STAC search → thumbnail download → VLM coarse detect chain works end-to-end
- VLM honestly reports `confidence: 0.1` and `facility_type: uncertain` because thumbnail GSD is too coarse
- VLM uses `geo_ctx` (lat/lon/scene_id/datetime) provided by us to fold in the disclosed Natanz context

### 3.2 What's left as a Phase 2 task (not blocking arXiv v1)
- Download the actual `visual` COG (TCI.tif, ~50–200 MB per scene), crop to a 5 km × 5 km AOI centred on the facility, and re-run Module A
- Add the same flow to Libya / Iraq / Syria
- Compare against the heuristic V05_E08 / V07_E08 / V08_E08 expected indicators

---

## 4. Claude for Science — submit application

The application draft (`docs/Claude_for_Science_application.md`) is now updated with live Phase 2 numbers. Attachments are pre-staged at:

```
arxiv_submission/c4s_attachments/
  OS-PM-preprint.pdf       (108 KB, 11 pages)
  OS-PM-c4s-application.md (your application — sections 1-10)
  OS-PM-demo-deck.md       (7-slide brief)
```

### 4.1 Pre-submit edits

In `docs/Claude_for_Science_application.md` (and the copy in `arxiv_submission/c4s_attachments/`), replace:
- `[Your full name]`, `[Title]`, `[Institution, Department]`, `[name@institution.ac.kr]`, `[0000-0000-0000-0000]`
- `arXiv:[ID]` → real arXiv ID (after step 1)
- `github.com/[org]/os-pm` → real URL (after step 2)

### 4.2 Submit

1. Search "Anthropic Claude for Science" on anthropic.com/research
2. Locate the current application form (URL changes)
3. Paste sections from `OS-PM-c4s-application.md` into the form
4. Attach `OS-PM-preprint.pdf`
5. Submit

### 4.3 After submit

- Save the confirmation email + application ID to `docs/advisory/c4s_app.md` (create the file if needed)
- Add a CHANGELOG entry under `[Unreleased]`: "Submitted Claude for Science application YYYY-MM-DD"

### 4.4 Honest expectations

Approval typically takes 1–4 weeks. The OpenRouter path (already working) is the no-dependency baseline; treat C4S credit as upside, not critical path. If denied, revise based on feedback and re-apply 30 days later.

---

## 5. Optional follow-ups (post-arXiv)

| Task | Trigger | Effort |
|------|---------|--------|
| Send `email_yim_kaist.md` outreach | Immediately after arXiv ID is live | 30 min (personalise) |
| Send `email_lance_kim_kaeri.md` outreach | Same | 30 min |
| First advisory committee meeting | After 2 of 5 seats accept | 90-min meeting |
| Phase 2 imagery COG pipeline | After arXiv submission | 1 week |
| Realistic-negative GNN-light retraining | After negative-class data sourced | 3 days |
| arXiv v2 (Phase 2 results) | Q4 2026 | TBD |
| Submission to S&GS | After arXiv v2 settles | 4–8 weeks review |

---

## 6. Sanity matrix — what's automated vs manual

| Action | Automated this session | Requires user |
|--------|-----------------------|---------------|
| arXiv preprint LaTeX written | ✅ | — |
| arXiv bundle built | ✅ | — |
| arXiv submission web flow | — | **Yes (login + click)** |
| Author info filled | — | **Yes (only you can sign)** |
| `git init`, `git commit` | ✅ | — |
| GitHub repo created | — | **Yes (gh CLI or web)** |
| `git push` | — | **Yes (after auth)** |
| `[org]` placeholder replacement | — | **Yes (after pick handle)** |
| Zenodo DOI generated | — | **Yes (after first GitHub release)** |
| `[zenodo-doi]` placeholder replacement | — | **Yes (after DOI)** |
| Imagery VLM pipeline | ✅ | — |
| Phase 2 COG download + crop | — | (next session) |
| C4S application drafted | ✅ | — |
| C4S form submitted | — | **Yes (form click)** |
| OpenRouter key rotated | — | **Recommended (security)** |
| OpenRouter spend cap set | — | **Yes (settings)** |

---

## 7. Working directory map (where everything lives)

```
ospm/
├── .git/                          local git repo (initial commit d0a3bf9)
├── .env                           OpenRouter key (gitignored, never committed)
├── MANUAL_ACTIONS.md              <- this file
├── paper/
│   ├── main.tex                   manuscript (replace [Author 1] etc.)
│   ├── ARXIV_METADATA.md          arXiv form fields
│   ├── COVER_NOTE.md              outreach letters (en + ko)
│   ├── SUBMISSION_CHECKLIST.md    pre-submit checklist
│   └── build_arxiv_bundle.py      run after edits
├── arxiv_submission/
│   ├── os-pm-arxiv-v1-2026-05-10.tar.gz    upload this to arXiv
│   ├── os-pm-arxiv-v1-2026-05-10.zip       alternative
│   ├── os-pm-arxiv-v1-2026-05-10.pdf       cross-check (108 KB, 11 pages)
│   └── c4s_attachments/                      attachments for Claude for Science
├── docs/
│   ├── Claude_for_Science_application.md   replace PI placeholders, then submit
│   ├── outreach/
│   │   ├── email_yim_kaist.md     PI outreach (personalise + send)
│   │   ├── email_lance_kim_kaeri.md
│   │   └── outreach_tracking.md
│   └── advisory/
│       └── charter.md             v0.1 — ratify at first meeting
└── data/                            (local outputs; gitignored)
    ├── retrofit/full_retrofit_report.json
    ├── retrofit/phase2_ablation.json
    ├── retrofit/imagery_phase2.json
    ├── retrofit/gnn_lite_loo.json
    ├── natanz/natanz_retrofit_report.json
    └── imagery_vlm/natanz_vlm_result.json
```

---

**End of manual-action checklist.**
