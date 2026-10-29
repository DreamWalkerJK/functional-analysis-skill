#!/usr/bin/env python3
"""Install the portable skill without overwriting an existing installation."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

NAME = "functional-analysis"
ROOT = Path(__file__).absolute().parents[1]


def absolute(path: Path) -> Path:
    """Normalize dot segments without concealing symbolic links."""
    return Path(os.path.abspath(path.expanduser()))


def reject_links(path: Path) -> None:
    """Reject symlinks and Windows reparse points in every existing component."""
    path = absolute(path)
    for component in (*reversed(path.parents), path):
        try:
            info = component.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symbolic links and reparse points are not supported: {component}")


def manifest(folder: Path) -> dict[str, str]:
    reject_links(folder)
    if not folder.is_dir():
        raise ValueError(f"Expected a directory: {folder}")
    result: dict[str, str] = {}
    for parent, directories, files in os.walk(folder, followlinks=False):
        for name in directories + files:
            child = Path(parent) / name
            reject_links(child)
            if child.is_file():
                result[child.relative_to(folder).as_posix()] = hashlib.sha256(child.read_bytes()).hexdigest()
            elif not child.is_dir():
                raise ValueError(f"Unsupported filesystem entry: {child}")
    return result


def destination(agent: str, scope: str, project: Path | None, dest: Path | None) -> Path:
    if dest is not None:
        if project is not None or scope != "user":
            raise ValueError("Use --dest alone; it selects the parent skills directory.")
        return absolute(dest) / NAME
    if scope == "project":
        if project is None:
            raise ValueError("--project is required when --scope project is selected.")
        base = absolute(project)
        reject_links(base)
        if not base.is_dir():
            raise ValueError(f"Project directory does not exist: {base}")
    else:
        if project is not None:
            raise ValueError("--project requires --scope project.")
        base = Path.home()
    return absolute(base / (".claude" if agent == "claude" else ".agents") / "skills" / NAME)


def install(source: Path, target: Path, apply: bool = False) -> str:
    source, target = absolute(source), absolute(target)
    reject_links(source)
    reject_links(target)
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and installation paths must not overlap.")
    expected = manifest(source)
    if "SKILL.md" not in expected:
        raise ValueError(f"Source does not contain SKILL.md: {source}")
    if target.exists():
        if manifest(target) == expected:
            return f"Already installed; files are identical: {target}"
        raise ValueError(f"Installation conflict; existing files were preserved: {target}")
    if not apply:
        return f"Preview: install {len(expected)} files into {target}\nUse --apply to perform this installation."
    target.parent.mkdir(parents=True, exist_ok=True)
    reject_links(target.parent)
    # Stage on the destination volume, verify the copy, then reserve the target
    # with mkdir(exist_ok=False). A concurrent install can never be replaced.
    with tempfile.TemporaryDirectory(prefix=f".{NAME}-stage-", dir=target.parent) as temporary:
        staged = Path(temporary) / NAME
        shutil.copytree(source, staged)
        if manifest(staged) != expected:
            raise ValueError("Source changed during installation; no installation was created.")
        reject_links(target)
        target.mkdir(exist_ok=False)
        try:
            for child in staged.iterdir():
                os.rename(child, target / child.name)
            if manifest(target) != expected:
                raise ValueError("Installed file verification failed.")
        except BaseException:
            # This directory was created exclusively by this invocation.
            reject_links(target)
            shutil.rmtree(target)
            raise
    return f"Installed and verified {len(expected)} files: {target}"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "claude", "generic"), default="generic")
    parser.add_argument("--scope", choices=("user", "project"), default="user")
    parser.add_argument("--project", type=Path, help="Existing project root (required for project scope)")
    parser.add_argument("--dest", type=Path, help="Custom parent skills directory; the skill name is appended")
    parser.add_argument("--source", type=Path, default=ROOT / "skills" / NAME, help="Source skill directory")
    parser.add_argument("--apply", action="store_true", help="Apply the previewed installation")
    args = parser.parse_args()
    try:
        print(install(args.source, destination(args.agent, args.scope, args.project, args.dest), args.apply))
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
