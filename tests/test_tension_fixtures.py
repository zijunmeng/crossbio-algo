"""Fixture tests for the 4 spec-required tension fixtures (Phase 4).

Fixtures (tests/fixtures/tension/):
  1. real-contradiction.json               — empirical_contradiction, observed, direct both sides
  2. fake-contradiction-estimand-mismatch.json — apparent conflict that is REALLY an estimand
                                              mismatch, honestly labeled literature_inferred
  3. evidence-gap-unvalidated-interaction.json — never-compared conditions, condition_evidence
                                              per condition, honest gap labeling
  4. negative-result-chain.json            — END-TO-END chain where the tension-derived
                                              hypothesis is REFUTED by the discriminating
                                              experiment, honestly recorded (kill executed)

Each fixture must validate GREEN as shipped; targeted MUTATIONS must be caught (the fixture
is not just data — it is a specification of what honesty looks like, and the mutations
specify what happens to dishonest variants of it).
"""
import copy
import json
import os

from crossbio_validate import core

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "tension")

DA = core.stamp({"artifact_id": "da-fixture", "stage": "data-audit", "parent_artifact_id": None,
    "skill_version": "0.4.0",
    "stage_fields": {"biological_unit": "donor", "estimand": "the unobserved true count at a dropout position",
        "fatal_issues": [], "cohort_structure": "12 donors", "leakage_graph": "donor split",
        "split_strategy": "donor-level 5-fold"}})


def load(name):
    with open(os.path.join(FIX, name)) as f:
        return json.load(f)


def errs(findings):
    return [f for f in findings if f.severity == "ERROR"]


def restamp(a):
    return core.stamp(a)


# ---------- 1. real contradiction ----------

def test_fixture_real_contradiction_green():
    a = load("real-contradiction.json")
    assert a["stage_fields"]["tensions"][0]["type"] == "empirical_contradiction"
    assert a["stage_fields"]["tensions"][0]["evidence_status"] == "observed"
    assert not errs(core.validate_chain([DA, a]))


def test_fixture_real_contradiction_mutation_indirect_breaks_it():
    a = load("real-contradiction.json")
    a["stage_fields"]["evidence_items"][0]["evidence_strength"] = "indirect"
    restamp(a)
    assert errs(core.validate_chain([DA, a]))  # contradiction must be relabeled


# ---------- 2. fake contradiction (estimand mismatch) ----------

def test_fixture_estimand_mismatch_green():
    """The honest labeling: apparent conflict, different estimands → estimand_mismatch,
    literature_inferred (the diagnosis is synthesis), with the alternative named."""
    a = load("fake-contradiction-estimand-mismatch.json")
    t = a["stage_fields"]["tensions"][0]
    assert t["type"] == "estimand_mismatch"
    assert t["evidence_status"] == "literature_inferred"
    assert not errs(core.validate_chain([DA, a]))


def test_fixture_estimand_mismatch_mutation_observed_without_direct():
    a = load("fake-contradiction-estimand-mismatch.json")
    t = a["stage_fields"]["tensions"][0]
    t["evidence_status"] = "observed"          # claim it was directly observed…
    t["evidence_refs"] = ["E3"]                # …but the diagnosis evidence is INDIRECT
    for e in a["stage_fields"]["evidence_items"]:
        e["evidence_strength"] = "indirect" if e["evidence_id"] == "E3" else e["evidence_strength"]
    a["stage_fields"]["evidence_items"] = [e for e in a["stage_fields"]["evidence_items"] if e["evidence_id"] == "E3"]
    t["method_refs"] = ["M1", "M2"]
    for m in a["stage_fields"]["method_cards"]:
        m["evidence_refs"] = ["E3"]
    restamp(a)
    assert errs(core.validate_chain([DA, a]))  # observed without direct evidence → caught


# ---------- 3. pure evidence gap ----------

def test_fixture_evidence_gap_green():
    a = load("evidence-gap-unvalidated-interaction.json")
    t = a["stage_fields"]["tensions"][0]
    assert t["type"] == "unvalidated_interaction"
    assert len(t["condition_evidence"]) == 2
    assert not errs(core.validate_chain([DA, a]))


def test_fixture_evidence_gap_mutation_dropped_condition_evidence():
    a = load("evidence-gap-unvalidated-interaction.json")
    del a["stage_fields"]["tensions"][0]["condition_evidence"]
    restamp(a)
    assert errs(core.validate_chain([DA, a]))


def test_fixture_evidence_gap_mutation_dangling_condition_ref():
    a = load("evidence-gap-unvalidated-interaction.json")
    a["stage_fields"]["tensions"][0]["condition_evidence"]["sparse-no-batch"] = ["E404"]
    restamp(a)
    assert errs(core.validate_chain([DA, a]))


# ---------- 4. negative result end-to-end ----------

def test_fixture_negative_result_chain_green_with_honest_kill():
    """The hypothesis was refuted; the chain records it honestly: the AC is a
    documented_limitation (NOT passed), the kill executed via component_necessity
    (remove_or_redesign WARNING), tension lineage intact end-to-end."""
    chain = load("negative-result-chain.json")
    findings = core.validate_chain(chain)
    assert not errs(findings), core.format_findings(findings)
    # the honest kill-switch record is present and surfaces as a WARNING
    assert any(f.rule == "component-necessity" and f.severity == "WARNING" for f in findings)
    # lineage: brainstorm cites the tension; design carries the six fields
    de = next(a for a in chain if a["stage"] == "design")
    for fld in core.TENSION_DESIGN_FIELDS:
        assert de["stage_fields"].get(fld), f"design missing {fld}"


def test_fixture_negative_result_mutation_limitation_marked_passed():
    """Overclaim mutation: the refuted hypothesis's test flips to 'passed' → must ERROR."""
    chain = load("negative-result-chain.json")
    co = next(a for a in chain if a["stage"] == "code")
    for t in co["stage_fields"]["tests"]:
        if t["test_id"] == "t2":
            t["status"] = "passed"
    core.stamp(co)
    findings = core.validate_chain(chain)
    assert any(f.rule == "verification-mode" for f in errs(findings))


def test_fixture_negative_result_mutation_design_drops_kill_fields():
    chain = load("negative-result-chain.json")
    de = next(a for a in chain if a["stage"] == "design")
    for fld in ("kill_criteria", "minimum_discriminating_experiment"):
        de["stage_fields"].pop(fld)
    core.stamp(de)
    findings = core.validate_chain(chain)
    assert any(f.rule == "tension-lineage" for f in errs(findings))
