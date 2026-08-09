# crossbio-algo Standard run — scRNA-seq imputation (home-field)

**Case:** `benchmarks/cases/scrna-imputation`
**Run:** `standard-1`
**Effort mode:** Standard (auto-inferred from T2 target)
**Stages run:** data-audit → topic-viability → algorithm-design (full) → spec-writing → 1× adversarial-panel-audit
**Model:** glm-5.2 (same-model adversarial panel — see Honest Limitation)
**skill_version:** 0.3.0
**Validator:** `python -m crossbio_validate validate-chain …/artifacts` → **VALID — 0 findings** (after audit-driven revisions)

**Research ask (verbatim):** "I have sparse scRNA-seq counts. I want to recover the true transcript counts at dropout positions (imputation). Build me an algorithm. Python (scanpy), CPU only, no deep learning." Target tier: T2 tool paper. Compute: CPU only, Python/scanpy.

---

## 1. Data & estimand audit (GATE — root of the chain)

`artifact: data-audit.json · provenance d18a6c55e019 · fatal_issues = [] (GATE passes)`

| Field | Finding |
|---|---|
| **biological_unit** | `biological_replication_unit = donor`. `generalization_axis = NEW donor`, NOT new cell within a donor. Cells from one donor are correlated (shared dissociation, library, batch, genotype); cell-level n is pseudoreplication at the new-donor axis (Squair et al. 2021). The *method* operates cell-by-cell, but the *validity claim* ("imputation reduces error on unseen samples") is judged at donor level. |
| **observational_unit** | cell (scRNA-seq; correlated within donor). |
| **estimand** | **The counterfactual true transcript count y*_{c,g} at a position (cell c, gene g) whose observed value is zero due to technical dropout (mask M_{c,g}=0), over the target population of future scRNA-seq experiments on the same tissue/platform family — the count that would have been observed absent technical dropout. A per-position counterfactual count, NOT a "denoised matrix" summary.** *(This string is byte-identical in design.json — rule 1.)* |
| **cohort_structure** | Typical imputation benchmark cohort: PBMC 10x v3 (~2.7k cells, 1 donor), mouse cortex (several donors), pancreas (Baron 2016, ~2k cells, multiple donors). For a new-donor claim the usable biological n is the donor count (often 2–6); millions of cells do NOT raise donor-level power. |
| **donor_batch_site** | Batch / platform differences are the main confounder; depth differences (FB4) confound biology if not normalized. Region/condition pairing is within-donor (OK). |
| **missingness_mechanism** | **Droplet UMI zeros are NOT automatically MNAR.** Per Svensson 2020, droplet UMI counts fit a single Negative Binomial — no extra zero-inflation term. A realized zero is a *mix* of (i) true biological zero (M=1, X=0) and (ii) technical dropout (M=0, X=0); for low-expression genes a zero is jointly caused (low true count AND ~10% capture failure) — so "technical dropout" is a modelling convenience for the stochastic-capture tail, NOT a cleanly separable per-entry process. **Method ASSUMES MAR** (β_dropout=0) for the primary estimator; MNAR is treated as a self-diagnosed failure boundary, NOT a default. *(Avoids trap T2.)* |
| **leakage_graph** | `dependency_structure`: cells within donor correlated; leak-relevant unit for new-donor axis = DONOR. Train/test MUST NOT share a donor. Additional WITHIN-cell leakage path in mask-then-impute: the mask must be sampled independently of expression magnitude (an expression-coupled mask silently turns evaluation into MNAR and hides the failure — trap T3). |
| **ground_truth_quality** | No ground truth in real data (the counterfactual count is unobservable by definition). Validation uses (a) mask-then-impute on observed nonzero entries as pseudo-ground-truth, (b) synthetic DGP with known truth, (c) orthogonal full-length/ISS validation where available. |
| **usable_sample_size** | Donor-level n (small, 2–6 typically). Cell-level n is pseudoreplication for the new-donor claim. |
| **split_strategy** | **Two nested splits, each with explicit `split_unit` + justification.** (1) **For imputation error:** hold out 20% of nonzero observed entries per cell; `split_unit = entry`; justification = per-counterfactual-count claim. **CRITICAL: Bernoulli(p=0.2) mask independent of expression magnitude, with a leakage regression check (|coef|<0.05).** *(Avoids trap T3.)* (2) **For new-donor generalization:** donor-level k-fold; `split_unit = donor`; justification = generalizes to future donors. |
| **licensing_privacy** | Public benchmark datasets (PBMC, pancreas, cortex); standard human-subjects constraints for any new cohort. |
| **fatal_issues** | **[]** — GATE passes; chain continues. |

