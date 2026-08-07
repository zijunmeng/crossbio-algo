"""SCOUT — Paired-projection spatial multimodal integration.

From paired scMultiome (RNA+ATAC, no spatial) + spatial RNA (no ATAC), infer spatial ATAC.
v0.2.1 model (P0-4 unified): **PLS** (SVD of the *centered* cross-covariance) learns the
paired factors; **entropic optimal transport** (Sinkhorn) projects spatial-only RNA into the
paired latent. CPU-only, numpy.

Coordinate-agnostic: SCOUT produces a per-spot ATAC estimate but does NOT consume spatial (xy)
coordinates — ``obsm['spatial']`` is passed through for downstream visualization only. There is no
spatial regularization (a deliberate scope boundary; see ``design.md``).

P0-4 consistency guarantee: there is ONE cross-modal coefficient `B_atac` (latent->ATAC, fit by
least squares on the paired data). It is used by BOTH `impute()` AND the cross-modal reconstruction
check -- so "the formula the tests validate" IS "the formula the code ships." v0.1's bug (the test
used `diag(svals)` while `impute` dropped them) cannot recur: there is a single map.

Run tests:  cd examples/scout && PYTHONPATH=. python -m pytest test_scout.py -v
"""
from __future__ import annotations

import numpy as np


# ----------------------------------------------------------------------------
# Task 1 -- pair_map: PLS via SVD of the CENTERED cross-covariance
# ----------------------------------------------------------------------------
class ScoutFit:
    """Fitted paired model. The cross-modal map is `B_atac` -- used by impute AND reconstruction."""

    def __init__(self, Z, U, V, B_atac, svals, mean_rna, mean_atac, k):
        self.Z = Z              # [n, k] paired RNA scores (latent)
        self.U = U              # [g_rna, k] RNA directions (orthonormal columns)
        self.V = V              # [g_atac, k] ATAC directions (orthonormal columns)
        self.B_atac = B_atac    # [k, g_atac] latent->ATAC regression coeff (THE cross-modal map)
        self.svals = svals      # [k] singular values of cross-covariance (coupling strength; NOT used by impute)
        self.mean_rna = mean_rna
        self.mean_atac = mean_atac
        self.k = k


def pair_map(multi_adata, k=30):
    """Learn the paired RNA-ATAC latent (PLS: SVD of the centered cross-covariance).

    Centering makes this honestly PLS / cross-covariance SVD. v0.1 mislabeled the UNCENTERED
    cross-product as "CCA-via-SVD" -- without centering + whitening it is not CCA.
    """
    X_rna = np.asarray(multi_adata.X, dtype=float)            # [n, g_rna]
    X_atac = np.asarray(multi_adata.obsm["ATAC"], dtype=float)  # [n, g_atac]
    n = X_rna.shape[0]
    mean_rna = X_rna.mean(axis=0)
    mean_atac = X_atac.mean(axis=0)
    Xr = X_rna - mean_rna
    Xa = X_atac - mean_atac

    C = (Xr.T @ Xa) / n                         # centered cross-covariance [g_rna, g_atac]
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    U, S, Vt = U[:, :k], S[:k], Vt[:k, :]

    Z = Xr @ U                                  # paired RNA scores [n, k]
    # THE cross-modal map: least-squares latent->ATAC. Proper rank-k predictor; impute & check share it.
    B_atac = np.linalg.lstsq(Z, Xa, rcond=None)[0]     # [k, g_atac]
    return ScoutFit(Z=Z, U=U, V=Vt.T, B_atac=B_atac, svals=S,
                    mean_rna=mean_rna, mean_atac=mean_atac, k=k)


# ----------------------------------------------------------------------------
# Task 2 -- project: spatial RNA -> paired latent via entropic OT (Sinkhorn)
# ----------------------------------------------------------------------------
def _sqdist(A, B):
    """Squared Euclidean distance [m, n]."""
    aa = (A * A).sum(axis=1)[:, None]
    bb = (B * B).sum(axis=1)[None, :]
    return np.maximum(aa + bb - 2.0 * (A @ B.T), 0.0)


def _sinkhorn(M, eps, n_iter=200):
    """Entropic OT transport plan P [m, n] for cost M, uniform marginals. Pure numpy.

    Production note: replace with `ot.sinkhorn` (POT) for >100k cells; the math is identical.
    """
    m, n = M.shape
    a = np.full(m, 1.0 / m)
    b = np.full(n, 1.0 / n)
    K = np.exp(-M / max(eps, 1e-12))
    u = np.ones(m)
    v = np.ones(n)
    for _ in range(n_iter):
        u = a / (K @ v + 1e-30)
        v = b / (K.T @ u + 1e-30)
    return u[:, None] * K * v[None, :]


