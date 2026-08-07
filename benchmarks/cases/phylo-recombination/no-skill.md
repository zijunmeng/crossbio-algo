# no-skill output (vanilla agent, NO crossbio-algo skills loaded)

A reasonable vanilla-agent answer to the prompt — plausible, but it walks past the traps.

## Proposed method
Sliding-window phylogenetic incongruence: for each genome, slide a window, build a tree per
window, and flag genomes whose window-trees disagree (topology shift = recombination). Output:
a per-genome recombination flag + approximate breakpoint.

## Pipeline
1. Load alignment (BioPython).
2. Slide window (e.g. 500bp, step 100).
3. Build NJ tree per window.
4. Compare topologies; flag discordant genomes.
5. Validate on known recombinants from databases.

## Notes
- Compare to existing tools (RDP4, GARD).
- Python, CPU; use scikit-bio / BioPython.

## What it missed (the traps a reviewer would flag)
- **Estimand vague**: "detect recombination" — not the breakpoint + parent-assignment estimand.
- **Leakage**: "validate on known recombinants from databases" — those were often CALLED by the
  same family of methods → circular ground truth; and no clade-aware split.
- **No naive baseline**: only vs RDP4/GARD; no single-breakpoint/null baseline.
- **No failure boundary**: silent on low-signal short tracts, gappy alignment, saturation.
- **Confound ignored**: shared-ancestry similarity can mimic a mosaic.
- **Loose deps, no seed.**
