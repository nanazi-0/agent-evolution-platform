# L5-oriented roadmap

## What is already executable

- L1: persistent evaluation feedback and failure memory;
- L2: persistent Prompt/behavior evolution;
- L3-ready: mutable Skill and declarative Harness surfaces with policy budgets;
- L4: the improver stores successful/rejected hypotheses and changes later search priority;
- L5-ready interfaces: isolated successor-model command, immutable model artifact identity, multi-domain held-out requirement and external quality/security gate.

The bundled demonstration reaches L4. It intentionally does not fabricate a trained successor model merely to display L5.

## What must be supplied for a bounded L5 experiment

1. A legally usable base model and versioned training dataset.
2. An isolated GPU training or distillation runner that implements the successor-model result contract.
3. At least two truly hidden domains that neither proposer nor trainer can read.
4. Repeated runs and confidence intervals showing the successor beats the frozen predecessor.
5. An evaluator built from deterministic tests, independent models and human calibration.
6. Compute, token, wall-time and generation budgets with hard stops.
7. Network-denied candidate sandboxes, ephemeral credentials and artifact signing.
8. Canary deployment, production drift monitoring and automatic rollback triggers.

## Evidence required before claiming L5-like behavior

- The successor model improves, not only its Prompt or Harness.
- The mechanism that proposes improvements also improves across generations.
- Gains transfer to unseen domains and do not rely on leaked benchmark answers.
- Safety, authorization, privacy and reliability do not regress.
- Improvement persists after a fresh process restart.
- Every accepted generation has reproducible artifacts, inputs, metrics and hashes.
- The result is described as a bounded experiment unless open-ended transfer has actually been demonstrated.

## Recommended technical choices

- Use the current platform as the outer research and governance loop.
- Use RRSI or HyperAgents only inside disposable containers as optional proposal engines.
- Use MLflow for model/training experiment tracking if model-weight evolution is enabled.
- Keep `agent-quality-security` as the external non-mutable judge.
- Start with a small open-weight model and LoRA/adapter training; do not begin by training a foundation model from scratch.

