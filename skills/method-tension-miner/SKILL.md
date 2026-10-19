---
name: method-tension-miner
description: >-
  Use when a research task needs NEW directions mined from literature evidence —
  BEFORE brainstorming. Extracts structured method cards from the literature,
  finds methodological TENSIONS between methods (reported contradictions,
  incompatible assumptions, unvalidated condition interactions, information
  loss, estimand mismatches, identifiability boundaries, benchmark blind spots),
  and converts each qualified tension into FALSIFIABLE competing hypotheses with
  a discriminating experiment. Honesty rules: no qualified tension is a VALID
  outcome (NO_QUALIFIED_TENSION); facts/inferences/gaps carry different status
  labels; "no papers found" is NEVER "nobody studied it". 触发场景：用户要"找新方向/
  发现创新点/挖掘方法学矛盾/这个领域还有什么可做的"，Publication 模式必跑，Standard
  发现型任务应跑。Runs AFTER data-and-estimand-audit, BEFORE brainstorm.
---

# Method Tension Miner

## Purpose

Turn traceable literature evidence into **methodological tensions**, and tensions into
**falsifiable competing hypotheses** — the raw material brainstorm can build on. This skill
does NOT invent ideas; it finds *disagreements, incompatibilities, and unexamined
combinations* that already live in the evidence, and states each one so an experiment
could tell the explanations apart.

**Utility first, novelty explicit** (P1): a tension is valuable when resolving it changes
method choice or scientific interpretation — not when it merely sounds clever.

**Not every run finds tension.** If nothing meets the bar, report
`no_qualified_tension` with the full search record. Fabricating contradictions to look
productive is the single worst failure mode of this skill (P5).

## Where it sits

```
data-and-estimand-audit (GATE)
   → method-tension-miner   ← this skill (policy per mode: see below)
      → brainstorm          (tension cards are ONE input, never the only one)
```

State machine (`crossbio` CLI):

| Mode | Default policy | Notes |
|---|---|---|
| Quick | `skipped` (pre-recorded reason) | enable with `--tension optional/required` when the user asks for discovery |
| Standard | `optional` | RUN when the task is discovery-type ("find new directions / what's unexplored"); explicit-skip when the user already has the one idea |
| Publication | `required` | cannot be silently skipped; if it cannot run, `crossbio block-stage method_tension --reason SEARCH_UNAVAILABLE --justification ...` |

```bash
crossbio init-run runs/<name> --mode standard --tension required   # discovery-type run
crossbio next runs/<name>            # gate: method_tension must complete-or-skip before brainstorm (publication)
crossbio complete-stage runs/<name> method_tension --artifact-id <id>
crossbio block-stage runs/<name> method_tension --reason SEARCH_UNAVAILABLE --justification "api down"
```

## Workflow

### Step 0 — Scope (FR-01). Record BEFORE searching:
- research question + intended biological use
- target data regime(s): sparsity, sample size, batch structure, spatial resolution, replicate design…
- known candidate methods (if any); target tier (T1–T4)
- literature window, available sources, search budget; user constraints (CPU-only, Python, …)

Missing scope items become EXPLICIT assumptions in `scope` — never silently invented facts.

### Step 1 — Method cards (FR-02). For each method (≥2 cards required to have anything to tension):
estimand / analysis unit / input representation / statistical + biological assumptions /
validated regimes (what the authors ACTUALLY tested) / reported failure modes /
benchmark fairness / evidence refs (paper + supplement + code + version). **Do not infer
algorithm internals from abstracts** — go to the method section, supplement, or source.
The machine schema requires ≥1 assumption per card; honest "assumptions unclear from the
paper" is itself a finding → record it as a tension (`assumption_conflict` candidate or
`identifiability_boundary`), not as a fake assumption.

### Step 2 — Tension candidates (FR-03). Classify by primary type (see
`references/tension-taxonomy.md`); auxiliary labels allowed via free text:

| type | it IS tension when… | machine requirement |
|---|---|---|
| `empirical_contradiction` | different studies report inconsistent results under comparable conditions | every `evidence_refs` entry is `direct` |
| `assumption_conflict` | two methods' assumptions cannot both hold in a named data regime | ≥2 `method_refs` + non-empty `conflict_regime` |
| `unvalidated_interaction` | conditions studied separately, never jointly | `condition_evidence` with ≥2 conditions, each with its own refs |
| `information_loss` | a representation/summary demonstrably drops problem-relevant signal | mechanism + prediction stated |
| `estimand_mismatch` | methods answer different questions; "conflict" dissolves once estimands are stated | both estimands quoted from method cards |
| `identifiability_boundary` | data design cannot distinguish competing mechanisms/parameters | degeneracy named |
| `benchmark_blind_spot` | no benchmark covers a condition critical to the target application | missing condition named |

