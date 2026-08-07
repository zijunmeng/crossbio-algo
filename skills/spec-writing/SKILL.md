---
name: spec-writing
description: Use when an algorithm-design formal-method-contract output exists and the next step is turning it into engineering specs before writing code. Use when the user says "帮我写 spec / PRD / 实现方案 / 技术文档 / requirements / design / tasks" or needs requirements.md / design.md / tasks.md artifacts. Use when bridging a research-idea (hypothesis/novelty) into executable engineering specs.
---

# Spec Writing

## Overview

An `algorithm-design` output is **research-idea language** (hypothesis, novelty, mechanism). Code needs **engineering language** (modules, interfaces, data structures, executable pseudocode, tests, acceptance). Designs die in that translation. This skill is the translation layer.

It borrows two mature paradigms rather than inventing its own 8-part stew:

- **Kiro spec-driven, three-phase** — produce three sequential markdown artifacts: **Requirements → Design → Tasks**. Write each fully before the next. Human-in-the-loop at each phase (pause for review between artifacts).
- **superpowers writing-plans bite-sized TDD** — Tasks are micro-steps (2–5 min each): write failing test → run/see fail → minimal implementation → run/see pass → commit. Real code in every step, no placeholders.

Position in the loop:
```
algorithm-design (formal method contract)  →  spec-writing (this skill: 3 artifacts)  →  code → publish
```

## Input

spec-writing consumes the design's **formal method contract** (canonical schema: `schemas/stage-schemas.json`). The load-bearing fields for the spec translation:
- `proposed_algorithm` → module breakdown
- `failure_boundaries` → acceptance criteria (each `traces_to` a boundary)
- `notation_and_shapes` → module interfaces (shapes must match — cross-stage rule 3)
- `simulation_dgp` → test cases (every DGP regime becomes a test)
- `optimization_or_inference` / `complexity` → engineering constraints
- `novelty_or_utility_basis` → Publication Roadmap

## Output — three artifacts, all mandatory, sequential

Write each one fully and pause for review before starting the next. Never collapse them into a single doc. Never start Tasks before Design is approved, or Design before Requirements.

### Artifact 1 — `requirements.md` (WHAT to build)
- **User need** — one paragraph: who, what problem, why now.
- **Goals** — carried from `algorithm-design`'s `proposed_algorithm` + `mathematical_abstraction`; state as measurable outcomes, not as "implement the algorithm."
- **Acceptance criteria** — write each in **EARS notation** (`WHEN <condition> THE SYSTEM SHALL <response>`; `IF <condition> THEN THE SYSTEM SHALL ...`). **Every criterion MUST trace (tag with `← failure_boundary`) to a failure_boundary**. Benchmark pass lines stated numerically.
- **Out of scope** — explicitly list what the MVP does NOT do (to prevent scope creep).
- Trace section: a small table mapping each `failure_boundary` → the criterion ID that validates it. None may be untraced.

### Artifact 2 — `design.md` (HOW to build)
- **Module breakdown** — name each module, its single responsibility, and a typed interface: inputs (name, type, domain data-model field), outputs (name, type, domain data-model field). No module without an interface. The data-model field type follows the **Domain data-model adapter** (see that section) — NOT assumed to be AnnData.
- **Data flow** — which data-model fields / files are read/written, in the chosen domain's vocabulary (e.g. AnnData: `adata.X`, `adata.obsm['X_pca']`; bulk: `expr_matrix.csv` + `samples.tsv`; genomics: `aligned.bam` → `variants.vcf`; proteomics: `mzML` → `peptides×samples` quant matrix); matrix/array shapes; file formats; how bytes move between modules.
- **Executable pseudocode per module** — **API-call level**, not high-level verbs. `sc.pp.neighbors(n_neighbors=15); sc.tl.leiden(resolution=1.0)` is correct. "做聚类" / "do clustering" / "process the data" is FORBID. One pseudocode block per module. Pseudocode uses the chosen domain's libraries, not scanpy by default.
- **Dependencies** — concrete library + version: e.g. `scanpy>=1.10`, `squidpy>=1.4`, `scvi-tools>=1.2`, `pygsp>=2.0.4`, TargetScan / miRBase DB release — OR the domain-equivalent (`pysam>=0.22` for genomics, `pyteomics>=2023.1` for proteomics, `pyopenms` for mass-spec, `nibabel`/`zarr` for imaging, `ete3`/`dendropy` for phylogenetics, `biopython` for FASTA/Newick, etc.). No bare "use scanpy."
- **Engineering constraints** — **stated under the user's actual compute environment, NOT assumed**: ask for and record GPU availability, data scale (single-cell? million-cell spatial?), the tool ecosystem they're in, and memory/time budget. The spec must stay within those stated constraints (e.g. if CPU-only, note the mini-batch / approximation strategy; if a specific stack is required, stay inside it). Do NOT hardcode "no GPU" or a particular ecosystem as a universal default.
- **Engineering deliverables** — see the **Engineering deliverables (nf-core style)** section; the P0 deliverables MUST be listed here and have corresponding tasks.
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

