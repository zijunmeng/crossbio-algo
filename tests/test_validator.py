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
            "acceptance_criteria": [{"id": "ac1", "traces_to": ["fb1"], "verification_mode": "analytic_argument"}],
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
            "implementations": [],
            "tests": [],
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


# ---------------- Phase 1: executable trace (DECLARED vs TESTED) ----------------
def _write_src(tmp_path, name="src.py", body="def pair_map():\n    return 1\n"):
    p = tmp_path / name
    p.write_text(body)
    return p


def test_good_chain_with_code_passes(tmp_path):
    """Correct source hashes + a passing test for an automated_test AC => valid."""
    src = _write_src(tmp_path)
    src_sha = core._source_sha256(str(src), "pair_map")  # same hashing the validator applies
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [
        {"id": "ac1", "traces_to": ["fb1"], "verification_mode": "automated_test"}]
    core.stamp(s)
    c = code()
    c["stage_fields"]["implementations"] = [
        {"module": "pair_map", "source_file": str(src), "symbol": "pair_map",
         "source_sha256": src_sha, "module_sha256": core._source_sha256(str(src), None)}]
    c["stage_fields"]["tests"] = [{"test_id": "t1", "verifies_ac": "ac1", "status": "passed"}]
    core.stamp(c)
    assert errs(core.validate_chain([da(), design(), s, c], root=str(tmp_path))) == []


def test_attack_declared_tested_but_no_test():
    """§3: AC declares verification_mode=automated_test but no passing test links -> FAIL."""
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [
        {"id": "ac1", "traces_to": ["fb1"], "verification_mode": "automated_test"}]
    core.stamp(s)
    c = code()  # tests=[] -> nothing verifies ac1
    assert "test-link" in rules(errs(core.validate_chain([da(), design(), s, c])))


def test_attack_source_hash_drift(tmp_path):
    """§2: source edited but source_sha256 not updated -> FAIL."""
    src = _write_src(tmp_path)
    c = code()
    c["stage_fields"]["implementations"] = [
        {"module": "pair_map", "source_file": str(src), "symbol": "pair_map", "source_sha256": "0" * 64}]
    core.stamp(c)
    assert "source-hash" in rules(errs(core.validate_chain([da(), design(), spec(), c], root=str(tmp_path))))


def test_attack_limitation_marked_passed():
    """§4: a documented_limitation cannot be marked status=passed -> FAIL."""
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [
        {"id": "ac1", "traces_to": ["fb1"], "verification_mode": "documented_limitation"}]
    core.stamp(s)
    c = code()
    c["stage_fields"]["tests"] = [{"test_id": "t1", "verifies_ac": "ac1", "status": "passed"}]
    core.stamp(c)
    assert "verification-mode" in rules(errs(core.validate_chain([da(), design(), s, c])))


def test_limitation_known_status_ok():
    """documented_limitation + status=known_limitation is honest -> that rule passes."""
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [
        {"id": "ac1", "traces_to": ["fb1"], "verification_mode": "documented_limitation"}]
    core.stamp(s)
    c = code()
    c["stage_fields"]["tests"] = [{"test_id": "t1", "verifies_ac": "ac1", "status": "known_limitation"}]
    core.stamp(c)
    assert "verification-mode" not in rules(errs(core.validate_chain([da(), design(), s, c])))


# ---------------- Phase A (v0.2.3): ATTESTED — results.json overrides self-declaration ----------------
def _code_with_impl(tmp_path, nodeid, status="passed"):
    src = _write_src(tmp_path)
    c = code()
    c["stage_fields"]["implementations"] = [{"module": "pair_map", "source_file": str(src),
        "symbol": "pair_map", "source_sha256": core._source_sha256(str(src), "pair_map"),
        "module_sha256": core._source_sha256(str(src), None)}]
    c["stage_fields"]["tests"] = [{"test_id": "t1", "verifies_ac": "ac1", "status": status,
                                   "pytest_nodeid": nodeid}]
    core.stamp(c)
    return c


def _ac_spec(mode="automated_test"):
    s = spec()
    s["stage_fields"]["acceptance_criteria"] = [
        {"id": "ac1", "traces_to": ["fb1"], "verification_mode": mode}]
    core.stamp(s)
    return s


def test_attested_results_override_self_declaration(tmp_path):
    """ATTESTED: results.json observing 'passed' => TESTED, even if artifact omits status.
    code.json has no authority to self-attest (reviewer §2 v0.2.3)."""
    (tmp_path / "results.json").write_text(json.dumps(
        {"tests": {"test_x.py::test_t1": {"outcome": "passed"}}}))
    c = _code_with_impl(tmp_path, "test_x.py::test_t1", status="passed")
    assert errs(core.validate_chain([da(), design(), _ac_spec(), c], root=str(tmp_path))) == []


def test_attested_observed_failure_beats_self_declared_passed(tmp_path):
    """ATTESTED: results.json observing 'failed' => ERROR, even though the artifact says status=passed.
    This is the core fix — DECLARED passed != TESTED passed."""
    (tmp_path / "results.json").write_text(json.dumps(
        {"tests": {"test_x.py::test_t1": {"outcome": "failed"}}}))
    c = _code_with_impl(tmp_path, "test_x.py::test_t1", status="passed")  # self-declares passed (a lie)
    assert "test-link" in rules(errs(core.validate_chain([da(), design(), _ac_spec(), c], root=str(tmp_path))))


def test_unattested_declared_passed_is_only_a_warning():
    """Without results.json, a self-declared 'passed' is a WARNING (unattested), not trusted — and not an error."""
    import tempfile
    td = tempfile.mkdtemp()
    src = _write_src(__import__("pathlib").Path(td))
    c = code()
    c["stage_fields"]["implementations"] = [{"module": "pair_map", "source_file": str(src),
        "symbol": "pair_map", "source_sha256": core._source_sha256(str(src), "pair_map"),
        "module_sha256": core._source_sha256(str(src), None)}]
    c["stage_fields"]["tests"] = [{"test_id": "t1", "verifies_ac": "ac1", "status": "passed",
                                   "pytest_nodeid": "test_x.py::test_t1"}]
    core.stamp(c)
    findings = core.validate_chain([da(), design(), _ac_spec(), c], root=td)
    assert "test-link" not in rules(errs(findings))  # not an ERROR
    assert any(f.rule == "test-link" and f.severity == "WARNING" for f in findings)  # is a WARNING


# ---------------- Phase A (v0.2.4): SOURCE-BOUND attestation ----------------
def test_source_attestation_stale_after_edit(tmp_path):
    """results.source_snapshot binds the attestation to the current source; editing a bound file
    without re-attesting -> STALE -> ERROR (closes the 'reuse old results after editing code' hole)."""
    import hashlib
    (tmp_path / "src.py").write_text("def f():\n    return 1\n")
    h = hashlib.sha256((tmp_path / "src.py").read_bytes()).hexdigest()
    (tmp_path / "results.json").write_text(json.dumps({"source_snapshot": {"src.py": h}, "tests": {}}))
    c = code()
    c["stage_fields"]["implementations"] = []  # isolate the source-attestation rule
    core.stamp(c)
    chain = [da(), design(), spec(), c]
    assert "source-attestation" not in rules(errs(core.validate_chain(chain, root=str(tmp_path))))
    (tmp_path / "src.py").write_text("def f():\n    return 2  # changed\n")  # edit source, don't re-attest
    assert "source-attestation" in rules(errs(core.validate_chain(chain, root=str(tmp_path))))
