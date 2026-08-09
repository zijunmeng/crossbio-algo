"""crossbio CLI — entry point for the artifact validator.

Subcommands:
  validate         <artifact.json>   validate ONE artifact (schema + provenance)
  validate-chain   <dir>             validate a dir of artifact.json as a chain
                                     (schema + parent-chain + stage-order + fatal-gate
                                      + the 5 cross-stage content rules)
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


def _run_attest(target, out, root="."):
    """Run pytest on `target` (from `root`), parse the JUnit XML, write results.json (observed
    outcomes). The validator's rule_test_link reads this to ATTEST test status — code.json has no
    authority to self-declare 'passed' (reviewer §2, v0.2.3)."""
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

    def _sh(cmd):
        try:
            return subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None

    git_commit = _sh(["git", "rev-parse", "HEAD"])
    env_hash = hashlib.sha256((_sh([sys.executable, "--version"]) or "").encode()).hexdigest()[:12]
    result = {
        "generated_via": "crossbio attest",
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_commit,
        "env_hash": env_hash,
        "tests": tests,
    }
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    json.dump(result, open(out, "w"), indent=2)
    n_pass = sum(1 for t in tests.values() if t["outcome"] == "passed")
    print(f"attested {len(tests)} outcomes ({n_pass} passed) -> {out}")
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
        help="validate a dir of artifact.json: schema + chain + 5 cross-stage rules",
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

    args = p.parse_args(argv)

    if args.cmd == "attest":
        return _run_attest(args.target, args.out, args.root)

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
