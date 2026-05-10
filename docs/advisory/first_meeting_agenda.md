# OS-PM Advisory Committee — First Meeting Agenda

**Date:** [TBD — target Phase 2 kickoff, 2026-MM-DD]
**Format:** Hybrid (Zoom + KAIST Daejeon meeting room option)
**Duration:** 90 minutes
**Materials:** preprint v1, 7-slide deck, charter v0.1, retrofit_report.json

---

## Agenda (90 min)

### 0. Opening (5 min)
- Roll call, brief introductions
- Confirm quorum (3 of 5)
- Conflicts of interest disclosure (each member, 1 minute)

### 1. Charter ratification (15 min)
- Walk through `charter.md` v0.1
- Discuss amendments
- Vote on v1.0 ratification

### 2. Scope policy reaffirmation (10 min)
- V11 weaponization permanent exclusion
- Operational-strike content out of scope
- Classified material not used
- Active/undisclosed cases not analysed
- Each member affirms (verbal, recorded in minutes)

### 3. Phase 1 review (20 min)
- PI presentation (10 min): preprint summary, retrofit results,
  GNN-light caveats, scope policy implementation
- Q&A (10 min)

### 4. Phase 2 plan (20 min)
- Imagery pipeline activation (Sentinel-2 / Landsat / SLSTR)
- VLM mode activation (pending API key)
- Negative-class data sourcing (declared peaceful programmes)
- Discussion: which Phase 2 milestones require committee approval?

### 5. Governance decisions (15 min)
- Meeting cadence (quarterly default; ad-hoc trigger conditions)
- Minutes archival (`docs/advisory/minutes/YYYY-MM-DD_NN.md`)
- External communication policy (single voice, redacted minutes)
- Confidentiality scope and term

### 6. Action items + next meeting (5 min)
- Capture per-member action items
- Set Q+1 meeting date
- Adjourn

---

## Materials checklist (PI to prepare)

- [ ] Charter v0.1 PDF
- [ ] Preprint v1 PDF (`os-pm-arxiv-v1-2026-05-09.pdf`)
- [ ] 7-slide deck PDF (`PI_demo_deck.md` rendered)
- [ ] Retrofit results JSON (`full_retrofit_report.json`)
- [ ] Scope policy 1-pager (extract from §6.1 of preprint)
- [ ] Conflict-of-interest disclosure template (one per member)

## Minutes template

`docs/advisory/minutes/YYYY-MM-DD_NN.md`:

```markdown
# OS-PM Advisory Committee — Meeting NN

**Date:** YYYY-MM-DD
**Format:** [Zoom / In-person / Hybrid]
**Attendees:** [list]
**Quorum:** ✓ / ✗
**Minutes by:** [PI / member]

## 1. Opening
- ...

## 2. [Agenda item]
- Discussion summary
- Decision: [agreed / deferred / vetoed]
- Vote: [Y/N/A counts]

## ...

## Action items
| Owner | Action | Due |
|-------|--------|-----|
| [name] | [action] | YYYY-MM-DD |

## Next meeting
[date, format]
```

## Conflict-of-interest disclosure template

```
OS-PM Advisory Committee — Conflict of Interest Disclosure

I, [Name], affirm the following as of [date]:

1. Equity or consulting relationships:
   [list, or "None"]

2. Funding relationships potentially conflicting with OS-PM:
   [list, or "None"]

3. Co-authorship or affiliation with active proliferation programmes:
   [list, or "None"]

4. Any other relationship that a reasonable observer might consider
   a conflict of interest:
   [list, or "None"]

I will update this disclosure within 30 days of any change. I commit
to recusing from votes where the conflict is direct or material.

Signature: ____________________  Date: ________
```
