from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def submit_quality_result(root: Path, settings: dict[str, Any], run_id: str, candidate_id: str, evaluation: dict[str, Any], report_dir: Path) -> dict[str, Any]:
    if not settings.get("enabled", False):
        return {"enabled": False, "passed": True, "detail": "quality platform disabled"}
    quality_root = Path(str(settings["root"]))
    python = quality_root / ".venv" / "Scripts" / "python.exe"
    cli = quality_root / "qualityctl.py"
    required = bool(settings.get("required", True))
    if not python.exists() or not cli.exists():
        return {"enabled": True, "passed": not required, "detail": "quality platform or its virtual environment is unavailable"}
    envelope = {
        "platform": str(settings.get("platform", "Generic CI")),
        "layer": "rsi-candidate-evaluation",
        "passed": bool(evaluation["passed"]),
        "summary": f"RSI candidate {candidate_id} held-out score={evaluation['score']:.4f}",
        "run_id": f"rsi-{run_id}-{candidate_id}",
        "check_id": "governed-rsi-heldout-gate",
        "required": True,
        "duration_seconds": evaluation.get("duration_seconds", 0),
        "metrics": evaluation.get("metrics", {}),
        "evidence_uri": str(Path(evaluation["evidence"]).resolve()),
    }
    destination = report_dir / "quality" / f"{candidate_id}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    result = subprocess.run([str(python), str(cli), "external-ingest", str(destination)], cwd=quality_root, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False, timeout=120)
    return {
        "enabled": True,
        "passed": result.returncode == 0,
        "detail": (result.stdout + result.stderr).strip(),
        "envelope": str(destination.resolve()),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }

