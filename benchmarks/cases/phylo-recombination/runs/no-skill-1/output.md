# Recombination Detection Algorithm Design — Viral Mosaic & Breakpoint Inference (CPU, Python/BioPython)

## 1. The Precise Problem

### 1.1 What the user has
- An alignment of ~5,000 viral genomes (a fast-evolving RNA virus, e.g. SARS-CoV-2 or HIV), produced by BioPython (`AlignIO`). Length `L` is on the order of 10^3–3×10^4 bp. Nucleotide, almost certainly with gaps (Ns and `-`), and with strong rate/strand heterogeneity.
- CPU only. No GPU. Python stack (BioPython, NumPy/SciPy).
- They want two outputs per genome:
  1. **Is this genome a mosaic (recombinant)?** — a binary classification plus a confidence.
  2. **Where are the breakpoints?** — coordinates (1-based or alignment-relative) of each crossover.

### 1.2 Formal statement

Given a multiple sequence alignment `A` of `N=5000` rows and `L` columns, partition the genomes into three conceptual roles per detected event:
- a **query** (potentially recombinant) genome `q`,
- a set of **parental candidates** `P` (the donor lineages, not necessarily sampled),
- a **background** `B` (the rest of the population, used to estimate the substitution model and the tree).

A genome `q` is **mosaic** if, along its sequence, the most likely ancestry changes at least once: there exist positions `1 = b_0 < b_1 < ... < b_k < b_{k+1} = L` and parental assignments `p_1, ..., p_{k+1}` with at least two *distinct* parental clusters, such that the likelihood of `q`'s columns under the segment-wise assignment `(p_i, b_{i-1}..b_i)` is substantially higher than under a single-parent assignment. Each `b_i` (i=1..k) is a **breakpoint**.

This is fundamentally a **model-selection problem on a sequence with a changepoint process**, not a tree-building problem. The tree is only an instrument for computing per-site likelihoods.

### 1.3 What "recombination" actually means here, and what it does NOT
- We are detecting **historical homologous recombination** leaving a phylogenetic mosaic signal. We are *not* detecting in vitro contamination, chimeric assemblies, or superinfection of a single sample — though all of those produce similar signals and we must explicitly guard against them (Section 6).
- We are detecting **signal in the alignment**, which is a function of *sampling density*. If the true parents are unsampled, "which parents" must be answered at the level of **clades/lineages** inferred from the background, not as named sequences.

### 1.4 Why this is hard (the failure modes that drive the design)
1. **Rate heterogeneity + sparse sampling destroys distance-based methods.** Pairwise distances between a query and a putative parent drift along the genome just from local rate variation, producing false breakpoints.
2. **Tree-likelihood per window is O(N) expensive and the window choice itself biases breakpoint resolution.** Sliding a fixed window produces blurry breakpoints and biases toward window-sized events.
3. **Homoplasmy mimics recombination.** A convergent substitution at a few sites in two unrelated clades looks identical to a small recombinant tract.
4. **Breakpoint locations are correlated with the prior on the number of breakpoints.** Naive greedy splitting over-segments.

The design below addresses each explicitly.

---

## 2. Method / Approach

A three-stage pipeline. Stage A builds the comparative information (clusters, distances, substitution model). Stage B scans each genome for candidate breakpoints. Stage C does model-based refinement and a global significance test. The whole pipeline is **pairwise-then-refine**: cheap screening first, expensive likelihood only on candidates.

### 2.0 Notation and preprocessing

- `A`: alignment, `N × L`. `A[i,j] ∈ {A,C,G,T,-,N}`.
- Drop columns that are all-gap or >50% ambiguous. Track kept columns so breakpoints can be reported in original coordinates.
- **Mask problematic regions *after* recording them, not before**: known problematic / low-complexity / homopolymeric regions (e.g. for SARS-CoV-2: ends of the genome, known repetitive stretches) should be flagged. Recombination calls inside flagged regions are reported but marked low-confidence.
- Estimate a substitution model once: **GTR + Γ₄** via maximum likelihood on a fixed reference tree (Stage A.3). For HIV, optionally HKY85 to save time. We do not re-fit per window; we re-use the rate matrix and only re-fit branch lengths locally.
- Codon-position-aware: for viruses with coding regions (SARS-CoV-2 is ~entirely coding), partition sites by codon position 1/2/3 and (optionally) by annotated ORF. This matters because position-3 sites saturate and will produce spurious long-branch attraction if pooled with positions 1/2.

