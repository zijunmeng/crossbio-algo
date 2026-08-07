---
name: algorithm-design
description: Use when someone wants to DESIGN a new algorithm, method, or model from scratch — to go beyond recombining existing methods and find a genuinely novel, mathematically-grounded approach. 触发场景：用户要设计新算法 / 新方法 / 新模型，或卡在"现有方法都不行、想找新思路"，或想把一个问题做得更有数学深度和创新性。Use BEFORE writing code or settling on a known method.
---

# Algorithm Design

## Overview
Designing a new algorithm means **formalizing a method that is useful**, not chasing structural novelty for its own sake. Many of the best algorithms are **rigorous combinations** of mature methods; a strict "must invent, not recombine" stance **induces pseudo-novelty** — it pushes the designer away from robust known solutions toward structurally-different-but-worse ones (our spatialEnKF / spatialDST collision with existing work is the lesson: novelty-first, utility-second designs reinvent things and still lose).

This skill enforces a **formal method contract** — a 15-required + 2-optional (17-field) specification grouped into Problem / Formalization / Algorithm / Guarantees / Validation — built by a 4-step process: **abstract to the mathematical essence → optionally import cross-domain sparks → state where it must fail → simulation-first**.

Two disciplines make it work:
- **Externalized reasoning (推理外显)**: the agent decides the professional calls itself, but explains *why* at every step. The user corrects or overrides whenever they want — they are never *required* to make a professional either/or they can't judge.
- **Honor the handoff**: if this follows a **crossbio-algo:topic-viability-assessment** run, read `_shared/research-design-handoff.md` and design **under the competitor constraint** it carries.

## When to Use
- Someone wants to design a new algorithm / method / model (not just run or compare existing ones)
- They're stuck: "existing methods don't work for my case, I need a new idea"
- They want more mathematical depth or genuine novelty

**Not for:** running a standard pipeline; applying a known method; debugging; hyperparameter tuning.

## Core Stance: Utility First, Novelty Explicit

The stance is **Utility first, novelty explicit**:

- **Utility first.** Designing a useful method is the goal. You MAY combine mature methods rigorously — many excellent algorithms are exactly that. Do NOT proactively avoid a robust known method just to be "structurally novel." If a careful combination of known methods is the strongest solution to the user's problem, recommend the combination.
- **Novelty explicit.** But you MUST state the **novelty locus** explicitly — where, precisely, is this method new? The valid loci are: **new estimand** (asking a question no current method asks) • **new data regime** (a regime where existing methods have not been characterized) • **new objective / likelihood** • **new constraint** (e.g. memory-bounded, streaming, privacy) • **new inference mechanism** • **new uncertainty guarantee / calibration** • **new scalability regime** • **new usability / robustness property**. Structural rearrangement alone ("we added a module / stacked two losses") is NOT a novelty locus.
- **Cross-domain inspiration is OPTIONAL fuel, not a requirement.** Reaching outside the home domain is a source of *non-obvious* sparks — use it when it produces a genuinely better solution. It is NOT a requirement for novelty, and it does NOT forbid combination of in-domain methods. Do not force cross-domain borrowing if a mature combination is stronger.

This stance replaces the older "Inventor, Not Librarian / inventing, not recombining" stance. The older stance induced pseudo-novelty: novelty-first designs that reinvented existing work and lost to it on the axis that actually mattered.

## Two Classes of Decision

