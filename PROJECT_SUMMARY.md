# crossbio-algo — 项目总结

> **给评审专家的快速理解文档。** 读这份 + `README.md` + `examples/scout/` 即可全面理解整套体系。

---

## 一句话定位

**跨域生信算法生成闭环**——把一句模糊的研究兴趣，变成经过竞品查证、对抗审计、带失效边界的**可执行算法 spec**。

## 解决什么问题

通用 coding agent（Claude Code / Codex）能跑分析、写代码，但**不会主动做科研诚实纪律**：
- 查证竞品（避免撞车/重造），
- 对抗审计（避免 overclaim），
- 推理外显（避免黑箱），
- 划失效边界（避免假装准）,
- 产出可执行 spec（避免"代码简单"）。

crossbio-algo 把这些固化成一个 **skill 闭环**，让 Claude 在科研任务里**每次必走结构化流程**，而非偶发的好行为。

## 起源

从 **auto-sc**（自主单细胞研究 agent，`/s1/SHARE/mengzijun/01_project/27_bioinfo_auto_research`）提炼——把 auto-sc 最有价值的部分（科研诚实纪律 + 跨域算法发明 + 同模型对抗 panel 审计）从独立 Python 项目提炼成 Claude Code skill 闭环。

---

## Skill 清单（6 skill + 2 共享文件）