### 2.1 Stage A — Population scaffolding (run once)

**A.1 Genetic clustering (cheap parental hypotheses).**
Construct a quick distance matrix using **number of differences on the masked alignment** (`np.eight`-encoded by `skbio` or a hand-rolled NumPy Hamming), cluster with **average-linkage hierarchical clustering** (`scipy.cluster.hierarchy`) at a threshold chosen so that the largest within-cluster Hamming distance is ~0.5–1% for SARS-CoV-2 or ~2–3% for HIV. The clusters are *parental candidates*. With N=5000 this is feasible: the full pairwise matrix is 5000² × 8 bytes ≈ 200 MB and can be computed in a single vectorized pass per row block.

If memory is tight, use a sparse proxy: take 5000 random informative columns, compute distances on those, cluster, and use the full columns only in Stage C.

**A.2 A reference tree (for ordering clades and branch lengths).**
Build an approximate ML tree with **FastTree-style**Neighbor-joining + ML refinement — but since we are CPU/Python only and BioPython has no NJ-with-ML, we implement NJ on the Juke–Cantor- or GTR-corrected distance matrix (Saitou–Nei, `scipy` has nothing built in but NJ is ~60 lines of NumPy), then do a single round of NNI branch-length optimization under GTR+Γ. We do *not* need a perfect tree — we need branch lengths good enough to make per-site likelihoods meaningful.

**A.3 Substitution model fit.**
On the reference tree, fit GTR (6 rates) + Γ₄ (shape α) + invariant-sites fraction `p_inv` by maximizing the likelihood (Newton–Raphson on the rates; line search on α). This is one slow CPU operation that we do *once*. Re-used in every Stage-C likelihood evaluation.

**A.4 Lineage labels.**
For each cluster ≥ some minimum size (e.g. 5), label it a **putative lineage**. Singletons become "unassigned". The set of lineage labels `{L_1, ..., L_m}` is the vocabulary of parental assignments the algorithm can output.

### 2.2 Stage B — Screening: where could breakpoints be?

For each query genome `q` we want a list of candidate intervals cheaply. Two complementary scans, then intersect their surprises.

**B.1 Running-parent scan (the workhorse).**

Pick a small set `K_q` of "kin" genomes for `q` — the 50 nearest neighbors by full-genome Hamming distance. For each genome `k ∈ K_q` compute the **column-wise agreement vector** `agree_{q,k}[j] = 1{A[q,j] == A[k,j]}`. Sum across `K_q` to get `S[j] = Σ_{k∈K_q} agree_{q,k}[j]`, a per-column "similarity to nearest neighbors" score in `[0, |K_q|]`.

Smooth `S` with a small median filter (window ~11 bp, edge-preserving). The intuition: in a non-recombinant, `S[j]` is roughly constant (high) across the whole genome. In a mosaic with a single introgressed tract `[b_1, b_2]` from a lineage outside `K_q`, `S` *drops* inside `[b_1, b_2]`.

Apply a **changepoint detector** to `S`: a CUSUM / E-Divisive (Matteson–James, `ecp`-style, re-implemented in NumPy) or, more cheaply, a Bayesian-blocks partition (`scipy`-free, ~40 lines). The detected segments are candidate parental tracts.

Per segment, assign a provisional parent: among all *other* clusters (not the one `q` mostly resembles), find the cluster whose consensus matches the segment best. If no cluster matches better than `q`'s own cluster, that segment is *not* introgressed — it is just noise.

This scan is O(N · |K_q| · L) ≈ 5000 · 50 · 3×10⁴ ≈ 7.5×10⁹ bit-ops — vectorizable with NumPy and parallelizable with `multiprocessing.Pool`. A few minutes on a multi-core CPU.

