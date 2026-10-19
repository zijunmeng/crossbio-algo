# crossbio-algo v0.4.0：方法学张力发现与可证伪假设生成

## 开发规格说明书（SPEC）

-   **状态**：Proposed / 待实施
-   **目标版本**：v0.4.0（建议；若实施过程中出现破坏性 schema
    变更，应重新评估版本号）
-   **基线版本**：crossbio-algo v0.3.2
-   **目标仓库**：https://github.com/zijunmeng/crossbio-algo
-   **建议文件路径**：`docs/specs/2026-10-19-method-tension-miner.md`
-   **核心交付**：新增 `method-tension-miner`
    Skill；将方法学张力产物接入现有 artifact
    链、brainstorm、算法设计、对抗审查和 benchmark。
-   **非目标**：本次不重写 auto-sc、不构建通用多 Agent
    平台、不承诺自动"发明理论"，也不以增加 Skills 数量作为成功标准。

------------------------------------------------------------------------

## 1. 执行摘要

crossbio-algo v0.3.2 已经具备数据与 estimand
审计、范式发散、竞品深比较、算法设计契约、对抗审查、spec 生成、artifact
provenance、状态机和
validator。下一阶段不应简单增加更多提示词，而应补上一个目前尚未被独立定义、输出和评估的能力：

> **从可追溯的文献证据中发现方法学张力，并把张力转化为能够被实验区分的竞争性假设。**

本 SPEC 提议增加 `method-tension-miner`，并对现有 Skills 与 validator
做最小必要改动。新模块应发现并区分：

1.  文献已经报告的实证结果矛盾；
2.  两种方法依赖的假设可能不兼容；
3.  不同数据条件分别被研究过、但其交互条件尚未被直接检验；
4.  现有分析流程可能丢失的信息；
5.  方法的 estimand 不一致，导致看似冲突、实则回答不同问题；
6.  可识别性或适用边界尚未明确的情形。

**没有发现合格张力是允许的输出。**
系统不得为了满足数量要求而虚构矛盾，也不得将"检索未发现论文"直接表述为"此前无人研究"。

本次成功标准不是"产生更多创意"，而是：相较当前
v0.3.2，在相同研究主题、文献范围、模型预算与运行次数下，增强版能否产出更多经盲审判定为证据充分、非明显重复、具有明确可证伪预测且值得实验检验的研究假设。

## 2. 背景与当前基线

根据当前公开仓库 README，v0.3.2 的主要能力包括：

-   三档工作模式：Quick、Standard、Publication；
-   `data-and-estimand-audit` 作为不可跳过的根节点；
-   `brainstorm` 的范式发散要求；
-   `topic-viability-assessment` 的竞品深比较；
-   `algorithm-design` 的结构化设计契约；
-   `adversarial-panel-audit`；
-   `spec-writing`；
-   `artifact.json`
    链、provenance、父子关系、阶段顺序和部分内容规则验证；
-   `run-manifest` 状态机、显式 skip 原因以及 source-bound test
    attestation；
-   现有 skill-effectiveness benchmark 和 SCOUT 端到端示例。

当前架构已能约束"怎样把方法研发做得更规范"，但需要单独检验它是否能改善"怎样找到更有价值的方法学问题"。新增模块应复用现有纪律，而不是另建一套互不兼容的流程。

## 3. 目标、非目标与设计原则

### 3.1 目标

1.  从方法论文、综述、补充材料、基准研究和代码中提取结构化方法证据。
2.  识别并分类方法之间的张力，明确哪些是直接证据、哪些是推论、哪些只是待验证的空白。
3.  为每条张力提供可追溯证据、可能机制、竞争解释、可观测预测和证伪标准。
4.  将合格张力作为 `brainstorm`
    的一种输入来源，但不排斥自由探索、跨领域迁移或用户已有的研究假设。
5.  通过现有 validator
    和状态机保证阶段产物可追溯、可校验、不能静默跳过。
6.  建立对照 benchmark，检验新增模块的增量价值。
7.  支持证据不足时诚实停止、缩小问题范围或回退到原有工作流。

### 3.2 非目标

