"""Validator tests — each cross-stage rule + chain check has a GREEN case and a
deliberately-drifted RED case that MUST be caught. Plus CLI end-to-end.

Run: python -m pytest tests/test_validator.py -v
"""
import json

import pytest

from crossbio_validate import core

ESTIMAND = "the unobserved true count at a dropout position"


# ---- artifact builders (all provenance-stamped so rule 5 passes by default) ----
def da(**over):
    a = {
        "artifact_id": "da-1",
        "stage": "data-audit",
        "parent_artifact_id": None,
        "skill_version": "0.2.1",
        "stage_fields": {
            "biological_unit": "donor",
            "estimand": ESTIMAND,
            "fatal_issues": [],
            "cohort_structure": "40 donors",
            "leakage_graph": "donor-level split",
            "split_strategy": "donor-level 5-fold",
        },
    }
    a.update(over)
    return core.stamp(a)


def design(**over):
    a = {
        "artifact_id": "design-1",
        "stage": "design",
        "parent_artifact_id": "da-1",
        "skill_version": "0.2.1",
        "stage_fields": {
            "problem_definition": "recover true counts",
            "estimand": ESTIMAND,
            "notation_and_shapes": {"shapes": {"X": "n×g", "Z": "n×k"}},
            "objective_or_likelihood": "max NB log-lik - lambda * tr(y^T L y)",
            "identifiability": "identifiable under MAR",
            "failure_boundaries": [{"id": "fb1", "mechanism": "MNAR"}],
            "complexity": "O(n^3)",
        },
    }
    a.update(over)
    return core.stamp(a)


def spec(**over):
    a = {
        "artifact_id": "spec-1",
        "stage": "spec",
        "parent_artifact_id": "design-1",
        "skill_version": "0.2.1",
        "stage_fields": {
            "module_interfaces": {"impute": {"out": {"name": "X", "shape": "n×g"}}},
            "acceptance_criteria": [{"id": "ac1", "traces_to": ["fb1"]}],
            "pseudocode_hashes": {"impute": "abc123"},
        },
    }
    a.update(over)
    return core.stamp(a)


def code(**over):
    a = {
        "artifact_id": "code-1",
        "stage": "code",
        "parent_artifact_id": "spec-1",
        "skill_version": "0.2.1",
        "stage_fields": {
            "module_hashes": {"impute": "def456"},
            "test_results": {"passed": 8},
            "acceptance_status": "all pass",
        },
    }
    a.update(over)
    return core.stamp(a)


def errs(findings):
    return [f for f in findings if f.severity == "ERROR"]


def rules(findings):
    return {f.rule for f in findings}


GOOD = [da, design, spec, code]


# ---------- GREEN: a full good chain ----------
def test_good_chain_valid():
    assert errs(core.validate_chain([da(), design(), spec(), code()])) == []


def test_good_chain_minimal_dataaudit_design_spec():
    assert errs(core.validate_chain([da(), design(), spec()])) == []


# ---------- rule 1: estimand continuity ----------
def test_rule1_estimand_drift_detected():
    d = design()
    d["stage_fields"]["estimand"] = "a different estimand"
    core.stamp(d)
    assert "rule1-estimand" in rules(errs(core.validate_chain([da(), d, spec()])))


def test_rule1_estimand_change_with_justification_ok():
    d = design()
    d["stage_fields"]["estimand"] = "reframed estimand"
    d["estimand_change_justification"] = "pivoted after viability"
    core.stamp(d)
    assert "rule1-estimand" not in rules(errs(core.validate_chain([da(), d, spec()])))


# ---------- rule 2: no orphan failure_boundary ----------
def test_rule2_orphan_failure_boundary_detected():
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [{"id": "ac1", "traces_to": ["fb_other"]}]
    core.stamp(s)
    assert "rule2-no-orphan" in rules(errs(core.validate_chain([da(), design(), s])))


# ---------- rule 3: notation consistency ----------
def test_rule3_notation_mismatch_detected():
    s = spec()
    s["stage_fields"]["module_interfaces"] = {"impute": {"out": {"name": "X", "shape": "g×n"}}}
    core.stamp(s)
    assert "rule3-notation" in rules(errs(core.validate_chain([da(), design(), s])))


def test_rule3_freeform_notation_warns_not_errors():
    d = design()
    d["stage_fields"]["notation_and_shapes"] = "free text, no shapes dict"
    core.stamp(d)
    findings = core.validate_chain([da(), d, spec()])
    assert "rule3-notation" not in rules(errs(findings))  # no ERROR
    assert any(f.rule == "rule3-notation" and f.severity == "WARNING" for f in findings)


