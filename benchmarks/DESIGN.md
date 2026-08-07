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

## Domains (case matrix) — deliberately NOT all scanpy
| case | domain | why included |
|---|---|---|
| sc-rna-imputation | single-cell | the home field (baseline) |
| spatial-mapping | spatial omics | SCOUT's domain |
| **phylo-recombination** | **phylogenetics / virology** | non-scanpy; a viral-genome algorithm (the "virus developer" generality test) |
| variant-calling | genomics | non-scanpy; BCFtools/GATK neighbor |
| metagenomics-strain | metagenomics | non-scanpy |
| protein-interface | proteomics / sequences | non-scanpy |
| survival-clinical-ml | clinical ML | leakage-prone; tests data-audit |
| network-grn | network biology | graph/causal |

Each case is a real research-direction prompt with known failure traps (the grader checks whether
each trap was caught).

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

## Methodology
1. Fix a prompt per case (with known traps).
2. Generate outputs under each mode (the skills are deterministic given the prompt + mode; record seed).
3. Grade each output on the rubric. **Blinded** = the grader does not know which mode produced which output.
4. Report per-dimension delta (mode − no-skill) and a weighted total.

## Honest limitations (MUST state — mirrors adversarial-panel-audit's stance)
- **Same-model grader.** In this pilot the grader is the same model that authored the outputs — it
  is NOT blinded and shares bias. The numbers below are a *methodology demonstration*, not evidence.
  The real benchmark needs **external blinded domain experts** (one per domain) grading anonymized
  outputs. Until then, treat scores as illustrative.
- **Single pilot case.** One case (phylo-recombination) does not establish cross-domain
  generalization; the full 8-domain matrix is the next milestone.
- **Author-of-both bias.** The same agent wrote no-skill and Standard outputs; it may strawman the
  no-skill side. Mitigation in the real eval: different sessions/agents per mode + external graders.

## Status
- ✅ Methodology + rubric + harness (`run_case.py`) + 1 pilot (phylo-recombination, non-scanpy).
- ⬜ Full 8-domain matrix + external blinded grading — the next milestone (v0.3).
