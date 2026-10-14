"""Check input classification without SDK execution or real source material."""
import hashlib
import json
import subprocess
import sys
import importlib.util
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "tools/sdk-preflight.py"
SPEC = importlib.util.spec_from_file_location("sdk_preflight", FILE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class InputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sailfish-preflight-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "sources").mkdir()

    def test_digest_matches_then_detects_corruption(self):
        path = self.root / "sources/fixture.tar"
        path.write_bytes(b"synthetic public source")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(MODULE.inspect_file(self.root, "sources/fixture.tar", sha)["status"],
                         "sha256_matches")
        path.write_bytes(b"changed synthetic public source")
        self.assertEqual(MODULE.inspect_file(self.root, "sources/fixture.tar", sha)["status"],
                         "sha256_mismatch")

    def test_missing_verification_is_reported_without_creating_it(self):
        self.assertEqual(MODULE.inspect_file(self.root, "evidence/verification.json")["status"],
                         "missing")
        self.assertFalse((self.root / "evidence").exists())

    def test_present_record_is_not_reported_as_authenticated(self):
        (self.root / "record.json").write_text("{}")
        self.assertEqual(MODULE.inspect_file(self.root, "record.json")["status"],
                         "present_unverified")

    def test_sdk_path_check_never_executes_the_sdk(self):
        project = self.root / "sailfish-gnupg-runtime"
        (project / "sources").mkdir(parents=True)
        (project / "evidence").mkdir()
        archive = b"synthetic public archive"
        name = "sources/synthetic-1.0.tar.bz2"
        (project / name).write_bytes(archive)
        (project / (name + ".sig")).write_text("synthetic signature placeholder")
        (project / "sources/signature_key.asc").write_text("synthetic public key placeholder")
        (project / "evidence/source-verification.json").write_text("{}")
        (project / "sources.lock.json").write_text(json.dumps({"sources": [
            {"name": "synthetic", "version": "1.0",
             "sha256": hashlib.sha256(archive).hexdigest()}]}))
        sdk = self.root / "SDK"
        (sdk / "bin").mkdir(parents=True)
        marker = self.root / "sdk-was-executed"
        cli = sdk / "bin/sfdk"
        cli.write_text("#!/bin/sh\ntouch " + str(marker) + "\n")
        cli.chmod(0o755)
        result = subprocess.run([sys.executable, str(FILE), "--root", str(self.root),
                                 "--component", "runtime", "--sdk-root", str(sdk),
                                 "--target", "Synthetic-aarch64", "--json"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["sdk_cli"], "present_not_executed")
        self.assertEqual(report["signature_authentication"], "not_performed")
        self.assertEqual(report["target_installation"], "not_verified")
        self.assertFalse(marker.exists())

    def test_source_directory_symlink_is_refused(self):
        (self.root / "other").mkdir()
        (self.root / "other/file").write_text("synthetic fixture")
        (self.root / "linked-sources").symlink_to(self.root / "other", target_is_directory=True)
        self.assertEqual(MODULE.inspect_file(self.root, "linked-sources/file")["status"],
                         "symlink_refused")

if __name__ == "__main__":
    unittest.main()
