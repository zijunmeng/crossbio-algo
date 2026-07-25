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

## Rule
Table A tells you **which fields** to mine; Table B tells you **which methods** those fields use. Use both — name the domain AND the specific technique borrowed.
