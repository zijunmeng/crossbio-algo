#!/usr/bin/env python3
"""crossbio-algo skill-effectiveness benchmark harness.

Two evidence streams:
  check               confound (a) guard — every case's prompt.md is free of its traps.json answer-key.
  objective <rundir>..  bias-free: crossbio_validate on each run's artifacts/ -> valid/invalid/absent.
  summary <case>..      per (case x mode): objective status + rubric totals (from grading.json).

LLM generation + rubric grading are Claude-driven (dispatch subagents that read the skill files),
not Python; this script orchestrates case structure, the objective check, and scoring aggregation.

Usage:
  python run_benchmark.py check
  python run_benchmark.py objective cases/<d>/runs/<mode>-1 ...
  python run_benchmark.py summary phylo-recombination scrna-imputation
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
CASES = os.path.join(ROOT, "cases")
sys.path.insert(0, REPO)


def _rubric():
    return json.load(open(os.path.join(ROOT, "rubric.json")))


def _weighted(scores, rubric):
    W = sum(d["weight"] for d in rubric["dimensions"])
    s = sum(d["weight"] * (scores.get(d["dim"], 0) / 3.0) for d in rubric["dimensions"])
    return s / W if W else 0.0


def _looks_like_artifact(d):
    return isinstance(d, dict) and "stage" in d and "stage_fields" in d


def _objective(rundir):
    """Run crossbio_validate on <rundir>/artifacts/. Returns {status, n_artifacts, errors, warnings}."""
    art = os.path.join(rundir, "artifacts")
    jsons = glob.glob(os.path.join(art, "*.json")) if os.path.isdir(art) else []
    if not jsons:
        return {"status": "absent", "n_artifacts": 0, "errors": [], "warnings": []}
    try:
        from crossbio_validate import core
        artifacts = [d for d in (json.load(open(f)) for f in jsons) if _looks_like_artifact(d)]
        if not artifacts:
            return {"status": "absent", "n_artifacts": 0, "errors": [], "warnings": []}
        findings = core.validate_chain(artifacts, root=art)
    except Exception as e:  # noqa: BLE001
        return {"status": "invalid", "n_artifacts": len(jsons),
                "errors": [f"validator crashed: {e}"], "warnings": []}
    errs = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARNING"]
    return {"status": "valid" if not errs else "invalid", "n_artifacts": len(artifacts),
            "errors": [f"{f.rule}: {f.message[:100]}" for f in errs],
            "warnings": [f.rule for f in warns]}


def cmd_check():
    """Confound (a) guard: prompt.md must NOT leak the traps.json answer-key (trap ids / 'Known traps')."""
    leaks = []
    n = 0
    for case in sorted(os.listdir(CASES)):
        cd = os.path.join(CASES, case)
        p, t = os.path.join(cd, "prompt.md"), os.path.join(cd, "traps.json")
        if not (os.path.isfile(p) and os.path.isfile(t)):
            continue
        n += 1
        prompt = open(p).read().lower()
        traps = json.load(open(t))
        for tr in traps.get("traps", []):
            tid = str(tr.get("id", "")).lower()
            if tid and tid in prompt:
                leaks.append(f"{case}: prompt.md leaks trap id {tid!r}")
        if "known traps" in prompt or "answer key" in prompt:
            leaks.append(f"{case}: prompt.md contains a traps/answer-key section (confound a)")
    if leaks:
        print("CONFOUND (a) LEAKS:")
        for x in leaks:
            print("  -", x)
        return 1
    print(f"check OK — {n} cases, no trap leaks in any prompt.md")
    return 0


def cmd_objective(rundirs):
    for rd in rundirs:
        r = _objective(rd)
        meta_p = os.path.join(rd, "meta.json")
        meta = json.load(open(meta_p)) if os.path.isfile(meta_p) else {}
        case = os.path.basename(os.path.dirname(rd))
        run = os.path.basename(rd)
        print(f"{case}/{run}  [{meta.get('mode', '?'):8}] -> {r['status']}  ({r['n_artifacts']} artifacts)"
              + (f"  warns={r['warnings']}" if r['warnings'] else ""))
        for e in r["errors"]:
            print("    ERROR:", e)
    return 0


def cmd_summary(cases):
    rubric = _rubric()
    for case in cases:
        cd = os.path.join(CASES, case)
        rundirs = sorted(glob.glob(os.path.join(cd, "runs", "*")))
        print(f"\n# {case}")
        by_mode = {}
        for rd in rundirs:
            meta = json.load(open(os.path.join(rd, "meta.json"))) if os.path.isfile(os.path.join(rd, "meta.json")) else {}
            mode = meta.get("mode", "?")
            gp = os.path.join(rd, "grading.json")
            scores = json.load(open(gp)).get("scores", {}) if os.path.isfile(gp) else {}
            tot = _weighted(scores, rubric) if scores else None
            by_mode.setdefault(mode, []).append((tot, _objective(rd)["status"]))
        base = next((t for m, rows in by_mode.items() if m == "no-skill" for t, _ in rows if t is not None), None)
        print(f"  {'mode':10} {'rubric':>7}  {'objective':>10}  delta_vs_no-skill")
        for mode in sorted(by_mode):
            for tot, status in by_mode[mode]:
                delta = "" if base is None or tot is None or mode == "no-skill" else f"{tot - base:+.2f}"
                rtot = f"{tot:.2f}" if tot is not None else "  n/a "
                print(f"  {mode:10} {rtot:>7}  {status:>10}  {delta}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    cmd = sys.argv[1]
    if cmd == "check":
        return cmd_check()
    if cmd == "objective":
        return cmd_objective(sys.argv[2:])
    if cmd == "summary":
        return cmd_summary(sys.argv[2:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
