# Research and implementation sources

The project reuses concepts, not source code, from these systems:

- Darwin Gödel Machine — archive-based open-ended agent code improvement: https://github.com/kew-lab/darwin-godel-machine
- HyperAgents — task/meta-agent self-referential modification: https://github.com/facebookresearch/HyperAgents
- Google RRSI — regularized harness evolution and out-of-distribution validation: https://github.com/google-research/rrsi
- OpenRSI — measurable AI4AI without claiming general RSI is solved: https://github.com/FrontisAI/OpenRSI
- MLflow prompt optimization — evaluation-driven prompt search and held-out comparison: https://mlflow.org/cookbook/agent-alignment-optimization/
- LangMem prompt optimization — persistent procedural-memory updates: https://langchain-ai.github.io/langmem/reference/prompt_optimization/
- openJiuwen — production agent framework, evaluation, memory, sandbox and evolution modules: https://github.com/openJiuwen-ai
- Microsoft Agentic Innovation — bounded, validated and reversible agent repair: https://www.microsoft.com/en-us/research/group/agentic-innovation/
- RSI survey — distinction between bounded refinement and open-ended RSI: https://arxiv.org/abs/2607.07663

## Deliberate differences

- No arbitrary generated-code execution on the host.
- No automatic human approval.
- No evaluator self-modification.
- No claim of model-weight self-training or open-ended intelligence improvement.
- Standard-library core and provider-neutral command/HTTP contracts.

