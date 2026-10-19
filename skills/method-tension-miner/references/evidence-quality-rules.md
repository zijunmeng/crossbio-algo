# Evidence Quality Rules (v0.4.0)

What counts as evidence for a method card or a tension — and what does not.

## Source priority (highest first)

1. **Method paper, methods section + supplement** — the ONLY authoritative source for
   assumptions, objective, and validation regimes.
2. **Source code + release notes** — resolves ambiguities the paper hides (defaults,
   preprocessing, silent filters). Record repo + commit/version.
3. **Benchmark studies** (independent head-to-head) — for `empirical_contradiction` and
   `benchmark_blind_spot`.
4. **Reviews** — for orientation and gap-hunting ONLY; a review's characterization of a
   method is `indirect` evidence until checked against the primary.
5. **Preprints / conference abstracts** — usable, flagged as such in `notes`.

## Every evidence item MUST carry a locator

`locator` = section / table / figure / equation / code path where the claim lives
(e.g. "Fig. 3b", "supplement §2.4, eq. S7", "src/impute.py:L141"). A citation without
a locator cannot be checked by a human later — treat it as missing.

## `direct` vs `indirect` (the load-bearing distinction)

- `direct`: the source itself reports the exact claim (the contradiction table, the
  failure-mode paragraph, the ablation).
- `indirect`: the source supports a COMPONENT of your claim; the claim itself is your
  synthesis across sources.

Rules:
- `empirical_contradiction` and `evidence_status: observed` require ≥1 `direct` ref —
  the validator enforces this.
- Cross-paper synthesis is GOOD science — label it `literature_inferred` and write the
  chain. The sin is not inference; the sin is inference dressed as observation.
- Review says "method A fails on X" → indirect until you see A's paper say it.

## Fabrication guards

- Never cite a paper you have not opened (title-matching is not reading).
- If a doi/url is unavailable offline, say so in `notes` — do not guess identifiers.
- Quotes in `claim_supported` should be close to the source's own wording.
- Sample of last resort: if you cannot verify a load-bearing claim, the tension's
  ceiling is `unverified`.

## Search-record honesty (FR-07/FR-08)

Any `not_found_in_scoped_search` novelty claim and any `no_qualified_tension` result
must record: sources searched, queries, `searched_at` date, and
`coverage_limitations` (language restrictions, paywalled journals not searched,
preprint cutoff, time budget hit). "Not found in the scope I actually searched" is the
only defensible phrasing — it is never "nobody has studied this".
