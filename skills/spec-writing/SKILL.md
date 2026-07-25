---
name: spec-writing
description: Use when an algorithm-design 6-field output exists and the next step is turning it into engineering specs before writing code. Use when the user says "帮我写 spec / PRD / 实现方案 / 技术文档 / requirements / design / tasks" or needs requirements.md / design.md / tasks.md artifacts. Use when bridging a research-idea (hypothesis/novelty) into executable engineering specs.
---

# Spec Writing

## Overview

An `algorithm-design` output is **research-idea language** (hypothesis, novelty, mechanism). Code needs **engineering language** (modules, interfaces, data structures, executable pseudocode, tests, acceptance). Designs die in that translation. This skill is the translation layer.

It borrows two mature paradigms rather than inventing its own 8-part stew:

- **Kiro spec-driven, three-phase** — produce three sequential markdown artifacts: **Requirements → Design → Tasks**. Write each fully before the next. Human-in-the-loop at each phase (pause for review between artifacts).
- **superpowers writing-plans bite-sized TDD** — Tasks are micro-steps (2–5 min each): write failing test → run/see fail → minimal implementation → run/see pass → commit. Real code in every step, no placeholders.

Position in the loop:
```
algorithm-design (6 fields)  →  spec-writing (this skill: 3 artifacts)  →  code → publish
```

## Input

The 6 fields from `~/.claude/skills/algorithm-design/SKILL.md`:
`mathematical_abstraction` / `cross_domain_inspiration` / `proposed_algorithm` / `failure_boundary` / `simulation_plan` / `novelty_basis`.

## Output — three artifacts, all mandatory, sequential

Write each one fully and pause for review before starting the next. Never collapse them into a single doc. Never start Tasks before Design is approved, or Design before Requirements.

### Artifact 1 — `requirements.md` (WHAT to build)
- **User need** — one paragraph: who, what problem, why now.
- **Goals** — carried from `algorithm-design`'s `proposed_algorithm` + `mathematical_abstraction`; state as measurable outcomes, not as "implement the algorithm."
- **Acceptance criteria** — write each in **EARS notation** (`WHEN <condition> THE SYSTEM SHALL <response>`; `IF <condition> THEN THE SYSTEM SHALL ...`). **Every criterion MUST trace (tag with `← failure_boundary`) to a failure_boundary**. Benchmark pass lines stated numerically.
- **Out of scope** — explicitly list what the MVP does NOT do (to prevent scope creep).
- Trace section: a small table mapping each `failure_boundary` → the criterion ID that validates it. None may be untraced.

### Artifact 2 — `design.md` (HOW to build)
- **Module breakdown** — name each module, its single responsibility, and a typed interface: inputs (name, type, AnnData field), outputs (name, type, AnnData field). No module without an interface.
- **Data flow** — which AnnData/adata fields are read/written (`adata.X`, `adata.obsm['X_pca']`, `adata.obsp['connectivities']`…); matrix shapes; file formats (`.h5ad`, `.bam`, `.parquet`); how bytes move between modules.
- **Executable pseudocode per module** — **API-call level**, not high-level verbs. `sc.pp.neighbors(n_neighbors=15); sc.tl.leiden(resolution=1.0)` is correct. "做聚类" / "do clustering" / "process the data" is FORBID. One pseudocode block per module.
- **Dependencies** — concrete library + version: e.g. `scanpy>=1.10`, `squidpy>=1.4`, `scvi-tools>=1.2`, `pygsp>=2.0.4`, TargetScan / miRBase DB release. No bare "use scanpy."
- **Engineering constraints** — **stated under the user's actual compute environment, NOT assumed**: ask for and record GPU availability, data scale (single-cell? million-cell spatial?), the tool ecosystem they're in, and memory/time budget. The spec must stay within those stated constraints (e.g. if CPU-only, note the mini-batch / approximation strategy; if a specific stack is required, stay inside it). Do NOT hardcode "no GPU" or a particular ecosystem as a universal default.
- **Publication Roadmap** (mandatory, keep verbatim from the prior skill) — be EXPLICIT that the spec covers an MVP, and what is still needed to publish. MUST contain:
  - **MVP scope** — what is already validated (core novelty + which `failure_boundary`).
  - **Engineering gap** — real DBs / real method (e.g. LDA not proxy) / scalability / CI + container — each with **effort (person-days) + priority (P0/P1/P2)**.
  - **Experiment gap** — fair benchmark vs named competitors / full validation of each `failure_boundary` / real datasets.
  - **Writing gap** — intro (competitor positioning) / methods / results (applicability-boundary figure) / discussion (limitations).
  - Purpose: the user leaves knowing "where I am / what's missing / what to do next" — **NEVER mistaking MVP for publishable**.

