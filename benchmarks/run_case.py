#!/usr/bin/env python3
"""Skill-effectiveness benchmark harness.

Loads rubric.json + a case's grading.json, computes the weighted total per mode and the delta
vs no-skill. The SCORES in grading.json are assigned by a grader (pilot: same-model, NOT blinded
— see DESIGN.md limitations). This script only does the mechanical weighted sum + delta.

Usage:
  python run_case.py                       # grade all cases
  python run_case.py cases/phylo-recombination
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_rubric():
    return json.load(open(os.path.join(ROOT, "rubric.json")))


def weighted_total(scores, rubric):
    """scores: {dim: 0-3}; weighted normalized total in [0,1]."""
    W = sum(d["weight"] for d in rubric["dimensions"])
    s = sum(d["weight"] * (scores.get(d["dim"], 0) / 3.0) for d in rubric["dimensions"])
    return s / W if W else 0.0


def grade_case(case_dir, rubric):
    g = json.load(open(os.path.join(case_dir, "grading.json")))
    rows = []
    for mode in ("no-skill", "quick", "standard", "publication"):
        if mode in g["scores"]:
            rows.append((mode, weighted_total(g["scores"][mode], rubric)))
    base = next((t for m, t in rows if m == "no-skill"), None)
    print(f"\n# {g['case']}  (domain: {g.get('domain', '?')})")
    print(f"  {'mode':12} {'total':>6}   delta_vs_no-skill")
    for mode, total in rows:
        delta = "" if base is None or mode == "no-skill" else f"{total - base:+.2f}"
        print(f"  {mode:12} {total:6.2f}   {delta}")
    if "no-skill" in g["scores"] and "standard" in g["scores"]:
        ns, st = g["scores"]["no-skill"], g["scores"]["standard"]
        moved = [(d["dim"], ns.get(d["dim"], 0), st.get(d["dim"], 0))
                 for d in rubric["dimensions"] if ns.get(d["dim"], 0) != st.get(d["dim"], 0)]
        if moved:
            print("  dims that moved (no-skill -> standard):")
            for dim, a, b in moved:
                print(f"    {dim:28} {a} -> {b}")


def main(case=None):
    rubric = load_rubric()
    if case:
        cases = [case]
    else:
        cases = sorted(glob.glob(os.path.join(ROOT, "cases", "*")))
    cases = [c for c in cases if os.path.isfile(os.path.join(c, "grading.json"))]
    for c in cases:
        grade_case(c, rubric)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