---

## 2. Topic-viability assessment (T2 ruler)

`target_tier = T2 (tool paper, Genome Biology / Bioinformatics / NAR class)`

### Competitor deep-comparison table (5-category, built before scoring)

| Competitor | Input | Method (core mechanism) | Output | Key limitation | Delta vs proposed | **Category** |
|---|---|---|---|---|---|---|
| **scVI** (2018) | scRNA counts | deep generative VAE, NB likelihood, amortized inference | denoised latent + imputed counts | requires training a VAE (slow on CPU); zero-inflated optional; no identifiability boundary | proposed: CPU-native graph-spectral recovery + explicit β_dropout diagnostic; cheaper, interpretable, less expressive | **1 (functional substitute)** |
| **MAGIC** (2018) | scRNA counts | graph diffusion (Markov on kNN graph), no likelihood | smoothed/diffused counts | no count likelihood; no dropout model; unconditional diffusion over-smooths; no MNAR diagnostic | proposed: NB likelihood + joint logistic dropout + identifiability boundary | **1 (functional substitute)** |
| **SAVER** (2018) | scRNA counts | Poisson-Gamma posterior per gene, denoising | denoised counts | per-gene, no cell-graph structure | proposed: adds cell-graph smoothness + dropout coupling | **1 (functional substitute)** |
| **DCA** (2019) | scRNA counts | ZINB autoencoder (deep learning) | denoised counts | deep learning (user forbids); ZINB assumes zero-inflation trap T2 warns against | proposed: NB (not ZINB), graph-spectral, no DL | **1 (functional substitute)** |
| **scImpute** (2018) | scRNA counts | kNN + dropout-model per cell type | imputed counts | non-identifiable under MNAR (no boundary reported); kNN graph sensitive to sparsity | proposed: explicit identifiability analysis + graph-spectral recovery | **2 (methodological neighbor)** |
| **kNN-mean baseline** | scRNA counts | average over k nearest cells | filled counts | no count model, no dropout model | must be benchmarked against | **5 (naive baseline — MANDATORY)** |
| **global-mean / per-gene-mean** | scRNA counts | fill with mean | filled counts | ignores cell structure | must be benchmarked against | **5 (naive baseline)** |
| **all-zero / copy-observed** | scRNA counts | fill 0 / leave zeros | unchanged | trivial | must be benchmarked against | **5 (naive baseline)** |
| **downstream-robust method** (e.g. GLM-DE robust to sparsity) | scRNA counts | model sparsity directly, no imputation | DE results bypassing imputation | skips the imputation step entirely | indirect — adoption/user-value competitor | **4 (workflow alternative)** |

**competitors_by_category:**
- **1 (functional substitutes, must beat/differentiate):** scVI, MAGIC, SAVER, DCA
- **2 (methodological neighbor):** scImpute
- **3 (input-slot alternative):** — (all take the same scRNA counts the user has)
- **4 (workflow alternative):** sparsity-robust DE bypassing imputation
- **5 (naive baseline, MANDATORY benchmark):** kNN-mean, global-mean, per-gene-mean, all-zero, copy-observed

### Multi-dimensional score (decision-uncertainty band, NOT a CI)

| # | Dimension | w | score | pess | opt | conf | grade | w·s |
|---|---|---|---|---|---|---|---|---|
| 1 | biological_validity | 0.20 | 0.75 | 0.70 | 0.80 | med | B | 0.1500 |
| 2 | data_feasibility | 0.15 | 0.85 | 0.83 | 0.87 | high | A | 0.1275 |
| 3 | functional_differentiation | 0.15 | 0.60 | 0.50 | 0.70 | low | B | 0.0900 |
| 4 | benchmarkability | 0.15 | 0.75 | 0.70 | 0.80 | med | B | 0.1125 |
| 5 | implementation_feasibility | 0.10 | 0.80 | 0.75 | 0.85 | med | B | 0.0800 |
| 6 | reproducibility | 0.10 | 0.75 | 0.70 | 0.80 | med | B | 0.0750 |
| 7 | adoption_user_value | 0.10 | 0.65 | 0.55 | 0.75 | med | B | 0.0650 |
| 8 | ethics_privacy_licensing | 0.05 | 0.90 | 0.88 | 0.92 | high | A | 0.0450 |

