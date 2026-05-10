# Anthropic Claude for Science — Application Draft

**Status:** v0.1 draft for user review. Replace bracketed `[...]` placeholders with the PI's real information before submitting.
**Programme URL (verify before submitting):** Search "Anthropic Claude for Science" on anthropic.com/research; the application form lives there.
**Target outcome:** Academic API credit for OS-PM Phase 2 (imagery + literature VLM analysis).
**Expected processing time:** 1–4 weeks (Anthropic communicates by email).

> **How to use this draft**
> The Claude for Science application form has typical fields (PI, institution, project, model, expected usage). Fill the form using the answers below as a starting point. The wording is intentionally honest and conservative; reviewers tend to reward specificity and ethics over scale.

---

## 1. Principal Investigator

| Field | Value |
|-------|-------|
| Name | `[Your full name]` |
| Title | `[e.g., Assistant Professor / Senior Researcher / PhD candidate]` |
| Affiliation | `[Institution, Department]` |
| Email (institutional) | `[name@institution.ac.kr]` |
| ORCID | `[0000-0000-0000-0000]` |
| Co-PI / collaborators | (Optional) Prof. Man-Sung Yim (KAIST) — pending review; Dr. Lance K. Kim (KAERI) — pending review |
| Country | Republic of Korea |

> **Verification suggestion:** Anthropic typically prefers institutional email over personal gmail. If you do not yet have an institutional address, link your personal email to a verifiable institutional page.

## 2. Project name

```
OS-PM: Open-Source Reconstruction of the IAEA Physical Model — academic
nuclear safeguards system, Phase 2 (vision-language imagery analysis).
```

## 3. Public artefacts (cite at top of application)

- arXiv preprint: `arXiv:[ID after submission]`
- Code repository: `github.com/[org]/os-pm` (Apache-2.0)
- Project description: `OS-PM 프로젝트 종합 현황.md` and `paper/main.pdf` (attach 8-page PDF)
- Scope policy: `pm_schema/V11_weaponization_excluded/_volume_overview.yaml`

## 4. Project summary (≈250 words)

```
OS-PM is an open-source academic reconstruction of the IAEA Physical
Model — the technical backbone of state-level safeguards developed by
Liu and Morsy (1999). The Physical Model itself remains in restricted
IAEA technical-report distribution; only two academic groups (JRC
Ispra under Cojazzi/Renda; FZ-Jülich under Niemeyer) have published
partial reconstructions. We have completed Phase 1, which ships 88
in-scope element cells across 11 of the 12 PM volumes (Volume 11
weaponization is permanently excluded by schema-level policy), six
analysis modules with 57 unit tests passing, and four historical
retrofit cases (Iran-Natanz 2002, Libya 2003, Iraq pre-1991,
Syria-Al-Kibar 2007). The first preprint is at arXiv:[ID].

Phase 2 requires vision-language model access to (i) classify
satellite imagery (Sentinel-2 / Landsat / Sentinel-3 SLSTR thermal)
against the PM cell schema, (ii) read scientific abstracts from
OpenAlex and decide proliferation relevance (eliminating false
positives such as the geophysical "centrifuge" mismatch our Phase 1
heuristic exposed), and (iii) extract HS-coded trade flow signals
from UN COMTRADE narrative descriptions. We pair Anthropic Claude as
primary with Qwen2.5-VL-72B as a reproducibility fallback to ensure
academic openness.

Outputs: a peer-reviewed system paper (target Science & Global
Security), a Phase 2 retrofit ablation, and a public release of
all PM cell schemas under Apache-2.0.

The project is detection-only academic research. Volume 11
weaponization is permanently excluded by design and oversight.
```

