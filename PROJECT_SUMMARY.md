# crossbio-algo — 项目总结 (v0.2.2)

## v0.2.2（当前）—— DECLARED → TRACED → **TESTED**

三轮评审（**7.6/10**）后,核心论点:**DECLARED ≠ TRACED ≠ TESTED ≠ VALIDATED ≠ SCIENTIFICALLY SUPPORTED**。v0.2.1 只做到 DECLARED→TRACED(结构可追溯);v0.2.2 解决 **TRACED→TESTED** —— validator 现在能区分"声明"与"被验证"。

| Phase | 内容 | 证据 |
|---|---|---|
| **0 release blockers** | CI 红(PyYAML)修复 `pip install -e ".[test,examples]"`;版本单源(plugin.json/pyproject/CITATION/CHANGELOG 一致,`test_meta` 强制);schema 移入 package(`importlib.resources`),**wheel 实测含 schema**;README 8→9 | 干净 conda env wheel build+install+validate 从 /tmp 通过 |
| **1 executable trace(中心)** | 真 source hash(从磁盘重算);`FB→AC→TEST→RESULT` 图;`verification_mode`(test/sim/benchmark/**documented_limitation**/...);**规则 6**:声明 tested 但无 passing test → FAIL;**规则 7**:documented_limitation 不能标 pass;**规则 8**:source 漂移 → FAIL | 26 validator 测试(含攻击样本);SCOUT fb3/fb4 诚实标 documented_limitation;**validator 拒绝 v0.2.1 的假声明**(把 fb3 翻成 tested → "DECLARED, not TESTED")|

**全套测试 crossbio env 干净验证通过**(validator 26 + viability 5 + SCOUT 9 + meta 2)。

**Phase 2(SCOUT 诚实最小夹具)**:eps 量纲修复(§11.1)、raw-count `count_layer` 契约(§14)、coordinate-agnostic 文档、AC 命名漂移修复;fb3/fb4 诚实标 documented_limitation;改 `project()` 触发 source-hash 漂移 → validator 抓到 → re-stamp 通过(rule 8 实战)。

**Phase 3(skill effectiveness benchmark)**:`benchmarks/` 设计 + 10 维 rubric + `run_case.py` harness + 1 个 **non-scanpy** pilot(phylo-recombination,病毒方向):standard 0.95 vs no-skill 0.36(**+0.59**,trap 维 estimand/leakage/benchmark/failure-boundary 全移动)。诚实限制:same-model grader、非盲、单 case → 完整 8 域 + 外部盲评专家是下一里程碑(TESTED→SCIENTIFICALLY SUPPORTED)。

---

## v0.2.1 —— 把 "machine-checkable" 从纸面变成会跑的代码


> **给评审专家的快速理解文档。** 读这份 + `README.md` + `examples/scout/` + `tests/baseline-tests.md` 即可全面理解。

---

## 一句话定位

**证据驱动的跨域生信算法生成闭环**——把一句模糊研究兴趣，变成经过数据审计、竞品查证、对抗审计、带失效边界的**机器可校验可执行算法 spec**。

## v0.2.1（当前）—— 把 "machine-checkable" 从纸面变成会跑的代码

二轮专家评审（**5.5→7.0/10**）后，5 个 P0 全部落实并验证：

| P0 | v0.2.1 修复 | 证据 |
|---|---|---|
| **P0-1** 新旧合同并存（6 vs 16 字段）| 单一 schema `crossbio_validate/schemas/stage-schemas.json`（`$defs`+`oneOf` 按 stage 约束 `stage_fields`）；字段计数修正为 **15 required + 2 optional**；6-field 残留清零 | `grep` 无残留；schema 拒绝缺 `objective_or_likelihood` 的 design |
| **P0-2** artifact 只"设计为可检查" | `crossbio_validate` CLI（schema + provenance + parent-chain + stage-order + fatal-gate + 5 跨阶段规则）；**21 测试**（每规则 GREEN + 故意漂移 RED）| `crossbio validate-chain` 抓 estimand/notation/pseudocode 漂移 |
| **P0-3** SCOUT 没满足自身 requirements | SCOUT 重建为 **PLS + entropic OT** 旗舰；**9 测试**；每个 AC trace 到 failure_boundary | `examples/scout/artifacts/` 链 `validate-chain` 通过（0 findings）|
| **P0-4** 数学公式不一致 | 唯一 `B_atac`（`impute` 与重构检查共用）；PLS **中心化**；不再误称 CCA | `test_impute_uses_one_B_atac`、`test_pair_map_is_pls_not_uncentered_MUTATION` |
| **P0-5** viability 区间算术不闭合 | 改 **pessimistic/base/optimistic**（区间构造性闭合），重命名 *decision uncertainty band* | 5 测试 |

