---
name: brainstorm
description: >-
  Use when a researcher has a fuzzy interest and wants MULTIPLE candidate
  ideas / project topics before any single one is evaluated. Two modes —
  dev (invent a new algorithm / method / tool: each idea is a seed of
  algorithm invention, carrying the mathematical essence + cross-domain
  spark) or research (explore a biomedical direction: hypothesis / gap /
  novelty). Triggered when the user wants to find topics, has not yet
  committed to one, and is before topic-viability-assessment. Runs BEFORE
  topic-viability-assessment.
---

# Brainstorm

## Overview
From a fuzzy interest, generate **N (default ≥3) deep, novel candidate ideas** — the creative engine that feeds `topic-viability-assessment`. A naive brainstorm either dumps the first obvious idea, recycles stale memory as "current trends," or only produces confirming directions (the field's consensus, restated). This skill forces a 5-round progressive process (landscape → gap → cross-domain → ideation → critique) plus a self-critique loop, so output is **multi-candidate, gap-mined, currency-checked, and ready to feed viability or algorithm-design.**

The skill runs in **two modes**, picked once and held for the whole run:

- **dev mode** — the user wants to *invent a new algorithm / method / tool*. Each idea is a **seed of algorithm invention**: it must carry `algorithm_abstraction` (mathematical essence + computational pattern + recommended domains) and a concrete `cross_domain_inspiration`. This is what lets the agent propose *unexpected* new algorithms (invent from the mathematical structure across domains), not merely recombine field methods. Seeds hand off to the **crossbio-algo:algorithm-design** skill for full design.
- **research mode** — the user wants to *explore a biomedical / scientific direction*. Each idea carries hypothesis / gap / novelty / feasibility / data_needed in the classic research-direction style.

Two disciplines hold in both modes:
- **Run autonomously through all 5 rounds.** Professional judgment (what gaps exist, which domains cross-pollinate, what algorithm family a structure implies) is NOT outsourced to the user. Only genuine user-decision points pause for input.
- **Verify, never recall.** Any claim about current state / trends / methods MUST be checked against PubMed / bioRxiv / arXiv — memory is treated as stale until confirmed.

## When to Use
- User has a fuzzy interest ("胎脑 microglia 异质性", "spatial niches", "scRNA-seq imputation 想做得更有数学深度") and wants candidate ideas.
- User wants multiple thesis / project topics to choose among.
- Before any single idea is evaluated.
- The output feeds **crossbio-algo:topic-viability-assessment** (research) or **crossbio-algo:algorithm-design** (dev).

**Not for:** evaluating ONE idea (use topic-viability-assessment); doing the full algorithm design — math derivation, failure boundary, simulation plan (use algorithm-design). Brainstorm hands off; it does not design.

## Pick the Mode
Decide once, at the start. Ask the user, or infer from the input:
- **dev** if the interest is an algorithm / method / tool / computational technique ("我想做一个新的 X 算法", "spatial smoothing 有没有新做法", "imputation 想找新思路").
- **research** if the interest is a biomedical / scientific direction ("microglia 异质性", "哪些 niche 还没研究").

State the chosen mode out loud and hold it for all 5 rounds.

## Autonomy Boundary — where to involve the user
The 5 rounds run autonomously. Pause ONLY at:
- **R1 exit**: confirm the interest's specific angle (e.g. "microglia — neurodevelopment vs neurodegeneration?"; in dev mode, also confirm the rough problem class / constraints — **ASK the user for their compute constraints: GPU available? data (modality / scale / access)? tool stack / frameworks they're fluent in?** Do NOT assume any specific environment).
- **R4 exit**: present N candidates, let the user pick one, several, or all to carry forward.

Do NOT ask the user to do gap-mining, cross-domain mapping, abstraction choice, or critique — that is the agent's job.

## The 5 Rounds