**B.2 Compatibility / partition-distance scan (the corroborator).**

For informative (bi-allelic) columns partition the alignment into windows of fixed width `w ≈ 200–400 bp` (overlap 50%). In each window compute the **pairwise partition distance** between `q` and each cluster consensus. The parent-of-best-fit per window gives a string `parent(win_1), parent(win_2), ...`. A change in this string is a candidate breakpoint.

This is the classical *informative-site* signal used by RDP/bootscan; we keep it because it is robust to distance-scale errors that distort Stage B.1.

**B.3 Intersection.**
Candidate breakpoints are positions within ~`w` of a change in *both* B.1 (CUSUM segment boundary) and B.2 (parental-string change). This double-detection requirement suppresses rate-heterogeneity artifacts: B.1 is sensitive to local mutation rate; B.2 is sensitive to convergence; the intersection removes both because the two failure modes rarely coincide.

### 2.3 Stage C — Likelihood-based refinement and the final call

For each query that has at least one surviving candidate breakpoint, do a proper model-based evaluation.

**C.1 Single-parent vs. two-parent likelihood ratio.**

Fix the parental candidates discovered in B. For each ordered pair `(p_A, p_B)` of distinct lineages and each candidate breakpoint `b`, evaluate two likelihoods on the masked columns of `q`:

- **H0 (no recombination):** `q` descends from a single parent (the best of `{p_A, p_B, "outgroup"}`); compute `logL_0 = Σ_j log P(q[j] | tree_constrained_to_one_parent, GTR+Γ, branch lengths fit)`.
- **H1 (recombination at b):** columns `1..b` are constrained to descend from `p_A`, columns `b+1..L` from `p_B`; `logL_1(b) = logL_left(p_A, b) + logL_right(p_B, b)`.

The branch lengths in H1 are fit independently on each side; this is what gives H1 its power — the same overall branch length, partitioned, will not help unless the *pattern* of substitutions favors different parents on the two sides.

Use a **standard likelihood-ratio test with parametric bootstrap** for the p-value (the asymptotic χ² mixture is unreliable here because of the boundary at `b` and the non-identifiability under H0). For each `q`, simulate 100 datasets under H0 (using the fitted single-parent model), re-run the breakpoint scan, and record the max LRS. The p-value is the fraction of simulations whose max-LRS exceeds the observed. This is the part that makes the method trustworthy and the part that costs CPU time — see §5 for budget.

**C.2 Multiple breakpoints — a sequential procedure.**

To find `k` breakpoints, run a recursive binary segmentation:
1. Test the whole genome for *one* breakpoint via C.1.
2. If significant, fix it, then recurse on each side.
3. Stop when no further split is significant (with Bonferroni correction on the number of tested positions).

Do **not** fit a global `k`-breakpoint model jointly by EM: in 5000 genomes, the EM gets stuck in local optima and the per-genome compute is unbounded. Binary segmentation is conservative (slightly undercalls short internal tracts) but well-behaved.

**C.3 Breakpoint localization — a confidence interval.**

For each called breakpoint `b*`, define the **profile-likelihood CI** as the set `{b : 2(logL_1(b*) − logL_1(b)) < χ²_{1,0.95}}`. Report this CI alongside the point estimate. This is essential: a "breakpoint at position 12,345" is meaningless without a ±N window, and on real viral data N is often 50–500 bp because substitution density limits resolution.

**C.4 Output per genome.**
```
genome_id   is_recombinant   n_breakpoints  breakpoints (orig coords)   CI_width   parents            p_bootstrap   max_LRS
G_0042      True             2              [(4521, 4583),(18920,19010)]  60,90      L3→L7, L7→L3       0.01          84.3
G_0450      False            0              —                            —          —                  0.43          3.1
```

### 2.4 Putting the stages together — pseudocode

