# Changelog

All notable changes to **crossbio-algo**. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased / 0.2.1] — 2026-08-07

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
- README refreshed to v0.2.1: correct test counts (21 validator / 8 scout), real repo tree, new Validator section, no stale placeholders.

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