### R1 — Landscape (MUST verify)
Map the field: dominant methods, key entities / regions / modalities, and **last-2-year trends**. Every "current consensus / trend / method" claim MUST be checked against PubMed + bioRxiv (or arXiv for computational work). No claim from unverified memory.
- In dev mode, the landscape includes the **method landscape**: what algorithms / method families currently dominate this problem, and what each assumes.
Exit question: confirm the specific angle the user cares about (+ dev-mode constraints).

### R2 — Gap Mining (FORBID all-confirming)
Actively hunt: unexplored entities / regions / windows, method limitations, contradictory findings, missing tools, under-sampled modalities, populations where findings don't replicate. In dev mode, gaps are often *method assumptions that break* (e.g. "every imputer assumes dropout ⊥ expression").
**Hard rule:** at least one gap must be NON-confirming (contradicts or extends the consensus). If every gap merely restates the field's open todos, redo.

### R3 — Cross-Domain
- **research mode** — open `_shared/../algorithm-design/cross-domain-inspiration.md` (the essence→domains table). For each promising gap, mine ≥2 domains OUTSIDE the home field and name the concrete technique borrowed.
- **dev mode** — first state each gap's **`algorithm_abstraction`** (what mathematical essence does this gap *fundamentally* reduce to?). Then open the cross-domain-inspiration table and mine ≥2 domains for that essence, naming the concrete technique borrowed. The abstraction is what unlocks non-obvious cross-domain sparks.

- **AVOID THE FAMOUS-ALGORITHM TRAP (dev mode, mandatory)**: do NOT just borrow a famous named algorithm (EnKF / MVS / graph wavelet / Kalman / OT) — those are usually ALREADY applied in omics (Kalman→GRN, MVS→PASTE/MOS, SGWT→BioGSP). Before adopting a cross-domain method, **search whether it has already been applied in omics**; if yes, drop it or find an unused variant. Prefer mining the *mathematical structure* for solutions not yet ported to omics, over importing a famous algorithm's name.

In both modes: all inspiration from inside the home field = invalid.

### R4 — Ideation (generate N, default ≥3)
Produce N structured proposals. The schema depends on the mode.

