# arXiv Submission Metadata — OS-PM

**File:** `paper/ARXIV_METADATA.md`
**Use:** Copy fields directly into the arXiv submission form.
**Status:** v0.1 — review before clicking Submit.

---

## Title

```
OS-PM: A Vision-Language-Model-based, Open-Source Reconstruction of the
IAEA Physical Model for Academic Nuclear Safeguards Research
```

(204 chars including spaces; arXiv allows up to ~250.)

## Authors

> **⚠ User input required.** Replace placeholders before clicking Submit.

```
[Author 1]^{1}, [Author 2]^{1}, [Author 3]^{2}

^{1}[Institution 1, Country]
^{2}[Institution 2, Country]
```

Corresponding author email: `[email@example.com]`
ORCID(s): `0000-0000-0000-0000` (recommended for all authors)

## Abstract (final wording for submission)

> arXiv abstract field has a 1920-character limit (including newlines).
> The wording below is **1875 chars** — leaves margin for last-minute edits.

```
The IAEA Physical Model (PM), developed under Programme 93+2, organises
indicators of every nuclear-fuel-cycle process into a 12-volume,
8-element-per-process matrix that underpins state-level acquisition
path analysis (APA). The PM itself remains in restricted technical-
report distribution, limiting independent academic study of state-level
safeguards methodology. We introduce OS-PM, a vision-language model
(VLM)-driven reconstruction that populates the PM matrix using only
open-licensed data — multispectral and SAR satellite imagery, the
OpenAlex bibliographic graph, UN COMTRADE trade flows, and public
environmental-radiation networks — coupled with Bayesian indicator
fusion, expert-elicitation strength estimation, a graph-native APA
layer, and a historical-retrofit validator. We release 88 of the 88
in-scope element cells (Volume 11 weaponization is permanently
excluded by policy) plus 12 volume overviews, six analysis modules
implemented and unit-tested, and a four-case retrofit harness covering
Iran-Natanz (2002), Libya (2003), Iraq pre-1991, and Syria-Al-Kibar
(2007). On Phase 1 (literature-only, no VLM) the validator achieves
top-1 process-identification accuracy of 1.00 across all four cases
but mean posterior 0.29 and ECE 0.71, indicating that ranking is
robust while calibration awaits the imagery and trade modalities
planned for Phase 2. A graph-feature classifier with leave-one-out
cross-validation reaches 1.00 separation between positive and
synthetic-negative samples; we report this with explicit caveats. We
discuss what fraction of the PM is recoverable from open sources,
what is not, and how OS-PM should and should not be used. Code,
prompts, PM-cell schema, and the retrofit harness are released under
Apache-2.0 with an explicit Volume-11-out-of-scope policy.
```

(1875 chars / 1920 limit ✓)

## Comments (free-form, 200 chars)

```
Phase 1 system paper. 8 pages, 4 tables, 1 figure. Code and PM-schema
released under Apache-2.0 at github.com/pinking-jeong/Nonproliferation.
```

## Subject classes (arXiv categories)

### Primary

```
cs.CY  (Computers and Society)
```

Rationale: OS-PM is fundamentally a sociotechnical system at the
intersection of computing and international policy. cs.CY is the natural
arXiv home for academic verification systems.

### Cross-list (in order of relevance)

```
physics.soc-ph    (Physics and Society)            ← nuclear nonproliferation policy
cs.AI             (Artificial Intelligence)        ← VLM-based extraction
cs.LG             (Machine Learning)               ← graph-feature classifier
eess.IV           (Image and Video Processing)     ← satellite imagery analysis
```

Total cross-lists: 4 (arXiv allows up to 4).

### MSC class (optional)

```
68T05   (Learning and adaptive systems)
68T07   (Artificial neural networks)
```

### ACM class (optional)

```
I.2.6   (Learning)
I.4.7   (Image Feature Measurement)
K.4.1   (Public Policy Issues)
```

## License

```
arXiv non-exclusive license to distribute (NLD)
```

Rationale: Compatible with Apache-2.0 source release. CC-BY-4.0 is also
acceptable; NLD is simpler for a first preprint and does not preclude
later journal submission.

## Submission category checks

| Question | Answer |
|----------|--------|
| Has this been submitted to a journal? | No (preprint first). |
| Is this a revision? | v1 (first submission). |
| Multimedia attachments? | None for v1; Phase 2 may add a 2-min screencast. |
| Permissions reviewed? | All citations are own work or properly cited. |
| Ancillary files? | Optional: provide PM cell YAMLs as a supplementary tarball. |

## Submission process notes

1. **Account registration**: All authors should have arXiv accounts
   linked via ORCID before submission.
2. **Endorsement**: cs.CY may require endorsement for first-time
   submitters; check arXiv endorsement rules. If needed, ask Yim/Lance
   Kim or the advisory committee chair to endorse.
3. **Compile cross-check**: Authors should compile the bundle locally
   with `latexmk -pdf -xelatex main.tex` and verify the resulting PDF
   matches the one we submit.
4. **48-hour hold**: arXiv puts new submissions on hold for ~48 hours
   for moderator review. Plan announcement / outreach accordingly.

---

## Pre-submission checklist (must all be ✓)

- [ ] Author names + affiliations + emails finalised (no placeholders)
- [ ] ORCID added for each author
- [ ] Abstract under 1920 chars
- [ ] All `\todo{}` macros removed from `main.tex`
- [ ] PDF compiles without errors or unresolved references
- [ ] Bibliography entries verified (DOIs resolved where applicable)
- [ ] Volume 11 exclusion policy referenced in §6.2
- [ ] Acknowledgments updated (funder, advisory committee)
- [ ] License explicitly mentioned in `LICENSE` and on first PDF page
- [ ] Code repo URL works (currently placeholder `pinking-jeong/Nonproliferation`)
- [ ] Anthropic AUP compliance review (no V11 content via API)
- [ ] Internal review by advisory committee chair (sign-off email)
- [ ] Institutional IRB / DURC sign-off (or note that this is a
      methodological paper not requiring IRB)
- [ ] KOSTI sanity check on export-control implications
