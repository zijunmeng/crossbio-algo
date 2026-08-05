---
name: using-crossbio-algo
description: Bootstrap for the crossbio-algo skill loop. Use at the start of any research / algorithm / method / tool task, or when the user proposes a research direction. Introduces the brainstorm → viability → audit → design → spec loop, when to trigger each skill, the priority order, and the fallback mechanism. 触发场景：用户提出研究方向 / 算法 / 工具 / 方法，或会话开始需要知道这套研究闭环时。
---

# Using Crossbio-Algo

## Overview
This is the **bootstrap** for the crossbio-algo skill loop — a coordinated chain that turns a fuzzy research interest into a vetted, executable algorithm spec, with scientific-honesty discipline. Think of it as the map: it tells you which skill to use when, and how they connect.

## The Loop
```
research-intake  (user has data + research question)
  → data-and-estimand-audit  (GATE: audit donor leakage / batch / sample unit / ground truth before any invention)
      ✋ fatal issue → STOP until resolved or user accepts risk
  → brainstorm  (N candidate ideas; dev-mode invents algorithms from math essence + cross-domain)
  → topic-viability  (competitor DEEP-COMPARISON table → tier-aware score)
      ★ adversarial-panel-audit  (before trusting the verdict)
  → algorithm-design  (4-step inventive; autonomous + externalized reasoning)
      ★ adversarial-panel-audit
  → spec-writing  (kiro requirements/design/tasks; acceptance ← failure_boundary)
      ★ adversarial-panel-audit
  → code
```

## When to trigger each skill
| Signal from the user | Skill |
|---|---|
| 用户有数据 + 研究问题，在 brainstorm/design 前 | **data-and-estimand-audit** (GATE — 审计 donor 泄漏/批次/样本单位/ground truth；fatal issue 则停) |
| "I want to explore a direction / find topics / get multiple ideas" | **brainstorm** (dev-mode if algorithm/tool; research-mode if biomedical direction) |
| "Is this idea worth doing? / value it? / competitors?" | **topic-viability-assessment** (MUST build deep-comparison table first; ask target tier) |
| "Design an algorithm / method for X" | **algorithm-design** (autonomous 4-step; externalize reasoning) |
| "Write spec / PRD / implementation plan / requirements" | **spec-writing** (kiro 3 artifacts) |
| Any artifact about to be trusted, or "审一下 / review / 靠谱吗" | **adversarial-panel-audit** (subagent panel) |

## Priority / order
- **data-and-estimand-audit BEFORE brainstorm** (数据/estimand 审计先于算法发明；fatal_issues 未解决则不进 brainstorm).
- **brainstorm BEFORE viability** (generate candidates, then score).
- **viability BEFORE design** (vet before investing design effort).
- **design BEFORE spec** (invent before engineering).
- **adversarial-panel-audit is horizontal** — fires before ANY artifact is trusted (viability verdict / design / spec / result).
- If an idea is rejected → **fallback** to remaining brainstorm candidates (see `_shared/research-design-handoff.md`); never discard, never jump to "switch direction" without offering the remaining candidates + a "generate more?" prompt.

## Two disciplines that hold the loop together
- **Honest colleague**: no skill vetoes the user. Viability is counsel; it forces an *informed* decision (build the comparison table, ask the tier), then respects the user's call. Audit is two-way insurance (prevents under-score AND over-claim).
- **Truth carries forward**: every handoff carries upstream truth (competitors, failure boundaries, target tier) — no stage restarts from a blank slate.

## Effort modes (Quick / Standard / Publication)
The full loop (above) is the **Publication** mode — the complete closed loop. For many tasks that is overkill (a quick feasibility check or a T3 exercise does not need brainstorm + viability + multi-round audit). So the loop has three effort tiers. **State the effort mode out loud** when you start (the same way you state the mode), so the user knows the scope.

### Quick (~30 min — fast feasibility / practice)
Run: **data-and-estimand-audit** → **algorithm-design-lite** → basic tests. Skip brainstorm / viability / full spec / adversarial-panel-audit.
- **algorithm-design-lite** = only the 4 load-bearing fields of the formal contract: `problem_definition`, `estimand`, `objective_or_likelihood`, `failure_boundaries`. (The full 16-field contract is NOT required here — see `algorithm-design` SKILL for the lite variant.)
- The data-audit artifact is still produced (estimand must carry forward).
- **Best for**: "is this idea even viable?", T3 learning, T4 internal one-off need, a single quick sanity check.

### Standard (~half day — the regular tool paper)
Run: **data-and-estimand-audit** → **topic-viability-assessment** (deep-comparison table + multi-dim score) → **algorithm-design** (full formal 16-field contract) → **spec-writing** (kiro three-phase) → **1 round adversarial-panel-audit**.
- Skip brainstorm (user already has the idea; viability scores that one idea).
- **Best for**: T2 tool paper — the default mode for "build me a tool worth publishing."

### Publication (~multiple days — full publication)
Run the **full closed loop**: brainstorm (multiple ideas) → viability (full assessment) → **multi-round adversarial-panel-audit** → algorithm-design (formal) → spec-writing (kiro) → benchmark → Publication Roadmap.
- **Best for**: T1 top-tier / a complete publication where the full honesty discipline (multi-idea generation, multi-round adversarial audit) earns its cost.

### Mode selection
- **User picks** explicitly ("just a quick check" → Quick; "this is a real paper" → Standard/Publication).
- **Auto-infer from target tier** if the user doesn't pick: **T3/T4 → Quick**, **T2 → Standard**, **T1 → Publication**.
- The user can override the inferred mode at any time.

### What is NEVER skipped (holds across all modes)
- **data-and-estimand-audit** always runs — even in Quick, the data/estimand audit artifact is produced (leakage / batch / ground-truth audit before any invention).
- **Artifact chain** stays intact across modes — `data-audit` (root) → `design` → `spec` → `code` with estimand continuity and provenance hashes. The lite design still emits the `estimand` + `failure_boundaries` that downstream artifacts validate against.
- **Honest-colleague principle** holds — no mode vetoes the user; mode only sets scope.

## How to invoke
Each skill auto-triggers from its own `description`. To force a stage, use the Skill tool with the skill name. Read the individual SKILL.md files for each skill's internal rules.

## References
- `_shared/research-design-handoff.md` — the full loop contract + handoff blocks + fallback mechanism.
- Individual skill SKILL.md files for stage-specific rules (invoked as **crossbio-algo:brainstorm**, **crossbio-algo:topic-viability-assessment**, **crossbio-algo:algorithm-design**, **crossbio-algo:spec-writing**, **crossbio-algo:adversarial-panel-audit**).
