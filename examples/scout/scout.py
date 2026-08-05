"""SCOUT — 配对-投射整合 (spatial RNA + paired multiome → spatial ATAC). MVP, 全 CPU.
Task1 pair_map / Task2 project / Task3 impute / Task4 sim. 正式版按 tasks.md 分包。"""
import numpy as np
from sklearn.neighbors import NearestNeighbors


# ---------- Task 1: pair_map (配对潜在, CCA-via-SVD) ----------
def pair_map(multi_adata, k=30):
    """学 RNA-ATAC 配对潜在 (CCA-via-SVD on the cross-covariance).

    返回 Z_pair[n,k], W_rna[g_rna,k], W_atac[g_atac,k], svals[k].
    svals 是 cross-covariance 的奇异值；cross-modal ATAC 可由
    (X_rna @ W_rna) @ diag(svals) @ W_atac.T 重构 (低秩近似).
    """
    X_rna = np.asarray(multi_adata.X, dtype=float)
    X_atac = np.asarray(multi_adata.obsm['ATAC'], dtype=float)
    C = (X_rna.T @ X_atac) / X_rna.shape[0]          # cross-covariance
    U, S, Vt = np.linalg.svd(C, full_matrices=False)
    U, S, Vt = U[:, :k], S[:k], Vt[:k, :]
    Z_pair = X_rna @ U                                # [n, k]
    return Z_pair, U, Vt.T, S                         # W_rna=U, W_atac=Vt.T, svals=S


# ---------- Task 2: project (空间投射 + 置信度, AC-1) ----------
def project(spatial_X, Z_pair, multi_X, k_neighbors=15):
    """空间 RNA → 投射到配对潜在 + 置信度 (异质邻域→低置信)."""
    k = min(k_neighbors, Z_pair.shape[0])
    nn = NearestNeighbors(n_neighbors=k).fit(multi_X)
    dist, idx = nn.kneighbors(spatial_X)
    w = np.exp(-dist / np.maximum(dist.mean(axis=1, keepdims=True), 1e-9))
    w = w / w.sum(axis=1, keepdims=True)
    spatial_Z = np.einsum('nk,nkd->nd', w, Z_pair[idx])
    neigh_std = Z_pair[idx].std(axis=1).mean(axis=1)  # 邻域 Z 一致性
    confidence = 1.0 / (1.0 + neigh_std)
    return spatial_Z, confidence


# ---------- Task 3: impute ----------
def impute(spatial_Z, W_atac):
    """推断空间 ATAC: [n,k] @ [k,g_atac]."""
    return spatial_Z @ W_atac.T


# ---------- Task 4: sim (downsample 失效曲线, AC-2) ----------
def downsample_curve(n_multi=300, n_spatial=200, k=5, g_rna=20, g_atac=30,
                     reads_list=(100, 50, 20, 10, 5), seed=0):
    """合成配对+空间, downsample spatial RNA, 测投射 drift vs 全reads参考 (AC-2)."""
    rng = np.random.default_rng(seed)
    Z_multi = rng.normal(size=(n_multi, k))
    Z_space = rng.normal(size=(n_spatial, k))
    W_rna = rng.normal(size=(k, g_rna))
    W_atac = rng.normal(size=(g_atac, k))

    multi = _AD(np.clip(Z_multi @ W_rna, 0, None).astype('float32'),
                {'ATAC': np.clip(Z_multi @ W_atac.T, 0, None).astype('float32')})
    Z_pair, _, _, _ = pair_map(multi, k=k)

    X_space_ref = np.clip(Z_space @ W_rna, 0, None)             # 全 reads 参考
    spatial_Z_ref, _ = project(X_space_ref, Z_pair, np.asarray(multi.X))

    rows = []
    for reads in reads_list:
        lam = X_space_ref / max(X_space_ref.mean(), 1e-9) * reads
        X_down = rng.poisson(lam).astype(float)                 # downsample (Poisson)
        X_down *= np.asarray(multi.X).mean() / max(X_down.mean(), 1e-9)   # 固定尺度 (AC-2 关键)
        spatial_Z, _ = project(X_down, Z_pair, np.asarray(multi.X))
        drift = float(np.sqrt(((spatial_Z - spatial_Z_ref) ** 2).mean()))
        rows.append((reads, drift))
    return rows


class _AD:                       # 最小 AnnData 替身 (MVP, 避免 anndata 依赖摩擦)
    def __init__(self, X, obsm):
        self.X = X
        self.obsm = obsm