-   不宣称系统能自动生成真正原创的科学理论。
-   不把每个文献局限都转化成新方法项目。
-   不要求所有研究方向必须跨领域借鉴。
-   不强制每次运行都必须发现方法学张力。
-   不将 LLM 自评分作为创新性的主要证据。
-   不在 v0.4.0 建设覆盖所有生物医学实体的通用知识图谱。
-   不默认新增 GPU 依赖；首版以 CPU 可执行的检索、结构化和轻量验证为主。
-   不重写现有 validator、artifact 链或三档模式。
-   不把"尚未检索到相关工作"当作"首次提出"的证据。

### 3.3 设计原则

**P1. Utility first, novelty explicit。**
新颖性是显式审查维度，但不能凌驾于问题价值和可验证性之上。

**P2. Tension is not an evidence gap。**
未被比较不等于方法冲突；空白只有在明确说明潜在机制与可检验后果时才成为研究候选。

**P3. Facts, inferences, and hypotheses must be separated。**
文献事实、跨文献推论、待验证假设必须使用不同状态标签。

**P4. Falsifiability must be operational。**
每条合格张力至少对应一个可观测预测、一个区分竞争解释的实验，以及明确的否证结果。

**P5. No forced novelty。** 找不到高质量张力时必须报告
`NO_QUALIFIED_TENSION`，而不是凑数。

**P6. Validator checks structure, not scientific truth。** validator
能检查字段、引用、链接和追溯关系，但不能自动证明论文解读正确或方法真正原创。

**P7. Keep the existing discovery paths。**
张力驱动只是创新来源之一，不替代用户问题、领域知识、范式发散和跨领域灵感。

## 4. 用户故事

-   **US-01：方法开发者**希望 AI
    不只是总结"现有方法的局限"，而是能定位不同方法假设之间可研究的冲突。
-   **US-02：研究者**希望知道一条张力来自原文的直接报告、跨论文推论，还是仅仅来自检索空白。
-   **US-03：方法开发者**希望每个候选方向都包含能区分新旧解释的实验，而不是只包含算法名称。
-   **US-04：项目维护者**希望新增 Skill 与现有 artifact、状态机和
    validator 一致，旧项目仍然可验证。
-   **US-05：评估者**希望能比较当前版和增强版的输出质量，且评价不完全依赖同一个
    LLM。
-   **US-06：用户**希望在没有合格张力时仍可继续常规研发，不被流程强迫制造创新。

## 5. 新增模块与总体流程

### 5.1 新 Skill

新增目录：

``` text
skills/method-tension-miner/
├── SKILL.md
├── templates/
│   └── tension-record.example.json
└── references/
    ├── tension-taxonomy.md
    └── evidence-quality-rules.md
```

具体文件可根据仓库现有的 Skill 目录约定调整，但必须保持 Skill
frontmatter、触发描述和插件 manifest 约定一致。

### 5.2 建议流程

``` text
data-and-estimand-audit
        |
        v
method-tension-miner  [按运行模式决定 required / optional / skipped]
        |
        v
brainstorm  <--- tension cards + user problem + paradigm divergence + cross-domain ideas
        |
        v
topic-viability-assessment
        |
        v
adversarial-panel-audit
        |
        v
algorithm-design
        |
        v
adversarial-panel-audit
        |
        v
spec-writing
        |
        v
adversarial-panel-audit
        |
        v
code / benchmark / source-bound attestation
```

`method-tension-miner` 产物必须进入 artifact 链；不得只写一份游离的
Markdown 报告。

### 5.3 三档模式策略

  -----------------------------------------------------------------------------------------------------------------------------------------------
  模式                    新 Skill 策略                                        规则
  ----------------------- ---------------------------------------------------- ------------------------------------------------------------------
  Quick                   默认跳过；用户显式要求发现新方向时可启用窄范围扫描   必须写明 skip reason；不得增加默认成本

  Standard                条件启用                                             若用户给定明确
                                                                               idea，可跳过；若任务是"找新方向/创新方法/探索未解决问题"，应运行

  Publication             必须运行                                             若未找到合格张力，需输出完整的搜索范围与
                                                                               `NO_QUALIFIED_TENSION`，之后允许原有 brainstorm 继续
  -----------------------------------------------------------------------------------------------------------------------------------------------

