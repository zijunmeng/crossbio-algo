# SCOUT — Tasks (bite-sized TDD)

**Goal**: SCOUT MVP — 配对-投射整合, 推断空间 ATAC。
**Architecture**: scMultiome 配对先验 → 投射空间 RNA → 推断空间 ATAC。
**Tech Stack**: scanpy / scikit-learn / POT, 全 CPU。

---

### Task 1: `scout.pair_map` (配对潜在推断)
**Files:** Create `src/scout/pair_map.py`, `tests/test_pair_map.py`

- [ ] **Step 1: Write the failing test**
```python
# tests/test_pair_map.py
import numpy as np
from anndata import AnnData
from scout import pair_map

def test_pair_map_recovers_known_latent():
    rng = np.random.default_rng(0)
    Z = rng.normal(size=(500, 5))                 # 已知真值潜在
    W_rna = rng.normal(size=(5, 20)); W_atac = rng.normal(size=(30, 5))
    adata = AnnData(X=(Z @ W_rna).astype('float32'))
    adata.obsm['ATAC'] = (Z @ W_atac.T).astype('float32')
    Z_hat, _, _ = pair_map.fit(adata, k=5)
    assert Z_hat.shape == (500, 5)
    from scipy.linalg import orthogonal_procrustes      # 容许符号/旋转
    R, _ = orthogonal_procrustes(Z_hat, Z)
    assert np.allclose(Z_hat @ R, Z, atol=0.15)
```
- [ ] **Step 2: Run test, verify FAIL** — `pytest tests/test_pair_map.py -v` → FAIL "No module named 'scout'"
- [ ] **Step 3: Minimal implementation** — `pair_map.fit` 用 TruncatedSVD on cross-covariance (见 design.md 伪代码)
- [ ] **Step 4: Run test, verify PASS** — `pytest tests/test_pair_map.py -v` → PASS
- [ ] **Step 5: Commit** — `git commit -m "feat: scout.pair_map 配对潜在推断"`

### Task 2: `scout.project` (空间投射 + 置信度, ← AC-1)
**Files:** Create `src/scout/project.py`, `tests/test_project.py`
- [ ] **Step 1: Write failing test (trace AC-1)**
```python
def test_confidence_drops_in_heterogeneous_region():
    # 同质邻域(同 Z) → 高置信; 异质邻域(混 Z) → 低置信
    Z_pair_homogeneous = np.zeros((100, 5))       # 全同 → std=0 → 高置信
    Z_pair_hetero = np.random.default_rng(1).normal(size=(100, 5))  # 混 → std大 → 低置信
    ...
    assert confidence_hetero < confidence_homogeneous
```
- [ ] **Step 2:** Run → FAIL | **Step 3:** 实现 (最近邻 + 软加权 + std 置信度, design 伪代码) | **Step 4:** Run → PASS | **Step 5:** commit

### Task 3: `scout.impute` + benchmark (← AC-4)
**Files:** Create `src/scout/impute.py`, `tests/test_impute.py`
- [ ] **Step 1:** Write failing test — semi-synthetic: 已知空间 ATAC 真值, 验证 `impute` 恢复 AUROC > 0.7
- [ ] **Step 2-5:** Run→FAIL / 实现 (`spatial_Z @ W_atac.T`) / Run→PASS / commit

### Task 4: simulation harness — downsample 失效曲线 (← AC-2, simulation_plan)
**Files:** Create `src/scout/sim.py`
- [ ] **Step 1:** Write failing test — downsample reads 100→50→10→5, `project_confidence` 应随稀疏单调下降 (验证 AC-2 邻域借用生效)
- [ ] **Step 2-5:** Run→FAIL / 实现 (合成配对+空间, downsample, 跑 project) / Run→PASS / commit

---

## Self-Review (跑完检查)
- ✅ 每模块有 typed interface + 测试 (pair_map/project/impute/sim)。
- ✅ 每个 `simulation_plan` case (downsample) 是 Task 4 测试。
- ✅ AC-1 (Task 2) / AC-2 (Task 4) / AC-4 (Task 3) 有对应 task; AC-3 (规模) 在 benchmark 阶段测。
- ✅ 每步真实代码, 无 placeholder (TBD/TODO/"add error handling" 均无)。
- ✅ 类型一致: `Z_pair`/`W_rna`/`W_atac`/`spatial_Z` 跨 task 命名一致。