def project(fit, spatial_adata, eps=None, n_iter=200, reads_threshold=10.0, count_layer=None):
    """Project spatial RNA into the paired latent by entropic OT, + per-spot confidence.

    - AC-1 (heterogeneous region -> low confidence): a spot is low-confidence if it is OUT of the
      paired manifold (nearest paired cell far beyond the cloud's own spacing -> fb1) OR its OT
      transport is spread (high entropy = ambiguous mapping).
    - AC-2 (per-spot reads < threshold -> low_confidence): flagged True; the spot still receives a
      latent (mean paired latent fallback / OT barycenter for in-manifold spots).

    Out-of-manifold spots are excluded from Sinkhorn (they would underflow the kernel and distort
    the transport) and receive the mean paired latent + a low-confidence flag. For >100k spots, run
    Sinkhorn in mini-batches over the in-manifold set (POT's ``ot.sinkhorn``); the math is unchanged.

    Returns spatial_Z [m, k], confidence [m] in [0,1], low_confidence [m] (bool).
    """
    X_s = np.asarray(spatial_adata.X, dtype=float)            # [m, g_rna]
    m = X_s.shape[0]
    # AC-2 read-depth uses RAW counts. count_layer selects the layer; if None, .X is assumed raw
    # counts (a warning is appropriate) — many .X are log1p/normalized, for which reads<threshold is
    # meaningless (reviewer §14). Pass count_layer="counts" to apply the rule correctly.
    if count_layer is not None and hasattr(spatial_adata, "layers") and count_layer in spatial_adata.layers:
        reads = np.asarray(spatial_adata.layers[count_layer], dtype=float).sum(axis=1)
    elif count_layer is not None:
        import sys
        print(f"SCOUT: count_layer {count_layer!r} not found — reads rule disabled", file=sys.stderr)
        reads = np.full(m, np.inf)
    else:
        reads = X_s.sum(axis=1)

    Xr_s = X_s - fit.mean_rna
    phi_s = Xr_s @ fit.U                                       # spatial RNA-side latent coords [m, k]
    phi_p = fit.Z                                              # paired RNA-side latent coords [n, k]

    Dp = _sqdist(phi_p, phi_p); np.fill_diagonal(Dp, np.inf)
    paired_nn = np.median(Dp.min(axis=1))                      # typical squared NN spacing in the cloud
    if eps is None:
        eps = 0.5 * paired_nn + 1e-9     # squared-cost units (M is squared dist) -> M/eps dimensionless (reviewer §11.1)

    M = _sqdist(phi_s, phi_p)                                  # [m, n] cost
    far = M.min(axis=1) > 9.0 * paired_nn                      # out-of-manifold (fb1): >3x cloud spacing
    Href = np.log(fit.Z.shape[0])

    spatial_Z = np.tile(fit.Z.mean(axis=0), (m, 1)).astype(float)   # fallback for out-of-manifold
    H = np.full(m, Href)                                       # far -> max entropy -> flagged
    in_idx = np.where(~far)[0]
    if in_idx.size:
        P = _sinkhorn(M[in_idx], eps=eps, n_iter=n_iter)       # clean: only in-manifold rows
        Ps = P.sum(axis=1, keepdims=True) + 1e-30
        spatial_Z[in_idx] = (P @ fit.Z) / Ps                   # barycentric projection
        Pn = P / Ps
        H[in_idx] = -np.sum(Pn * np.log(Pn + 1e-30), axis=1)

    confidence = 1.0 - np.clip(H / (Href + 1e-9), 0.0, 1.0)
    low_confidence = (reads < reads_threshold) | far | (H > 0.6 * Href)
    return spatial_Z, confidence, low_confidence


# ----------------------------------------------------------------------------
# Task 3 -- impute: the ONE cross-modal map (P0-4 consistency)
# ----------------------------------------------------------------------------
def impute(spatial_Z, fit):
    """Infer spatial ATAC. Uses the SAME `B_atac` the cross-modal reconstruction check validates."""
    return spatial_Z @ fit.B_atac                              # [m, k] @ [k, g_atac] -> [m, g_atac]