状态机必须从 run manifest
中读取该阶段的策略，不能仅根据目录中是否存在文件推断阶段是否应该运行。对必须运行的阶段，不能用普通
skip 绕过；若因检索不可用等原因无法完成，应以显式 `blocked`
或现有等价状态记录原因，并由 validator 阻止将该 run 标记为完整合规。

## 6. `method-tension-miner` 的功能需求

### FR-01：输入范围定义

Skill 开始前应记录：

-   研究问题及预期的生物学用途；
-   目标数据模态与 data
    regime（如稀疏度、样本量、批次结构、空间分辨率、重复设计等）；
-   当前已知的候选方法（若有）；
-   目标研究等级或项目类型；
-   文献时间范围、可用检索渠道、检索预算；
-   用户明确给定的约束（如 CPU-only、Python 生态、可用样本等）。

缺失关键范围时，先明确假设与限制；不得把未提供的条件伪装成已知事实。

### FR-02：提取方法卡片

每种方法至少提取：

-   研究目标与 target estimand；
-   分析单位；
-   输入表示与关键变换；
-   统计/生物学假设；
-   适用数据条件；
-   作者实际验证过的条件；
-   已报告的失败模式；
-   基准对照及其公平性；
-   原始论文、补充材料、实现代码和版本；
-   证据定位信息。

不能仅依据摘要推断算法细节。关键假设应尽可能回到原始方法论文、补充材料或源代码核实。

### FR-03：张力分类

每条张力必须属于以下一种主类型，可带辅助标签：

1.  `empirical_contradiction`：不同研究在可比条件下报告了不一致结果。
2.  `assumption_conflict`：两种方法的基础假设在特定 data regime
    下可能不兼容。
3.  `unvalidated_interaction`：多个数据条件分别被研究，但它们共同出现时的影响尚未直接验证。
4.  `information_loss`：现有表示、汇总或离散化可能丢失与目标问题相关的信息。
5.  `estimand_mismatch`：方法回答的目标不同，造成结果不可直接比较。
6.  `identifiability_boundary`：数据设计可能不足以区分多个机制或参数解释。
7.  `benchmark_blind_spot`：现有基准未覆盖一个对目标应用关键的条件。

### FR-04：证据状态分类

每条张力必须具有一个 `evidence_status`：

-   `observed`：原始来源直接报告了该现象或矛盾。
-   `literature_inferred`：基于多个有来源的事实推导，原文未直接提出该张力。
-   `unverified`：合理但尚未被足够证据支持的候选问题。
-   `no_qualified_tension`：在声明的检索范围内未找到达到门槛的张力。

不得把 `unverified`
写成既定事实；不得把"没有找到论文"写成"文献证明不存在"。

### FR-05：生成机制解释和竞争假设

对 `observed` 或 `literature_inferred`
的张力，应至少提出一个可检验的机制解释；对重要张力，尽量提出至少两个竞争解释。每个解释必须说明：

-   依据哪些证据；
-   关键假设是什么；
-   哪些数据条件会让它成立或失效；
-   它与其他解释的可观测区别；
-   可能的替代解释（如样本构成、测量误差、预处理差异、estimand
    不一致）。

### FR-06：可区分的预测

每条进入候选池的张力必须至少包含：

-   一个可观测预测；
-   一个最小判别实验；
-   一个明确的否证标准；
-   预期结果对方法选择或科学解释的影响。

仅写"在更多数据中验证""比较多个算法"不算判别实验。实验必须说明什么结果支持哪个解释，以及什么结果会否定该解释。

### FR-07：新颖性状态

新颖性字段只允许使用：

-   `known_related_work`：找到实质相关工作；
-   `possible_overlap`：有近似工作，需要人工判定；
-   `not_found_in_scoped_search`：在明确范围内未找到，但不能声称首次；
-   `expert_review_required`：需要领域专家判断。

必须记录搜索日期、查询式、检索源和关键近似方法。禁止单凭相似关键词检索无结果就宣称"首次提出"。

### FR-08：停止与回退

如果未找到合格张力：

1.  输出 `NO_QUALIFIED_TENSION`；
2.  列出实际检索的来源、查询式、日期、覆盖范围和限制；
3.  区分"没有发现"与"证据不足"；
4.  不阻止后续原有 brainstorm 使用用户问题、范式发散和跨领域探索；
5.  不自动生成空泛的创新方向来满足数量要求。

