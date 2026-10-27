from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .config import load_settings
from .engine import approve, rollback, run
from .store import Store


def root() -> Path:
    return Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description="Governed RSI agent evolution platform")
    sub = command.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--config", type=Path, default=root() / "configs" / "demo.toml")
    execute = sub.add_parser("run")
    execute.add_argument("--config", type=Path, default=root() / "configs" / "demo.toml")
    status = sub.add_parser("status")
    status.add_argument("--run-id", default="latest")
    approval = sub.add_parser("approve")
    approval.add_argument("--run-id", default="latest")
    approval.add_argument("--actor", required=True)
    approval.add_argument("--reason", required=True)
    revert = sub.add_parser("rollback")
    revert.add_argument("--actor", required=True)
    revert.add_argument("--reason", required=True)
    sub.add_parser("audit-verify")
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "doctor":
        settings = load_settings(args.config)
        quality = Path(str(settings.quality_platform.get("root", "")))
        print(f"python={sys.version.split()[0]}")
        print(f"project_root={root()}")
        print(f"venv={sys.prefix != sys.base_prefix}")
        print(f"provider={settings.evolution.get('provider')}")
        print(f"quality_platform={'ready' if (quality / 'qualityctl.py').exists() else 'unavailable'}")
        print(f"api_key={'set' if os.environ.get('EVOLUTION_API_KEY') else 'not-set (not needed for deterministic demo)'}")
        return 0
    if args.command == "run":
        result = run(load_settings(args.config))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"RSI_GATE={'ELIGIBLE' if result['status'] == 'eligible' else 'BLOCKED'}")
        return 0 if result["status"] == "eligible" else 1
    store = Store(root())
    if args.command == "status":
        print(json.dumps(store.get_run(args.run_id), ensure_ascii=False, indent=2))
        return 0
    if args.command == "approve":
        print(json.dumps(approve(root(), args.run_id, args.actor, args.reason), ensure_ascii=False, indent=2))
        return 0
    if args.command == "rollback":
        print(json.dumps(rollback(root(), args.actor, args.reason), ensure_ascii=False, indent=2))
        return 0
    if args.command == "audit-verify":
        passed, count = store.verify_audit()
        print(f"AUDIT_CHAIN={'PASS' if passed else 'FAIL'} events={count}")
        return 0 if passed else 1
    return 2

