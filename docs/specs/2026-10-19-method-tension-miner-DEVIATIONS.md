# v0.4.0 Implementation Deviation Report

> Companion to `docs/specs/2026-10-19-method-tension-miner.md` (the SPEC).
> Per SPEC Appendix A constraint 9, every conflict between the SPEC and the implemented
> code is reported here — nothing was silently changed. Status: **all 6 phases delivered;
> release published as capability-complete, effectiveness explicitly NOT claimed.**

## Gate check (SPEC Phase 6)

| gate | status |
|---|---|
| schema / state machine / compatibility tests green | ✅ 95 tests, incl. v0.3.2 chain + manifest compat |
| ≥3 domains end-to-end run successfully | ❌ NOT DONE — requires real LLM sessions; fixtures + template approximate the artifact shapes (see D5) |
| no systematic gap→contradiction mislabeling observed | ⏸ UNTESTED — no real runs yet; machine rule exists and fixture-tested |
| benchmark data complete & recomputable | ◐ harness + rubric + template complete; data absent (D6) |
| blinded review shows positive signal (or analyzed negative) | ❌ NOT RUN (D6) |

**Release decision (per SPEC Phase 6):** shipped as v0.4.0 because the DELIVERED parts
(schema/validator/state machine/skills/tests/docs) meet their acceptance criteria and old
runs stay compatible. The release notes deliberately do NOT claim improved hypothesis
quality — the "creativity-enhanced" claim waits for the pilot. "测试通过 ≠ 方法有用 ≠
方法原创" is stated in README Status, CHANGELOG, and the benchmark DESIGN.

## Deviations

**D1 — Stage naming.** SPEC suggests `method_tension`; implemented `method-tension` (schema,
kebab-case like `data-audit`) and `method_tension` (state machine, snake_case like
`data_audit`). SPEC §7 itself mandates following the existing schema's naming conventions.

**D2 — Payload placement.** SPEC §7's JSON is flat; implemented under the canonical
`stage_fields` envelope. SPEC explicitly says the example is "logical, not copy-replace"
and to reuse the existing envelope.

**D3 — DAG placement in Quick/Standard.** SPEC's flow diagram shows method-tension before
brainstorm universally. Implemented: hard-gated before brainstorm in **Publication only**;
in Quick/Standard it is a parallel optional branch appended after the existing stages.
Reason: AC-05 (v0.3.2 behavior preserved bit-for-bit) + the existing test contracts
(`allowed_stage()` assertions). The enforcement exists exactly where the SPEC's mode table
makes the stage non-skippable; in the other modes the SPEC itself defines it as
skipped/conditional.

**D4 — Quick default skip mechanics.** SPEC: "Quick 默认跳过；必须写明 skip reason".
Implemented as a PRE-RECORDED skip at `init-run` (reason_code NOT_APPLICABLE + v0.4.0
policy justification in the manifest), reversible via `complete-stage`. Alternative
(agent skips at runtime) would add a default gate stop — the recorded default adds zero
cost and is visible in the manifest from the start.

**D5 — Phase 2 acceptance ("3 试点主题生成 schema-valid artifact").** This is an
LLM-runtime property; this implementation session had no budget to run 3 real research
topics through live agents. Delivered instead: a schema-valid worked template
(`skills/method-tension-miner/templates/tension-record.example.json`) + 4 validated
fixtures covering the SPEC's required shapes (real contradiction / estimand-mismatch fake
contradiction / evidence gap / negative-result chain). Real-theme runs are folded into the
benchmark pilot (D6).

**D6 — Phase 5 pilot NOT RUN.** The 27-run A/B/C pilot requires 27 fresh agent sessions
with controlled skill environments plus ≥2 blinded human-domain graders — outside this
implementation. Delivered: pre-registered protocol (`tension-mining-DESIGN.md`), frozen
6-gate rubric (`qhy-rubric.json`), honest report template (`TENSION_PILOT_TEMPLATE.md`,
STATUS: NOT RUN), and the `run_benchmark.py qhy` aggregator (ungraded runs print UNGRADED,
never imputed). SPEC constraint 8 forbids fabricating these numbers; an empty report is
the honest state.

**D7 — SPEC §9.3's 12 machine rules → 11 implemented + 1 structural.** Rules 1-8, 10 are
code (`tension-refs` / `tension-status` / `tension-lineage` families); rule 9 (validator
never upgrades novelty) is enforced STRUCTURALLY — the novelty enum has no first/novel
value (tested: `test_schema_rejects_novelty_first_ever`); rule 11 reuses the existing
executable-trace rules (test-link family) unchanged; rule 12 (validator ≠ scientific
backing) is a documentation guarantee embedded in schema descriptions, rule docstrings,
README, and the skill's prohibited-behaviors list.

**D8 — One rule added beyond the SPEC.** `finalize` treats a completed `method_tension`
without `artifact_id` as a phantom completion (missing item) — the same discipline the
state machine already applies to other required stages; without it the stage could be
"completed" with no deliverable.

## What was NOT changed (per SPEC §3.2 non-goals)

No rewrite of the validator/artifact chain/three-mode system; no GPU dependency added;
no LLM-self-score novelty evidence anywhere; `examples/scout/` untouched; v0.3.2 chains,
manifests, and CI paths unchanged in behavior.
