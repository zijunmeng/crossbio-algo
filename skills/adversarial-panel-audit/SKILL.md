---
name: adversarial-panel-audit
description: Use when a research artifact (a viability verdict, an algorithm design, a spec, or a result/conclusion) has just been produced and is about to be trusted or adopted — before you act on it, commit to it, or hand it downstream. Also when the user says "审一下 / review / 帮我把关 / 这靠谱吗" about any research output, or when you reach a key decision point and want a second adversarial pass. A horizontal quality-assurance layer over the rest of the skill chain.
---

# Adversarial Panel Audit

## Overview
A trusted artifact gets trusted because it survived attack, not because it read well. Spawn an **adversarial panel of same-model subagents** that each play a different expert role and pressure-test the artifact from their angle. Implemented entirely with Claude Code's native Agent tool — **no external models.** Breaks two failure modes: (1) the same Claude that produced an artifact rationalizes it again (confirmation bias); (2) a flaw slides into use and sinks weeks of downstream work.

**Honest naming note:** this is *not* a cross-model audit. Every panel member is the **same Claude**. It is an *adversarial panel of same-model subagents* with information isolation + role specialization. See "Honest Limitation" below for the blind-spot this leaves and the hybrid upgrade path that closes it.

## Core Mechanism — 4 elements, all required
1. **Information isolation.** Each audit subagent receives ONLY the artifact (the conclusion / design / spec / result block) — NEVER the producer's reasoning trace, scratchpad, or rationale. Forced independent judgment.
2. **Multi-role panel.** Spawn 3 subagents in parallel via the Agent tool, each a distinct expert role chosen by audit target from the role menu in `agents/*.md`. Pick 3 of the 6 roles most relevant to the artifact.
3. **Complete the role's checklist, do not invent critique.** Each subagent MUST complete its role's full checklist (`agents/<role>.md`). It is FORBIDDEN to return a vacuous "looks good / no issues" without having run the checklist. BUT a subagent that completes its checklist in good faith and finds **no material issue** SHOULD say so — do NOT manufacture a problem to fill a quota. Forced-finding quotas cause critique inflation (fabricated issues that waste revision cycles). Default to suspicion while *checking*; report what the check actually found.
4. **Structured verdict.** Aggregate the panel → `pass` | `needs_revision` (list the exact fields to fix) | `fail`. Never emit "都挺好".

## The 6 roles (one file each in `agents/`)
| Role | Audits |
|---|---|
| **domain-biologist** | biology premise / mechanism plausibility / is the question biologically sound |
| **statistical-reviewer** | statistical rigor — p-values / multiple testing / effect size / confidence intervals |
| **algorithm-methodologist** | math abstraction / objective / identifiability / complexity |
| **benchmark-auditor** | benchmark fairness / no leakage / naive baseline present |
| **implementation-reviewer** | runnable / interfaces / boundary conditions / edge cases |
| **reproducibility-reviewer** | seeds / environment / data availability / actually reproducible |

Read the relevant `agents/<role>.md` for each role's full checklist before spawning it. **Pick 3** of the 6 for any single audit, chosen by what the artifact is. Optionally add a **defender / replicator** seat (see below).

## Optional — the defender / replicator seat
A 4th (optional) subagent whose job is the *opposite* of the others: **refute or replicate** the findings the other panel members raised. It tries to reproduce each claimed problem from the artifact alone; a finding that cannot be reproduced or is shown to rest on a misread is **downgraded or dropped**. Purpose: filter false positives — the panel is adversarial toward the *artifact*, the defender is adversarial toward the *panel's findings*. Use this whenever the other three raised blocking/severe findings you might act on.

## How to Run
1. Extract the artifact block alone — strip every trace of the producer's reasoning.
2. In ONE message, spawn the 3 panel subagents via the Agent tool (parallel). Each gets: its role (from `agents/<role>.md`) + the isolated artifact + the "complete the checklist, don't manufacture critique" clause. Add a defender/replicator seat if useful.
3. Collect the findings → resolve into the verdict. `pass` only if no panel member raised a **blocking** issue (after defender/replicator filtering).

## Finding format (every issue MUST be structured)
Each finding a subagent raises MUST carry these fields — unstructured "this seems off" is not a valid finding:
```
finding:
  claim:                # one-line statement of the problem
  evidence:             # the concrete artifact text/data/quote that backs it
  severity:             # critical | major | minor
  confidence:           # high | med | low
  reproduction_check:   # how to verify it (reproduce / counter-example / static check). "not checked" is allowed but lowers confidence.
  blocking:             # true | false   (true = must fix before trusting artifact)
  suggested_fix:        # concrete fix, or "none — flag for author" if the reviewer can't prescribe
```
A finding with low confidence + `reproduction_check: not checked` should be treated as a *question*, not a defect, until the defender/replicator (or author) checks it.

