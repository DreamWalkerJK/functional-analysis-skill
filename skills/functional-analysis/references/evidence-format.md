# Optional evidence index

Ordinary source citations remain sufficient. For reproducible local source anchors, write a UTF-8 JSON index and verify it using:

```sh
python <skill-directory>/scripts/verify_evidence.py --root <source-root> --index <evidence.json>
```

The root is supplied at execution time, so the index can travel between users without embedding a personal home directory. Paths use forward slashes relative to the root. Parent traversal, absolute paths, drive paths, symbolic links and Windows reparse points are rejected. Use a real source root rather than a symlink alias; on macOS, resolve a `/var` alias to `/private/var` before invoking the checker.

```json
{
  "schema_version": 1,
  "source": {
    "revision": "<commit or document version>",
    "working_tree": "<relevant changes or status snapshot reference>",
    "analyzed_on": "YYYY-MM-DD"
  },
  "evidence": [
    {
      "id": "E01",
      "path": "src/processor.py",
      "symbol": "process",
      "start_line": 10,
      "end_line": 24,
      "file_sha256": "<64 lowercase hexadecimal characters>",
      "excerpt_sha256": "<64 lowercase hexadecimal characters>"
    }
  ]
}
```

Every evidence ID is unique. Line spans are one-based and inclusive. File hashes cover raw bytes. Excerpt hashes use UTF-8 decoding (a BOM remains a character), `splitlines()`, the selected line span, then `"\n".join(...)` encoded as UTF-8 without an extra final newline. These rules are independent of CRLF/LF line endings for the excerpt; a line-ending change still changes the whole-file hash.

Capture a verified range after reading the source, for example:

```python
from pathlib import Path
import hashlib

root = Path("<source-root>").resolve()
relative, start, end = "src/processor.py", 10, 24
raw = (root / relative).read_bytes()
lines = raw.decode("utf-8").splitlines()
assert 1 <= start <= end <= len(lines)
anchor = {
    "id": "E01", "path": relative, "symbol": "process",
    "start_line": start, "end_line": end,
    "file_sha256": hashlib.sha256(raw).hexdigest(),
    "excerpt_sha256": hashlib.sha256("\n".join(lines[start-1:end]).encode("utf-8")).hexdigest(),
}
```

Store the resulting anchor in the `evidence` list and retain a human-readable index in the document. Link prose to its evidence IDs. Multiple roots need separate indices; each source revision belongs to its own root.

Exit code 0 means all listed anchors match the current files. Exit code 1 means an invalid index or a mismatched/unavailable source anchor. This does not verify that the claim follows from those lines, that all dependencies were inspected, that the recorded revision is checked out, or that the application runs correctly. Check the baseline and semantic interpretation separately. The index should contain source locations and hashes, not secrets or copied private source.