**Never compared ≠ contradictory** (P2 / AC-03): two methods never tested head-to-head is
`unvalidated_interaction` at best — with a mechanism and a discriminating experiment —
never an `empirical_contradiction`.

### Step 3 — Evidence status (FR-04). Label every tension:
- `observed` — a source DIRECTLY reports the phenomenon/contradiction (validator requires ≥1 `direct` evidence ref)
- `literature_inferred` — you derived it across sources; write the derivation chain in `claim`/`confidence_rationale`; the original papers did NOT say it
- `unverified` — plausible candidate, evidence not yet sufficient. SAY SO.

Never present `unverified` as established; never write "the literature shows X does not
exist" from an empty result set — the honest form is "not found within the searched scope".

### Step 4 — Mechanisms + competing hypotheses (FR-05). For `observed`/`literature_inferred`
tensions: ≥1 testable mechanism, and for IMPORTANT tensions ≥2 COMPETING explanations.
Each: supporting evidence refs / key assumptions / regimes where it holds or fails /
observable difference from rivals / alternative explanations (sample composition,
measurement error, preprocessing differences, estimand mismatch…). If you cannot state
what would distinguish your explanation from "the two studies just used different
samples", you do not have a tension yet — downgrade to `unverified` or drop it.

### Step 5 — Falsifiability (FR-06). Every tension entering the candidate pool needs:
- ≥1 observable prediction
- a minimum discriminating experiment — which outcome supports WHICH explanation, and
  which outcome refutes it ("validate on more data" / "compare several algorithms" do NOT count)
- explicit falsification criteria
- impact if true / impact if false (on method choice or interpretation)

### Step 6 — Novelty status (FR-07). Only four values, ever:
`known_related_work` / `possible_overlap` / `not_found_in_scoped_search` /
`expert_review_required` — with `nearest_related_work` entries, search date, queries,
sources. `not_found_in_scoped_search` REQUIRES recorded coverage limitations. **The
validator structurally cannot certify "first ever" — and so can't you.** Claiming primacy
from keyword-empty search results is forbidden.

### Step 7 — Stop / fallback (FR-08). If nothing qualifies:
`result_status: no_qualified_tension` + sources, queries, dates, coverage, limitations —
then the loop CONTINUES with the normal brainstorm (user problem, paradigm divergence,
cross-domain ideas). A tension-less run is not a failed run. Do not generate filler.

## Output artifact (machine-checked)

One `artifact.json`, stage `method-tension`, chained to the data-audit artifact
(`parent_artifact_id`). Payload under `stage_fields` — full schema in
`crossbio_validate/schemas/stage-schemas.json` (`method_tension_fields`); a complete
worked example in `templates/tension-record.example.json`. Then:

```bash
crossbio stamp artifacts/method-tension.json     # write the correct provenance_hash
crossbio validate artifacts/method-tension.json  # schema + provenance
crossbio complete-stage runs/<name> method_tension --artifact-id <id>
```

The validator checks structure and traceability (dangling refs, status-label honesty,
per-type payload, falsifiability fields, lineage to brainstorm/design) — **it cannot
check that you read the papers correctly or that anything is actually novel (P6)**. A
green validator is a receipt of discipline, not of truth.

## Handoff to brainstorm

Tension cards are ONE input source. Brainstorm must also run its free exploration,
paradigm divergence, and cross-domain rounds; ideas record their origin
(`source: tension | user_problem | paradigm_divergence | cross_domain_transfer`, with
`tension_ids` when tension-derived). For tension-derived ideas the design stage MUST
carry the six tension-resolution fields (see `algorithm-design` SKILL: §8.3 of the spec).

## Prohibited behaviors

- Fabricating or inflating contradictions to fill a quota (novelty theater)
- `unverified`/inferred material presented as `observed` fact
- "no results found" → "nobody has studied this"
- Abstract-only inference about method internals
- Skipping the search-record when reporting no_qualified_tension
- Feeding tensions to brainstorm as the ONLY idea source
- Treating validator-PASS as scientific endorsement
