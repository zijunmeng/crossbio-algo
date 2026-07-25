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
      ★ cross-model-audit  (subagent panel, info-isolated, forced-adversarial)
  → algorithm-design  (4-step inventive; autonomous run + externalized reasoning)
      ★ cross-model-audit
  → spec-writing  (kiro: requirements / design / tasks; acceptance traces to failure_boundary)
      ★ cross-model-audit
  → code
```
**Fallback mechanism**: an idea rejected at any stage falls back to the remaining candidates — never discarded.

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
| `brainstorm` | 5-round ideation; dev-mode = algorithm-abstraction + cross-domain (invents, doesn't recombine) |
| `topic-viability-assessment` | competitor deep-comparison table (input/method/output/limitation/delta); tier-aware score; FORBID judging crowdedness from names |
| `algorithm-design` | 4-step inventive design; autonomous + externalized reasoning; pause only at global forks |
| `spec-writing` | kiro requirements → design → tasks; bite-sized TDD; acceptance ← failure_boundary; Publication Roadmap |
| `cross-model-audit` | subagent panel (info-isolated, role-based, forced-adversarial); pass/needs_revision/fail |
| `_shared/research-design-handoff` | the loop contract + fallback mechanism |

## Demo
`examples/scout/` — a full run on **"spatial multimodal data fusion"**: brainstorm (6 ideas) → viability (deep-comparison, 3 rejected) → audit (caught overclaim) → fallback → design → spec (kiro 3-file) → code → 4 tests green. Produces **SCOUT**, a T2 tool (paired-projection spatial RNA+ATAC integration, all-CPU).

## Who
Computational biologists / bioinformatians. Generalizable to any domain where you **brainstorm → vet → design → spec** an algorithm or method.

## Status
v0.1 — validated end-to-end on one direction (spatial omics). Roadmap: per-skill baseline tests, multi-domain validation, real-data benchmarks.

## License
MIT.
