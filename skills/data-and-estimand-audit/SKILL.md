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

## Generalization target determines the rules (read this first)
The severity of every check below — pseudoreplication, the split unit, even the missingness story — is **not universal**; it depends on the population the user wants to generalize to. A pseudoreplication that sinks a "generalize to new donors" claim may be benign for a "new cells within this donor" claim. So the FIRST thing the auditor pins down is the generalization target, and every downstream rule is judged relative to it. Before filling the audit table, the auditor MUST answer (record these as guided sub-questions inside the existing fields — do NOT invent new schema keys):
- `target_population` — what is the world of future samples the conclusion should hold over? (inside the `estimand` field, as the "for whom / over what" clause.)
- `generalization_axis` — generalize to a **new donor**? a **new batch**? a **new site**? a **new cell within a donor**? (record inside `biological_unit`, as the axis the replicate must match.)
- `dependency_structure` — which units are correlated? (cells within a donor? spots within a section? wells within a batch?) — record inside `leakage_graph`.
- `biological_replication_unit` — what counts as ONE independent replicate **for this estimand**? (record inside `biological_unit`.) This is the unit that, if repeated, gives independent information under the chosen generalization axis.
- `split_unit` + `split_unit_justification` — split train/test at what unit, and WHY that unit matches the generalization axis. (record inside `split_strategy`.) A split at a finer unit than the generalization axis is leakage; a split at a coarser unit than necessary throws away power.

The three rules that looked absolute in older versions (cells-as-replicates, scRNA-zero=MNAR, donor-split-mandatory) are all **conditionals** read off this target — see the audit table and "Common failure modes" below.

## The Audit — required output (all fields, none optional)
| Field | What to check |
|---|---|
| `biological_unit` | What is ONE independent biological replicate **for this estimand**? State `biological_replication_unit` + the `generalization_axis` it matches (new donor? new batch? new cell within donor?). Cells within a donor are usually correlated; whether that matters depends on the generalization axis — if generalizing to new donors, donor is the replicate and cell-level n is pseudoreplication. This confusion (cell-level n passed off as biological n) is the #1 error. |
| `observational_unit` | What does one row/sample in the data represent? |
| `estimand` | What EXACTLY is being estimated/predicted, **and over what `target_population`**? Precise — not "cluster the cells" but "recover known cell-type labels" / "estimate cell-type proportions per region"; add the "for whom / over what future samples" clause. |
| `cohort_structure` | n donors, n samples, n cells/spot; paired/unpaired; longitudinal? |
| `donor_batch_site` | How are donor / batch / site / platform confounded with each other AND with phenotype? Draw the confound graph. |
| `missingness_mechanism` | Why is data missing? MCAR / MAR / MNAR — and **why this mechanism for this platform**? Droplet scRNA zeros are NOT automatically zero-inflated dropout; UMI count data often needs no extra zero-inflation, so MNAR is not the default. State the assumed mechanism with justification rather than defaulting to MNAR. "MNAR ignored" is a risk to check, not a universal fact. |
| `leakage_graph` | Can train/test share donors, patients, batches, or correlated samples? Record the `dependency_structure` (cells within donor? spots within section?). Temporal/spatial leakage? |
| `ground_truth_quality` | Does ground truth exist? Is it **independent** of the method being evaluated? (labels from the same method = circular.) |
| `usable_sample_size` | After accounting for non-independence (count at the `biological_replication_unit`, not finer), how many independent units? Power is at the replication-unit level. |
| `split_strategy` | How to split train/test without leakage, **and why at this unit**. State `split_unit` + `split_unit_justification` — the split unit must MATCH the generalization axis (donor-level split when generalizing to new donors; batch/site split when generalizing to a new batch/site). A split finer than the axis = leakage; coarser than needed wastes power. |
| `licensing_privacy` | Can the data be published? Human-subjects/consent/IRB constraints? |
| `fatal_issues` | List any blocking issues that MUST be resolved before algorithm invention. |

## GATE decision
- If `fatal_issues` is non-empty → **STOP**. Present issues to user. Do not proceed to brainstorm/algorithm-design until resolved (or user explicitly accepts risk with documented justification).
- Common fatal issues (all judged RELATIVE to the generalization axis):
  - train/test leakage at a finer unit than the generalization axis (e.g. cell-level split when the claim is about new donors);
  - batch fully confounded with phenotype (unidentifiable — any "difference" could be batch);
  - no ground truth + claim of "validation";
  - pseudoreplication — counting correlated units as independent biological replicates in significance tests (e.g. cells within a donor when the claim generalizes to new donors). Named candidate fatal issue; confirm it actually bites under the stated axis before escalating to fatal.

