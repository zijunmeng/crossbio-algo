"""SCOUT v0.2.1 tests -- PLS + entropic OT.

P0-4: there is ONE B_atac used by impute AND the reconstruction check (no shadow formula,
no dropped svals). Each correctness test has a deliberately-broken MUTATION that must score
worse, so the suite distinguishes the right algorithm from wrong ones.

Run:  cd examples/scout && PYTHONPATH=. python -m pytest test_scout.py -v
"""
import numpy as np

import scout


def _column_corr(A, B):
    """Mean per-peak (per-column) Pearson correlation in [-1,1]."""
    A = np.asarray(A, float) - np.asarray(A, float).mean(0)
    B = np.asarray(B, float) - np.asarray(B, float).mean(0)
    na = np.linalg.norm(A, axis=0) + 1e-12
    nb = np.linalg.norm(B, axis=0) + 1e-12
    return float(np.mean((A / na * B / nb).sum(0)))


def _subspace_alignment(Z_hat, Z_true):
    A = Z_hat - Z_hat.mean(0); B = Z_true - Z_true.mean(0)
    A /= np.linalg.norm(A, axis=0, keepdims=True) + 1e-12
    B /= np.linalg.norm(B, axis=0, keepdims=True) + 1e-12
    return float(np.linalg.svd(A.T @ B, compute_uv=False).mean())


def _make_paired(seed=0, n=500, k=5, g_rna=20, g_atac=30, rna_noise=0.5):
    """RNA + ATAC from shared Z; RNA carries extra noise uncorrelated with ATAC
    (this separates PLS -- which ignores ATAC-uncorrelated RNA variance -- from RNA-only PCA)."""
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n, k))
    W_rna = rng.normal(size=(k, g_rna))
    W_atac = rng.normal(size=(g_atac, k))
    X_rna = Z @ W_rna + rna_noise * rng.normal(size=(n, g_rna))
    X_atac = Z @ W_atac.T
    return scout._AD(X_rna.astype("float32"), {"ATAC": X_atac.astype("float32")}), Z, W_rna, W_atac


# ---------------- Task 1: pair_map (PLS) ----------------
def test_pair_map_recovers_shared_subspace():
    adata, Z, _, _ = _make_paired()
    fit = scout.pair_map(adata, k=5)
    assert fit.Z.shape == (500, 5)
    assert _subspace_alignment(fit.Z, Z) > 0.8, "PLS latent must recover the shared subspace"


def test_pair_map_is_pls_not_uncentered_MUTATION():
    """P0-4: pair_map CENTERS before SVD. v0.1's uncentered cross-product would chase a shared offset."""
    adata, Z, _, _ = _make_paired()
    Xr = np.asarray(adata.X, float) + 50.0
    Xa = np.asarray(adata.obsm["ATAC"], float) + 50.0
    fit = scout.pair_map(scout._AD(Xr.astype("float32"), {"ATAC": Xa.astype("float32")}), k=5)
    assert _subspace_alignment(fit.Z, Z) > 0.7, "centering must keep PLS robust to a shared offset"


def test_pair_map_cross_modal_prediction_MUTATION():
    """P0-4 core: the ONE B_atac carries cross-modal info; impute & reconstruction use it identically."""
    adata, _, _, _ = _make_paired()
    X_atac = np.asarray(adata.obsm["ATAC"], float)
    fit = scout.pair_map(adata, k=5)

    recon_correct = fit.Z @ fit.B_atac                 # the reconstruction check
    corr_correct = _column_corr(recon_correct, X_atac)
    # consistency guard (P0-4): impute on the paired scores == the reconstruction (same B_atac)
    assert np.allclose(scout.impute(fit.Z, fit), recon_correct), \
        "impute and the reconstruction check must use the SAME B_atac"

    rng = np.random.default_rng(123)
    corr_mut = _column_corr(fit.Z @ rng.normal(size=fit.B_atac.shape), X_atac)  # random B_atac
    assert corr_correct > 0.5, f"learned B_atac reconstructs ATAC (per-peak>0.5): {corr_correct:.3f}"
    assert corr_mut < corr_correct - 0.3, "mutation (random B_atac) must reconstruct worse"
    assert corr_mut < 0.2, f"random B_atac should be ~0 corr: {corr_mut:.3f}"


