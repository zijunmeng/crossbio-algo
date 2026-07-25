# SCOUT — Requirements

## User Need
研究者拥有配对 scMultiome (RNA+ATAC，无空间) + Stereo-seq (空间 RNA，无 ATAC)，想在亚细胞分辨率整合 + 推断空间 ATAC，发 **T2 工具论文** (Genome Biology/Bioinformatics)。全 CPU (无 GPU)，scanpy 生态。

## Goals (from algorithm-design)
配对-投射整合：用 scMultiome 的配对先验给 Stereo-seq 空间 RNA 补 ATAC 维度，输出**空间 ATAC + RNA-ATAC 联合整合状态 + 投射置信度**。

## Acceptance Criteria (EARS, trace to failure_boundary)
- **AC-1 ← failure_boundary ③ (RNA-ATAC 空间不保守)**: WHEN 整合落在细胞类型异质区域, THE SYSTEM SHALL 报告 per-cell `project_confidence` 下降, 不假装准。
- **AC-2 ← failure_boundary ② (空间 RNA 稀疏)**: WHEN per-cell RNA reads < 10, THE SYSTEM SHALL 标记 `obs['low_confidence']=True` 并启用邻域借用 (k≥15)。
- **AC-3 ← failure_boundary ④ (OT 计算)**: THE SYSTEM SHALL 在 100k 细胞全流程 CPU < 30 min / < 16 GB RAM (mini-batch OT, batch=4096)。
- **AC-4 (benchmark)**: 在配对 semi-synthetic 上, 空间 ATAC 恢复 AUROC > SCGLUE 基线 且 > ISON 基线, Δ ≥ 0.05。

## Out of Scope
- 不追求跨域方法新颖 (OT/矩阵分解是成熟方法, T2 增量定位)。
- 不做 GRN/cis-调控推断 (spaGRN/SCENIC+ 的领域)。
- 不做 cell segmentation (上游, 用现成 cellpose/spateo 输出)。

## Trace Table
| failure_boundary | validates |
|---|---|
| ③ RNA-ATAC 空间不保守 | AC-1 |
| ② 空间 RNA 稀疏 | AC-2 |
| ④ OT 计算成本 | AC-3 |
| benchmark delta | AC-4 |
