# Algorithm Design: scRNA-seq Dropout Imputation via Graph-Regularized NB-GLM Borrowing

## 0. One-paragraph summary

We treat dropout imputation as a **denoising-by-borrowing** problem: each (cell $i$, gene $g$) zero in the count matrix is a missing value whose latent true count we estimate by combining (a) a global mean-rate prediction from a regularized Negative-Binomial (NB) generalized linear model (GLM) fit in gene-factor space, with (b) a local smoothing over a $k$-nearest-neighbor (kNN) cell graph restricted to cells that are **biologically similar and that actually expressed $g$** (an "expresser neighborhood"). The two estimates are mixed by a per-position confidence weight that is high when the local neighborhood is dense and consistent, and low (falling back to the GLM) when it is sparse. This is CPU-only, scanpy-native, no deep learning, and produces both an imputed matrix and per-entry confidence for downstream gating.

---

## 1. The precise problem

### 1.1 Inputs
- `adata`: an `AnnData` object with raw counts in `adata.X` (sparse, integer, $n_{\text{cells}} \times n_{\text{genes}}$). We assume UMI counts from a 10x-style (or equivalent) droplet platform; smart-seq2 full-length is a separate case (see §7).
- Optional but helpful: `adata.obs['total_counts']`, `adata.var['n_cells_by_counts']`, `adata.var['mt']` (mitochondrial flag) — we will recompute what we need if absent.
- Optional: batch key in `adata.obs` (we handle batch in §3.3).
- No ground-truth imputed values are available (this is the realistic regime; validation is done via the masking scheme in §4).

### 1.2 What we are estimating
For each entry $(i, g)$ that is **zero in the raw counts**, we want a point estimate $\hat{x}_{ig}$ of the latent true transcript count, *plus* an uncertainty $\hat{\sigma}_{ig}$. We do **not** impute entries that are genuinely not expressed (see §1.4 and the dropout-vs.-structural-zero distinction in §7); we output a probability $\pi_{ig}$ that the zero is a dropout (technical zero) rather than a true zero, and only "fill" entries with $\pi_{ig}$ above a user threshold.

### 1.3 The dropout model we assume
A common, defensible generative sketch (Huang et al. 2018, "SAVER"; Li & Li 2018, "scVI lineage"; van Dijk et al. 2018, "MAGIC"):

$$
X_{ig} \sim \text{NB}(\mu_{ig}, \theta_g) \quad \text{(true count)}, \qquad
Y_{ig} \mid X_{ig} \sim \text{Bernoulli}\!\bigl(\rho(\mu_{ig})\bigr) \cdot X_{ig} \quad \text{(observed)},
$$

where the detection probability $\rho$ is an increasing function of the true mean $\mu_{ig}$ — low-abundance transcripts in a given cell are preferentially lost. The observed $Y_{ig}=0$ can arise from two causes:
- **Technical dropout**: $X_{ig}>0$ but the molecule was not captured ($Y_{ig}=0$). This is what we impute.
- **Structural / biological zero**: $X_{ig}=0$ because the gene is off in that cell. We must *not* invent signal here.

Crucially, $\rho$ is not assumed known; we never invert it directly. We borrow strength across cells/genes and let the data identify which zeros are dropouts.

### 1.4 Why this is hard (the failure modes we have to design around)
1. **Indistinguishability**: at a single $(i,g)$ entry you cannot tell dropout from true-zero without external information. Any method that fills *every* zero over-imputes and inflates false signal.
2. **Mean-expression confound**: highly expressed genes rarely drop out; genes near zero in all cells are almost always truly off. A naive mean-imputation will smear marker genes into cell types where they don't belong.
3. **Batch effects**: capture efficiency differs across libraries/chromium runs; borrowing across batches without correction transfers bias.
4. **Cell-type graph errors**: if the kNN graph is built on dropout-degraded data, neighbors may be wrong, and smoothing propagates error.
5. **Computational cost**: $n_{\text{cells}} \sim 10^4$–$10^6$, $n_{\text{genes}} \sim 2\times10^4$; dense operations are infeasible. Memory and runtime must be carefully managed.

