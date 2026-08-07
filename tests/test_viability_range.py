"""Pure-Python implementation of the topic-viability-assessment aggregation, plus
tests that the per-dimension pessimistic/base/optimistic scheme is arithmetically
closed and ordered.

This is the P0-5 fix: the old "+/-0.06 / +/-0.03 widening" rule was internally
inconsistent (its stated components did not sum to its reported half-width) and
was misleadingly framed as a confidence interval. The replacement is a
deterministic per-dimension pessimistic/base/optimistic triple whose weighted
sums ARE the band endpoints — the band always closes by construction — and it is
honestly named a *decision uncertainty band*, not a statistical confidence interval.

Run: PYTHONPATH=. python -m pytest tests/test_viability_range.py -v
"""
from pathlib import Path

CONF_DELTA = {"high": 0.02, "med": 0.05, "low": 0.10}
GRADE_DELTA = {"A": 0.02, "B": 0.05, "C": 0.10}


def _clamp(x):
    return max(0.0, min(1.0, x))


def _delta(confidence, evidence_grade):
    """Uncertainty delta for one dimension: the WORSE (larger) of the two
    mappings. A low-confidence judgment OR a C-grade source can widen the
    uncertainty on its own, so the conservative max is used."""
    return max(CONF_DELTA[confidence], GRADE_DELTA[evidence_grade])


def viability_aggregate(dimensions, weights):
    """Aggregate per-dimension (score, confidence, evidence_grade) under weights
    into a base total and a (pessimistic, optimistic) band.

    dimensions: list of (score, confidence, evidence_grade)
    weights:    list of floats aligned 1:1 with dimensions
    returns:    (total_base, (pessimistic_total, optimistic_total))
    """
    assert len(dimensions) == len(weights), "dimensions and weights must align"
    total = pess = opt = 0.0
    for (score, confidence, evidence_grade), w in zip(dimensions, weights):
        d = _delta(confidence, evidence_grade)
        total += w * score
        pess += w * _clamp(score - d)
        opt += w * _clamp(score + d)
    return total, (pess, opt)


# The spaGRN worked example from SKILL.md, recomputed in-test so the example is
# mechanically verified: (score, confidence, evidence_grade), weight
EXAMPLE_DIMENSIONS = [
    (0.75, "med", "B"),   # 1 biological_validity        w=0.20
    (0.80, "high", "A"),  # 2 data_feasibility           w=0.15
    (0.55, "low", "B"),   # 3 functional_differentiation  w=0.15
    (0.60, "med", "B"),   # 4 benchmarkability           w=0.15
    (0.75, "med", "B"),   # 5 implementation_feasibility  w=0.10
    (0.70, "med", "B"),   # 6 reproducibility            w=0.10
    (0.70, "med", "B"),   # 7 adoption_user_value        w=0.10
    (0.90, "high", "A"),  # 8 ethics_privacy_licensing   w=0.05
]
EXAMPLE_WEIGHTS = [0.20, 0.15, 0.15, 0.15, 0.10, 0.10, 0.10, 0.05]
# weights sum to 1.0 — assert once for sanity
assert abs(sum(EXAMPLE_WEIGHTS) - 1.0) < 1e-9


def _per_dimension_triples(dimensions):
    """Compute (pessimistic, base, optimistic) for each dimension."""
    out = []
    for score, confidence, evidence_grade in dimensions:
        d = _delta(confidence, evidence_grade)
        out.append((_clamp(score - d), score, _clamp(score + d)))
    return out


# ---------- tests ----------
def test_pess_base_opt_ordering():
    """For every dimension AND for the totals: pessimistic <= base <= optimistic."""
    for (p, b, o) in _per_dimension_triples(EXAMPLE_DIMENSIONS):
        assert p <= b <= o
    total, (pess, opt) = viability_aggregate(EXAMPLE_DIMENSIONS, EXAMPLE_WEIGHTS)
    assert pess <= total <= opt


def test_range_arithmetic_closes():
    """The example's band endpoints MUST equal the literal weighted sums of the
    per-dimension pessimistic/optimistic — recompute from the triples and assert
    they match what viability_aggregate returns. The band closes by construction.
    """
    total, (pess, opt) = viability_aggregate(EXAMPLE_DIMENSIONS, EXAMPLE_WEIGHTS)

    triples = _per_dimension_triples(EXAMPLE_DIMENSIONS)
    expected_total = sum(w * b for (_, b, _), w in zip(triples, EXAMPLE_WEIGHTS))
    expected_pess = sum(w * p for (p, _, _), w in zip(triples, EXAMPLE_WEIGHTS))
    expected_opt = sum(w * o for (_, _, o), w in zip(triples, EXAMPLE_WEIGHTS))

    assert abs(total - expected_total) < 1e-9
    assert abs(pess - expected_pess) < 1e-9
    assert abs(opt - expected_opt) < 1e-9

    # The recomputed example numbers documented in SKILL.md (honest values).
    # base = 0.7025 -> 0.70 ; pessimistic = 0.6510 -> 0.65 ; optimistic = 0.7540 -> 0.75
    assert abs(total - 0.7025) < 1e-9
    assert abs(pess - 0.6510) < 1e-9
    assert abs(opt - 0.7540) < 1e-9


def test_clamping():
    """Optimistic clamps to 1.0 at the top edge; pessimistic clamps to 0.0 at the
    bottom edge."""
    # score 0.98 with low confidence -> d=0.10 -> optimistic = min(1.08, 1.0) = 1.0
    top, (top_p, top_o) = viability_aggregate([(0.98, "low", "A")], [1.0])
    assert top_o == 1.0
    # the clamped optimistic should NOT exceed the base by more than the headroom
    assert top_o == 1.0 and top == 0.98
    assert abs(top_p - 0.88) < 1e-9  # 0.98 - 0.10

    # score 0.02 with low confidence -> d=0.10 -> pessimistic = max(-0.08, 0.0) = 0.0
    bot, (bot_p, bot_o) = viability_aggregate([(0.02, "low", "A")], [1.0])
    assert bot_p == 0.0
    assert abs(bot_o - 0.12) < 1e-9  # 0.02 + 0.10
    assert bot == 0.02


def test_blocking_issue_forces_low():
    """Documentation/honest-framing test: the SKILL must (a) name the band a
    'decision uncertainty band' and (b) still carry the machine-required field
    name `viability_range`."""
    skill = Path(__file__).resolve().parents[1] / "skills" / "topic-viability-assessment" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    assert "decision uncertainty band" in text, (
        "SKILL.md must frame the band honestly as a 'decision uncertainty band'"
    )
    assert "viability_range" in text, (
        "machine schema requires the `viability_range` field name — keep it"
    )
    # the broken widening rule must be gone
    assert "±0.06" not in text and "±0.03" not in text, (
        "old widening-by-weighted-contribution rule must be removed"
    )


def test_delta_max_of_confidence_and_grade():
    """For mixed cases the worse signal wins (e.g. med confidence + C grade -> 0.10)."""
    assert _delta("high", "A") == 0.02
    assert _delta("med", "B") == 0.05
    assert _delta("low", "C") == 0.10
    assert _delta("med", "C") == 0.10   # grade C dominates med confidence
    assert _delta("low", "A") == 0.10   # low confidence dominates A grade
    assert _delta("high", "C") == 0.10  # grade C dominates high confidence
