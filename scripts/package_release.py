#!/usr/bin/env python3
"""Build a standalone skill archive and committed source archive with SHA-256."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).absolute().parents[1]
NAME = "functional-analysis"
PROJECT = "functional-analysis-skill"
SKILL_PREFIX = f"skills/{NAME}/"


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root)


def package(root: Path, output: Path | None = None) -> list[Path]:
    if git(root, "status", "--porcelain", "--untracked-files=normal").strip():
        raise ValueError("Commit all source changes before packaging.")
    version = git(root, "show", "HEAD:VERSION").decode("utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("VERSION must use numeric major.minor.patch format.")
    # Reject tracked symbolic links: git archive can preserve links that a ZIP
    # consumer later expands outside the intended skill directory.
    tree = [record for record in git(root, "ls-tree", "-r", "-z", "HEAD").split(b"\0") if record]
    for record in tree:
        if record.startswith(b"120000 "):
            raise ValueError("Tracked symbolic links are not supported in release archives.")
        if record.startswith(b"160000 "):
            raise ValueError("Submodules must be vendored or excluded before release packaging.")
    required = ("LICENSE", f"{SKILL_PREFIX}SKILL.md")
    for entry in required:
        git(root, "cat-file", "-e", f"HEAD:{entry}")
    output = output or root / "dist"
    output.mkdir(parents=True, exist_ok=True)
    source_zip = output / f"{PROJECT}-{version}-source.zip"
    prefix = f"{PROJECT}-{version}/"
    timestamp = int(git(root, "show", "-s", "--format=%ct", "HEAD").strip())
    moment = datetime.fromtimestamp(max(timestamp, 315532800), timezone.utc)
    archive_time = (moment.year, moment.month, moment.day, moment.hour, moment.minute, moment.second)
    # Read committed blobs directly. git archive may apply eol/export attributes,
    # which can change bytes depending on the publishing machine's Git config.
    with zipfile.ZipFile(source_zip, "w", zipfile.ZIP_DEFLATED) as archive:
        for record in tree:
            metadata, encoded_path = record.split(b"\t", 1)
            mode, kind, object_id = metadata.split()
            if kind != b"blob":
                raise ValueError("Only ordinary tracked files are supported.")
            path = encoded_path.decode("utf-8")
            info = zipfile.ZipInfo(prefix + path, archive_time)
            info.create_system = 3
            info.external_attr = int(mode, 8) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, git(root, "cat-file", "blob", object_id.decode("ascii")))
    skill_zip = output / f"{NAME}-{version}.zip"
    with zipfile.ZipFile(source_zip) as source, zipfile.ZipFile(skill_zip, "w", zipfile.ZIP_DEFLATED) as skill:
        written: dict[str, bytes] = {}
        for entry in source.infolist():
            relative = entry.filename.removeprefix(prefix)
            if entry.is_dir():
                continue
            if relative.startswith(SKILL_PREFIX):
                target = f"{NAME}/" + relative.removeprefix(SKILL_PREFIX)
            elif relative == "LICENSE":
                target = f"{NAME}/LICENSE"
            else:
                continue
            payload = source.read(entry)
            if target in written:
                if written[target] != payload:
                    raise ValueError(f"Conflicting release file: {target}")
                continue
            written[target] = payload
            copied = zipfile.ZipInfo(target, entry.date_time)
            copied.compress_type = zipfile.ZIP_DEFLATED
            copied.external_attr = entry.external_attr
            skill.writestr(copied, payload)
    checksum = output / f"{PROJECT}-{version}-SHA256SUMS.txt"
    checksum.write_text("".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
        for path in (skill_zip, source_zip)
    ), encoding="utf-8", newline="\n")
    return [skill_zip, source_zip, checksum]


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Output directory (defaults to dist/)")
    args = parser.parse_args()
    try:
        for path in package(ROOT, args.output):
            print(path)
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