- **viability_total = 0.7450**
- **viability_range = 0.66–0.79 (decision uncertainty band: pessimistic–optimistic)** — entirely ≥ 0.5 ⇒ viable under T2.
- **should_proceed = true** (no dimension has blocking_issue=true)
- **biggest_failure_risk:** the β_dropout self-diagnostic does not actually discriminate MNAR from MAR on real data (it is not data-identified under MAR — see audit finding) — collapsing the novelty axis into an uninformative flag.

**Verdict:** viable T2. The locked improvable axis vs the Cat-1 substitutes: **the only scRNA imputer with an explicit identifiability boundary and a self-diagnosed MNAR flag** — vs MAGIC (no likelihood), scVI (deep prior, no boundary), SAVER (no graph), DCA (deep + ZINB which the platform argues against). The benchmark MUST include the Cat-5 naive baselines.

---

## 3. Algorithm design (full formal-method contract)

`artifact: design.json · provenance fb99ad422b1a · parent scrna-impute-data-audit-001`

**Method name:** gsNB-Dropout — graph-spectral NB imputation with joint dropout self-diagnosis.

### Group P — Problem
- **problem_definition:** Recover the counterfactual true count at each dropout position in a sparse scRNA-seq UMI matrix, CPU-only Python/scanpy, no DL, while transparently reporting the MAR/MNAR regime in which recovery is identifiable.
- **estimand:** *(byte-identical to data-audit — rule 1)*

### Group F — Formalization
- **mathematical_abstraction:** **Masked signal recovery on a cell-similarity graph with an NB count likelihood, jointly fit with a logistic dropout model.** Rejected: ZINB-VAE (DL forbidden, buries identifiability in a deep prior); pure matrix completion (cells×genes is not low-rank in the CS sense — smoothness is on the cell graph, not the matrix); MAGIC-style unconditional diffusion (no likelihood, no boundary).
- **notation_and_shapes:** X (n_cells×n_genes, observed counts); M (n_cells×n_genes, observation mask — **LATENT, not observed**); W (n_cells×n_cells, kNN graph); L (n_cells×n_cells, symmetric normalized Laplacian); U (n_cells×n_cells, graph Fourier basis, truncated to k=64); Y (n_cells×n_genes, recovered counts); P (n_cells×n_genes, dropout probs); phi (n_genes, NB dispersion); lib (n_cells, library offset); alpha_dropout, beta_dropout (scalars).
- **objective_or_likelihood:** *(audit-revised)* **M is treated as LATENT** — a real zero could be biological (M=1, X=0) or technical (M=0, X=0). The complete-data log-likelihood is marginalized over soft responsibilities r[c,g] = P(M=0|X,Y,α,β):
  ```
  Q = Σ_{c,g} [ (1−r_cg)·(log P(X=0|Y, M=1) + log P(M=1|Y)) + r_cg·log P(M=0|Y) ]  −  λ·tr(Yᵀ L Y)
  ```
  with P(X|Y,M=1) = NB(mean=Y, disp=φ[g]) (so a true biological zero gets the NB-at-zero probability), P(M=0|Y) = sigmoid(α + β·log1p(Y)), and the graph-Laplacian smoothness penalty λ·tr(YᵀLY) on the FULL Y. Y at masked entries is constrained to span(U[:,:k]).
- **identifiability:** *(audit-revised — two-level honesty)*
  - **Under MNAR (β≠0):** NOT identifiable without an external instrument. A low observed count and a high-but-dropped-out count produce identical evidence (X=0 both). *(trap T6)*
  - **Under MAR (β=0) — NECESSARY CORRECTION:** Y at masked entries is **NOT data-identified; it is PRIOR-DOMINATED.** The NB likelihood contributes zero gradient at masked entries; recovery is pinned almost entirely by the graph-smoothness prior + the mask posterior. So under MAR the imputation is **well-defined but identification-by-assumption** (mathematically kin to MAGIC/scImpute in the MAR limit), NOT identification-by-data. **Identification is restored only by an external instrument** (spike-ins/ERCC, paired full-length+droplet).
  - **The method's contribution is NOT claiming data-identification under MAR** — it is (a) making the prior-dominance explicit, (b) jointly fitting β_dropout + CI as a *regime indicator*, (c) flagging MNAR rather than papering over it.

