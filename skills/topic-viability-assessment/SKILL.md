---
name: topic-viability-assessment
description: Use when a researcher proposes a research direction, thesis/project topic, or a new method/algorithm to build, and wants to know whether it's worth pursuing — whether it is obsolete, overcrowded, or built on a flawed premise, what the risks are, and whether/how to pivot. 触发场景：用户提出研究方向 / 课题 / 想做的新算法或新方法，并询问"值不值得做""是否过时""有什么风险""要不要换方向"。Use BEFORE committing serious time to a new research line.
---

# Topic Viability Assessment

## Overview
Before sinking time into a research direction, run ONE honest viability verdict from the stance of a **skeptical senior reviewer**, grounded in **current evidence (not memory)**, scored under the user's actual target tier, and — critically — built on a **per-competitor deep-difference comparison, not a head-count of names**. Returns a score, an explicit proceed/stop call, and a concrete pivot if the topic is dead.

A naked evaluation tends to either flatter (cheerlead), judge from stale memory, silently apply the "paradigm-novelty" ruler to every goal, **or — the most common failure — see a list of same-keyword tools and declare the field "crowded" without ever checking what each one actually does**. This skill turns it into a reliable, structured, currency-checked, tier-aware, **competitor-differentiated** decision.

## Target Tier — viability depends on the goal (ASK FIRST)
"Worth doing?" has no single answer — it depends on the user's target. **Ask the target tier before scoring, and score under that tier's ruler.** Do NOT silently apply the T1 ruler to a T2 goal — that falsely kills perfectly publishable work.

| Tier | Goal | Ruler |
|---|---|---|
| **T1** | paradigm-novelty paper (Nature/Cell/Science) | structurally novel, no direct competitor |
| **T2** | tool paper (Genome Biology / Bioinformatics / NAR / Briefings) | defensibly better than existing on ≥1 axis + engineering quality + fair benchmark |
| **T3** | learning / practice | no bar |
| **T4** | solve a specific data / internal need | does it solve your problem? |

A crowded field is a real threat to T1, a soft constraint to T2 (find one improvable axis), and irrelevant to T3/T4. Always state which ruler you scored under.

## When to Use
- Someone proposes a research direction / thesis topic / new method or algorithm and asks "is it worth doing?"
- Before committing weeks to a new research line
- Comparing several candidate topics

**Not for:** already-decided work that just needs execution; pure implementation questions.

## Core Stance: Reviewer, Not Cheerleader
- Default to skepticism. **BE BRUTALLY HONEST.** If the topic is dead, say so plainly.
- **Never judge "is this field still alive" or "is this crowded" from memory.** Verify with search first.
- **Never judge crowdedness from competitor names or counts.** Verify what each competitor actually does first (see Competitor Deep-Comparison Table below).
- Question the **premise**, not just the method.

## Search Coverage — never single-source
Different topic types hide their competitors in different indexes; searching only one misses the real threats:
- **Biomedical / disease topics** → PubMed is primary (Nature Medicine, Cell, Nature Neuroscience...).
- **Bioinformatics / computational algorithms** → BOTH PubMed (formally published methods: Nature Methods, Genome Biology, Bioinformatics, NAR...) AND preprints (bioRxiv, arXiv q-bio/cs/lg). Flagship competitors (scVI, MAGIC, CellChat, SAVER...) are in PubMed — **skipping PubMed misses them**.
- **Pure ML/AI methods** → arXiv + venue proceedings (NeurIPS/ICML/ICLR) + Papers With Code.

Always search ≥2 sources appropriate to the topic type.

## The 4 Questions
1. Has this been rendered **OBSOLETE** by a paradigm shift?
2. Is there evidence the core **PREMISE IS FLAWED**?
3. What is the **CURRENT consensus**? Has the field moved on?
4. If obsolete/flawed: what is the **RECOMMENDED PIVOT**? (For T2: which axis of existing tools is improvable?)

## Competitor Deep-Comparison Table — MANDATORY before any score

**This is the heart of the skill. A score produced WITHOUT this table is invalid — redo.** The single most common failure mode is seeing a list of same-keyword tools (all called "spatial GRN", all called "scRNA imputation") and declaring the field "extremely crowded" from names alone. Names lie. Two tools sharing a keyword often occupy **different methodological slots** and are NOT direct competitors.

