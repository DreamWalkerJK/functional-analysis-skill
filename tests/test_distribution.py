"""Behavioral tests for installation isolation and committed release content."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).absolute().parents[1]


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load_script("install")
packager = load_script("package_release")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="功能说明-install-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source"
        (self.source / "references").mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: functional-analysis\n---\n分析\n", encoding="utf-8")
        (self.source / "references" / "guide.md").write_text("Evidence\n", encoding="utf-8")
        self.target = self.base / "用户" / "skills" / installer.NAME

    def make_link(self, link: Path, target: Path):
        try:
            link.symlink_to(target, target_is_directory=target.is_dir())
        except OSError as exc:
            self.skipTest(f"Symbolic links unavailable: {exc}")

    def test_preview_has_no_side_effects(self):
        self.assertIn("Preview", installer.install(self.source, self.target))
        self.assertFalse(self.target.parent.exists())

    def test_install_and_repeat_preserve_content_and_mtimes(self):
        self.assertIn("Installed and verified", installer.install(self.source, self.target, True))
        self.assertEqual(installer.manifest(self.source), installer.manifest(self.target))
        before = {p: p.stat().st_mtime_ns for p in self.target.rglob("*")}
        self.assertIn("Already installed", installer.install(self.source, self.target, True))
        self.assertEqual(before, {p: p.stat().st_mtime_ns for p in self.target.rglob("*")})

    def test_python_caches_do_not_enter_or_conflict_with_installation(self):
        cache = self.source / "__pycache__"
        cache.mkdir()
        (cache / "local.pyc").write_bytes(b"generated")
        (self.source / "local.pyo").write_bytes(b"generated")
        installer.install(self.source, self.target, True)
        self.assertFalse((self.target / "__pycache__").exists())
        self.assertFalse((self.target / "local.pyo").exists())
        target_cache = self.target / "__pycache__"
        target_cache.mkdir()
        (target_cache / "local.pyc").write_bytes(b"runtime-generated")
        self.assertIn("Already installed", installer.install(self.source, self.target, True))
        self.assertEqual(b"runtime-generated", (target_cache / "local.pyc").read_bytes())

    def test_modified_installation_is_preserved(self):
        installer.install(self.source, self.target, True)
        local = self.target / "SKILL.md"
        local.write_text("local edit", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "conflict"):
            installer.install(self.source, self.target, True)
        self.assertEqual("local edit", local.read_text(encoding="utf-8"))

    def test_extra_user_file_is_preserved(self):
        installer.install(self.source, self.target, True)
        local = self.target / "notes.txt"
        local.write_text("private", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "conflict"):
            installer.install(self.source, self.target, True)
        self.assertEqual("private", local.read_text(encoding="utf-8"))

    def test_empty_existing_directory_is_not_claimed(self):
        self.target.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, "conflict"):
            installer.install(self.source, self.target, True)
        self.assertEqual([], list(self.target.iterdir()))

    def test_source_requires_skill_file(self):
        (self.source / "SKILL.md").unlink()
        with self.assertRaisesRegex(ValueError, "SKILL.md"):
            installer.install(self.source, self.target, True)
        self.assertFalse(self.target.exists())

    def test_reject_overlapping_paths(self):
        for target in (self.source, self.source / "nested", self.base):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "overlap"):
                installer.install(self.source, target, True)

    def test_reject_dot_segment_overlap(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            installer.install(self.source, self.base / "x" / ".." / "source", True)

    def test_reject_source_link(self):
        link = self.source / "linked"
        self.make_link(link, self.base)
        with self.assertRaisesRegex(ValueError, "links"):
            installer.install(self.source, self.target, True)
        self.assertFalse(self.target.exists())

    def test_reject_destination_ancestor_link(self):
        external = self.base / "external"
        external.mkdir()
        self.make_link(self.target.parents[1], external)
        with self.assertRaisesRegex(ValueError, "links"):
            installer.install(self.source, self.target, True)
        self.assertEqual([], list(external.iterdir()))

    def test_failed_move_cleans_only_new_installation(self):
        self.target.parent.mkdir(parents=True)
        neighbor = self.target.parent / "other-skill"
        neighbor.mkdir()
        (neighbor / "SKILL.md").write_text("keep", encoding="utf-8")
        actual_rename = os.rename
        attempts = 0

        def fail_second(source, target):
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                raise OSError("simulated disk failure")
            return actual_rename(source, target)

        with mock.patch.object(installer.os, "rename", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "simulated"):
                installer.install(self.source, self.target, True)
        self.assertFalse(self.target.exists())
        self.assertEqual("keep", (neighbor / "SKILL.md").read_text(encoding="utf-8"))
        self.assertFalse(list(self.target.parent.glob(".functional-analysis-stage-*")))

    def test_cli_unicode_paths(self):
        command = [sys.executable, str(ROOT / "scripts" / "install.py"), "--source", str(self.source), "--dest", str(self.target.parent)]
        preview = subprocess.run(command, capture_output=True)
        self.assertEqual(0, preview.returncode, preview.stderr)
        self.assertFalse(self.target.exists())
        applied = subprocess.run(command + ["--apply"], capture_output=True)
        self.assertEqual(0, applied.returncode, applied.stderr)
        self.assertEqual(installer.manifest(self.source), installer.manifest(self.target))

    def test_destination_maps_user_and_project(self):
        with mock.patch.object(installer.Path, "home", return_value=self.base):
            for agent, directory in (("codex", ".agents"), ("generic", ".agents"), ("claude", ".claude")):
                self.assertEqual(self.base / directory / "skills" / installer.NAME,
                                 installer.destination(agent, "user", None, None))
                self.assertEqual(self.base / directory / "skills" / installer.NAME,
                                 installer.destination(agent, "project", self.base, None))
        self.assertEqual(self.target, installer.destination("generic", "user", None, self.target.parent))

    def test_project_scope_requires_explicit_existing_root(self):
        for project in (None, self.base / "missing"):
            with self.assertRaises(ValueError):
                installer.destination("codex", "project", project, None)
        with self.assertRaises(ValueError):
            installer.destination("codex", "user", self.base, None)
        with self.assertRaises(ValueError):
            installer.destination("codex", "project", self.base, self.base)

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_reject_windows_junction(self):
        external = self.base / "external"
        external.mkdir()
        junction = self.source / "junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(external)], capture_output=True)
        if result.returncode:
            self.skipTest(f"Cannot create junction: {result.stderr!r}")
        self.addCleanup(junction.rmdir)
        with self.assertRaisesRegex(ValueError, "reparse"):
            installer.install(self.source, self.target, True)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="功能说明-release-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "repo"
        self.root.mkdir()
        self.output = self.base / "release"
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Distribution Test")
        self.git("config", "user.email", "distribution@example.invalid")
        source = self.root / "skills" / installer.NAME
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("技能\n", encoding="utf-8")
        (source / "references").mkdir()
        (source / "references" / "guide.md").write_text("evidence\n", encoding="utf-8")
        (self.root / "LICENSE").write_text("Test license\n", encoding="utf-8")
        (self.root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("private-local.txt\n", encoding="utf-8")
        self.commit()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.STDOUT)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-m", "test(distribution): add fixture")

    def test_archives_match_commit_and_exclude_ignored_private_files(self):
        (self.root / "private-local.txt").write_text("Do not publish", encoding="utf-8")
        skill_zip, source_zip, checksum = packager.package(self.root, self.output)
        with zipfile.ZipFile(skill_zip) as archive:
            self.assertEqual({"functional-analysis/SKILL.md", "functional-analysis/references/guide.md", "functional-analysis/LICENSE"}, set(archive.namelist()))
            self.assertEqual(self.git("show", "HEAD:skills/functional-analysis/SKILL.md"), archive.read("functional-analysis/SKILL.md"))
        with zipfile.ZipFile(source_zip) as archive:
            self.assertFalse(any("private-local" in name for name in archive.namelist()))
            self.assertFalse(any("/.git/" in name for name in archive.namelist()))
            for name in archive.namelist():
                if not name.endswith("/"):
                    relative = name.removeprefix("functional-analysis-skill-0.1.0/")
                    self.assertEqual(self.git("show", f"HEAD:{relative}"), archive.read(name))
        for line in checksum.read_text(encoding="utf-8").splitlines():
            expected, filename = line.split("  ", 1)
            self.assertEqual(hashlib.sha256((self.output / filename).read_bytes()).hexdigest(), expected)

    def test_dirty_tracked_content_is_not_packaged(self):
        (self.root / "LICENSE").write_text("uncommitted", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Commit"):
            packager.package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_untracked_content_requires_review(self):
        (self.root / "accidental.txt").write_text("untracked", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Commit"):
            packager.package(self.root, self.output)

    def test_invalid_version_rejected(self):
        (self.root / "VERSION").write_text("../invalid\n", encoding="utf-8")
        self.commit()
        with self.assertRaisesRegex(ValueError, "VERSION"):
            packager.package(self.root, self.output)

    def test_tracked_symbolic_link_rejected_without_dereferencing(self):
        blob = subprocess.check_output(["git", "hash-object", "-w", "--stdin"],
                                       cwd=self.root, input=b"../../../private\n").decode().strip()
        self.git("update-index", "--add", "--cacheinfo", "120000", blob, "skills/functional-analysis/escape")
        self.git("config", "core.symlinks", "false")
        self.git("checkout", "--", "skills/functional-analysis/escape")
        self.git("commit", "-m", "test(distribution): add symlink fixture")
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            packager.package(self.root, self.output)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
