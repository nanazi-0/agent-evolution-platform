from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .config import Settings
from .evaluator import Evaluation, evaluate
from .policy import validate_candidate
from .proposer import create_proposer, materialize
from .quality import submit_quality_result
from .reporting import write_report
from .store import Store, now
from .meta import initial_state, save_state, update_state
from .maturity import assess
from .successor import run_successor_adapter


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:6]


def _eval_dict(result: Evaluation) -> dict:
    return {"passed": result.passed, "score": result.score, "metrics": result.metrics, "failures": result.failures, "evidence": str(result.evidence), "duration_seconds": result.duration_seconds}


def run(settings: Settings) -> dict:
    root, run_id = settings.root, _run_id()
    baseline = settings.path(str(settings.project["baseline_dir"]))
    hidden_eval = settings.path(str(settings.project["hidden_eval"]))
    if not baseline.is_dir() or not hidden_eval.is_file():
        raise ValueError("baseline_dir or hidden_eval does not exist")
    runtime = root / ".runtime" / "candidates" / run_id
    report_dir = root / "reports" / run_id
    runtime.mkdir(parents=True, exist_ok=False)
    baseline_output = report_dir / "evaluations" / "baseline.json"
    baseline_eval = evaluate(settings.evaluation["command"], root, baseline, hidden_eval, baseline_output, int(settings.evaluation.get("timeout_seconds", 300)))
    store = Store(root)
    store.start_run(run_id, str(settings.project["name"]), baseline_eval.score)
    proposer = create_proposer(str(settings.evolution.get("provider", "deterministic")))
    parent_path, parent_id, parent_eval = baseline, "baseline", baseline_eval
    candidates: list[dict] = []
    accepted: list[str] = []
    max_generations = int(settings.evolution.get("max_generations", 3))
    count = int(settings.evolution.get("candidates_per_generation", 3))
    min_gain = float(settings.evolution.get("minimum_improvement", 0.01))
    target = float(settings.evolution.get("target_score", 1.0))
    quality_result = {"enabled": False, "passed": True, "detail": "not submitted"}
    meta_path = report_dir / "meta-improver-state.json"
    meta_state = initial_state(str(settings.evolution["objective"]), int(settings.evolution.get("experiment_budget", max_generations * count)))
    save_state(meta_state, meta_path)
    for generation in range(1, max_generations + 1):
        remaining_budget = int(meta_state["experiment_budget"]) - int(meta_state["experiments_used"])
        if remaining_budget <= 0:
            break
        proposal_sets = proposer.propose(parent_path, parent_eval.failures, min(count, remaining_budget), str(settings.evolution["objective"]), meta_state)
        if not proposal_sets:
            break
        generation_results: list[tuple[dict, Evaluation, Path]] = []
        for index, proposals in enumerate(proposal_sets, start=1):
            candidate_id = f"g{generation:02d}-c{index:02d}-{uuid4().hex[:6]}"
            candidate_path = runtime / candidate_id
            materialize(parent_path, candidate_path, proposals)
            policy = validate_candidate(parent_path, candidate_path, settings.policy)
            evidence_path = report_dir / "evaluations" / f"{candidate_id}.json"
            if policy.passed:
                result = evaluate(settings.evaluation["command"], root, candidate_path, hidden_eval, evidence_path, int(settings.evaluation.get("timeout_seconds", 300)))
            else:
                evidence_path.parent.mkdir(parents=True, exist_ok=True)
                payload = {"passed": False, "score": 0.0, "metrics": {}, "failures": [{"id": "policy", "detail": reason} for reason in policy.reasons]}
                evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                result = Evaluation(False, 0.0, {}, payload["failures"], evidence_path, 0.0, "")
            rationale = "; ".join(item.rationale for item in proposals)
            item = {"candidate_id": candidate_id, "run_id": run_id, "generation": generation, "parent_id": parent_id, "path": str(candidate_path.resolve()), "policy_passed": int(policy.passed), "evaluation_passed": int(result.passed), "score": result.score, "rationale": rationale, "evidence_path": str(evidence_path.resolve()), "created_at": now(), "changed_files": policy.changed_files, "policy_reasons": policy.reasons}
            store.add_candidate(item)
            candidates.append(item)
            generation_results.append((item, result, candidate_path))
        best_item, best_eval, best_path = max(generation_results, key=lambda entry: entry[1].score)
        previous_score = parent_eval.score
        accepted_id: str | None = None
        if best_item["policy_passed"] and best_eval.score >= parent_eval.score + min_gain:
            if best_eval.passed:
                quality_result = submit_quality_result(root, settings.quality_platform, run_id, best_item["candidate_id"], _eval_dict(best_eval), report_dir)
                if not quality_result["passed"]:
                    break
            parent_path, parent_id, parent_eval = best_path, best_item["candidate_id"], best_eval
            accepted.append(parent_id)
            accepted_id = parent_id
            store.audit("candidate_selected", parent_id, {"generation": generation, "score": parent_eval.score, "quality": quality_result})
        else:
            accepted_id = None
        if bool(settings.evolution.get("recursive_improver", True)):
            meta_state = update_state(meta_state, generation, previous_score, [entry[0] for entry in generation_results], accepted_id)
            save_state(meta_state, meta_path)
        if accepted_id is None or parent_eval.score >= target:
            break
    improved = parent_id != "baseline"
    successor = run_successor_adapter(root, settings.successor_model, parent_path, run_id, report_dir)
    successor_required = bool(settings.successor_model.get("required", False))
    status = "eligible" if improved and parent_eval.passed and quality_result["passed"] and (successor["passed"] or not successor_required) else "blocked"
    report = {"schema_version": "1.0", "run_id": run_id, "project": settings.project["name"], "created_at": now(), "status": status, "baseline_score": baseline_eval.score, "champion_id": parent_id, "champion_score": parent_eval.score, "accepted_lineage": accepted, "quality_platform": quality_result, "successor_model": successor, "meta_improver_state": str(meta_path.resolve()), "candidates": candidates, "human_approval_required": bool(settings.policy.get("require_human_approval", True)), "mutable_surface": settings.policy.get("allowed_paths", [])}
    report["maturity"] = assess(report, meta_state, successor)
    json_path, html_path = write_report(report, report_dir)
    store.finish_run(run_id, status, parent_id, parent_eval.score, json_path)
    report["report_json"] = str(json_path.resolve())
    report["report_html"] = str(html_path.resolve())
    return report


