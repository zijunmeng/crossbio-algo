# SCOUT — Requirements (v0.2.1)

> Acceptance criteria below trace to `design.md` failure_boundaries and to `artifacts/spec.json`
> (validated by `crossbio validate-chain`). v0.2.0 over-claimed (AC-3 scaling, AC-4 SCGLUE/ISON);
> v0.2.1 states only what the code actually does, and moves scaling / external-tool comparison to the Roadmap.

## User Need
A researcher has paired scMultiome (RNA+ATAC, no spatial) + Stereo-seq (spatial RNA, no ATAC) and
wants to infer spatial ATAC via a CPU-only paired-projection, targeting a **T2 tool paper**.

## Goals (from algorithm-design)
Paired-projection integration: use the scMultiome paired prior to give spatial RNA an ATAC dimension,
producing **spatial ATAC + a project confidence/low_confidence flag**.

## Acceptance Criteria (EARS, each traces to a failure_boundary — no orphans)
- **AC-fb1 ← fb1 (out-of-manifold)**: WHEN a spatial spot's nearest paired cell is farther than 3× the
  paired cloud's spacing, THE SYSTEM SHALL flag it `low_confidence=True` and assign the mean paired
  latent as a fallback (not a confident-but-wrong imputation).
- **AC-fb2 ← fb2 (sparse spatial RNA)**: WHEN per-spot RNA reads < `reads_threshold`, THE SYSTEM SHALL
  flag `low_confidence=True` AND still return a latent (fallback), so downstream can down-weight the spot.
- **AC-fb3 ← fb3 (weak pairing)**: WHEN `pairing_strength → 0` (cross-covariance singular values shrink),
  THE SYSTEM's ATAC recovery SHALL collapse toward the naive baseline (the method does not hallucinate
  signal the pairing cannot support).
- **AC-fb4 ← fb4 (batch shift)**: documented limitation — batch shift between paired and spatial is not
  modeled; flagged in the Publication Roadmap (an honest boundary, not a silent failure).
- **AC-bench ← fb1,fb3 (benchmark)**: on semi-synthetic in-manifold data, SCOUT per-peak ATAC recovery
  SHALL exceed the mean-impute and zero baselines (the naive competitors a fair benchmark MUST include).
- **AC-consistency (P0-4)**: `impute(spatial_Z, fit)` SHALL equal `spatial_Z @ fit.B_atac` — the ONE
  cross-modal coefficient also used by the reconstruction check (no shadow formula, no dropped svals).

## Out of Scope (moved to Roadmap, NOT claimed as met)
- **100k spots / CPU <30min / <16GB** (old AC-3): the Sinkhorn here is the reference implementation;
  the mini-batch + POT production path is a Roadmap engineering item, not validated in this example.
- **Beat SCGLUE/ISON by Δ≥0.05** (old AC-4): SCGLUE/ISON are deep-learning/GPU tools whose
  semi-synthetic comparison is an external harness (run them, feed imputed matrices to `_perpeak_corr`);
  this example benchmarks SCOUT against the naive baselines only.
- GRN / cis-regulation inference; cell segmentation.

## Trace Table
| failure_boundary | validates |
|---|---|
| fb1 out-of-manifold | AC-fb1 |
| fb2 sparse spatial RNA | AC-fb2 |
| fb3 weak pairing | AC-fb3 |
| fb4 batch shift | AC-fb4 (documented limitation) |
| benchmark / consistency | AC-bench, AC-consistency |
