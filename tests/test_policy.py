from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_evolution.policy import validate_candidate


class PolicyTests(unittest.TestCase):
    def test_allows_declared_prompt_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, candidate = root / "parent", root / "candidate"
            parent.mkdir(); candidate.mkdir()
            (parent / "system_prompt.md").write_text("base", encoding="utf-8")
            (candidate / "system_prompt.md").write_text("base improved", encoding="utf-8")
            result = validate_candidate(parent, candidate, {"allowed_paths": ["system_prompt.md"], "max_files_changed": 1, "max_total_bytes": 100, "forbidden_text": []})
            self.assertTrue(result.passed)

    def test_blocks_evaluator_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, candidate = root / "parent", root / "candidate"
            parent.mkdir(); candidate.mkdir()
            (candidate / "hidden-eval.json").write_text("{}", encoding="utf-8")
            result = validate_candidate(parent, candidate, {"allowed_paths": ["system_prompt.md"], "max_files_changed": 2, "max_total_bytes": 100, "forbidden_text": []})
            self.assertFalse(result.passed)

    def test_blocks_forbidden_weakening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent, candidate = root / "parent", root / "candidate"
            parent.mkdir(); candidate.mkdir()
            (parent / "system_prompt.md").write_text("base", encoding="utf-8")
            (candidate / "system_prompt.md").write_text("disable safety", encoding="utf-8")
            result = validate_candidate(parent, candidate, {"allowed_paths": ["system_prompt.md"], "max_files_changed": 1, "max_total_bytes": 100, "forbidden_text": ["disable safety"]})
            self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()