The algorithm below is designed to address each of these explicitly.

---

## 2. Method / approach

Five stages, all in scanpy / scipy / sklearn / statsmodels (CPU). No neural nets.

### Stage A — Preprocessing and "honesty" filtering

1. **Load `adata`**, force `adata.X` to a `csr_matrix` of integers. Sanity-check: no negatives, no NaNs, min is 0.
2. **Cell QC** (default thresholds, user-overridable): drop cells with `total_counts` outside $[Q_{0.01}, Q_{0.99}]$ of the log distribution, `pct_counts_mt > 20%`, `n_genes_by_counts < 200`. Record removed cells; never silently drop.
3. **Gene QC**: keep genes expressed in $\geq$ `min_cells` cells (default = 1% of cells, but at least 3 — this is the *gene must be detectably on somewhere* filter, the precondition for the dropout model to be identifiable for that gene). Remove genes in $\leq$ `min_cells` cells from the imputation target set (they have no basis for imputation; we leave their zeros as zeros).
4. **Normalization for graph-building only**: create `adata.layers['norm_log']` = `sc.pp.normalize_total` (target_sum = median of `total_counts` across cells) followed by `sc.pp.log1p`. This layer is used *only* to build the cell graph and the gene factors — **the imputed output is on the raw-count scale**, which is what a biologist expects and what NB models need.
5. **Optional HVG selection** (default 2000) used *only* for graph construction (PCA), not for restricting imputation targets.

> Design note: we deliberately separate the "analysis scale" (log-normalized) from the "imputation scale" (raw counts). Mixing them is a classic source of artifact (e.g., returning log-scale values that look like counts).

### Stage B — Cell-graph and gene-factor construction

1. **PCA on HVGs** of `adata.layers['norm_log']` → top 50 PCs. Scale before PCA (`sc.pp.scale`, `max_value=10`) to avoid a few highly variable genes dominating.
2. **kNN cell graph** in PC space, cosine distance, `n_neighbors = 25` (tunable; see §3.1). Use `pynndescent` (CPU, approximate, $O(n \log n)$) for $n_{\text{cells}} > 5\times 10^4$, exact `sklearn` otherwise. Store as a sparse adjacency $W \in \mathbb{R}^{n \times n}$.
3. **Batch-aware option** (`use_harmony=True`, default off if no batch key): run Harmony (`harmonypy`, CPU) on the PC matrix to obtain a batch-corrected embedding, then build the kNN graph there. This prevents the graph from clustering cells by batch instead of by type.
4. **Gene factors**: do a rank-$r$ (default $r=30$) **non-negative matrix factorization** of the raw-count matrix `adata.X` restricted to the QC-passing gene set:
   $$ X \approx L S, \quad L \geq 0 \in \mathbb{R}^{n \times r}, \ S \geq 0 \in \mathbb{R}^{r \times G}. $$
   Use `sklearn.decomposition.NMF` with `beta_loss='kullback-leibler'` (matches the Poisson/NB count likelihood), `init='nndsvda'`, `max_iter=300`. For $n>10^5$ we use mini-batch NMF (`MiniBatchNMF`). The NMF factors capture co-expression programs (cell-cycle, lineage, stress) used by the GLM below.

> Why NMF and not just PCA? NMF's non-negativity makes the gene factors interpretable as expression programs, and the KL-divergence objective is the right one for counts. PCA on log-data is fine for the *graph* (where we care about geometry) but bad for *rate estimation* (where we care about counts).

### Stage C — Per-gene Negative-Binomial GLM in factor space

For each gene $g$ in the imputation target set, fit an NB-GLM predicting the raw count $X_{ig}$ from the cell factors $L_{i,:}$:

$$ \log \mu_{ig} = \beta_{0g} + L_{i,:}\,\beta_g, \qquad X_{ig} \sim \text{NB}(\mu_{ig}, \theta_g). $$

