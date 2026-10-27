from __future__ import annotations

from typing import Any


def assess(report: dict[str, Any], meta_state: dict[str, Any], successor: dict[str, Any]) -> dict[str, Any]:
    achieved = 0
    evidence: list[str] = []
    if report.get("candidates"):
        achieved = 1
        evidence.append("L1: evaluation feedback persisted across candidate attempts")
    if report.get("accepted_lineage"):
        achieved = 2
        evidence.append("L2: prompt/behavior artifacts changed persistently and improved held-out score")
    changed = {path for item in report.get("candidates", []) for path in item.get("changed_files", [])}
    if any(path.startswith(("skills/", "harness/")) for path in changed):
        achieved = max(achieved, 3)
        evidence.append("L3: skill or harness structure evolved")
    if len(meta_state.get("generation_productivity", [])) >= 2:
        achieved = max(achieved, 4)
        evidence.append("L4: improver strategy learned from previous generation outcomes")
    l5_checks = {
        "successor_model_improved": bool(successor.get("enabled")) and bool(successor.get("passed")),
        "multiple_heldout_domains": int(successor.get("heldout_domains", 0)) >= 2,
        "recursive_improver": len(meta_state.get("generation_productivity", [])) >= 2,
        "external_quality_gate": bool(report.get("quality_platform", {}).get("enabled")) and bool(report.get("quality_platform", {}).get("passed")),
        "autonomous_closed_loop": report.get("status") == "eligible",
    }
    if all(l5_checks.values()):
        achieved = 5
        evidence.append("L5-oriented evidence bundle satisfied for this bounded experiment")
    return {
        "achieved_level": achieved,
        "label": "bounded L5-oriented experiment" if achieved == 5 else f"L{achieved} demonstrated",
        "evidence": evidence,
        "l5_checks": l5_checks,
        "important_limit": "Even an L5 result here is bounded experimental evidence, not proof of open-ended general recursive self-improvement.",
    }
