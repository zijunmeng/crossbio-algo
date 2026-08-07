# SCOUT — Tasks (bite-sized TDD, v0.2.1)

**Goal**: SCOUT MVP — paired-projection spatial multimodal integration (PLS + entropic OT), infer spatial ATAC.
**Architecture**: paired factors (PLS) → spatial projection (OT) → ATAC imputation (ONE cross-modal `B_atac`).
**Tech stack**: numpy (SVD, lstsq, Sinkhorn); CPU-only. Run: `cd examples/scout && PYTHONPATH=. python -m pytest test_scout.py -v`.

---

### Task 1: `scout.pair_map` — paired latent via PLS (centered cross-covariance SVD)
**Files:** `examples/scout/scout.py` (`pair_map`, `ScoutFit`), `test_scout.py`
- [ ] **Step 1 — failing test**: `test_pair_map_recovers_shared_subspace` (PLS latent recovers the shared Z subspace, alignment > 0.8) + `test_pair_map_is_pls_not_uncentered_MUTATION` (robust to a +50 offset because it CENTERS) + `test_pair_map_cross_modal_prediction_MUTATION` (the ONE `B_atac` reconstructs ATAC > 0.5; random `B_atac` ≈ 0).
- [ ] **Step 2 — run, verify FAIL** (ModuleNotFoundError / assertion).
- [ ] **Step 3 — implement**: center X_rna/X_atac; `C=XrᵀXa/n`; `np.linalg.svd`; truncate k; `Z=XrU`; `B_atac=np.linalg.lstsq(Z, Xa)`. Return `ScoutFit`.
- [ ] **Step 4 — run, verify PASS**. [ ] **Step 5 — commit**.

### Task 2: `scout.project` — spatial RNA → paired latent via entropic OT + confidence
**Files:** `scout.py` (`_sqdist`, `_sinkhorn`, `project`), `test_scout.py`
- [ ] **Step 1 — failing test**: `test_ot_projects_inmanifold_end_to_end_MUTATION` (in-manifold → imputed ATAC correlates with truth > 0.5; random transport worse) + `test_low_confidence_low_reads_AC2` (reads<threshold flagged) + `test_low_confidence_out_of_manifold_AC1` (out-of-manifold flagged).
- [ ] **Step 2 — run, FAIL**. [ ] **Step 3 — implement**: `phi_s=(X_s−mean_rna)U`; detect out-of-manifold (nearest paired > 3× cloud spacing); Sinkhorn on in-manifold rows; barycentric `spatial_Z=(P@Z)/rowsum(P)`; entropy→confidence; `low_confidence = reads<thr | far | high-entropy`.
- [ ] **Step 4 — PASS**. [ ] **Step 5 — commit**.

### Task 3: `scout.impute` — the ONE cross-modal map (P0-4)
**Files:** `scout.py` (`impute`), `test_scout.py`
- [ ] **Step 1 — failing test**: `test_impute_uses_one_B_atac` (`impute(Zs, fit) == Zs @ fit.B_atac`).
- [ ] **Step 2 — FAIL**. [ ] **Step 3 — implement**: `return spatial_Z @ fit.B_atac`.
- [ ] **Step 4 — PASS**. [ ] **Step 5 — commit**.

### Task 4: simulation + benchmark + downsample failure curve
**Files:** `scout.py` (`simulate`, `_perpeak_corr`, `benchmark`, `downsample_curve`), `test_scout.py`
- [ ] **Step 1 — failing test**: `test_benchmark_beats_naive_AC4` (scout > mean-impute > zero) + `test_downsample_drift_and_lowconfidence_grow_AC2` (drift & low_confidence fraction grow as reads drop).
- [ ] **Step 2 — FAIL**. [ ] **Step 3 — implement**: DGP (shared Z, in/out-manifold spatial, pairing_strength, Poisson downsample); per-peak corr; benchmark vs mean/zero; downsample curve.
- [ ] **Step 4 — PASS**. [ ] **Step 5 — commit**.

### Task 5: artifact chain (machine-checkable handoff)
**Files:** `examples/scout/artifacts/{data-audit,design,spec,code}.json`
- [ ] Build the 4 stamped artifacts (estimand continuous, every fb traced by an AC, notation consistent, pseudocode→code).
- [ ] `crossbio validate-chain examples/scout/artifacts` → **VALID, 0 findings**.

---

## Self-review
- ✅ Each module has a typed interface + a mutation-discriminating test.
- ✅ Every `failure_boundary` (fb1–fb4) has a matching acceptance criterion (no orphans — also machine-checked in `artifacts/spec.json`).
- ✅ P0-4: one `B_atac` used by `impute` AND the reconstruction check (`test_impute_uses_one_B_atac`, `test_pair_map_cross_modal_prediction_MUTATION`).
- ✅ No placeholders; no over-claimed ACs (scaling & SCGLUE/ISON moved to Roadmap).
