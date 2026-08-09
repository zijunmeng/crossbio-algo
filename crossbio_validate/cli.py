"""crossbio CLI — entry point for the artifact validator.

Subcommands:
  validate         <artifact.json>   validate ONE artifact (schema + provenance)
  validate-chain   <dir>             validate a dir of artifact.json as a chain
                                     (schema + parent-chain + stage-order + fatal-gate
                                      + 8 content rules: 5 cross-stage + 3 executable-trace)
  validate-project <dir>             scan a project dir for artifacts and validate-chain
  stamp            <artifact.json>   write the correct provenance_hash (authoring helper)
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

from . import core
from .process import RunManifest, VALID_SKIP_REASONS


def _looks_like_artifact(d) -> bool:
    return isinstance(d, dict) and "stage" in d and "stage_fields" in d


def _load_artifacts(path: str) -> list[dict]:
    arts: list[dict] = []
    if os.path.isfile(path):
        arts.append(json.load(open(path)))
        return arts
    if not os.path.isdir(path):
        raise FileNotFoundError(path)
    for f in sorted(glob.glob(os.path.join(path, "**", "*.json"), recursive=True)):
        try:
            d = json.load(open(f))
        except Exception as e:  # noqa: BLE001
            print(f"WARN: could not parse {f}: {e}", file=sys.stderr)
            continue
        if _looks_like_artifact(d):
            arts.append(d)
    return arts


def _file_sha256(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _env_fingerprint():
    """Rich environment fingerprint: python + platform + arch + key package versions, canonicalized
    (reviewer v0.2.4 — sha256(python --version) alone collided across numpy 1.x/2.x etc.)."""
    import platform
    from importlib import metadata

    pkgs = ["pytest", "numpy", "scipy", "scikit-learn", "jsonschema", "pyyaml"]
    versions = {}
    for p in pkgs:
        try:
            versions[p] = metadata.version(p)
        except Exception:
            versions[p] = "missing"
    blob = json.dumps({
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": versions,
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:12], versions


def _run_attest(target, out, root=".", bind=()):
    """Run pytest on `target` (from `root`), parse the JUnit XML, write results.json (observed
    outcomes) BOUND to a SOURCE SNAPSHOT. The test target is always hashed; ``--bind`` adds impl
    files. rule_test_link attests outcomes; rule_source_attestation binds them to the current source
    (so editing scout.py/test_scout.py without re-attesting -> STALE -> ERROR)."""
    import datetime
    import subprocess
    import tempfile
    import xml.etree.ElementTree as ET

    junit = tempfile.mktemp(suffix=".xml")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", target, f"--junit-xml={junit}", "-q", "--no-header"],
        cwd=root, capture_output=True, text=True,
    )
    tests = {}
    if os.path.exists(junit):
        try:
            for tc in ET.parse(junit).getroot().iter("testcase"):
                file = tc.get("file") or target
                nodeid = f"{file}::{tc.get('name')}"
                outcome = "passed"
                for child in tc:
                    if child.tag in ("failure", "error"):
                        outcome = "failed"
                    elif child.tag == "skipped":
                        outcome = "skipped"
                tests[nodeid] = {"outcome": outcome}
        finally:
            try:
                os.remove(junit)
            except OSError:
                pass

    # SOURCE SNAPSHOT — binds the observed results to the current source (closes the
    # "reuse an old results.json after editing code" hole; git_commit alone can't bind pre-commit).
    # Paths are stored RELATIVE TO THE results.json OUTPUT DIR so the validator (whose root is that
    # dir) resolves them correctly.
    out_dir = os.path.dirname(os.path.abspath(out))
    test_file = target.split("::", 1)[0]  # nodeid "path::test" -> hash the test FILE (reviewer v0.2.5 §3)
    source_snapshot = {}
    for f in [test_file, *bind]:
        p = f if os.path.isabs(f) else os.path.join(root, f)
        if os.path.isfile(p):
            source_snapshot[os.path.relpath(p, out_dir)] = _file_sha256(p)

    def _sh(cmd):
        try:
            return subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None

    env_fp, env_versions = _env_fingerprint()
    result = {
        "generated_via": "crossbio attest",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": _sh(["git", "rev-parse", "HEAD"]),  # informational; source_snapshot is the real binding
        "env_fingerprint": env_fp,
        "env": env_versions,
        "source_snapshot": source_snapshot,
        "tests": tests,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(result, open(out, "w"), indent=2)
    n_pass = sum(1 for t in tests.values() if t["outcome"] == "passed")
    print(f"attested {len(tests)} outcomes ({n_pass} passed), bound to {len(source_snapshot)} source file(s) -> {out}")
    return 0 if proc.returncode == 0 else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="crossbio", description="crossbio-algo artifact validator"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="validate ONE artifact.json (schema + provenance)")
    v.add_argument("artifact")

    vc = sub.add_parser(
        "validate-chain",
        help="validate a dir of artifact.json: schema + chain + 8 content rules (5 cross-stage + 3 executable-trace)",
    )
    vc.add_argument("dir")

    vp = sub.add_parser(
        "validate-project", help="scan a project dir for artifacts and validate the chain"
    )
    vp.add_argument("dir")

    st = sub.add_parser(
        "stamp", help="compute & write the correct provenance_hash into an artifact.json"
    )
    st.add_argument("artifact")

    at = sub.add_parser(
        "attest", help="run pytest and write observed results.json (ATTESTED outcomes)"
    )
    at.add_argument("target", help="pytest target (file/nodeid), repo-relative")
    at.add_argument("--out", required=True, help="output results.json path")
    at.add_argument("--root", default=".", help="repo root to run pytest from (default cwd)")
    at.add_argument("--bind", action="append", default=[],
                    help="source file to bind the attestation to (repeatable); the test target is always bound")

    # ---- Process Assurance Layer (v0.3.1) ----
    ir = sub.add_parser("init-run", help="create a run-manifest.json for a research task")
    ir.add_argument("run_dir")
    ir.add_argument("--mode", default="standard", choices=["quick", "standard", "publication"])
    ir.add_argument("--tier", default="T2")

    nx = sub.add_parser("next", help="get the ALLOWED stage (state-machine gate)")
    nx.add_argument("run_dir")

    cs = sub.add_parser("complete-stage", help="mark a stage completed + link artifact/evidence")
    cs.add_argument("run_dir")
    cs.add_argument("stage")
    cs.add_argument("--artifact-id", default=None)
    cs.add_argument("--evidence-manifest", default=None)

    ss = sub.add_parser("skip-stage", help="skip a stage with explicit justification")
    ss.add_argument("run_dir")
    ss.add_argument("stage")
    ss.add_argument("--reason", required=True, choices=sorted(VALID_SKIP_REASONS))
    ss.add_argument("--justification", required=True)

    fn = sub.add_parser("finalize", help="check process compliance → READY_FOR_USER or PROVISIONAL_NONCOMPLIANT")
    fn.add_argument("run_dir")

    args = p.parse_args(argv)

    if args.cmd == "attest":
        return _run_attest(args.target, args.out, args.root, bind=args.bind)

    # ---- Process Assurance Layer handlers (v0.3.1) ----
    if args.cmd == "init-run":
        m = RunManifest.create(args.run_dir, mode=args.mode, target_tier=args.tier)
        print(f"run-manifest created: {m.path}")
        print(f"  mode={args.mode} tier={args.tier}  next={m.allowed_stage()}")
        return 0

    if args.cmd == "next":
        m = RunManifest.load(args.run_dir)
        allowed = m.allowed_stage()
        if allowed:
            print(f"ALLOWED_STAGE={allowed}")
        else:
            status, _, _ = m.finalize()
            print(f"NO_PENDING_STAGE  finalize={status}")
        return 0

    if args.cmd == "complete-stage":
        m = RunManifest.load(args.run_dir)
        try:
            m.complete_stage(args.stage, artifact_id=args.artifact_id, evidence_manifest=args.evidence_manifest)
            print(f"stage {args.stage} → completed  next={m.allowed_stage()}")
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        return 0

    if args.cmd == "skip-stage":
        m = RunManifest.load(args.run_dir)
        try:
            m.skip_stage(args.stage, args.reason, args.justification)
            print(f"stage {args.stage} → skipped ({args.reason})  next={m.allowed_stage()}")
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        return 0

    if args.cmd == "finalize":
        m = RunManifest.load(args.run_dir)
        status, missing, warnings = m.finalize()
        print(f"PROCESS: {status}")
        for w in warnings:
            print(f"  WARN: {w}")
        if missing:
            print("MISSING:")
            for item in missing:
                print(f"  - {item}")
        art_dir = os.path.join(args.run_dir, "artifacts")
        if os.path.isdir(art_dir):
            arts = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(art_dir, "*.json")))]
            arts = [d for d in arts if isinstance(d, dict) and "stage" in d and "stage_fields" in d]
            if arts:
                findings = core.validate_chain(arts, root=art_dir)
                errs = [f for f in findings if f.severity == "ERROR"]
                print(f"ARTIFACT_CHAIN: {'PASS' if not errs else 'FAIL'} ({len(arts)} artifacts, {len(errs)} errors)")
            else:
                print("ARTIFACT_CHAIN: ABSENT")
        else:
            print("ARTIFACT_CHAIN: ABSENT (no artifacts/ dir)")
        return 0 if status == "READY_FOR_USER" else 1

    if args.cmd == "stamp":
        a = json.load(open(args.artifact))
        core.stamp(a)
        json.dump(a, open(args.artifact, "w"), indent=2, ensure_ascii=False)
        print(f"stamped {args.artifact}: provenance_hash={a['provenance_hash']}")
        return 0

    if args.cmd == "validate":
        a = json.load(open(args.artifact))
        findings = core.validate_artifact(a)
    else:  # validate-chain | validate-project
        arts = _load_artifacts(args.dir)
        if not arts:
            print(f"no artifacts found in {args.dir}", file=sys.stderr)
            return 2
        findings = core.validate_chain(arts, root=args.dir)

    print(core.format_findings(findings))
    return 1 if any(f.severity == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
