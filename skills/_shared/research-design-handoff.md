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
research-intake  (user has data + research question)
  → data-and-estimand-audit  (GATE before brainstorm: audit data+estimand)
      ✋ fatal_issues non-empty → STOP until resolved or user accepts risk
  → brainstorm  (N candidate ideas)
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
data-and-estimand-audit is a **GATE** — it runs once, before brainstorm, and blocks the loop on fatal issues.

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
- **data-and-estimand-audit**: 审计数据+estimand（biological_unit / leakage / ground_truth / fatal_issues）；产出 data audit artifact；**brainstorm/algorithm-design 必须在 fatal_issues 为空（或用户显式接受风险）后才能开始**。
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

## Machine-Checkable Artifacts (artifact.json)

Markdown-only handoffs **drift**. Real example: SCOUT's design.md said `TruncatedSVD` (a dimension-mismatch bug), but `scout.py` silently switched to `np.linalg.svd` — the spec never constrained the code, and nobody caught it until expert review. To make that drift machine-detectable, **every stage emits TWO artifacts**:

- **`artifact.md`** — the human-readable output this contract already describes (the 16-field design, the kiro three-phase spec, the data-audit table, etc.).
- **`artifact.json`** — a machine-checkable companion whose schema is `_shared/artifact-schema.json` and whose `stage_fields` are the stage's structured payload (see `artifact-validation.md` for the per-stage field table).

### Artifact chain (root → leaf)
```
data-audit  (ROOT)  stage_fields: biological_unit / estimand / fatal_issues / cohort_structure / leakage_graph / split_strategy
   ↓ estimand propagates to ALL downstream stages
design             stage_fields: problem_definition / estimand / notation_and_shapes / objective_or_likelihood / identifiability / failure_boundaries / complexity
   ↓ failure_boundaries + notation_and_shapes propagate to spec
spec              stage_fields: module_interfaces / acceptance_criteria (each traces_to a failure_boundary) / pseudocode_hashes
   ↓
code              stage_fields: module_hashes / test_results / acceptance_status
```
Each artifact carries `parent_artifact_id` forming the chain, and a `provenance_hash` (= `sha256(canonical_json(content))[:12]`) so tampering/silent edits are detectable.

### Downstream stage MUST validate before continuing
Before a stage trusts its input, it runs the 5 cross-stage consistency checks defined in `_shared/artifact-validation.md`:
1. **estimand continuity** — `design.estimand == data-audit.estimand` (silent change = invalid; requires explicit `estimand_change_justification`).
2. **failure_boundary → acceptance, no orphans** — every `design.failure_boundaries` item has ≥1 matching `spec.acceptance_criteria` whose `traces_to` names it.
3. **notation consistency** — `spec.module_interfaces` shapes/names == `design.notation_and_shapes` (the SCOUT TruncatedSVD-vs-np.linalg.svd drift is caught here).
4. **pseudocode → code** — each spec pseudocode hash has matching implemented code (or documented `code.divergence` with justification).
5. **provenance_hash integrity** — `provenance_hash == sha256(canonical_json(content))[:12]`.

**Validation failure = drift = STOP.** Do not proceed to the next stage until the drift is reconciled (fix the downstream artifact, or document an explicit, justified divergence). This is a hard gate, on top of the existing cross-model-audit adversarial gate.

**References**: schema — `_shared/artifact-schema.json`; rules + validation pseudocode — `_shared/artifact-validation.md`.

## One-line summary
> brainstorm generates, viability scores under the user's ruler, design invents under competitor constraint, spec makes it buildable, and audit adversarially checks each — truth carries forward, never restarted, never trusted unchecked, and now machine-checked via the artifact.json chain at every handoff.
