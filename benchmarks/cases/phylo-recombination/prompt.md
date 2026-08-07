# Case: phylo-recombination (viral genomics)

## Prompt (the research direction given to the agent)
> I have an alignment of ~5,000 viral genomes (a fast-evolving virus, e.g. SARS-CoV-2 / HIV).
> I want to **detect recombination** (which genomes are mosaic / where the breakpoint is).
> Build me an algorithm for it. I work in Python (BioPython), CPU only.

## Domain
phylogenetics / virology — **deliberately non-scanpy** (tests that the skills generalize beyond
single-cell; a "virus algorithm developer" case).

## Known traps (the grader checks whether each was caught)
- **T1 estimand**: "detect recombination" is vague — the estimand is the breakpoint locations +
  parent assignment per genome, not a yes/no.
- **T2 leakage**: a train/test split that shares a clade (or the same parent) leaks phylogenetic
  signal; the split unit is a CLADE / parent-pair, not a single genome.
- **T3 circular truth**: recombination "truth" from the SAME detection method (or a correlated
  one) = circular ground truth.
- **T4 confound**: shared ancestry vs true recombination — high sequence similarity can mimic a
  mosaic; saturation at high divergence hides the signal.
- **T5 benchmark fairness**: must compare to RDP4 / GARD / 3SEQ AND a naive single-breakpoint
  baseline, on a simulation with known truth.
- **T6 failure boundary**: low-signal short tracts; gappy alignment; divergent-saturation regime.
