"""SCOUT tests — 对应 tasks.md Task1-4.

v0.2.0: 加 mutation testing. 原测试是循环验证 (truth 与算法同公式), 不能区分
正确/错误实现. 本文件每个测试除验证正确实现通过外, 还构造一个错误实现 (mutation),
并断言 mutation 在同一正确性断言上失败 —— 即测试能区分.

关键缺口 (专家指出): pair_map 原测试只测 Z 恢复, "忽略 ATAC 只 RNA SVD" 的错误实现
也通过. 现加 cross-modal ATAC prediction: 用学到的 cross-covariance 因子从 RNA
重构 ATAC, 断言重构与真值 ATAC 的逐列相关显著高于 mutation (忽略 ATAC → 重构垃圾).

跑: PYTHONPATH=. python -m pytest test_scout.py -v
"""
import numpy as np
import pytest

import scout


# ---------- helpers ----------
def _column_correlation(A, B):
    """逐列相关取均值 (每个 ATAC 特征独立衡量重构质量), 返回 [-1,1].
    比 Procrustes 子空间对齐更严苛: 不容许任意旋转."""
    A = np.asarray(A, float) - np.asarray(A, float).mean(0)
    B = np.asarray(B, float) - np.asarray(B, float).mean(0)
    na = np.linalg.norm(A, axis=0) + 1e-12
    nb = np.linalg.norm(B, axis=0) + 1e-12
    return float(np.mean((A / na * B / nb).sum(0)))


def assert_correct_passes_mutation_fails(assertion, correct_label="correct",
                                         mutation_label="mutation"):
    """对给定 assertion(callable -> bool) 验证: 在正确实现上为 True, 在 mutation 上为 False.

    用法: 提供两个 assertion, 第一个用正确实现的输出, 第二个用 mutation 的输出.
    本 helper 调用它们并报告. 这里实现为对成对结果的直接断言包装. """
    # 直接断言形式在各自测试里内联, 此处仅作文档/占位 (各测试内联以保持清晰).
    raise NotImplementedError  # pragma: no cover


# ---------- Task 1: pair_map ----------
def _make_paired_data(seed=0, n=500, k=5, g_rna=20, g_atac=30):
    """RNA 和 ATAC 由同一 Z 生成, 但 W_rna 与 W_atac 独立随机 (不同)."""
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n, k))
    W_rna = rng.normal(size=(k, g_rna))      # 注意形状 (k, g_rna)
    W_atac = rng.normal(size=(g_atac, k))    # (g_atac, k)
    adata = scout._AD((Z @ W_rna).astype('float32'),
                      {'ATAC': (Z @ W_atac.T).astype('float32')})
    return adata, Z, W_rna, W_atac


def test_pair_map_recovers_known_latent():   # 保留原基本正确性
    adata, Z, _, _ = _make_paired_data()
    Z_hat, _, _, _ = scout.pair_map(adata, k=5)
    assert Z_hat.shape == (500, 5)
    # CCA 尺度任意 → 子空间对齐 (canonical correlations)
    A = Z_hat - Z_hat.mean(0); B = Z - Z.mean(0)
    A /= np.linalg.norm(A, axis=0, keepdims=True); B /= np.linalg.norm(B, axis=0, keepdims=True)
    svals = np.linalg.svd(A.T @ B, compute_uv=False)
    assert svals.mean() > 0.85, f"pair_map 子空间恢复差: {svals}"