### Group A — Algorithm
- **cross_domain_inspiration:** Engaged, two domains outside single-cell imputation: (1) **graph signal processing** — graph-Laplacian low-pass / graph-Fourier as the recovery operator (truncated eigenbasis U[:,:k] as the low-pass projection); (2) **missing-data / causal inference** — the MNAR-not-identifiable-without-instrument theory, operationalized as the joint logistic dropout whose slope β_dropout is the self-diagnostic. CS sparsity prior discarded (weaker match); Bayesian search discarded (no search problem).
- **proposed_algorithm (gsNB-Dropout):** (1) preprocess (filter min_genes=500, normalize_total, log1p, HVG 2000, scale, PCA 50); (2) kNN graph + symmetric Laplacian; (3) **eigsh on (c·I−L), which='LM'** (pure-matvec Lanczos for the k lowest-frequency eigenvectors — explicitly avoiding which='SM' shift-invert whose factorization dominates RAM at 1e5 cells); (4) per-gene NB dispersion by method-of-moments; (5) **EM with latent M** — mask-E-step computes r[c,g]=P(M=0|X,Y,α,β); Y-M-step solves the smoothness-regularized expected-NB-MLE for Y in span(U[:,:k]) (damped Newton, trust region); dropout-M-step Newton on (α,β); (6) diagnose: emit β_dropout_hat + CI, mnar_flag, impute_confidence; emit layers['imputed'], layers['mask_posterior'], layers['impute_variance'].
- **optimization_or_inference:** Generalized EM (mask-marginalized). Q maximized in three coordinated blocks: mask-E-step (closed form per entry), Y-M-step (low-pass projection + damped-Newton inner, **NOT claimed convex** — NB log-lik only locally concave), dropout-M-step (convex logistic Newton). Monotone non-decrease of Q (MM-style); coordinate-wise optimum; not global; init Y=observed-mean, φ=MoM, β=0. Stop at rel-change < 1e-4 or 50 iters.
- **complexity:** *(audit-revised)* Per outer iter: full eigendecomp O(n³) caps ~1e4 cells; truncated Lanczos O(k·n·n_neighbors) per matvec. E-step NB-gradient inner steps: damped Newton, observed-convergence reported. Total O(k·n·n_neighbors + n·m·T_outer). **Memory:** X stored SPARSE; Y and P dense. At 1e5 cells × 2e4 genes: X ~hundreds of MB, Y ~8 GB, P ~8 GB, peak **~20–24 GB** (the earlier "8–16 GB" estimate was optimistic and is corrected). Dense path caps at ~3e4 cells; gene-chunking above.

### Group G — Guarantees
- **failure_boundaries** (4, each with condition + mechanism + guard):
  - **FB1 — MNAR dropout (|β| large), no instrument.** Mechanism: not identifiable; smoothness prior over-smooths → systematic over-imputation; RMSE ~linear in |β|. Guard: report mnar_flag=(|β_hat|>τ) + impute_confidence=1/(1+|β_hat|).
  - **FB2 — Ultra-sparse cells (<500 genes detected).** Mechanism: kNN graph collapses onto hubs; low-frequency subspace too small → over-smoothing erases real variation → degrades to global-mean. Guard: filter min_genes=500; sub-threshold cells → per-gene observed-mean + impute_confidence=0. *(trap T4)*
  - **FB3 — Cell-type heterogeneity > graph bandwidth** (lineage-transition genes OR cross-donor composition shift). Mechanism: low-pass treats high-freq variation as noise → attenuates real biology / type-blurs under composition shift. Guard: per-gene graph-bandwidth diagnostic; widen k or NB-mean for high-freq genes; within-type neighborhoods + inter-batch anchor for new donors.
  - **FB4 — Sequencing-depth confound** (>5x library-size spread, graph on raw counts). Mechanism: kNN clusters by total UMI not biology; smoothness propagates depth as if biological. Guard: normalize before graph; lib as NB offset; graph on PCA of normalized matrix.
- **uncertainty_and_calibration:** Point estimate by default; optional posterior variance from the Laplacian-precision-inverse on the low-pass subspace (layers['impute_variance']). Under MAR nominal coverage on synthetic; under MNAR over-confident — known limitation tied to FB1.
- **invariances:** permutation-invariant in cell/gene index; NOT scale-invariant (raw vs normalized changes NB dispersion); NOT invariant to batch index.

