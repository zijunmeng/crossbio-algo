# Case: scRNA-seq imputation (home-field, single-cell)

## Research ask
I have sparse scRNA-seq counts. I want to **recover the true transcript counts at dropout
positions** (imputation). Build me an algorithm. Python (scanpy), CPU only, no DL.

## Constraints stated by the user
- Python (scanpy), CPU only, no deep learning.
- Sparse UMI count matrix; goal = recover counts at masked/dropout positions.
