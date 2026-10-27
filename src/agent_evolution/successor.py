from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_successor_adapter(project_root: Path, config: dict[str, Any], champion: Path, run_id: str, report_dir: Path) -> dict[str, Any]:
    if not config.get("enabled", False):
        return {"enabled": False, "passed": True, "detail": "successor-model adapter disabled"}
    command_template = list(config.get("command", []))
    if not command_template:
        return {"enabled": True, "passed": not bool(config.get("required", False)), "detail": "successor-model command is empty"}
    output = report_dir / "successor-model.json"
    values = {"python": sys.executable, "root": str(project_root.resolve()), "champion": str(champion.resolve()), "run_id": run_id, "output": str(output.resolve())}
    command = [str(part).format(**values) for part in command_template]
    result = subprocess.run(command, cwd=project_root, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=int(config.get("timeout_seconds", 7200)), check=False)
    if result.returncode != 0 or not output.exists():
        return {"enabled": True, "passed": False, "detail": f"successor command failed: exit={result.returncode}", "stdout": result.stdout, "stderr": result.stderr}
    payload = json.loads(output.read_text(encoding="utf-8"))
    required_fields = {"passed", "model_id", "artifact_uri", "baseline_score", "successor_score", "heldout_domains"}
    missing = sorted(required_fields - set(payload))
    if missing:
        return {"enabled": True, "passed": False, "detail": f"successor result missing: {', '.join(missing)}"}
    improved = float(payload["successor_score"]) > float(payload["baseline_score"])
    cross_domain = int(payload["heldout_domains"]) >= 2
    payload.update({"enabled": True, "passed": bool(payload["passed"]) and improved and cross_domain, "detail": "successor model improved on multiple held-out domains" if improved and cross_domain else "successor evidence is insufficient"})
    return payload

