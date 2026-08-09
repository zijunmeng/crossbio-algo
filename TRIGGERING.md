# crossbio-algo 触发指南

> 本文档说明 7 个 skill 如何自动触发、触发链的顺序、以及手动触发方式。

---

## 机制

Claude Code 在每条用户消息后扫描所有已装 skill 的 YAML frontmatter `description` 字段。
当消息内容与某个 skill 的触发条件匹配时,该 SKILL.md 被自动加载到上下文中。

**你不需要 slash 命令。正常聊研究方向就会触发。**

---

## 触发链(7 个 skill)

### 总览

```
用户提出研究方向
      ↓
using-crossbio-algo (bootstrap, 最高优先)
      ↓
data-and-estimand-audit ✋GATE (所有模式都跑, 不可跳过)
      ↓ (fatal_issues 非空 → 停, 等用户决定)
      ↓
brainstorm (可选: 用户要多个候选时)
      ↓
topic-viability-assessment (评分: 5 类竞品 + 8 维 + plausible range)
      ↓
    ★ adversarial-panel-audit (信任前必审)
      ↓
algorithm-design (16 字段 formal method contract)
      ↓
    ★ adversarial-panel-audit
      ↓
spec-writing (kiro 三段式: requirements / design / tasks)
      ↓
    ★ adversarial-panel-audit
      ↓
code
```

★ = adversarial-panel-audit 是横向 QA 层: 在任何 artifact 被信任前都可以触发。

---

### 各 skill 的触发条件 + 示例

| skill | 触发信号 | 你可以这样说 |
|---|---|---|
| **using-crossbio-algo** | 用户提出研究方向 / 算法 / 工具 / 方法 | "我想做谱系示踪算法" |
| **data-and-estimand-audit** | 有数据 + 研究问题, 在 brainstorm/design 之前 | (由 bootstrap 自动触发, 无需手动) |
| **brainstorm** | 想要多个候选方向 / 找课题 | "这几个方向哪个值得做" / "帮我找课题" |
| **topic-viability-assessment** | 提出一个具体方向, 问值不值得 | "这个 idea 会不会太挤" / "有什么竞品" |
| **algorithm-design** | 要设计新算法 / 新方法 / 新模型 | "帮我设计一个 X 算法" / "现有方法都不行" |
| **spec-writing** | 有 algorithm-design 输出, 要写工程 spec | "写 spec" / "帮我写实现方案" |
| **adversarial-panel-audit** | 任何 artifact 即将被信任 / 用户说"审一下" | "审一下" / "靠谱吗" / "review" |

---

## 三档模式

| 模式 | 跑什么 | 跳什么 | 适用场景 |
|---|---|---|---|
| **Quick** (~30 min) | data-audit → design-lite(4 字段) → tests | brainstorm / viability / full spec / audit | "这 idea 能不能建?" T3/T4 |
| **Standard** (~半天) | data-audit → viability → full design → spec → 1 audit | brainstorm | T2 工具论文(默认) |
| **Publication** (~多天) | full loop: brainstorm → viability → multi-audit → design → spec → benchmark → roadmap | 无 | T1 顶刊 / 完整发表 |

**选择方式**: 用户显式选("快速检查" → Quick,"这是正经论文" → Standard/Publication),或自动从 target tier 推断(T3/T4→Quick, T2→Standard, T1→Publication)。用户随时可覆盖。

**所有模式都跑的**: data-and-estimand-audit(GATE)、artifact 链(estimand 连续 + provenance hash)、honest-colleague 原则。

---

## 实际操作示例

### 示例 1: Quick — 快速可行性检查

```
你: 我想用 graph signal processing 做 scRNA imputation,值不值得做?Quick 模式。

Claude: (触发 using-crossbio-algo → Quick 模式)
        1. data-and-estimand-audit: 审 dropout 机制 (MCAR/MAR/MNAR) + estimand (counterfactual count)
        2. algorithm-design-lite: problem_definition / estimand / objective / failure_boundaries (4 字段)
        3. test sketch: simulation DGP + naive baselines
        → 产出 data-audit artifact + 4-字段 design + test sketch
```

