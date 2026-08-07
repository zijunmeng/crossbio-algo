"""Core validation logic for crossbio-algo artifacts.

Intra-stage (per artifact): schema (jsonschema) + provenance_hash integrity.
Chain-level: parent-chain, stage-order, fatal-gate.
Cross-stage content rules: estimand continuity / no-orphan failure_boundary /
notation consistency / pseudocode->code.

The 5 rules + chain checks correspond 1:1 to the spec in
``skills/_shared/artifact-validation.md``; that doc used to be pseudocode only —
this module is the real, tested implementation.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

import jsonschema

# The canonical stage schema is bundled INSIDE the package (crossbio_validate/schemas/)
# so wheels include it. Resolved at runtime via importlib.resources; see load_schema().

STAGES = ["data-audit", "brainstorm", "viability", "design", "spec", "code", "audit"]

# child_stage -> set of allowed PARENT stages (None = root / no parent).
# Encodes the loop topology from research-design-handoff.md (data-audit is the
# GATE root; brainstorm/viability/design can each chain from earlier stages;
# spec must follow design; code must follow spec; audit is horizontal).
ALLOWED_PARENT_STAGES = {
    "data-audit": {None},
    "brainstorm": {"data-audit"},
    "viability": {"brainstorm", "data-audit"},
    "design": {"viability", "brainstorm", "data-audit"},
    "spec": {"design"},
    "code": {"spec"},
    "audit": set(STAGES),
}


@dataclass
class Finding:
    rule: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    artifact_id: Optional[str] = None


# ---------- hashing ----------
def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash12(obj) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()[:12]


def stamp(a: dict) -> dict:
    """Set the correct provenance_hash on an artifact (mutates + returns).

    Used when authoring fixtures / real artifacts so they pass rule 5.
    """
    content = {k: v for k, v in a.items() if k != "provenance_hash"}
    a["provenance_hash"] = hash12(content)
    return a


def load_schema() -> dict:
    """Load the canonical stage schema (bundled in the package for wheel correctness)."""
    try:
        from importlib.resources import files
        return json.loads(files("crossbio_validate.schemas").joinpath("stage-schemas.json").read_text())
    except Exception:  # source-tree fallback (editable / direct run)
        p = os.path.join(os.path.dirname(__file__), "schemas", "stage-schemas.json")
        with open(p) as f:
            return json.load(f)


# ---------- per-artifact ----------
def validate_schema(a: dict, schema: Optional[dict] = None) -> list[Finding]:
    schema = schema or load_schema()
    try:
        jsonschema.validate(a, schema)
        return []
    except jsonschema.ValidationError as e:
        path = ".".join(str(p) for p in e.absolute_path) or "<root>"
        return [Finding("schema", "ERROR", f"{e.message} (at {path})", a.get("artifact_id"))]


def validate_provenance(a: dict) -> list[Finding]:
    if "provenance_hash" not in a:
        return [Finding("provenance", "ERROR", "missing provenance_hash", a.get("artifact_id"))]
    content = {k: v for k, v in a.items() if k != "provenance_hash"}
    expected = hash12(content)
    if a["provenance_hash"] != expected:
        return [
            Finding(
                "provenance",
                "ERROR",
                f"provenance_hash {a['provenance_hash']!r} != recomputed {expected!r}"
                f" (content tampered or hash is stale)",
                a.get("artifact_id"),
            )
        ]
    return []


def validate_artifact(a: dict, schema: Optional[dict] = None) -> list[Finding]:
    return validate_schema(a, schema) + validate_provenance(a)


# ---------- chain structure ----------
def _by_id(arts: list[dict]) -> dict:
    return {a["artifact_id"]: a for a in arts if "artifact_id" in a}


def validate_parent_chain(arts: list[dict]) -> list[Finding]:
    ids = _by_id(arts)
    out: list[Finding] = []
    for a in arts:
        pid = a.get("parent_artifact_id")
        if pid is None:
            if a.get("stage") != "data-audit":
                out.append(
                    Finding(
                        "parent-chain",
                        "ERROR",
                        f"parent_artifact_id is null but stage={a.get('stage')!r}"
                        f" (only the data-audit artifact may be the chain root)",
                        a.get("artifact_id"),
                    )
                )
        elif pid not in ids:
            out.append(
                Finding(
                    "parent-chain",
                    "ERROR",
                    f"parent_artifact_id {pid!r} not found in chain (dangling parent)",
                    a.get("artifact_id"),
                )
            )
    return out


def validate_stage_order(arts: list[dict]) -> list[Finding]:
    ids = _by_id(arts)
    out: list[Finding] = []
    for a in arts:
        st = a.get("stage")
        pid = a.get("parent_artifact_id")
        parent_stage = None if pid is None else ids.get(pid, {}).get("stage")
        allowed = ALLOWED_PARENT_STAGES.get(st)
        if allowed is None:
            continue  # unknown stage caught by schema
        if parent_stage not in allowed:
            out.append(
                Finding(
                    "stage-order",
                    "ERROR",
                    f"stage {st!r} has parent stage {parent_stage!r}; allowed parents:"
                    f" {sorted('null' if x is None else x for x in allowed)}",
                    a.get("artifact_id"),
                )
            )
    return out


def validate_fatal_gate(arts: list[dict]) -> list[Finding]:
    """data-audit.fatal_issues non-empty => chain must NOT continue unless risk accepted."""
    out: list[Finding] = []
    downstream = [
        a for a in arts if a.get("stage") not in (None, "data-audit", "audit")
    ]
    if not downstream:
        return out
    ds_stages = sorted({a["stage"] for a in downstream})
    for a in arts:
        if a.get("stage") != "data-audit":
            continue
        fatal = (a.get("stage_fields") or {}).get("fatal_issues") or []
        if not fatal:
            continue
        risk = a.get("risk_accepted") or (a.get("decision") or {}).get("risk_accepted")
        if not risk:
            out.append(
                Finding(
                    "fatal-gate",
                    "ERROR",
                    f"data-audit has {len(fatal)} fatal_issue(s) but chain continues to"
                    f" {ds_stages} without risk_accepted=true (GATE violated)",
                    a.get("artifact_id"),
                )
            )
    return out


# ---------- cross-stage content rules ----------
def rule1_estimand_continuity(arts: list[dict]) -> list[Finding]:
    da = next((a for a in arts if a.get("stage") == "data-audit"), None)
    if not da:
        return []
    da_est = (da.get("stage_fields") or {}).get("estimand")
    if da_est is None:
        return []
    out: list[Finding] = []
    for a in arts:
        if a.get("stage") != "design":
            continue
        sf = a.get("stage_fields") or {}
        d_est = sf.get("estimand")
        if d_est is not None and d_est != da_est and not a.get("estimand_change_justification"):
            out.append(
                Finding(
                    "rule1-estimand",
                    "ERROR",
                    f"design.estimand != data-audit.estimand and no"
                    f" estimand_change_justification: {d_est!r} vs {da_est!r}",
                    a.get("artifact_id"),
                )
            )
    return out


def rule2_no_orphan_failure_boundary(arts: list[dict]) -> list[Finding]:
    design = next((a for a in arts if a.get("stage") == "design"), None)
    spec = next((a for a in arts if a.get("stage") == "spec"), None)
    if not design or not spec:
        return []
    fbs = (design.get("stage_fields") or {}).get("failure_boundaries") or []
    fb_ids = {fb.get("id") for fb in fbs if isinstance(fb, dict) and fb.get("id")}
    acs = (spec.get("stage_fields") or {}).get("acceptance_criteria") or []
    traced: set[str] = set()
    for ac in acs:
        if isinstance(ac, dict):
            traced.update(ac.get("traces_to") or [])
    out: list[Finding] = []
    for fid in fb_ids:
        if fid not in traced:
            out.append(
                Finding(
                    "rule2-no-orphan",
                    "ERROR",
                    f"failure_boundary {fid!r} has no acceptance_criterion tracing to it"
                    f" (orphan risk — a declared failure mode nobody tests)",
                    design.get("artifact_id"),
                )
            )
    return out


_SHAPE_RE = re.compile(r"^[A-Za-z]\w*(?:×|x)[A-Za-z]\w*$|^\d+(?:×|x)\d+$")


def _extract_shapes(obj) -> set[str]:
    """Collect shape strings recursively: values under a 'shape' key, or standalone
    tokens matching a shape pattern like n×g / 200×5."""
    shapes: set[str] = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "shape" and isinstance(v, str):
                    shapes.add(v.strip())
                walk(v)
        elif isinstance(x, list):
            for i in x:
                walk(i)
        elif isinstance(x, str):
            for tok in re.split(r"[,\s]+", x):
                if _SHAPE_RE.match(tok):
                    shapes.add(tok)

    walk(obj)
    return shapes


def rule3_notation_consistency(arts: list[dict]) -> list[Finding]:
    design = next((a for a in arts if a.get("stage") == "design"), None)
    spec = next((a for a in arts if a.get("stage") == "spec"), None)
    if not design or not spec:
        return []
    d_not = (design.get("stage_fields") or {}).get("notation_and_shapes")
    s_iface = (spec.get("stage_fields") or {}).get("module_interfaces")
    if not isinstance(d_not, dict) or not isinstance(s_iface, (dict, list)):
        return [
            Finding(
                "rule3-notation",
                "WARNING",
                "notation_and_shapes / module_interfaces not in extractable form"
                " ({shapes:{symbol:shape}} + interface shape fields) — rule 3 skipped.",
                spec.get("artifact_id"),
            )
        ]
    d_shapes: set[str] = set()
    if isinstance(d_not.get("shapes"), dict):
        d_shapes.update(str(v) for v in d_not["shapes"].values())
    d_shapes |= _extract_shapes(d_not)
    s_shapes = _extract_shapes(s_iface)
    undeclared = s_shapes - d_shapes
    if undeclared:
        return [
            Finding(
                "rule3-notation",
                "ERROR",
                f"spec interfaces use shapes not declared in design.notation_and_shapes:"
                f" {sorted(undeclared)} (design↔spec notation drift — the SCOUT class of bug)",
                spec.get("artifact_id"),
            )
        ]
    return []


def rule4_pseudocode_to_code(arts: list[dict]) -> list[Finding]:
    spec = next((a for a in arts if a.get("stage") == "spec"), None)
    code = next((a for a in arts if a.get("stage") == "code"), None)
    if not spec or not code:
        return []
    pseudo = (spec.get("stage_fields") or {}).get("pseudocode_hashes") or {}
    if not isinstance(pseudo, dict):
        return []
    mods = (code.get("stage_fields") or {}).get("module_hashes") or {}
    sf = code.get("stage_fields") or {}
    div = sf.get("divergence") or code.get("divergence") or {}
    out: list[Finding] = []
    for module in pseudo:
        if module not in mods and module not in div:
            out.append(
                Finding(
                    "rule4-pseudocode-code",
                    "ERROR",
                    f"spec pseudocode module {module!r} has no matching"
                    f" code.module_hashes entry and no documented divergence",
                    code.get("artifact_id"),
                )
            )
    return out


def validate_chain(arts: list[dict], root: str = ".") -> list[Finding]:
    schema = load_schema()
    out: list[Finding] = []
    for a in arts:
        out += validate_artifact(a, schema)
    out += validate_parent_chain(arts)
    out += validate_stage_order(arts)
    out += validate_fatal_gate(arts)
    out += rule1_estimand_continuity(arts)
    out += rule2_no_orphan_failure_boundary(arts)
    out += rule3_notation_consistency(arts)
    out += rule4_pseudocode_to_code(arts)
    out += rule_source_hash(arts, root)
    out += rule_test_link(arts)
    out += rule_verification_mode_status(arts)
    return out


# ---------- executable-trace rules (DECLARED vs TESTED) ----------
TEST_REQUIRED_MODES = {"automated_test", "simulation", "benchmark"}


def _source_sha256(path: str, symbol: Optional[str] = None) -> str:
    """Recompute sha256 of a source file, or just the body of `symbol` (def/class)."""
    import ast
    with open(path) as f:
        src = f.read()
    if symbol:
        try:
            tree = ast.parse(src)
            seg = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
                    seg = ast.get_source_segment(src, node)
                    break
            if seg is not None:
                src = seg
        except SyntaxError:
            pass  # unparseable -> hash whole file (likely mismatches -> flagged)
    return hashlib.sha256(src.encode()).hexdigest()


def rule_source_hash(arts: list[dict], root: str = ".") -> list[Finding]:
    """REAL source hashing (reviewer §2): recompute sha256 from disk, compare to declared.
    Catches 'source edited but the artifact hash not updated'."""
    code = next((a for a in arts if a.get("stage") == "code"), None)
    if not code:
        return []
    out: list[Finding] = []
    for impl in (code.get("stage_fields") or {}).get("implementations") or []:
        if not isinstance(impl, dict):
            continue
        sf = impl.get("source_file")
        if not sf:
            continue
        path = sf if os.path.isabs(sf) else os.path.join(root, sf)
        if not os.path.exists(path):
            out.append(Finding("source-hash", "ERROR",
                f"implementation {impl.get('module')!r}: source_file {sf!r} not found under root",
                code.get("artifact_id")))
            continue
        recomputed = _source_sha256(path, impl.get("symbol"))
        if recomputed != impl.get("source_sha256"):
            out.append(Finding("source-hash", "ERROR",
                f"implementation {impl.get('module')!r}: source_sha256"
                f" {str(impl.get('source_sha256'))[:12]}.. != recomputed {recomputed[:12]}.."
                f" (source drifted from the declared hash)",
                code.get("artifact_id")))
    return out


def rule_test_link(arts: list[dict]) -> list[Finding]:
    """DECLARED vs TESTED (reviewer §3): an acceptance_criterion in a test-requiring mode
    MUST have >=1 passing test linked to it."""
    spec = next((a for a in arts if a.get("stage") == "spec"), None)
    code = next((a for a in arts if a.get("stage") == "code"), None)
    if not spec or not code:
        return []
    acs = (spec.get("stage_fields") or {}).get("acceptance_criteria") or []
    tests = (code.get("stage_fields") or {}).get("tests") or []
    out: list[Finding] = []
    for ac in acs:
        if not isinstance(ac, dict) or ac.get("verification_mode") not in TEST_REQUIRED_MODES:
            continue
        ac_id = ac.get("id")
        linked = [t for t in tests if isinstance(t, dict) and t.get("verifies_ac") == ac_id]
        if not any(t.get("status") == "passed" for t in linked):
            out.append(Finding("test-link", "ERROR",
                f"acceptance_criterion {ac_id!r} declares verification_mode={ac.get('verification_mode')!r}"
                f" but no passing test links to it (DECLARED, not TESTED)",
                spec.get("artifact_id")))
    return out


def rule_verification_mode_status(arts: list[dict]) -> list[Finding]:
    """A documented_limitation MUST NOT be marked passed (reviewer §4) — it is known_limitation."""
    spec = next((a for a in arts if a.get("stage") == "spec"), None)
    code = next((a for a in arts if a.get("stage") == "code"), None)
    if not spec or not code:
        return []
    acs = (spec.get("stage_fields") or {}).get("acceptance_criteria") or []
    tests = (code.get("stage_fields") or {}).get("tests") or []
    out: list[Finding] = []
    for ac in acs:
        if not isinstance(ac, dict) or ac.get("verification_mode") != "documented_limitation":
            continue
        ac_id = ac.get("id")
        linked = [t for t in tests if isinstance(t, dict) and t.get("verifies_ac") == ac_id]
        if any(t.get("status") == "passed" for t in linked):
            out.append(Finding("verification-mode", "ERROR",
                f"acceptance_criterion {ac_id!r} is verification_mode=documented_limitation"
                f" but a linked test marks it status=passed — a limitation cannot be 'passed' (overclaim)",
                code.get("artifact_id")))
    return out


def format_findings(findings: list[Finding]) -> str:
    if not findings:
        return "VALID — 0 findings."
    errs = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARNING"]
    lines = []
    for f in findings:
        mark = "ERROR" if f.severity == "ERROR" else "WARN "
        aid = f"[{f.artifact_id}] " if f.artifact_id else ""
        lines.append(f"  [{mark}] {f.rule}: {aid}{f.message}")
    lines.append(f"\n  -> {len(errs)} error(s), {len(warns)} warning(s)")
    return "\n".join(lines)