def approve(root: Path, run_id: str, actor: str, reason: str) -> dict:
    if not actor or actor == "automation":
        raise ValueError("approval requires a named human actor")
    store = Store(root)
    run_row = store.get_run(run_id)
    if run_row["status"] != "eligible":
        raise ValueError(f"run is not eligible: {run_row['status']}")
    candidate = store.get_candidate(str(run_row["champion_id"]))
    release_id = f"release-{uuid4().hex[:12]}"
    snapshot = root / "releases" / "snapshots" / release_id
    shutil.copytree(Path(candidate["path"]), snapshot)
    current = store.current_release()
    if current:
        store.deactivate(current["release_id"])
    manifest = {"release_id": release_id, "run_id": run_row["run_id"], "candidate_id": candidate["candidate_id"], "status": "active", "actor": actor, "reason": reason, "snapshot_path": str(snapshot.resolve()), "previous_release_id": current["release_id"] if current else None, "created_at": now()}
    store.add_release(manifest)
    pointer = root / "releases" / "current.json"
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def rollback(root: Path, actor: str, reason: str) -> dict:
    if not actor or actor == "automation":
        raise ValueError("rollback requires a named human actor")
    store = Store(root)
    current = store.current_release()
    if not current or not current.get("previous_release_id"):
        raise ValueError("no previous release is available")
    with store.connect() as db:
        previous = db.execute("SELECT * FROM releases WHERE release_id=?", (current["previous_release_id"],)).fetchone()
    if previous is None:
        raise ValueError("previous release record is missing")
    store.deactivate(current["release_id"], "rolled-back")
    store.deactivate(previous["release_id"], "active")
    manifest = dict(previous)
    manifest.update({"status": "active", "rollback_actor": actor, "rollback_reason": reason, "rolled_back_from": current["release_id"], "rollback_at": now()})
    (root / "releases" / "current.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    store.audit("rollback", previous["release_id"], manifest)
    return manifest