## 7. Artifact 数据契约

新增 stage 名称建议为 `method_tension`。所有通用字段（例如
`artifact_id`、`run_id`、`parent_artifact_id`、`provenance_hash`、时间戳及
schema version）应沿用现有 `stage-schemas.json` 的 canonical
定义，不另建第二套公共 envelope。

建议的 stage-specific 结构如下：

``` json
{
  "stage": "method_tension",
  "scope": {
    "research_question": "string",
    "data_regime": ["string"],
    "target_tier": "T1|T2|T3|T4",
    "literature_cutoff_date": "YYYY-MM-DD"
  },
  "search_protocol": {
    "sources": ["string"],
    "queries": ["string"],
    "searched_at": "YYYY-MM-DD",
    "coverage_limitations": ["string"]
  },
  "method_cards": [
    {
      "method_id": "M1",
      "name": "string",
      "estimand": "string",
      "analysis_unit": "string",
      "assumptions": ["string"],
      "validated_regimes": ["string"],
      "reported_limitations": ["string"],
      "evidence_refs": ["E1"]
    }
  ],
  "evidence_items": [
    {
      "evidence_id": "E1",
      "source_type": "primary_paper|review|supplement|code|benchmark",
      "title": "string",
      "year": 2025,
      "doi_or_url": "string",
      "locator": "section/table/figure/code path",
      "claim_supported": "string",
      "evidence_strength": "direct|indirect",
      "notes": "string"
    }
  ],
  "tensions": [
    {
      "tension_id": "TENS-001",
      "type": "assumption_conflict",
      "evidence_status": "observed|literature_inferred|unverified",
      "claim": "string",
      "method_refs": ["M1", "M2"],
      "evidence_refs": ["E1"],
      "mechanism_hypotheses": [
        {
          "hypothesis": "string",
          "supporting_evidence_refs": ["E1"],
          "alternative_explanations": ["string"]
        }
      ],
      "predictions": ["string"],
      "discriminating_experiment": "string",
      "falsification_criteria": ["string"],
      "impact_if_true": "string",
      "impact_if_false": "string",
      "novelty_status": "possible_overlap",
      "nearest_related_work": ["string"],
      "confidence_rationale": "string"
    }
  ],
  "result_status": "qualified_tensions_found|no_qualified_tension|blocked",
  "limitations": ["string"]
}
```

以上是逻辑示例，不是要求复制替换现有 schema。实现时必须遵守当前 schema
的命名、枚举和公共字段约定；若现有 schema 已有等价字段，优先复用。

## 8. 与现有 Skills 的集成要求

### 8.1 `brainstorm`

-   增加可选输入：`method_tension` artifact。
-   候选 idea
    应记录来源：`tension_ids`、`user_problem`、`paradigm_divergence`、`cross_domain_transfer`
    或组合。
-   不要求所有 idea 都来自张力；避免系统只会沿着已知文献中的矛盾思考。
-   对张力驱动的 idea，必须说明新 idea 如何回应张力，以及是否引入了新的
    estimand、分析单位、数据表示或推断机制。
-   继续执行 v0.3.2 的范式发散规则；不能因张力输入而跳过替代范式。

### 8.2 `topic-viability-assessment`

-   将 tension
    的近似方法和来源文献作为竞品检索起点，而不是作为竞品检索的终点。
-   明确区分"研究问题相同""estimand
    相同""核心机制相似""只共享技术组件"。
-   对 `possible_overlap` 和 `not_found_in_scoped_search`
    强制标记人工复核需求。
-   若发现直接竞品，应允许 idea
    回退或重构，而不是仅通过更换名称或添加模块规避撞车。

### 8.3 `algorithm-design`

对 tension-derived idea 增加以下承重字段：

-   `tension_resolution`：新方法如何回应张力；
-   `competing_explanations`：要区分的机制或解释；
-   `discriminating_predictions`：不同解释的不同预测；
-   `minimum_discriminating_experiment`：最小判别实验；
-   `kill_criteria`：哪些结果要求放弃、简化或重构方法；
-   `incremental_vs_structural_claim`：核心贡献属于工程改进、方法改进、分析范式变化还是新增分析能力。

这些字段应被后续 spec 和 acceptance tests
追溯，不能只存在于头脑风暴文档。