def test_pair_map_cross_modal_atac_prediction_mutation():
    """最关键 mutation test: pair_map 必须用了 ATAC.

    正确实现 (cross-cov C = X_rna.T @ X_atac): 学到的因子能从 RNA 重构 ATAC.
    Mutation (忽略 ATAC, 只对 X_rna 做 SVD + 随机 W_atac): 重构与真值 ATAC 几乎无关.
    """
    adata, _, _, _ = _make_paired_data()
    X_rna = np.asarray(adata.X, dtype=float)
    X_atac = np.asarray(adata.obsm['ATAC'], dtype=float)

    # --- 正确实现: scout.pair_map ---
    _, W_rna_hat, W_atac_hat, svals = scout.pair_map(adata, k=5)
    # cross-modal 重构 (低秩 cross-covariance 近似):
    #   X_atac ≈ (X_rna @ W_rna) @ diag(svals) @ W_atac.T
    recon_correct = (X_rna @ W_rna_hat) @ np.diag(svals) @ W_atac_hat.T
    corr_correct = _column_correlation(recon_correct, X_atac)

    # --- Mutation: 忽略 ATAC —— 只对 X_rna 做 SVD, W_atac 随机 (专家点名的错误实现) ---
    rng = np.random.default_rng(123)
    Vt_rna = np.linalg.svd(X_rna, full_matrices=False)[2][:5, :].T   # (g_rna, k) RNA-only loadings
    W_atac_garb = rng.normal(size=W_atac_hat.shape)
    svals_garb = np.linalg.svd(X_rna, full_matrices=False)[1][:5]
    recon_mut = (X_rna @ Vt_rna) @ np.diag(svals_garb) @ W_atac_garb.T
    corr_mut = _column_correlation(recon_mut, X_atac)

    # 断言: 正确重构相关高, mutation 重构相关低 (显著差距)
    assert corr_correct > 0.5, (
        f"正确 pair_map 应能 cross-modal 重构 ATAC (逐列相关 >0.5): {corr_correct:.3f}")
    assert corr_mut < corr_correct - 0.3, (
        f"mutation (忽略 ATAC) 的重构相关 ({corr_mut:.3f}) 应显著低于正确实现 "
        f"({corr_correct:.3f}) —— 否则测试不能区分 '用了 ATAC' 与 '忽略 ATAC'")
    # mutation 必须真正失败 (即其重构几乎无用)
    assert corr_mut < 0.2, (
        f"忽略 ATAC 的 mutation 重构相关 ({corr_mut:.3f}) 应接近 0 (重构垃圾): {corr_mut}")


# ---------- Task 2: project (置信度) ----------
def test_confidence_drops_in_heterogeneous_region():   # 保留原基本正确性
    rng = np.random.default_rng(1)
    multi_X = rng.normal(size=(200, 10))
    Z_hetero = rng.normal(size=(200, 5))            # 异质邻域
    Z_homog = np.zeros((200, 5)); Z_homog[:, 0] = 1.0   # 同质
    _, conf_het = scout.project(multi_X[:50], Z_hetero, multi_X, k_neighbors=15)
    _, conf_hom = scout.project(multi_X[:50], Z_homog, multi_X, k_neighbors=15)
    assert conf_het.mean() < conf_hom.mean(), "异质区置信度应更低 (AC-1)"


def test_project_confidence_mutation():
    """mutation test: project 必须区分异质/同质区.

    正确实现: 异质邻域 std 大 → 置信度低 (AC-1).
    Mutation (固定常数置信, 不看邻域): 异质/同质置信相同, 违反 AC-1.
    """
    rng = np.random.default_rng(1)
    multi_X = rng.normal(size=(200, 10))
    Z_hetero = rng.normal(size=(200, 5))
    Z_homog = np.zeros((200, 5)); Z_homog[:, 0] = 1.0

    # --- 正确实现 ---
    _, conf_het = scout.project(multi_X[:50], Z_hetero, multi_X, k_neighbors=15)
    _, conf_hom = scout.project(multi_X[:50], Z_homog, multi_X, k_neighbors=15)

    # --- Mutation: 固定置信 (常数, 不依赖邻域一致性) ---
    def project_fixed_conf(spatial_X, Z_pair, multi_X, k_neighbors=15, const=0.5):
        return np.full(spatial_X.shape[0], const)
    conf_het_m = project_fixed_conf(multi_X[:50], Z_hetero, multi_X)
    conf_hom_m = project_fixed_conf(multi_X[:50], Z_homog, multi_X)

    # AC-1 断言函数
    def satisfies_ac1(ch, cm):
        return ch.mean() < cm.mean()

    assert satisfies_ac1(conf_het, conf_hom), "正确 project 应满足 AC-1 (异质<同质)"
    assert not satisfies_ac1(conf_het_m, conf_hom_m), (
        "固定常数置信的 mutation 不应满足 AC-1 —— 否则测试不能区分 '区分邻域' 与 '常数'")


