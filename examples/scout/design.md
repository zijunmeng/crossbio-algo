# SCOUT — Design

## Module Breakdown (typed interfaces)
| 模块 | 职责 | 输入 | 输出 |
|---|---|---|---|
| `scout.pair_map` | scMultiome 学 RNA-ATAC 配对潜在 | `multi_adata` (AnnData, `.X`=RNA, `.obsm['ATAC']`) | `Z_pair` (np.float32 [n_cells,k]), `W_rna`, `W_atac` |
| `scout.project` | 空间 RNA → 投射到配对潜在 + 置信度 | `spatial_adata` (`.X`=RNA, `.obsm['spatial']`), `Z_pair`, `multi_adata.X` | `spatial_Z` ([n_spatial,k]), `project_confidence` ([n_spatial]) |
| `scout.impute` | 推断空间 ATAC + 联合状态 | `spatial_Z`, `W_atac` | `spatial_adata.obsm['ATAC_imputed']` ([n_spatial, n_peaks]) |
| `scout.spatial` | 空间可视化 | `spatial_adata`, `ATAC_imputed` | Moran's I, 空间图 |
| `scout.sim` | semi-synthetic + downsample + benchmark | params | truth + metrics |

## Data Flow
```
multi_adata.X(RNA) + multi_adata.obsm['ATAC']
  → pair_map → Z_pair + W_rna/W_atac
  → project (← spatial_adata.X) → spatial_Z + project_confidence
  → impute → spatial_adata.obsm['ATAC_imputed']
  → spatial (squidpy)
```
字段：`spatial_adata.obsm['spatial']`=xy; `.obs['project_confidence']`; `.obs['low_confidence']`; `.obsm['ATAC_imputed']`; `.uns['scout_metrics']`.

## Pseudocode (API-call level — no high-level verbs)

### scout.pair_map.fit (配对潜在, CCA-via-SVD)
```python
import numpy as np
def fit(multi_adata, k=30):
    X_rna = np.asarray(multi_adata.X, dtype=float)        # [n, g_rna]
    X_atac = np.asarray(multi_adata.obsm['ATAC'], dtype=float)  # [n, g_atac]
    C = (X_rna.T @ X_atac) / X_rna.shape[0]               # cross-covariance [g_rna, g_atac]
    U, S, Vt = np.linalg.svd(C, full_matrices=False)      # C = U @ diag(S) @ Vt
    U, Vt = U[:, :k], Vt[:k, :]                           # 截断到 top-k
    W_rna = U                                             # RNA 侧映射 [g_rna, k]
    W_atac = Vt.T                                         # ATAC 侧映射 [g_atac, k]
    Z_pair = X_rna @ W_rna                                # 配对潜在 [n, k]
    return Z_pair, W_rna, W_atac
```

### scout.project.fit (空间投射 + 置信度, AC-1)
```python
from sklearn.neighbors import NearestNeighbors
def project(spatial_adata, Z_pair, multi_X, k_neighbors=15):
    nn = NearestNeighbors(n_neighbors=k_neighbors).fit(multi_X)
    dist, idx = nn.kneighbors(spatial_adata.X)
    weights = np.exp(-dist / dist.mean(axis=1, keepdims=True))   # 软加权
    spatial_Z = np.einsum('nk,nkd->nd', weights, Z_pair[idx]) / weights.sum(1, keepdims=True)
    # 置信度 = 邻域 Z 的一致性 (异质→低, AC-1)
    neigh_std = Z_pair[idx].std(axis=1).mean(axis=1)
    project_confidence = 1.0 / (1.0 + neigh_std)
    return spatial_Z, project_confidence
```

### scout.impute
```python
def impute(spatial_Z, W_atac):
    return spatial_Z @ W_atac.T                 # [n_spatial,k] @ [k,g_atac] → ATAC
```

## Dependencies
`scanpy>=1.10`, `squidpy>=1.4`, `scikit-learn>=1.4` (NearestNeighbors), `numpy>=1.26` (`np.linalg.svd` for pair_map), `scipy>=1.11`, `anndata>=0.10`, `POT>=0.9` (sinkhorn, 可选 OT 精化).

## Engineering Constraints
全 CPU (无 GPU, 禁 torch 训练); mini-batch OT (batch=4096) 扛百万像素; scanpy/squidpy 生态; `random_state=0` 固定可复现; 记录 db/数据版本。

## Publication Roadmap
- **MVP scope**: pair_map + project + impute 在 semi-synthetic 跑通 (核心创新 + 失效②③验证)。
- **Engineering gap**: 真 scMultiome 接驳 / OT sinkhorn 调参 / CI+Docker (3 人天, P0)。
- **Experiment gap**: benchmark vs SCGLUE/ISON / downsample 失效曲线 / 真实胎脑 Stereo-seq (5 人天, P0)。
- **Writing gap**: intro (vs SCGLUE unpaired / SpatialGlue GPU) / methods (配对-投射数学) / results (适用边界图) (4 人天, P1)。