### 8.4 `adversarial-panel-audit`

新增或调整一个审查角色 `methodological-skeptic`，重点检查：

-   所谓张力是否只是 estimand 不同；
-   是否忽略了原文中的适用条件；
-   是否将缺少比较误写成实证矛盾；
-   机制解释是否只是事后合理化；
-   实验是否真的能区分竞争解释；
-   新方法是否可能被现有简单方法以更低复杂度实现；
-   新颖性陈述是否超出检索证据。

### 8.5 `spec-writing`

-   将假设、预测、判别实验和 kill criteria 传递到
    requirements/design/tasks。
-   每个重要 claim 必须对应验收标准或被明确标记为未经验证的科学假设。
-   对尚未验证的理论命题，不允许在 spec 中改写成确定性结论。

## 9. Validator 与状态机改动

### 9.1 Schema

-   在 `crossbio_validate/schemas/stage-schemas.json` 中新增
    `method_tension` stage schema。
-   使用现有公共 envelope、枚举与 provenance 约定。
-   若 schema 有严格 `oneOf` 或 stage-order 规则，补充相应分支。
-   旧的 v0.3.2 artifact 必须仍可验证；不要通过破坏性字段改名强迫历史
    run 迁移。

### 9.2 状态机

-   在 run manifest 中为 `method_tension` 声明 `required`、`optional` 或
    `skipped` 策略。
-   Publication 默认 required；Standard 按是否为发现型任务决定；Quick
    默认 skipped。
-   required 阶段若无法执行，状态必须是 blocked/failed
    或仓库现有等价状态，不能以静默 skip 通过 finalize。
-   optional/skipped 必须记录 `reason_code` 与 justification。
-   `crossbio next`、`complete-stage`、`skip-stage`、`finalize`
    应遵守该策略。
-   不允许因新 stage 破坏现有 stage-order 和 parent-chain 校验。

### 9.3 内容校验规则

新增的机器规则至少包括：

1.  所有 `evidence_refs` 必须引用 artifact 中存在的 evidence ID。
2.  所有 `method_refs` 必须引用存在的 method card。
3.  `empirical_contradiction`
    必须有可定位的直接证据；若只有间接推论，必须改标
    `literature_inferred`。
4.  `assumption_conflict` 必须明确列出双方假设及冲突发生的 data regime。
5.  `unvalidated_interaction`
    必须记录每个条件分别有何证据，以及检索范围和未覆盖之处。
6.  每条合格 tension 必须有 prediction、discriminating experiment 和
    falsification criteria。
7.  `not_found_in_scoped_search` 必须附带搜索范围、日期和检索式。
8.  `no_qualified_tension` 允许 tensions
    为空，但必须有搜索记录和限制说明。
9.  任何 `novelty_status` 都不能由 validator
    自动升级为"first/novel"；validator 只检查字段和证据链。
10. 若后续 idea 声称源自某 tension，其 `tension_ids` 必须可解析到父
    artifact。
11. 重要的 hypothesis → design → acceptance criterion → test/result
    关系继续沿用现有 executable-trace 规则。
12. validator
    必须明确提示：结构通过不代表科学结论正确，也不代表新颖性已被证实。

## 10. 验收标准

### AC-01：可追溯性

**Given** 一个包含至少两种方法和多篇来源的研究主题，\
**When** `method-tension-miner` 完成，\
**Then** 每条张力都能追溯到具体证据 ID、来源和定位信息；不存在悬空引用。

### AC-02：事实与推论分离

**Given** 原文没有直接声称两种方法互相矛盾，\
**When** Skill 根据不同论文推导潜在冲突，\
**Then** 产物必须标记为 `literature_inferred`，并写出推导链，不能标为
`observed`。

### AC-03：不能把未比较等同于冲突

**Given** 两种方法从未在同一数据条件下直接比较，\
**When** Skill 发现该文献空白，\
**Then** 只能生成 `unvalidated_interaction`
或相应的待验证标签；必须提出机制解释和判别实验，不能直接宣称两种方法互相矛盾。

### AC-04：无合格张力时可诚实退出

**Given** 搜索后没有满足质量标准的张力，\
**When** Skill 完成，\
**Then** 输出
`no_qualified_tension`、检索范围、查询式和局限；Publication
流程可继续原有 brainstorm，但不能伪造张力。

