"""Offline behavioral checks using disposable synthetic Git repositories."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]

class CheckoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sailfish-workspace-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.remote = self.root / "synthetic-origin"
        self.remote.mkdir()
        self.git(self.remote, "init", "--initial-branch=main")
        (self.remote / "fixture.txt").write_text("synthetic fixture\n")
        self.git(self.remote, "add", "fixture.txt")
        self.git(self.remote, "-c", "user.name=Test", "-c",
                 "user.email=test@example.invalid", "-c", "commit.gpgsign=false",
                 "commit", "-m", "Synthetic public fixture")
        self.pin = self.git(self.remote, "rev-parse", "HEAD")
        self.workspace = self.root / "tools-repository"
        (self.workspace / "tools").mkdir(parents=True)
        shutil.copyfile(SOURCE / "tools/workspace.py", self.workspace / "tools/workspace.py")
        self.projects = [
            {"name": "component", "remote": str(self.remote), "branch": "main"},
            {"name": "source-fork", "remote": str(self.remote), "branch": "main",
             "commit": self.pin, "upstream": "https://github.com/example/upstream.git"}]
        (self.workspace / "manifest.yml").write_text(json.dumps({"projects": self.projects}))
        self.destination = self.root / "checkouts"

    def git(self, path, *args):
        return subprocess.check_output(["git", "-C", str(path), *args],
                                       text=True, stderr=subprocess.DEVNULL).strip()

    def run_helper(self, *args):
        return subprocess.run([sys.executable, str(self.workspace / "tools/workspace.py"),
                               *args, "--root", str(self.destination)],
                              capture_output=True, text=True)

    def test_clone_pin_and_upstream(self):
        result = self.run_helper("clone")
        self.assertEqual(result.returncode, 0, result.stderr)
        fork = self.destination / "source-fork"
        self.assertEqual(self.git(fork, "rev-parse", "HEAD"), self.pin)
        self.assertEqual(self.git(fork, "branch", "--show-current"), "")
        self.assertEqual(self.git(fork, "remote", "get-url", "upstream"),
                         self.projects[1]["upstream"])

    def test_repeated_clone_preserves_dirty_work_and_branch(self):
        self.assertEqual(self.run_helper("clone").returncode, 0)
        component = self.destination / "component"
        self.git(component, "switch", "-c", "my-work")
        (component / "fixture.txt").write_text("uncommitted synthetic work\n")
        (component / "new.txt").write_text("untracked synthetic work\n")
        before = self.git(component, "status", "--porcelain")
        result = self.run_helper("clone")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git(component, "branch", "--show-current"), "my-work")
        self.assertEqual(self.git(component, "status", "--porcelain"), before)
        self.assertEqual((component / "fixture.txt").read_text(), "uncommitted synthetic work\n")

    def test_dry_run_creates_nothing(self):
        result = self.run_helper("clone", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.destination.exists())

    def test_wrong_origin_stops_before_other_clone(self):
        self.destination.mkdir()
        component = self.destination / "component"
        subprocess.run(["git", "clone", str(self.remote), str(component)],
                       check=True, capture_output=True)
        self.git(component, "remote", "set-url", "origin", "https://github.com/example/wrong.git")
        result = self.run_helper("clone")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unexpected origin", result.stderr)
        self.assertFalse((self.destination / "source-fork").exists())

    def test_symlink_stops_before_clone(self):
        self.destination.mkdir()
        (self.destination / "component").symlink_to(self.remote, target_is_directory=True)
        result = self.run_helper("clone")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stderr)
        self.assertFalse((self.destination / "source-fork").exists())

if __name__ == "__main__":
    unittest.main()
