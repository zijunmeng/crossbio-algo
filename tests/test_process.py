"""Adversarial process-compliance tests for the Process Assurance Layer (v0.3.1).

Each test drives a fresh RunManifest through realistic agent misbehaviour and asserts the
state machine + finalize audit catch the violation. These guard the CCC finding: an agent
that loads skills but silently skips search / brainstorm / artifact / audit.
"""
import pytest

from crossbio_validate.process import RunManifest


# --- helpers -----------------------------------------------------------------

def _complete_chain(manifest: RunManifest, stages_with_artifacts):
    """Complete each stage in order, attaching artifact_id unless the entry is a tuple
    (stage, {"evidence_manifest": ...}) style override."""
    for item in stages_with_artifacts:
        if isinstance(item, tuple):
            stage, kwargs = item
            manifest.complete_stage(stage, **kwargs)
        else:
            manifest.complete_stage(item, artifact_id=f"art-{item}")


# --- 1. gate: cannot jump past viability -------------------------------------

def test_gate_blocks_skip_to_design(tmp_path):
    """complete_stage must refuse a stage whose predecessor (viability) is still pending,
    and the offending stage must remain pending after the failed attempt."""
    m = RunManifest.create(str(tmp_path), mode="standard", target_tier="T2")

    # Jump straight to algorithm_design without touching viability.
    with pytest.raises(ValueError) as exc:
        m.complete_stage("algorithm_design", artifact_id="X")
    msg = str(exc.value)
    assert "BLOCKED" in msg, f"error should say BLOCKED: {msg!r}"
    assert "viability" in msg, f"error should name the unmet predecessor viability: {msg!r}"

    # The stage must still be pending — the failed transition mutated nothing.
    assert m.stage_status("algorithm_design") == "pending"
    # The gate still points at the legitimate front of the queue (data_audit), NOT at
    # algorithm_design — the jump attempt did not corrupt the DAG.
    assert m.allowed_stage() == "data_audit"
    # And viability (the unmet predecessor of algorithm_design) is itself still pending,
    # confirming the gate is genuinely what is blocking the jump.
    assert m.stage_status("viability") == "pending"


# --- 2. memory-only competitors: search without receipt ----------------------

def test_memory_only_competitors_caught_by_finalize(tmp_path):
    """Agent claims to have searched (status=completed) but produced no evidence_manifest.
    Finalize must downgrade to PROVISIONAL_NONCOMPLIANT and name the missing receipt."""
    m = RunManifest.create(str(tmp_path), mode="standard", target_tier="T2")

    m.complete_stage("data_audit", artifact_id="aud-1")
    # evidence_search WITHOUT evidence_manifest — the "memory-only competitors" smell.
    m.complete_stage("evidence_search", artifact_id="evi-1")
    m.skip_stage("brainstorm",
                 reason_code="USER_DEFINED_SINGLE_DIRECTION",
                 justification="user already fixed the direction")
    m.complete_stage("viability", artifact_id="viab-1")
    m.complete_stage("algorithm_design", artifact_id="des-1")
    m.complete_stage("specification", artifact_id="spec-1")
    m.complete_stage("adversarial_audit", artifact_id="aud-2")

    status, missing, warnings = m.finalize()
    assert status == "PROVISIONAL_NONCOMPLIANT", f"expected noncompliant, got {status}"
    missing_blob = "\n".join(missing)
    assert "evidence_search" in missing_blob, f"missing should name evidence_search: {missing!r}"
    assert "evidence_manifest" in missing_blob, (
        f"missing should name the missing evidence_manifest receipt: {missing!r}")


# --- 3. justified brainstorm skip is compliant -------------------------------

def test_justified_brainstorm_skip_passes(tmp_path):
    """brainstorm is NOT required in standard mode; skipping it with a reason_code is fully
    compliant — it must not appear in the missing list at finalize."""
    m = RunManifest.create(str(tmp_path), mode="standard", target_tier="T2")

    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search",
                     artifact_id="evi-1",
                     evidence_manifest="ev/manifest.json")
    m.skip_stage("brainstorm",
                 reason_code="USER_DEFINED_SINGLE_DIRECTION",
                 justification="single predefined direction from user")

    # Skip recorded + gate advanced past brainstorm.
    assert m.stage_status("brainstorm") == "skipped"
    assert m.allowed_stage() == "viability"

    m.complete_stage("viability", artifact_id="viab-1")
    m.complete_stage("algorithm_design", artifact_id="des-1")
    m.complete_stage("specification", artifact_id="spec-1")
    m.complete_stage("adversarial_audit", artifact_id="aud-2")

    status, missing, warnings = m.finalize()
    assert status == "READY_FOR_USER", f"justified skip should be compliant: {status}, missing={missing!r}"
    assert not any("brainstorm" in m_ for m_ in missing), (
        f"skipped-with-reason brainstorm must not be in missing: {missing!r}")