## Domain data-model adapter (do NOT default to AnnData)

**The spec-writing skill is domain-agnostic about the data model.** `scanpy`/`AnnData` is ONE adapter (the single-cell one), not the universal assumption. **Before writing `design.md`, confirm the user's domain** and pick the matching data model. The example in this skill (graph-wavelet imputation) uses AnnData because it is a single-cell example — do NOT generalize that to other domains.

| Domain | Data model | Example shape |
|---|---|---|
| Single-cell / spatial omics | AnnData / MuData | cells × genes (sparse) |
| Bulk omics | matrix + sample metadata | samples × features |
| Genomics | FASTQ / BAM / CRAM / VCF / GFF | reads / variants |
| Proteomics | mzML / quantification tables | peptides × samples |
| Medical imaging | OME-Zarr / NIfTI | voxel arrays |
| Phylogenetics | FASTA / Newick | sequences / trees |
| Metagenomics | reads / contigs / abundance tables | taxa × samples |

**How to apply, at spec-writing time:**
1. **Ask/confirm the domain first** — if `algorithm-design` output or the user context does not make the domain obvious, ask. Do not silently assume single-cell.
2. **Select the adapter** — use the data model above (or a defensible domain equivalent) to drive `design.md`'s data flow, pseudocode libraries, and dependency versions. Module interfaces reference the domain's field/file names (e.g. `expr_matrix[samples, features]`, `aligned.bam`, `pep_quant[m/z, samples]`), not AnnData slots.
3. **Keep the example labeled** — the graph-wavelet imputation example below is a **single-cell domain example**; it stays in AnnData. Other domains write analogous artifacts in their own vocabulary.

## Engineering deliverables (nf-core style)

Specs that stop at "write the algorithm + `scanpy>=1.10`" are not engineering-ready. Borrowing the **nf-core** community standard, the spec's `tasks.md` MUST include tasks that generate the following engineering artifacts — not only the algorithm code. At minimum, the **P0** items are required in every MVP spec; P1/P2 items are listed as tasks or named in the Publication Roadmap's engineering gap.

| Priority | Deliverable | What the task produces |
|---|---|---|
| **P0** | Environment lock | `requirements.txt` / `environment.yml` (or `pixi.toml`) with **pinned** versions, not loose `scanpy>=1.10`. Lock file committed and reproducible. |
| **P0** | CI (GitHub Actions) | `.github/workflows/` running **lint + test on push**; matrix over OS/Python when relevant; fails on lint or test error. |
| **P0** | Small test data | A small, license-clear dataset (checked in or fetched by hash) **with expected outputs** committed alongside, so tests are deterministic and reproducible. |
| **P0** | Deterministic seed policy | All random sources fixed (`numpy`/`torch`/`random`/framework seeds) and the seed recorded; any non-determinism (GPU kernels, sparse solvers) documented. |
| **P1** | Container | `Dockerfile` / `Apptainer`/`Singularity` recipe built FROM the environment lock; published image tag recorded. |
| **P1** | Benchmark report | Auto-generated performance/accuracy report (e.g. `pytest-benchmark` / `asv` / custom) committed as a build artifact. |
| **P1** | CLI / API | A documented command-line entry point (`typer`/`argparse`) AND a programmatic API, both covered by tests. |
| **P1** | Tutorial / quickstart | A runnable quickstart (README or notebook) that works against the test data end-to-end. |
| **P2** | Changelog | `CHANGELOG.md` following Keep-a-Changelog / semver, updated per release. |
| **P2** | Citation metadata | `CITATION.cff` (authors, title, version, DOI slot) so the tool is citable. |
| **P2** | License / data-use record | `LICENSE` chosen + a note recording the license/data-use terms of every bundled dataset (especially for the small test data). |

