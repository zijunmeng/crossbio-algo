---
name: topic-viability-assessment
description: Use when a researcher proposes a research direction, thesis/project topic, or a new method/algorithm to build, and wants to know whether it's worth pursuing — whether it is obsolete, overcrowded, or built on a flawed premise, what the risks are, and whether/how to pivot. 触发场景：用户提出研究方向 / 课题 / 想做的新算法或新方法，并询问"值不值得做""是否过时""有什么风险""要不要换方向"。Use BEFORE committing serious time to a new research line.
---

# Topic Viability Assessment

## Overview
Before sinking time into a research direction, run ONE honest viability verdict from the stance of a **skeptical senior reviewer**, grounded in **current evidence (not memory)**, scored under the user's actual target tier, and — critically — built on a **per-competitor deep-difference comparison classified into 5 competitor categories, not a head-count of names**, and expressed as a **multi-dimensional score with a decision uncertainty band (pessimistic–optimistic), not a false-precision single point**. Returns a tiered score, an explicit proceed/stop call, and a concrete pivot if the topic is dead.

A naked evaluation tends to either flatter (cheerlead), judge from stale memory, silently apply the "paradigm-novelty" ruler to every goal, or — the two most common failures — **(a) see a list of same-keyword tools and declare the field "crowded" without checking what each one actually does, and (b) declare a method "novel" because it uses a different mathematical mechanism than a neighbor, while ignoring that it competes for the exact same task**. This skill turns it into a reliable, structured, currency-checked, tier-aware, **competitor-classified and range-scored** decision.

## Target Tier — viability depends on the goal (ASK FIRST)
"Worth doing?" has no single answer — it depends on the user's target. **Ask the target tier before scoring, and score under that tier's ruler.** Do NOT silently apply the T1 ruler to a T2 goal — that falsely kills perfectly publishable work.

| Tier | Goal | Ruler |
|---|---|---|
| **T1** | paradigm-novelty paper (Nature/Cell/Science) | structurally novel, no functional substitute |
| **T2** | tool paper (Genome Biology / Bioinformatics / NAR / Briefings) | defensibly better than existing on ≥1 axis + engineering quality + fair benchmark that includes naive baselines |
| **T3** | learning / practice | no bar |
| **T4** | solve a specific data / internal need | does it solve your problem? |

A crowded field is a real threat to T1, a soft constraint to T2 (find one improvable axis), and irrelevant to T3/T4. Always state which ruler you scored under.

## When to Use
- Someone proposes a research direction / thesis topic / new method or algorithm and asks "is it worth doing?"
- Before committing weeks to a new research line
- Comparing several candidate topics

**Not for:** already-decided work that just needs execution; pure implementation questions.

## Core Stance: Reviewer, Not Cheerleader
- Default to skepticism. **BE BRUTALLY HONEST.** If the topic is dead, say so plainly.
- **Never judge "is this field still alive" or "is this crowded" from memory.** Verify with search first.
- **Never judge crowdedness from competitor names or counts.** Verify what each competitor actually does first (see Competitor Deep-Comparison Table below).
- **Never assume "different method ⇒ not a competitor."** Two methods using different math (VAE vs matrix factorization vs graph method) can still compete for the identical task — method difference does not exempt you from comparison.
- Question the **premise**, not just the method.

## Search Coverage — never single-source
Different topic types hide their competitors in different indexes; searching only one misses the real threats:
- **Biomedical / disease topics** → PubMed is primary (Nature Medicine, Cell, Nature Neuroscience...).
- **Bioinformatics / computational algorithms** → BOTH PubMed (formally published methods: Nature Methods, Genome Biology, Bioinformatics, NAR...) AND preprints (bioRxiv, arXiv q-bio/cs/lg). Flagship competitors (scVI, MAGIC, CellChat, SAVER...) are in PubMed — **skipping PubMed misses them**.
- **Pure ML/AI methods** → arXiv + venue proceedings (NeurIPS/ICML/ICLR) + Papers With Code.

