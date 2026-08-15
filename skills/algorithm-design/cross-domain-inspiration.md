# Cross-Domain Inspiration Pool

Reference for algorithm-design **Step 2 (Cross-Domain Inspiration)**. Mined from auto-sc's `_brainstorm_cross_domain` (dev mode) — the "mathematical essence → scientific domains" map, expanded with a complementary method-level table.

## How to use
1. From Step 1 you named the essence (e.g. "this is fundamentally a dynamics/time-series problem").
2. Look it up below → mine 3–5 concrete techniques from the listed domains.
3. You MUST cite ≥2 domains OUTSIDE the problem's home field. If every inspiration is from the home field, you have NOT crossed domains — redo Step 2.

## A. Essence → scientific domains (where to look)

| If the essence is... | Mine these domains |
|---|---|
| **动力学 / 时序** (ODE, PDE, vector fields, dynamical systems) | 流体力学 (Navier-Stokes solvers), 气象预测 (ensemble Kalman filters), 控制理论 (PID, optimal control), 量子力学 (Schrödinger solvers) |
| **序列 / 字符串** (encoding, compression, pattern matching) | 信息论 (Huffman / arithmetic coding, LZMA, BWT), 视频编解码 (H.264/H.265 motion estimation), 密码学 (entropy analysis, secure hashing), 计算语言学 (finite-state transducers) |
| **图 / 网络** (topology, message passing, community detection) | 社交网络分析 (community detection, influence propagation), 电力网络 (stability, load balancing), 博弈论 (Nash equilibrium on graphs), 交通网络 (shortest path, flow optimization) |
| **图像 / 空间** (segmentation, registration, feature extraction) | 卫星遥感 (multispectral analysis, change detection), 医学影像 (CT/MRI segmentation, deformable registration), 拓扑数据分析 (persistent homology, manifold learning), 天体物理 (source detection, cosmic web) |
| **概率 / 统计** (Bayesian inference, hypothesis testing, MCMC) | 金融量化 (stochastic calculus, Black-Scholes, risk modeling), 贝叶斯搜索理论 (optimal search patterns), 极值理论 (rare-event modeling), 流行病学 (compartmental models, R0) |
| **优化** (linear / nonlinear programming, combinatorial) | 运筹学 (supply chain, scheduling), 能源市场 (unit commitment, economic dispatch), 航空调度 (crew pairing, fleet assignment), 芯片设计 (placement & routing) |
| **高维统计** (dimensionality reduction, manifold learning) | 信号处理 (compressed sensing, sparse recovery), 心理测量学 (factor analysis, IRT), 宇宙学 (CMB power spectrum), 计算化学 (MD dimensionality reduction) |

## B. Math structure → method pool (solution-level)

| Math structure | Method pools |
|---|---|
| sparse / masked matrix completion | recommender systems (collaborative filtering), compressed sensing, image inpainting, Bayesian matrix factorization |
| signal recovery on a graph | graph signal processing (graph Fourier / wavelet), spectral graph theory |
| manifold + missing data | kernel regression on manifolds, Laplacian regularization, semi-supervised learning |
| zero-inflated counts | ecology / insurance zero-inflated & hurdle models, ZINB regression |
| distribution alignment | optimal transport (Wasserstein / Gromov-Wasserstein), domain adaptation, MMD |
| directed influence / causality | Granger causality, Bayesian networks, structural causal models |
| ordered-structure recovery | dynamical systems, RNA velocity, pseudotime / manifold learning |

## C. Paradigm Axes — flip these to break out of the field's default framing

The first abstraction an agent thinks of is anchored to the field's dominant paradigm. To genuinely diverge (范式不同), take the field's default framing and flip ≥2 of these axes:

| Axis | Default (most fields) | Flip to |
|---|---|---|
| **机制 vs 关联** | statistical association (correlate, regress, permute) | physics/mechanism: write the process as field equations, reaction-diffusion, or a dynamical system |
| **静态 vs 动力学** | static snapshot (one time, equilibrium assumed) | temporal dynamics: evolution, trajectories, transients |
| **个体 vs 关系** | the entity (cell, gene, sample) is the unit | the relation/interaction is the unit; structure emerges from edges not nodes |
| **全局 vs 局部** | one global model over all data | local models + consistency constraints; multiscale decomposition |
| **代数 vs 几何/拓扑** | algebraic operations on vectors/matrices | geometric (manifolds, curvature, fiber bundles) or topological (persistent homology, connectivity) structure |
| **确定性 vs 概率** | point estimate | full generative probability model with identifiable parameters |
| **判别 vs 生成** | predict/estimate the output | simulate the data-generating process; the estimator is the inverse of the simulator |
| **单目标 vs 博弈** | one objective to optimize | multiple agents with conflicting objectives (game-theoretic equilibrium) |
| **信息 vs 能量** | fit / minimize error | information-theoretic limits (channel capacity, mutual information, MDL); or variational/energy principles |
| **连续 vs 组合** | continuous optimization | discrete/combinatorial structure (matchings, flows, lattices, grammars) |

**How to use**: (1) name the field's dominant paradigm; (2) pick 2-3 axes; (3) flip them; (4) write down what abstraction the flip produces (one sentence); (5) judge it on utility vs the dominant paradigm — is the flipped framing closer to the true data-generating mechanism, or just different? Keep the one that serves the estimand better. **Flipping is a search strategy, not a selection rule** — a paradigm-different design that fails the utility bar loses to a rigorous in-paradigm one; but you only get to claim "the dominant paradigm is best" AFTER looking at the flips.

**Worked example — cell-cell communication (the SPICE lesson)**: field's dominant paradigm = *statistical association* (co-expression + database lookup). Flips: (a) mechanism → model ligand as a diffusion-reaction field over tissue space, receptor activation as local absorption — signaling becomes a PDE inverse problem; (b) relation → make the interaction (edge), not the cell, the statistical unit; estimate edge-level confidence directly; (c) information → treat sender/receiver as a communication channel; ask what is the transfer rate and what bounds it. Each flip produces a different algorithm family AND a different validation path — that is the point.

## Rule
Table A tells you **which fields** to mine; Table B tells you **which methods** those fields use; Table C tells you **how to re-frame the problem itself**. Use A+B+C — name the domain, the specific technique, and (for T1/T2) the paradigm you are in vs the field's default.
