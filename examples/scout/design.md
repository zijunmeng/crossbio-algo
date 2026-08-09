# SCOUT — Design (v0.2.1, PLS + entropic OT)

> The machine-checkable payload of this design is in `artifacts/design.json` (validated by
> `crossbio validate-chain examples/scout/artifacts`). This file is the human-readable full
> formal-method contract (15 required + 2 optional fields). v0.2.0 said "CCA-via-SVD" and shipped
> `TruncatedSVD`; v0.2.1 unifies to **PLS** (centered cross-covariance SVD) + **optimal transport**
> (Sinkhorn) with ONE cross-modal coefficient `B_atac` used by `impute` and the reconstruction check.

## Model in one sentence
Paired factors by **PLS** (SVD of the centered RNA-ATAC cross-covariance) + spatial projection by
**entropic optimal transport** (Sinkhorn) into the paired latent; spatial ATAC = projected latent · `B_atac`.

## Module breakdown (typed interfaces)
| module | responsibility | in | out |
|---|---|---|---|
| `scout.pair_map` | learn paired RNA-ATAC latent (PLS) | `multi_adata.X` (RNA n×g_rna), `multi_adata.obsm['ATAC']` (n×g_atac) | `ScoutFit` (.Z n×k, .U g_rna×k, .V g_atac×k, .B_atac k×g_atac, .svals k) |
| `scout.project` | spatial RNA → paired latent via OT + confidence | `fit`, `spatial_adata.X` (m×g_rna) | `spatial_Z` (m×k), `confidence` (m), `low_confidence` (m, bool) |
| `scout.impute` | infer spatial ATAC (the ONE cross-modal map) | `spatial_Z`, `fit.B_atac` | `atac_hat` (m×g_atac) |
| `scout.simulate` / `benchmark` / `downsample_curve` | semi-synthetic DGP + AC checks | params | metrics |

## Data flow
```
multi_adata.X(RNA) + .obsm['ATAC']
  → pair_map  →  ScoutFit{Z, U, V, B_atac, svals}        (PLS: centered cross-covariance SVD + lstsq B_atac)
spatial_adata.X(RNA)
  → project(fit, spatial) → spatial_Z + confidence + low_confidence   (entropic OT / Sinkhorn, out-of-manifold detection)
  → impute(spatial_Z, fit) → atac_hat = spatial_Z @ B_atac            (ONE map; same as the reconstruction check)
```

## Group P — Problem
- `problem_definition`: from paired scMultiome (RNA+ATAC) + spatial RNA (no ATAC), infer spatial ATAC via a shared paired latent; CPU-only.
- `estimand`: the unobserved spatial ATAC accessibility at each spot, recovered through the paired shared latent.

## Group F — Formalization
- `mathematical_abstraction`: masked cross-modal factor recovery + distribution alignment (OT). (rejected: a deep generative VAE — needs GPU, opaque failure mode.)
- `notation_and_shapes`: `X_rna∈R^{n×g_rna}`, `X_atac∈R^{n×g_atac}`, `X_s∈R^{m×g_rna}` spatial RNA; centered → `Xr, Xa`; `C=XrᵀXa/n`; SVD `C=U diag(S) Vᵀ`; `Z=XrU` (n×k); `B_atac=lstsq(Z,Xa)` (k×g_atac); spatial latent coords `φ_s=(X_s−mean_rna)U`, `φ_p=Z`; transport plan `P` (m×n); `spatial_Z` (m×k); `atac_hat` (m×g_atac).
- `assumptions`: paired cells share latent Z with linear RNA/ATAC loadings; spatial spots are mixtures alignable to the paired manifold by OT; counts overdispersed (narrative; the demo DGP is Gaussian-linear).
- `objective_or_likelihood`: PLS `max tr(Uᵀ C V)` over orthonormal U,V (⇒ SVD of C); `B_atac = argmin‖Xa−ZB‖²`; spatial projection `min⟨P,M⟩+ε·KL(P‖ab)` (Sinkhorn), `M`=squared cost between `φ_s` and `φ_p`.
- `identifiability`: spatial ATAC is **not** directly identifiable (no spatial ATAC observed). Identifiable only via the shared latent + the OT-alignment assumption; fails when the spatial manifold does not overlap the paired manifold (fb1) or pairing is weak (fb3).