Always search ≥2 sources appropriate to the topic type. **Deliberately search for the naive baselines in the space** (zero-imputation, mean-filling, k-NN, linear regression) — they are the most important real competitors and reviewers will demand you beat them.

## The 4 Questions
1. Has this been rendered **OBSOLETE** by a paradigm shift?
2. Is there evidence the core **PREMISE IS FLAWED**?
3. What is the **CURRENT consensus**? Has the field moved on?
4. If obsolete/flawed: what is the **RECOMMENDED PIVOT**? (For T2: which axis of existing tools is improvable, and which naive baseline must be beaten?)

## Competitor Deep-Comparison Table — MANDATORY before any score

**This is the heart of the skill. A score produced WITHOUT this table is invalid — redo.** The two most common failure modes this skill exists to prevent:

1. **Name-judging forbidden:** seeing a list of same-keyword tools (all called "spatial GRN", all called "scRNA imputation") and declaring the field "extremely crowded" from names alone. Names lie.
2. **Method-as-shield forbidden:** excusing a competitor as "not really a competitor" just because its mathematical mechanism differs. A VAE, a matrix-factorization method, and a graph method that all impute scRNA counts are **functional substitutes** for the same task — they compete regardless of method.

For every competitor surfaced by search (including the naive baselines in the space), build one row of the table by checking the actual paper/preprint text (cite it), NOT the abstract's framing, then assign it ONE of the five competitor categories:

| Competitor | Input data required | Method (core mechanism) | Output | Key limitation | Delta vs proposed | **Category (1–5)** |
|---|---|---|---|---|---|---|
| <name + cite> | what modality/scale it needs | how it actually works | what it returns | what it can't do | concrete input/method/output difference | 1–5 (see below) |

### The 5 competitor categories — assign exactly one per row

| # | Category | Meaning | What it implies for scoring |
|---|---|---|---|
| **1** | **Functional substitute** | Same task, results are substitutable for the user's decision. **Direct competitor — even if the method differs.** A VAE imputer and a k-NN imputer both substitute for "fill in missing counts" = both are functional substitutes. | **Must beat or differentiate against.** Unbeaten functional substitute ⇒ strong negative weight on functional differentiation + benchmarkability. |
| **2** | **Methodological neighbor** | Mathematical mechanism is closely related (shared model family, shared objective, shared regularizer). | **Should distinguish** — show why the mechanism change matters, or it reads as a variant. |
| **3** | **Input-slot alternative** | Serves the same downstream decision but needs input data the user doesn't have (e.g. requires spatial ATAC when the user has RNA only). **Genuine different slot for THIS user** — but only because of their data constraint, not because the task differs. | **Different slot for this user** — do not count as a direct competitor, but name it explicitly so reviewers see you considered it. The data constraint is real; it is just not the *only* axis of competition. |
| **4** | **Workflow alternative** | Reaches the same end via an upstream/downstream workaround that bypasses this method's step entirely (e.g. skipping imputation by using a method robust to sparsity). | **Indirect** — note it, account for it in adoption/user-value scoring. |
| **5** | **Naive baseline** | The simplest methods in the space — all-zero / mean-fill / k-NN / linear / nearest-neighbor / random. | **The most important real competitor. Must be benchmarked against and beaten.** Reviewers will demand this; failing to include it is an automatic benchmarkability penalty. |

**Key correction vs the old "yes/no" column:** a competitor is a **functional substitute (Category 1)** when it competes for the same task with substitutable output — **method difference does NOT save you from this classification.** Input-slot (Category 3) is still a legitimate "different slot for this user" when the user genuinely lacks that data, but it is no longer the *sole* test of "direct competitor." A VAE-vs-graph method pair serving the same user on the same data is Category 1, not Category 3.

