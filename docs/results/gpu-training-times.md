# GPU training time estimates

Planning estimates updated 4 November 2026 for the current tabular XGBoost CUDA pipeline and the local 4.34-million-detection dataset. These are elapsed pipeline times, not neural-network epochs or installation/download times.

| Workflow | RTX 4070 Laptop, 8 GB | RTX 3090 Desktop, 24 GB |
|---|---:|---:|
| Quick training, reduced holdouts | 12–20 minutes | 10–18 minutes |
| Full training, six holdouts | 18–25 minutes | 13–22 minutes |
| Harmonization model stage alone, full | About 4–6 minutes | About 2–4 minutes |

These ranges assume the same processed coverage/features, local SSD, completed weather cache, about eight helper threads, sufficient system RAM, one run at a time, and a similarly capable host CPU. The laptop should be plugged in, cooled, and in its normal performance mode. Heavy background work, throttling, slow disks, swapping, extra data, changed hyperparameters, or a selected learned model requiring extra out-of-fold GPU fits can exceed the ranges.

## What was measured

The RTX 4070 Laptop with driver 592.82 and eight helper threads completed the initial full trial's model stage in **274 seconds**. Its recorded stages totaled about **19 minutes 6 seconds**, but the initial trial failed the historical anomaly-seam gate and was rejected. Following selection repair, the accepted **downstream resume from intervals** took **586 seconds**, including **399 verified CUDA fits**. The resumed figure excludes ingestion, selection, and repair, and must not be presented as full training time.

The RTX 3090 is **not attached or benchmarked**. Its numbers are estimates, not measured claims. They assume a comparable or better CPU/SSD; GPU model and VRAM alone are insufficient to predict elapsed time. Its larger memory gives more headroom, but memory capacity does not imply a threefold speedup.

## Why the expected difference is modest

In the recorded full trial, roughly half the elapsed time was outside the CUDA model/drift/outlook stages. Those CPU/I/O/calibration/anomaly stages remain a floor. The outlook stage also executes hundreds of small fits with launch/transfer/host overhead. Scaling only the useful GPU portion therefore gives overlapping whole-run ranges; the 3090 could be only slightly faster on this workload. Do not infer speed from GPU utilization or compare unlike quick/full runs.

## Obtain a fair benchmark on each machine

1. Use the same Git revision, input hashes/files, helper-thread count, and quick/full setting. Finish downloads before timing.
2. Run the installer and `python scripts/workflow.py gpu-check` on each machine.
3. Stop other project runs and restart the API only after training. Use `python scripts/workflow.py train --backend cuda --gpu-id 0 --threads 8`.
4. Save `results/runs/<timestamp>/execution.json`, `cuda-fits.jsonl`, `results/latest.json`, and hardware details. Exclude failed runs from accepted-science performance claims, while retaining their diagnostics.
5. Compare both stage timings and scientific results. A faster run is acceptable only when all QA gates pass. Repeat if thermal or background load makes one result unrepresentative.

No fresh full training was launched just to produce these estimates. Read [CUDA results](cuda-results.md) for existing evidence and [training operations](../guides/training.md) for commands.
