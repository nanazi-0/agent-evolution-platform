from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prompt = (args.candidate / "system_prompt.md").read_text(encoding="utf-8").lower()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))["requirements"]
    failures = [{"id": item["id"], "layer": item["layer"], "detail": "held-out requirement not satisfied"} for item in cases if item["needle"].lower() not in prompt]
    passed_count = len(cases) - len(failures)
    score = passed_count / len(cases)
    security = [item for item in cases if item["layer"] == "security"]
    security_passed = all(item["needle"].lower() in prompt for item in security)
    payload = {"passed": score >= 0.95 and security_passed, "score": score, "metrics": {"requirements_passed": passed_count, "requirements_total": len(cases), "security_passed": security_passed}, "failures": failures}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"score": score, "failures": len(failures)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

