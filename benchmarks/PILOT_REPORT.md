# v0.3 Pilot Report — skill-effectiveness benchmark (2 domains)

> The question: do the crossbio-algo skills make AI-designed bioinformatics algorithms more
> scientifically sound than a vanilla agent — across domains, not just neater chains? This pilot is
> a **methodology demonstration on 2 of 8 domains**, with two evidence streams. It is NOT the
> blinded human-expert eval (the final milestone).

## Setup
- **2 domains** × **2 modes** ({no-skill, Standard}), single run each. `phylo-recombination`
  (non-scanpy / viral genomics — the generality test) + `scrna-imputation` (home-field single-cell).
- **no-skill**: an independent subagent session given the `prompt.md` ONLY (no skills, no `CLAUDE.md`,
  no traps), instructed to be genuinely competent. **Standard**: an independent session given the
  prompt + the Standard-mode skill chain, asked to emit the `artifact.json` chain.
- 8 cases total are seeded; the other 6 are not run in this pilot.
- Run metadata in each `runs/<mode>-1/meta.json` (model, mode, skill_files_loaded, bias note).

## Evidence stream 1 — OBJECTIVE (bias-free, reproducible) — the primary result
`run_benchmark.py objective` runs `crossbio_validate` on each run's `artifacts/`.

| case | no-skill | Standard |
|---|---|---|
| phylo-recombination | **absent** (0 artifacts) | **valid** (3 artifacts, 0 errors) |
| scrna-imputation | **absent** (0 artifacts) | **valid** (3 artifacts, 0 errors) |

Both Standard runs emit a validator-passing `data-audit→design→spec` chain (estimand byte-identical
across stages, every failure_boundary traced by an acceptance_criterion, provenance intact). Neither
no-skill run emits any artifact chain. **This is non-LLM evidence**: the skills structurally force a
discipline (explicit estimand + leakage audit + failure boundaries + traced acceptance) that a
vanilla agent does not produce, on both a home-field and a non-scanpy domain.

## Evidence stream 2 — RUBRIC (same-model glm-5.2, mode-blinded) — secondary
A grader subagent scored each `output.md` on the 10-dim `rubric.json` **without knowing the mode**
(anonymized `/tmp/gN.md`; domain known, mode not). `run_benchmark.py summary`:

| case | no-skill (rubric / traps) | Standard (rubric / traps) | Δrubric |
|---|---|---|---|
| phylo-recombination | 0.88 / 5-of-6 | 1.00 / 6-of-6 | **+0.12** |
| scrna-imputation | 0.71 / 1-of-6 | 0.98 / 6-of-6 | **+0.27** |

The gaps are on exactly the discipline dimensions the skills target:
- **phylo no-skill** missed the **clade/parent-pair leakage split (T2)** + reproducibility (no
  pinned seeds/deps). It was otherwise competent (caught T1,T3–T6) — **not a strawman**, which makes
  the Standard advantage on the leakage + reproducibility dims more credible.
- **scrna no-skill** defaulted to **MNAR/zero-inflation without justification (T2)**, used an
  **expression-coupled validation mask with no leakage check (T3)**, and **omitted naive baselines
  (T5)** — the classic single-cell imputation errors. Standard caught all of these.

## What this shows / does NOT show
**Shows (provisionally):** on 2 domains, Standard mode (a) emits a machine-validated evidence chain
no-skill never produces (objective, bias-free), and (b) catches the leakage / assumption / benchmark
traps the no-skill agent misses on the discipline dimensions (rubric, same-model blinded).

**Does NOT show:**
- Not **human-expert** evidence — the grader is the same model (glm-5.2) that authored both sides.
  Author-of-both + author-as-grader bias persists (mitigated by independent sessions + mode-blinding,
  not eliminated).
- Not **multi-run** — one run per cell; LLM non-determinism not characterized.
- Not **all 8 domains** — 2 of 8.
- Not **Publication mode** — only no-skill vs Standard.
- The rubric deltas are **small** (0.12 on phylo, where no-skill was already strong). The robust,
  bias-free signal is the **objective stream** (valid chain vs absent), not the rubric magnitudes.

## Final milestone (v0.3 complete)
Recruit **blinded domain experts** (one per domain); run all 8 × {no-skill, Standard, Publication} ×
N runs; report quality **and** token/time cost (does the skill discipline justify its overhead?). That
is the publishable "method paper" — the answer to whether crossbio-algo is research methodology, not
just engineering.