| skill | 职责 | 关键设计 |
|---|---|---|
| **using-crossbio-algo** | bootstrap 元 skill | 闭环图 + 触发优先级 + fallback；会话开始让 Claude 知道整套体系 |
| **brainstorm** | 创意引擎 | 5 轮（landscape→gap→cross-domain→ideation→critique + self-critique loop）；dev/research 双模式；dev-mode 每个 idea 含 `algorithm_abstraction`（数学本质+计算模式+推荐跨域）；**famous-algorithm trap**（禁套用已被组学用过的著名算法）+ R5 跨域碰撞检查 |
| **topic-viability-assessment** | 课题评估 | **竞品深度对比表**（逐个查原文：输入/方法/输出/局限/delta/是否直接竞品）；**目标分层 T1-T4**（评分按目标，不单维唱衰）；按**方法学插槽**判直接竞品（不同插槽≠竞品）；禁"看名字判拥挤" |
| **algorithm-design** | 算法设计 | 4 步（数学抽象→跨域灵感→失效边界→simulation-first）；**自主跑 + 推理外显**（不每步问用户，只在全局分叉停）；28 域灵感池；novelty_basis 按目标 tier |
| **spec-writing** | spec 生成 | **kiro 三段式**（requirements.md / design.md / tasks.md）；验收 EARS 记法 + **trace 到 failure_boundary**；tasks 是 bite-sized TDD（真实代码，no placeholder）；**Publication Roadmap**（MVP scope + 工程/实验/写作 gap + 工作量+优先级） |
| **adversarial-panel-audit** | 对抗审计 | **same-model subagent panel**（信息隔离 + 多角色 + 完成各角色 checklist，不强制找 ≥1 问题，避免 critique inflation）；可选 defender/replicator 席位过滤假阳性；每个 finding 结构化（claim/evidence/severity/confidence/reproduction_check/blocking/fix）；agents/*.md 6 角色；结构化裁决（pass/needs_revision/fail）；横切各产出（viability/design/spec/result）；诚实声明同模型盲点 + hybrid 升级路径（混入真外部模型才成为真 cross-model） |
| `_shared/research-design-handoff` | 联动契约 | 完整闭环 + handoff block（各阶段产物传递）+ **fallback 回退机制**（idea 失败→回退剩余候选，不丢弃） |
| `algorithm-design/cross-domain-inspiration` | 28 域灵感池 | 数学本质→科学领域映射表（流体力学/信息论/博弈论/卫星遥感/金融量化/运筹学/宇宙学…）+ 方法池；auto-sc dev-mode 提炼 |

---

## 闭环流程

```
brainstorm  (N candidate ideas; dev-mode 从数学本质跨域发明)
  → topic-viability  (竞品深度对比表 → tier 评分; 禁看名字判拥挤)
      ★ adversarial-panel-audit  (对抗 panel, 信任前必审)
  → algorithm-design  (4 步发明; 自主跑 + 推理外显)
      ★ adversarial-panel-audit
  → spec-writing  (kiro requirements/design/tasks; 验收 ← failure_boundary)
      ★ adversarial-panel-audit
  → code
```
**Fallback**：任一阶段否决一个 idea → 回退到 brainstorm 剩余候选（强制提示"或 dev-mode 再生成"），**永不丢弃已生成候选**。

---

## 关键创新（vs 通用 agent / 现有 bio-agent）

1. **竞品深度对比表 + 插槽判断**——不靠名字/数量判拥挤（实测：spaGRN 评估时"看名字判拥挤"打 0.3，深度对比后修正到 0.55；STARNet 要空间 ATAC vs 只 RNA = 不同插槽，非直接竞品）。
2. **目标分层 T1-T4**——viability 按用户目标评分（T1 顶刊范式创新 / T2 工具论文 / T3 练手 / T4 特定数据），不单维唱衰（同一课题 T1=0.25 / T2=0.55）。
3. **双向对抗审计**——subagent panel 信息隔离 + 强制对抗，既防低估（spaGRN 看名字 0.3 → audit 修正 0.55）也防高估（spatialEnKF "EnKF 跨域空白"0.6 → audit 打到 0.4，DS 换名 EDL 撞车）。
4. **推理外显 + 自主跑**——algorithm-design 区分"用户决策点"（目标/约束/偏好）vs"专业判断"（抽象/方法/参数），自主跑专业判断 + 外显理由，只在全局分叉问用户。
5. **失效边界一等公民**——每个算法必给失效条件 + 机制，spec 验收 trace 到失效边界（不假装准）。
6. **kiro 三段式 spec**——requirements/design/tasks 分离 + bite-sized TDD，治"设计→代码"断层（auto-sc 原 PRD/SPEC 的痛点）。
7. **fallback 回退机制**——idea 失败不丢弃候选（auto-sc broker rollback 在创意层的延伸）。
8. **famous-algorithm trap + R5 跨域碰撞检查**——避免跨域借用撞车（实测：EnKF→Kalman-GRN 占、MVS→PASTE/MOS 占、图小波→BioGSP 占；改进后从 DS/IB/反应扩散等未被用数学结构出发）。

---

## 工程规范（对照 superpowers）

| 维度 | 状态 |
|---|---|
| plugin 化 | ✅ `.claude-plugin/plugin.json` + 目录结构 |
| namespace | ✅ `crossbio-algo:xxx` + `REQUIRED SUB-SKILL`（路径无关） |
| bootstrap | ✅ `using-crossbio-algo` 元 skill + `CLAUDE.md` 模板（SessionStart hook 留用户手动加） |
| per-skill 测试 | ✅ `tests/baseline-tests.md`，6 skill RED（裸 Claude 违反）+ GREEN（skill 补）实测 |
| 去个人化 | ✅ 通用约束（不硬编码 GPU/scanpy/特定数据），example 保留具体方向 |
| demo | ✅ `examples/scout/` 全链（spec + 代码 + 4 测试绿） |
| 文档 | ✅ README + CLAUDE.md + PROJECT_SUMMARY（本文） |
| license | ✅ MIT |

**与 superpowers 对比**：superpowers 是**通用工程纪律**（TDD/debugging/plan），5.1.0 成熟（hook/CI/多 harness）；crossbio-algo 是**科研领域闭环**（brainstorm→竞品查证→对抗审计→设计→spec），v0.1。**科研场景 crossbio-algo 更专**（superpowers 没有竞品查证/对抗审计/失效边界/kiro spec）。工程差距（marketplace/CI/多 harness）是 v0.1 vs 5.1.0 的时间问题。

---

## 验证

**SCOUT demo**（`examples/scout/`）：在"空间多模态数据融合"方向全链跑通——brainstorm（6 idea）→ viability（深度对比，3 撞车否决）→ audit（抓 overclaim）→ fallback → design（6 字段）→ spec（kiro 三段式）→ 代码 → **4 测试绿**。产出 SCOUT（配对-投射空间 RNA+ATAC 整合工具，T2，全 CPU）。

**6 skill baseline 测试**（TDD-for-skills）：每个 skill RED（裸 Claude 行为）+ GREEN（skill 行为）。核心发现——**裸 Claude 内容质量高，skill 补结构化纪律 + 一致性**（查证/抽象/三段式/panel/闭环），把"偶发的好行为"变成"每次必走的流程"。

**全链测洞察**：空间多模态方向 6 个"跨域借用算法"idea（EnKF/MVS/图小波/DS/IB/反应扩散）的命运——揭示 **"跨域借用算法"在 2026 成熟/热领域边际递减**（著名算法多已被组学应用），务实路径是**接受 T2 增量**（成熟方法 + 工程 + 公平 benchmark）。

---

## 状态 + 路线图

**v0.1（当前）**：7 skill 闭环 + 工程规范化 + SCOUT demo + per-skill baseline 测试。本地 git（3 commit），待 push GitHub。

**路线图**：
- 近期：push GitHub + marketplace 注册；slash command（`/crossbio-algo` 显式触发）；SessionStart hook（自动 bootstrap）。
- 中期：per-skill 测试 CI；多方向验证（不只空间多组学）；真实数据 benchmark。
- 长期：跨 harness（Codex/Gemini）；社区贡献；真实用户反馈迭代。

---

## 目录结构

```
crossbio-algo/
├── .claude-plugin/plugin.json        # 插件清单
├── README.md                          # 定位/安装/使用/demo
├── CLAUDE.md                          # bootstrap 模板（用户复制到项目）
├── PROJECT_SUMMARY.md                 # 本文（给评审专家）
├── LICENSE                            # MIT
├── skills/
│   ├── using-crossbio-algo/SKILL.md   # bootstrap 元 skill
│   ├── brainstorm/SKILL.md
│   ├── topic-viability-assessment/SKILL.md
│   ├── algorithm-design/{SKILL.md, cross-domain-inspiration.md}
│   ├── spec-writing/SKILL.md
│   ├── adversarial-panel-audit/{SKILL.md, agents/*.md (6 角色)}
│   └── _shared/research-design-handoff.md
├── examples/scout/                    # SCOUT 全链 demo
│   ├── {requirements,design,tasks}.md
│   └── {scout,test_scout}.py
└── tests/baseline-tests.md            # per-skill baseline 测试规范 + RED 实测
```

---

## 一句话给专家

> crossbio-algo 把"自主科研 agent"最有价值的部分（科研诚实纪律 + 跨域算法发明 + 同模型对抗 panel 审计，诚实非跨模型）提炼成一个 7-skill Claude Code 闭环——从模糊研究兴趣到可执行算法 spec，带竞品查证/双向审计/失效边界/kiro 三段式。已用 SCOUNT demo + 6 skill baseline 测试验证。工程规范化（namespace/bootstrap/测试/去个人化），待 GitHub 发布。