### A. User decisions (collect ONCE, up front — these the user can actually judge)
Ask these in a single opening pass before designing:
- **Target tier** — T1 (top journal, structurally novel) / T2 (tool, defensibly better than competitors + benchmark) / T3 (practice / learning) / T4 (solve a specific-data need).
- **Resource constraints** — GPU available? What data (modality, scale, access)? What tool stack / frameworks are they fluent in?
- **Biological preference** — what mechanism / regulation / phenomenon do they actually care about (so the abstraction doesn't drift away from their science)?

### B. Professional calls (the agent decides, states recommendation + reason, user may override but is never forced to pick)
- Mathematical abstraction choice.
- Cross-domain method selection (and the decision of whether cross-domain borrowing helps at all).
- Objective / likelihood formulation.
- Identifiability analysis.
- Optimization / inference method.
- Failure-boundary derivation.
- Simulation parameters and regime.
- Benchmark protocol design.
- Concrete technical / library choices.

These are **not** turned into either/or questions for the user. The agent commits to a recommendation with its rationale; the user interjects only if they disagree.

## The 4-Step Inventive Process — autonomous run, externalized reasoning, pause only at global forks

Run all four steps. At each step: **state the choice + the reason out loud** (推理外显), then continue. Do NOT stop to ask a binary question unless hitting a **global fork** (see below). Collect the up-front user decisions (Section A) first, then run.

### 1. Mathematical Abstraction (first)
Commit: "Abstracting this as fundamentally a **[X]** problem, because [reason tied to the data structure / goal]." Give the runner-up abstraction you rejected and why. Typical X: masked/sparse matrix completion • signal recovery on a graph • manifold regression with missing data • zero-inflated latent inference • distribution alignment (OT) • directed-graph / causal discovery • spectral clustering • ordered-structure (trajectory) recovery.
**Global fork (stop and ask) only if**: two abstractions lead to *entirely different algorithm families and validation paths* and you cannot pick on technical merit alone — then present both directions with the trade-off and let the user steer.

### 2. Cross-Domain Inspiration (optional spark — engage when it gives a non-obvious edge)
Open `cross-domain-inspiration.md` (next to this file) — the essence→domains map (fluid dynamics, info theory, game theory, satellite remote sensing, quantitative finance, operations research, cosmology…) plus the method pool. Engage it **when** a cross-domain method would plausibly give a non-obvious improvement on at least one axis (estimand / scalability / robustness / inference). If you engage it: state "Mined [domains] for essence X; sparks A / B / C; **selecting [method] because [reason]**", name the discarded sparks and why. If you do NOT engage it (a mature in-domain combination is strongest), state that explicitly and why — cross-domain borrowing is optional, not a checkbox. **Never** force ≥2-domain borrowing to satisfy an old novelty rule.

### 3. Failure Boundary (derive, don't assume)
State: "This algorithm degrades / fails when [mathematical condition], because [mechanism]." Derive it from the abstraction, not from intuition. Fold in any platform/data failure modes surfaced in the up-front user pass. Do not stop to ask.

### 4. Simulation-First (before real data)
Commit: "Building synthetic data with a fully specified **data-generating process (DGP)** to probe that boundary." Specify: the DGP (not just parameter sweeps), the **null regime** (where the true signal is absent — method must not hallucinate), the **adversarial regime** (where the failure condition is deliberately triggered), the **oracle upper bound** (the best any method could do with ground truth), the **trivial lower bound** (a naive baseline — see Validation), and the swept parameter ranges and why they stress the boundary. Do not stop to ask.

## Required Output — the Formal Method Contract (5 groups · 15 required + 2 optional fields)

None of the **required** fields are optional; the **encouraged** fields are filled when they apply. Missing a required field = invalid output.

### Group P — Problem (all required)
| Field | Meaning |
|---|---|
| `problem_definition` | One-sentence precise statement of the problem (what is being solved, for what input, to what end). |
| `estimand` | What exactly is being estimated / predicted / inferred (e.g. "the unobserved true count at a dropout position"). Carries the `estimand` from **crossbio-algo:data-and-estimand-audit** if it exists. |

### Group F — Formalization (all required)
| Field | Meaning |
|---|---|
| `mathematical_abstraction` | "Fundamentally a [X] problem" + the rejected alternative and why. |
| `notation_and_shapes` | Full notation with matrix shapes (e.g. `X ∈ R^{n×g}` counts, `Z ∈ R^{n×k}` latent, `M ∈ {0,1}^{n×g}` mask). Define every symbol. |
| `assumptions` | Data-generating assumptions: count distribution (NB / Poisson / ZINB), dropout mechanism (MCAR / MAR / MNAR), batch structure, independence assumptions. Carries missingness / cohort info from the **data-and-estimand-audit** if it exists. |
| `objective_or_likelihood` | **The objective function or likelihood being maximized / minimized.** E.g. "maximize NB log-likelihood + λ·graph-Laplacian smoothness penalty" or "minimize MSE subject to conservation constraint". Must be a concrete expression, not a verbal description. **This is the core of formalization — vocabulary-only abstraction without an objective is invalid.** |
| `identifiability` | **Can the estimand be uniquely determined from data of this type?** State the condition under which it is identifiable, and the condition under which it is NOT (e.g. "if dropout probability is coupled to true expression → MNAR → true count and dropout are confounded → not identifiable without an instrument"). If not identifiable in general, state what additional assumption or data makes it identifiable. |

### Group A — Algorithm (all required)
| Field | Meaning |
|---|---|
| `cross_domain_inspiration` | Cross-domain sparks (if engaged): ≥0 domains outside the home field + method + why selected, OR an explicit statement that a mature in-domain combination is stronger and cross-domain borrowing was not engaged. |
| `proposed_algorithm` | Concrete algorithm steps, derived from the abstraction and objective (not a re-listing of existing field methods). |
| `optimization_or_inference` | **How the objective is solved.** EM / SGD / Adam / variational ELBO / closed-form / MAP / MCMC? Convergence guarantees (convex? local opt? initialization-sensitive?)? Stopping criterion? A method without a solver is a sketch, not an algorithm. |
| `complexity` | **Time and space complexity.** `O(?)` per iteration and total; whether it scales to the user's `n` cells / `g` genes / samples. Memory footprint. Identify the bottleneck step. |

### Group G — Guarantees (`failure_boundaries` required; `uncertainty_and_calibration` + `invariances` encouraged)
| Field | Meaning |
|---|---|
| `failure_boundaries` | Condition under which it degrades / fails, with **both** the condition (when) and the mechanism (why). Derived from the abstraction. |
| `uncertainty_and_calibration` *(encouraged)* | Point estimate or interval / posterior? If uncertainty is reported, is it calibrated (coverage on synthetic) or only relative? What is the uncertainty over — the estimand, a downstream prediction? |
| `invariances` *(encouraged)* | What transformations leave the output unchanged — cell-index permutation? gene-index permutation? count scaling? batch index? State as invariance statements. |

### Group V — Validation (all required)
| Field | Meaning |
|---|---|
| `simulation_dgp` | The full **data-generating process** (not just parameter sweeps): how the synthetic ground truth is generated, how observations / mask / noise are sampled from it. Must include: **null regime** (signal absent — method must return null, not hallucinate), **adversarial regime** (failure condition deliberately triggered), **oracle upper bound** (best achievable with ground-truth access), **trivial lower bound** (a naive baseline's score), and the swept ranges with reason. |
| `benchmark_protocol` | **The benchmark protocol.** Vs which competing methods' which implementations (cite code/version)? Are conditions fair (same preprocessing, same held-out mask, same compute budget)? Is there data leakage (test set leaking into imputation / batch correction)? **MUST include naive baselines** — all-zero / global-mean / nearest-neighbor / copy-the-input — because the simplest competitors are the most important real ones (a method that loses to mean-imputation has no utility). |
| `novelty_or_utility_basis` | **Utility first, novelty explicit.** Name the novelty locus (new estimand / data regime / objective / constraint / inference / uncertainty guarantee / scalability / usability). Tier-dependent: **T1** = structurally novel locus; **T2** = defensibly better than named top_competitors on ≥1 axis under fair benchmark (NOT necessarily structurally novel — rigorous combination can be T2); **T3** = N/A; **T4** = solves the stated specific-data need. **If a viability handoff exists, MUST state the delta vs each named top_competitor.** |

## Mandatory Discipline (close the loopholes)
- **MUST give `objective_or_likelihood` + `identifiability`.** An output with a `mathematical_abstraction` full of vocabulary ("it's a manifold / latent / graph problem") but no concrete objective function and no identifiability discussion is **vocabulary packaging, not formalization** — invalid; redo.
- **MUST give `optimization_or_inference` + `complexity`.** An algorithm must state not just *what* it does but *how it is solved* (solver + convergence) and *how expensive it is* (time/space, scales to N cells?). A method with no solver and no complexity is a sketch — invalid; complete.
- **MUST give a `benchmark_protocol` that includes naive baselines** (all-zero / global-mean / nearest-neighbor / copy-input). A protocol that only compares to fancy SOTA methods and omits the simple competitors is missing the most important real comparison — invalid; add naive baselines.
- Starts from an existing method ("use a VAE…") without abstraction → redo from the structure (the abstraction is still required even though combination is now allowed — combination must be principled, not bolt-on).
- No `failure_boundaries` → incomplete; derive one (with both condition and mechanism).
- No `simulation_dgp` (or a DGP that is only parameter sweeps, no null/adversarial/oracle/trivial regime) → incomplete; design the full probe.
- `novelty_or_utility_basis` = "added a module / added a loss" with no named novelty locus → invalid; name the locus or concede it's a T2 utility improvement.
- **Skipping the up-front user-decision pass, OR running the design without externalizing the reasoning (no recommendation + reason at each step) → invalid**; collect user decisions first, then run with 推理外显, pausing only at true global forks.
- **Asking the user to make a professional either/or (math abstraction / objective / identifiability / solver / cross-domain method / failure condition / sim params / benchmark design) that they cannot judge → invalid**; that is the agent's call — recommend with reasons, let the user override voluntarily.
- **Ignoring a viability handoff** (designing as if competitors don't exist) → invalid; honor the contract and state the delta vs each named top_competitor in `novelty_or_utility_basis`.

## Red Flags
- Has `mathematical_abstraction` but no `objective_or_likelihood` → "vocabulary packaging, not formalization" — invalid; force a concrete objective.
- No `identifiability` discussion → "never considered whether this can be solved from the given data" — invalid; add the identifiability analysis.
- `benchmark_protocol` has no naive baseline (all-zero / mean / nearest-neighbor) → "never compared to the simplest real competitor" — invalid; add naive baselines.
- Every cited method is from the problem's own field AND the design claims cross-domain novelty → field-locked; either engage true cross-domain sparks or drop the novelty claim.
- Skipped abstraction, went straight to "use a VAE / transformer / GNN" → librarian mode; abstract first (abstraction is required even for combination designs).
- No stated failure condition → you don't understand your own algorithm.
- "Tested on a benchmark" is the only validation (no null/adversarial/oracle/trivial regime in `simulation_dgp`) → benchmarking, not boundary-finding.
- Professional calls made with no recommendation / no stated reason → black-boxed; re-run with 推理外显 (state choice + why at each step).
- User was forced into a binary on a technical judgment outside their scope → mis-scoped collaboration; the agent should have recommended.

## Artifact output
In addition to the formal method contract above (human-readable: 15 required + 2 optional = 17 fields), this stage emits **`artifact.json`** (schema: `schemas/stage-schemas.json`): `stage_fields = {problem_definition, estimand, notation_and_shapes, objective_or_likelihood, identifiability, failure_boundaries, complexity}`.
Three fields propagate downstream and are cross-stage-validated (`_shared/artifact-validation.md`):
- **`estimand` MUST == `data-audit.artifact.estimand`** (rule 1) — drift requires an explicit `estimand_change_justification`; silent change = invalid.
- **`failure_boundaries`** propagate to spec — every boundary item MUST have a matching `spec.acceptance_criteria` with `traces_to` naming it (rule 2, no orphans).
- **`notation_and_shapes`** propagate to spec — `spec.module_interfaces` shapes/names MUST match (rule 3; this is the rule that would have caught SCOUT's TruncatedSVD-vs-np.linalg.svd drift).

## References
- `cross-domain-inspiration.md` (in this folder) — the 28-domain essence→domains map + method pool.
- `_shared/research-design-handoff.md` — the viability→design contract (read if chained from **crossbio-algo:topic-viability-assessment**).
- `schemas/stage-schemas.json` + `_shared/artifact-validation.md` — the machine-checkable artifact this stage emits.

## Example — scRNA-seq imputation (formal method contract)

```
# Group P — Problem
problem_definition: Recover the true transcript count at positions rendered zero by technical dropout in sparse scRNA-seq, so downstream differential / trajectory analyses are not biased by technical zeros.
estimand: The unobserved true count y*_ig at a dropout position (M_ig = 0) for cell i, gene g — i.e. the counterfactual count that would have been observed without technical dropout.

# Group F — Formalization
mathematical_abstraction:
  Fundamentally a masked signal-recovery problem on a cell-similarity graph.
  (rejected: zero-inflated latent inference via VAE — would force a generative family and bury the
   recovery structure in a latent prior, making the failure mode opaque; the graph-signal view keeps
   the failure boundary transparent.)
notation_and_shapes:
  X ∈ R_+^{n×g}    observed counts (n cells, g genes)
  M ∈ {0,1}^{n×g}  mask (1 = observed, 0 = dropout)
  W ∈ R_+^{n×n}    cell-similarity graph weights (kNN, row-normalized)
  L ∈ R^{n×n}      graph Laplacian of W
  θ = (y*, p)      parameters: true counts y* ∈ R_+^{n×g}, dropout probs p ∈ [0,1]^{n×g}
assumptions:
  - Count distribution: Negative Binomial (overdispersed), X_ig ~ NB(mean=y*_ig, dispersion=φ_g).
  - Dropout mechanism: P(M_ig=0) = sigmoid(α + β·y*_ig). Under MCAR/MAR (β≈0) imputation is benign;
    under MNAR (β<0, dropout coupled to low expression) recovery is confounded (see identifiability).
  - Smoothness: true counts are smooth on the cell graph, y*^T L y* small (cells close on graph have
    similar expression).
  - Batch / cohort structure is carried from the data-and-estimand-audit and modeled as a known covariate.
objective_or_likelihood:
  Maximize over y* (at masked entries):
    ℓ(y*) = Σ_{ig: M_ig=1} log NB(X_ig | y*_ig, φ_g)        # likelihood at observed entries
          − λ · tr(y*^T L y*)                                # graph-Laplacian smoothness penalty
          + Σ_{ig: M_ig=0} log p(M_ig | y*_ig)               # dropout model (treats M as observed)
  i.e. NB log-likelihood at observed entries, regularized toward smoothness on the cell graph,
  jointly with a logistic dropout model. λ ≥ 0 is the smoothness weight.
identifiability:
  NOT identifiable in general under MNAR: if dropout probability is coupled to the true count
  (β ≠ 0), then a low observed count and a high-but-dropped-out count produce the same evidence,
  so y* at masked entries is confounded with the dropout model parameters.
  Identifiable under either: (a) MAR dropout (β = 0) — then dropout carries no y* information and y*
  is pinned by the NB likelihood at observed entries + smoothness; or (b) an external instrument
  (e.g. spike-ins with known true counts and same dropout) that separately identifies the dropout
  curve. We assume (a) for the primary method and treat (b) as an optional extension; the MNAR
  regime is reported as a failure boundary, not papered over.

# Group A — Algorithm
cross_domain_inspiration:
  Engaged:
    - Graph signal processing (graph wavelet / graph-Fourier low-pass): denoise by suppressing
      high graph-frequency components — the cell-similarity graph is the native domain.
    - Compressed sensing: sparse recovery from few observations given a sparsifying transform —
      weaker fit, since scRNA expression is not sparse on the cell graph in the CS sense.
  Selected: graph signal processing — native domain, smoothness assumption is a graph-bandwidth
  assumption; CS discarded as its sparsity prior is a weaker match to the data.
proposed_algorithm:
  Graph-frequency-thresholded imputation:
    1. Build kNN cell-similarity graph W from observed-entry cosine similarity.
    2. Compute graph Laplacian L and its eigen-decomposition.
    3. For each gene, project observed counts onto graph-frequency basis; attenuate high-frequency
       (above cutoff τ) components (noise); keep low-frequency (smooth) components.
    4. At masked entries, fill with the low-frequency reconstruction.
    5. Fit the logistic dropout model p(M|y*) jointly; iterate steps 3–4 (cf. optimization below).
optimization_or_inference:
  Alternating maximization (a block-EM-style scheme):
    - E-step-ish: given current dropout params, solve the smoothness-regularized NB MLE for y* —
      this is a convex quadratic-ish prox step (closed-form prox on the Laplacian penalty + NB
      gradient step), converges in O(1/λ) iterations for fixed dispersion.
    - M-step: given y*, update dropout logistic params by Newton steps (convex).
  Convergence: alternating ascent on a tight lower bound of ℓ → monotonic non-decrease; converges
  to a coordinate-wise optimum (NOT guaranteed global; initialization-sensitive — initialize y* from
  observed-entry mean imputation). Stop when relative change in ℓ < 1e-4.
complexity:
  Per outer iteration:
    - Graph eigen-decomposition (precompute once): O(n^3) — for large n, use Lanczos to truncate to
      top-k low-frequency eigenvectors → O(k·n·k_nn).
    - Per-gene frequency filter: O(n·k) once eigenvectors are fixed.
    - Newton dropout update: O(n·g) per gene.
  Total: O(k·n·k_nn + n·g·T) for T outer iterations after precompute.
  Memory: O(n·k) for truncated eigenvectors + O(n·g) for y* — bottleneck is the n×g count matrix.
  Scales to ~10^5 cells with truncated eigendecomposition; full eigendecomposition caps at ~10^4.

# Group G — Guarantees
failure_boundaries:
  - Condition: dropout is MNAR (β strongly negative — dropout coupled to low true expression).
    Mechanism: the NB likelihood at observed entries cannot distinguish a genuinely low-expressing
    cell from a dropped-out high-expressing cell; the smoothness prior then smooths toward neighbors,
    which under MNAR systematically over-imputes. Recovery error grows roughly linearly in |β|.
  - Condition: cell graph mis-estimates similarity in ultra-sparse regimes (<500 genes detected).
    Mechanism: kNN graph collapses onto a few hubs; the low-frequency subspace is too small to
    carry signal → over-smoothing erases real biological variation.
uncertainty_and_calibration (encouraged):
  Point estimate by default. Optional: posterior variance on y* at masked entries from the Laplacian
  precision matrix inverse — reported as relative uncertainty. Coverage on synthetic under MAR is
  ~nominal; under MNAR it is over-confident (uncertainty understated) — report as a known limitation.
invariances (encouraged):
  - Permutation-invariant in cell index and gene index (graph built per-run).
  - NOT scale-invariant: raw counts vs library-size-normalized counts change the NB dispersion fit.
  - NOT invariant to batch index: batch must be a covariate; ignoring batch biases the graph.

# Group V — Validation
simulation_dgp:
  DGP:
    - Sample latent cell states z_i ~ N(0, I_k) on a 2D manifold; build ground-truth cell graph.
    - Generate true counts y*_ig ~ NB(mean = exp(z_i · B_:g), dispersion = φ_g).
    - Generate mask M_ig ~ Bernoulli(1 − sigmoid(α + β·y*_ig)); zero out X where M = 0.
  Regimes:
    - Null: set y*_ig = 0 at a subset of positions (true signal absent) → method must NOT hallucinate
      non-zero counts; report false-imputation rate.
    - Adversarial: sweep β ∈ [0, −2] (MCAR → strong MNAR) to drive the failure boundary; also sweep
      n_detected_genes ∈ {100, 500, 2000} to drive the graph-collapse boundary.
    - Oracle upper bound: give the method the true M and a noiseless y* at observed entries — best
      achievable recovery.
    - Trivial lower bound: global-mean imputation and copy-observed (no imputation).
  Sweep: β (dropout coupling), λ (smoothness weight), n_detected (sparsity); plot recovery RMSE vs β
  to locate the exact break point.
benchmark_protocol:
  Competitors (same preprocessing, same held-out mask, same compute budget):
    - Naive: all-zero imputation, global-mean imputation, kNN-mean imputation, copy-observed.
    - SOTA: scVI (deep generative), MAGIC (graph diffusion), SAVER (denoising), DCA (ZINB AE).
    - Same code/version pinned; same 80/20 observed/masked split per cell; no test-set leakage
      (mask sampled independently of expression magnitude — checked by a leakage test).
  Metrics: RMSE on held-out counts, Pearson on held-out entries, false-imputation rate in null regime,
    downstream-cluster ARI recovery, runtime, peak memory.
  Fairness: identical mask generation, identical dispersion pre-fit, compute-matched (cap wall-clock).
novelty_or_utility_basis:
  Utility first, novelty explicit.
  Novelty locus: a new inference mechanism for this estimand — graph-frequency selection as the
    smoothing operator, with a jointly-fit logistic dropout model, rather than averaging/diffusion
    (MAGIC) or a deep generative prior (scVI). The estimand (true count at dropout) and the objective
    (NB likelihood + graph smoothness) are shared with prior work; the novelty is the solver + the
    joint dropout coupling, and the identifiability analysis that prior imputation methods omit.
  Tier: T2 — defensibly better on ≥1 axis (transparent failure boundary under MNAR + lower compute
    than scVI) under a fair benchmark that includes naive baselines. NOT claimed as T1 structural
    novelty: it is a rigorous combination of graph signal processing + NB likelihood + logistic
    dropout, not a new estimand or a new objective.
  Delta vs named top_competitors:
    - vs MAGIC: MAGIC diffuses unconditionally; we condition on the dropout model and expose the MNAR
      failure; MAGIC does not report an identifiability boundary.
    - vs scVI: scVI amortizes a deep prior; we use a closed-form graph-frequency step → cheaper and
      interpretable, at the cost of expressivity (a T2 trade-off, not a T1 win).
```
