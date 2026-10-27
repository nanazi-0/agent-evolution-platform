from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def initial_state(objective: str, budget: int) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "objective": objective,
        "experiment_budget": budget,
        "experiments_used": 0,
        "failure_priority": [],
        "successful_hypotheses": [],
        "rejected_hypotheses": [],
        "generation_productivity": [],
    }


def update_state(state: dict[str, Any], generation: int, parent_score: float, results: list[dict[str, Any]], accepted_id: str | None) -> dict[str, Any]:
    updated = json.loads(json.dumps(state))
    updated["experiments_used"] += len(results)
    ranked = sorted(results, key=lambda item: item["score"], reverse=True)
    gains = [round(float(item["score"]) - parent_score, 6) for item in ranked]
    updated["generation_productivity"].append({
        "generation": generation,
        "best_gain": max(gains, default=0.0),
        "mean_gain": round(sum(gains) / len(gains), 6) if gains else 0.0,
        "accepted": accepted_id,
    })
    for item in ranked:
        record = {"candidate_id": item["candidate_id"], "rationale": item["rationale"], "gain": round(float(item["score"]) - parent_score, 6)}
        target = "successful_hypotheses" if item["candidate_id"] == accepted_id else "rejected_hypotheses"
        updated[target].append(record)
    remaining_failures: list[str] = []
    if ranked:
        evidence = json.loads(Path(ranked[0]["evidence_path"]).read_text(encoding="utf-8"))
        remaining_failures = [str(item.get("id")) for item in evidence.get("failures", []) if item.get("id")]
    updated["failure_priority"] = remaining_failures
    return updated


def save_state(state: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

