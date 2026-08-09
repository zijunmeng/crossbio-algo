# Process Audit —— Xenium CCC 工具设计

> **这不是成果展示,是失败分析。** 用户提了一个真实研究方向(Xenium 空间 CCC 算法),agent 用 crossbio-algo skills 设计了一个叫 SPICE 的方法。用户追问"你调研了所有工具吗?""SPICE 是怎么提出的?"——agent 承认走了捷径。这份报告如实记录**实际发生了什么 vs skills 要求什么**,以及 skills 需要怎么改。
>
> 日期:2026-08-09。Agent: glm-5.2。Skill version: 0.3.0。

---

## 一、实际过程(time-line)

| 步骤 | skills 要求的 | agent 实际做的 | 合规? |
|---|---|---|---|
| ① 用户提方向 | 触发 `using-crossbio-algo` → 自动进 `data-and-estimand-audit` (GATE) | ✅ 做了 data-audit(审了 estimand / panel 约束 / ground truth / pseudoreplication) | ✅ |
| ② 竞品查证 | `topic-viability-assessment` 硬规则:**"Never judge from memory. Verify with search first."** | ❌ **从记忆里列了 6 个工具(CellChat / COMMOT / NicheNet / CellPhoneDB / HoloNet / SpaTalk),没查 PubMed / bioRxiv** | ❌ 违反头号规则 |
| ③ Brainstorm | 如果用户要多个候选 → `brainstorm` 5 轮;**R1 每条 trend/method 声明必须 verified** | ❌ **完全跳过 brainstorm**。直接从 data-audit 跳到 design | ❌ |
| ④ algorithm-design | 先 `mathematical_abstraction`(抽象到数学本质)→ 再 `cross_domain_inspiration`(查跨域灵感表)→ 再 propose。推理外显。 | ❌ **没有走 abstraction→cross-domain 流程**。SPICE 的核心想法(空间因果 / IV / niche-controlled regression / distance-decay / observability 分级)全部来自 **agent 自己的直接推理**,不是从 cross-domain-inspiration.md 挖出来的 | ❌ 违反 process |
| ⑤ artifact 输出 | 每阶段 emit `artifact.json`(data-audit / design / spec),用 `validate-chain` 校验 | ❌ **没有 emit 任何 artifact.json**。只输出了 Markdown 设计文档 | ❌ |
| ⑥ adversarial-panel-audit | Standard 模式最后 1 round 审计 | ❌ 跳过 | ❌ |

**结论:7 步里只有第 1 步(data-audit)合规。** 后面 5 步全部走了捷径。

---

## 二、SPICE 是怎么"提出"的(诚实还原)

**不是从 brainstorm 流程出来的。** Agent 直接从以下推理链设计了 SPICE:

1. 用户说"不只是 L-R database lookup" → agent 想:核心问题是"不用 DB 怎么定义 signaling evidence"。
2. agent 的空间统计知识 → "用 sender ligand 的空间变异作为 instrument,regress receiver downstream on it"。
3. agent 的因果推断知识 → "control for niche confounders; observational data 只能给 association 不能给 causal"。
4. agent 对 CellChat 的了解 → "CellChat 做 co-expression + permutation,没有 niche control,没有 downstream evidence"。
5. agent 对 Xenium 的了解 → "400 基因 panel 是硬约束,需要 observability 分级"。

**这些推理本身是合理的**(estimand 严格、observability 分级、distance-decay 判别器、kill-switch 都是对的)。**但它们不是从 skills 的结构化流程产出的**——是从 agent 自己的知识直接跳出来的。

**这就是问题:skills 提供了好的 DISCIPLINE(estimand 严格性、failure boundaries、observability——这些框架来自 skills),但 failed on PROCESS enforcement(没走 brainstorm、没 search、没 emit artifact)。**

---

## 三、根因分析

### 根因 1:skills 有 DECLARED 规则,但没有 ENFORCEMENT 机制

| 规则 | 写在哪里 | enforced? |
|---|---|---|
| "Never judge from memory, search first" | topic-viability SKILL.md | ❌ 纯 prose,无 gate。agent 可以直接忽略 |
| "brainstorm BEFORE viability BEFORE design" | using-crossbio-algo SKILL.md | ❌ 纯顺序建议,无 artifact 前置依赖强制 |
| "every R1 claim must be verified" | brainstorm SKILL.md | ❌ 无机器检查(cite 了没有?) |
| "emit artifact.json per stage" | _shared/handoff | ❌ 在 SCOUT example 里做了,但在 live use 里没有强制 |

**对比**:data-audit 的 `fatal_issues` 非空 → validate-chain **机器拒绝** → 这是 enforced。但 viability/brainstorm 的规则没有等价的机器 gate。

### 根因 2:artifact 链在 live loop 里不强制

SCOUT example 里,每个阶段产出 artifact.json + validate-chain 校验。但当 agent **实际用 skills 设计一个新方法**时,它没有 emit 任何 artifact。artifact 链只在 example 里跑,不在 live use 里跑。这导致:
- estimand continuity(rule 1)没人检查。
- failure_boundary → acceptance trace(rule 2)没人检查。
- provenance(rule 5)不存在。
- 整个 design 是"自洽但未经机器校验"的——正好是 framework 要防的。

### 根因 3:skills 没有"自我审计"步骤

adversarial-panel-audit 审的是**产出物**(design / spec / result),不是**过程**("你走了 brainstorm 吗?你 search 了吗?你 emit artifact 了吗?")。没有任何 skill 检查 agent 是否**遵循了流程本身**。

