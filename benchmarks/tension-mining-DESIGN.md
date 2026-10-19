# Tension-Mining Effectiveness Study — A/B/C Design (v0.4.0)

> **The question (spec §11.1):** does `method-tension-miner` raise the yield of
> high-quality methodological hypotheses — not just artifact compliance or text volume?
>
> **STATUS: DESIGNED, NOT RUN.** No pilot data exists yet. This file + `qhy-rubric.json`
> + `TENSION_PILOT_TEMPLATE.md` are the pre-registered protocol. Running it requires
> 27 real agent sessions (see "How the runs happen"). Fabricating these results would
> violate the project's core principle; an empty report is the honest state.

## Groups (independent variable)

| group | environment | workflow |
|---|---|---|
| **A — no-skill** | NO crossbio-algo skills, no CLAUDE.md bootstrap, no traps | vanilla agent, same prompt, same budgets |
| **B — current** | crossbio-algo **v0.3.2** skills (7 skills, tension stage absent/skipped) | data-audit → brainstorm → viability → design → spec |
| **C — enhanced** | crossbio-algo **v0.4.0** (8 skills incl. method-tension-miner, `--tension required`) | data-audit → **method-tension** → brainstorm(tension input) → viability → design(6 fields) → spec |

Held constant across groups: model version, system prompt, retrieval tools, context/time
budget, available literature scope. Any unavoidable mismatch is RECORDED in the report
(deviation log), never silently ignored.

## Primary endpoint — Qualified Hypothesis Yield (QHY)

Per run: the number of independent candidate hypotheses that pass ALL six pre-registered
hard gates (see `qhy-rubric.json` — grader scores each gate binary; a hypothesis is
qualified iff all six are YES):

1. **traceable evidence** — every load-bearing literature claim has source + locator; no fabricated citations (spot-check ≥3)
2. **real delta** — clearly differs from nearest related work, OR explicitly flagged as needing novelty review
3. **mechanism, not recombination** — states a mechanism/assumption tension, not just a new algorithm name or parameter change
4. **discriminating experiment** — an executable experiment whose outcome patterns separate the competing explanations
5. **explicit failure standard** — states what result refutes the hypothesis
6. **worth testing** — the question has real value and matches data the user could plausibly get

AI self-scores are NEVER sufficient for any gate. Report QHY as count/run and its
distribution (not just the mean).

## Secondary endpoints

- evidence-support rate of reported tensions; fraction of evidence-gaps mislabeled as contradictions; novelty overclaim rate; near-duplicate candidate rate; time + token cost per qualified hypothesis; tension→runnable-prototype conversion; cross-domain and cross-run stability.

## Blinding (spec §11.6)

- Graders do not know which group an output came from (strip provenance, shuffle, random IDs).
- ≥2 independent domain graders per output; +1 tie-breaker when they disagree.
- LLM judges may pre-screen, never decide.
- Rubric + gates frozen BEFORE any grading (this file is the freeze).
- Report disagreements, failures, and confidence intervals — not just means.
- Distinguish retrospective rediscovery (re-finding published methods) from prospective originality.

## Pilot (spec §11.3) — 27 runs before anything scales

| case | domain | why chosen |
|---|---|---|
| `cases/scrna-imputation/` | single-cell (home-field) | rich, contradictory imputation literature |
| `cases/phylo-recombination/` | non-home-field | the generality test |
| `cases/network-grn-inference/` | network / causal | tension-dense (causality vs correlation) |

3 cases × 3 groups × 3 independent runs = 27. Freeze after pilot; expansion to all 8
cases × ≥5 runs/group only under the frozen rules. If budget shrinks the design, report
the actual N — never dress a small sample as robust.

## How the runs happen (manual protocol — this is the part CI cannot do)

Each run = one FRESH Claude Code session on one case's `prompt.md`:
- A: no skills installed (check `~/.claude/skills` empty of crossbio skills)
- B: v0.3.2 skills only (git worktree at tag `v0.3.2`, skills copied to `~/.claude/skills`)
- C: v0.4.0 skills (this branch/main after merge) + run started with
  `crossbio init-run runs/<case>-<group>-<n> --mode standard --tension required`
- record in `runs/<...>/meta.json`: model, date, skills versions, token/time, budget
- save the session's hypothesis output verbatim (no post-editing) + any artifacts/

Grading: outputs stripped of group markers → shuffled → graded per `qhy-rubric.json` by
each grader independently → `qhy-grading.json` per output → `run_benchmark.py qhy` aggregates.

## Interpretation boundary (spec §11.7)

Even a significant C>B result means only: under the tested conditions, the module improved
candidate-hypothesis quality. It does NOT mean the system invents theories. Real method
innovation additionally requires completing a candidate through math analysis, implementation,
independent benchmarks, and real-data validation.
