# Changelog

All notable changes to **crossbio-algo**. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/).

## [0.2.4] — 2026-08-09

### OBSERVED -> SOURCE-BOUND ATTESTED (reviewer round 5): the attestation is now bound to the CURRENT SOURCE.
- `crossbio attest --bind <file>` records a `source_snapshot` (hashes of impl + test files at attest time);
  `rule_source_attestation` recomputes current hashes and FAILS if any changed since attest — closes the
  'reuse an old results.json after editing code' hole (git_commit alone can't bind, since attest runs pre-commit).
- env fingerprint upgraded from sha256(python --version) to python+platform+arch+key-package versions.
- multi-test aggregation (§1): acceptance_criterion.test_aggregation (all default / any); rule_test_link no
  longer breaks on the first attested test.
- test code is now hashed (test target auto-bound) — weakening a test assertion flips the snapshot (§2).
- CI now runs `crossbio attest` fresh against the current checkout BEFORE validate-chain.
- Complexity kill-switch: `component_necessity` field + `rule_component_necessity` — when a component is shown
  <= a simpler alternative across pre-registered regimes, decision=remove_or_redesign and the framework warns
  ('simplest surviving model wins'). SCOUT's OT is flagged (PLS-direct >= SCOUT).
- README/pyproject drifts fixed (Status 0.2.4, SCOUT 11 tests, verification_mode enum, '5 rules'->'8').

## [0.2.3] — 2026-08-09

### EXECUTED -> ATTESTED (reviewer round 4): the validator no longer trusts an artifact's self-declared 'passed'.
- `crossbio attest <tests> --out results.json` runs pytest (--junit-xml) and records OBSERVED outcomes;
  rule_test_link attests acceptance_criteria against results.json — a self-declared 'passed' with no
  attested result is only a WARNING (unattested); an observed FAILED is an ERROR even if the artifact says passed.
- source-hash closure (§5): implementations carry `module_sha256` (whole-file) alongside the symbol hash,
  so edits to a module's dependencies (_sinkhorn/_sqdist) flip the hash even when the symbol body is unchanged.
- SCOUT correctness (§2/§3/§4): impute now adds the ATAC intercept `mean_atac` back (B_atac was fit on centered
  ATAC — v0.2.2 dropped it, invisible to Pearson); RMSE metric + nonzero-intercept DGP added. Benchmark mean
  baseline uses TRAINING ATAC (no leakage); PLS-direct (no-OT) baseline added; runs fb3/fb1 regimes.
- HONEST FINDING surfaced by the new baseline: on the synthetic DGP, PLS-direct >= SCOUT (OT does NOT help
  here) — the fixture documents this rather than hiding it behind degenerate mean/zero baselines.
- README drifts fixed (§6): SCOUT 'T2 tool' -> 'T2-targeted research fixture'; 'invents not recombine' retired;
  Quick 'viable' contradiction; loop root = data-audit; test count 21 -> 26; validator 5 -> 8 rules.

## [0.2.2] — 2026-08-08

### Fixed (release blockers)
- CI was red: workflow now installs via `pip install -e \".[test]\"` (PyYAML added to test extras) — single dependency source.
- Version identity unified: `plugin.json` 0.2.0 -> 0.2.2, homepage corrected to `zijunmeng/crossbio-algo`; `tests/test_meta.py::test_all_versions_match` enforces pyproject == plugin.json == CITATION == CHANGELOG.
- Packaging: canonical schema moved INSIDE the package (`crossbio_validate/schemas/`, resolved via `importlib.resources`) so wheels include it; editable install previously masked the `../schemas/` path. CI now runs `python -m build` + wheel install + `crossbio validate-chain` to test the installed-wheel path.
- README scout test count corrected 8 -> 9.

### Theme
- v0.2.2 migrates the validator from DECLARED->TRACED toward **TRACED->TESTED**: real source hashing + FB->AC->TEST->RESULT graph + `verification_mode` (incl. `documented_limitation`).

## [0.2.1] — 2026-08-07

### Added
- Canonical machine schema `schemas/stage-schemas.json` (`$defs` for every stage + top-level `oneOf`) — the single source of truth for all `artifact.json` shapes.
- `crossbio_validate` validator package + `crossbio` console script. `crossbio validate-chain <dir>` runs: jsonschema check → provenance integrity → parent-chain → stage-order → fatal-gate → the 5 cross-stage content rules (estimand continuity / no-orphan failure_boundary / notation consistency / pseudocode→code / provenance). Companion subcommands: `validate` (one artifact), `validate-project` (scan + chain), `stamp` (authoring helper for `provenance_hash`).
- 21 validator tests in `tests/test_validator.py`, including deliberately-drifted RED cases that the validator must catch.
- CI: `.github/workflows/validate.yml` — runs the validator suite plus a skill-frontmatter + plugin-manifest + schema-parse sanity check on every push/PR.
- `requirements.txt` pinning the validator's runtime dep (`jsonschema>=4.21`).
- `CITATION.cff`, `CONTRIBUTING.md`, this `CHANGELOG.md`.

### Changed
- `algorithm-design` contract relabeled and correctly counted: **15 required + 2 optional** (17-field) Formal Method Contract, grouped Problem / Formalization / Algorithm / Guarantees / Validation. (The earlier "16-field" count was a mis-count; the field set itself was already the 17 above.)
- `skills/_shared/artifact-validation.md` — the 5 cross-stage rules now reference a real implemented validator (`crossbio_validate`), not pseudocode.
- `topic-viability-assessment` scoring: the single false-precision point estimate is replaced by a **decision uncertainty band** (pessimistic / base / optimistic), whose width is derived from each dimension's per-dimension confidence/evidence grade. Explicitly framed as a *decision* band, not a statistical confidence interval (no coverage guarantee). The per-dimension arithmetic now closes.
- README refreshed to v0.2.1: correct test counts (21 validator / 9 scout), real repo tree, new Validator section, no stale placeholders.

### Fixed
- 6-field vs Formal-Method-Contract drift reconciled across `spec-writing`, the handoff contract, and `brainstorm` — all now point at the same 15-required + 2-optional design contract.
- Removed the duplicated `_shared/artifact-schema.json`; the schema is now canonical at `schemas/stage-schemas.json` only.

## [0.2.0] — earlier

The "evidence-driven + machine-checkable" rewrite, built on the v0.1 idea-novelty pipeline:

- **7 skills** forming a closed loop: `using-crossbio-algo` (bootstrap), `data-and-estimand-audit`, `brainstorm`, `topic-viability-assessment`, `algorithm-design`, `spec-writing`, `adversarial-panel-audit`.
- **`data-and-estimand-audit` as a hard GATE** — fatal issues (donor leakage, batch confounding, pseudoreplication, circular ground truth, MNAR, …) stop the chain before any algorithm is invented.
- **`adversarial-panel-audit`** — honestly-named same-model subagent panel (6 role-based agents, info-isolated, no forced critique; `defender`/`replicator` roles; structured findings).
- **Three effort modes** — Quick / Standard / Publication — so the full loop isn't forced onto trivial tasks. Auto-inferred from target tier (T1–T4).
- **`artifact.json` handoff concept** — machine-checkable artifacts with estimand continuity, failure_boundary→acceptance traces, notation consistency, pseudocode→code, and provenance hashes (the precursor to the v0.2.1 validator).
- `examples/scout/` flagship: spatial RNA+ATAC integration rebuilt on **PLS + optimal transport** (all-CPU, T2 tool positioning). 8 tests.