# ---------- rule 4: pseudocode -> code ----------
def test_rule4_pseudocode_orphan_detected():
    c = code()
    c["stage_fields"]["module_hashes"] = {}  # 'impute' no longer implemented
    core.stamp(c)
    assert "rule4-pseudocode-code" in rules(errs(core.validate_chain([da(), design(), spec(), c])))


def test_rule4_divergence_documented_ok():
    c = code()
    c["stage_fields"]["module_hashes"] = {}
    c["stage_fields"]["divergence"] = {"impute": "used closed-form instead of iterated solve"}
    core.stamp(c)
    assert "rule4-pseudocode-code" not in rules(errs(core.validate_chain([da(), design(), spec(), c])))


# ---------- rule 5: provenance ----------
def test_rule5_provenance_tamper_detected():
    d = design()
    d["provenance_hash"] = "000000000000"  # deliberately wrong, not re-stamped
    assert "provenance" in rules(errs(core.validate_chain([da(), d, spec()])))


def test_stamp_roundtrip():
    a = da()
    assert core.validate_provenance(a) == []
    a["stage_fields"]["estimand"] = "mutated"
    assert core.validate_provenance(a)  # now stale
    core.stamp(a)
    assert core.validate_provenance(a) == []


# ---------- schema (intra-stage) ----------
def test_schema_missing_objective_or_likelihood_detected():
    d = design()
    del d["stage_fields"]["objective_or_likelihood"]
    core.stamp(d)
    assert "schema" in rules(errs(core.validate_chain([da(), d, spec()])))


def test_schema_arbitrary_stage_fields_rejected():
    d = {
        "artifact_id": "d-x",
        "stage": "design",
        "parent_artifact_id": "da-1",
        "skill_version": "0.2.1",
        "provenance_hash": "deadbeefdead",
        "stage_fields": {"anything": "is accepted"},  # the old P0-2 hole
    }
    assert "schema" in rules(errs(core.validate_chain([da(), d, spec()])))


# ---------- chain structure ----------
def test_parent_chain_dangling_detected():
    d = design()
    d["parent_artifact_id"] = "does-not-exist"
    core.stamp(d)
    assert "parent-chain" in rules(errs(core.validate_chain([da(), d, spec()])))


def test_stage_order_violation_detected():
    s = spec()
    s["parent_artifact_id"] = "da-1"  # spec parent must be design, not data-audit
    core.stamp(s)
    assert "stage-order" in rules(errs(core.validate_chain([da(), design(), s])))


def test_fatal_gate_violation_detected():
    da2 = da()
    da2["stage_fields"]["fatal_issues"] = ["donor leakage in train/test"]
    core.stamp(da2)
    assert "fatal-gate" in rules(errs(core.validate_chain([da2, design(), spec()])))


def test_fatal_gate_with_risk_accepted_ok():
    da2 = da()
    da2["stage_fields"]["fatal_issues"] = ["donor leakage in train/test"]
    da2["risk_accepted"] = True
    core.stamp(da2)
    assert "fatal-gate" not in rules(errs(core.validate_chain([da2, design(), spec()])))


def test_fatal_gate_no_downstream_ok():
    da2 = da()
    da2["stage_fields"]["fatal_issues"] = ["donor leakage"]
    core.stamp(da2)
    assert core.validate_chain([da2]) == []  # fatal but chain stops here = fine


# ---------- CLI end-to-end ----------
def _write_chain(tmp_path, arts):
    for a in arts:
        a = dict(a)
        a.pop("__source", None)
        json.dump(a, open(tmp_path / f"{a['artifact_id']}.json", "w"))


def test_cli_validate_chain_good_exits_0(tmp_path, capsys):
    from crossbio_validate.cli import main

    _write_chain(tmp_path, [da(), design(), spec()])
    rc = main(["validate-chain", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "0 findings" in out


def test_cli_validate_chain_drifted_exits_1(tmp_path, capsys):
    from crossbio_validate.cli import main

    d = design()
    d["stage_fields"]["estimand"] = "drifted"
    core.stamp(d)
    _write_chain(tmp_path, [da(), d, spec()])
    rc = main(["validate-chain", str(tmp_path)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "rule1-estimand" in out


def test_cli_validate_single_artifact(tmp_path, capsys):
    from crossbio_validate.cli import main

    p = tmp_path / "a.json"
    json.dump(da(), open(p, "w"))
    assert main(["validate", str(p)]) == 0