# ---------------- Task 2: project (entropic OT) ----------------
def test_ot_projects_inmanifold_end_to_end_MUTATION():
    """In-manifold spatial -> imputed ATAC matches truth; random transport -> garbage."""
    multi, spatial = scout.simulate(seed=1, manifold_overlap=1.0, rna_noise=0.3)
    atac_true = np.asarray(spatial.obsm["ATAC_true"], float)
    fit = scout.pair_map(multi, k=5)
    spatial_Z, _c, _l = scout.project(fit, spatial)
    corr_correct = _column_corr(scout.impute(spatial_Z, fit), atac_true)

    rng = np.random.default_rng(7)
    corr_mut = _column_corr(scout.impute(rng.normal(size=spatial_Z.shape), fit), atac_true)
    assert corr_correct > 0.5, f"OT-projected in-manifold spatial should recover ATAC: {corr_correct:.3f}"
    assert corr_mut < corr_correct - 0.3, "random transport (no OT) must be worse"


def test_low_confidence_low_reads_AC2():
    """AC-2: spots with reads < threshold are flagged low_confidence."""
    multi, spatial = scout.simulate(seed=2)
    fit = scout.pair_map(multi, k=5)
    X = np.asarray(spatial.X, float).copy()
    X[:20] = 0.0                                # zero reads for first 20 spots
    low_ad = scout._AD(X.astype("float32"), dict(spatial.obsm))
    _z, _c, lowc = scout.project(fit, low_ad, reads_threshold=10.0)
    assert lowc[:20].all(), "low-reads spots must be flagged low_confidence (AC-2)"


def test_low_confidence_out_of_manifold_AC1():
    """AC-1: out-of-manifold spatial cells (spread OT transport) are flagged low_confidence."""
    multi, spatial = scout.simulate(seed=3, manifold_overlap=0.3)   # 70% out-of-manifold
    fit = scout.pair_map(multi, k=5)
    _z, _c, lowc = scout.project(fit, spatial, reads_threshold=-1.0)  # disable reads flag, isolate AC-1
    n_spatial = spatial.X.shape[0]
    n_in = int(0.3 * n_spatial)
    assert lowc[n_in:].mean() > 0.5, f"out-of-manifold spots should be low_confidence (AC-1): {lowc[n_in:].mean():.2f}"


# ---------------- Task 3: impute consistency (P0-4) ----------------
def test_impute_uses_one_B_atac():
    """P0-4 regression guard: impute uses fit.B_atac exactly (no shadow formula, no dropped svals)."""
    adata, _, _, _ = _make_paired()
    fit = scout.pair_map(adata, k=5)
    rng = np.random.default_rng(5)
    Zs = rng.normal(size=(30, 5))
    assert np.allclose(scout.impute(Zs, fit), Zs @ fit.B_atac)


# ---------------- Task 4: downsample + benchmark ----------------
def test_downsample_drift_and_lowconfidence_grow_AC2():
    rows = scout.downsample_curve(seed=0, reads_list=(100, 50, 20, 10, 5))
    drifts = [r[1] for r in rows]
    lowfracs = [r[2] for r in rows]
    assert drifts[0] < drifts[-1], f"drift must grow as reads drop: {drifts}"
    assert lowfracs[-1] >= lowfracs[0], f"low_confidence fraction must grow as reads drop: {lowfracs}"


def test_benchmark_beats_naive():
    """AC-4: SCOUT recovery > mean-impute and > zero (the naive baselines a fair benchmark must include)."""
    res = scout.benchmark(seed=0, k=5)
    assert res["scout"] > res["mean_impute"], f"SCOUT must beat mean-impute: {res}"
    assert res["scout"] > res["zero"], f"SCOUT must beat zero: {res}"
    assert res["scout"] > 0.3, f"SCOUT recovery should be meaningful: {res}"
