---
name: data-and-estimand-audit
description: >-
  Use BEFORE brainstorming or designing any algorithm, when the user has data
  and a research/analysis question. Audit the data and the estimand for the
  failure modes that actually sink bioinformatics projects: donor leakage,
  sample-unit errors (cells as independent replicates), batch confounded with
  phenotype, missing or circular ground truth, train/test patient overlap,
  missingness mechanism, licensing. This is a GATE — if a fatal issue is
  found, stop and fix the data or reframe the question before inventing any
  algorithm. 触发场景：用户有数据 + 研究问题，在头脑风暴/算法设计之前。
---

# Data & Estimand Audit

## Overview
Most bioinformatics projects fail **not** from lacking a clever algorithm, but from **wrong problem definition or data flaws**: donor leakage, cells treated as independent biological replicates, batch perfectly confounded with phenotype, ground truth that doesn't exist or comes from the method being tested. This skill audits the data + estimand **before** any algorithm invention — it is a **GATE**. If a fatal issue is found, stop; fix the data or reframe the question before brainstorm/design.

**Loop position**: `research-intake → data-and-estimand-audit (this, GATE) → brainstorm → viability → ...`

## When to Use
- User has data + a research/analysis question, BEFORE brainstorm or algorithm-design.
- Do not proceed to algorithm invention until the audit passes (or fatal issues are explicitly accepted by the user with documented risk).

**Not for**: pure literature exploration with no data yet; already-decided execution where data integrity is established.

## Core Stance: Question the data and the question, not just the method
- The biggest failures are **upstream** of the algorithm. Audit them first.
- Default to skepticism about: data provenance, sample independence, ground-truth validity, batch/phenotype confounding.

## The Audit — required output (all fields, none optional)
| Field | What to check |
|---|---|
| `biological_unit` | What is ONE independent biological replicate? (donor? tissue? cell?) — **cells are NOT independent replicates of the donor**; this confusion is the #1 error. |
| `observational_unit` | What does one row/sample in the data represent? |
| `estimand` | What EXACTLY is being estimated/predicted? Precise — not "cluster the cells" but "recover known cell-type labels" / "estimate cell-type proportions per region". |
| `cohort_structure` | n donors, n samples, n cells/spot; paired/unpaired; longitudinal? |
| `donor_batch_site` | How are donor / batch / site / platform confounded with each other AND with phenotype? Draw the confound graph. |
| `missingness_mechanism` | Why is data missing? MCAR / MAR / MNAR? (scRNA dropout is MNAR — couples to expression.) |
| `leakage_graph` | Can train/test share donors, patients, batches, or correlated samples? Temporal/spatial leakage? |
| `ground_truth_quality` | Does ground truth exist? Is it **independent** of the method being evaluated? (labels from the same method = circular.) |
| `usable_sample_size` | After accounting for non-independence (donor-level n, not cell-level n), how many independent units? Power is donor-level. |
| `split_strategy` | How to split train/test without leakage — **donor-level split, not cell-level**, if multiple cells per donor. |
| `licensing_privacy` | Can the data be published? Human-subjects/consent/IRB constraints? |
| `fatal_issues` | List any blocking issues that MUST be resolved before algorithm invention. |

## GATE decision
- If `fatal_issues` is non-empty → **STOP**. Present issues to user. Do not proceed to brainstorm/algorithm-design until resolved (or user explicitly accepts risk with documented justification).
- Common fatal issues:
  - donor/patient leakage in train/test (cell-level split when donor-level needed);
  - batch fully confounded with phenotype (unidentifiable — any "difference" could be batch);
  - no ground truth + claim of "validation";
  - cells counted as biological replicates in significance tests (pseudoreplication).

## Common failure modes to hunt (the real project-killers)
- **Donor/patient leakage**: train and test share donors (cell-level split when donor-level needed).
- **Sample-unit error / pseudoreplication**: cells treated as independent replicates of the donor → inflated n, fake significance.
- **Batch-phenotype confounding**: batch perfectly aligned with condition → unidentifiable.
- **Circular ground truth**: labels/evaluation from the method being tested, or a correlated method.
- **Missing ground truth**: claiming "validation" when no independent truth exists.
- **MNAR ignored**: dropout coupled to expression, wrongly treated as MCAR.
- **Sequencing-depth/platform confound**: depth differences mistaken for biology.

## Mandatory Discipline
- MUST state `biological_unit` + `observational_unit` explicitly (most errors come from confusing these).
- MUST draw the leakage/confound graph (donor/batch/site vs phenotype).
- MUST specify `split_strategy` at donor level (not cell level) if multiple cells per donor.
- MUST flag any fatal issue as GATE — do not proceed silently.
- FORBID: proceeding to algorithm design with unresolved fatal issues without explicit user acceptance.

## Red Flags — the audit is probably invalid if:
- `biological_unit` not stated, or "cell" when there are multiple cells per donor (pseudoreplication).
- No leakage graph drawn (can't claim "no leakage" without checking donor overlap).
- Ground truth claimed but its source not stated (circular? independent?).
- `usable_sample_size` counts cells as independent (inflated power).
- Fatal issue found but the audit proceeds anyway without user sign-off.

## Example — fetal brain scMultiome + Stereo-seq
```
biological_unit: donor (each fetal donor = one biological replicate)
observational_unit: cell (scMultiome) / spot or bin (Stereo-seq) — NOT independent replicates
estimand: spatial cell-type composition + within-cell-type cis-regulatory state (NOT "cluster the cells")
cohort_structure: 40 donors (20 DS + 20 control), 6 brain regions each (within-donor paired); 2 donors with Stereo-seq
donor_batch_site: CHECK — are all DS donors from one site/batch? (if so, DS-vs-control is confounded with site → unidentifiable). region is within-donor (paired, OK).
missingness_mechanism: scRNA dropout = MNAR (couples to expression); ATAC sparsity similar — must model, not assume MCAR.
leakage_graph: train/test MUST split at DONOR level — cells within a donor are correlated; Stereo-seq bins within a section are spatially correlated. Cell-level split = leakage.
ground_truth_quality: cell-type labels — from where? If from clustering on THIS data, circular. Need independent reference (published atlas markers, or orthogonal validation).
usable_sample_size: 40 donors (biological n). Millions of cells but NOT independent — statistical power is donor-level (40), not cell-level (millions).
split_strategy: donor-level leave-out (e.g., 5-fold by donor), stratified by DS/control × region.
licensing_privacy: fetal tissue — IRB/consent constraints; verify publishability before claiming "publicly available".
fatal_issues: ["DS donors all from one site → DS-vs-control confounded with site — cannot attribute effect to DS" — GATE, must resolve (balance site across groups, or reframe as site-specific exploratory)].
```

## References
- `crossbio-algo:using-crossbio-algo` — the loop (this skill is the GATE before brainstorm).
- `crossbio-algo:_shared/research-design-handoff` — the loop contract (data audit artifact carries forward; algorithm-design MUST receive it).