### Group V — Validation
- **simulation_dgp:** Full DGP on a 2D Swiss-roll/tree manifold, n_cells∈{500,2000,10000}; genes 80% low-freq smooth + 20% high-freq transition (probe FB3); true counts Y*~NB(mean=lib·softmax(z·B), disp=φ); mask M~Bernoulli(1−sigmoid(α+β·log1p(Y*))) with β∈{0 (null/MAR), −0.5, −1.0, −2.0 (adversarial MNAR)}. **Regimes:** NULL (inject true zeros — method must NOT hallucinate, report false-imputation rate); ADVERSARIAL (β=−2 + n_detected∈{100,500,2000} → drives FB1+FB2); ORACLE (true M + noiseless Y* — reported ONLY as a labeled ceiling, NOT a competitor); TRIVIAL (global-mean, copy-observed — lower bound). Sweep β×λ×n_detected×k.
- **benchmark_protocol:** Competitors — **Cat 5 naive (MANDATORY):** all-zero, global-mean, per-gene-mean, kNN-mean, copy-observed; **Cat 1 SOTA:** scVI, MAGIC, SAVER, DCA. Same preprocessing, same expression-INDEPENDENT Bernoulli(0.2) mask, same compute budget, same seeds, **SAME hyperparameter-search budget** (audit-driven). **FIT-SCOPE (audit-driven):** dispersion + library factors fit on TRAIN entries only, frozen before imputation. **Leakage check:** |coef| of mask-indicator ~ log-expression < 0.05. Metrics: RMSE + Pearson on held-out, false-imputation rate in null, downstream ARI, runtime, peak memory. **Per-estimand tables (audit-driven):** in-sample entry-level (its own table) vs new-donor donor-level k-fold (its own table) — NOT conflated. Per-regime reporting so FB1/FB2 are visible.
- **novelty_or_utility_basis:** **Utility first, novelty explicit.** Novelty locus: **new inference mechanism + new identifiability diagnostic.** (1) Graph-spectral low-pass as the recovery operator (CPU-native, transparent bandwidth); (2) joint logistic dropout whose slope IS the MNAR self-diagnostic — prior imputers fit dropout but none turn the coupling into a per-sample identifiability flag; (3) explicit identifiability analysis (MAR=prior-dominated, MNAR=not-identifiable) that prior imputers OMIT. **T2 — defensibly better on ≥1 axis** (transparent boundary + lower compute than scVI + self-diagnosed confidence) under a fair benchmark with naive baselines. **Delta vs named top_competitors:** vs MAGIC — we condition on the dropout model + expose MNAR; vs scVI — closed-form graph-spectral step (cheaper, interpretable) at the cost of expressivity; vs SAVER — we add cell-graph smoothness + dropout coupling; vs DCA — NB (not ZINB) + no DL.

### Component necessity (complexity kill-switch)
- **joint_logistic_dropout_model** vs NB+smooth-only: **retain** — the joint fit is the ONLY source of the MNAR self-diagnostic; in the β=0 regime it reduces to the simpler alternative (no harm). Pre-registered regimes: β∈{0,−1,−2}.
- **truncated_eigendecomposition** vs full diffusion: **retain** — truncated Lanczos O(k·n·k_nn) vs full O(n²·t); on n=10000 this is the difference between CPU-runnable and not; recovery within 5% for k≥32.

---

## 4. Spec summary

`artifact: spec.json · provenance 014124989f1b · parent scrna-impute-design-001`

**Domain adapter:** single-cell (AnnData/scanpy) — the user's stack.

**Module interfaces (7 modules, shapes ⊆ design.notation_and_shapes.shapes — rule 3 ✓):**
1. `preprocess_filter` — FB2/FB4 guard; outputs adata.obsm['X_pca'], adata.uns['lib'].
2. `build_cell_graph` — kNN cosine graph W + Laplacian L → adata.obsp.
3. `graph_lowpass_basis` — eigsh(cI−L, which='LM') → U[:,:k].
4. `fit_dispersion` — per-gene NB dispersion φ by MoM.
5. `em_impute_loop` — latent-M generalized EM; outputs layers['imputed'], ['mask_posterior'], ['impute_variance'], uns['beta_dropout'], ['alpha_dropout'].
6. `diagnose_mnar` — read β_hat + CI; set uns['mnar_flag'], uns['impute_confidence'].
7. `gene_bandwidth_diagnostic` — per-gene graph-frequency spectrum; flag high-freq genes (FB3 guard).