# --- 4. required stage completed without artifact ----------------------------

def test_required_stage_completed_without_artifact_caught(tmp_path):
    """A required stage marked completed but with NO artifact_id is a phantom completion.
    Finalize must downgrade and name 'specification' + 'no artifact_id'."""
    m = RunManifest.create(str(tmp_path), mode="standard", target_tier="T2")

    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search",
                     artifact_id="evi-1",
                     evidence_manifest="ev/manifest.json")
    m.skip_stage("brainstorm",
                 reason_code="USER_DEFINED_SINGLE_DIRECTION",
                 justification="direction fixed")
    m.complete_stage("viability", artifact_id="viab-1")
    m.complete_stage("algorithm_design", artifact_id="des-1")
    # specification completed WITHOUT artifact_id — the audit target.
    m.complete_stage("specification")
    m.complete_stage("adversarial_audit", artifact_id="aud-2")

    status, missing, warnings = m.finalize()
    assert status == "PROVISIONAL_NONCOMPLIANT", f"phantom completion should be noncompliant: {status}"
    missing_blob = "\n".join(missing)
    assert "specification" in missing_blob, f"missing should name specification: {missing!r}"
    assert "no artifact_id" in missing_blob, (
        f"missing should explain the no-artifact_id defect: {missing!r}")


# --- 5. publication mode: required+skipped brainstorm → WARNING, not missing --

def test_publication_mode_requires_brainstorm(tmp_path):
    """In publication mode brainstorm is required. Skipping it with a valid reason_code IS
    allowed, but finalize must surface a WARNING (required stage was skipped) rather than
    silently treating it as a normal compliant skip. It must NOT appear in the missing list
    because the skip carries a reason_code."""
    m = RunManifest.create(str(tmp_path), mode="publication", target_tier="T1")

    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search",
                     artifact_id="evi-1",
                     evidence_manifest="ev/manifest.json")
    m.skip_stage("brainstorm",
                 reason_code="USER_DEFINED_SINGLE_DIRECTION",
                 justification="user committed to a single direction before publication run")

    # Sanity: the skip was recorded.
    assert m.stage_status("brainstorm") == "skipped"

    status, missing, warnings = m.finalize()

    # brainstorm is required+skipped-with-reason → WARNING, not missing.
    warn_blob = "\n".join(warnings)
    missing_blob = "\n".join(missing)
    assert any("brainstorm" in w for w in warnings), (
        f"required+skipped brainstorm must produce a WARNING: {warnings!r}")
    assert "skipped (required)" in warn_blob or "required" in warn_blob, (
        f"warning should flag required-ness: {warnings!r}")
    assert not any("brainstorm" in m_ for m_ in missing), (
        f"reason-coded skip must NOT be a missing item: {missing!r}")


# --- 6. v0.4.0: method_tension policy / blocked / backward compat ------------------------------

def test_quick_mode_tension_pre_skipped_with_reason(tmp_path):
    """Quick default = tension OFF, but as a RECORDED skip (reason + justification), never silent.
    The gate must point straight at data_audit (no added default cost)."""
    m = RunManifest.create(str(tmp_path), mode="quick", target_tier="T3")
    assert m.stage_status("method_tension") == "skipped"
    assert m.data["stages"]["method_tension"]["skip_reason_code"] == "NOT_APPLICABLE"
    assert m.allowed_stage() == "data_audit"


def test_quick_mode_tension_can_be_enabled_later(tmp_path):
    """User explicitly asks for discovery in Quick → complete the stage from 'skipped'."""
    m = RunManifest.create(str(tmp_path), mode="quick", tension_policy="optional")
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("method_tension", artifact_id="mt-1")
    assert m.stage_status("method_tension") == "completed"


