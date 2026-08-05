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

## How to invoke
Each skill auto-triggers from its own `description`. To force a stage, use the Skill tool with the skill name. Read the individual SKILL.md files for each skill's internal rules.

## References
- `_shared/research-design-handoff.md` — the full loop contract + handoff blocks + fallback mechanism.
- Individual skill SKILL.md files for stage-specific rules (invoked as **crossbio-algo:brainstorm**, **crossbio-algo:topic-viability-assessment**, **crossbio-algo:algorithm-design**, **crossbio-algo:spec-writing**, **crossbio-algo:adversarial-panel-audit**).