```
def detect_recombination(aln):
    aln_masked, kept_cols, flags = preprocess(aln)
    clusters, cluster_consensus = stage_A_cluster_and_tree(aln_masked)
    model = stage_A_fit_GTRGamma(aln_masked, ref_tree)

    results = []
    for q in genomes:
        kin = nearest_neighbors(q, aln_masked, k=50)
        segs_B1 = cusum_scan(q, kin)
        parent_string_B2 = window_parent_string(q, cluster_consensus)
        candidates = intersect(segs_B1, parent_string_B2)
        if not candidates: results.append(no_recomb(q)); continue
        bps, pvals, CIs = likelihood_refine(q, candidates, clusters, model,
                                            n_boot=100)
        results.append(RecombCall(q, bps, pvals, CIs))
    return results
```

---

## 3. Validation Plan

Validation has to attack three things independently: **detection** (is q a mosaic?), **localization** (where are the breakpoints?), and **parental assignment** (which lineages?). All three can be right or wrong independently.

### 3.1 Simulated data — the primary validation, because we know ground truth

Use a **known simulator** (the gold standard is `Seq-Gen` or `Pyvolve`/`ALF` for the tree, plus a custom recombination step) but, to remove simulator bias, generate two independent simulator families and check they agree:

- **Family 1 — coalescent + recombination network.** Use `msprime` to simulate a recombination network with recombination rate `ρ`, then `Seq-Gen` (GTR+Γ) to drop sequences down the network. Recombination breakpoints are exactly known.
- **Family 2 — empirical-tree mosaic.** Take the *real* reference tree from Stage A.2, pick two lineages `L_A, L_B`, choose a query tip, then synthesize a mosaic by concatenating columns from `L_A`'s tip and `L_B`'s tip at a chosen breakpoint. This tests the algorithm on the *exact* tree it will see in production, but the simulation is a concatenation so the only noise is real substitution noise.

For each family, sweep over the parameters that matter:
- Recombinant tract length: 200, 500, 1000, 2000, 5000 bp.
- Parental divergence: 0.5%, 1%, 2%, 5% (so we know the detectability frontier).
- Number of breakpoints: 1, 2, 3.
- Sample size: 1000, 5000, 10000.
- Rate heterogeneity: low (α=1) vs high (α=0.1).

**Metrics:**
- Detection: precision, recall, F1 at FDR = 0.05 (i.e., control p-values with Benjamini–Hochberg across the 5000 genomes). Plot a **power-vs-tract-length** curve stratified by parental divergence. This single figure is the headline validation result.
- Localization: for called breakpoints, the median absolute error `|b̂ − b_true|` and the **CI coverage** — does the 95% profile-likelihood CI contain the true breakpoint 95% of the time? If coverage is < 90%, the CIs are overconfident and we widen them.
- Parental assignment: for true recombinants, fraction where the assigned parent clade contains the true parent (or, when the true parent is unsampled, is its sister clade).

### 3.2 Realistic adversarial simulations

Specifically generate the *hard* cases and verify the algorithm fails gracefully:
- Pure clonal evolution with strong rate heterogeneity (no recombination) → false-positive rate should be ≤ 5%.
- Convergent substitutions injected at random sites in two clades → should *not* be called recombination if the convergent tracts are < ~100 bp.
- Tree uncertainty: shrink `N` so the reference tree is wrong → detection power should degrade smoothly, not collapse.

### 3.3 Real-data benchmarking against established tools

Compare against `RDP5`, `GARD` (HyPhy), `3SEQ`, `Bootscan` (RDP5 implementation), and `PhiPack` (pairwise compatibility + NSS + MaxChi²). On the same 5000-genome alignment:

- **Agreement matrix**: for each genome, do all tools agree on recombination status? Disagreement is informative, not failure — annotate cases where our method and GARD agree but Bootscan disagrees (often a short-tract case where window methods are known to be weak).
- **Breakpoint concordance**: among genomes called recombinant by ≥2 tools, are the breakpoints within ±200 bp of each other?
- **Runtime**: GARD on 5000 × 30000 is impractical (GARD is O(N² L) and times out); we expect to be 10–100× faster while having comparable power on simulated data. This runtime advantage is a real contribution, not a vanity metric, because the user is CPU-only.

### 3.4 Biological sanity checks on real data

