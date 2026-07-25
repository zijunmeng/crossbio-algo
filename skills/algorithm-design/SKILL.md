---
name: algorithm-design
description: Use when someone wants to DESIGN a new algorithm, method, or model from scratch — to go beyond recombining existing methods and find a genuinely novel, mathematically-grounded approach. 触发场景：用户要设计新算法 / 新方法 / 新模型，或卡在"现有方法都不行、想找新思路"，或想把一个问题做得更有数学深度和创新性。Use BEFORE writing code or settling on a known method.
---

# Algorithm Design

## Overview
Designing a new algorithm means **inventing**, not recombining. Most "design a new algorithm" requests get answered by listing existing methods (VAE, KNN, scVI...) and bolting modules on — incremental engineering, not a new algorithm. This skill forces a 4-step inventive process: **abstract to the mathematical essence → import solutions from OTHER domains → state where it must fail → probe that boundary on synthetic data.**

Two disciplines make it work:
- **Externalized reasoning (推理外显)**: the agent decides the professional calls itself, but explains *why* at every step. The user corrects or overrides whenever they want — they are never *required* to make a professional either/or they can't judge.
- **Honor the handoff**: if this follows a **crossbio-algo:topic-viability-assessment** run, read `_shared/research-design-handoff.md` and design **under the competitor constraint** it carries.

## When to Use
- Someone wants to design a new algorithm / method / model (not just run or compare existing ones)
- They're stuck: "existing methods don't work for my case, I need a new idea"
- They want more mathematical depth or genuine novelty

**Not for:** running a standard pipeline; applying a known method; debugging; hyperparameter tuning.

## Core Stance: Inventor, Not Librarian
- Invent a structurally new method, not catalog or recombine known ones.
- Start from the **mathematical structure**, not from existing methods in the field.
- Inspiration must come from **outside the problem's home domain**.

## Two Classes of Decision

