"""Source-anchor integrity tests using synthetic inputs."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/functional-analysis/scripts/verify_evidence.py"
spec = importlib.util.spec_from_file_location("verify_evidence", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / "模块.py"
        self.raw = "# 说明\r\ndef process():\r\n    return 1\r\n".encode("utf-8")
        self.path.write_bytes(self.raw)
        self.index = {"schema_version": 1, "source": {"revision": "synthetic"}, "evidence": [{
            "id": "E01", "path": "模块.py", "symbol": "process", "start_line": 2, "end_line": 3,
            "file_sha256": hashlib.sha256(self.raw).hexdigest(),
            "excerpt_sha256": hashlib.sha256("def process():\n    return 1".encode()).hexdigest(),
        }]}

    def test_unicode_crlf_and_cli(self):
        self.assertEqual(1, checker.verify(self.root, self.index))
        output = self.root / "evidence.json"
        output.write_text(json.dumps(self.index), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), "--index", str(output)], capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_stale_file_is_rejected(self):
        self.path.write_bytes(b"# shifted\n" + self.raw)
        with self.assertRaisesRegex(ValueError, "changed"):
            checker.verify(self.root, self.index)

    def test_schema_and_ranges(self):
        for key, value in [("start_line", True), ("start_line", 0), ("end_line", 1), ("end_line", 99), ("file_sha256", "bad"), ("symbol", "")]:
            index = copy.deepcopy(self.index)
            index["evidence"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                checker.verify(self.root, index)
        for index in [[], {}, {"schema_version": True}, {**self.index, "source": []}, {**self.index, "evidence": []}]:
            with self.subTest(index=index), self.assertRaises(ValueError):
                checker.verify(self.root, index)

    def test_duplicate_id_is_rejected(self):
        self.index["evidence"].append(dict(self.index["evidence"][0]))
        with self.assertRaisesRegex(ValueError, "unique"):
            checker.verify(self.root, self.index)

    def test_escape_and_ambiguous_paths(self):
        for path in ["../secret", "/etc/passwd", "C:/secret", "a\\b", "a//b", "./模块.py"]:
            self.index["evidence"][0]["path"] = path
            with self.subTest(path=path), self.assertRaises(ValueError):
                checker.verify(self.root, self.index)

    def test_excerpt_mismatch_is_rejected(self):
        self.index["evidence"][0]["excerpt_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "excerpt"):
            checker.verify(self.root, self.index)


if __name__ == "__main__":
    unittest.main()
