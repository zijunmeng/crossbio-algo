# Artifact Validation — Machine-Checkable Handoff

## Why
Markdown-only handoffs **drift**. Real example: SCOUT's design.md said `TruncatedSVD + svd.transform(np.eye(...))` (a dimension-mismatch bug), but scout.py silently switched to `np.linalg.svd` — the spec never constrained the code, and nobody caught it until expert review. **`artifact.json` makes each stage's output machine-checkable and defines cross-stage consistency rules that catch such drift automatically.**

## Per-stage artifact.json
Each stage emits **`artifact.md`** (human-readable) **+ `artifact.json`** (machine-checkable, schema: `_shared/artifact-schema.json`).

### stage_fields (per stage, the structured payload)
| stage | stage_fields (key) |
|---|---|
| data-audit | `biological_unit`, `estimand`, `fatal_issues`, `cohort_structure`, `leakage_graph`, `split_strategy` |
| brainstorm | `candidates:[{title,hypothesis,gap,novelty_locus}]`, `chosen_id` |
| viability | `competitors_by_category`, `viability_dimensions`, `viability_total`, `viability_range`, `should_proceed` |
| design | `problem_definition`, `estimand`, `notation_and_shapes`, `objective_or_likelihood`, `identifiability`, `failure_boundaries`, `complexity` |
| spec | `module_interfaces`, `acceptance_criteria` (each `traces_to` a failure_boundary), `pseudocode_hashes` |
| code | `module_hashes`, `test_results`, `acceptance_status` |
| audit | `panel_findings`, `verdict`, `blocking` |

## Cross-stage consistency rules (MUST check — violation = drift = invalid)

1. **estimand continuity**: `design.estimand == data-audit.estimand` (and spec/code carry it forward unchanged). If estimand changed mid-loop, an explicit `estimand_change_justification` field is required; silent change = invalid.

2. **failure_boundary → acceptance (no orphans)**: every item in `design.failure_boundaries` has ≥1 matching `spec.acceptance_criteria` whose `traces_to` field names it. No orphan failure_boundary (uncared-for risk).

3. **notation consistency**: `spec.module_interfaces` (shapes, names) == `design.notation_and_shapes`. The SCOUT bug (design said `X@U`, spec/code diverged) → hash/content mismatch flagged here.

4. **pseudocode → code**: each spec pseudocode block has a content hash in `spec.pseudocode_hashes`; the implemented code must match (or `code.divergence` documents why, with justification).

5. **provenance_hash integrity**: `artifact.provenance_hash == sha256(canonical_json(content))[:12]`. Detects tampering or silent edits.

## How to validate (pseudocode)
```python
import json, hashlib
def h(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:12]

def validate_chain(artifacts):  # artifacts: dict stage->artifact.json
    # rule 5: provenance
    for a in artifacts.values():
        assert a["provenance_hash"] == h({k:v for k,v in a.items() if k!="provenance_hash"})
    # rule 1: estimand continuity
    if "design" in artifacts and "data-audit" in artifacts:
        d_est = artifacts["design"]["stage_fields"]["estimand"]
        a_est = artifacts["data-audit"]["stage_fields"]["estimand"]
        assert d_est == a_est or artifacts["design"].get("estimand_change_justification"), \
            f"estimand drift: data-audit={a_est} vs design={d_est}, no justification"
    # rule 2: failure_boundary -> acceptance (no orphans)
    if "design" in artifacts and "spec" in artifacts:
        fbs = artifacts["design"]["stage_fields"]["failure_boundaries"]
        acs = artifacts["spec"]["stage_fields"]["acceptance_criteria"]
        for fb in fbs:
            assert any(fb["id"] in ac.get("traces_to", []) for ac in acs), \
                f"ORPHAN failure_boundary '{fb}' — no acceptance criterion tests it"
    # rule 3: notation consistency
    if "design" in artifacts and "spec" in artifacts:
        d_not = artifacts["design"]["stage_fields"]["notation_and_shapes"]
        s_iface = artifacts["spec"]["stage_fields"]["module_interfaces"]
        assert shapes_match(d_not, s_iface), "notation drift: design shapes != spec interfaces"
    return True
```

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