**Where these land in the artifacts:**
- `design.md` — list the **P0 deliverables** under the **Engineering deliverables** bullet (and any P1/P2 that constrain the design). Full coverage gaps go in the **Publication Roadmap → Engineering gap** with effort + priority, as usual.
- `tasks.md` — include a concrete task for **at least: environment lock + CI + small test data + deterministic seed policy** (the four P0 items). Each task follows the normal bite-sized TDD structure (write test → see fail → implement → see pass → commit).

## Strong-constraint checklist (the spec set is incomplete if any fail)
- [ ] All three artifacts present (`requirements.md`, `design.md`, `tasks.md`), written sequentially, reviewed between phases.
- [ ] `requirements.md`: every acceptance criterion in EARS notation; **every `failure_boundary` has a matching criterion**; trace table complete.
- [ ] `design.md`: every module has a typed interface; pseudocode at API-call level (no high-level verbs); dependencies version-pinned; Engineering constraints reflect the **user's stated** environment (not an assumed default); Publication Roadmap present (MVP scope + 3 gaps with effort + priority).
- [ ] **Domain data-model adapter applied**: the user's domain confirmed, and the data flow / pseudocode / dependencies use that domain's model (NOT a silent AnnData default); the example is tagged as a single-cell example.
- [ ] **Engineering deliverables**: `design.md` lists the P0 deliverables (environment lock + CI + test data + deterministic seed policy); `tasks.md` has a task for each P0 item.
- [ ] `tasks.md`: bite-sized 5-step TDD tasks; every step has **real code** (no placeholders); every `simulation_plan` case is a test; Self-review done.
- [ ] No FORBID phrases anywhere: "做一个X", "用合适的参数", "做聚类", "用合适的模型", "TBD", "TODO", "implement later", "add error handling", "handle edge cases", "use a suitable method".

## Artifact output
In addition to the three kiro artifacts above (human-readable), this stage emits **`artifact.json`** (schema: `schemas/stage-schemas.json`): `stage_fields = {module_interfaces, acceptance_criteria (each traces_to a design failure_boundary), pseudocode_hashes}`.
Three cross-stage rules apply (`_shared/artifact-validation.md`):
- **rule 2 (no orphans)** — every `design.failure_boundaries` item MUST have ≥1 matching `acceptance_criteria` whose `traces_to` names it (machine-checked, not just the trace table above).
- **rule 3 (notation consistency)** — `module_interfaces` shapes/names MUST == `design.notation_and_shapes` (catches design→spec divergence).
- **rule 4 (pseudocode → code)** — each pseudocode block has a content hash in `pseudocode_hashes`; the implemented code MUST match, or any divergence is recorded with justification.

## References
- **crossbio-algo:algorithm-design** — the formal-method-contract input this skill consumes.
- Kiro spec-driven development — Requirements → Design → Tasks three-phase workflow (kiro.dev/docs/specs).
- superpowers:writing-plans — bite-sized TDD task granularity, no-placeholders rule, self-review.
- `schemas/stage-schemas.json` + `_shared/artifact-validation.md` — the machine-checkable artifact this stage emits.

## Example — three-artifact excerpt (graph-wavelet imputation, **single-cell domain example**)

> This example uses the **single-cell adapter** (AnnData/scanpy). It is ONE illustration of the Domain data-model adapter — for bulk / genomics / proteomics / imaging / phylogenetics / metagenomics, write analogous artifacts in that domain's vocabulary, not in AnnData.

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
