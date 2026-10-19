"""Method-tension-miner content-rule tests (v0.4.0 — spec §9.3, AC-01..AC-06).

Each machine rule has a GREEN case and a deliberately-broken RED case that MUST be caught:
  - tension-refs      : dangling evidence/method/hypothesis references (AC-01)
  - tension-status    : facts-vs-inference honesty (AC-02/AC-03), honest NO_TENSION (AC-04),
                        blocked-reason, per-type payload requirements
  - tension-lineage   : brainstorm/design tension_ids resolve + tension-derived design carries
                        the six load-bearing fields (AC-06, spec §8.3)

P6 holds: these tests assert STRUCTURE and TRACEABILITY enforcement — none of them can or
should assert that a tension is scientifically true or actually novel.
"""
import json

import pytest

from crossbio_validate import core


# ---- artifact builders (provenance-stamped so rule 5 passes by default) ----

def evidence(eid="E1", strength="direct", **over):
    e = {
        "evidence_id": eid,
        "source_type": "primary_paper",
        "title": "Method A outperforms B on matched donors",
        "year": 2025,
        "doi_or_url": "https://doi.org/10.1234/example",
        "locator": "Table 2",
        "claim_supported": "A > B on matched-donor benchmark",
        "evidence_strength": strength,
        "notes": "",
    }
    e.update(over)
    return e


def method_card(mid="M1", **over):
    m = {
        "method_id": mid,
        "name": "Method " + mid,
        "estimand": "the imputed true expression at a dropout position",
        "analysis_unit": "cell",
        "assumptions": ["dropout is MAR within cell type"],
        "validated_regimes": ["10x v3, 5k cells/sample"],
        "reported_limitations": ["fails on MNAR"],
        "evidence_refs": ["E1"],
    }
    m.update(over)
    return m


def tension(tid="TENS-001", ttype="empirical_contradiction", status="observed", **over):
    t = {
        "tension_id": tid,
        "type": ttype,
        "evidence_status": status,
        "claim": "A and B report opposite orderings on matched conditions",
        "method_refs": ["M1", "M2"],
        "evidence_refs": ["E1", "E2"],
        "mechanism_hypotheses": [
            {
                "hypothesis": "ordering flips because A assumes MAR and the benchmark data is MNAR",
                "supporting_evidence_refs": ["E1"],
                "alternative_explanations": ["sample composition differs across the two studies"],
            }
        ],
        "predictions": ["A's advantage vanishes under explicit MNAR simulation"],
        "discriminating_experiment": "Generate MNAR dropout with known ground truth; if A's RMSE advantage disappears while B's stays, the MAR assumption is the mechanism.",
        "falsification_criteria": ["A retains its advantage under MNAR simulation"],
        "impact_if_true": "A's benchmark wins are regime-specific; benchmarks must include MNAR arms",
        "impact_if_false": "the two results reconcile via sample composition, no method issue",
        "novelty_status": "possible_overlap",
        "nearest_related_work": ["MNAR-simulation benchmark study, 2023"],
        "confidence_rationale": "direct reports on both sides + mechanism consistent with assumptions",
    }
    t.update(over)
    return t


def mt(**over):
    """A fully-compliant method-tension artifact (GREEN baseline)."""
    a = {
        "artifact_id": "mt-1",
        "stage": "method-tension",
        "parent_artifact_id": "da-1",
        "skill_version": "0.4.0",
        "stage_fields": {
            "scope": {
                "research_question": "which imputation method to trust in sparse 10x data",
                "data_regime": ["10x v3", "sparse", "batch-structured"],
                "target_tier": "T2",
                "literature_cutoff_date": "2026-10-01",
            },
            "search_protocol": {
                "sources": ["PubMed", "bioRxiv", "GitHub"],
                "queries": ["scRNA imputation benchmark", "imputation MNAR"],
                "searched_at": "2026-10-19",
                "coverage_limitations": ["no non-English literature", "preprints excluded after 2024-01"],
            },
            "method_cards": [method_card("M1"), method_card("M2", assumptions=["smoothness over kNN graph"], evidence_refs=["E2"])],
            "evidence_items": [
                evidence("E1", strength="direct"),
                evidence(eid="E2", strength="direct", title="Method B outperforms A",
                         claim_supported="B > A on the same matched-donor benchmark"),
            ],
            "tensions": [tension()],
            "result_status": "qualified_tensions_found",
            "limitations": ["single-domain pilot scope"],
        },
    }
    deep = over.pop("stage_fields", None)
    if deep:
        a["stage_fields"].update(deep)
    a.update(over)
    return core.stamp(a)