### A. User decisions (collect ONCE, up front — these the user can actually judge)
Ask these in a single opening pass before designing:
- **Target tier** — T1 (top journal, structurally novel) / T2 (tool, defensibly better than competitors + benchmark) / T3 (practice / learning) / T4 (solve a specific-data need).
- **Resource constraints** — GPU available? What data (modality, scale, access)? What tool stack / frameworks are they fluent in?
- **Biological preference** — what mechanism / regulation / phenomenon do they actually care about (so the abstraction doesn't drift away from their science)?

### B. Professional calls (the agent decides, states recommendation + reason, user may override but is never forced to pick)
- Mathematical abstraction choice.
- Cross-domain method selection.
- Failure-boundary derivation.
- Simulation parameters and regime.
- Concrete technical / library choices.

These are **not** turned into either/or questions for the user. The agent commits to a recommendation with its rationale; the user interjects only if they disagree.

## The 4-Step Inventive Process — autonomous run, externalized reasoning, pause only at global forks

Run all four steps. At each step: **state the choice + the reason out loud** (推理外显), then continue. Do NOT stop to ask a binary question unless hitting a **global fork** (see below). Collect the up-front user decisions (Section A) first, then run.

### 1. Mathematical Abstraction (first)
Commit: "Abstracting this as fundamentally a **[X]** problem, because [reason tied to the data structure / goal]." Give the runner-up abstraction you rejected and why. Typical X: masked/sparse matrix completion • signal recovery on a graph • manifold regression with missing data • zero-inflated latent inference • distribution alignment (OT) • directed-graph / causal discovery • spectral clustering • ordered-structure (trajectory) recovery.
**Global fork (stop and ask) only if**: two abstractions lead to *entirely different algorithm families and validation paths* and you cannot pick on technical merit alone — then present both directions with the trade-off and let the user steer.

### 2. Cross-Domain Inspiration (≥2 domains OUTSIDE the home field)
Open `cross-domain-inspiration.md` (next to this file) — the essence→domains map (fluid dynamics, info theory, game theory, satellite remote sensing, quantitative finance, operations research, cosmology…) plus the method pool. State: "Mined [domains] for essence X; sparks A / B / C; **selecting [method] because [reason]**." Name the discarded sparks and why. Do not ask the user to choose between inspirations — recommend.

### 3. Failure Boundary (derive, don't assume)
State: "This algorithm degrades / fails when [mathematical condition], because [mechanism]." Derive it from the abstraction, not from intuition. Fold in any platform/data failure modes surfaced in the up-front user pass. Do not stop to ask.

### 4. Simulation-First (before real data)
Commit: "Building synthetic data with controllable [params] to probe that boundary; sweeping [regime] because that's where the failure condition bites." Specify the parameter ranges you chose and why they stress the boundary. Do not stop to ask.

## Required Output — all 6 fields, none optional
| Field | Meaning |
|---|---|
| `mathematical_abstraction` | "Fundamentally a [X] problem" + the rejected alternative and why |
| `cross_domain_inspiration` | ≥2 domains OUTSIDE the home field + method from each + which was selected and why |
| `proposed_algorithm` | derived from the abstraction, NOT a re-listing of existing field methods |
| `failure_boundary` | condition under which it degrades / fails, with mechanism |
| `simulation_plan` | synthetic data with controllable params to probe the boundary, with chosen regime + reason |
| `novelty_basis` | why worth publishing **under the user's target tier** — **if a handoff exists, MUST state the delta vs each named top_competitor**; T1 = structurally novel, T2 = defensibly better on ≥1 axis + fair benchmark (NOT necessarily novel), T3 = N/A, T4 = solves the stated need |

## Mandatory Discipline (close the loopholes)
- All inspiration from the SAME field → invalid; cross domains.
- Starts from an existing method ("use a VAE…") without abstraction → redo from the structure.
- No `failure_boundary` → incomplete; derive one.
- No `simulation_plan` → incomplete; design the probe.
- Novelty = "added a module / added a loss" → incremental; re-derive.
- **Skipping the up-front user-decision pass, OR running the design without externalizing the reasoning (no recommendation + reason at each step) → invalid**; collect user decisions first, then run with 推理外显, pausing only at true global forks.
- **Asking the user to make a professional either/or (math abstraction / cross-domain method / failure condition / sim params) that they cannot judge → invalid**; that is the agent's call — recommend with reasons, let the user override voluntarily.
- **Ignoring a viability handoff** (designing as if competitors don't exist) → invalid; honor the contract.

## Red Flags
- Every cited method is from the problem's own field → field-locked; cross out.
- Skipped abstraction, went straight to "use a VAE / transformer / GNN" → librarian mode; abstract first.
- No stated failure condition → you don't understand your own algorithm.
- "Tested on a benchmark" is the only validation → benchmarking, not boundary-finding.
- Professional calls made with no recommendation / no stated reason → black-boxed; re-run with 推理外显 (state choice + why at each step).
- User was forced into a binary on a technical judgment outside their scope → mis-scoped collaboration; the agent should have recommended.

## References
- `cross-domain-inspiration.md` (in this folder) — the 28-domain essence→domains map + method pool.
- `_shared/research-design-handoff.md` — the viability→design contract (read if chained from **crossbio-algo:topic-viability-assessment**).

## Example — scRNA-seq imputation
```
mathematical_abstraction: Fundamentally a masked signal-recovery problem on a cell-similarity graph.
  (rejected: zero-inflated latent inference — would force a generative VAE family and bury the recovery structure in a latent prior; the graph-signal view keeps the failure mode transparent.)
cross_domain_inspiration:
  - Graph signal processing (graph wavelet / Fourier low-pass) — denoise by suppressing high graph-frequency components.
  - Compressed sensing — sparse recovery from few observations given a sparsifying transform.
  selected: graph signal processing — the cell-similarity graph is the native domain; compressed sensing's sparsity assumption is weaker for this data.
proposed_algorithm: Graph-wavelet thresholded imputation — decompose the signal on the cell graph into wavelet bands; suppress noise bands; recover only low-frequency components at masked entries; model each zero's dropout probability to decide fill vs keep.
failure_boundary: Degrades when dropout probability is coupled to true expression (masked assumption breaks) and when the cell graph mis-estimates similarity in ultra-sparse regimes.
simulation_plan: Known smooth graph signal + injected zeros with controllable sparsity and dropout-expression coupling; sweep both; plot recovery error vs coupling to locate the break. Regime chosen: coupling ∈ [0,1] to find the exact break point.
novelty_basis: Recovers via graph-frequency selection rather than averaging/diffusion or a VAE — a structurally different smoothing operator.
```