(Word count ≈ 250 — adjust per the actual form's character limit.)

## 5. Model and usage

| Field | Value |
|-------|-------|
| Models requested | `claude-sonnet-4.6` (primary), `claude-haiku-4.5` (bulk classification), `claude-opus-4.7` (verification of contested cases) |
| Phase 2 estimated monthly token use | Input: ~50M, Output: ~5M |
| Phase 2 estimated monthly cost (Anthropic direct) | ~$200–400 USD |
| Caching strategy | System prompts and PM-schema RAG context cached per call (90% reduction) |
| Storage | Outputs persisted as JSON to `data/retrofit/`; no model fine-tuning |

> If the form asks for a credit amount, **request the lowest tier first**. Anthropic responds well to honest scoping. You can re-apply for higher tiers once Phase 2 results validate the projected usage.

## 6. Ethical scope and oversight (verbatim where possible)

```
OS-PM is bound by a five-element scope policy:

1. Detection only. The project enables academic safeguards research,
   never operational sanctions or strike planning.
2. Volume 11 weaponization permanently excluded by schema-level
   policy. The exclusion is documented in
   pm_schema/V11_weaponization_excluded/_volume_overview.yaml and
   reaffirmed in the system paper.
3. Open-licensed data only. Sentinel-2 (CC BY), Landsat (Public
   Domain), OpenAlex (CC0), UN COMTRADE (Open Data), EURDEP
   (open) — no classified or distribution-restricted material.
4. Historical, post-disclosure cases only. We do not analyse
   active or undisclosed proliferation cases.
5. Independent oversight. A 5-seat advisory committee (Chair,
   Technical AI/VLM, Technical GIS/RS, Policy, Ethics) reviews
   schema additions, case selections, and public releases.

We commit to compliance with Anthropic's Acceptable Use Policy,
specifically the prohibitions on weapons-related uses. Outputs from
the API are inspected automatically and manually for inadvertent
weapons-relevant content, and any such content is redacted before
release.
```

## 7. Anticipated outputs

| Deliverable | Target | Timeline |
|-------------|--------|----------|
| Phase 2 evaluation report (public) | arXiv v2 | Q4 2026 |
| Peer-reviewed system paper | Science & Global Security | Q1 2027 |
| Open dataset of PM cell schemas | Zenodo with DOI | Released with arXiv v2 |
| Reproducible benchmark harness | GitHub | Continuous |
| Conference talk | INMM Annual Meeting / ESARDA Symposium | 2027 |

## 8. Why Claude (versus alternatives)

```
We evaluated Claude (Anthropic), GPT-4o (OpenAI), Gemini (Google),
and Qwen2.5-VL (Alibaba, open-weight). Phase 1 selected Claude for
three reasons:

1. JSON-conforming structured output is more reliable in our
   prompt-caching regime, which compounds across hundreds of
   per-paper calls.
2. The Anthropic Acceptable Use Policy prohibits exactly the V11
   weaponization content that OS-PM also prohibits, giving us a
   policy-level alignment that simplifies institutional review.
3. Vision performance on satellite imagery rubrics (industrial
   facility classification) is competitive with the closed-source
   alternatives in our internal benchmarking.

We also use Qwen2.5-VL-72B as an open-weight reproducibility check;
the Claude path provides the accuracy ceiling and the Qwen path
provides academic auditability.
```

## 9. Data handling commitments

```
- API outputs are stored locally and shared only via the public
  Apache-2.0 release.
- We do not submit user data to the API; only public source material
  (papers, satellite imagery) is sent.
- We retain logs of which papers/images were sent on which date, for
  reproducibility.
- We do not opt in to API training data collection (Anthropic's
  default is no training on API content; we will not change this).
```

## 10. Optional: letters of support

- `[Yim 교수 (KAIST)]` — pending; will follow up post-arXiv.
- `[Lance K. Kim (KAERI)]` — pending; will follow up post-arXiv.
- `[Advisory committee chair]` — pending appointment.

> **Recommendation:** Submit the application without letters of support first. If denied or deferred, recruit two letters from the PI candidates and re-apply. Anthropic communicates whether letters would help.

---

## A. Application checklist (pre-submit)

- [ ] PI placeholders replaced with real information
- [ ] arXiv preprint published (or at least scheduled — give the date)
- [ ] GitHub repo public (otherwise the link is unverifiable)
- [ ] 8-page PDF attached or linked
- [ ] Scope policy explicitly cited
- [ ] Estimated monthly cost realistic (under-promise; can re-apply)
- [ ] Email is institutional, not personal
- [ ] AUP self-check signed by PI

## B. After submission

- Save the confirmation email + application ID to `docs/advisory/c4s_app.md`.
- If approved: register the credits in console.anthropic.com Billing, switch `VLM_BACKEND=anthropic` in `.env`, and document the change in `CHANGELOG.md`.
- If denied: review the feedback (if any), strengthen the application with letters of support, and re-apply after 30 days.

## C. Honest appraisal

This kind of academic credit programme has a relatively high acceptance rate for well-scoped, ethics-forward, peer-review-targeting projects. OS-PM checks all those boxes; the main risk is timing (Phase 1 preprint must be live first, otherwise reviewers cannot verify the project exists).

The OpenRouter path (`API_key_setup_guide.md` §1) covers Phase 2 even if this application is delayed or denied. Treat C4S credit as an upside, not a critical-path dependency.