- For SARS-CoV-2: there are **well-characterized recombinant lineages** (the "recombinant" Pango lineages such as XBB, XBD, CH.1.1, etc., curated by the Pango nomenclature committee). A strong external validation is: **does our method, run blind, recover the breakpoints catalogued for these known recombinants?** This is the cleanest real-data test.
- For HIV: within-host recombinant forms (CRFs) have annotated breakpoints; cross-check.
- Negative controls: a single strictly clonal lineage (e.g. a flu HA clade, or a lab-passaged SARS-CoV-2 lineage) should yield zero recombinants.

### 3.5 Internal consistency checks (during the run)

- **Bootstrap CI coverage on real data**: under H0 simulations fit *per query*, the H0-rejection rate at α=0.05 should be ~5% across all *non-recombinant-looking* queries. If it is 15%, the model is misspecified (probably branch lengths) and we re-fit.
- **Left–right symmetry**: re-run each query reverse-complemented; breakpoints should be at `L−b`. Sanity check on the implementation.

---

## 4. Key Assumptions

Stated explicitly so they can be checked.

1. **The alignment is correct and homologous.** Garbage in → garbage out. A bad alignment produces spurious breakpoints at misaligned columns. We assume the user has done a reasonable codon-aware alignment (MAFFT --auto or similar) and we will report low confidence near gappy regions.
2. **Substitution model is approximately GTR+Γ.** For RNA viruses this is standard; the only place it fails badly is hyper-mutated regions (e.g. APOBEC-edited HIV genomes), which we mask in §2.0.
3. **Recombination breakpoints are rare events.** We assume at most a handful per genome. If a genome has 30 breakpoints, it is more likely a hypermutable / dual-infection artifact than biology, and we flag rather than embrace it.
4. **Parents are sampled densely enough that the recombinant tract resembles *some* sampled lineage.** If the true parent is a totally unsampled clade, every method (ours included) will fail to assign a parent; we can still detect "this tract is anomalous" but not "from whom".
5. **No strong selection within the recombinant tract.** Strong convergent selection (immune escape in spike, drug resistance in HIV pol) can produce patterns indistinguishable from recombination. We assume selection is weak relative to neutral drift at the tract scale; this is a real and unavoidable confound.
6. **The alignment is dominated by one gene, or at most a few.** If multiple genes with very different rates are concatenated, the per-segment model may need a partition per gene. We support partitions (§2.0) but assume the user annotates them.
7. **CPU budget is generous but finite.** We assume on the order of 10²–10³ CPU-hours is acceptable (a 16-core node for a day or two). The parametric bootstrap is the cost driver; §5 explains how to trade it off against rigor.

---

## 5. Compute / Engineering Notes

- **Vectorization.** All Stage-A and Stage-B operations on the alignment are NumPy-wide. Encode the alignment as a `np.uint8` array of shape `(N, L)`; agreement vectors reduce to broadcasting.
- **Parallelism.** Stage A.1 (clustering) and A.2 (NJ) are once-off. Stage B and C are **embarrassingly parallel across genomes** — `multiprocessing.Pool` over the 5000 queries. This is the scaling axis: do not parallelize *within* a genome; parallelize across.
- **Memory.** The 5000 × 30000 uint8 alignment is 150 MB; the pairwise distance matrix for clustering is the dominant cost (~200 MB). Total peak memory < 4 GB; runs on a laptop.
- **Bootstrap budget.** 100 parametric-bootstraps × 5000 genomes × ~1 s per scan ≈ 6 days on one core; with 16 cores ≈ 9 h. If this is too slow, reduce to 50 bootstraps and use the analytical LRS as a fast pre-filter, bootstrapping only borderline cases (0.01 < p_analytical < 0.1).
- **Library footprint.** BioPython for I/O, NumPy/SciPy for everything else. ML likelihood evaluation is hand-written (Felsenstein pruning on a 4-taxon constraint tree) — about 200 lines of NumPy with caching of partial likelihoods. No compiled extensions required.

---

## 6. Limitations and Failure Cases

