# Contributing to OS-PM

Thank you for your interest in OS-PM. This document explains how to
contribute, the scope policy, and the review process.

## TL;DR

1. **Open an issue first** for anything beyond a typo. Significant
   changes (new modules, schema additions, large refactors) require
   buy-in from the core team.
2. **Fork → branch → PR.** Branches should follow `feature/<short-name>`
   or `fix/<short-name>` patterns.
3. **Tests must pass.** Run `pytest tests/` locally before opening a PR.
4. **All Apache-2.0 contributions accepted.** Sign-off (`-s`) is
   appreciated but not strictly required.
5. **Volume 11 is out of scope, period.** See "Scope policy" below.

## Scope policy (non-negotiable)

OS-PM is **detection-only** academic research. The following are
permanently out of scope and will be rejected without review:

- IAEA Physical Model Volume 11 (Weaponization) operational detail
- Critical mass / yield / pit-assembly content
- Implosion / gun-type assembly geometry
- Tritium-boost yield optimisation
- Test-device design parameters
- In-progress / undisclosed case analysis (we only accept retrospective
  cases that have been publicly disclosed)
- Operational sanctions / strike planning content
- Classified or distribution-restricted source material

Additions that materially expand the system's offensive utility will
be rejected. When in doubt, open an issue and ask before writing code.

## Adding a new PM cell

1. Create a YAML file in `pm_schema/V<NN>_<volume_name>/`.
2. Follow the schema in `backend/app/schemas/pm_cell.py`.
3. Add a unit test if the cell uses unusual structure.
4. Ensure `pytest tests/test_apa_graph.py::test_populate_from_pm_schema_runs`
   still passes.

## Adding a new historical case

1. Open an issue describing the case, the public-disclosure event, and
   the proposed cut-off date.
2. The case must already be **publicly disclosed**. We will not accept
   in-progress cases.
3. Add the case to `backend/app/modules/validator.py::HISTORICAL_CASES`.
4. Add per-case collector(s) to `backend/app/modules/case_collectors.py`.
5. Update `tests/test_validator.py`.

## Style

- Python: PEP 8 + ruff (`pyproject.toml` has the config).
- Imports: `from __future__ import annotations` at top of every module.
- Type hints: required on public functions and class attributes.
- Docstrings: short module docstring + per-public-function docstring.
- No emojis in code or docstrings (matches project convention).

## Tests

- Unit tests live in `tests/`. Each module has a corresponding `test_*`.
- Mocks for VLM calls are encouraged (see `tests/test_vlm_collector.py`).
- Coverage target: 80% module-level. We are lenient on the imagery and
  document modules pending Phase 2 wiring.

## Reviews

- Two-reviewer rule for changes to `backend/app/modules/validator.py`,
  `apa_graph.py`, `gnn_lite.py`, and any `pm_schema/V11_*` content.
- One-reviewer rule for everything else.
- The advisory committee chair has the final veto on scope-relevant
  changes.

## Code of Conduct

By participating you agree to follow our `CODE_OF_CONDUCT.md`.

## Questions?

Open a GitHub Discussion or email the maintainers (see `README.md`).
