# Artifact Validation — Machine-Checkable Handoff

## Why
Markdown-only handoffs **drift**. Real example: SCOUT's design.md said `TruncatedSVD + svd.transform(np.eye(...))` (a dimension-mismatch bug), but scout.py silently switched to `np.linalg.svd` — the spec never constrained the code, and nobody caught it until expert review. **`artifact.json` makes each stage's output machine-checkable and defines cross-stage consistency rules that catch such drift automatically.**

## Per-stage artifact.json
Each stage emits **`artifact.md`** (human-readable) **+ `artifact.json`** (machine-checkable, schema: `crossbio_validate/schemas/stage-schemas.json`).

### stage_fields (per stage, the structured payload)
| stage | stage_fields (key) |
|---|---|
| data-audit | `biological_unit`, `estimand`, `fatal_issues`, `cohort_structure`, `leakage_graph`, `split_strategy` |
| brainstorm | `candidates:[{title,hypothesis,gap,novelty_locus}]`, `chosen_id` |
| viability | `competitors_by_category`, `viability_dimensions`, `viability_total`, `viability_range`, `should_proceed` |
| design | `problem_definition`, `estimand`, `notation_and_shapes`, `objective_or_likelihood`, `identifiability`, `failure_boundaries`, `complexity` |
| spec | `module_interfaces`, `acceptance_criteria` (each `id` + `traces_to` a failure_boundary + `verification_mode`), `pseudocode_hashes` |
| code | `module_hashes`, `test_results`, `acceptance_status`, `implementations:[{module,source_file,source_sha256}]`, `tests:[{test_id,verifies_ac,status}]` |
| audit | `panel_findings`, `verdict`, `blocking` |

## Cross-stage consistency rules (MUST check — violation = drift = invalid)

1. **estimand continuity**: `design.estimand == data-audit.estimand` (and spec/code carry it forward unchanged). If estimand changed mid-loop, an explicit `estimand_change_justification` field is required; silent change = invalid.

2. **failure_boundary → acceptance (no orphans)**: every item in `design.failure_boundaries` has ≥1 matching `spec.acceptance_criteria` whose `traces_to` field names it. No orphan failure_boundary (uncared-for risk).

3. **notation consistency**: `spec.module_interfaces` (shapes, names) == `design.notation_and_shapes`. The SCOUT bug (design said `X@U`, spec/code diverged) → hash/content mismatch flagged here.

4. **pseudocode → code**: each spec pseudocode block has a content hash in `spec.pseudocode_hashes`; the implemented code must match (or `code.divergence` documents why, with justification).

5. **provenance_hash integrity**: `artifact.provenance_hash == sha256(canonical_json(content))[:12]`. Detects tampering or silent edits.

### Executable-trace rules (DECLARED ≠ TESTED — added v0.2.2)

