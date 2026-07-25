---
name: cross-model-audit
description: Use when a research artifact (a viability verdict, an algorithm design, a spec, or a result/conclusion) has just been produced and is about to be trusted or adopted — before you act on it, commit to it, or hand it downstream. Also when the user says "审一下 / review / 帮我把关 / 这靠谱吗" about any research output, or when you reach a key decision point and want a second adversarial pass. A horizontal quality-assurance layer over the rest of the skill chain.
---

# Cross-Model Audit

## Overview
A trusted artifact gets trusted because it survived attack, not because it read well. Spawn a **panel of subagents** that each play a different expert and are **forced to find problems**. Implemented with Claude Code's native Agent tool — no external models. Breaks two failure modes: (1) the same Claude that produced an artifact rationalizes it again (confirmation bias); (2) a flaw slides into use and sinks weeks of downstream work.

## Core Mechanism — 4 elements, all required
1. **Information isolation.** Each audit subagent receives ONLY the artifact (the conclusion / design / spec / result block) — NEVER the producer's reasoning trace, scratchpad, or rationale. Forced independent judgment.
2. **Multi-role panel.** Spawn 3 subagents in parallel via the Agent tool, each a distinct expert lens chosen by audit target (table below).
3. **Forced adversariality.** Every subagent prompt MUST contain: "find ≥1 concrete problem, default to suspicion, you are FORBIDDEN to return 'looks good / no issues'." A clean bill of health is treated as a failed audit, not a pass.
4. **Structured verdict.** Aggregate the panel → `pass` | `needs_revision` (list the exact fields to fix) | `fail`. Never emit "都挺好".

## Panel Configuration (by audit target)
| Audit target | Subagent 1 | Subagent 2 | Subagent 3 |
|---|---|---|---|
| **viability assessment** | domain biologist (does the biology premise hold?) | competitor expert ("I shipped stAPAminer — your delta vs mine stands up?") | skeptical reviewer |
| **algorithm design** | methodologist (is the math abstraction sound?) | failure-boundary hunter (where does it break?) | algorithm-implementer (can this actually run on CPU / in scanpy?) |
| **spec** | software engineer | test engineer | requirements-consistency checker |
| **result / conclusion** | statistician (tests, effect sizes, multiple-testing) | overclaim hunter (cherry-picking, overstatement) | biological-plausibility checker |

## How to Run
1. Extract the artifact block alone — strip every trace of the producer's reasoning.
2. In ONE message, spawn the 3 panel subagents via the Agent tool (parallel). Each gets: the role + the isolated artifact + the forced-adversariality clause.
3. Collect the 3 findings → resolve into the verdict. `pass` only if no panel member raised a blocking issue.

## Honest Limitation (MUST state to the user)
Every subagent is the **same Claude** — they share training bias and the blind spots that come with it. They catch confirmation bias and one-sided framing; they **cannot** catch a flaw that is a blind spot for Claude in general. The information-isolation + role-adversariality design is the mitigation, not a cure. Optional **hybrid upgrade**: mix in a real external model (DeepSeek / GPT via API) on one panel seat to de-correlate bias — same prompt scaffolding, different base model → "multi-perspective + de-correlated" double benefit. State this even when you don't use it.

## Hard Constraints
- [ ] MUST isolate information — the producer's reasoning trace is never passed to any subagent.
- [ ] MUST force adversariality — a subagent returning "no issues" counts as a failed audit, not a pass.
- [ ] MUST emit a structured verdict (`pass` / `needs_revision` + exact fields / `fail`); "looks fine" is forbidden.
- [ ] MUST declare the same-model-limitation to the user (and offer the hybrid option).
- [ ] FORBID collapsing the panel into one subagent or having one agent speak for all three roles.
- [ ] FORBID skipping the panel on an artifact "because it's short / obvious" — that is exactly when a flaw hides.

## Example — auditing a graph-wavelet imputation design
```
artifact handed to panel (NO reasoning trace): the proposed_algorithm + failure_boundary + simulation_plan block.
panel (algorithm-design row):
  methodologist:        "low-pass assumes the signal IS band-limited on the cell graph;
                        for lineage-transition genes it's high-frequency by design — untested assumption."
  failure-boundary hunter: "stated boundary 'dropout coupled to expression' under-specifies the
                        real killer: graph mis-construction in ultra-sparse regimes."
  implementer:          "naive graph wavelet is O(N²); needs Nyström approximation to run on CPU — spec not runnable as written."
verdict: needs_revision
fields to fix:
  - failure_boundary: add ultra-sparse graph-misconstruction regime.
  - proposed_algorithm: state + test the band-limitedness assumption.
  - simulation_plan: add a sparse-graph scalability probe; specify Nyström.
```

## References
- `~/.claude/skills/_shared/research-design-handoff.md` — the viability→design contract; audit inherits its target_tier ruler.
- `~/.claude/skills/algorithm-design/cross-domain-inspiration.md` — when auditing an algorithm design, check inspiration actually crossed domains.
