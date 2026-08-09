# Project CLAUDE.md — crossbio-algo bootstrap

> Copy this file into your project's `CLAUDE.md` and fill in the context below.
> Claude reads CLAUDE.md every session — this is the simplest bootstrap for the crossbio-algo skill loop (no hook needed).

## When the user proposes research / an algorithm / a tool / a method
Follow the **crossbio-algo** loop. Read the **crossbio-algo:using-crossbio-algo** skill for the full loop + trigger priority. In short:

1. **brainstorm** — if multiple ideas are wanted (dev-mode: utility-first, novelty explicit — abstract to math essence + cross-domain sparks)
2. **topic-viability-assessment** — score ONE idea: build the competitor DEEP-COMPARISON table first (never judge crowdedness from names); tier-aware (ask T1–T4 first)
3. **adversarial-panel-audit** — adversarial same-model subagent panel BEFORE trusting any artifact
4. **algorithm-design** — 4-step inventive design; autonomous + externalized reasoning; pause only at global forks
5. **spec-writing** — kiro requirements / design / tasks; acceptance traces to failure_boundary
6. code

**Fallback**: if an idea is rejected at viability/audit/design, fall back to the remaining brainstorm candidates — never discard them.

## My research context (fill in)
- **domain**: <e.g. spatial transcriptomics / single-cell / proteomics>
- **compute**: <e.g. no GPU, Python + scanpy/squidpy; or GPU available>
- **target tier**: <T1 paradigm-novelty / T2 tool paper / T3 learning / T4 specific-data>
- **effort mode**: <Quick / Standard / Publication — or leave blank to auto-infer from tier: T3/T4→Quick, T2→Standard, T1→Publication>
- **data I have**: <e.g. paired scMultiome + Stereo-seq>

## Honest-colleague principle
The agent is a counsel, not a gatekeeper — it never vetoes, but it forces informed decisions and carries competitor truth forward. Audit is two-way insurance: prevents both under-scoring (judging crowded from names) and over-claiming (cross-domain "novelty" that's already ported).
