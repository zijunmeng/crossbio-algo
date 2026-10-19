# Tension-Mining Pilot Report — TEMPLATE (fill per run; NOTHING below may be invented)

> **STATUS: NOT RUN.** This is the pre-registered template. Until real sessions happen,
> every results cell stays `—` and this file's status line stays NOT RUN. The objective
> stream can be recomputed by anyone via `run_benchmark.py`; the QHY stream requires the
> blinded graders' `qhy-grading.json` files committed under each run dir.

- protocol: `benchmarks/tension-mining-DESIGN.md` (frozen before grading)
- rubric: `benchmarks/qhy-rubric.json` (6 hard gates; all-true = qualified)
- code versions: A(no-skill)/B = — · C = commit —
- model(s): — · date(s): — · graders: — (independent, blinded; LLM pre-screen only: —)

## Deviation log (anything not held constant — record ALL, ignore NONE)
| # | planned | actual | impact |
|---|---|---|---|
| — | — | — | — |

## Runs
| case | group | run id | tokens | time | artifacts status | raw output |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

## Primary endpoint — Qualified Hypothesis Yield
| case | A (no-skill) | B (v0.3.2) | C (v0.4.0) |
|---|---|---|---|
| scrna-imputation | — | — | — |
| phylo-recombination | — | — | — |
| network-grn-inference | — | — | — |

per-run values (do NOT collapse to means only): —
inter-grader disagreement: — · confidence interval: —

## Secondary endpoints
| endpoint | A | B | C |
|---|---|---|---|
| evidence-support rate of tensions | — | — | — |
| evidence-gap mislabeled as contradiction | — | — | — |
| novelty overclaim rate | — | — | — |
| near-duplicate candidate rate | — | — | — |
| cost per qualified hypothesis (tokens/time) | — | — | — |

## Failure cases (publish them, don't hide them)
—

## Honest interpretation (§11.7 — even a significant C>B says only "improved candidate
quality under tested conditions", NOT "invents theories")
—

## Release-decision gate check (spec Phase 6)
- [ ] schema/state-machine/compat tests green
- [ ] ≥3 domains end-to-end
- [ ] no systematic gap→contradiction mislabeling observed
- [ ] benchmark data complete & recomputable
- [ ] blinded QHY positive signal, OR negative signal analyzed and design revised
