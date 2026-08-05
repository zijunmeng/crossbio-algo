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
brainstorm  (N candidate ideas; dev-mode: algorithm-abstraction + cross-domain invention)
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
| **Quick** | data-and-estimand-audit → algorithm-design-lite (only the 4 load-bearing fields: `problem_definition` / `estimand` / `objective_or_likelihood` / `failure_boundaries`) → basic tests | brainstorm, viability, full 16-field design, full spec, adversarial-panel-audit | ~30 min | "is this idea viable?", T3 learning, T4 internal one-off |
| **Standard** | data-audit → topic-viability (deep-comparison + multi-dim score) → algorithm-design (full 16-field) → spec-writing (kiro 3-phase) → 1 round adversarial-panel-audit | brainstorm (user already has the one idea) | ~half day | T2 tool paper — the default |
| **Publication** | the full closed loop: brainstorm (≥3 ideas) → viability → multi-round audit → formal design → kiro spec → benchmark → Publication Roadmap | nothing | ~multiple days | T1 top-tier / complete publication |

**Mode selection**: user picks, or auto-infer from target tier — **T3/T4 → Quick, T2 → Standard, T1 → Publication** (user can override).

**Never skipped** (all modes): `data-and-estimand-audit` always runs (the estimand/leakage audit is the root of the artifact chain); the artifact chain stays intact with estimand continuity + provenance hashes; the honest-colleague principle holds.

## Install
```bash
git clone https://github.com/YOUR/crossbio-algo
# user-level (all projects):
cp -r crossbio-algo/skills/* ~/.claude/skills/
# recommended: copy the bootstrap template into your project
cp crossbio-algo/CLAUDE.md ./CLAUDE.md   # then fill in your research context
```
Or install as a Claude Code plugin via the marketplace (plugin.json provided).

## Skills
| skill | role |
|---|---|
| `using-crossbio-algo` | **bootstrap**: the loop, when to trigger each, priority order |
| `data-and-estimand-audit` | GATE: 审计数据+estimand（donor 泄漏/批次/样本单位/ground truth）在算法发明前 |
| `brainstorm` | 5-round ideation; dev-mode = algorithm-abstraction + cross-domain (invents, doesn't recombine) |
| `topic-viability-assessment` | competitor deep-comparison table (input/method/output/limitation/delta); tier-aware score; FORBID judging crowdedness from names |
| `algorithm-design` | 4-step inventive design; autonomous + externalized reasoning; pause only at global forks |
| `spec-writing` | kiro requirements → design → tasks; bite-sized TDD; acceptance ← failure_boundary; Publication Roadmap |
| `adversarial-panel-audit` | adversarial panel of same-model subagents (info-isolated, role-based, no forced critique); pass/needs_revision/fail |
| `_shared/research-design-handoff` | the loop contract + fallback mechanism |

## Demo
`examples/scout/` — a full run on **"spatial multimodal data fusion"**: brainstorm (6 ideas) → viability (deep-comparison, 3 rejected) → audit (caught overclaim) → fallback → design → spec (kiro 3-file) → code → 4 tests green. Produces **SCOUT**, a T2 tool (paired-projection spatial RNA+ATAC integration, all-CPU).

## Who
Computational biologists / bioinformatians. Generalizable to any domain where you **brainstorm → vet → design → spec** an algorithm or method.

## Status
v0.1 — validated end-to-end on one direction (spatial omics). Roadmap: per-skill baseline tests, multi-domain validation, real-data benchmarks.

## License
MIT.
