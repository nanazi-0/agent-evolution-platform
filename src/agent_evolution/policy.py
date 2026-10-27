from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyResult:
    passed: bool
    reasons: list[str]
    changed_files: list[str]
    total_bytes: int


def _files(root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def validate_candidate(parent: Path, candidate: Path, policy: dict) -> PolicyResult:
    before, after = _files(parent), _files(candidate)
    changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
    reasons: list[str] = []
    allowed = [str(item) for item in policy.get("allowed_paths", [])]
    for name in changed:
        if not any(fnmatch.fnmatch(name, pattern) for pattern in allowed):
            reasons.append(f"path outside mutable surface: {name}")
    if len(changed) > int(policy.get("max_files_changed", 4)):
        reasons.append(f"changed file budget exceeded: {len(changed)}")
    total_bytes = sum(len(after.get(name, b"")) for name in changed)
    if total_bytes > int(policy.get("max_total_bytes", 32768)):
        reasons.append(f"changed byte budget exceeded: {total_bytes}")
    forbidden = [str(item).lower() for item in policy.get("forbidden_text", [])]
    for name in changed:
        text = after.get(name, b"").decode("utf-8", errors="replace").lower()
        for needle in forbidden:
            if needle in text:
                reasons.append(f"forbidden text in {name}: {needle}")
    return PolicyResult(not reasons and bool(changed), reasons or ([] if changed else ["no effective change"]), changed, total_bytes)

