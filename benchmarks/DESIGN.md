# Skill Effectiveness Benchmark — Design

> **The question the plugin must eventually answer (reviewer §18):**
> *Do these 7 skills help a researcher design a better bioinformatics algorithm than a vanilla
> agent without them — specifically, fewer leakage / estimand / benchmark / math / engineering
> errors — across domains, not just single-cell?*

This is the product-evidence gap that distinguishes "a helpful prompt collection" from
"infrastructure that prevents self-consistent-but-wrong evidence chains." It is the future
method-paper (TESTED → SCIENTIFICALLY SUPPORTED). This file is the methodology; one pilot case
(`cases/phylo-recombination/`) seeds it.

## The comparison (independent variable)
For one research-direction prompt, produce the algorithm design under each mode:
- **no-skill** — a vanilla agent given the same prompt with NO crossbio-algo skills loaded (the control).
- **Quick** — `data-and-estimand-audit` + `algorithm-design-lite` + tests.
- **Standard** — `data-audit` + `topic-viability` + full `algorithm-design` + `spec` + 1 audit.
- **Publication** — full loop.

## Domains (case matrix) — 6 of 8 deliberately non-scanpy (the generality test)
Each case lives at `cases/<domain>/` with `prompt.md` (agent-visible research ask, NO answer-key) +
`traps.json` (agent-invisible answer key: trap id → rubric dim). `run_benchmark.py check` enforces
that no `prompt.md` leaks its traps.

| case | domain | scanpy? |
|---|---|---|
| **phylo-recombination** | phylogenetics / virology | no — the "virus developer" test |
| **variant-calling** | genomics (low-depth tumor) | no |
| **metagenomics-strain-tracking** | metagenomics (longitudinal) | no |
| **protein-interface-prediction** | proteomics / structural | no |
| **survival-clinical-ml** | clinical ML | no — leakage-prone |
| **network-grn-inference** | network biology / causal | no |
| scrna-imputation | single-cell | yes — home-field |
| spatial-celltype-deconv | spatial omics | yes — home-field |

## Rubric (dependent variable) — `rubric.json`
10 dimensions, each scored 0–3 with anchors. A "trap" dimension is binary-ish (caught / missed).
| dim | what it scores | trap it catches |
|---|---|---|
| problem_definition | is the problem stated precisely (input/estimand/output)? | vague "build a tool" |
| estimand_correctness | is the estimand exact & correct for the data? | "cluster the cells" non-estimand |
| data_leakage | train/test split at the right unit? donor/sequence/temporal leakage? | cell-level split; using truth as input |
| statistical_assumptions | are count/dropout/independence assumptions stated & matched to data? | NB vs Gaussian; pseudoreplication |
| benchmark_fairness | naive baselines included? same mask/compute? no leakage in eval? | only vs SOTA, omitting mean/kNN |
| novelty_honesty | novelty locus explicit; no overclaim; competitors classified (5 classes)? | "novel" w/o checking |
| implementability | solver + complexity + interfaces stated? | a sketch with no solver |
| failure_boundary_quality | ≥1 derived failure condition (when+mechanism)? | "tested on a benchmark" only |
| reproducibility | seed/env/data-version/pinned deps? | loose `scanpy>=1.10` |
| overall_usefulness | would a senior reviewer advance it? | cheerleading |

## Two evidence streams
**(1) Objective — bias-free, reproducible (primary).** Does the run emit a `crossbio_validate`-passing
artifact chain (`data-audit→design→spec`)? `run_benchmark.py objective <rundirs>` runs the validator.
Standard mode is *defined* to emit such a chain (estimand continuity / no orphan failure_boundary /
no DECLARED-without-TESTED enforced); a no-skill agent does not. This is non-LLM evidence that the
skills produce structural discipline — independent of any grader.

**(2) Rubric — same-model, mode-blinded (secondary).** A grader scores the run's `output.md` on the
10-dim `rubric.json` WITHOUT knowing the mode → `grading.json`. `run_benchmark.py summary` aggregates.
Labeled: same-model, not human-expert.

## Methodology + confound fixes (vs the v0.2 pilot)
1. **Confound (a) prompt/traps split** — `prompt.md` holds only the ask; `traps.json` is the
   agent-invisible answer key. `run_benchmark.py check` fails if a prompt leaks a trap.
2. **Confound (b) non-determinism** — each run records `meta.json` (model, mode, skill_files_loaded,
   run_id). Multi-run = multiple run dirs (single run in this pilot).
3. **Confound (c) strawman no-skill** — no-skill and Standard are generated in **independent
   subagent sessions**; the no-skill session sees ONLY the prompt (no skills, no `CLAUDE.md`, no
   traps) and is instructed to be genuinely competent. Same-model bias remains (documented), not
   eliminated.
4. The **grader is blinded to mode** (receives `output.md` with no mode label).

## Honest limitations (MUST state)
- Rubric stream is **same-model** (glm-5.2), mode-blinded — NOT human-expert, NOT unbiased.
  Author-of-both + author-as-grader bias persists (mitigated by independent sessions + blinded
  grading, not eliminated).
- **Objective stream is bias-free** and is the primary v0.3 evidence.
- Pilot = 2 domains (phylo-recombination + scrna-imputation) × {no-skill, Standard}, single run
  each. Not multi-run, not all 8, not human-graded.

## Status
- ✅ Harness (`run_benchmark.py`: check / objective / summary), rubric, 8 cases seeded, 2-domain pilot run.
- ⬜ **Final milestone (v0.3 complete):** recruit blinded domain experts; run all 8 ×
  {no-skill, Standard, Publication} × N runs; report quality + token/time cost. That is the
  publishable "method paper".
