# Connect a real agent

1. Copy only the mutable artifacts into `targets/<name>/baseline/`.
2. Keep production credentials and hidden evaluation data outside that directory.
3. Declare an explicit `allowed_paths` list. Start with Prompt and Skill files; do not begin with arbitrary source-code mutation.
4. Replace `tools/demo_evaluator.py` with a command that starts the candidate in an isolated environment and writes the evaluator contract below.
5. Add real task success, RAG grounding, prompt injection, authorization, privacy, regression, performance and cost cases.
6. Configure the external quality command or result ingestion in `agent-quality-security`.
7. Run several seeds and compare against a frozen baseline before approving a version.
8. Roll out to a small canary and send production failures back as new regression cases.

## Evaluator result contract

```json
{
  "passed": true,
  "score": 0.97,
  "metrics": {
    "task_success": 0.98,
    "unsafe_action_rate": 0.0,
    "p95_latency_ms": 1200
  },
  "failures": []
}
```

`passed` must fail closed on critical security failures. `score` must be between 0 and 1 and should represent a documented composite objective. Keep evaluator implementation and hidden inputs inaccessible to the candidate.

## Suggested production progression

- Stage 1: Prompt-only evolution with human approval.
- Stage 2: Prompt + Skill metadata and memory-policy evolution.
- Stage 3: Declarative workflow/Harness evolution in containers.
- Stage 4: Source-code patches with disposable sandboxes, network deny-by-default and signed promotion.
- Model-weight or training-loop evolution is a separate research program and is intentionally out of scope for the default runtime.

## Successor-model adapter contract

For an L5-oriented experiment, configure `[successor_model]` with an isolated training command. It must write:

```json
{
  "passed": true,
  "model_id": "agent-model-generation-2",
  "artifact_uri": "registry://models/agent-model-generation-2",
  "baseline_score": 0.71,
  "successor_score": 0.78,
  "heldout_domains": 3
}
```

The training process must not receive the hidden evaluation cases. A separate evaluator should score the resulting immutable model artifact. Set `required=true` only after this isolation is implemented.
