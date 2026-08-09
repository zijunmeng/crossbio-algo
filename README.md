# crossbio-algo

**Autonomous research loop for computational biology** — turns a fuzzy research interest into a vetted, executable algorithm spec, with scientific-honesty discipline.

## Why
Generic coding agents (Claude Code / Codex) can run analyses and write code, but they don't *proactively* do the discipline a researcher needs:
- **check competitors** (avoid reinventing /撞车),
- **adversarially audit** (avoid overclaim),
- **externalize reasoning** (avoid black-box),
- **define failure boundaries** (avoid overclaiming accuracy),
- **produce executable specs** (avoid "simple code").

`crossbio-algo` installs these as a coordinated skill loop.

## The loop
```
data-and-estimand-audit  (GATE root — donor leakage / batch / sample-unit / ground truth; runs in every mode, incl. Quick)
  → brainstorm  (N candidate ideas; dev-mode: algorithm-abstraction + cross-domain, utility-first)
  → topic-viability  (competitor DEEP-COMPARISON table; tier-aware T1–T4 score)
      ★ adversarial-panel-audit  (subagent panel, info-isolated, role-based)
  → algorithm-design  (4-step inventive; autonomous run + externalized reasoning)
      ★ adversarial-panel-audit
  → spec-writing  (kiro: requirements / design / tasks; acceptance traces to failure_boundary)
      ★ adversarial-panel-audit
  → code
```
**Fallback mechanism**: an idea rejected at any stage falls back to the remaining candidates — never discarded.

## Effort modes — Quick / Standard / Publication
The full loop is for a complete publication. For lighter tasks it is overkill, so there are three tiers. **State the mode out loud** when you start.

| Mode | Runs | Skips | ~Time | Fits |
|---|---|---|---|---|
| **Quick** | data-and-estimand-audit → algorithm-design-lite (only the 4 load-bearing fields: `problem_definition` / `estimand` / `objective_or_likelihood` / `failure_boundaries`) → basic tests | brainstorm, viability, full 15-required+2-optional design, full spec, adversarial-panel-audit | ~30 min | "is this idea buildable / sane to attempt?", T3 learning, T4 internal one-off |
| **Standard** | data-audit → topic-viability (deep-comparison + multi-dim score) → algorithm-design (full 15-required+2-optional contract) → spec-writing (kiro 3-phase) → 1 round adversarial-panel-audit | brainstorm (user already has the one idea) | ~half day | "is this idea worth doing?" (lightest viability mode), T2 tool paper — the default |
| **Publication** | the full closed loop: brainstorm (≥3 ideas) → viability → multi-round audit → formal design → kiro spec → benchmark → Publication Roadmap | nothing | ~multiple days | T1 top-tier / complete publication |

**Mode selection**: user picks, or auto-infer from target tier — **T3/T4 → Quick, T2 → Standard, T1 → Publication** (user can override).

**Never skipped** (all modes): `data-and-estimand-audit` always runs (the estimand/leakage audit is the root of the artifact chain); the artifact chain stays intact with estimand continuity + provenance hashes; the honest-colleague principle holds.

## Install

### A. Claude Code plugin (recommended)
```
/plugin marketplace add zijunmeng/crossbio-algo
/plugin install crossbio-algo@crossbio-algo
```
Then copy the bootstrap template into your project:
```bash
cp CLAUDE.md /path/to/your/project/CLAUDE.md   # fill in your research context
```

### B. Manual (no plugin manager)
```bash
git clone https://github.com/zijunmeng/crossbio-algo
cp -r crossbio-algo/skills/* ~/.claude/skills/        # user-level skills
cp crossbio-algo/CLAUDE.md /path/to/your/project/CLAUDE.md
```

### C. Validator only (`crossbio` CLI, no skills)
```bash
pip install git+https://github.com/zijunmeng/crossbio-algo
crossbio validate-chain <artifact-dir>
crossbio attest <tests> --bind <src> --out results.json
```

### After install
1. Fill in your project's `CLAUDE.md` (domain / compute / target tier / data).
2. Propose a research direction → skills auto-trigger (data-audit → viability → design → spec).
3. Validate each stage's `artifact.json` with `crossbio validate-chain`.