Rules for filling the table:
- **"Input data required" is non-negotiable.** It determines whether a tool is an input-slot alternative (Category 3) for this user — but input difference alone does NOT exclude Category 1; what matters is whether the *output is substitutable for the user's decision*.
- **"Method" must be the actual mechanism** (what math/signal it uses), not a keyword. Method similarity drives Category 2; method difference does NOT automatically demote Category 1 to "non-competitor."
- **"Delta vs proposed" must be specific**, in input/method/output terms — never "similar approach, more mature". If you cannot state a concrete delta, you have not read the paper.
- **"Category" is decided by task/slot/mechanism reality, not by keyword overlap and not by a single axis.** Read the row and assign 1–5 honestly.

## Scoring — multi-dimensional, range-bounded, driven by the category analysis

### Why not a single 0–1 point
A bare `0.62` vs `0.55` is **false precision** — it implies a measurement resolution the evidence does not support. Replace the single point with a **multi-dimensional score** (8 independent dimensions), each with its own confidence and evidence grade, and aggregate into a **decision uncertainty band**. The width of the band reflects how much of the score rests on low-confidence / inferred / guessed evidence.

> **Honest framing.** This band is a **decision uncertainty band, NOT a statistical confidence interval.** It has no coverage guarantees — it is a structured, deterministic way to propagate each dimension's per-dimension confidence into a low–high bracket for the decision. Do not call it a "confidence interval" or "95% CI"; it is not one.

### The 8 dimensions