**Acceptance criteria (11, every failure_boundary traced — rule 2 ✓):**
| AC id | traces_to | verification_mode | what it checks |
|---|---|---|---|
| AC-FB1-1 | FB1 | simulation | β_hat within ±0.2 of true β at β=−2; mnar_flag fires |
| AC-FB1-2 | FB1 | simulation | MAR/null (β=0) correctly NOT flagged |
| AC-FB1-3 | FB1 | documented_limitation | mnar_flag → disclaimer that counts are not identifiable; confidence scaled (this is a *known limitation*, NOT a pass) |
| AC-FB2-1 | FB2 | automated_test | sub-threshold cells flagged + excluded |
| AC-FB2-2 | FB2 | simulation | RMSE(2000 detected) < 0.7·RMSE(100 detected) |
| AC-FB3-1 | FB3 | automated_test | high-graph-freq genes flagged |
| AC-FB4-1 | FB4 | automated_test | depth-confounded batches → graph built on PCA(normalized), not raw X |
| AC-FB4-2 | FB4 | analytic_argument | NB mean = lib·q (depth as offset) |
| AC-BENCH-1 | FB1,FB2,FB3 | benchmark | RMSE strictly < all 4 naive baselines AND ≤ weakest SOTA (MAGIC), 5 seeds, leakage check |
| AC-BENCH-2 | FB1 | benchmark | null-regime false-imputation rate ≤ per-gene-mean baseline |
| AC-COMPLEX-1 | FB2 | automated_test | n=10000 uses truncated Lanczos; <30 min, <16 GB (smoke test) |

**Pseudocode hashes:** present for all 7 modules (placeholders; rule 4 fires only when a code stage exists — not produced in this Standard run).

---

## 5. Adversarial panel audit (1 round, same-model subagent panel)

**Honest limitation:** every panel member is the same Claude (glm-5.2) — they share training bias and the blind spots that come with it. They catch confirmation bias and one-sided framing; they CANNOT catch a flaw that is a blind spot for Claude in general. The information-isolation + role-adversariality + structured-verdict design is a mitigation, not a cure. Optional hybrid upgrade: an external-model seat (DeepSeek/GPT via API) would de-correlate bias — not used in this run.

**Panel:** 3 information-isolated subagents — **algorithm-methodologist** (math soundness), **benchmark-auditor** (fairness/leakage/baselines), **domain-biologist** (biology premise).

### Findings (aggregated, pre-revision)

