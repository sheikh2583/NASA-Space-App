# Contributor onboarding

Start with the current [README](../README.md). It includes fresh Windows/Linux initialization, a dataset-free mock UI launch, debugging, CUDA training, recovery, and deployment to your own GitHub Pages repository.

- [CUDA training guide](TRAINING.md): dependencies, input layout, smoke/quick/full sequence, logs, and recovery.
- [GPU time estimates](GPU_TRAINING_TIMES.md): RTX 4070 Laptop and RTX 3090 assumptions and evidence.
- [CUDA results](CUDA_RESULTS.md): accepted science and failed-trial diagnostics.
- [Hosting](HOSTING.md): snapshot refresh versus full API hosting.
- [Claude handoff](CLAUDE_HANDOFF.md): current implementation and continuation notes.

The earlier onboarding backlog described the pre-training, pre-hosting prototype and has been removed because it no longer represented the project. The live UI now uses named administrative filters on OSM; manual polygon/rectangle drawing is no longer the primary selection workflow. Training setup is CUDA-first. UI-only setup remains available without an NVIDIA GPU.