For every competitor surfaced by search, build one row of the table by checking the actual paper/preprint text (cite it), NOT the abstract's framing:

| Competitor | Input data required | Method (core mechanism) | Output | Key limitation | Delta vs the proposed direction | Direct competitor? |
|---|---|---|---|---|---|---|
| <name + cite> | what modality/scale it needs | how it actually works | what it returns | what it can't do | concrete difference | yes / no + why |

Rules for filling it:
- **"Input data required" is non-negotiable.** A tool that hard-requires spatial ATAC is not a competitor to a method designed for RNA-only data — they serve users with different datasets. This is the slot boundary.
- **"Method" must be the actual mechanism** (what math/signal it uses), not a keyword. "Uses GCN on the spot graph" vs "infers cis-regulation from motif accessibility" are different slots even if both are labeled "spatial GRN".
- **"Delta vs proposed" must be specific**, in input/method/output terms — never "similar approach, more mature". If you cannot state a concrete delta, you have not read the paper.
- **"Direct competitor?" is decided by slot overlap, not keyword overlap.** Mark `no` unless the competitor overlaps the proposed direction on the SAME input slot AND the SAME method slot AND targets the SAME output.

### Core lesson: different methodological slots are NOT direct competitors
A field's keyword (e.g. "spatial GRN inference") often covers several **slots** defined by what input the user actually has:
- "I have spatial ATAC + RNA → infer cis GRN" is one slot.
- "I have spatial RNA only → impute/deduce cis regulation without ATAC" is a different slot.
- "I have spatial RNA → infer trans co-expression networks" is yet another.

A tool built for slot 1 (hard-depends on ATAC) is **not** a direct competitor to a proposed method for slot 2 (no ATAC available). Calling them "the same crowded space" is the exact error this skill exists to prevent. Always identify the slot each tool serves before counting it as competition.

## Scoring — driven by the delta analysis, NOT the competitor count

- **Score from the "Direct competitor?" column of the table**, not from how many rows exist. Ten tools that all occupy a different slot from the proposal = effectively zero direct competitors.
- **"Competitors are numerous" is NOT a scoring input on its own.** To push a score low, you must show that each named direct competitor overlaps the proposal on input + method + output, and that no improvable axis remains (T2) or that structural novelty is gone (T1).
- Do not conflate **crowded** with **obsolete** — and remember "crowded" is tier-dependent (kills T1, nudges T2 only if no improvable axis survives the delta analysis).
- If, after building the table, the "Direct competitor?" column is mostly `no`, the crowdedness argument collapses — say so explicitly and score accordingly, even if the keyword-space looked full.

## Required Output — all fields, none optional
| Field | Meaning |
|---|---|
| `target_tier` | T1 / T2 / T3 / T4 — the ruler used |
| `competitor_comparison_table` | the per-competitor table above (MANDATORY — output is invalid without it) |
| `direct_competitors` | the subset marked "yes" in the table, each with its improvable axis (T2) / novelty-kill status (T1) |
| `is_obsolete_or_flawed` | true if dead / dying / flawed premise |
| `paradigm_shift_status` | one sentence: where the field moved |
| `critical_evidence` | concrete papers/arguments — real, cited, verified against source text |
| `recommended_pivot` | specific alternative / improvable axis. NOT "try something else" |
| `viability_score` | 0.0–1.0 **scored under target_tier's ruler, from the delta analysis** — must be justified by the table, not by competitor count |
| `warning_flags` | specific concerns |
| `should_proceed` | true ONLY if genuinely viable under that tier |

## Score → Decision
- **≥ 0.5** — viable under the tier; proceed; address `warning_flags`
- **0.3–0.5** — high risk under the tier: resolve flags or pivot
- **< 0.3** — seriously doubtful under the tier
- **< 0.15** — effectively dead, hard stop unless a concrete pivot is adopted

These thresholds are strictest for T1. **For T2, a crowded keyword-space alone does NOT push you low** — only the absence of ANY improvable axis across the genuine direct competitors does.