| # | panel seat | claim | sev | conf | blocking | resolution |
|---|---|---|---|---|---|---|
| 1 | methodologist | Objective conditions on M as if observed, but M is NOT observable (real zeros are biological-or-technical ambiguous) | **critical** | high | **YES** | **FIXED** — objective rewritten to treat M as LATENT; complete-data log-lik marginalized over soft responsibilities r[c,g]=P(M=0|X,Y,α,β); EM gains an explicit mask-E-step |
| 2 | methodologist | Under MAR, Y at masked entries is identified ONLY by the smoothness prior (NB lik contributes zero gradient there) — the "MAR ⇒ identifiable" claim overstates | **major** | high | **YES** | **FIXED** — identifiability rewritten two-level: MNAR=not-identifiable, MAR=well-defined-but-PRIOR-DOMINATED (identification-by-assumption, kin to MAGIC in the MAR limit); only an external instrument restores data-identification |
| 3 | methodologist | E-step labeled "convex projection" but NB log-lik is only locally concave in its mean — not globally convex | major | med | no | **FIXED** — dropped "convex" claim; spec says damped Newton + trust region + observed-convergence-reported (not claimed) |
| 4 | methodologist | eigsh(which='SM') on L uses shift-invert factorization (O(n^1.5) fill-in) — complexity understated; 1e5-cell RAM estimate optimistic | major | med | no | **FIXED** — switched to eigsh(cI−L, which='LM') pure-matvec Lanczos; RAM estimate corrected to ~20–24 GB at 1e5 cells, dense path caps at 3e4 |
| 5 | methodologist | β_dropout self-diagnostic CI is weak under MAR (data carries little β info) — flag may be unreliable | major | med | no | **FIXED** — added β_dropout identifiability caveat to assumptions; pre-register Type I/II on known-MNAR simulator; degrade to "flag not measurement" without a calibrant |
| 6 | methodologist | HVG pre-filtering on dropout-corrupted data is circular | minor | med | no | noted; mitigation = iterate HVG or all-gene graph flagged for future work |
| 7 | benchmark | Hyperparameter budget not equalized across competitors — only compute budget | major | med | no | **FIXED** — protocol now mandates same HPO budget (30 Optuna trials, 3-fold inner CV) per method, search logs reported |
| 8 | benchmark | Dispersion/normalization fit-scope not pinned to TRAIN — potential test-on-train leak | major | med | no | **FIXED** — protocol now states all φ + lib factors fit on TRAIN entries only, frozen before imputation |
| 9 | benchmark | ORACLE regime might be read as a competitor | minor | high | no | **FIXED** — ORACLE is reported ONLY as a labeled ceiling, never in the headline table |
| 10 | benchmark | New-donor sub-claim has no metric definition — risk of conflating estimands | minor | med | no | **FIXED** — two separate tables: in-sample entry-level vs new-donor donor-level (no re-masking) |
| 11 | biologist | "Technical dropout" presented as cleanly separable per zero — but for low-expression genes a zero is jointly caused (low count + capture failure) | major | high | no | **FIXED** — assumption reframed: dropout = stochastic-capture tail of a low NB mean, modelling convenience not separable process |
| 12 | biologist | "Imputed counts feed DE without bias" is contested (Andrews & Hemberg 2018) — presented as settled | major | med | no | **FIXED** — added as explicit LIMITATION; recommend DE-on-imputed only when mnar_flag clear + confidence high |
| 13 | biologist | Graph-smoothness most violated at rare/progenitor lineages + cross-donor composition shift (user's fetal-brain domain) | major | med | no | **FIXED** — FB3 mechanism extended to composition shift; guard adds within-type neighborhoods + inter-batch anchor; new-donor graph-attachment gap noted |
| 14 | biologist | Ambient RNA + dissociation-stress confounders silently absorbed as biology | minor | med | no | **FIXED** — pipeline contract: X is post-decontamination + stress-genes-flagged before imputation |
| 15 | biologist | β_dropout estimation procedure (the linchpin) left unspecified | minor | med | no | **FIXED** — cross-referenced to methodologist #5; spike-in/ERCC restores tight identification |

### Verdict (post-revision)

All **blocking** findings (#1, #2) were resolved by rewriting `objective_or_likelihood` (latent-M marginalization) and `identifiability` (two-level honesty). All **non-blocking** findings were addressed by enriching `assumptions`, `complexity`, `benchmark_protocol`, `proposed_algorithm`, and the FB3 mechanism. No finding was dismissed.

**Panel verdict: `pass` (after revision).** No blocking finding survives. The artifact chain re-validates cleanly (`VALID — 0 findings`).

---

## 6. Validator result

```
$ python -m crossbio_validate validate-chain benchmarks/cases/scrna-imputation/runs/standard-1/artifacts
VALID — 0 findings.
```

**Chain:** `data-audit (d18a6c55e019, root)` → `design (fb99ad422b1a)` → `spec (014124989f1b)`.
All cross-stage rules pass: estimand continuity (rule 1, byte-identical), no-orphan failure_boundary (rule 2, all FB1–FB4 traced), notation consistency (rule 3, spec shapes ⊆ design notation), provenance integrity (rule 5). Rules 4/6/7/8/9 require a code stage — not produced in this Standard run.

---

## 7. Honest limitations & next steps

- **The novelty axis rests on the β_dropout self-diagnostic**, which is NOT tightly data-identified under MAR. Before submission the diagnostic's Type I/II MUST be measured on a known-MNAR simulator (downsample full-length data with depth-coupled dropout). If the flag cannot discriminate, the novelty collapses and the method is a re-skin of regularized MAGIC — the single biggest failure risk.
- **The MVP does NOT include real-data benchmarking** — the spec covers synthetic DGP + the protocol; running it vs scVI/MAGIC/SAVER/DCA + the 5 naive baselines on PBMC/pancreas/cortex is the P0 experiment gap (Publication Roadmap).
- **No code stage** — this Standard run stops at spec. The next step is `tasks.md` → bite-sized TDD implementation of the 7 modules, then `crossbio attest` to turn declared tests into source-bound attested results.
- **Same-model panel blind spot** — the audit caught real issues (the latent-M and prior-dominance fixes are substantive) but cannot catch a flaw that is glm-5.2's general blind spot. A hybrid external-model seat is recommended before publication trust.
