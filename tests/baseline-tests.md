# crossbio-algo — Per-Skill Baseline Tests (TDD for Skills)

> Borrowed from superpowers `writing-skills` Iron Law: **no skill without a failing test first.**
> Each skill MUST have a baseline test: run a pressure scenario WITHOUT the skill (RED — agent violates the rule) and WITH the skill (GREEN — agent complies).

## Method
- **RED**: spawn a subagent via the Agent tool WITHOUT giving it the skill content; run the pressure scenario; record the baseline behavior (expected to violate the skill's rule).
- **GREEN**: spawn a subagent WITH the skill content; run the same scenario; verify compliance.
- **REFACTOR**: if GREEN still has loopholes, tighten the skill and re-test.

## Per-skill tests

### topic-viability-assessment
- **scenario**: evaluate a "looks crowded" direction (e.g. "a new scRNA-seq clustering method"), T2.
- **RED expected** (verified 2026-07-25): naked Claude does NOT judge-from-names — it gives a deep qualitative assessment (Leiden strong, hard to prove, desk-reject risk + 5 pivot angles). BUT it produces NO structured deep-comparison table, NO target-tier score, NO slot-based direct-competitor judgment. **The skill's real value = forcing a STRUCTURED verdict (table + tier + slot), not preventing name-judging.** (Consistent with the early PASGate finding: baseline is strong; the skill adds structure/comparability/discipline.)
- **GREEN**: builds a competitor deep-comparison table (input/method/output/limitation/delta); decides direct competitors by slot (not keyword); score driven by delta analysis, not count.

### brainstorm
- **scenario**: user wants candidate ideas for a direction.
- **RED expected**: returns only 1 idea; all gaps are confirming; cites "current trends" from memory.
- **GREEN**: ≥3 candidates; ≥1 non-confirming gap; trends verified; dev-mode ideas carry `algorithm_abstraction` + cross-domain.

### algorithm-design
- **scenario**: design an algorithm.
- **RED expected**: jumps to a known method ("use a VAE") without abstraction; no externalized reasoning; asks the user a professional either/or at every step; no failure boundary.
- **GREEN**: math abstraction → cross-domain → failure boundary → simulation; autonomous run with reasoning externalized; pauses only at global forks.

### spec-writing
- **scenario**: turn a design into a spec.
- **RED expected**: high-level verbs ("do clustering"); acceptance not traced to failure_boundary; no tasks file.
- **GREEN**: kiro 3 artifacts (requirements/design/tasks); API-call-level pseudocode; acceptance ← failure_boundary; bite-sized TDD tasks with real code.

### adversarial-panel-audit
- **scenario**: audit a produced artifact.
- **RED expected**: returns "looks good"; no information isolation; no structured verdict.
- **GREEN**: panel of same-model subagents, info-isolated, each completes its role checklist (does NOT force ≥1 finding — critique inflation forbidden; may conclude "no material issue — checklist completed"); structured findings (claim/evidence/severity/confidence/reproduction_check/blocking/fix); optional defender/replicator seat; structured pass/needs_revision/fail verdict.

### using-crossbio-algo (bootstrap)
- **scenario**: user proposes a research task.
- **RED expected**: doesn't know the loop; triggers wrong/no skill.
- **GREEN**: identifies the loop, triggers skills in order, applies fallback on rejection.

## Running a test
```
# RED (no skill):
Agent(prompt="<scenario>", subagent_type="general-purpose")   # do NOT inject skill content
# GREEN (with skill):
Agent(prompt="<scenario> + <paste skill SKILL.md content>", subagent_type="general-purpose")
# Compare: does GREEN comply where RED violated?
```

## RED 实测汇总（2026-07-25，全部 5 skill + 之前 topic-viability）
裸 Claude **内容质量普遍高**（多 idea / 详细设计 / 详细 spec / 找问题审计 / depth 评估）—— baseline 强。**skill 的价值 = 结构化纪律 + 一致性**，不是"内容更好"：
| skill | 裸 Claude 违反（RED 实测） | skill 补的纪律（GREEN） |
|---|---|---|
| brainstorm | 凭记忆不查证；无 dev-mode abstraction；无 self-critique | 查证 + algorithm_abstraction + self-critique |
| algorithm-design | 套现成方法不抽象；全 scRNA 无跨域；无严格失效边界；无 simulation-first/推理外显 | 抽象→跨域→失效边界→simulation + 推理外显 |
| spec-writing | 无 kiro 三段式分离；无 Publication Roadmap；测试非 bite-sized TDD（但验收 trace 做得好） | kiro 三段式 + Roadmap + bite-sized TDD |
| adversarial-panel-audit | 单审计非 panel；无信息隔离；无结构化裁决（但找了 4 个硬伤） | panel + 信息隔离 + 完成角色 checklist（不强制找问题）+ 结构化 finding + 结构化裁决 |
| using-crossbio-algo | 不识别闭环；不触发 skill 序列（直接单步答） | bootstrap 闭环 + 按序触发 |
| topic-viability | 不结构化（无对比表/tier/插槽；虽 depth 但定性叙述） | 深度对比表 + tier + 插槽判断 |

**结论**：区分"实测"与"推断"——
- **RED 实测**：全部 5 skill + topic-viability 的裸行为已记录（见上表"RED 实测"列）。
- **GREEN 实测**：仅 **topic-viability** 有正式的 RED+GREEN 对照实测。
- **GREEN 推断**（非实测）：其余 5 skill（brainstorm / algorithm-design / spec-writing / adversarial-panel-audit / using-crossbio-algo）的 GREEN 行为是基于之前真实运行（SCOUT / spaGRN / spatialEnKF 等带 skill 的实际项目）的**推断**，**未做正式的 skill-enabled vs skill-disabled 对照 eval suite**。该对照 eval 计划在 v0.2 迁移到 skill-creator eval 框架后补齐。

RED 揭示裸 Claude 虽强但缺结构化纪律——skill 的价值 = 把"偶发的好行为"变成"每次必走的结构化流程"。

## Status
- **topic-viability**: 正式 RED+GREEN 实测完成（RED 见上方 demo，GREEN 经 spaGRN/SCOUT 真实运行间接验证 + 本次对照实测）。
- **其余 5 skill**: RED 实测完成（裸行为已记录）；GREEN 为基于历史真实运行的推断，**非正式对照 eval**——正式 skill-enabled vs skill-disabled 对照 eval 待做（v0.2 计划迁移到 skill-creator eval 框架）。
