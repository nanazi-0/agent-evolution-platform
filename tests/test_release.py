from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agent_evolution.config import load_settings
from agent_evolution.engine import approve, rollback, run


class ReleaseTests(unittest.TestCase):
    def test_two_approvals_and_rollback_preserve_snapshots(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            shutil.copytree(source, root, ignore=shutil.ignore_patterns(".venv", ".runtime", "data", "reports", "releases", "__pycache__"))
            config = root / "configs" / "demo.toml"
            text = config.read_text(encoding="utf-8").replace("enabled = true", "enabled = false", 1)
            config.write_text(text, encoding="utf-8")
            first = run(load_settings(config))
            first_release = approve(root, first["run_id"], "test-reviewer", "verified first evidence")
            second = run(load_settings(config))
            second_release = approve(root, second["run_id"], "test-reviewer", "verified second evidence")
            self.assertEqual(second_release["previous_release_id"], first_release["release_id"])
            restored = rollback(root, "test-reviewer", "canary regression")
            self.assertEqual(restored["release_id"], first_release["release_id"])
            self.assertTrue(Path(restored["snapshot_path"]).is_dir())


if __name__ == "__main__":
    unittest.main()