## Group A — Algorithm
- `cross_domain_inspiration`: PLS (chemometrics) for paired factors; entropic OT (economics/transport) for cross-domain alignment. Both mature; the utility locus is the CPU-only, transparent combination + explicit failure boundaries (not new math).
- `proposed_algorithm`: (1) center X_rna, X_atac; (2) `C=XrᵀXa/n`, SVD→U,S,V (truncate k); (3) `Z=XrU`; (4) `B_atac=lstsq(Z,Xa)`; (5) for spatial: `φ_s=(X_s−mean_rna)U`; detect out-of-manifold spots (nearest paired > 3× cloud spacing); (6) Sinkhorn on in-manifold spots → `P`; barycentric `spatial_Z=(P@Z)/rowsum(P)`; (7) `atac_hat=spatial_Z@B_atac`; (8) confidence from transport entropy, `low_confidence` from reads<threshold | out-of-manifold | high entropy.
- `optimization_or_inference`: SVD (closed-form) + least-squares (closed-form) + Sinkhorn fixed-point iterations (converges for entropic OT; `n_iter=200`). Production: `ot.sinkhorn` (POT), mini-batch over m.
- `complexity`: pair_map SVD `O(min(g,n)²·max)` + lstsq `O(nk²)`; project Sinkhorn `O(n_iter·m_in·n)` (mini-batch over m for scale); CPU-feasible to ~100k spots with mini-batch.

## Group G — Guarantees
- `failure_boundaries`: **fb1** out-of-manifold spatial (transport spreads/collapses → fallback to mean latent, flagged); **fb2** reads<threshold (sparse RNA, flagged); **fb3** weak pairing/small svals (latent carries little ATAC info); **fb4** batch shift (OT aligns batch, not biology — documented limitation).
- `uncertainty_and_calibration` *(encouraged)*: per-spot `confidence∈[0,1]` from transport entropy (relative, not coverage-calibrated); `low_confidence` boolean.
- `invariances` *(encouraged)*: not scale-invariant (centering + cross-covariance depend on units); permutation-invariant in cell/spot and gene/peak index.

## Group V — Validation
- `simulation_dgp`: shared Z → paired RNA+ATAC (linear loadings); spatial cells = copies of paired Z (in-manifold) + shifted draws (out-of-manifold, fb1); `pairing_strength→0` (fb3); Poisson downsample of spatial reads (fb2). Includes null (random spatial), oracle (true latent), trivial (mean/zero baselines).
- `benchmark_protocol`: per-peak Pearson + RMSE of (imputed vs ATAC_true) for SCOUT vs **pls_direct (PLS, no OT)**, **mean-impute** (from the TRAINING/paired ATAC mean — no leakage), **zero**, across regimes {nominal, fb3-weak-pairing, fb1-out-of-manifold} (ac-bench traces fb1+fb3, so those regimes MUST be exercised, not just nominal). SCGLUE/ISON: external harness. **HONEST FINDING (v0.2.3)**: on this synthetic DGP, `pls_direct >= SCOUT` (nominal 1.00 vs 0.97; out-of-manifold 1.00 vs 0.38, RMSE 0.00 vs 5.87) — the OT step's contribution is NOT demonstrated by this benchmark; the DGP does not create the distribution-shift regime where OT would help. A documented limitation of the fixture's benchmark, NOT a claim that OT is useless.
- `novelty_or_utility_basis`: SCOUT is the **skills' end-to-end research fixture**, NOT a publication-grade T2 tool. PLS+OT are mature; the fixture's value is exercising the full loop + surfacing (honestly) that its own benchmark does NOT justify the OT step. Coordinate-agnostic (no spatial regularization); fb3/fb4 documented limitations.

## Dependencies
`numpy>=1.26` (SVD, lstsq, Sinkhorn), `scikit-learn>=1.4` (optional NearestNeighbors fallback). Production OT: `POT>=0.9`. No AnnData hard-depend (uses a `_AD` substitute so the example runs dep-light).

## Engineering constraints
CPU-only (no GPU); `numpy.random.default_rng(seed)` for reproducibility; deterministic given seed. Mini-batch Sinkhorn for >100k spots.

## Publication Roadmap
- **MVP scope** (this example): pair_map + project + impute on semi-synthetic, all 4 failure_boundaries tested, benchmark beats naive baselines (scout≈0.97 vs ≈0). Artifact chain machine-validated.
- **Engineering gap**: POT `ot.sinkhorn` for >100k / real scMultiome ingestion / Docker+CI (3d, P0).
- **Experiment gap**: real SCGLUE/ISON benchmark on shared semi-synthetic + real fetal-brain Stereo-seq; coupling-sweep & manifold-overlap figures (5d, P0).
- **Writing gap**: intro (vs SCGLUE/ISON), methods (PLS+OT math, identifiability), results (applicability-boundary figure fb1–fb4) (4d, P1).