**P1/P2**：`agents/→reviewer-roles/`（诚实命名，非真 subagent）；data-audit 绝对规则按 `generalization_axis` 软化（Squair/Svensson）；Quick 模式"viable"矛盾修复；README/CHANGELOG/CITATION.cff/CONTRIBUTING.md/CI/env-lock。

**全套测试：validator 21 + viability 5 + SCOUT 9 = 35 passed**（`python -m pytest tests/`）。

---

## v0.1 → v0.2 的转变（核心）

| v0.1（"idea novelty pipeline"）| v0.2（"evidence-driven + machine-checkable"）|
|---|---|
| 流程完整，证据不完整 | 数据审计（GATE）先于算法发明 |
| 6 字段 design（数学抽象易成词汇包装）| **formal method contract（15 required + 2 optional 字段）**（objective/likelihood/identifiability/复杂度/uncertainty）|
| "Inventing not recombining"（诱导伪创新）| **"Utility first, novelty explicit"**（允许组合，明确 novelty locus）|
| 竞品"插槽判断"（method 不同≠竞品，过严）| **5 类竞品分类**（functional substitute / methodological neighbor / input-slot / workflow / naive baseline）|
| viability 单 0-1 分（假精确）| **8 维评分 + 每维 confidence/evidence_grade + plausible range** |
| Markdown handoff（design-code 漂移）| **artifact.json 机器校验**（5 条跨阶段规则：estimand 连续/failure_boundary→acceptance/notation 一致/pseudocode→code/provenance）|
| cross-model-audit（名字误导——非真跨模型）| **adversarial-panel-audit**（诚实命名 + 6 agents + 不强迫找问题 + defender/replicator）|
| 强绑 AnnData | **7 领域 adapter**（sc/spatial/bulk/genome/proteomics/imaging/phylo/metagenomics）|
| 完整闭环（对简单任务过重）| **三档模式**（Quick/Standard/Publication）|

---

## Skill 清单（7 skill + 6 agents + 4 共享文件）

