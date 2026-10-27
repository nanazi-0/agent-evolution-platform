from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agent_evolution.config import load_settings
from agent_evolution.engine import run


class EngineTests(unittest.TestCase):
    def test_demo_reaches_eligible_without_auto_approval(self) -> None:
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project"
            shutil.copytree(source, root, ignore=shutil.ignore_patterns(".venv", ".runtime", "data", "reports", "releases", "__pycache__"))
            config = root / "configs" / "demo.toml"
            text = config.read_text(encoding="utf-8").replace("enabled = true", "enabled = false", 1)
            config.write_text(text, encoding="utf-8")
            result = run(load_settings(config))
            self.assertEqual(result["status"], "eligible")
            self.assertEqual(result["champion_score"], 1.0)
            self.assertFalse((root / "releases" / "current.json").exists())


if __name__ == "__main__":
    unittest.main()

