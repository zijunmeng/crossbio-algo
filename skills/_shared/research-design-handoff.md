---
name: research-design-handoff
description: Shared contract chaining the research skills across the FULL loop — brainstorm → topic-viability → algorithm-design → spec-writing, with cross-model-audit as a horizontal QA layer at each handoff. Read when transitioning between stages.
---

# Research → Design → Spec Handoff Contract (full loop)

## Purpose
Keep the skill chain honest across the FULL loop, not just viability→design. Two failure modes this prevents:
1. A stage ignores upstream truth (design ignores viability's competitors; spec ignores design's failure_boundary).
2. cross-model-audit never fires → no adversarial check → silent slop gets trusted.

## The Full Loop
```
brainstorm  (N candidate ideas)
  → topic-viability  (score each under target tier; pick)
      ★ cross-model-audit  (adversarial review of the assessment)
  → algorithm-design  (6-field design, under competitor constraint)
      ★ cross-model-audit  (adversarial review of the design)
  → spec-writing  (executable engineering spec from the 6 fields)
      ★ cross-model-audit  (adversarial review of the spec)
  → code / execution
      ★ cross-model-audit  (adversarial review of results)
```
cross-model-audit is **horizontal** — it fires at EACH ★ before the artifact is trusted.

## The "Honest Colleague" Principle (unchanged)
- No skill vetoes the user. They are counsel, not gatekeeper.
- "Worth doing" is multi-dimensional (target tier). Ask tier first; score under that ruler.
- Every handoff carries upstream truth forward; no stage restarts from a blank slate.

## Target Tiers (unchanged — see topic-viability SKILL for full table)
T1 paradigm-novelty / T2 tool paper / T3 learning / T4 specific-data.

## Handoff Blocks (one per stage transition)
**brainstorm → viability**
```
BRAINSTORM_HANDOFF:
  candidates: [<idea: title/hypothesis/gap/novelty> × N]   # N≥3, ≥1 non-confirming gap
```
**viability → design**
```
VIABILITY_HANDOFF:
  target_tier, verdict, score, top_competitors (+improvable axes), user_choice, locked_angle, design_constraints
```
**design → spec**
```
DESIGN_HANDOFF:
  mathematical_abstraction, cross_domain_inspiration, proposed_algorithm,
  failure_boundary, simulation_plan, novelty_basis   # the 6 fields + carried target_tier
```
**spec → code**
```
SPEC_HANDOFF:
  modules/interfaces, dataflow, pseudocode, deps, tests, acceptance(+engineering_constraints)
```

## Stage obligations
- **brainstorm**: emit ≥3 candidates with ≥1 non-confirming gap; verify trends (no memory); hand off the set.
- **topic-viability**: score under target_tier; if low + user insists → informed choice (accept tier risk / lock improvable axis / supply info); emit VIABILITY_HANDOFF.
- **algorithm-design**: receive VIABILITY_HANDOFF; `novelty_basis` MUST address delta vs each top_competitor (tier-dependent); autonomous run with externalized reasoning, pause only at global forks; emit 6 fields.
- **spec-writing**: receive DESIGN_HANDOFF; spec MUST be executable-level (no vague verbs like "do clustering"); acceptance criteria MUST map to `failure_boundary`; emit SPEC_HANDOFF.
- **cross-model-audit**: at each ★, spawn a subagent panel (info-isolated, role-based, forced-adversarial); emit `pass / needs_revision(exact fields) / fail`. Honest about same-model blind spot.

## Fallback Mechanism — NEVER discard upstream candidates when one idea fails
When an idea/artifact is rejected at viability / audit / design:
1. **Fall back to the remaining candidates from the upstream stage** (e.g. brainstorm R4's *other* ideas) — do NOT discard them. Present them for the user to pick next (or auto-advance by priority).
2. **Always prompt the user**: "Remaining candidates: [X, Y]. Or shall I dev-mode generate N more?"
3. Only when ALL remaining candidates are ALSO rejected → re-run the upstream stage (re-brainstorm) or pivot direction.
- FORBID: jumping to "switch direction / regenerate" and dropping already-generated candidates just because the *picked* one failed.
- (This is the creative-layer analogue of auto-sc's broker `rollback` — extends it from execution to ideation.)

## One-line summary
> brainstorm generates, viability scores under the user's ruler, design invents under competitor constraint, spec makes it buildable, and audit adversarially checks each — truth carries forward, never restarted, never trusted unchecked.