#### dev mode — each idea is a SEED OF ALGORITHM INVENTION
Every field is mandatory. The point is to hand `algorithm-design` a rich seed, NOT a finished design — no deep math derivation, no failure-boundary derivation, no simulation plan (that is algorithm-design's job).

| Field | Meaning |
|---|---|
| `title` | concise, specific |
| `algorithm_abstraction` | object: **mathematical_essence** (the core problem class, e.g. "高维非线性动力系统的稳态推断", "masked signal recovery on a graph"); **computational_pattern** (the solving shape, e.g. "ODE 拟合 + 稳态求解", "graph wavelet thresholding"); **recommended_domains** (≥2 fields OUTSIDE the home field to mine, from the cross-domain table) |
| `cross_domain_inspiration` | the concrete cross-domain technique (domain + method), e.g. "ensemble Kalman filter (meteorology data assimilation) → RNA-velocity vector-field smoothing". MUST reference the 28-domain table in the algorithm-design skill's `cross-domain-inspiration.md` attachment |
| `hypothesis` | the testable claim the algorithm would enable / embody |
| `gap_addressed` | the R2 gap (cite it) |
| `novelty_score` | why this is an *invention*, not incremental — the structural delta vs the nearest existing method |
| `feasibility` | respects the **user's stated compute constraints** (GPU? tool stack? data?) — ask for them at R1 if not yet known; flag any idea needing heavy compute or resources the user doesn't have |
| `existing_tools_gap` | the named competitor(s) and the axis this seed would beat them on |

Exit question: present N, let the user pick one / several / all.

#### research mode — classic research-direction idea
| Field | Meaning |
|---|---|
| `title` | concise, specific |
| `hypothesis` | testable, falsifiable |
| `gap_addressed` | the R2 gap (cite it) |
| `cross_domain_inspiration` | domain + technique from R3 |
| `novelty` | why not incremental — delta vs the nearest existing work |
| `feasibility` | data availability, compute — **under the user's stated constraints** (ask at R1 if unknown); do not assume a specific environment |
| `data_needed` | specific datasets / atlases |

Exit question: present N, let the user pick one / several / all.

### R5 — Critique
For each idea: `fatal_flaw` (what could kill it) · `novelty_verification` (re-search — is it actually novel, or already done?) · `improvement` (concrete edit to incorporate). In dev mode, the fatal_flaw probes whether the abstraction is sound, not whether the full design is (that's algorithm-design's job).
- **dev mode — novelty_verification MUST check cross-domain collision**: search whether the proposed `cross_domain_inspiration` method has **already been applied in omics** (e.g. Kalman→GRN; graph wavelet→BioGSP). If it has, the idea's novelty collapses to the *combination* only — flag it, and either find an unused variant or drop the idea. Do NOT hand an already-ported-method idea to viability (it will be rejected there).

## Self-Critique Loop (max 2 rounds)
After R5, fold each critique back into its idea (re-edit the fields). Re-critique the revised version. Stop when stable or after 2 rounds — do not loop forever.

## Division of Labor — brainstorm vs algorithm-design (dev mode)
Brainstorm gives **the seed of an invention**: the abstraction, the cross-domain spark, the hypothesis, the gap, the novelty claim. It does NOT do:
- full math derivation / convergence / identifiability argument,
- failure-boundary derivation (the condition + mechanism under which the algorithm degrades),
- simulation plan (synthetic data + sweep regime to probe the boundary),
- the final `proposed_algorithm` with its operator-level specification.

Those are the job of the **crossbio-algo:algorithm-design** skill, which receives the seed and invents *under the competitor constraint*. A dev-mode idea is done when a colleague could read it and say "I see the invention you're proposing and where it's new" — not when they could implement it.

## Checklist — mandatory discipline
- [ ] **Mode chosen** (dev or research) and stated; held for all 5 rounds.
- [ ] Generates **≥3** structured candidates in the mode's schema. Giving only 1 idea = FAIL.
- [ ] ≥1 gap is **non-confirming** (contradicts/extends consensus). All-confirming = FAIL.
- [ ] Every R1 "current state / trend / method" claim is **verified** (PubMed/bioRxiv/arXiv), not recalled. Memory-presented-as-current = FAIL.
- [ ] **dev mode only**: every idea carries `algorithm_abstraction` (all three sub-fields) + `cross_domain_inspiration` referencing the 28-domain table. Missing either = FAIL.
- [ ] Each idea cites **≥2 cross-domain inspirations** from outside the home field.
- [ ] Every idea carries ALL its mode's R4 fields — none optional.
- [ ] Feasibility respects **the user's stated compute constraints** (GPU? stack? data?) — ask for them at R1 if unknown; do NOT assume any specific environment. Flag any idea needing heavy compute or resources the user doesn't have.
- [ ] Each idea survived `novelty_verification` in R5.
- [ ] **dev mode only**: the idea is a SEED, not a full design (no deep math / failure boundary / simulation plan). Over-designing = scope-creep; trim to the seed.

## Red Flags — output is probably invalid if:
- Mode never stated, or schema drifts between modes mid-run → re-declare and re-run R4.
- Only 1 idea returned → redo, generate N.
- Gaps are all "more data / bigger model" (confirming) → mine contradictions.
- Trends cited from memory → verify.
- Cross-domain inspirations all from the home field → re-cross.
- **dev mode**: idea names a method ("use a VAE") but has no `algorithm_abstraction` → abstract first, then ideate.
- **dev mode**: idea includes a full failure-boundary derivation or simulation plan → that's algorithm-design; trim the seed.
- **dev mode**: `cross_domain_inspiration` is a famous algorithm name (EnKF/MVS/graph wavelet/Kalman/OT) and you didn't check whether it's already applied in omics → check first (R5 collision check); if already ported, drop or find an unused variant.
- Idea has no failure-aware `fatal_flaw` → incomplete critique.

## Handoff
- **research mode** → REQUIRED SUB-SKILL: **crossbio-algo:topic-viability-assessment**: each surviving idea is directly feedable — carry its R4 fields + R5 critique. User picks one or all; viability scores each under its target tier.
- **dev mode** → **crossbio-algo:topic-viability-assessment** (score the seed under its tier) AND/OR directly to **crossbio-algo:algorithm-design** (deepen the seed into a full 6-field design). Carry `algorithm_abstraction` + `cross_domain_inspiration` + `novelty_score` + `existing_tools_gap` forward.

See `_shared/research-design-handoff.md` for the full-loop contract.

## References
- `cross-domain-inspiration.md` (attachment of **crossbio-algo:algorithm-design**) — the 28-domain essence→domains table + method pool (used in R3).
- **crossbio-algo:algorithm-design** — receives a dev-mode seed and does the full inventive design.
- **crossbio-algo:topic-viability-assessment** — scores a candidate under the user's target tier.
- `_shared/research-design-handoff.md` — the brainstorm→viability→design→spec contract.

## Example — dev mode: "scRNA-seq imputation, want a more mathematically deep approach"
```
mode: dev
R1 Landscape (verified): imputation dominated by model-based methods (scVI/ZINB), graph-smoothing (MAGIC), and matrix-factorization (SAVER); last-2yr trend = modeling counts directly rather than impute-then-analyze; premise that "zeros ≠ dropouts" under active debate [PubMed/bioRxiv cited].
  → exit: user wants a structurally novel imputer, no GPU, scanpy stack.
R2 Gaps: (a) every imputer assumes dropout ⊥ true expression — breaks under biology-coupled dropout; (b) no method uses the *graph-frequency* structure of expression; (c) imputation error never uncertainty-calibrated.
R3 Cross-Domain (via algorithm_abstraction + cross-domain-inspiration.md):
  gap (b) → abstraction {essence: masked signal recovery on a graph; pattern: graph-spectral thresholding; domains: graph signal processing, compressed sensing}
            → spark: graph signal processing (graph wavelet / Fourier low-pass); compressed sensing (sparse recovery under a sparsifying transform).
R4 Ideation (3 of N), each a SEED:
  Idea-1 "Graph-wavelet thresholded imputation"
    algorithm_abstraction: {essence: masked signal recovery on a cell-similarity graph; pattern: spectral decomposition + band-suppress + masked recovery; domains: graph signal processing, compressed sensing}
    cross_domain_inspiration: graph signal processing (graph wavelet) — denoise by suppressing high graph-frequency components [ref cross-domain-inspiration.md Table B].
    hypothesis: expression is band-limited on the cell graph; recovering low-frequency components at masked entries beats averaging/diffusion.
    gap_addressed: (b).
    novelty_score: structurally different smoothing operator (frequency selection) vs averaging/diffusion/VAE — not a module bolted on.
    feasibility: scanpy + graph Fourier, no GPU.
    existing_tools_gap: MAGIC (diffusion) and scVI (generative) both smear high-frequency signal; this preserves it selectively.
  Idea-2 "Dropout-expression-coupling-aware imputer" — abstraction {essence: missing-not-at-random inference; ...}; ...
  Idea-3 "Uncertainty-calibrated imputation as Bayesian graph regression" — abstraction {essence: Bayesian regression on a manifold with missing data; ...}; ...
R5 Critique: Idea-1 fatal_flaw = graph-similarity mis-estimation in ultra-sparse regimes; novelty_verification = re-search confirms no direct competitor doing graph-frequency selection; improvement = pair with a graph-construction sanity check.
→ 3 SEEDS handed to algorithm-design (each carries abstraction + spark + novelty; NOT yet a failure boundary or simulation plan — that is algorithm-design's job).
```
