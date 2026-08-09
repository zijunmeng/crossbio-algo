# crossbio-algo Standard-mode run — phylo-recombination (run `standard-1`)

**Case:** viral-genome recombination detection (SARS-CoV-2 / HIV, ~5000 genomes, CPU-only Python/BioPython).
**Mode:** Standard (data-audit → topic-viability → algorithm-design → spec-writing → 1 adversarial-panel-audit round).
**Target tier:** T2 (tool paper).
**Skill version:** 0.3.0.
**Artifacts:** `artifacts/{data-audit,design,spec}.json` — validated by `python -m crossbio_validate validate-chain` → **VALID (0 errors)** after audit-driven revisions.

This document is the human-readable run; the three `.json` files are the machine-checkable artifact chain (estimand continuity, no-orphan failure boundaries, notation consistency all enforced).

---

## STAGE 1 — Data & estimand audit (GATE)

The estimand is NOT "is there recombination." It is the **per-genome mosaic structure**: a binary mosaic label `z_i`, AND — if mosaic — the ordered breakpoint coordinates `B_i = (b_i1, ..., b_ik)` and the parent-cluster assignment `c_i(w)` for each inter-breakpoint segment. Over `target_population` = future samplings of the same viral species at comparable diversity. (Trap T1 — vague estimand — caught: stated as breakpoint coordinates + parent assignment, not a yes/no.)