## Verdict aggregation
- Collect all findings across the panel.
- If a defender/replicator seat ran, apply its verdict per finding: confirmed / downgraded / refuted.
- **`pass`**: no blocking finding survives. (Zero findings is a valid pass IF each checklist was completed — that is not "looks good", that is a checked-and-clean pass.)
- **`needs_revision`**: ≥1 blocking finding survived; list the exact fields to fix.
- **`fail`**: the artifact is built on a refuted premise / cannot be salvaged field-by-field.

## Honest Limitation (MUST state to the user)
Every subagent is the **same Claude** — they share training bias and the blind spots that come with it. They catch confirmation bias and one-sided framing; they **cannot** catch a flaw that is a blind spot for Claude in general. The information-isolation + role-adversariality + defender/replicator design is a mitigation, not a cure. Optional **hybrid upgrade**: mix in a real external model (DeepSeek / GPT via API) on one panel seat to de-correlate bias — same prompt scaffolding, different base model → genuine multi-perspective + de-correlated. When that seat is occupied, the audit legitimately becomes "cross-model" on that seat; until then it stays honestly "same-model adversarial panel." State this even when you don't use the hybrid option.

## Hard Constraints
- [ ] MUST isolate information — the producer's reasoning trace is never passed to any subagent.
- [ ] MUST have each subagent complete its role's full checklist (`agents/<role>.md`).
- [ ] MUST NOT mandate ≥1 finding per subagent — a checklist completed in good faith that finds no material issue is a valid result. Do not invent critique.
- [ ] MUST FORBID vacuous "looks good" / "no issues" that is NOT backed by a completed checklist.
- [ ] MUST require every finding to be structured (claim/evidence/severity/confidence/reproduction_check/blocking/suggested_fix).
- [ ] MUST emit a structured verdict (`pass` / `needs_revision` + exact fields / `fail`).
- [ ] MUST declare the same-model limitation to the user (and offer the hybrid option).
- [ ] FORBID collapsing the panel into one subagent or having one agent speak for all roles.
- [ ] FORBID skipping the panel on an artifact "because it's short / obvious" — that is exactly when a flaw hides.

## Example — auditing a graph-wavelet imputation design
```
artifact handed to panel (NO reasoning trace): the proposed_algorithm + failure_boundary + simulation_plan block.
panel (pick algorithm-methodologist + benchmark-auditor + implementation-reviewer):
  algorithm-methodologist (CHECKLIST COMPLETE):
    finding:
      claim: "low-pass assumes the signal IS band-limited on the cell graph;
              for lineage-transition genes it's high-frequency by design — untested assumption."
      evidence: "proposed_algorithm step 2 applies a low-pass graph operator unconditionally"
      severity: major
      confidence: high
      reproduction_check: "static — re-read the operator definition; confirmed no high-pass branch"
      blocking: true
      suggested_fix: "state + test the band-limitedness assumption; add a frequency-diagnostic probe"
  benchmark-auditor: (checklist complete; no material issue found on benchmark fairness —
                     naive baseline present, no leakage detected)
  implementation-reviewer:
    finding:
      claim: "naive graph wavelet is O(N²); spec not runnable on CPU without approximation"
      evidence: "simulation_plan complexity row says O(N²), no approximation named"
      severity: major
      confidence: med
      reproduction_check: "not checked (no code to run)"
      blocking: true
      suggested_fix: "specify Nyström approximation; add a sparse-graph scalability probe"
verdict: needs_revision
fields to fix:
  - failure_boundary: add ultra-sparse graph-misconstruction regime.
  - proposed_algorithm: state + test the band-limitedness assumption.
  - simulation_plan: add a sparse-graph scalability probe; specify Nyström.
(note: benchmark-auditor found nothing — that is a checked pass on its checklist, not a failure.)
```

## References
- `agents/*.md` — the 6 role definitions (role + what it audits + checklist). Read the relevant ones before spawning.
- `_shared/research-design-handoff.md` — the viability→design contract; audit inherits its target_tier ruler.
- `cross-domain-inspiration.md` (attachment of **crossbio-algo:algorithm-design**) — when auditing an algorithm design, check inspiration actually crossed domains.
