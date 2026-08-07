# Standard-mode output (crossbio-algo: data-audit GATE → algorithm-design → spec)

Same prompt, run through the skills. Compact (full artifact chain in artifacts/).

## data-and-estimand-audit (GATE)
- **biological_unit**: a recombination event (a mosaic genome w.r.t. ≥2 parents) — NOT a single
  genome nor a single site.
- **estimand**: for each genome, the set of breakpoint coordinates + parent-assignment per
  segment (argmax over mosaics P(mosaic | alignment)), under a substitution model — not "detect".
- **leakage_graph**: evaluation split unit = **clade / parent-pair**, not genome — genomes in the
  same clade share ancestry → cell-level... genome-level split leaks phylogenetic signal.
- **ground_truth_quality**: recombination truth must come from a **simulation with a known DGP**
  (coalescent + injected breakpoints), NOT from "known recombinants" called by a correlated
  method (circular) — flagged fatal unless reframed.
- **usable_sample_size**: # independent parent-pairs / clades, not # genomes.

## algorithm-design (selected fields)
- **objective_or_likelihood**: maximize P(breakpoints, parents | alignment) = Σwindows
  [log-likelihood under parent substitution models] − λ·(#breakpoints) (a penalized mosaic
  likelihood; the penalty controls over-segmentation).
- **identifiability**: a breakpoint is identifiable only if the parent-pair substitution-rate
  contrast × tract length exceeds noise; NOT identifiable under saturation or near-identical parents.
- **failure_boundaries**:
  - fb1 tract length < L_min → signal below noise (mechanism: per-window tree unresolved).
  - fb2 alignment gapiness > g* → missing data mimics topology shift.
  - fb3 divergence saturation (too many substitutions) → homoplasy → false mosaic.
  - fb4 near-identical parents → breakpoint not identifiable (collinearity).
- **benchmark_protocol**: vs **RDP4 / GARD / 3SEQ** AND a **naive single-breakpoint + a null
  (no-recombination) baseline**, on a coalescent simulation with injected breakpoints (known
  truth), same alignment/mask/compute; metrics = breakpoint-localization error + parent-assignment
  F1 + false-positive rate in the null regime.
- **novelty_or_utility_basis**: T2 — utility locus = a CPU-only mosaic-likelihood with explicit
  identifiability boundaries under saturation/gappiness; competitors classified (RDP4/GARD =
  functional substitutes, single-breakpoint = naive baseline).

## spec (kiro) — omitted here for brevity (full chain in artifacts/)
pinned deps, seed=0, BioPython/scikit-bio, deterministic.