6. **acceptance → test (no false "tested")**: every `spec.acceptance_criteria` whose `verification_mode` is `automated_test` / `simulation` / `benchmark` MUST have ≥1 matching `code.tests` entry (`verifies_ac == ac.id`) with `status == passed`. A criterion that *declares* a test mode but has no passing test linked is **DECLARED, not TESTED** → invalid. (This is the rule that catches v0.2.1's "all 4 failure_boundaries have a passing test" overclaim.)

7. **documented_limitation ≠ passed**: a criterion with `verification_mode == documented_limitation` MUST NOT have a linked test with `status == passed` — a known limitation cannot be "passed"; its status is `known_limitation`. Scientific software distinguishes *untested-by-design* from *verified*.

8. **source hash integrity**: every `code.implementations` entry's `source_sha256` (the symbol body) AND `module_sha256` (the whole file) are recomputed from disk and compared. The module hash catches edits to a symbol's *dependencies* (e.g. `_sinkhorn`, `_sqdist`) that don't change the symbol's own body (reviewer §5). A mismatch → invalid.

9. **ATTESTED ≠ DECLARED (v0.2.3)**: a `code.tests` entry's `status` is NOT trusted as evidence. `crossbio attest <tests> --out results.json` runs pytest (`--junit-xml`) and records the OBSERVED outcomes; `rule_test_link` attests each test-requiring acceptance_criterion against `results.json`. With `results.json` present, an observed FAILED is an ERROR even if the artifact self-declares `status: passed`; without `results.json`, a self-declared `passed` is only a WARNING (unattested). **The artifact has no authority to declare itself tested** — DECLARED `passed` ≠ TESTED `passed`.

`verification_mode` ∈ {`automated_test`, `simulation`, `benchmark`, `analytic_argument`, `documented_limitation`, `external_validation`}.

## How to validate (IMPLEMENTED — was pseudocode in v0.2.0)

These rules are no longer prose. They are enforced by **`crossbio_validate`** (Python, in this repo's `crossbio_validate/` package, tested in `tests/test_validator.py`):

```bash
crossbio validate-chain <dir>           # validate a dir of artifact.json as a chain
crossbio validate <artifact.json>       # one artifact (schema + provenance only)
crossbio validate-project <dir>         # scan a project dir for artifacts
crossbio stamp <artifact.json>          # authoring helper: write the correct provenance_hash
# or, without installing:  python -m crossbio_validate validate-chain <dir>
```

`validate-chain` runs, for a chain: every artifact against `crossbio_validate/schemas/stage-schemas.json` (intra-stage) + provenance integrity + parent-chain integrity + stage-order + the fatal GATE + the 5 cross-stage rules below. It exits non-zero on any ERROR.

The rule logic (spec — the live code is `crossbio_validate/core.py`):
```python
# rule 5 (provenance): a["provenance_hash"] == sha256(canonical_json({k:v for k,v in a if k!="provenance_hash"}))[:12]
# rule 1 (estimand continuity): design.estimand == data-audit.estimand OR design has estimand_change_justification
# rule 2 (no orphans): for each fb in design.failure_boundaries: exists ac in spec.acceptance_criteria with fb.id in ac.traces_to
# rule 3 (notation consistency): every shape in spec.module_interfaces is declared in design.notation_and_shapes.shapes
#                                  (free-form notation -> WARNING + skip, not a false ERROR)
# rule 4 (pseudocode -> code): for each module in spec.pseudocode_hashes: module in code.module_hashes OR module in code.divergence
# rule 6 (test-link / DECLARED!=TESTED): AC verification_mode in {automated_test,simulation,benchmark} => a code.tests entry verifies_ac=ac.id with status=passed
# rule 7 (limitation != pass): verification_mode=documented_limitation => no linked test may be status=passed (use known_limitation)
# rule 8 (source hash): code.implementations[].source_sha256 recomputed from disk (symbol body) and compared
# also enforced: parent_artifact_id resolves; stage order follows ALLOWED_PARENT_STAGES; fatal_issues non-empty + downstream present => risk_accepted required
```

The drift this catches is real and tested: see `tests/test_validator.py` — each rule has a GREEN case and a deliberately-drifted RED case that MUST fail (estimand drift, orphan failure_boundary, notation mismatch, pseudocode orphan, provenance tamper, dangling parent, stage-order break, fatal-gate violation).

## Integration into the loop
- **handoff contract** (`research-design-handoff.md`): each stage MUST emit `artifact.json` (not just `.md`); downstream stage MUST validate cross-stage rules before proceeding.
- **algorithm-design**: design `artifact.json` carries `estimand + failure_boundaries + notation_and_shapes` (machine-checkable, not just prose).
- **spec-writing**: spec `artifact.json`'s `acceptance_criteria` MUST `traces_to` design's `failure_boundaries` (validated by rule 2, not just claimed).
- **adversarial-panel-audit**: audit can check `artifact.json` chain consistency — drift is now an auditable finding.
- **data-and-estimand-audit**: the chain's root artifact (estimand + fatal_issues propagate forward; everything traces back to it).

## What this prevents (the failure modes it catches)
- **SCOUT-type design-code drift**: spec said TruncatedSVD, code used np.linalg.svd → rule 3/4 catches.
- **Orphan failure_boundary**: design says "fails at reads<5" but no acceptance tests it → rule 2 catches.
- **Silent estimand change**: data-audit says estimand X, design quietly does Y → rule 1 catches.
- **Untracked tampering**: someone edits an artifact without updating provenance → rule 5 catches.
