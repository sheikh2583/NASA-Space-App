# Current training results

The active training path uses CUDA. Read [CUDA_RESULTS.md](CUDA_RESULTS.md) for the GPU hardware verification, selection correction, accepted outputs, QA, and timing evidence. Read [TRAINING.md](TRAINING.md) to reproduce the supported workflow.

Current selected harmonization: **B1**, with selection CCC 0.8855 versus XGBoost CUDA 0.8696 across Terra+Aqua and Terra-only holdouts. All five scientific QA groups passed. The accepted downstream run recorded 399 verified GPU fits. A resumed downstream time must not be presented as full training time.

[GPU estimates](GPU_TRAINING_TIMES.md) distinguish measured RTX 4070 evidence from the unmeasured RTX 3090 projection. The historical experimental comparison remains in [CUDA results](CUDA_RESULTS.md) and Git history; the obsolete standalone CPU training report/instructions have been removed.