| # | Dimension | Weight | What it scores |
|---|---|---|---|
| 1 | **Biological validity** | 20% | Is the biological premise sound? Is the proposed mechanism mechanistically reasonable? |
| 2 | **Data feasibility** | 15% | Does the available data actually support the estimand? (inherits from data-audit; a tool that needs data the user doesn't have scores low here) |
| 3 | **Functional differentiation** | 15% | Is there a defensible delta vs the **functional substitutes (Category 1)**? (not just vs methodological neighbors — must beat the substitutes, not the neighbors) |
| 4 | **Benchmarkability** | 15% | Can it be benchmarked fairly, without leakage, AND including the naive baselines (Category 5)? A benchmark plan that omits the simplest baselines scores low here. |
| 5 | **Implementation feasibility** | 10% | Can it actually be built given the resources / compute / complexity? |
| 6 | **Reproducibility** | 10% | Can it be reproduced — seeds, environment, data availability, deterministic enough? |
| 7 | **Adoption / user value** | 10% | Will real users install and use it? Does it solve a real pain point vs the workflow alternatives (Category 4)? |
| 8 | **Ethics / privacy / licensing** | 5% | Can it be published and deployed lawfully and ethically? |

### Per-dimension output
For each dimension emit:
- `score` — on a 0–1 scale (use 0.25 increments; finer granularity is false precision). This is the **base** value.
- `pessimistic` — `clamp(score − d_i, 0, 1)`, the low end for this dimension (see deltas below)
- `optimistic` — `clamp(score + d_i, 0, 1)`, the high end for this dimension
- `confidence` — `low` / `med` / `high` (how sure are you of this score given the evidence)
- `evidence_grade` — `A` (measured / tested against source) / `B` (inferred from related evidence) / `C` (guess / memory / unstated)
- `blocking_issue` — boolean; true if a problem here is severe enough to stop the project regardless of total score
- `unknowns` — short list of what you would need to know to raise confidence

The uncertainty delta `d_i` is **derived from `confidence` and `evidence_grade` together** by taking the worse (larger) of the two mappings — the conservative read, since either a low-confidence judgment or a C-grade evidence source can widen the uncertainty on its own:

| `confidence` | delta | | `evidence_grade` | delta | | effective `d_i` |
|---|---|---|---|---|---|---|
| `high` | 0.02 | | `A` | 0.02 | | `max(0.02, 0.02) = 0.02` |
| `med`  | 0.05 | | `B` | 0.05 | | `max(0.05, 0.05) = 0.05` |
| `low`  | 0.10 | | `C` | 0.10 | | `max(0.10, 0.10) = 0.10` |

(For a mixed case — e.g. `confidence=med` but `evidence_grade=C` — `d_i = max(0.05, 0.10) = 0.10`. The worse signal wins.)

### Aggregation → total + decision uncertainty band
For each dimension `i` with weight `w_i` and base score `s_i` (the per-dimension `score`), and uncertainty delta `d_i` from the table above:

- `pessimistic_i = clamp(s_i − d_i, 0, 1)`
- `optimistic_i  = clamp(s_i + d_i, 0, 1)`

Then aggregate by literal weighted sum — both endpoints are computed, so the band **always closes by construction**:

- **`viability_total`** (base) = `Σ w_i · s_i`
- **`viability_range`** = `[ Σ w_i · pessimistic_i , Σ w_i · optimistic_i ]`

- The band is the honest statement. **Never report only the point.** If the band straddles a decision threshold, say so explicitly.
- Format the `viability_range` string as e.g. `"0.65–0.75 (decision uncertainty band: pessimistic–optimistic)"`.
- **Any `blocking_issue=true` ⇒ hard flag**; the total may still be computed, but `should_proceed` is set to false until the block is resolved, regardless of the number.

## Required Output — all fields, none optional
| Field | Meaning |
|---|---|
| `target_tier` | T1 / T2 / T3 / T4 — the ruler used |
| `competitor_comparison_table` | the per-competitor table above (MANDATORY — output is invalid without it), each row carrying a 1–5 category |
| `competitors_by_category` | the table rows grouped by category 1–5, so the genuine functional substitutes and the naive baselines are visible at a glance |
| `is_obsolete_or_flawed` | true if dead / dying / flawed premise |
| `paradigm_shift_status` | one sentence: where the field moved |
| `critical_evidence` | concrete papers/arguments — real, cited, verified against source text |
| `recommended_pivot` | specific alternative / improvable axis. NOT "try something else" |
| `viability_dimensions` | the 8 per-dimension objects (score [base] / pessimistic / optimistic / confidence / evidence_grade / blocking_issue / unknowns) |
| `viability_total` | weighted sum of the base scores, 0–1 |
| `viability_range` | decision uncertainty band, formatted as e.g. `"0.65–0.75 (decision uncertainty band: pessimistic–optimistic)"` — NOT a statistical confidence interval |
| `warning_flags` | specific concerns |
| `should_proceed` | true ONLY if genuinely viable under that tier AND no dimension has blocking_issue=true |
| `biggest_failure_risk` | the single most likely thing to sink it, even when proceeding |

## Score → Decision (applied to the decision uncertainty band, not the point)
Interpret the **band** (the `[pessimistic, optimistic]` bracket of `viability_range`) against the tier's ruler:
- **Band entirely ≥ 0.5** — viable under the tier; proceed; address `warning_flags`.
- **Band straddles 0.5** — borderline: the call depends on resolving the low-confidence dimensions. Flag them; proceed only with a plan to raise their evidence_grade to A/B.
- **Band entirely 0.3–0.5** — high risk under the tier: resolve flags or pivot.
- **Band entirely < 0.3** — seriously doubtful under the tier.
- **Band entirely < 0.15** — effectively dead, hard stop unless a concrete pivot is adopted.

These thresholds are strictest for T1. **For T2, a crowded keyword-space alone does NOT push you low** — only the absence of ANY improvable axis across the genuine functional substitutes (Category 1) does, and only if the naive baselines (Category 5) are not beaten by a defensible margin.

## Mandatory Discipline (close the loopholes)
- **Ask target tier first.** Never score without knowing it.
- **Build the Competitor Deep-Comparison Table before scoring.** A score with no table is invalid. Every row must be filled from verified source text, not from the competitor's name or abstract framing.
- **Classify every competitor into one of the 5 categories.** A bare yes/no is no longer allowed.
- **Method difference does NOT exempt a tool from Category 1.** Two tools with different math serving the same task on the same data are functional substitutes — score them as direct competitors.
- **Input-slot (Category 3) is a real distinction for THIS user, but not the only axis.** Keep it; do not let it be the sole reason a competitor is "not a competitor."
- **Benchmarkability must check the naive baseline (Category 5).** If your benchmark plan does not include the simplest methods in the space, benchmarkability scores low regardless of everything else.
- **Functional differentiation must be argued against Category 1 (functional substitutes), not only against Category 2 (methodological neighbors).** Beating a neighbor is not enough; you must beat the substitute.
- **Score must be multi-dimensional with per-dimension confidence + evidence_grade, AND every dimension must carry its own `pessimistic`/`optimistic` triple (score − d_i, score, score + d_i, clamped), and the total must carry a decision uncertainty band derived from those triples.** A single bare point like `0.62` is invalid — it is false precision.
- If `is_obsolete_or_flawed = true` → `recommended_pivot` MUST be non-empty and specific.
- A score with no `critical_evidence` is invalid — every score needs a cited basis, and the crowdedness basis must come from the table's category column.
- For any "is this current / obsolete" claim → **search first**, do not trust memory.
- Any dimension with `blocking_issue=true` ⇒ `should_proceed=false` until resolved, even if the total looks fine.
- Even when the band is entirely ≥ 0.5, state the single biggest thing that could make this fail.

## Red Flags — your assessment is probably invalid if:
- **You judged "crowded" from competitor names or counts without generating the per-competitor deep-comparison table → invalid; rebuild the table and re-score.**
- **You marked a tool "not a competitor" purely because its method differs, when it serves the same task on the same data → invalid; reclassify it as Category 1 (functional substitute).**
- **You classified every same-keyword tool as Category 1 without checking input/method/output slots → invalid; reclassify, some will be Category 2/3/4.**
- **Your benchmark plan has no naive baseline (Category 5) → benchmarkability score invalid; add it.**
- **You argued "different from STARNet (a methodological neighbor)" but never addressed the functional substitute (Category 1) → functional differentiation score invalid.**
- **You reported a single bare viability point (e.g. `0.62`) with no per-dimension breakdown and no pessimistic/optimistic triple per dimension → false precision; redo as multi-dimensional with a decision uncertainty band.**
- **Reporting a single bare viability point with no pessimistic/optimistic per dimension → false precision; redo.** (The band endpoints must be the literal weighted sums of the per-dimension `pessimistic`/`optimistic` — if they are not recomputable from the per-dimension triples, the band is invalid.)
- You scored without confirming the target tier → ask it first.
- "Field is healthy" based only on memory → verify currency.
- Encouragement with no risks/flags → cheerleading; redo as skeptic.
- An "obsolete" verdict with no pivot → incomplete; supply one.
- You applied the T1 ruler to a T2 goal → re-score under the correct ruler.
- The "Delta vs proposed" column reads "similar, more mature" with no concrete input/method/output difference → you haven't read the paper; redo that row.

## Handoff to Algorithm Design
You are a **counsel, not a gatekeeper** — you do NOT veto. Once the target tier is set and viability is scored under it (with the competitor table and the multi-dimensional score attached):
1. If viable under the tier → hand off directly.
2. If low under the tier but the user wants to proceed → that is the user's call; just make it informed (see `_shared/research-design-handoff.md`). Options (informed door): (a) accept the tier's risk, (b) lock an improvable axis that survived the category analysis vs the functional substitutes (T2), or (c) supply info that changes a low-confidence dimension's score (e.g. new evidence that raises evidence_grade from C to A).
3. Emit the handoff block (target_tier, verdict, total + decision uncertainty band, the competitor_comparison_table with categories, the functional substitutes + their improvable axes, the naive baselines that must be beaten, the user's choice) so algorithm-design inherits the real competitive landscape — not a name list.

The user decides; your job is to ensure they decide **informed under the right ruler, against the category-classified competitor set, and with an honest decision uncertainty band rather than a fake-precision point**, then carry the truth forward.

## Example — spaGRN-style spatial GRN from RNA-only data (the lesson case)
```
target_tier: T2 (tool paper)

competitor_comparison_table:
  | Competitor | Input | Method | Output | Key limitation | Delta vs proposed | Category |
  | SpaGRN (2023) | spatial RNA + ATAC-inspired motif | deep learning integrating cis motif | cell-type GRN | requires ATAC / motif info | proposed needs NO ATAC, same RNA→cis task | 1 (functional substitute) |
  | ISON (2024) | spatial RNA only | graph + co-expression regularized | cis/trans GRN | RNA-only but co-expression-based, no cis mechanism | proposed adds a cis-regulatory signal from RNA alone | 1 (functional substitute) |
  | STARNet (2022) | spatial ATAC + RNA | GCN on spot graph | cis GRN | hard-depends on spatial ATAC | proposed targets RNA-only users | 3 (input-slot alternative) |
  | spatialEnKF (2021) | spatial RNA only | ensemble Kalman filter on ODE GRN | trans dynamics GRN | ODE param ID, no cis regulation | proposed targets cis, different mechanism family | 2 (methodological neighbor) |
  | co-accessibility baseline | spatial RNA only | Pearson r over spot pairs | co-expression graph | no causality, no cis | proposed adds causal/cis signal | 5 (naive baseline) |
  | SCENIC+ (RNA-only fallback) | scRNA + motif | GRNBoost2 + motif enrichment | cis GRN | single-cell, ignores spatial | proposed adds spatial structure | 4 (workflow alternative — bypass spatial step) |

competitors_by_category:
  1 (functional substitute, must beat): SpaGRN, ISON
  2 (methodological neighbor, should distinguish): spatialEnKF
  3 (input-slot alternative, different slot for this user): STARNet
  4 (workflow alternative, indirect): SCENIC+ RNA-only fallback
  5 (naive baseline, must benchmark): co-accessibility baseline

is_obsolete_or_flawed: false
paradigm_shift_status: Field is segmenting by input modality (ATAC-available vs RNA-only), not collapsing; RNA-only cis-GRN is still an open slot.

critical_evidence:
  - SpaGRN pipeline verified to ingest motif/accessibility (source text, method section) — but it ALSO serves the same RNA→cis decision, so it is a functional substitute, not merely a different-slot tool.
  - ISON is RNA-only and co-expression-regularized — direct functional substitute for the RNA-only spatial GRN task; the delta must be a cis-regulatory signal, not "we use RNA too".
  - STARNet hard-requires spatial ATAC peaks (verified) — genuine input-slot alternative for a user without ATAC.
  - spatialEnKF is ODE/EnKF on the same RNA-only input — methodological neighbor; reviewers will ask why not EnKF.

recommended_pivot: none needed at the topic level — but lock the improvable axis: "the only RNA-only spatial method that recovers a cis-regulatory signal", AND mandate a fair benchmark vs ISON (Cat 1) + the co-accessibility naive baseline (Cat 5), not only vs ATAC-dependent tools.

viability_dimensions:   (each carries a pessimistic / base / optimistic triple; d_i = max(confidence_delta, grade_delta))
  #                                 score   pessimistic  optimistic  conf  grade  d_i   |  w       w·s      w·pess    w·opt
  1 biological_validity:        { score: 0.75, pessimistic: 0.70, optimistic: 0.80, confidence: med,  evidence_grade: B, blocking_issue: false, unknowns: ["is cis signal recoverable from RNA alone at spot resolution?"] }   # d_i=0.05 | 0.20  → 0.1500  0.1400  0.1600
  2 data_feasibility:           { score: 0.80, pessimistic: 0.78, optimistic: 0.82, confidence: high, evidence_grade: A, blocking_issue: false, unknowns: [] }                                                                                   # d_i=0.02 | 0.15  → 0.1200  0.1170  0.1230
  3 functional_differentiation: { score: 0.55, pessimistic: 0.45, optimistic: 0.65, confidence: low,  evidence_grade: B, blocking_issue: false, unknowns: ["concrete delta vs ISON on a shared dataset", "whether the cis signal is real or co-accessibility in disguise"] }   # d_i=0.10 | 0.15  → 0.0825  0.0675  0.0975
  4 benchmarkability:           { score: 0.60, pessimistic: 0.55, optimistic: 0.65, confidence: med,  evidence_grade: B, blocking_issue: false, unknowns: ["ground-truth cis GRN for spatial RNA is scarce; leakage risk"] }                  # d_i=0.05 | 0.15  → 0.0900  0.0825  0.0975
  5 implementation_feasibility: { score: 0.75, pessimistic: 0.70, optimistic: 0.80, confidence: med,  evidence_grade: B, blocking_issue: false, unknowns: ["training cost on full Stereo-seq slides"] }                                       # d_i=0.05 | 0.10  → 0.0750  0.0700  0.0800
  6 reproducibility:            { score: 0.70, pessimistic: 0.65, optimistic: 0.75, confidence: med,  evidence_grade: B, blocking_issue: false, unknowns: ["seed stability of cis edge recovery"] }                                              # d_i=0.05 | 0.10  → 0.0700  0.0650  0.0750
  7 adoption_user_value:        { score: 0.70, pessimistic: 0.65, optimistic: 0.75, confidence: med,  evidence_grade: B, blocking_issue: false, unknowns: ["whether RNA-only users currently fall back to SCENIC+ (Cat 4)"] }                    # d_i=0.05 | 0.10  → 0.0700  0.0650  0.0750
  8 ethics_privacy_licensing:   { score: 0.90, pessimistic: 0.88, optimistic: 0.92, confidence: high, evidence_grade: A, blocking_issue: false, unknowns: [] }                                                                                   # d_i=0.02 | 0.05  → 0.0450  0.0440  0.0460

viability_total: 0.7025   (Σ w·s = 0.1500 + 0.1200 + 0.0825 + 0.0900 + 0.0750 + 0.0700 + 0.0700 + 0.0450 = 0.7025)
viability_range: 0.65–0.75 (decision uncertainty band: pessimistic–optimistic)
  (pessimistic = Σ w·pess = 0.1400 + 0.1170 + 0.0675 + 0.0825 + 0.0700 + 0.0650 + 0.0650 + 0.0440 = 0.6510 → 0.65;
   optimistic  = Σ w·opt  = 0.1600 + 0.1230 + 0.0975 + 0.0975 + 0.0800 + 0.0750 + 0.0750 + 0.0460 = 0.7540 → 0.75)
  NOTE: this is a decision uncertainty band, NOT a statistical confidence interval — it has no coverage guarantees.

warning_flags:
  - "must benchmark against ISON (Cat 1) and the co-accessibility naive baseline (Cat 5) — beating STARNet (Cat 3) is not enough"
  - "reviewers may initially mis-read as crowded by keyword — lead with the category argument (only ISON is a real functional substitute)"
  - "the cis-vs-co-accessibility distinction (functional_differentiation, low confidence) is the swing factor — resolve it before submission"

should_proceed: true
biggest_failure_risk: the cis signal is indistinguishable from plain co-accessibility (Cat 5 baseline) on the available benchmarks, collapsing functional differentiation and turning the method into a re-skin of the naive baseline.
```
Note how this differs from a name-only read: "SpaGRN/STARNet/ISON all do spatial GRN" would wrongly declare the field crowded AND wrongly excuse SpaGRN/ISON as "different method". The category table shows only ISON is a true functional substitute (Cat 1), STARNet is a different input-slot (Cat 3), and the real swing factors are functional_differentiation (vs ISON) and benchmarkability (vs the co-accessibility naive baseline) — both low/medium confidence, hence a wide decision uncertainty band (0.65–0.75) rather than a fake-precision point.

## References
- `_shared/research-design-handoff.md` — the viability→design contract; carry the competitor_comparison_table (with categories) forward so **crossbio-algo:algorithm-design**'s `novelty_basis` is checked against the genuine functional substitutes (Cat 1) and the naive baselines (Cat 5).