**Fundamental limits (no method can overcome these):**
- **Unsampled parents.** If neither true parent is in the dataset, we can flag a tract as anomalous but cannot name a donor. We will report these as "orphan tracts" with a placeholder parent.
- **Substitution-density resolution floor.** A recombinant tract shorter than ~`1 / (π × tract_length)` informative sites is statistically indistinguishable from noise, where π is pairwise diversity. For SARS-CoV-2 (π ≈ 10⁻³) this floor is ~1 kb; for HIV (π ≈ 10⁻²) it is ~100 bp. We report a per-event "resolution estimate" so the user knows.
- **Convergent evolution at the tract scale.** Immune-escape sites in spike, drug-resistance sites in HIV pol, and receptor-binding changes can produce convergent tracts of 50–300 bp that look exactly like recombination. Biologically, they are not. We cannot distinguish these from recombination without external information.

**Method-specific failure modes (and our mitigations):**
- **Greedy binary segmentation misses short internal tracts.** A 300-bp tract in the middle of a 30-kb genome flanked by two long parental tracts may be absorbed into one side. Mitigation: after the main pass, scan residuals for short tracts; report any that pass a stricter threshold.
- **The reference tree from Stage A.2 is wrong.** If NJ puts the wrong lineages together, parental assignment degrades. Mitigation: never trust the tree topology for assignment — only for branch lengths. Assignment comes from cluster consensus (Stage A.1), which is robust to tree error.
- **Hypermutants.** APOBEC / ADAR editing produces clusters of mutations that look like a recombination tract from a divergent lineage. Mitigation: pre-filter rows with the tell-tale signature (G→A in HIV, context-dependent in SARS-CoV-2) using an existing hypermutant screen.
- **Sequencing / assembly chimeras.** These are *real* mosaics but not biological recombination. Mitigation: flag recombinants whose breakpoints coincide with known difficult-to-sequence regions, with extreme branch lengths on one tract, or with low-coverage regions if the user provides coverage.
- **Dual infection / within-host recombination.** A single sample that is itself a mixture can look like a recombinant. We have no way to detect this from the alignment alone; the user must rule it out with read-level data.
- **Rate heterogeneity masquerading as recombination.** The CUSUM scan (B.1) is vulnerable. The intersection with B.2 and the parametric bootstrap under H0 (which includes rate heterogeneity via Γ) are the guards. If the user's data has extreme rate heterogeneity (α < 0.05), the false-positive rate will rise; we recommend then partitioning by gene / codon position before the scan.
- **Multiple-testing across 5000 genomes.** Naive per-genome p-values give many false discoveries. We control with Benjamini–Hochberg at FDR = 0.05 globally; for very-stringent calls, Bonferroni on the 5000 tests.

**Things we explicitly do NOT do, and why:**
- We do **not** infer a recombinant phylogenetic network (e.g. SplitsTree, NeighborNet) for all 5000 genomes — these do not scale and do not localize breakpoints.
- We do **not** build a separate ML tree per window (the classical bootscan) — window-size bias dominates and the compute is N× higher. We replace it with the CUSUM + parental-string scan and reserve likelihood evaluation for refinement.
- We do **not** attempt a joint Bayesian model over all genomes (too slow on CPU for 5000 × 30000). The per-genome frequentist procedure is what makes CPU feasibility possible.

---

## 7. Summary of the Design in One Paragraph

Treat recombination as a **changepoint problem on the genome's ancestry**: build a population scaffold once (clusters + NJ tree + GTR+Γ), screen each genome cheaply with two independent scans (a CUSUM on nearest-neighbor agreement and a windowed parental-string scan) whose intersection suppresses both rate-heterogeneity and convergence artifacts, then refine only the surviving candidates with a **likelihood-ratio test of one-parent vs. two-parent models**, using **parametric bootstrap** for honest p-values and **profile-likelihood intervals** for breakpoint localization. Validate by simulation under two simulator families (sweeping tract length, divergence, sample size), benchmark against RDP5/GARD/3SEQ, and check on real SARS-CoV-2 Pango-recombinant lineages as external ground truth. The method is CPU-feasible (a 16-core node for ~a day), and its principal limits — unsampled parents, the substitution-density resolution floor, and convergence-vs-recombination confounding — are inherent to the problem, not to the algorithm.