### AC-05：状态机与模式兼容

-   Quick 默认可显式 skip 新 stage；
-   Standard 根据 discovery policy 正确 required/optional/skip；
-   Publication 无法静默跳过；
-   旧版 v0.3.2 artifact 链仍通过历史兼容测试。

### AC-06：设计追溯

**Given** 某 idea 来自 `TENS-001`，\
**When** idea 进入 algorithm-design 和 spec-writing，\
**Then** tension ID、核心预测、判别实验和 kill criteria 在后续 artifact
中可追溯。

### AC-07：复杂度淘汰机制不回退

如果实验显示新增模块或算法组件不优于更简单的基线，应沿用现有
`remove_or_redesign` 规则，不允许以"理论创新"为由豁免。

### AC-08：可重复运行

固定输入、检索快照和配置后，benchmark harness 能记录模型、提示词/Skill
版本、文献范围、预算、时间、token 用量和输出
artifact。随机性允许导致内容不同，但记录必须可复核。

## 11. Benchmark 设计

### 11.1 研究问题

主要问题：新增 `method-tension-miner`
是否提高了高质量方法学假设的产出率，而不是仅提高 artifact
合规率或文本长度？

### 11.2 对照组

-   **A：No-skill**：相同主题与资源预算，不加载 crossbio-algo。
-   **B：Current**：当前 v0.3.2 工作流。
-   **C：Enhanced**：v0.4.0，启用 method-tension-miner 及集成改动。

三组尽量保持模型版本、系统提示、检索工具、上下文预算、时间预算和可用文献范围一致。记录任何无法完全匹配的因素。

### 11.3 分阶段实验

**Pilot：** 选择 3
个差异明显的领域（建议包括一个单细胞/空间组学领域、一个非本领域案例、一个网络或扰动分析案例），每个领域每组运行
3 次，共 27 次。先验证评分标准、harness 和成本。

**Expansion：** 在 pilot 规则冻结后扩展到仓库已有的 8 个 benchmark
domain；建议每组每领域至少 5
次独立运行。若成本受限，应报告实际运行数，不得将小样本结果包装为稳健结论。

### 11.4 主要终点

主要终点建议为 **Qualified Hypothesis Yield（合格假设产出率）**：每次
run
中通过预注册硬门槛、且经盲审认为值得进一步实验检验的独立候选假设数量。

合格假设必须同时满足：

1.  有可追溯证据，不存在关键来源幻觉；
2.  与最接近已有工作有明确、实质性的差别，或清楚标记为尚需新颖性复核；
3.  机制解释明确，且不只是更换常见算法/参数；
4.  有能够区分竞争解释的可执行实验；
5.  有明确的失败标准；
6.  研究问题有实际价值，且与可用数据相匹配。

不要把"被 AI 自己打高分"作为合格依据。

### 11.5 次要终点

-   tension 的证据支持率；
-   将 evidence gap 错误标成 contradiction 的比例；
-   未经证据支持的新颖性过度声称率；
-   近似/重复候选比例；
-   专家对重要性、新颖性、可证伪性、可行性和证据质量的盲评；
-   产出一个合格假设的时间与 token 成本；
-   从假设到可运行原型的转化比例；
-   结果在不同领域和不同运行之间的稳定性。

### 11.6 盲审规则

-   评审者不知道输出来自哪一组；
-   至少两名领域评审者独立评分；条件允许时增加第三名；
-   LLM judge 可用于辅助筛查，但不能作为主要证据；
-   预先固定评分 rubric 和判定阈值；
-   报告分歧、失败案例和置信区间，不只报告均值；
-   区分"历史回溯成功"（重新发现后来已发表的方法）与"前瞻性原创贡献"。

### 11.7 结果解释边界

即使 Enhanced 组显著优于
Current，也只能说明该机制在已测试条件下改善了候选假设质量，不能直接证明系统自动发明了新理论。要证明实际方法创新，还需要选取候选方向完成数学分析、算法实现、独立基准和真实数据验证。

## 12. 实施任务拆分

### Phase 0：冻结基线与测试计划

