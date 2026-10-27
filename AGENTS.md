# Project collaboration rules

- Keep the evaluator, hidden evaluation data, governance policy, and release approvals outside the mutable candidate surface.
- Never execute model-generated code on the host by default. Use an explicitly configured sandbox for code mutation experiments.
- A higher training score is not sufficient for promotion. Held-out quality, security, policy, and regression gates must pass.
- Treat `.runtime/`, `data/`, `reports/`, and `releases/` as generated runtime state.
- Do not commit credentials, production payloads, personal data, hidden evaluation cases, or raw model traces containing secrets.
- Python dependencies must be installed only in this project's `.venv`.
- Run `scripts/test.ps1` after changing the engine, policies, evaluator contract, persistence, or promotion logic.

