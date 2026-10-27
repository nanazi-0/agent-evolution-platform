from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


class Store:
    def __init__(self, root: Path) -> None:
        self.path = root / "data" / "evolution.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, project TEXT, status TEXT, baseline_score REAL, champion_id TEXT, champion_score REAL, created_at TEXT, completed_at TEXT, report_path TEXT);
            CREATE TABLE IF NOT EXISTS candidates(candidate_id TEXT PRIMARY KEY, run_id TEXT, generation INTEGER, parent_id TEXT, path TEXT, policy_passed INTEGER, evaluation_passed INTEGER, score REAL, rationale TEXT, evidence_path TEXT, created_at TEXT);
            CREATE TABLE IF NOT EXISTS releases(release_id TEXT PRIMARY KEY, run_id TEXT, candidate_id TEXT, status TEXT, actor TEXT, reason TEXT, snapshot_path TEXT, previous_release_id TEXT, created_at TEXT);
            CREATE TABLE IF NOT EXISTS audit(sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT, subject_id TEXT, payload_json TEXT, created_at TEXT, previous_hash TEXT, event_hash TEXT UNIQUE);
            """)

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, factory=ClosingConnection)
        db.row_factory = sqlite3.Row
        return db

    def audit(self, event_type: str, subject_id: str, payload: dict[str, Any]) -> None:
        with self.connect() as db:
            row = db.execute("SELECT event_hash FROM audit ORDER BY sequence DESC LIMIT 1").fetchone()
            previous = row[0] if row else "GENESIS"
            created = now()
            payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
            digest = hashlib.sha256(f"{previous}|{event_type}|{subject_id}|{created}|{payload_json}".encode()).hexdigest()
            db.execute("INSERT INTO audit(event_type,subject_id,payload_json,created_at,previous_hash,event_hash) VALUES(?,?,?,?,?,?)", (event_type, subject_id, payload_json, created, previous, digest))

    def start_run(self, run_id: str, project: str, baseline_score: float) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?)", (run_id, project, "running", baseline_score, None, baseline_score, now(), None, None))
        self.audit("run_started", run_id, {"project": project, "baseline_score": baseline_score})

    def add_candidate(self, item: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO candidates VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(item[key] for key in ("candidate_id","run_id","generation","parent_id","path","policy_passed","evaluation_passed","score","rationale","evidence_path","created_at")))
        self.audit("candidate_evaluated", item["candidate_id"], {"score": item["score"], "policy_passed": bool(item["policy_passed"]), "evaluation_passed": bool(item["evaluation_passed"])})

    def finish_run(self, run_id: str, status: str, champion_id: str, champion_score: float, report_path: Path) -> None:
        with self.connect() as db:
            db.execute("UPDATE runs SET status=?,champion_id=?,champion_score=?,completed_at=?,report_path=? WHERE run_id=?", (status, champion_id, champion_score, now(), str(report_path.resolve()), run_id))
        self.audit("run_completed", run_id, {"status": status, "champion_id": champion_id, "champion_score": champion_score})

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self.connect() as db:
            if run_id == "latest":
                row = db.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT 1").fetchone()
            else:
                row = db.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if row is None:
            raise ValueError(f"run not found: {run_id}")
        return dict(row)

    def get_candidate(self, candidate_id: str) -> dict[str, Any]:
        with self.connect() as db:
            row = db.execute("SELECT * FROM candidates WHERE candidate_id=?", (candidate_id,)).fetchone()
        if row is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        return dict(row)

    def add_release(self, item: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO releases VALUES(?,?,?,?,?,?,?,?,?)", tuple(item[key] for key in ("release_id","run_id","candidate_id","status","actor","reason","snapshot_path","previous_release_id","created_at")))
        self.audit("release_changed", item["release_id"], item)

    def current_release(self) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM releases WHERE status='active' ORDER BY created_at DESC LIMIT 1").fetchone()
        return dict(row) if row else None

    def deactivate(self, release_id: str, status: str = "superseded") -> None:
        with self.connect() as db:
            db.execute("UPDATE releases SET status=? WHERE release_id=?", (status, release_id))

    def verify_audit(self) -> tuple[bool, int]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM audit ORDER BY sequence").fetchall()
        previous = "GENESIS"
        for row in rows:
            material = f"{row['previous_hash']}|{row['event_type']}|{row['subject_id']}|{row['created_at']}|{row['payload_json']}".encode()
            if row["previous_hash"] != previous or hashlib.sha256(material).hexdigest() != row["event_hash"]:
                return False, int(row["sequence"])
            previous = row["event_hash"]
        return True, len(rows)
