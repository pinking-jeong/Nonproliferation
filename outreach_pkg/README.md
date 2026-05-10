# PI Outreach Package

**For:** Private circulation to Yim 교수 (KAIST), Lance K. Kim 박사 (KAERI), and other selected academic contacts before arXiv submission.
**Generated:** 2026-05-11
**Repository:** https://github.com/pinking-jeong/Nonproliferation
**Status:** Phase 1 v0.1.0 complete; arXiv preprint pending PI sign-off

> **Important.** This package is intended for individual academic recipients during the *pre-arXiv* review window. Do not redistribute. Once the preprint is on arXiv, the public link replaces this private bundle.

---

## How to use this folder

1. Pick the recipient subfolder (`yim_kaist/` or `lance_kim_kaeri/`).
2. Open the `email.md` inside — it has the personalised email body ready to copy into Gmail / Outlook.
3. Attach all three files from `_shared/` to the email:
   - `OS-PM-preprint-v0.1.0.pdf` (108 KB, 11 pages)
   - `OS-PM-demo-deck.md` (7-slide brief, render via `marp` or send as Markdown)
   - `cover-letter.md` (longer formal letter, optional)

If you have time before sending: replace `[Author 1]` / `[Email]` / `[Institution]` placeholders inside `cover-letter.md`. (For the email body in `email.md`, fill `[성명]` / `[소속]` / `[email]` etc.)

---

## Package contents

```
outreach_pkg/
├── README.md                                      ← this file
├── _shared/
│   ├── OS-PM-preprint-v0.1.0.pdf                 11-page system paper
│   ├── OS-PM-demo-deck.md                         7-slide overview (Marp-compatible)
│   └── cover-letter.md                            formal letter template (en + ko)
├── yim_kaist/
│   ├── email.md                                   bilingual outreach email
│   └── attachments_to_include.txt                 checklist for the recipient
├── lance_kim_kaeri/
│   ├── email.md                                   English outreach + JRC Big Table compatibility note
│   └── attachments_to_include.txt
└── tracking.md                                    status tracker (response dates)
```

---

## Pre-send checklist (per recipient)

- [ ] Replace `[성명]` / `[소속]` / `[직위]` / `[email]` / `[orcid]` placeholders in the email body
- [ ] Replace `[제안 날짜 1]` / `[제안 날짜 2]` with two concrete date proposals (~2–3 weeks out)
- [ ] Verify recipient's email address is current (KAIST / KAERI directory or ORCID page)
- [ ] BCC your advisor or institutional contact (optional, for visibility)
- [ ] Test the GitHub link `https://github.com/pinking-jeong/Nonproliferation` in an incognito window
- [ ] Confirm the three attachments open correctly on your machine

## Follow-up cadence

| Day | Action |
|-----|--------|
| 0 | Send email |
| +7 | If no response: gentle follow-up (one paragraph) |
| +14 | If still no response: ask via mutual contact (학회, 동료) |
| Response received | Reply within 24 hours; propose meeting time |
| Post-meeting | Update `tracking.md`, send thank-you note within 24 hours |

---

## After both PIs respond positively

1. Reflect their feedback in `paper/main.tex` (acknowledge in Acknowledgments section)
2. Rebuild arXiv bundle: `cd paper && python build_arxiv_bundle.py --version v1`
3. Submit to arXiv per [`MANUAL_ACTIONS.md`](../MANUAL_ACTIONS.md) §3
4. Once arXiv ID is live, send a brief thank-you with the arXiv link
5. Invite them onto the advisory committee per [`docs/advisory/charter.md`](../docs/advisory/charter.md)

If the response is critical: revise according to feedback, do not submit to arXiv until issues are resolved.

If no response after two follow-ups: continue with arXiv submission anyway, send the arXiv link as a thinner "for your awareness" note.

---

## Privacy note

The recipient list and tracking status (`tracking.md`) are for internal planning only. Do not commit specific recipient details to the public repo. The PI candidate research notes (`docs/PI_candidates_open_source_research.md`) is also internal.
