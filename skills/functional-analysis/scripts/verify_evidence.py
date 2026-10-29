#!/usr/bin/env python3
"""Verify local source anchors; this does not verify prose or runtime behavior."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import sys


def reject_links(path: Path) -> None:
    for part in (*reversed(path.parents), path):
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symbolic link or reparse point is not supported: {part}")


def verify(root: Path, index: dict) -> int:
    root = Path(os.path.abspath(root.expanduser()))
    reject_links(root)
    if not root.is_dir():
        raise ValueError("Source root must be an existing directory")
    if not isinstance(index, dict) or type(index.get("schema_version")) is not int or index["schema_version"] != 1:
        raise ValueError("Expected schema_version 1")
    if not isinstance(index.get("source"), dict):
        raise ValueError("source must be an object recording the analysis baseline")
    items = index.get("evidence")
    if not isinstance(items, list) or not items:
        raise ValueError("evidence must be a nonempty list")
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each evidence item must be an object")
        identifier = item.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"E[0-9]+", identifier) or identifier in seen:
            raise ValueError("Evidence IDs must be unique E<number> strings")
        seen.add(identifier)
        path = item.get("path")
        if not isinstance(path, str) or not path or "\\" in path or ":" in path:
            raise ValueError(f"{identifier}: expected a relative POSIX path")
        parts = path.split("/")
        if any(p in ("", ".", "..") for p in parts) or PurePosixPath(path).is_absolute() or PureWindowsPath(path).drive:
            raise ValueError(f"{identifier}: invalid relative path")
        target = root.joinpath(*parts)
        reject_links(target)
        if not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"{identifier}: file is outside the source root")
        if not isinstance(item.get("symbol"), str) or not item["symbol"].strip():
            raise ValueError(f"{identifier}: symbol must be a nonempty string")
        start, end = item.get("start_line"), item.get("end_line")
        if type(start) is not int or type(end) is not int or start < 1 or end < start:
            raise ValueError(f"{identifier}: invalid inclusive line range")
        for key in ("file_sha256", "excerpt_sha256"):
            if not isinstance(item.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", item[key]):
                raise ValueError(f"{identifier}: invalid {key}")
        raw = target.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["file_sha256"]:
            raise ValueError(f"{identifier}: source file changed: {path}")
        lines = raw.decode("utf-8").splitlines()
        if end > len(lines):
            raise ValueError(f"{identifier}: line range exceeds the file")
        excerpt = "\n".join(lines[start - 1:end]).encode("utf-8")
        if hashlib.sha256(excerpt).hexdigest() != item["excerpt_sha256"]:
            raise ValueError(f"{identifier}: excerpt hash does not match")
    return len(items)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--index", required=True, type=Path)
    args = parser.parse_args()
    try:
        count = verify(args.root, json.loads(args.index.read_text(encoding="utf-8")))
        print(f"Verified {count} source anchors. Integrity only; semantics and runtime behavior were not tested.")
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