| skill | 职责 | 关键设计（v0.2） |
|---|---|---|
| **using-crossbio-algo** | bootstrap 元 skill | 闭环图 + 触发优先级 + fallback + **三档模式**（Quick/Standard/Publication，auto-infer from tier）|
| **data-and-estimand-audit** 🆕 | GATE（算法发明前）| 12 字段审计（biological_unit/estimand/fatal_issues/leakage_graph/split_strategy...）；**fatal_issues 非空 = 链条停**（GATE）；7 大真实失败模式（donor 泄漏/批次混杂/pseudoreplication/circular ground truth/MNAR...）|
| **brainstorm** | 创意引擎 | 5 轮 + dev/research 双模式；dev-mode algorithm_abstraction + 跨域；**famous-algorithm trap** + R5 跨域碰撞检查 |
| **topic-viability-assessment** | 课题评估 | **5 类竞品分类** + **8 维评分**（每维 confidence/evidence_grade + plausible range）；禁看名字判拥挤 |
| **algorithm-design** | 算法设计 | **formal method contract（15 required + 2 optional 字段）**（problem/estimand/abstraction/notation/assumptions/**objective_or_likelihood**/**identifiability**/cross-domain/algorithm/**optimization_or_inference**/**complexity**/failure_boundaries/uncertainty/invariances/simulation_dgp/**benchmark_protocol**/novelty_or_utility）；**"utility first, novelty explicit"** stance；自主跑 + 推理外显 |
| **spec-writing** | spec 生成 | kiro 三段式（requirements/design/tasks）+ 验收 trace failure_boundary + **7 领域 adapter** + **nf-core 11 工程交付物** + Publication Roadmap |
| **adversarial-panel-audit** | 对抗审计 | **诚实命名**（same-model panel，非 cross-model）；**6 agents**（domain-biologist/statistical-reviewer/algorithm-methodologist/benchmark-auditor/implementation-reviewer/reproducibility-reviewer）；**不强迫找问题**（禁空泛 looks good + 可"no material issue" + defender/replicator）；结构化 finding（claim/evidence/severity/confidence/reproduction_check/blocking/fix）|
| **agents/** (6) | 审计角色定义 | 每个 .md：角色 + 审什么 + checklist |
| `_shared/research-design-handoff` | 联动契约 | 完整闭环 + fallback + **三档说明** + **artifact.json 机制** |
| `crossbio_validate/schemas/stage-schemas.json` 🆕 | artifact 结构 | JSON Schema（id/parent/stage/provenance_hash/stage_fields）|
| `_shared/artifact-validation.md` 🆕 | 5 条跨阶段校验 | estimand 连续 / failure_boundary→acceptance / notation 一致 / pseudocode→code / provenance |
| `algorithm-design/cross-domain-inspiration` | 28 域灵感池 | 数学本质→科学领域映射 |

---

## 闭环流程（v0.2）

```
data-and-estimand-audit ✋GATE  (fatal_issues 非空 = 停)
  → brainstorm  (N candidate; dev-mode 跨域发明, famous-algorithm trap)
  → topic-viability  (5类竞品 + 8维评分 + range; 禁看名字判拥挤)
      ★ adversarial-panel-audit  (6-agent panel, 信任前必审)
  → algorithm-design  (formal-method contract; utility-first; 自主跑+推理外显)
      ★ adversarial-panel-audit
  → spec-writing  (kiro三段式; 领域adapter; nf-core; 验收←failure_boundary)
      ★ adversarial-panel-audit
  → code
```
**三档**：Quick（data-audit + design-lite + tests，~30min）/ Standard（data-audit + viability + formal-design + spec + 1-audit，T2）/ Publication（full loop + multi-audit + benchmark，T1）。
**artifact chain**：data-audit(root) → design → spec → code，5 条跨阶段校验贯穿。
**Fallback**：idea 失败→回退剩余候选，永不丢弃。

---

## v0.2 评审落实（8 commit）

| commit | 改进 | 回应评审 |
|---|---|---|
| `5c237aa` | P0 修复 + SCOUT mutation tests | YAML blocker / 循环验证→能区分对错 |
| `c248770` | data-and-estimand-audit (GATE) | "最大缺口——donor 泄漏/批次/样本单位" |
| `bb7201a` | formal method (6→16 字段 + utility-first) | "6 字段不足 + inventing 诱导伪创新" |
| `462ed94` | viability 5 类竞品 + 多维评分 | "直接竞品过严 + 0-1 假精确" |
| `76ec276` | artifact.json (5 校验) | "design-spec-code 漂移" |
| `e9a4b11` | adversarial-panel-audit (诚实 + agents) | "非真 cross-model + critique inflation" |
| `1b7299d` | 领域 adapter + nf-core | "强绑 AnnData + 缺工程交付物" |
| `c11095a` | 三档模式 | "完整闭环对简单任务过重" |

**评审路线图**：前 30 天 ✅ / 31-60 天 ✅ / 61-90 天 skill 改进 ✅。剩余（多方向验证 + 真实盲测）需发布后实际使用。

---

## 目录结构（v0.2）

```
crossbio-algo/
├── .claude-plugin/plugin.json
├── README.md  CLAUDE.md  PROJECT_SUMMARY.md  CHANGELOG.md  CITATION.cff  CONTRIBUTING.md  LICENSE  .gitignore  pyproject.toml  requirements.txt
├── crossbio_validate/schemas/stage-schemas.json          (canonical machine schema, $defs+oneOf)  🆕 v0.2.1
├── crossbio_validate/                  (validator CLI: schema + chain + 5 rules)   🆕 v0.2.1
├── skills/
│   ├── using-crossbio-algo/SKILL.md
│   ├── data-and-estimand-audit/SKILL.md
│   ├── brainstorm/SKILL.md
│   ├── topic-viability-assessment/SKILL.md
│   ├── algorithm-design/{SKILL.md, cross-domain-inspiration.md}
│   ├── spec-writing/SKILL.md
│   ├── adversarial-panel-audit/{SKILL.md, reviewer-roles/*.md (6)}   🔄 v0.2.1 改名
│   └── _shared/{research-design-handoff.md, artifact-validation.md}
├── examples/scout/   (PLS+OT spec + 代码 + 9 测试含 mutation + artifacts/ 链)
├── tests/{test_validator.py (21), test_viability_range.py (5), baseline-tests.md}
└── .github/workflows/validate.yml      (CI)   🆕 v0.2.1
```

---

## 一句话给专家

> crossbio-algo v0.2.1 把"自主科研 agent"最有价值的部分（科研诚实纪律 + 数据审计 + formal method + 机器可校验 handoff + 对抗 panel）提炼成一个 7-skill Claude Code 闭环——从数据审计到可执行 spec，带 GATE/竞品查证/双向审计/失效边界/三档模式。v0.2.1 的决定性进步：**machine-checkable 从纸面变成代码**——`crossbio_validate` 真的会拒绝漂移的 artifact，SCOUT 旗舰的 4 段 artifact 链真的通过了校验。35 测试全绿。下一步：GitHub 发布 + 多方向验证 + 真实盲测。