-   [ ] 记录当前 git commit、版本号、现有 tests 和 benchmark 配置。
-   [ ] 保存 v0.3.2 的 benchmark 运行配置与输出。
-   [ ] 预先确定 pilot 的领域、模型、预算、评分 rubric 和主要终点。
-   [ ] 确认当前 schema、manifest 与 stage-order
    实现，避免凭文档猜测内部接口。

**验收：** 能在干净环境重跑现有测试；基线结果与配置归档。

### Phase 1：数据契约与 validator

-   [ ] 在 canonical stage schema 中新增 `method_tension`。
-   [ ] 定义 tension taxonomy、evidence status、novelty status 枚举。
-   [ ] 实现引用完整性、状态逻辑和实验字段检查。
-   [ ] 更新状态机以支持 required/optional/skipped policy。
-   [ ] 增加旧 artifact 兼容测试和负例 fixture。

**验收：** 合法 fixture
通过；悬空引用、缺失证伪标准、无搜索记录的"未发现"状态等负例失败；旧链仍然可验证。

### Phase 2：实现 Skill

-   [ ] 新建 `skills/method-tension-miner/SKILL.md`。
-   [ ] 新建 taxonomy 与 evidence-quality references。
-   [ ] 定义检索范围、来源优先级和 evidence capture 规则。
-   [ ] 定义 no-qualified-tension、blocked 和 fallback 行为。
-   [ ] 为新 Skill 添加 frontmatter、触发说明和示例。
-   [ ] 更新 plugin manifest、入口 Skill 和相关文档。

**验收：** 能在 3 个试点主题上生成 schema-valid
artifact；不能把检索空白直接标成实证冲突。

### Phase 3：集成现有 Skills

-   [ ] 更新 `brainstorm` 接收 tension artifact 并记录 idea 来源。
-   [ ] 更新 `topic-viability-assessment`
    对张力相关工作的去重和竞品审查。
-   [ ] 更新 `algorithm-design` 传递预测、判别实验和 kill criteria。
-   [ ] 更新 `adversarial-panel-audit` 的 methodological-skeptic
    检查项。
-   [ ] 更新 `spec-writing` 的假设到验收标准追溯。
-   [ ] 更新 `_shared` handoff contract，保证跨阶段引用一致。

**验收：** tension-derived idea
能端到端追溯到设计、spec、测试和结果；独立 idea 仍可正常运行。

### Phase 4：测试与示例

-   [ ] 新增 schema、validator、process、integration tests。
-   [ ] 新增至少 3 个 tension fixture：真实文献矛盾、假矛盾（estimand
    不同）、纯 evidence gap。
-   [ ] 新增一个负结果
    fixture：初始假设被实验否定，系统正确记录并放弃/简化方法。
-   [ ] 将测试加入 CI。
-   [ ] 更新 README、CHANGELOG、PROJECT_SUMMARY 和版本单源测试。

**验收：** 所有新旧测试通过；文档、manifest、pyproject、CITATION
和版本号保持一致。

### Phase 5：Benchmark pilot

-   [ ] 实现 A/B/C 三组运行 harness。
-   [ ] 记录模型、配置、文献快照、预算、token、时间和 artifact。
-   [ ] 完成 27 次 pilot，或清楚记录实际偏离。
-   [ ] 进行盲审，计算主要与次要终点。
-   [ ] 公开报告失败案例、成本和局限。

**验收：** 可从原始输出重算指标；评分者不知道组别；结果不依赖单一 LLM
自评。

### Phase 6：发布决策

只有满足以下条件才建议将新模块作为默认 Publication 路径发布：

-   schema、状态机和兼容测试通过；
-   至少 3 个领域端到端运行成功；
-   未发现系统性将 evidence gap 误报为 contradiction 的问题；
-   benchmark 数据完整且能复核；
-   盲审显示合格假设质量有积极信号，或清楚说明未观察到改善并据此修订设计。

若质量未改善，不应仅凭 Skill
已完成开发就发布为"创新能力增强版"；应分析失败来源并允许回退。