- Fit with `statsmodels.discrete.discrete_model.NegativeBinomial` (Poisson warm-start for $\beta$, then $\theta_g$ via the NB1/P dispersion search). For speed on large $G$, parallelize across genes with `joblib.Parallel(n_jobs=-1)`; each gene fit is small ($n \times r$, $r=30$).
- Output: a matrix of fitted means $\hat\mu_{ig}$ for **every** cell $i$ (including zeros). This is the **global / model-based rate** — what the gene's expression "should be" given the cell's program loadings.
- Store per-gene dispersion $\hat\theta_g$; we'll use it in the confidence step.
- Add an $\ell_2$ penalty (`alpha=1e-3`) so we don't overfit rare cell types.

> Why a GLM and not deep generative? Because (i) it's CPU-cheap, (ii) it gives calibrated uncertainty via the NB variance $\mu + \mu^2/\theta$, (iii) it's interpretable and debuggable, and (iv) it gracefully degrades for lowly expressed genes (large $\hat\theta_g^{-1}$) — which is exactly where you *don't* want to over-impute.

### Stage D — Local expresser-neighborhood smoothing

The GLM is smooth and global; it can miss sharp cell-type boundaries (e.g., a marker that is on in one cluster and off elsewhere). We correct this with a **local, expression-restricted** smoother.

For cell $i$ and gene $g$ (with $Y_{ig}=0$):
1. Find $i$'s neighbors on the cell graph: $\mathcal{N}(i) = \{j : W_{ij}>0\}$.
2. Restrict to **expressers**: $\mathcal{N}_g^+(i) = \{j \in \mathcal{N}(i) : Y_{jg} > 0\}$.
3. If $|\mathcal{N}_g^+(i)| \geq m_{\min}$ (default 3), compute the local estimate as the **dispersion-shrinkage** mean:
   $$
   \hat{x}_{ig}^{\text{loc}}
   = \frac{\sum_{j \in \mathcal{N}_g^+(i)} W_{ij}\,Y_{jg} + \hat\theta_g^{-1}\,\hat\mu_{ig}}
          {\sum_{j \in \mathcal{N}_g^+(i)} W_{ij} + \hat\theta_g^{-1}}.
   $$
   This is a James–Stein / empirical-Bayes shrinkage of the local observed counts toward the GLM prior mean, with the prior weight $1/\hat\theta_g$ — genes with low dispersion trust the prior more; genes with high dispersion trust the data more.
4. If $|\mathcal{N}_g^+(i)| < m_{\min}$ (the gene is rare in this neighborhood), we **do not** produce a local estimate; we fall back to $\hat\mu_{ig}$ alone, and we flag the entry as low-confidence.

### Stage E — Per-position confidence weighting and dropout probability

For each dropout entry $(i,g)$ we produce:

1. **Imputed value**: a convex combination
   $$
   \hat{x}_{ig} = \lambda_{ig}\,\hat{x}_{ig}^{\text{loc}} + (1-\lambda_{ig})\,\hat\mu_{ig},
   \qquad
   \lambda_{ig} = \text{sigmoid}\!\bigl(\alpha_0 + \alpha_1 \log|\mathcal{N}_g^+(i)| + \alpha_2\,\overline{W}_{ig}\bigr),
   $$
   where $\overline{W}_{ig}$ is the mean graph weight to the expresser neighbors. So when the local evidence is rich and high-weight, we trust the local estimate; when it's thin, we trust the global GLM. The $\alpha$'s are fit by the masking validation in §4 (we choose them to minimize the masked-NRMSE — they are *learned from the data's own observed entries*, not hand-set).
2. **Uncertainty**: 
   $$
   \hat\sigma_{ig}^2 = \hat{x}_{ig} + \frac{\hat{x}_{ig}^2}{\hat\theta_g}.
   $$
3. **Dropout probability** $\pi_{ig}$: fit a logistic model on the *observed* entries of all genes — regress $[Y_{ig}=0]$ vs. $>0$ on features $\log(\hat\mu_{ig})$, $\log(\overline{Y}_{\cdot g})$, and `total_counts`$_i$ (a cell-level efficiency covariate). Apply it to the zero entries. Entries with $\pi_{ig} < \tau$ (default $\tau=0.5$) are deemed likely-structural-zeros and **not** imputed (kept at 0). This is the key mechanism that prevents the "smearing markers everywhere" failure mode.

### Output

- `adata.layers['imputed']`: dense-or-sparse matrix on the raw-count scale. Non-dropout entries are unchanged from `adata.X`; dropout entries are replaced by $\hat{x}_{ig}$ (rounded to nearest integer for downstream compatibility with count-based tools); structural zeros stay 0.
- `adata.layers['imputed_confidence']`: $1/\hat\sigma_{ig}$ per entry (or NaN where not applicable).
- `adata.layers['dropout_prob']`: $\pi_{ig}$.
- `adata.uns['imputation_meta']`: all hyperparameters, the $\alpha$ coefficients, the gene-dispersion vector, QC masks.

Downstream pipelines can then choose to use `imputed` directly, or reweight analyses by `imputed_confidence` (recommended for differential expression — see §6).

---

## 3. Key design decisions and their justification

### 3.1 Why both global (GLM) and local (graph) estimates?
A pure-graph smoother (MAGIC-style) over-smooths and erases sharp cluster boundaries; a pure-model approach (GLM-only) misses local structure the factors don't capture. The convex combination with **learned** $\lambda_{ig}$ lets the data tell us where each source is reliable. This is the central novelty relative to a vanilla kNN-impute.

### 3.2 Why restrict the local smoother to *expresser* neighbors?
If we averaged over *all* neighbors of $i$, a gene on in 20% of $i$'s neighborhood would be diluted by 80% structural zeros, biasing the local estimate toward zero — exactly the dropout we're trying to fix. Restricting to $Y_{jg}>0$ neighbors conditions on "this gene is actually expressible here", which is the right conditioning event for "what would the count be if it were expressed".

### 3.3 Why batch correction only in the graph, not in the counts?
Harmonizing the cell *graph* removes the spurious "cells cluster by batch" failure mode without touching the count magnitudes — so imputed counts stay comparable across batches in absolute terms, which DE tests need. If we instead harmonized the counts, we'd risk negative / uninterpretable values.

### 3.4 Why NB and not Poisson?
Poisson assumes variance = mean; real scRNA-seq has variance $\gg$ mean (overdispersion). Using Poisson would systematically underestimate uncertainty and over-trust the local smoother. NB with a free $\theta_g$ is the standard, correct choice (cf. scRNA-seq DE tools from 2017 onward).

### 3.5 Hyperparameters (defaults, all tunable, all logged in `uns`)
| Symbol | Meaning | Default | Tuning strategy |
|---|---|---|---|
| `n_neighbors` | kNN graph size | 25 | grid over $\{10, 15, 25, 50\}$, pick by masked NRMSE (§4) |
| `n_pcs` | PCA dim | 50 | default; lower if $n_{\text{cells}}$ small |
| `n_factors` ($r$) | NMF rank | 30 | grid over $\{10, 20, 30, 50\}$ |
| `min_cells` | gene QC | $\max(3, 0.01 n)$ | — |
| $m_{\min}$ | expresser neighborhood floor | 3 | raise for sparse data |
| $\tau$ | dropout-prob threshold | 0.5 | see §4 ROC analysis |

---

## 4. Validation plan

We use **three independent levels** of validation. None requires external ground truth.

### 4.1 Self-masking (negative-control) on observed entries
This is the primary quantitative test.
1. Take all **nonzero** entries of the raw matrix.
2. Mask a random fraction $f$ (we sweep $f \in \{0.1, 0.25, 0.5\}$) of them — set to 0, *as if they were dropouts*.
3. Run the imputer (re-fit from scratch on the masked matrix).
4. Compare predictions $\hat{x}_{ig}$ to the true held-out counts $X_{ig}$ via:
   - **NRMSE** (primary): $\sqrt{\langle(\hat{x}-X)^2\rangle} / \text{std}(X)$.
   - **Mean absolute error** on the count scale.
   - **Pearson and Spearman correlation** between $\hat{x}$ and $X$ on masked entries.
   - **Calibration**: do the true counts fall in $[\hat{x} - 1.96\hat\sigma, \hat{x} + 1.96\hat\sigma]$ ~95% of the time? (Tests the uncertainty, not just the point estimate.)
5. **Ablations**: re-run with (a) GLM-only ($\lambda\equiv0$), (b) local-only ($\lambda\equiv1$), (c) no expresser restriction, (d) no dropout-probability gating. The full method should beat all four.
6. **Baselines**: scran-impute, MAGIC (graph diffusion), SAVER (if installable; it's a Poisson-GAM baseline), simple gene-mean imputation. The full method should be competitive with SAVER and beat MAGIC on cluster-boundary preservation (§4.3).

> Self-masking is biased: the masked entries were *observed*, so they may have higher $\rho$ than real dropouts. We acknowledge this but it remains the standard, fairest feasible test. We also stratify the masking by gene expression quantile to probe behavior at low vs. high abundance.

### 4.2 Recovery of known marker genes (positive control)
Pick well-characterized markers for each expected cell type (e.g., for fetal brain: *SOX2*, *HES1* for progenitors; *DCX*, *TUBB3* for neuroblasts; *AIF1*, *PTPRC* for microglia/macrophages; *PDGFRA* for OPCs).
- After imputation, check that markers become *more* cleanly bimodal across clusters (lower within-cluster zero-fraction, higher between-cluster difference) **without** appearing in clusters where they're biologically absent. Concretely: for marker $g$ of cluster $c$, compute
  $$ \Delta_g = \frac{\bar{x}_{g,\text{in }c} - \bar{x}_{g,\text{not in }c}}{\bar{x}_{g,\text{all}}} $$
  before and after imputation; good imputation **increases** $\Delta_g$. A bad imputer (over-smoothing) **decreases** $\Delta_g$ by smearing the marker out.

### 4.3 Downstream-stability check
Run a standard pipeline (Leiden clustering, UMAP, rank-genes-group DE) on (a) raw data, (b) log-normalized data, (c) imputed data. Report:
- Adjusted Rand Index between clusterings (a) vs (c) and (b) vs (c). Too-high agreement = imputation did nothing; too-low = imputation changed the biology.
- **Cluster-boundary sharpness**: mean silhouette on the imputed data should not collapse relative to log-normalized (a MAGIC-tell is that silhouette inflates artificially because everything becomes smooth — we check we don't do this).

### 4.4 External / synthetic data (optional, strongest)
- Run on a **simulated** dataset with known truth: `splatter` (R) or `SymSim` generate counts with a tunable dropout rate. Fit our imputer, compare to the no-dropout ground truth directly. This removes the self-masking bias.
- If wet-lab data are available: the classic **bulk-vs-single-cell** agreement test — aggregate imputed scRNA-seq counts per cell type and correlate with bulk RNA-seq of sorted populations. High correlation ⇒ imputation is recovering real signal.

### 4.5 Acceptance criteria
- Masked NRMSE ≤ baseline-best across $f \in \{0.1, 0.25, 0.5\}$.
- 95%-calibration interval coverage within $[0.90, 0.99]$.
- Marker $\Delta_g$ increases for ≥80% of markers and decreases for none.
- Cluster ARI vs log-normalized in $[0.85, 0.99]$ (i.e., biological structure preserved, modest refinement allowed).

---

## 5. Key assumptions

1. **UMI counts, droplet platform.** The NB model and the count-scale output assume integer UMI data. Smart-seq2 (full-length, TPM-like) violates this and needs a different likelihood (lognormal/Gaussian on log-TPM); we have a `platform='smartseq2'` branch that swaps NB-GLM for a Gaussian-on-log GLM and skips the rounding step, but the rest of the pipeline (graph, factors, gating) is identical.
2. **Cells of the same biological state share co-expression programs.** This is what lets us borrow from neighbors. It is violated when the population is a *continuous* trajectory with no clear local structure (e.g., a poorly sampled differentiation wave) — there the local smoother degrades gracefully to the GLM.
3. **The dropout probability is a monotone function of true mean.** Standard assumption; the gating model in §E3 encodes this. If a platform has *cell-specific* capture (e.g., the Qian et al. 2020 protocols with strong cell-size dependence), we add a cell-level efficiency covariate (already in the model via `total_counts`).
4. **Sufficient cells per gene.** Genes in <1% of cells have no basis for imputation; we exclude them. This is a hard floor — imputation *cannot* recover a gene nobody expressed.
5. **The NMF rank $r$ captures the relevant programs.** If the biology needs >50 factors (very heterogeneous tissue), $r$ must scale up; we provide a residual-based diagnostic (the held-out reconstruction error on masked entries, as a function of $r$).
6. **No time-dependence.** We treat the matrix as iid given state. Time-series scRNA-seq would benefit from a graph that includes a temporal-neighbor edge — out of scope here, easy extension.

---

## 6. Limitations and failure cases

1. **Cannot distinguish dropout from true-zero with certainty.** $\pi_{ig}$ is a probability, not a verdict. At $\tau=0.5$ we will misclassify some structural zeros as dropouts (false signal injected) and vice versa (real dropouts left as zero). The user must tune $\tau$ via the §4.1 ROC curve for their tolerance of false-positive vs. false-negative imputation.
2. **Marker smearing in very rare cell types.** If a cell type has only a handful of cells, its kNN neighborhood is dominated by other types, and the local smoother will pull markers toward zero (the expresser-neighborhood restriction helps but doesn't fully fix this when $|\mathcal{N}_g^+(i)| < m_{\min}$). Mitigation: raise `n_neighbors` for rare clusters, or use cluster-aware graph reweighting.
3. **Computational ceiling.** For $n_{\text{cells}} > 10^6$, even NMF and the per-gene GLM fit (parallelized) become slow. Practical ceiling on a single CPU box is ~$10^5$ cells / ~$2\times10^4$ genes in ~1 hour; above that, subsample for graph/factor estimation and apply the fitted models to the full matrix (the per-entry imputation itself is embarrassingly parallel).
4. **Imputed counts are not real measurements.** Downstream tests (DE, pathway enrichment) on imputed data have inflated degrees of freedom if treated naively. We strongly recommend: (i) always carry the confidence layer, (ii) for DE, use the original counts in an NB test and treat imputed values as priors, not data — *do not plug imputed counts into a count-based DE test as if they were observed.* This is a methodological footgun the design tries to head off by exposing `imputed_confidence`.
5. **Batch correction is geometric, not magnitude-correcting.** If capture efficiency differs 2× between batches, our imputed counts will still show that 2× difference (correctly, in some sense — but DE across batches will be confounded). Users wanting cross-batch DE should additionally use a size-factor / spike-in correction.
6. **NMF factor identifiability.** NMF factors are unique only up to permutation and (under separability) are well-identified; pathological data can give unstable loadings. We mitigate with NNDSVD initialization and report a stability diagnostic (refit with 5 random seeds, report mean factor-pairwise cosine).
7. **No use of gene-gene co-expression directly in the smoother.** A more powerful method would smooth over a *bipartite* cell-gene graph (cf. HERO/netNMF-sc). We deliberately stay unipartite for CPU tractability and interpretability; this is a known accuracy/complexity trade-off.
8. **Rounding introduces a small bias** for downstream count tools. We offer `round_output=False` to keep fractional values; the user accepts the consequences for their tooling.

---

## 7. Concrete pseudocode / scanpy sketch

```python
import scanpy as sc, numpy as np, scipy.sparse as sp
from sklearn.decomposition import NMF
from statsmodels.discrete.discrete_model import NegativeBinomial
from sklearn.neighbors import NearestNeighbors
import joblib

def impute(adata, n_neighbors=25, n_pcs=50, n_factors=30,
           min_cells=None, batch_key=None, tau=0.5, m_min=3,
           mask_frac_for_alpha_fit=0.2, seed=0):
    rng = np.random.default_rng(seed)
    # --- A. preprocessing ---
    adata.layers['raw'] = adata.X.copy()
    sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
    sc.pp.filter_cells(adata, min_genes=200)
    sc.pp.filter_genes(adata, min_cells=min_cells or max(3, int(0.01*adata.n_obs)))
    adata.layers['norm_log'] = sc.pp.log1p(
        sc.pp.normalize_total(adata, target_sum=None, inplace=False)['X']).copy()
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, layer='norm_log', flavor='seurat_v3')
    # --- B. graph + factors ---
    sc.pp.scale(adata, layer='norm_log', max_value=10)
    sc.tl.pca(adata, n_comps=n_pcs, use_highly_variable=True)
    if batch_key:
        import harmonypy
        sc.external.pp.harmony_integrate(adata, key=batch_key)
        use_obsm = 'X_pca_harmony'
    else:
        use_obsm = 'X_pca'
    sc.pp.neighbors(adata, n_neighbors=n_neighbors, use_rep=use_obsm, metric='cosine')
    X_raw = adata.layers['raw'].tocsr().astype(float)
    nmf = NMF(n_components=n_factors, solver='mu', beta_loss='kullback-leibler',
              init='nndsvda', max_iter=300, random_state=seed)
    L = nmf.fit_transform(X_raw)            # n x r
    S = nmf.components_                     # r x G
    # --- C. per-gene NB-GLM (parallelized) ---
    def fit_gene(g):
        y = np.asarray(X_raw[:, g].todense()).rnel()
        try:
            glm = NegativeBinomial(y, L).fit_regularized(alpha=1e-3)
            mu = glm.predict(L)
            theta = glm.params.get('alpha', 1.0)
            return mu, theta
        except Exception:
            return np.full(y.shape, y.mean()), 1.0
    res = joblib.Parallel(n_jobs=-1)(
        joblib.delayed(fit_gene)(g) for g in range(adata.n_vars))
    Mu = np.column_stack([r[0] for r in res])     # n x G fitted means
    Theta = np.array([r[1] for r in res])         # G dispersions
    # --- D + E. local expresser-neighborhood smoothing + gating ---
    # (build neighbor index from adata.obsp['connectivities'])
    # ... [expresser-neighbor shrinkage + learned lambda via mask fit] ...
    # omitted for brevity; follows §2 Stages D-E
    # --- output ---
    adata.layers['imputed'] = ...        # count-scale
    adata.layers['imputed_confidence'] = ...
    adata.layers['dropout_prob'] = ...
    return adata
```

(Full implementation would be ~300 LOC; the sketch above is faithful to the math in §2.)

---

## 8. Why this design and not another

I considered and rejected:
- **Deep generative (scVI/scANVI)**: forbidden by the CPU / no-DL constraint; also harder to interpret and to give calibrated per-entry uncertainty.
- **Pure graph diffusion (MAGIC)**: over-smooths, destroys cluster boundaries; our §4.3 check would flag it.
- **SAVER-style (gene-by-gene Poisson-GAM)**: strong baseline, but slow and doesn't borrow across genes; our NMF+GLM is a faster, cross-gene-borrowing analog.
- **kNN-impute (vanilla)**: dilutes markers by averaging over all neighbors including structural zeros — exactly the failure our expresser-neighborhood restriction fixes.
- **DCA (deep count autoencoder)**: forbidden by no-DL.

The design above is, in effect, a **CPU-only, interpretable, uncertainty-quantified** synthesis of the GLM (model-based, like scVI's decoder without the neural net) and graph-smoothing (like MAGIC) ideas, with two engineering choices — expresser-restricted smoothing and learned per-position mixing — that address the specific failure modes in §1.4.
