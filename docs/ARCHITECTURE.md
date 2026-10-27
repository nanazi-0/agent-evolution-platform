# Architecture and trust boundaries

## Closed loop

```text
immutable baseline + production feedback
                  ↓
       proposer forms hypotheses
                  ↓
   meta-improver updates experiment strategy
                  ↓
 candidate workspace (declared files only)
                  ↓
 policy budget and forbidden-change guard
                  ↓
 held-out evaluator outside candidate tree
                  ↓
 independent quality/security control plane
                  ↓
 select only a statistically/operationally better child
                  ↓
 eligible → named human approval → version snapshot
                  ↓
 monitoring → feedback → next generation or rollback
```

## Security invariants

1. Candidate workspaces never contain hidden evaluation data.
2. The proposer cannot edit the evaluator, policies, approval code, quality gates, or audit store.
3. A candidate must improve by at least `minimum_improvement`; ties do not replace the parent.
4. A security failure is fail-closed even when the aggregate score improves.
5. Generated code is not executed on the host by default. The initial implementation mutates declarative artifacts only.
6. Approval requires a named actor. Automation may create an eligible release but may not impersonate a human.
7. Promotion creates snapshots; it never overwrites the immutable baseline.
8. Every material event enters a SHA-256 chained audit log.

An intermediate candidate with an incomplete gate may be retained only inside the isolated research lineage so later generations can build on it. It can never become `eligible`, be submitted as a passing external gate, or be approved for release until every required final gate passes.

## Evidence strength

The bundled demo proves orchestration, isolation, lineage, evaluation, external gate ingestion, approval boundaries and rollback mechanics. It does not prove a production agent is good. Production use requires real golden cases, unseen regression/adversarial sets, repeated trials, cost/latency limits and the full `agent-quality-security` profile against the actual target environment.

## L5-oriented extension

The optional successor-model adapter can invoke a separately sandboxed fine-tuning, distillation, synthetic-data or research pipeline. Its result is accepted only when it identifies a versioned model artifact, beats its frozen baseline and passes at least two held-out domains. The harness champion, meta-improver state, successor evidence, external quality result and audit chain form one evidence bundle.

The adapter is disabled by default because model training requires a user-selected model, data rights, compute budget and sandbox. Enabling an empty or unverifiable command fails closed when `required=true`.