## 13. 风险与缓解

  --------------------------------------------------------------------------------
  风险                                缓解策略
  ----------------------------------- --------------------------------------------
  Novelty                             不强制数量；独立 novelty status；对抗审查
  theater：为了显得创新而夸大矛盾     

  引用幻觉或引用不能支持主张          记录精确定位；优先原始论文；抽样人工核验

  将未比较误判为冲突                  强制区分 contradiction、assumption conflict
                                      与 unvalidated interaction

  过度依赖跨领域类比                  跨领域仅作为候选来源；必须形式化迁移假设

  新阶段让所有任务变慢                Quick 默认跳过；Standard
                                      条件启用；Publication 必须运行

  validator 误被理解为科学背书        明确其只验证结构和追溯，不验证真理或原创性

  同模型自评导致偏差                  专家盲审为主要评价；LLM judge 只作辅助

  benchmark 泄题或领域过窄            独立 holdout
                                      任务、冻结陷阱、扩大领域与重复次数

  新 Skill 输出很多但无实际价值       以 Qualified Hypothesis Yield
                                      与原型转化率评价

  schema 变更破坏旧 run               向后兼容、版本化迁移、保留历史 fixture
  --------------------------------------------------------------------------------

## 14. 发布、版本与文档

建议目标版本为 `v0.4.0`，前提是实现保持对旧 artifact 的兼容，且新 stage
是增量能力。若必须破坏旧 schema 或状态机契约，应重新评估版本策略。

需要同步检查：

-   `pyproject.toml`
-   `.claude-plugin/plugin.json`
-   `CITATION.cff`
-   `CHANGELOG.md`
-   `README.md`
-   `PROJECT_SUMMARY.md`
-   `TRIGGERING.md`
-   `CLAUDE.md`
-   CI 中的版本单源和 schema 检查

所有新增 Skills
必须有清晰的触发条件、输入、输出、禁止行为和失败回退规则。文档中必须明确区分"测试通过""方法有用""方法原创"三个不同结论。

## 15. 完成定义（Definition of Done）

本 SPEC 只有在以下事项全部满足后才算完成：

-   [ ] 新 Skill 可安装、可触发、可输出合法 artifact。
-   [ ] 新 artifact 被 validator 和状态机正确识别。
-   [ ] Quick、Standard、Publication 的行为符合规定。
-   [ ] 旧版 artifact 和旧测试继续通过。
-   [ ] `brainstorm` 到 `spec-writing` 的张力引用可追溯。
-   [ ] 对真实矛盾、假矛盾、证据空白和无合格张力均有测试。
-   [ ] 至少一个端到端案例包含被否定的假设，并正确执行简化/回退。
-   [ ] benchmark 的 A/B/C 对照可以复现，盲审和评分规则已固定。
-   [ ] README、CHANGELOG、版本文件和 CI 同步。
-   [ ] 发布说明没有把"生成假设"夸大为"自动发现新理论"。

------------------------------------------------------------------------

## 附录 A：交给 Claude Code / Codex 的实施指令

请按本 SPEC 实施 crossbio-algo v0.4.0。先检查当前分支、git status、真实
schema、状态机和 tests；不要根据本 SPEC
猜测内部函数签名。先输出实现计划和可能冲突，再按 Phase 0--6 逐步实施。

约束：

1.  不重写现有架构；优先最小增量修改。
2.  不破坏 v0.3.2 artifact 兼容性。
3.  先实现 schema、validator 和负例测试，再实现 Skill 内容。
4.  所有新行为必须有自动化测试；不要只更新文档。
5.  对无法由机器判断的科学质量问题，必须明确保留人工审查，不得伪装成
    validator 能力。
6.  每完成一个 Phase，运行相关测试并汇报改动、结果、未完成项和风险。
7.  不得为了让测试通过而弱化失败条件或删除负例。
8.  benchmark 结果必须来自实际运行；禁止编造实验数据或专家评分。
9.  若发现本 SPEC
    与当前代码存在冲突，先报告冲突与兼容方案，不要静默改变核心设计。
10. 最终交付：代码、测试、示例 artifact、benchmark
    harness/报告模板、CHANGELOG 和实现偏差报告。

## 附录 B：参考基线

-   Repository: https://github.com/zijunmeng/crossbio-algo
-   当前公开 README 所述基线：v0.3.2
-   当前主要原则：utility-first、novelty explicit、数据/estimand
    审计优先、artifact
    可追溯、状态机禁止静默跳步、复杂度淘汰机制、source-bound test
    attestation。
-   本文档是拟议开发规格，不代表新增能力已经实现，也不代表
    `method-tension-miner` 已被证明能提高原创性。