## Skills
| skill | role |
|---|---|
| `using-crossbio-algo` | **bootstrap**: the loop, when to trigger each, priority order |
| `data-and-estimand-audit` | GATE: 审计数据+estimand（donor 泄漏/批次/样本单位/ground truth）在算法发明前 |
| `brainstorm` | 5-round ideation; dev-mode = algorithm-abstraction + cross-domain (utility-first, novelty explicit — see algorithm-design) |
| `topic-viability-assessment` | competitor deep-comparison table (input/method/output/limitation/delta); tier-aware score; FORBID judging crowdedness from names |
| `algorithm-design` | 4-step inventive design; autonomous + externalized reasoning; pause only at global forks |
| `spec-writing` | kiro requirements → design → tasks; bite-sized TDD; acceptance ← failure_boundary; Publication Roadmap |
| `adversarial-panel-audit` | adversarial panel of same-model subagents (info-isolated, role-based, no forced critique); pass/needs_revision/fail |
| `_shared/research-design-handoff` | the loop contract + fallback mechanism |

## Validator — the machine-checkable handoff
Each stage emits an `artifact.json` (schema: `crossbio_validate/schemas/stage-schemas.json`). The `crossbio` validator checks a directory of these as a chain:

```bash
crossbio validate-chain <dir>     # schema + provenance + parent-chain + stage-order
                                  # + fatal-gate + 8 content rules (5 cross-stage + 3 executable-trace)
crossbio validate <one.json>      # one artifact: schema + provenance only
crossbio validate-project <dir>   # scan a project dir, then validate-chain
crossbio stamp <one.json>         # authoring helper: write the correct provenance_hash
```

**What it catches** — design↔spec↔code drift: an estimand that changed silently between stages, a `failure_boundary` with no acceptance test tracing back to it, notation shapes that diverged (e.g. `X∈ℝ^{n×p}` in design vs `n×d` in spec), pseudocode that has no code counterpart, or a broken `parent_artifact_id` / `provenance_hash`. Plus the **executable-trace** rules (Phase 1): every acceptance criterion in a **test-requiring** mode (`automated_test` / `simulation` / `benchmark`) MUST link to ≥1 **source-bound** passing test (FB→AC→TEST→RESULT — `crossbio attest` binds the result to the current source; a self-declared `passed` is only an unattested WARNING); a `documented_limitation` MUST NOT be marked `passed`; and a component shown ≤ a simpler alternative is flagged `remove_or_redesign` (complexity kill-switch). The kind of bug that previously slipped through to expert review.

**Run everything:**
```bash
python -m pytest tests/           # 30 validator tests (tests/test_validator.py)
                                  # + 11 scout tests (examples/scout/test_scout.py)
```
CI (`.github/workflows/validate.yml`) runs the validator suite plus a skill-frontmatter + plugin-manifest + schema-parse sanity check on every push/PR.

## Demo
`examples/scout/` — a full run on **"spatial multimodal data fusion"**: brainstorm (6 ideas) → viability (deep-comparison, 3 rejected) → audit (caught overclaim) → fallback → design → spec (kiro 3-file) → code → **11 tests green** (`examples/scout/test_scout.py`). Produces **SCOUT** — a T2-targeted research fixture / end-to-end example (paired-projection spatial RNA+ATAC integration on **PLS + optimal transport**, all-CPU; coordinate-agnostic, no spatial regularization).

## Repository layout
```
crossbio-algo/
├── .claude-plugin/plugin.json          Claude Code plugin manifest
├── pyproject.toml                      validator package + `crossbio` console script + [test] extra
├── requirements.txt                    validator runtime lock (jsonschema)
├── README.md  CLAUDE.md  CHANGELOG.md  CONTRIBUTING.md  CITATION.cff  PROJECT_SUMMARY.md  LICENSE
├── skills/                             the 7 skills
│   ├── using-crossbio-algo/  data-and-estimand-audit/  brainstorm/
│   ├── topic-viability-assessment/  algorithm-design/  spec-writing/
│   ├── adversarial-panel-audit/  (SKILL.md + agents/*.md)
│   └── _shared/{research-design-handoff.md, artifact-validation.md}
├── crossbio_validate/schemas/stage-schemas.json          CANONICAL machine schema ($defs + oneOf per stage)
├── crossbio_validate/                  validator CLI package (cli.py, core.py)
├── tests/test_validator.py             30 validator tests (incl. deliberately-drifted RED cases)
├── examples/scout/                     flagship: design/requirements/tasks.md + scout.py + test_scout.py (11 tests)
└── .github/workflows/validate.yml      CI: validator suite + frontmatter/manifest/schema sanity
```

## Who
Computational biologists / bioinformatians. Generalizable to any domain where you **brainstorm → vet → design → spec** an algorithm or method.

## Status
v0.2.4 — the loop is validated end-to-end on one direction (spatial omics), and the stage handoff is now **machine-checkable** via the `crossbio` validator (schema + chain + 8 rules: 5 cross-stage + 3 executable-trace; 26 tests). Roadmap: per-skill baseline tests, multi-domain validation, real-data benchmarks. See `CHANGELOG.md` for the v0.1 → v0.2 → v0.2.4 path.

## License
MIT.