def da(**over):
    a = {
        "artifact_id": "da-1",
        "stage": "data-audit",
        "parent_artifact_id": None,
        "skill_version": "0.4.0",
        "stage_fields": {
            "biological_unit": "donor",
            "estimand": "the imputed true expression at a dropout position",
            "fatal_issues": [],
            "cohort_structure": "40 donors",
            "leakage_graph": "donor-level split",
            "split_strategy": "donor-level 5-fold",
        },
    }
    a.update(over)
    return core.stamp(a)


def errs(findings):
    return [f for f in findings if f.severity == "ERROR"]


def rules(findings):
    return {f.rule for f in findings}


# ---------- GREEN: schema + all tension rules pass ----------

def test_green_method_tension_artifact_validates():
    findings = core.validate_chain([da(), mt()])
    assert not errs(findings), core.format_findings(findings)


def test_green_in_chain_with_brainstorm_and_design():
    """AC-06: a tension-derived idea flows mt -> brainstorm(tension_ids) -> design(6 fields)."""
    br = core.stamp({
        "artifact_id": "br-1", "stage": "brainstorm", "parent_artifact_id": "mt-1",
        "skill_version": "0.4.0",
        "stage_fields": {
            "candidates": [{
                "title": "regime-aware imputation benchmark",
                "hypothesis": "benchmark orderings flip under MNAR",
                "gap": "no MNAR arm in standard benchmarks",
                "novelty_locus": "evaluation design",
                "source": "tension",
                "tension_ids": ["TENS-001"],
            }],
            "chosen_id": 0,
        },
    })
    de = core.stamp({
        "artifact_id": "de-1", "stage": "design", "parent_artifact_id": "br-1",
        "skill_version": "0.4.0",
        "stage_fields": {
            "problem_definition": "p", "estimand": "the imputed true expression at a dropout position",
            "notation_and_shapes": {"shapes": {"X": "n×g"}},
            "objective_or_likelihood": "l", "identifiability": "i",
            "failure_boundaries": [{"id": "fb1"}], "complexity": "O(n log n)",
            "tension_ids": ["TENS-001"],
            "tension_resolution": "benchmark with explicit MNAR arms resolves the ordering flip",
            "competing_explanations": ["MAR-assumption failure", "sample-composition artifact"],
            "discriminating_predictions": ["A loses advantage under MNAR; B does not"],
            "minimum_discriminating_experiment": "MNAR simulation with known ground truth, both methods",
            "kill_criteria": ["if orderings do not flip under MNAR, abandon the regime-specific claim"],
            "incremental_vs_structural_claim": "evaluation-design change (structural)",
        },
    })
    findings = core.validate_chain([da(), mt(), br, de])
    assert not errs(findings), core.format_findings(findings)


# ---------- RED: dangling references (AC-01) ----------

def test_dangling_evidence_ref_caught():
    a = mt()
    a["stage_fields"]["tensions"][0]["evidence_refs"] = ["E1", "E9"]
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-refs" in rules(findings) and errs(findings)


def test_dangling_method_ref_caught():
    a = mt()
    a["stage_fields"]["tensions"][0]["method_refs"] = ["M1", "M9"]
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-refs" in rules(findings) and errs(findings)


def test_dangling_hypothesis_evidence_ref_caught():
    a = mt()
    a["stage_fields"]["tensions"][0]["mechanism_hypotheses"][0]["supporting_evidence_refs"] = ["E7"]
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-refs" in rules(findings) and errs(findings)


# ---------- RED: facts vs inference (AC-02 / AC-03) ----------

def test_indirect_backed_contradiction_must_relabel():
    """AC-02: a 'contradiction' nobody directly reported is literature_inferred."""
    a = mt()
    a["stage_fields"]["evidence_items"] = [
        evidence("E1", strength="indirect", claim_supported="A wins within its validated regime"),
        evidence(eid="E2", strength="indirect", claim_supported="B wins within a different regime"),
    ]
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)


def test_observed_without_direct_evidence_caught():
    a = mt()
    a["stage_fields"]["evidence_items"][1]["evidence_strength"] = "indirect"
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)


def test_unvalidated_interaction_needs_condition_evidence():
    """AC-03: never-compared methods are unvalidated_interaction, and each condition needs
    its own evidence record — not a claimed contradiction."""
    a = mt()
    a["stage_fields"]["tensions"][0] = tension(
        ttype="unvalidated_interaction", status="literature_inferred",
        condition_evidence={"sparse-10x": ["E1"], "bulk-like-full-depth": ["E2"]},
    )
    core.stamp(a)
    assert not errs(core.validate_chain([da(), a]))  # with condition_evidence: GREEN

    b = mt()
    b["stage_fields"]["tensions"][0] = tension(ttype="unvalidated_interaction",
                                               status="literature_inferred")
    core.stamp(b)
    findings = core.validate_chain([da(), b])
    assert "tension-status" in rules(findings) and errs(findings)  # without: RED