### Artifact 3 — `tasks.md` (bite-sized TDD plan)
Follow superpowers writing-plans granularity exactly.

**Plan header** — goal, 2–3 sentence architecture, tech stack.

**Each task** = one component, structured:
```
### Task N: [Component Name]
**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`
- [ ] Step 1: Write the failing test        (real test code, mapped 1:1 to a design module + a simulation_plan case)
- [ ] Step 2: Run test, verify it FAILS     (exact command + expected failure message)
- [ ] Step 3: Minimal implementation        (real code from the design's pseudocode)
- [ ] Step 4: Run test, verify it PASSES    (exact command)
- [ ] Step 5: Commit                         (exact git command, conventional-commit message)
```
- Every `simulation_plan` case from `algorithm-design` MUST appear as a test in some task.
- Run **Self-review** after writing all tasks: skim every requirement / module / simulation case — can you point to a task that implements it? List gaps and fill them. Scan for placeholder red flags. Check type/signature consistency across tasks.

## Strong-constraint checklist (the spec set is incomplete if any fail)
- [ ] All three artifacts present (`requirements.md`, `design.md`, `tasks.md`), written sequentially, reviewed between phases.
- [ ] `requirements.md`: every acceptance criterion in EARS notation; **every `failure_boundary` has a matching criterion**; trace table complete.
- [ ] `design.md`: every module has a typed interface; pseudocode at API-call level (no high-level verbs); dependencies version-pinned; Engineering constraints reflect the **user's stated** environment (not an assumed default); Publication Roadmap present (MVP scope + 3 gaps with effort + priority).
- [ ] `tasks.md`: bite-sized 5-step TDD tasks; every step has **real code** (no placeholders); every `simulation_plan` case is a test; Self-review done.
- [ ] No FORBID phrases anywhere: "做一个X", "用合适的参数", "做聚类", "用合适的模型", "TBD", "TODO", "implement later", "add error handling", "handle edge cases", "use a suitable method".

## References
- `~/.claude/skills/algorithm-design/SKILL.md` — the 6-field input this skill consumes.
- Kiro spec-driven development — Requirements → Design → Tasks three-phase workflow (kiro.dev/docs/specs).
- superpowers:writing-plans — bite-sized TDD task granularity, no-placeholders rule, self-review.

## Example — three-artifact excerpt (graph-wavelet imputation)

From `algorithm-design`: `proposed_algorithm`=graph-wavelet thresholded imputation; `failure_boundary`=degrades at per-cell reads<5 and when dropout couples to true expression; `simulation_plan`=known smooth signal + injected zeros, sweep sparsity & coupling.

**requirements.md (excerpt):**
```markdown
### AC-2 ← failure_boundary (reads<5)
- WHEN per-cell total reads < 5 THE SYSTEM SHALL set adata.obs['impute_confidence']=0
  for those cells and leave their values unchanged.
- WHEN a cell's adata.obs['impute_confidence']==0 THEN THE SYSTEM SHALL exclude it
  from all downstream neighborhood-graph construction.

### AC-3 ← failure_boundary (dropout-expression coupling)
- WHEN dropout-expression coupling > 0.7 THE SYSTEM SHALL emit
  adata.uns['coupling_warning']=True.
- IF coupling ≤ 0.5 THEN THE SYSTEM SHALL achieve recovery MSE < MAGIC baseline
  AND < SAVER baseline on the simulation sweep.

| failure_boundary          | validates |
|---------------------------|-----------|
| reads<5                   | AC-2      |
| dropout-expression coupling| AC-3      |
```

**design.md (one module excerpt):**
```markdown
### Module: wavelet_band_filter
Responsibility: graph-wavelet decompose per-gene signal; zero bands above cutoff tau.
Interface:
  in : adata (AnnData n_obs×n_vars), adata.obsp['connectivities'] (sparse n_obs×n_obs), tau (float, default 0.5)
  out: adata.layers['wavelet_filtered'] (np.float32, n_obs×n_vars)
Dependencies: pygsp>=2.0.4; scanpy>=1.10; numpy>=1.26
Pseudocode:
  G = pg.graphs.Graph(adata.obsp['connectivities']); G.compute_fourier_basis()
  for g in range(n_vars):
      s_hat = G.U.T @ adata.X[:, g]              # graph-Fourier
      s_hat[int(G.N*tau):] = 0                   # keep low-graph-freq
      adata.layers['wavelet_filtered'][:, g] = G.U @ s_hat
Constraints: CPU only; ≤16 GB at 50k cells via gene mini-batch (batch=2000).

Publication Roadmap:
  MVP scope: wavelet_band_filter on synthetic (core novelty + failure reads<5 validated).
  Engineering gap: real pygsp benchmark / gene-mini-batch memory tuning / Docker+CI (3d, P0).
  Experiment gap: benchmark vs MAGIC/SAVER/DCA on PBMC+pancreas / coupling-sweep figure / real tissue (5d, P0).
  Writing gap: intro (vs KNN/diffusion) / methods (graph-Fourier math) / results (applicability-boundary fig) (4d, P1).
```

**tasks.md (one task excerpt):**
````markdown
### Task 3: wavelet_band_filter
**Files:**
- Create: `impute/wavelet.py`
- Test: `tests/test_wavelet.py`

- [ ] **Step 1: Write failing test**
```python
import numpy as np, scanpy as sc, pygsp as pg
from impute.wavelet import wavelet_band_filter

def test_ring_recovers_bandlimited():
    adata = sc.datasets.pbmc3k()[:200].copy()
    # ring graph adjacency as connectivities
    G = pg.graphs.Ring(200); adata.obsp['connectivities'] = G.W
    sig = np.cos(2*np.pi*np.arange(200)/200)            # band-limited signal
    adata.X = sig.reshape(-1,1).astype(np.float32)
    out = wavelet_band_filter(adata, tau=0.5)
    assert out.layers['wavelet_filtered'].shape == adata.X.shape
    assert np.isfinite(out.layers['wavelet_filtered']).all()
    assert np.mean((out.layers['wavelet_filtered'].ravel()-sig)**2) < 1e-6
```

- [ ] **Step 2: Run — verify FAIL**
Run: `pytest tests/test_wavelet.py::test_ring_recovers_bandlimited -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'impute.wavelet'`

- [ ] **Step 3: Minimal implementation** (`impute/wavelet.py`)
```python
import numpy as np, pygsp as pg

def wavelet_band_filter(adata, tau=0.5, gene_batch=2000):
    G = pg.graphs.Graph(adata.obsp['connectivities'])
    G.compute_fourier_basis()
    X = np.asarray(adata.X, dtype=np.float32)
    out = np.empty_like(X)
    for s in range(0, X.shape[1], gene_batch):
        block = X[:, s:s+gene_batch]
        for g in range(block.shape[1]):
            s_hat = G.U.T @ block[:, g]
            s_hat[int(G.N*tau):] = 0
            out[:, s+g] = G.U @ s_hat
    adata.layers['wavelet_filtered'] = out
    return adata
```

- [ ] **Step 4: Run — verify PASS**
Run: `pytest tests/test_wavelet.py::test_ring_recovers_bandlimited -v`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add impute/wavelet.py tests/test_wavelet.py
git commit -m "feat(wavelet): band-limited graph-Fourier filter module"
```
````