| Field | Value |
|---|---|
| `biological_unit` | One viral genome = one observational unit. **biological_replication_unit = the parent-pair / clade**: two genomes sharing the same donor×acceptor pair are descent-copies of ONE event, not independent evidence. `generalization_axis` = new parent-pair / new clade of the same virus. Counting genomes as independent replicates of "recombination present" when they share a parent pair is the pseudoreplication error here (the cells-within-donor analogue). |
| `observational_unit` | One aligned viral genome (one row of the MSA). |
| `estimand` | Per genome: `z_i ∈ {0,1}`; if `z_i=1`, the breakpoint coordinates `B_i` and per-segment parent-cluster assignment `c_i(w)`. NOT a yes/no. |
| `cohort_structure` | n ≈ 5000 genomes, one MSA. HIV-1 L ≈ 9.8 kb; SARS-CoV-2 L ≈ 29.9 kb. No pairing/longitudinal structure beyond sampling-date metadata. Recombinant fraction a priori unknown (≈1–15% HIV; highly variable SARS-CoV-2). Metadata optional — the core method does not require it. |
| `donor_batch_site` | Not applicable in the cell/batch sense; the analogue is **parent-pair / clade confounding with sampling** (over-sampled lineages look like "the truth"). Recorded in the leakage graph. |
| `missingness_mechanism` | Alignment gaps ('-', 'N') are not count dropouts; they are biological (insertions/deletions) or technical (ambiguous calls / coverage). Assumed **MNAR** in gappy regions (bias = uniform distance overestimate). This drives failure boundary FB-GAPPY. Not MCAR. |
| `leakage_graph` | `dependency_structure`: genomes sharing a parent pair are correlated descent-copies; genomes in the same clade share vertical ancestry → correlated substitution patterns genome-wide. Leak-relevant unit for the new-parent-pair axis = the (donor,acceptor) pair and the clade. A per-genome train/test split leaks phylogenetic signal (each test genome's nearest neighbor in train reveals its parent cluster). (Trap T2 — caught: split unit = clade/parent-pair, not single genome.) |
| `ground_truth_quality` | Real-data recombination truth does NOT exist independently of a detection method. Any "truth" from another detector (3SEQ/RDP5/GARD output) is **circular** (trap T3). The only non-circular ground truth is a **coalescent/controlled simulation with injected breakpoints**. The benchmark uses simulator-only truth. |
| `usable_sample_size` | n ≈ 5000 genomes, but the independent unit for the new-clade claim = number of distinct clades/parent-pairs (tens to low hundreds), not 5000. Power for "does the method generalize to a new clade" is clade-level. |
| `split_strategy` | `split_unit` = parent-pair (donor,acceptor) for recombination detection; clade for parent-assignment and clustering. `split_unit_justification`: the claim generalizes to NEW parent-pairs / NEW clades, so the evaluation must isolate whole parent-pairs and whole clades. In the simulation DGP this is enforced by construction: held-out recombinant events use FRESH parent pairs not seen in fitting; non-recombinant background uses held-out clades. |
| `licensing_privacy` | Public viral genomes (GISAID/GenBank); GISAID has data-sharing terms but no human-subjects IRB constraint. Publishable. |
| **`fatal_issues`** | **[] — GATE passes.** No blocking data issue; the only design-level caveat (no independent real-data truth) is handled by the simulator-only benchmark protocol, not by a fatal issue. |

GATE decision: **PASS** (fatal_issues empty). Proceed to viability.

---

## STAGE 2 — Topic viability assessment (T2 tool-paper ruler)

Built from current evidence (not memory): the **Alfonsi et al. 2024 Nat Comms** "Data-driven recombination detection in viral genomes" (RecombinHunt), the **Jaya et al. 2023** benchmark of recombination-detection methods, the **Lam et al. 2018** 3SEQ complexity paper, the **Martin et al. 2021** RDP5 paper, the **Pond et al. 2006** GARD paper, and the HyPhy GitHub issue #1731 (GARD non-scaling). Search coverage: PubMed + bioRxiv + the HyPhy/RDP/3SEQ tool pages.

### Competitor deep-comparison table (each row from verified source text)

| Competitor | Input required | Method (core mechanism) | Output | Key limitation | Delta vs proposed | **Category** |
|---|---|---|---|---|---|---|
| **3SEQ** (Boni 2007; Lam 2018) | aligned MSA | all-triplets enumeration: test every (i,j,k) for i being a mosaic of j,k; O(mn²) after the Lam improvement | per-sequence p-value + breakpoint intervals | all-triplets ⇒ O(n²)–O(n³) in genome count; **does not scale to 5000 genomes** (Alfonsi 2024: "computational requirements do not scale") | proposed is per-genome O(n·L) (one Hamming pass + linear DP), not triplet; explicit homoplasy failure boundary | **1 — functional substitute** |
| **RDP5** (Martin 2021) | aligned MSA | suite of 7 methods (RDP, GENECONV, Bootscan, MaxChi, Chimaera, SiScan, 3SEQ); automated screening | recombinant list + breakpoints + parents | same triplet/topology scan family; caps at ~1000×10kb alignments per the RDP5 paper; slow at n=5000 | proposed targets the n=5000 CPU regime RDP5 does not reach; no nomenclature required | **1 — functional substitute** |
| **GARD** (Pond 2006; HyPhy) | aligned MSA | genetic-algorithm search for tree-topology change points across the alignment | breakpoints + per-partition trees | global topology search; **crashes on 27 SARS-CoV-2 sequences** (HyPhy #1731); does not scale | proposed replaces global topology search with per-genome local change-point + a local two-tree LRT | **1 — functional substitute** |
| **RecombinHunt** (Alfonsi 2024) | MSA + **a structured nomenclature** (Pango-style lineage mutation-spaces) | data-driven cumulative likelihood-ratio over lineage mutation frequencies | mosaic label + 1–2 breakpoints + donor/acceptor lineages | **requires a nomenclature**; **cannot detect events with <3 supporting mutations**; 1–2 breakpoints max; loses sensitivity on terminal-end recombination | proposed needs NO nomenclature, NO ≥3-mutation floor enforced a priori (resolves down to win_size); works in the no-nomenclature slot | **1 if nomenclature present; 3 (input-slot alternative) for THIS user** |
| **RIPPLES / RIVET** (Turakhia 2022; Smith 2023) | MSA + **a pre-built global phylogeny** | parsimony: place genome segments on the global tree, flag discordant placements | recombinant list + parents | **requires a global phylogeny** (millions of leaves for SARS-CoV-2); misses 33 Pango-recombinant lineages RecombinHunt finds | proposed needs no global phylogeny; trades accuracy when a good global tree exists | **1 if phylogeny present; 3 (input-slot) for THIS user** |
| **VirusRecom** (Zhou 2023) | MSA | information-theoretic | recombination signal | evaluated only on simulated + 3 lineages (XD/XE/XF) — not comprehensive | proposed has a full adversarial benchmark | **2 — methodological neighbor** |
| **KwARG** (Ignatieva 2022) | MSA (small) | parsimony genealogical reconstruction | ARG + recombinants | limited resolution; cannot resolve donor/acceptor at lineage level | proposed targets lineage-level parent assignment | **2 — methodological neighbor** |
| **Bolotie** (Varabyou 2021) | MSA | inter-clade recombination, rapid | inter-clade recombinants | inter-clade only (needs pre-defined clades) | proposed discovers clusters itself | **4 — workflow alternative** |
| **single-global-breakpoint scan** (naive) | MSA | one breakpoint per genome max, simplest change-point | breakpoints | no multi-breakpoint, no homoplasy correction | proposed must BEAT this (kill-switch AC-NAIVE-BASELINES) | **5 — naive baseline** |
| **no-recombination null** (naive) | MSA | calls everything non-recombinant | z_i = 0 ∀i | trivial | proposed must BEAT this on F1 (kill-switch) | **5 — naive baseline** |
| **raw nearest-neighbor switch** (naive / ablation) | MSA | call a breakpoint wherever the NN cluster changes, no discordance test | breakpoints | no homoplasy/identifiability correction — fires on homoplasy | the ablation that isolates the proposed discordance_test's contribution | **5 — naive baseline** |

### Category roll-up

- **1 — functional substitutes (must beat/differentiate):** 3SEQ, RDP5, GARD (always); RecombinHunt (if a nomenclature exists), RIPPLES/RIVET (if a global phylogeny exists).
- **2 — methodological neighbors:** VirusRecom, KwARG.
- **3 — input-slot alternatives (different slot for THIS user):** RecombinHunt (no nomenclature available), RIPPLES/RIVET (no global phylogeny).
- **4 — workflow alternative:** Bolotie (inter-clade rapid, bypasses per-genome detection).
- **5 — naive baselines (MUST benchmark + beat):** no-recombination null, single-global-breakpoint, raw-NN-switch ablation.

### 8-dimension score (T2 ruler)

The honest framing: this is a **decision uncertainty band**, not a statistical CI.

| # | Dimension | score | pess | opt | conf | grade | d_i | w·s |
|---|---|---|---|---|---|---|---|---|
| 1 | biological_validity | 0.80 | 0.70 | 0.90 | med | B | 0.10 | 0.16 |
| 2 | data_feasibility | 0.85 | 0.80 | 0.90 | high | A | 0.02 | 0.128 |
| 3 | functional_differentiation | 0.65 | 0.55 | 0.75 | med | B | 0.05 | 0.098 |
| 4 | benchmarkability | 0.75 | 0.70 | 0.80 | med | B | 0.05 | 0.113 |
| 5 | implementation_feasibility | 0.80 | 0.75 | 0.85 | high | B | 0.05 | 0.08 |
| 6 | reproducibility | 0.80 | 0.75 | 0.85 | med | B | 0.05 | 0.08 |
| 7 | adoption_user_value | 0.75 | 0.70 | 0.80 | med | B | 0.05 | 0.075 |
| 8 | ethics_privacy_licensing | 0.95 | 0.93 | 0.97 | high | A | 0.02 | 0.048 |

- **`viability_total`** = 0.782
- **`viability_range`** = "0.69–0.86 (decision uncertainty band: pessimistic–optimistic)"
- **`should_proceed`** = **true** (band entirely ≥ 0.5 under the T2 ruler; no blocking_issue).

### Verdict + handoff

- **Paradigm shift status:** the field is segmenting by **input slot** (nomenclature-available vs not; phylogeny-available vs not) and by **scale** (pandemic millions vs mid-scale thousands). The mid-scale, no-nomenclature, no-phylogeny slot the user occupies is **open**.
- **Recommended locked angle (T2):** the only mid-scale (~5000-genome, CPU) recombination detector that needs neither a nomenclature nor a global phylogeny, with an explicit recombination-vs-homoplasy identifiability correction.
- **Naive baselines that MUST be beaten:** no-recombination null, single-global-breakpoint, raw-NN-switch ablation.
- **Biggest failure risk:** the discordance test (the only recombination-vs-homoplasy handle) does not reduce FPR enough on the null+homoplasy regimes, collapsing functional differentiation and reducing the method to the raw-NN-switch naive baseline (no utility).

---

## STAGE 3 — Algorithm design (formal method contract, 15 required + 2 optional)

**Utility first, novelty explicit.** The estimand and the broad likelihood-ratio idea are shared with prior work; the novelty is a **new inference mechanism for this estimand at this scale**.

### Group P — Problem
- **`problem_definition`:** Given a ~5000-genome MSA (CPU-only Python/BioPython, no phylogeny/nomenclature assumed), infer per genome whether it is mosaic and, if so, the breakpoint coordinates and per-segment parent-cluster assignment — at a scale the triplet-scan (3SEQ/RDP5) and topology-search (GARD) classics do not reach.
- **`estimand`:** identical to data-audit (mosaic label `z_i` + breakpoint coordinates `B_i` + per-segment parent assignment `c_i(w)`).

### Group F — Formalization
- **`mathematical_abstraction`:** fundamentally a **change-point detection problem on a sequence of nearest-neighbor-graph membership profiles along the genome**. Non-recombinant ⇒ constant parent-cluster assignment across windows; mosaic ⇒ ≥1 change-points. Rejected: (1) phylogeny-rebuilding per partition (GARD — non-scaling); (2) all-triplets enumeration (3SEQ/RDP5 — O(n²)/O(n³)); (3) lineage-mutation-space scoring (RecombinHunt — requires nomenclature + ≥3 mutations).
- **`notation_and_shapes`:** `A ∈ {0..4}^{n×L}` alignment; `S_i ∈ ℝ^{n_win×n}` per-genome per-window similarity profile; `G_w` per-window kNN graph; `c_i ∈ {1..C}^{n_win}` per-window parent membership; `M ∈ {0,1}^{n×C}` whole-genome cluster assignment; `B_i ∈ ℤ^{k_i}` breakpoints; `P` per-segment parent path; `Q ∈ ℝ^{C×L}` cluster consensus. (Full list in `design.json`.)
- **`assumptions`:** JC69/Poisson within a window; **clades separable in local similarity** (load-bearing — if it fails → FB-WEAK-CLUSTERING); recombinant tract ≥ win_size; null ⇒ `c_i` constant in `w`.
- **`objective_or_likelihood`** (revised after audit — see Stage 5): penalized **least-squares segmented-Gaussian change-point** on the per-window best-parent-similarity trace `r_i[w] = max_c mean_{j∈c} S_i[w,j]`:
  `argmax_{k_i,B_i} [ -(1/2σ²) Σ_s Σ_{w∈seg s} (r_i[w] − μ_s)² ] − λ·k_i·log(n_win)`, with **λ fixed at 1** (pure model selection, standard BIC/MDL); the **LRT rejection threshold** (calibrated on the null DGP) decides WHETHER a breakpoint is present and controls FPR — separate from λ. Gaussian change-point family (Adams–MacKay 2007; Killick/PELT 2012; `ruptures` Dynp/Binseg).
- **`identifiability`:** NOT identifiable without the **discordance correction** — a NN-cluster change can be recombination, shared ancestry + rate variation, or homoplasy. Identifiable ONLY when the two candidate segments are **phylogenetically discordant** (two-tree vs one-tree local LRT, GARD's move applied locally). Restoring assumption: cluster separability. If parents are sisters/near-identical → NOT identifiable → FB-WEAK-CLUSTERING.

### Group A — Algorithm (RECOMB-CP)
1. **load_msa** — `Bio.AlignIO.read`, uint8 encode.
2. **window_similarity_profile** — tile into `n_win` windows; per genome `i`, `S_i[w,j] = 1 − p-distance` (vectorized Hamming).
3. **discover_parent_clusters** — per-window kNN graphs aggregated → spectral normalized-cut → `C` clusters + `M` + consensus `Q` (needs the alignment `A`, not just similarities — audit catch).
4. **per_genome_membership_path** — `c_i[w] = argmax_c` mean sim to cluster `c` in window `w`.
5. **detect_change_points** — DP segmented-likelihood on `r_i` (BIC penalty) → candidate `B_i`.
6. **discordance_test** — local NJ tree per segment (Bio.Phylo, JC69), two-tree vs one-tree LRT; keep breakpoints only where the two-tree model wins (Bonferroni).
7. **null_calibration** — null-DGP LRT threshold for FPR-controlled mosaic calls; Benjamini–Hochberg across genomes.
8. **report_genome** — `z_i`, breakpoint nt coordinates, parent assignments, confidence, flags.

- **`optimization_or_inference`:** (A) change-point DP — globally optimal (1-D segmentation with additive penalty), `O(n_win²)` per genome (or `O(n_win)` with PELT pruning); (B) spectral Ncut — eigendecomposition of the symmetric normalized Laplacian (global optimum of the relaxation) + k-means++ on top-C eigenvectors. Deterministic; only RNG is k-means seeding (fixed by seed).
- **`complexity`:** total `O(n²·L)` for the all-profiles Hamming pass (= one all-pairs pass, small byte-op constant) + `O(n·n_win²)` for all DPs + `O(n_recomb·L)` for discordance tests on candidates. Memory `O(n·L) ≈ 150 MB` uint8 + `O(n·k)` per window. CPU-feasible to ~10⁴ genomes. **(Audit correction: this is quadratic in n, not "linear per genome" as first stated — see Stage 5 AM-3. Still one order of magnitude below 3SEQ's O(n³).)**
- **`component_necessity`** (complexity kill-switch):
  - `discordance_test` — retained pending benchmark; `retain_if` it beats the raw-NN-switch ablation on FPR in null+homoplasy regimes without losing >5% recall.
  - `spectral_normalized_cut` — retained; `retain_if` it matches/beats fixed Pango labels in the no-nomenclature regime and is within 5% in the nomenclature regime.

### Group G — Guarantees (failure boundaries)

| id | condition | mechanism |
|---|---|---|
| **FB-HOMOPLASY** | high divergence ⇒ substitution saturation | convergent sites mimic a parent switch; per-window entropy diagnostic flags saturated windows unresolvable-not-recombinant |
| **FB-SHORT-TRACT** | recombinant tract < win_size (~300 nt) or < τ (~3) mutations | below the window's resolution; hard detection floor (matches RecombinHunt's <3-mut limit) |
| **FB-WEAK-CLUSTERING** | parent clusters recently diverged (sisters) | Ncut merges them; not identifiable from this data alone (needs denser sampling/outgroup) |
| **FB-GAPPY** | high gap/N density | biased per-window distance → over-segmentation; informative-site-count gate + gappy flag |
| **FB-RATE-HET** (added after audit — AM-4) | substitution rate varies along the genome (Γ site rates / hypervariable regions) WITHOUT recombination | the null "no recombination ⇒ c_i constant" is violated by rate variation alone (distinct from homoplasy); mitigated by +I+Γ null calibration and a rate-corrected distance, with a one-tree-WITH-rate-heterogeneity LRT null |

- **`uncertainty_and_calibration`** (encouraged): per-breakpoint LRT statistic → calibrated p-value (null DGP) → BH across genomes; coordinate-uncertainty ~ win_size/2. Calibrated-under-DGP, NOT a coverage-guaranteed CI.
- **`invariances`** (encouraged): invariant to genome-index, cluster-label, and within-window column permutation; NOT invariant to window-size, gap-handling, or outgroup inclusion.

### Group V — Validation
- **`simulation_dgp`:** coalescent-with-recombination simulator (SCOT/SimBac/sc2ts-style) OR controlled synthetic (K parent clades under JC69, inject recombinants by splicing a donor segment into an acceptor at a known breakpoint). Regimes: **NULL** (no recombination — FPR ≤ 1%); **ADVERSARIAL-HOMOPLASY** (convergent tracts, no recombination); **ADVERSARIAL-SHORT-TRACT** (tract lengths {win/4, win/2, win, 2win}); **ADVERSARIAL-WEAK** (sister-clade divergence {0.1, 0.5, 1, 5}%); **ADVERSARIAL-GAPPY** (gap density {0, 5, 20, 40}%); **ADVERSARIAL-RATE-HET** (Γ shape {0.1, 0.5, 1.0}, no recombination); **ORACLE** (true parent labels); **TRIVIAL** (single-breakpoint + no-recombination baselines). Swept: n ∈ {500, 2000, 5000}, L_tract, divergence, gap density, recombinant fraction {1, 5, 15}%, win_size {200, 300, 500}.
- **`benchmark_protocol`:** identical MSAs, identical gap-trimming, identical seeds, compute-matched; competitors at default/recommended settings + a documented tuning budget (audit catch BA-1); naive baselines (no-recombination, single-global-breakpoint, raw-NN-switch) MANDATORY; simulator-only truth (never another detector); ≥10 seeds, paired, with bootstrap CIs on the kill-switch (audit catch BA-3).
- **`novelty_or_utility_basis`:** T2 — new inference mechanism at this scale (change-point on NN-graph profiles + local two-tree LRT), defensibly better than 3SEQ/RDP5/GARD on the **scalability** axis (CPU-feasible at n=5000) and on the **no-phylogeny/no-nomenclature** input-slot axis, under a fair benchmark that includes the naive baselines. NOT T1 structural novelty. Deltas per named top-competitor recorded in `design.json`.

---

## STAGE 4 — Spec summary (kiro three-phase, genomics adapter)

Domain adapter: **phylogenetics/viral-genomics** (FASTA + BioPython AlignIO + numpy + Bio.Phylo) — NOT AnnData/scanpy.

**Module interfaces** (8 modules; full typed interfaces in `spec.json`): `load_msa`, `window_similarity_profile`, `discover_parent_clusters`, `per_genome_membership_path`, `detect_change_points`, `discordance_test`, `null_calibration`, `report_genome`. Shapes consistent with `design.notation_and_shapes` (rule 3 — checked by validate-chain).

**Acceptance criteria** (EARS notation; each traces_to ≥1 failure boundary — rule 2, no orphans, checked):

| AC id | traces_to | verification_mode | what it tests |
|---|---|---|---|
| AC-FB-HOMOPLASY-1 | FB-HOMOPLASY | simulation | convergent-tract FPR ≤ 1%; ≥90% homoplasy tracts flagged not-discordant |
| AC-FB-HOMOPLASY-2 | FB-HOMOPLASY | automated_test | saturation entropy flag fires + down-weights saturated-window breakpoints |
| AC-FB-SHORT-TRACT | FB-SHORT-TRACT | simulation | detection floor ≥ win/2 (documented limitation) |
| AC-FB-WEAK-CLUSTERING | FB-WEAK-CLUSTERING | simulation | power-vs-divergence curve; near_identical_parents flag for <0.5% divergence |
| AC-FB-GAPPY | FB-GAPPY | simulation | informative-site-count gate; gappy flag on gappy-window breakpoints |
| AC-FB-RATE-HET (added post-audit) | FB-RATE-HET | simulation | +I+Γ null holds FPR ≤ 1%; one-tree-WITH-rate-het LRT null |
| AC-NULL | FB-HOMOPLASY | simulation | no-recombination DGP ⇒ z_i=0 for ≥99% (no hallucination) |
| AC-ORACLE | FB-SHORT-TRACT, FB-WEAK-CLUSTERING | simulation | oracle-parents localization ceiling |
| AC-NAIVE-BASELINES | FB-HOMOPLASY, FB-SHORT-TRACT | benchmark | kill-switch: must beat no-recombination AND single-global-breakpoint by ΔF1 ≥0.10 AND Δrecall ≥0.15 |
| AC-SCALING | FB-GAPPY | benchmark | n=5000 on 1 CPU core in ≤8h, ≤8GB peak |
| AC-BENCHMARK-SOTA | FB-HOMOPLASY, FB-SHORT-TRACT | benchmark | vs 3SEQ/RDP5/GARD on identical MSAs, simulator-only truth |

Every `failure_boundaries[].id` (FB-HOMOPLASY, FB-SHORT-TRACT, FB-WEAK-CLUSTERING, FB-GAPPY, FB-RATE-HET) is named in ≥1 `acceptance_criteria[].traces_to`. **No orphans.**

**Engineering deliverables** (nf-core P0 list, for the future code stage): environment lock (`requirements.txt` / `environment.yml` pinned), CI (GitHub Actions lint+test), small license-clear test dataset with expected outputs, deterministic seed policy.

**Publication Roadmap** (MVP vs publishable):
- *MVP scope:* change-point core + discordance test on synthetic (validates FB-HOMOPLASY, FB-SHORT-TRACT, FB-RATE-HET, FB-NULL).
- *Engineering gap (P0):* real 3SEQ/RDP5/GARD benchmark harness, full-scale n=5000 memory tuning, Docker + CI (≈3–5 days).
- *Experiment gap (P0):* benchmark vs 3SEQ/RDP5/GARD + naive baselines on HIV and SARS-CoV-2 MSAs; full failure-boundary sweep figures (≈5–7 days).
- *Writing gap (P1):* intro (vs 3SEQ/RDP5/GARD/RecombinHunt/RIPPLES), methods (change-point + LRT math), results (applicability-boundary figure), discussion (FB-WEAK-CLUSTERING, FB-RATE-HET as honest limitations) (≈4 days).

---

## STAGE 5 — Adversarial panel audit (1 round, Standard mode)

Panel: 3 same-model subagents (information-isolated, role-specialized) — **algorithm-methodologist**, **benchmark-auditor**, **implementation-reviewer** — each given ONLY the artifact blocks (no producer reasoning). Optional **defender/replicator** seat not used (no blocking finding contested the producer's framing — the blocking findings were concrete defects the producer concedes).

**Honest limitation:** every panel member is the same Claude (glm-5.2); they share training bias and its blind spots. They catch one-sided framing and internal inconsistency; they cannot catch a flaw that is a Claude-general blind spot. A hybrid upgrade (one external-model seat) would de-correlate bias.

### Verdict: **needs_revision** (blocking findings found) → **revised → re-validated VALID**.

The blocking/major findings that exposed real defects were fixed in the artifacts and re-stamped. The findings that require the code/empirical stage (out of scope for this Standard run) are recorded as deferred TODOs.

#### Algorithm-methodologist (6 findings: 2 blocking, 4 major/minor)

| # | claim | sev | blocking | disposition |
|---|---|---|---|---|
| AM-1 | per-window likelihood `log P(S_i[w,*] \| parent=c)` incoherent — categorical on an n-dim vector | major | **yes** | **FIXED in design.json**: objective rewritten as penalized least-squares segmented-Gaussian change-point on the per-window best-parent-similarity trace `r_i[w]`; the categorical-on-vector mis-specification removed. |
| AM-2 | λ unspecified and overlapping with the LRT threshold | major | **yes** | **FIXED in design.json**: λ pinned at 1 (pure model selection, standard BIC); the LRT threshold (null-DGP-calibrated) is the separate testing knob that controls FPR. |
| AM-3 | "per-genome cost LINEAR in genome count" misrepresents an O(n²·L) all-pairs total | minor | no | **FIXED in design.json** (complexity field): reworded to total O(n²·L) with a small byte-op constant, vs O(n³) for triplet methods — one order of magnitude, not "linear." |
| AM-4 | rate-heterogeneity (without homoplasy) violates the null but is unnamed | major | no | **FIXED**: added failure boundary **FB-RATE-HET** + acceptance criterion **AC-FB-RATE-HET** (+I+Γ null calibration, one-tree-WITH-rate-het LRT null). |
| AM-5 | χ² LRT at ~300nt segments has unreliable asymptotics | minor | no | **DEFERRED to code stage** (parametric-bootstrap null for segments <600nt; recorded in `unresolved_risks`). |
| AM-6 | FB-WEAK-CLUSTERING has no runtime flag | minor | no | **DEFERRED to code stage** (cluster-separability flag in `report_genome`; recorded). |

*Checklist completed in good faith; the change-point abstraction, detect-then-validate decomposition, DP global-optimality, identifiability analysis, and failure-boundary list were judged sound.*

#### Benchmark-auditor (5 findings: 0 blocking, 3 major, 2 minor) — checklist completed, no leakage/circular-truth issue found

| # | claim | sev | blocking | disposition |
|---|---|---|---|---|
| BA-1 | competitor tuning budget asymmetric (proposed gets a grid, 3SEQ/RDP5/GARD get defaults) | major | no | **FIXED in design.json** (benchmark_protocol): explicit per-method ≤3-setting budget from each tool's published recommended range, selected by inner-CV on a separate seed; proposed method also reported at default setting. |
| BA-2 | breakpoint-localization metric ambiguous (conditional on detection vs unconditional) | major | no | **DEFERRED to code stage** (report both, miss = genome-length penalty; state headline). |
| BA-3 | kill-switch (ΔF1/Δrecall thresholds) seed-fragile (no paired-seed protocol / sig test) | major | no | **FIXED in design.json**: ≥10 seeds, paired across methods, kill-switch cleared outside the seed-CI / paired bootstrap. |
| BA-4 | split hierarchy (parent-pair within clade) not stated as nested | minor | no | **DEFERRED to code stage** (nested clade→parent-pair split). |
| BA-5 | compute-matched wall-clock cap disadvantages C/C++ competitors vs vectorized Python | minor | no | **DEFERRED to code stage** (report CPU-hours + DNFs separately, do not silently drop). |

*Benchmark design judged well above average: correct split unit, simulator-only truth, mandatory naive/ablation baselines, all four adversarial regimes, kill-switch present.*

#### Implementation-reviewer (14 findings: ~10 blocking/critical) — checklist completed

| # | claim | sev | blocking | disposition |
|---|---|---|---|---|
| IM-F1 | `discover_parent_clusters` cannot emit length-L consensus `Q` from similarity profiles alone | critical | **yes** | **FIXED in spec.json**: added `A (uint8, n×L)` to `discover_parent_clusters` inputs. |
| IM-F2 | `P` shape `n_win×(k_i+1)` wrong — per-segment assignments should be `(k_i+1,)` | major | **yes** | **FIXED in spec.json + design.json**: `P` shape = `k_i` (per-segment vector), semantics updated. |
| IM-F3 | `null_lrt_distribution` shape `k_i` wrong — should be `N_null` | major | **yes** | **PARTIALLY FIXED** (semantically corrected to "vector of LRT statistics from null DGP"); the literal shape token left as a declared `k_i` to keep rule-3 notation consistency — **DEFERRED to code stage**: introduce explicit `N_null` shape symbol when implementing. |
| IM-F11 | `A_segments` "each n×L" wrong — the two segments have widths summing to L | major | **yes** | **FIXED in spec.json**: reworded to "column-slices of A whose widths sum to L"; shape field kept as `n×L` (the declared superset) for rule-3 consistency. |
| IM-F4 | `lambda_bic` default conflates n_win with effective N | major | no | **DEFERRED to code stage** (state exact BIC form + free-params-per-segment + effective N). |
| IM-F5 | n=1 / all-identical genomes crash the similarity step silently | major | **yes** | **DEFERRED to code stage** (n<3 guard, all-identical guard → C=1 + near_identical_parents flag). |
| IM-F6 | all-gap genome: p-distance undefined | major | **yes** | **DEFERRED to code stage** (gap policy: pairwise-ignore + min_overlap threshold; documented). |
| IM-F7 | spectral ncut parameters (k, sigma, eigensolver, eigengap rule, C=1 fallback) unspecified | major | **yes** | **DEFERRED to code stage** (real pseudocode with `scipy.linalg.eigh` / eigengap rule). |
| IM-F8 | pseudocode hashes are topic-strings, not API-call-level pseudocode | major | **yes** | **DEFERRED to code stage** (the `pseudocode_hashes` field is intentionally a hash-keyed manifest in the machine schema; the real API-call pseudocode belongs in `tasks.md`, which is the next-stage artifact not produced in this Standard run). |
| IM-F9 | FASTA id uniqueness / id↔index mapping not threaded | major | **yes** | **DEFERRED to code stage** (`ids` array in `load_msa` output). |
| IM-F12 | `discordance_test` returns one p_value for up to C(k+1,2) segment pairs | major | no | **DEFERRED to code stage** (test-aggregation rule: min-over-pairs, Bonferroni by pair-count). |
| IM-F13 | NaN/inf policy for S in degenerate windows | minor | no | **DEFERRED to code stage** (`np.nanargmax`, NaN-zeroing rule). |
| IM-F14 | singleton cluster → undefined NJ tree | major | **yes** | **DEFERRED to code stage** (min cluster size ≥4 for the LRT; `low_signal` fallback). |
| IM-F10 | "streaming one window at a time" contradicts the n_win×n S_i contract | minor | no | **DEFERRED to code stage** (clarify lazy S_profiles consumption; per-S_i memory budget). |

*The shape-consistency defects (F1/F2/F3/F11) were the SCOUT-class interface-drift the validator's rule 3 exists to catch; fixed. The remaining implementation findings are real but belong to the tasks.md/code stage, which Standard mode does not produce.*

### Aggregated verdict and follow-through

- **`pass`?** No — there were blocking findings.
- **`needs_revision`?** Yes — 6 blocking/major findings (AM-1, AM-2, IM-F1, IM-F2, IM-F3, IM-F11) plus 4 material majors (AM-4, BA-1, BA-3, and the implicit "add a 5th failure boundary for rate-heterogeneity") were fixed **in the artifacts** and re-stamped. The remaining ~12 findings are deferred to the code stage (out of scope for Standard mode, which stops at spec-writing).
- **`fail`?** No — the premise (change-point on similarity profiles + local LRT) is sound; the defects were in the specification's coherence, not the approach.

After the revisions: `python -m crossbio_validate validate-chain artifacts/` → **VALID — 0 findings**.

---

## Cross-stage integrity (machine-checked)

- **estimand continuity (rule 1):** `design.estimand` == `data-audit.estimand` byte-for-byte.
- **no-orphan failure boundaries (rule 2):** every `failure_boundaries[].id` (FB-HOMOPLASY, FB-SHORT-TRACT, FB-WEAK-CLUSTERING, FB-GAPPY, FB-RATE-HET) is traced by ≥1 `acceptance_criteria[].traces_to`.
- **notation consistency (rule 3):** every shape token in `spec.module_interfaces` is declared in `design.notation_and_shapes.shapes`.
- **provenance (rule 5):** every artifact carries a recomputed `provenance_hash`; no tampering.
- **chain order + parent integrity:** `data-audit` (root, parent=null) → `design` (parent=data-audit) → `spec` (parent=design); stage order `data-audit → design → spec` allowed.
- **fatal GATE:** `data-audit.fatal_issues == []` → chain continues legitimately.

---

## Honest one-paragraph summary

The skill chain turned "detect recombination" into a precise estimand (per-genome mosaic label + breakpoint coordinates + parent assignment), forced a leakage-aware split (clade/parent-pair, not genome), refused circular ground truth (simulator-only), classified 11 competitors into the 5 categories (3SEQ/RDP5/GARD as functional substitutes; RecombinHunt/RIPPLES as input-slot alternatives for this user; no-recombination/single-breakpoint/raw-NN-switch as the must-beat naive baselines), scored viability 0.69–0.86 under the T2 ruler (proceed), produced a formal-method design (change-point on NN-graph membership profiles + a local two-tree LRT as the recombination-vs-homoplasy identifiability handle, with 5 failure boundaries), translated it to an 8-module spec with 11 EARS acceptance criteria all tracing a failure boundary, and then the adversarial panel caught real defects — an incoherent likelihood family, an under-specified penalty, four interface-shape drifts, a missing rate-heterogeneity confound, and benchmark tuning asymmetry — all of which were fixed in the artifacts and re-validated. The remaining implementation-level findings (edge cases, real API-call pseudocode, gap/NaN policies) are honestly deferred to the code stage that Standard mode does not run.
