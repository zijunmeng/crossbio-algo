"""SCOUT TDD tests — 对应 tasks.md Task1-4. 跑: python -m pytest test_scout.py -v"""
import numpy as np
import scout


def test_pair_map_recovers_known_latent():   # Task 1
    rng = np.random.default_rng(0)
    Z = rng.normal(size=(500, 5))
    W_rna = rng.normal(size=(5, 20)); W_atac = rng.normal(size=(30, 5))
    adata = scout._AD((Z @ W_rna).astype('float32'),
                      {'ATAC': (Z @ W_atac.T).astype('float32')})
    Z_hat, _, _ = scout.pair_map(adata, k=5)
    assert Z_hat.shape == (500, 5)
    # CCA 尺度任意 → 检查子空间对齐 (canonical correlations), 不强求精确恢复
    A = Z_hat - Z_hat.mean(0); B = Z - Z.mean(0)
    A /= np.linalg.norm(A, axis=0, keepdims=True); B /= np.linalg.norm(B, axis=0, keepdims=True)
    svals = np.linalg.svd(A.T @ B, compute_uv=False)
    assert svals.mean() > 0.85, f"pair_map 子空间恢复差 (canonical corr): {svals}"


def test_confidence_drops_in_heterogeneous_region():   # Task 2, AC-1
    rng = np.random.default_rng(1)
    multi_X = rng.normal(size=(200, 10))
    Z_hetero = rng.normal(size=(200, 5))            # 异质邻域
    Z_homog = np.zeros((200, 5)); Z_homog[:, 0] = 1.0   # 同质
    _, conf_het = scout.project(multi_X[:50], Z_hetero, multi_X, k_neighbors=15)
    _, conf_hom = scout.project(multi_X[:50], Z_homog, multi_X, k_neighbors=15)
    assert conf_het.mean() < conf_hom.mean(), "异质区置信度应更低 (AC-1)"


def test_impute_recovers_atac():   # Task 3, AC-4
    rng = np.random.default_rng(2)
    spatial_Z = rng.normal(size=(100, 5))
    W_atac = rng.normal(size=(30, 5))
    atac_true = spatial_Z @ W_atac.T
    atac_hat = scout.impute(spatial_Z, W_atac)
    assert np.allclose(atac_hat, atac_true, atol=1e-5), "impute 应精确恢复 (线性映射)"


def test_downsample_drift_grows_with_sparsity():   # Task 4, AC-2
    rows = scout.downsample_curve(reads_list=(100, 50, 20, 10, 5))
    drifts = [r[1] for r in rows]
    assert drifts[0] < drifts[-1], f"downsample→稀疏, drift 应增大 (AC-2): {drifts}"