## Mandatory Discipline (close the loopholes)
- **Ask target tier first.** Never score without knowing it.
- **Build the Competitor Deep-Comparison Table before scoring.** A score with no table is invalid. Every row must be filled from verified source text, not from the competitor's name or abstract framing.
- **Decide "Direct competitor?" by slot overlap (input + method + output), not by shared keyword.** Different slots ⇒ not a direct competitor, regardless of how similar the names sound.
- If `is_obsolete_or_flawed = true` → `recommended_pivot` MUST be non-empty and specific.
- A `viability_score` with no `critical_evidence` is invalid — every score needs a cited basis, and the crowdedness basis must come from the table's "Direct competitor?" column.
- For any "is this current / obsolete" claim → **search first**, do not trust memory.
- Even when score ≥ 0.5, state the single biggest thing that could make this fail.

## Red Flags — your assessment is probably invalid if:
- **You judged "crowded" from competitor names or counts without generating the per-competitor deep-comparison table → invalid; rebuild the table and re-score.**
- **You treated tools in different methodological slots (different input requirements / different core mechanisms) as direct competitors just because they share a keyword → invalid; re-classify by slot.**
- You scored without confirming the target tier → ask it first.
- "Field is healthy" based only on memory → verify currency.
- Encouragement with no risks/flags → cheerleading; redo as skeptic.
- A score with no evidence / no table → unsupported; redo.
- An "obsolete" verdict with no pivot → incomplete; supply one.
- You applied the T1 ruler to a T2 goal → re-score under the correct ruler.
- The "Delta vs proposed" column reads "similar, more mature" with no concrete input/method/output difference → you haven't read the paper; redo that row.

## Handoff to Algorithm Design
You are a **counsel, not a gatekeeper** — you do NOT veto. Once the target tier is set and viability is scored under it (with the competitor table attached):
1. If viable under the tier → hand off directly.
2. If low under the tier but the user wants to proceed → that is the user's call; just make it informed (see `~/.claude/skills/_shared/research-design-handoff.md`). Options (informed door): (a) accept the tier's risk, (b) lock an improvable axis that survived the delta analysis (T2), or (c) supply info that changes the score (e.g. a reclassified slot).
3. Emit the handoff block (target_tier, verdict, score, the competitor_comparison_table, the genuine direct_competitors + their improvable axes, user's choice) so algorithm-design inherits the real competitive landscape — not a name list.

The user decides; your job is to ensure they decide **informed under the right ruler and against the real (slot-filtered) competitor set**, then carry the truth forward.

## Example — spaGRN-style spatial GRN from RNA-only data (the lesson case)
```
target_tier: T2 (tool paper)
competitor_comparison_table:
  | Competitor | Input | Method | Output | Key limitation | Delta vs proposed | Direct? |
  | SpaGRN (2023) | spatial RNA + ATAC-inspired motif | deep learning integrating cis motif | cell-type GRN | requires ATAC / motif info | proposed needs NO ATAC | no (different input slot) |
  | STARNet (2022) | spatial ATAC + RNA | GCN on spot graph | cis GRN | hard-depends on spatial ATAC | proposed targets RNA-only users | no (different input slot) |
  | SCRIpro (2023) | scRNA + motif scan | regression on motif activity | cis regulation | single-cell, ignores spatial | proposed adds spatial structure | no (different spatial/non-spatial slot) |
direct_competitors: [] — all three share the "spatial GRN" keyword but occupy different input/method slots; none serves "RNA-only spatial → cis GRN".
is_obsolete_or_flawed: false
paradigm_shift_status: Field is segmenting by input modality (ATAC-available vs RNA-only), not collapsing.
critical_evidence: verified against source text of each paper — STARNet's method section hard-requires ATAC peaks; SpaGRN's pipeline ingests motif/accessibility; SCRIpro is non-spatial.
recommended_pivot: none needed — lock the improvable axis: "the only method for spatial cis GRN when no ATAC is available", with a fair benchmark against the RNA-only baseline.
viability_score: 0.62 under T2   — NOTE: a name-only read of "SpaGRN/STARNet/SCRIpro all do spatial GRN" would wrongly score ~0.3; the slot-filtered table shows no direct competitor, so the crowdedness penalty does not apply.
warning_flags: ["must benchmark against the strongest RNA-only baseline, not against ATAC-dependent tools", "reviewers may initially mis-read as crowded — lead with the slot argument"]
should_proceed: true
biggest_failure_risk: a future ATAC-free method lands before submission and occupies this exact slot.
```

## References
- `~/.claude/skills/_shared/research-design-handoff.md` — the viability→design contract; carry the competitor_comparison_table forward so design's `novelty_basis` is checked against genuine direct competitors.
