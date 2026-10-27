from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_evolution.store import Store


class StoreTests(unittest.TestCase):
    def test_audit_chain_detects_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory))
            store.audit("test", "one", {"value": 1})
            self.assertEqual(store.verify_audit(), (True, 1))
            with store.connect() as db:
                db.execute("UPDATE audit SET payload_json='{}' WHERE sequence=1")
            self.assertEqual(store.verify_audit(), (False, 1))


if __name__ == "__main__":
    unittest.main()