## Common failure modes to hunt (the real project-killers)
- **Leakage across the generalization axis**: train and test share a unit finer than the axis the claim generalizes over (donor-level claim with cell-level split is the classic).
- **Sample-unit error / pseudoreplication**: correlated units treated as independent replicates → inflated n, fake significance. (Squair et al. show single-cell differential testing inflates false positives when cell-level n is used in place of donor-level n.) Whether this bites depends on the axis: it sinks a "new donor" claim, it may not sink a "new cell within this donor" claim. State `biological_replication_unit`.
- **Batch-phenotype confounding**: batch perfectly aligned with condition → unidentifiable.
- **Circular ground truth**: labels/evaluation from the method being tested, or a correlated method.
- **Missing ground truth**: claiming "validation" when no independent truth exists.
- **Missingness mis-modeled / MNAR assumed by default**: droplet scRNA zeros are not automatically zero-inflated dropout. (Svensson shows droplet scRNA expression counts are NOT zero-inflated — a single negative-binomial count model fits, no extra zero-inflation term.) State the assumed `missingness_mechanism` with justification; defaulting every zero to MNAR is as wrong as defaulting to MCAR. The risk to check is a missingness story asserted without justification.
- **Sequencing-depth/platform confound**: depth differences mistaken for biology.

## Mandatory Discipline
- MUST state `biological_unit` + `observational_unit` explicitly, including `biological_replication_unit` and the `generalization_axis` it matches (most errors come from confusing the replication unit with the observational unit).
- MUST draw the leakage/confound graph (donor/batch/site vs phenotype) and record the `dependency_structure`.
- MUST specify `split_strategy` with a `split_unit` AND a `split_unit_justification` tying the split unit to the generalization axis (e.g. donor-level split "because the claim generalizes to new donors"). No hardcoded "donor-level split" without a justification — the right unit is axis-dependent (donor / batch / site).
- MUST flag any fatal issue as GATE — do not proceed silently.
- FORBID: proceeding to algorithm design with unresolved fatal issues without explicit user acceptance.

## Red Flags — the audit is probably invalid if:
- `biological_unit` not stated, or a `biological_replication_unit` finer than the `generalization_axis` (pseudoreplication: e.g. cell-as-replicate for a new-donor claim).
- No leakage graph drawn (can't claim "no leakage" without checking overlap at the generalization axis).
- `split_strategy` names a split unit but gives no `split_unit_justification`, or the split is finer than the generalization axis.
- `missingness_mechanism` defaulted to MNAR (or MCAR) without a platform/count-model justification.
- Ground truth claimed but its source not stated (circular? independent?).
- `usable_sample_size` counts units finer than `biological_replication_unit` as independent (inflated power).
- Fatal issue found but the audit proceeds anyway without user sign-off.

## Example — fetal brain scMultiome + Stereo-seq
```
biological_unit: donor (each fetal donor = one biological replicate).
  biological_replication_unit: donor.
  generalization_axis: new donor (the DS-vs-control biology claim is about future donors, not future cells of these same donors).
observational_unit: cell (scMultiome) / spot or bin (Stereo-seq) — correlated within donor/section, NOT the replication unit for this estimand.
estimand: spatial cell-type composition + within-cell-type cis-regulatory state (NOT "cluster the cells"), over target_population = future fetal donors of comparable gestational ages.
cohort_structure: 40 donors (20 DS + 20 control), 6 brain regions each (within-donor paired); 2 donors with Stereo-seq.
donor_batch_site: CHECK — are all DS donors from one site/batch? (if so, DS-vs-control is confounded with site → unidentifiable). region is within-donor (paired, OK).
missingness_mechanism: droplet scRNA is UMI count data — not automatically zero-inflated; start from a single negative-binomial count model and justify any extra zero-inflation/dropout term rather than defaulting to MNAR. ATAC sparsity analogous — state the mechanism, don't assume MCAR.
leakage_graph: dependency_structure — cells within a donor are correlated; Stereo-seq bins within a section are spatially correlated. For the new-donor axis the leak-relevant unit is the donor.
ground_truth_quality: cell-type labels — from where? If from clustering on THIS data, circular. Need independent reference (published atlas markers, or orthogonal validation).
usable_sample_size: 40 donors (biological n at the replication unit). Millions of cells but NOT independent at the new-donor axis — power is donor-level (40), not cell-level (millions).
split_strategy: donor-level leave-out (e.g., 5-fold by donor), stratified by DS/control × region.
  split_unit: donor.
  split_unit_justification: "the claim generalizes to NEW donors, so the split must isolate whole donors — a cell-level split would leak each donor's biology into both folds."
licensing_privacy: fetal tissue — IRB/consent constraints; verify publishability before claiming "publicly available".
fatal_issues: ["DS donors all from one site → DS-vs-control confounded with site — cannot attribute effect to DS" — GATE, must resolve (balance site across groups, or reframe as site-specific exploratory)].
```

## Artifact output
In addition to the table above (human-readable), this stage emits **`artifact.json`** (schema: `crossbio_validate/schemas/stage-schemas.json`): `stage_fields = {biological_unit, estimand, fatal_issues, cohort_structure, leakage_graph, split_strategy}`.
This is the **ROOT** of the artifact chain — `estimand` propagates to every downstream stage (design/spec/code MUST match it, validated by cross-stage rule 1), and **`fatal_issues` non-empty = the chain does not continue** (GATE — same blocking semantics as the GATE decision above, now machine-enforceable).

## References
- `crossbio-algo:using-crossbio-algo` — the loop (this skill is the GATE before brainstorm).
- `crossbio-algo:_shared/research-design-handoff` — the loop contract (data audit artifact carries forward; algorithm-design MUST receive it).
- `crossbio_validate/schemas/stage-schemas.json` + `_shared/artifact-validation.md` — the machine-checkable artifact this stage emits (root of the chain).