# ----------------------------------------------------------------------------
# Task 4 -- simulate (DGP) + downsample failure curve + benchmark
# ----------------------------------------------------------------------------
def simulate(n_multi=300, n_spatial=200, k=5, g_rna=20, g_atac=30,
             pairing_strength=1.0, manifold_overlap=1.0, rna_noise=0.0, seed=0):
    """Semi-synthetic DGP (per simulation_dgp in the design contract).

    - shared latent Z drives paired RNA+ATAC.
    - `pairing_strength` scales W_atac -> weak cross-covariance (fb3).
    - `manifold_overlap` in (0,1]: fraction of spatial cells drawn IN the paired manifold
      (the rest are out-of-manifold -> fb1, heterogeneous, should be low-confidence).
    - `rna_noise`: RNA-only variance uncorrelated with ATAC (separates PLS from RNA-only PCA).
    """
    rng = np.random.default_rng(seed)
    Z_multi = rng.normal(size=(n_multi, k))
    W_rna = rng.normal(size=(k, g_rna))
    W_atac = pairing_strength * rng.normal(size=(g_atac, k))

    rna_multi = Z_multi @ W_rna + rna_noise * rng.normal(size=(n_multi, g_rna)) + 10.0
    multi = _AD(rna_multi.astype("float32"),
                {"ATAC": (Z_multi @ W_atac.T).astype("float32")})

    n_in = int(manifold_overlap * n_spatial)
    Z_space = np.empty((n_spatial, k))
    Z_space[:n_in] = Z_multi[rng.choice(n_multi, n_in, replace=True)]         # in-manifold
    Z_space[n_in:] = rng.normal(size=(n_spatial - n_in, k)) * 2.0 + 3.0        # far from paired manifold (fb1)
    atac_true = Z_space @ W_atac.T                                            # ground-truth spatial ATAC
    rna_space = Z_space @ W_rna + rna_noise * rng.normal(size=(n_spatial, g_rna)) + 10.0
    spatial = _AD(rna_space.astype("float32"),
                  {"spatial": rng.uniform(size=(n_spatial, 2)),
                   "ATAC_true": atac_true.astype("float32")})
    return multi, spatial


def _perpeak_corr(A, B):
    """Mean per-peak (per-column) Pearson correlation in [-1,1]."""
    A = A - A.mean(0); B = B - B.mean(0)
    na = np.linalg.norm(A, axis=0) + 1e-12
    nb = np.linalg.norm(B, axis=0) + 1e-12
    return float(np.mean((A / na * B / nb).sum(0)))


def benchmark(seed=0, k=5):
    """Semi-synthetic benchmark (AC-4): SCOUT ATAC recovery vs naive baselines.

    Returns per-peak Pearson corr of imputed vs true ATAC for: scout, mean-impute, zero.
    SCGLUE/ISON comparison is a documented harness -- run those externally and feed their imputed
    matrices to `_perpeak_corr`; this computes SCOUT + the naive baselines any fair benchmark MUST
    include (the simplest competitors are the most important real ones).
    """
    multi, spatial = simulate(seed=seed, k=k)
    atac_true = np.asarray(spatial.obsm["ATAC_true"], dtype=float)

    fit = pair_map(multi, k=k)
    spatial_Z, _conf, _lowc = project(fit, spatial)
    atac_scout = impute(spatial_Z, fit)

    atac_mean = np.tile(atac_true.mean(0), (atac_true.shape[0], 1))   # global-mean baseline (Cat 5)
    atac_zero = np.zeros_like(atac_true)                              # all-zero baseline (Cat 5)
    return {
        "scout": _perpeak_corr(atac_scout, atac_true),
        "mean_impute": _perpeak_corr(atac_mean, atac_true),
        "zero": _perpeak_corr(atac_zero, atac_true),
    }


def downsample_curve(seed=0, reads_list=(100, 50, 20, 10, 5)):
    """AC-2 failure curve: downsample spatial RNA reads -> imputation drift grows AND the
    low_confidence fraction grows (budget-borrowing + flagging must engage)."""
    multi, spatial = simulate(seed=seed)
    X_ref = np.asarray(spatial.X, dtype=float).copy()
    atac_true = np.asarray(spatial.obsm["ATAC_true"], dtype=float)

    fit = pair_map(multi, k=5)
    scale_ref = X_ref.mean()

    rows = []
    for reads in reads_list:
        rng = np.random.default_rng(seed * 7 + reads)
        lam = X_ref / max(X_ref.mean(), 1e-9) * reads
        X_down = rng.poisson(np.clip(lam, 0, None)).astype(float)
        X_down *= scale_ref / max(X_down.mean(), 1e-9)         # fix scale so neighbors still match
        down_ad = _AD(X_down.astype("float32"), dict(spatial.obsm))
        spatial_Z, _c, lowc = project(fit, down_ad)
        atac_hat = impute(spatial_Z, fit)
        drift = float(np.sqrt(((atac_hat - atac_true) ** 2).mean()))
        rows.append((reads, drift, float(lowc.mean())))
    return rows


class _AD:                       # minimal AnnData substitute (keeps the example dep-light)
    def __init__(self, X, obsm):
        self.X = X
        self.obsm = obsm