# ---------- Task 3: impute ----------
def test_impute_recovers_atac():   # 保留原基本正确性
    rng = np.random.default_rng(2)
    spatial_Z = rng.normal(size=(100, 5))
    W_atac = rng.normal(size=(30, 5))
    atac_true = spatial_Z @ W_atac.T
    atac_hat = scout.impute(spatial_Z, W_atac)
    assert np.allclose(atac_hat, atac_true, atol=1e-5), "impute 应精确恢复 (线性映射)"


def test_impute_mutation():
    """mutation test: impute 必须用 spatial_Z @ W_atac.T, 不能退化.

    正确实现: 重构 ≈ truth.
    Mutation (全零 / 全局均值广播): 重构远离 truth.
    """
    rng = np.random.default_rng(2)
    spatial_Z = rng.normal(size=(100, 5))
    W_atac = rng.normal(size=(30, 5))
    atac_true = spatial_Z @ W_atac.T

    # --- 正确实现 ---
    atac_correct = scout.impute(spatial_Z, W_atac)
    err_correct = np.sqrt(((atac_correct - atac_true) ** 2).mean())

    # --- Mutation: 全零 ---
    def impute_zero(spatial_Z, W_atac):
        return np.zeros((spatial_Z.shape[0], W_atac.shape[0]))
    # --- Mutation: 全局均值广播 ---
    def impute_mean(spatial_Z, W_atac):
        m = atac_true.mean()   # 即使偷看 truth 的均值, 仍无法重构结构
        return np.full((spatial_Z.shape[0], W_atac.shape[0]), m)

    err_zero = np.sqrt(((impute_zero(spatial_Z, W_atac) - atac_true) ** 2).mean())
    err_mean = np.sqrt(((impute_mean(spatial_Z, W_atac) - atac_true) ** 2).mean())

    def close_enough(err):
        return err < 1e-4

    assert close_enough(err_correct), (
        f"正确 impute 误差应极小 (<1e-4): {err_correct:.3e}")
    assert not close_enough(err_zero), (
        f"全零 mutation 误差 ({err_zero:.3f}) 应远大于阈值 —— 否则测试不能区分重构与退化")
    assert not close_enough(err_mean), (
        f"均值广播 mutation 误差 ({err_mean:.3f}) 应远大于阈值 —— 否则测试不能区分重构与退化")
    # 进一步: mutation 误差应比正确实现大至少一个量级 (结构信息丢失)
    assert err_zero > 10 * max(err_correct, 1e-12)
    assert err_mean > 10 * max(err_correct, 1e-12)


# ---------- Task 4: downsample ----------
def test_downsample_drift_grows_with_sparsity():   # 保留原基本正确性
    rows = scout.downsample_curve(reads_list=(100, 50, 20, 10, 5))
    drifts = [r[1] for r in rows]
    assert drifts[0] < drifts[-1], f"downsample→稀疏, drift 应增大 (AC-2): {drifts}"


def test_downsample_mutation():
    """mutation test: downsample 必须读数越少 drift 越大 (AC-2).

    正确实现: reads 100→5 时 drift 单调 (大致) 增大.
    Mutation (drift 不随 reads 变化, 固定常数): 不满足 AC-2.
    """
    rows = scout.downsample_curve(reads_list=(100, 50, 20, 10, 5))
    drifts_correct = [r[1] for r in rows]

    # --- Mutation: drift 与 reads 无关 (固定常数) ---
    drifts_mut = [1.0] * len(drifts_correct)

    def satisfies_ac2(drifts):
        # reads 多 → drift 小; reads 少 → drift 大
        return drifts[0] < drifts[-1]

    assert satisfies_ac2(drifts_correct), (
        f"正确 downsample 应满足 AC-2 (reads 少 drift 大): {drifts_correct}")
    assert not satisfies_ac2(drifts_mut), (
        "固定 drift 的 mutation 不应满足 AC-2 —— 否则测试不能区分 '读数敏感' 与 '常数'")
    # 进一步: 正确实现首尾 drift 应有实质差距 (不是噪声)
    assert drifts_correct[-1] > drifts_correct[0] * 1.5, (
        f"AC-2 应有实质效应 (drift 末/首 >1.5x): {drifts_correct}")