### 根因 4:构建 skills 的 agent 自己第一个违反

这本身是一个重要发现:**skills 的规则强度不足以约束一个"自信"的 agent。** 当 agent 觉得自己"知道答案"(对 CCC 领域有知识)时,它会跳过结构化流程直接产出。这和 skills 想防的"self-consistent but wrong"是同一个失败模式的变体——只是这次是 **process-level** 而非 **artifact-level**。

---

## 四、Skills 需要的改进(具体、可操作)

### 改进 1:给 viability 加一个 search GATE(同 data-audit 的 fatal_issues)

**现状**:viability 说"search first"但是 prose。
**改进**:在 topic-viability 的 artifact 里加 `search_performed: bool` + `sources_cited: [url...]`。如果 `search_performed == false` → **validate-chain 报 ERROR**(同 fatal_issues 语义)。不允许没搜就进 design。

### 改进 2:artifact 前置依赖(没有 brainstorm/viability artifact → 不允许 design artifact)

**现状**:顺序写在 SKILL.md 里,不强制。
**改进**:在 schema 的 stage_fields 里,design artifact 的 `parent_artifact_id` 必须指向 viability 或 data-audit。如果 design 没有前置 artifact parent → validate-chain **拒绝**。这强制了流程顺序。

### 改进 3:live-loop artifact emission 设为 DEFAULT(不只是 example)

**现状**:SCOUT example emit artifact;live use 不 emit。
**改进**:在 using-crossbio-algo SKILL 里加硬规则:**"Every stage MUST emit artifact.json to a runs/ directory; the final output must include `crossbio validate-chain` output."** 加一个 `check_process` 命令到 run_benchmark:verify the artifact chain exists for a design run。

### 改进 4:加一个"process audit" skill(或 adversarial-panel-audit 的扩展)

**现状**:audit 审产出物,不审流程。
**改进**:adversarial-panel-audit 加一个 reviewer-role:**"process-auditor"** —— 检查:
- Did you search before claiming competitors?
- Did you run brainstorm (or justify skipping)?
- Did you emit artifacts?
- Did you validate-chain?
如果任一 No → finding (blocking)。

### 改进 5:brainstorm SKILL 加"mandatory if skipped, justify" 规则

**现状**:brainstorm 是 Standard 模式跳过的(Publication 才跑)。
**改进**:即使 Standard 跳过 brainstorm,也要 emit 一个 `{brainstorm_skipped: true, reason: "user has single idea"}` artifact——不是"无声跳过",而是"显式记录跳过 + 理由"。

---

## 五、这份报告对 v0.3 benchmark 的意义

这次 CCC 设计过程**本身就是一个 benchmark 数据点**——而且是 **no-skill 的行为**(agent 跳过了 skills 的核心流程,虽然它"知道"这些规则)。

如果把这个 CCC 设计放进 v0.3 benchmark 的 no-skill 槽:
- agent(作为 no-skill)产出了一个自洽的设计(SPICE)。
- 但 competitor list 来自记忆(可能漏/错)。
- 没走 brainstorm(可能错过了更好的方向)。
- 没 emit artifact(不可机器校验)。
- 没有 search-performed 的证据。

**如果 Standard 模式正确执行**,它应该:
- search PubMed → 发现 CellWHISPER (2026)、Spacia (multiple-instance learning)、GAT-co-attention 等记忆里没有的工具。
- 走 brainstorm R1-R5 → 可能发现 SPICE 不是唯一/最好的方向。
- emit artifact chain → validate-chain 机器校验。

**这就是 no-skill vs Standard 的真实 delta——不是 rubric 分数,而是流程合规性 + 文献覆盖度。**

---

## 修正(评审反馈后)

原报告将 SPICE 标记为 "no-skill"。修正:**SPICE 是 treatment-noncompliant**(agent 加载了 skills,
estimand/observability/kill-switch 的纪律影响了产出,但跳过了 search/brainstorm/artifact/audit)。
这比 no-skill 更重要——它测量 **adherence rate**:skills 存在时 agent 实际遵守流程的概率。

Benchmark 应增加 ITT vs per-protocol 分析(intention-to-treat vs per-protocol):
- ITT: 分配到 Standard 就算 treatment(不管是否遵守)→ 测总体部署效果
- per-protocol: 只比真正完成 Standard pipeline 的 run → 测 skills 本身效力
如果 per-protocol 效果大但 ITT 小 → 问题在 enforcement,不在 skill 效力。

SPICE 的 IV(instrumental variable)有 identifiability 问题:sender ligand spatial variation
不自动满足 IV 条件(relevance + exclusion restriction + independence)。ligand 表达受 hypoxia/
cell-state/niche 影响 → 这些也影响 receiver response → IV 可能无效。这正是"聪明的跨域类比
最容易生成漂亮但不可识别的方法"的标准案例,也是 literature search + adversarial audit 必要性的证据。

v0.3.1 修复方向(已实施): state-machine-enforced workflow(run-manifest + crossbio next/finalize)。

## 六、一句话总结

> crossbio-algo 的 skills 提供了正确的 discipline(estimand / failure boundaries / observability / kill-switch),但缺少 **process enforcement**(search gate / artifact-chain-in-live-loop / process-audit)。一个"自信"的 agent(包括构建 skills 的 agent 自己)会跳过流程直接产出——产出的质量可能很高,但 evidence chain 是断裂的(没 search、没 artifact、没 validate)。**这是 v0.3.1 最该修的。**