def test_assumption_conflict_needs_two_methods_and_regime():
    a = mt()
    a["stage_fields"]["tensions"][0] = tension(ttype="assumption_conflict", status="literature_inferred")
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)  # missing conflict_regime

    b = mt()
    b["stage_fields"]["tensions"][0] = tension(
        ttype="assumption_conflict", status="literature_inferred",
        method_refs=["M1"],  # only one side
        conflict_regime=["sparse 10x with batch structure"],
    )
    core.stamp(b)
    findings = core.validate_chain([da(), b])
    assert "tension-status" in rules(findings) and errs(findings)


# ---------- RED: honest NO_QUALIFIED_TENSION (AC-04) ----------

def test_no_qualified_tension_green_with_search_record():
    a = mt()
    a["stage_fields"]["tensions"] = []
    a["stage_fields"]["result_status"] = "no_qualified_tension"
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert not errs(findings), core.format_findings(findings)


def test_no_qualified_tension_with_tensions_is_contradictory():
    a = mt()
    a["stage_fields"]["result_status"] = "no_qualified_tension"
    core.stamp(a)
    assert errs(core.validate_chain([da(), a]))


def test_no_qualified_tension_without_coverage_limitations_caught():
    a = mt()
    a["stage_fields"]["tensions"] = []
    a["stage_fields"]["result_status"] = "no_qualified_tension"
    a["stage_fields"]["search_protocol"]["coverage_limitations"] = []
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)


def test_blocked_requires_reason():
    a = mt()
    a["stage_fields"]["result_status"] = "blocked"
    a["stage_fields"].pop("blocked_reason", None)
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)


# ---------- RED: novelty overclaim guard (FR-07 / §9.3 rule 7) ----------

def test_not_found_in_scoped_search_requires_coverage_limitations():
    a = mt()
    a["stage_fields"]["tensions"][0]["novelty_status"] = "not_found_in_scoped_search"
    a["stage_fields"]["search_protocol"]["coverage_limitations"] = []
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "tension-status" in rules(findings) and errs(findings)


def test_schema_rejects_novelty_first_ever():
    """§9.3 rule 9: no enum value can express 'first/novel' — the validator must be unable
    to certify primacy even if asked."""
    a = mt()
    a["stage_fields"]["tensions"][0]["novelty_status"] = "first_ever_proposed"
    core.stamp(a)
    findings = core.validate_chain([da(), a])
    assert "schema" in rules(findings) and errs(findings)


# ---------- RED: lineage (AC-06, §9.3 rule 10) ----------

def test_brainstorm_citing_unknown_tension_caught():
    br = core.stamp({
        "artifact_id": "br-1", "stage": "brainstorm", "parent_artifact_id": "mt-1",
        "skill_version": "0.4.0",
        "stage_fields": {"candidates": [{
            "title": "x", "hypothesis": "h", "gap": "g", "novelty_locus": "n",
            "tension_ids": ["TENS-404"],
        }], "chosen_id": 0},
    })
    findings = core.validate_chain([da(), mt(), br])
    assert "tension-lineage" in rules(findings) and errs(findings)


def test_tension_derived_design_missing_load_bearing_fields_caught():
    de = core.stamp({
        "artifact_id": "de-1", "stage": "design", "parent_artifact_id": "mt-1",
        "skill_version": "0.4.0",
        "stage_fields": {
            "problem_definition": "p", "estimand": "the imputed true expression at a dropout position",
            "notation_and_shapes": {"shapes": {"X": "n×g"}},
            "objective_or_likelihood": "l", "identifiability": "i",
            "failure_boundaries": [{"id": "fb1"}], "complexity": "O(n)",
            "tension_ids": ["TENS-001"],
            # the six §8.3 fields deliberately ABSENT
        },
    })
    findings = core.validate_chain([da(), mt(), de])
    assert "tension-lineage" in rules(findings) and errs(findings)


# ---------- chain topology ----------

def test_method_tension_parent_must_be_data_audit():
    a = mt(parent_artifact_id=None)
    findings = core.validate_chain([da(), a])
    assert "parent-chain" in rules(findings) and errs(findings)


def test_v032_chain_without_tension_artifact_still_validates():
    """AC-05: absence of a method-tension artifact is NOT an error for chains that never ran one."""
    old_style_design = core.stamp({
        "artifact_id": "de-1", "stage": "design", "parent_artifact_id": "da-1",
        "skill_version": "0.3.2",
        "stage_fields": {
            "problem_definition": "p", "estimand": "the imputed true expression at a dropout position",
            "notation_and_shapes": {"shapes": {"X": "n×g"}},
            "objective_or_likelihood": "l", "identifiability": "i",
            "failure_boundaries": [{"id": "fb1"}], "complexity": "O(n)",
        },
    })
    findings = core.validate_chain([da(), old_style_design])
    assert not errs(findings), core.format_findings(findings)
