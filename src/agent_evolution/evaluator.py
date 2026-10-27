from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Evaluation:
    passed: bool
    score: float
    metrics: dict[str, Any]
    failures: list[dict[str, Any]]
    evidence: Path
    duration_seconds: float
    stdout: str


def evaluate(command_template: list[str], project_root: Path, candidate: Path, hidden_eval: Path, output: Path, timeout: int) -> Evaluation:
    output.parent.mkdir(parents=True, exist_ok=True)
    values = {
        "python": sys.executable,
        "root": str(project_root.resolve()),
        "candidate": str(candidate.resolve()),
        "hidden_eval": str(hidden_eval.resolve()),
        "output": str(output.resolve()),
    }
    command = [str(part).format(**values) for part in command_template]
    started = time.perf_counter()
    result = subprocess.run(
        command, cwd=project_root, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False,
    )
    duration = round(time.perf_counter() - started, 3)
    if result.returncode != 0:
        raise RuntimeError(f"evaluator failed with exit code {result.returncode}: {result.stdout}{result.stderr}")
    payload = json.loads(output.read_text(encoding="utf-8"))
    score = float(payload["score"])
    if not 0 <= score <= 1:
        raise ValueError(f"evaluator score outside [0,1]: {score}")
    return Evaluation(
        passed=bool(payload["passed"]), score=score,
        metrics=dict(payload.get("metrics", {})), failures=list(payload.get("failures", [])),
        evidence=output, duration_seconds=duration, stdout=(result.stdout or "") + (result.stderr or ""),
    )
