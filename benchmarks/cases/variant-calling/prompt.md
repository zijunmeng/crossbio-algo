# Case: variant-calling (low-depth tumor WGS)

## Research ask
I have a panel of ~40 normal samples and one tumor sample, sequenced at low depth (~8x). I want to
**call somatic SNVs/indels** in the tumor. Build me an algorithm for it. I work in Python (pysam),
CPU only, no GPU.

## Constraints stated by the user
- Python + pysam, CPU only.
- Somatic (tumor vs the matched/pooled normal), not germline.
