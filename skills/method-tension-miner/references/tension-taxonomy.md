# Tension Taxonomy (v0.4.0)

Seven primary types. A tension carries exactly ONE primary `type`; auxiliary observations
go in `claim` / free text. Each type below: definition, the confusion it must NOT be
mistaken for, and what the machine validator enforces.

## 1. `empirical_contradiction`
**Definition**: independent studies report inconsistent results **under comparable
conditions** (same/convertible estimand, comparable regime).
**Not to be confused with**: different conditions → that is `unvalidated_interaction`;
different questions → `estimand_mismatch`.
**Validator**: every `evidence_refs` item has `evidence_strength: direct`; if only
indirect evidence exists it MUST be relabeled (`literature_inferred` + derivation chain).
**Death test**: could a referee reconcile the two papers by reading only their Methods
sections ("different preprocessing")? Then it is not yet a contradiction.

## 2. `assumption_conflict`
**Definition**: two methods' load-bearing assumptions cannot both hold in a named data
regime (e.g. MAR dropout vs. depth-dependent MNAR; independent samples vs. donor
repeated-measures).
**Not to be confused with**: methods merely using different math for compatible assumptions.
**Validator**: ≥2 `method_refs`; non-empty `conflict_regime` (the regimes where the
assumptions clash); each referenced method card carries ≥1 assumption.
**Prompt**: quote each assumption from its method card with its evidence ref — if you
cannot quote it, you have not read it.

## 3. `unvalidated_interaction`
**Definition**: condition A studied (evidence e1), condition B studied (e2), A∩B never
directly examined — AND a plausible mechanism for why A∩B behaves unlike either alone.
**Not to be confused with**: "nobody compared X and Y" (that is an evidence gap, not a
tension — P2: a gap becomes a candidate ONLY with mechanism + testable consequence).
**Validator**: `condition_evidence` mapping ≥2 conditions → evidence ids.
**Prompt**: for each condition, what is the evidence it was studied SEPARATELY? What is
the coverage limitation (where could A∩B hide)?

## 4. `information_loss`
**Definition**: a representation/summary/discretization demonstrably discards signal
relevant to the target question (e.g. spot-level aggregation destroying cell-type
mixtures; binarizing ATAC peaks discarding amplitude).
**Requirement**: state WHAT information, WHY it matters for THIS estimand, and a
prediction that would reveal the loss. Without the prediction it is a complaint, not a
tension.

## 5. `estimand_mismatch`
**Definition**: the methods answer different questions, so their "conflict" dissolves
once estimands are stated — YET the field keeps citing them as competing results.
**Validator expects**: both estimands quoted from the method cards.
**Why it is still a tension**: the mismatch itself is a finding — the field is
comparing incomparables; resolving it changes how benchmarks are read.

## 6. `identifiability_boundary`
**Definition**: the data design cannot distinguish competing mechanisms / parameter
explanations (degeneracy), and nobody has stated where that boundary is.
**Prompt**: name the degeneracy formally (which parameter combinations are
observationally equivalent); propose the minimum design change that breaks it.

## 7. `benchmark_blind_spot`
**Definition**: existing benchmarks systematically omit a condition critical to the
target application (e.g. no MNAR arm; no batch-confounded-with-phenotype arm; no
low-depth spatial regime).
**Not to be confused with**: "I wish benchmarks had my favorite dataset". The missing
condition must be load-bearing for a NAMED methodological reason.

---

## Evidence status (FR-04) — orthogonal to type

| status | meaning | machine check |
|---|---|---|
| `observed` | a source directly reports the phenomenon | ≥1 referenced evidence is `direct` |
| `literature_inferred` | derived across sources; original papers did not state it | derivation chain in claim/rationale (reviewer-checked) |
| `unverified` | plausible candidate, insufficient evidence | must NOT be presented as fact |

## Novelty status (FR-07)

`known_related_work` / `possible_overlap` / `not_found_in_scoped_search` /
`expert_review_required`. There is deliberately NO value that means "first/novel" —
neither the schema nor the validator can certify primacy, and neither may you.
`not_found_in_scoped_search` requires the scoped search record (queries + date +
coverage limitations) to be present.