def test_standard_default_tension_optional_and_nonblocking(tmp_path):
    """Standard default: optional, sits as a parallel branch — the classic standard flow is
    untouched (the v0.3.2 gate semantics are preserved bit-for-bit)."""
    m = RunManifest.create(str(tmp_path), mode="standard")
    assert m.stage_status("method_tension") == "pending"
    assert not m._dag()["method_tension"]["required"]
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search", artifact_id="evi-1", evidence_manifest="ev/m.json")
    m.skip_stage("brainstorm", reason_code="USER_DEFINED_SINGLE_DIRECTION",
                 justification="user has the one idea")
    assert m.allowed_stage() == "viability"  # NOT method_tension — parallel branch


def test_standard_discovery_run_tension_required(tmp_path):
    m = RunManifest.create(str(tmp_path), mode="standard", tension_policy="required")
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search", artifact_id="evi-1", evidence_manifest="ev/m.json")
    m.complete_stage("method_tension", artifact_id="mt-1")
    # required completion without phantom: with artifact_id → no missing entry
    status, missing, _ = m.finalize()
    assert not any("method_tension" in x for x in missing)


def test_publication_tension_gates_brainstorm(tmp_path):
    """Publication: method_tension is required AND brainstorm depends on it — the spec's
    flow (tension cards feed brainstorm) is hard-enforced."""
    m = RunManifest.create(str(tmp_path), mode="publication", target_tier="T1")
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search", artifact_id="evi-1", evidence_manifest="ev/m.json")
    with pytest.raises(ValueError) as exc:
        m.complete_stage("brainstorm", artifact_id="br-1")
    assert "method_tension" in str(exc.value)
    assert m.allowed_stage() == "method_tension"


def test_publication_blocked_tension_fails_finalize(tmp_path):
    """AC-05: a required stage that CANNOT run is recorded BLOCKED (explicit, never silent)
    and finalize must refuse READY_FOR_USER."""
    m = RunManifest.create(str(tmp_path), mode="publication", target_tier="T1")
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search", artifact_id="evi-1", evidence_manifest="ev/m.json")
    m.block_stage("method_tension", reason_code="SEARCH_UNAVAILABLE",
                  justification="literature search API down; cannot mine tensions honestly")
    assert m.stage_status("method_tension") == "blocked"
    # gate: brainstorm is blocked behind it
    with pytest.raises(ValueError):
        m.complete_stage("brainstorm", artifact_id="br-1")
    status, missing, warnings = m.finalize()
    assert status == "PROVISIONAL_NONCOMPLIANT"
    assert any("method_tension" in x and "BLOCKED" in x for x in missing)


def test_blocked_reason_code_validated(tmp_path):
    m = RunManifest.create(str(tmp_path), mode="publication")
    with pytest.raises(ValueError):
        m.block_stage("method_tension", reason_code="JUST_FEEL_LIKE_IT", justification="...")


def test_blocked_stage_recoverable_by_completing(tmp_path):
    m = RunManifest.create(str(tmp_path), mode="publication", target_tier="T1")
    m.complete_stage("data_audit", artifact_id="aud-1")
    m.complete_stage("evidence_search", artifact_id="evi-1", evidence_manifest="ev/m.json")
    m.block_stage("method_tension", reason_code="SEARCH_UNAVAILABLE", justification="api down")
    # tooling recovers → complete out of blocked
    m.complete_stage("method_tension", artifact_id="mt-1")
    assert m.stage_status("method_tension") == "completed"
    assert m.allowed_stage() == "brainstorm"


def test_old_v032_manifest_ignores_new_stage(tmp_path):
    """AC-05: a v0.3.2 run-manifest (no method_tension key) loaded under v0.4.0 behaves
    EXACTLY as before — the new stage is filtered out, the gate never points at it."""
    import json
    old_manifest = {
        "run_id": "old-run",
        "mode": "publication",
        "target_tier": "T1",
        "stages": {
            s: {"required": True, "status": st, "artifact_id": None,
                "skip_reason_code": None, "skip_justification": None, "evidence_manifest": None}
            for s, st in [("data_audit", "completed"), ("evidence_search", "completed"),
                          ("brainstorm", "completed"), ("viability", "pending")]
        },
    }
    p = tmp_path / "run-manifest.json"
    p.write_text(json.dumps(old_manifest))
    m = RunManifest.load(str(tmp_path))
    assert "method_tension" not in m._dag()
    assert m.allowed_stage() == "viability"