### 示例 2: Standard — T2 工具论文

```
你: 我有配对 scMultiome (RNA+ATAC, 无空间) + Stereo-seq (空间 RNA, 无 ATAC),
     想推断空间 ATAC, 发 T2 工具论文。全 CPU, Python scanpy 生态。

Claude: (触发 using-crossbio-algo → Standard 模式)
        1. data-and-estimand-audit (GATE):
           biological_unit = donor; estimand = 空间 ATAC accessibility;
           leakage_graph = donor-level split; ground_truth 来源审查
           → data-audit.json

        2. topic-viability-assessment:
           5 类竞品表 (SCGLUE / ISON / STARNet / co-accessibility / SCENIC+)
           8 维评分 + plausible range
           → viability verdict

        3. algorithm-design (16 字段 formal method contract):
           objective_or_likelihood / identifiability / failure_boundaries /
           simulation_dgp / benchmark_protocol / novelty_or_utility_basis
           → design.json

        4. spec-writing (kiro 三段式):
           requirements.md (EARS acceptance ← failure_boundary)
           design.md (typed module interfaces + pseudocode)
           tasks.md (bite-sized TDD)
           → spec.json

        5. adversarial-panel-audit (1 round, 3 reviewer roles):
           → verdict: pass / needs_revision / fail

        6. crossbio validate-chain artifacts/ (机器校验)
```

### 示例 3: Publication — 完整 T1 发表

```
你: 我想在空间多组学整合方向找几个好课题,要发顶刊。

Claude: (触发 using-crossbio-algo → Publication 模式)
        1. data-and-estimand-audit (GATE)
        2. brainstorm (5 轮: landscape → gap → cross-domain → ideation → critique)
           → N≥3 候选, 你选
        3. topic-viability-assessment (每个候选)
        4. adversarial-panel-audit (多轮)
        5. algorithm-design (formal method)
        6. spec-writing (kiro)
        7. benchmark + Publication Roadmap
```

---

## 如果没自动触发

### 方法 1: 显式点名 skill
直接说: "用 data-and-estimand-audit 审一下我的数据" 或 "跑 algorithm-design"。

### 方法 2: 检查安装
```
/plugin                           # 查看已装插件列表
ls ~/.claude/skills/              # 或检查手动 cp 的 skills
```

### 方法 3: CLAUDE.md 引导
你的项目 `CLAUDE.md` 里有 crossbio-algo bootstrap 模板(填了 domain/compute/tier/data),
Claude 每次会话读 CLAUDE.md → 知道走这套 loop。

---

## 与 validator 的联动

每个 skill 阶段产出 `artifact.json` (schema: `crossbio_validate/schemas/stage-schemas.json`):
```
data-audit (root) → design → spec → code
```

用 validator 校验:
```bash
crossbio validate-chain artifacts/         # 校验整条链
crossbio attest tests.py --bind src.py --out results.json   # source-bound attestation
```

校验内容(8 条 content rules):
1. estimand 连续 (design.estimand == data-audit.estimand)
2. 无孤儿 failure_boundary (每个 fb 有 acceptance trace)
3. notation 一致 (spec shapes ⊆ design notation)
4. pseudocode → code (每个 spec 模块有实现)
5. provenance 完整 (sha256 内容哈希)
6. test-link (声明 tested 的 AC 有真实 passing test)
7. documented_limitation ≠ passed (限制不能标 pass)
8. source-hash (impl source_sha256 从磁盘重算)

---

## Fallback 机制

当一个 idea 在 viability / audit / design 被拒:
1. **回退到 brainstorm 的剩余候选** —— 不丢弃, 让你选下一个
2. **提示**: "剩余候选: [X, Y]。或者要我重新 dev-mode 生成 N 个?"
3. 只有所有候选都被拒 → 重新 brainstorm 或换方向

---

## 一句话总结

> **你聊研究方向 → Claude 自动走 data-audit (GATE) → viability → design → spec → audit,每阶段产出 artifact.json,可用 crossbio validate-chain 机器校验。不需要 slash 命令,不需要手动触发。**
