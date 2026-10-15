"""Check SDK argument/path handling against fake SDKs, not real engines."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class SDKEntrypointTests(unittest.TestCase):
    def fixture(self, temporary, component):
        project = Path(temporary) / "project with spaces"
        (project / "tools").mkdir(parents=True)
        (project / "evidence").mkdir()
        shutil.copyfile(ROOT / component / "tools/sdk-build.sh", project / "tools/sdk-build.sh")
        (project / "evidence/source-verification.json").write_text("[]")
        (project / "tools/prepare-package.py").write_text("print('synthetic staging fixture')\n")
        sdk = Path(temporary) / "SDK with spaces"
        (sdk / "bin").mkdir(parents=True)
        cli = sdk / "bin/sfdk"
        cli.write_text("#!/usr/bin/env python3\nimport json,os,sys\n"
                       "with open(os.environ['SAILFISH_TEST_TRACE'],'a') as f:\n"
                       " f.write(json.dumps(sys.argv[1:])+'\\n')\n")
        cli.chmod(0o755)
        trace = Path(temporary) / "calls.jsonl"
        env = dict(os.environ, SAILFISH_SDK_ROOT=str(sdk),
                   SAILFISH_SDK_TARGET="Synthetic-aarch64", SAILFISH_TEST_TRACE=str(trace))
        return project, trace, env

    @unittest.skipUnless((ROOT / "sailfish-gnupg-runtime/tools/sdk-build.sh").is_file(),
                         "Requires sibling runtime checkout")
    def test_runtime_requires_explicit_target_before_sdk_execution(self):
        with tempfile.TemporaryDirectory(prefix="sailfish-sdk-entry-test-") as temporary:
            project, trace, env = self.fixture(temporary, "sailfish-gnupg-runtime")
            env.pop("SAILFISH_SDK_TARGET")
            result = subprocess.run(["bash", str(project / "tools/sdk-build.sh")],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(trace.exists())

    @unittest.skipUnless((ROOT / "sailfish-gnupg-runtime/tools/sdk-build.sh").is_file(),
                         "Requires sibling runtime checkout")
    def test_runtime_uses_explicit_sdk_and_target(self):
        with tempfile.TemporaryDirectory(prefix="sailfish-sdk-entry-test-") as temporary:
            project, trace, env = self.fixture(temporary, "sailfish-gnupg-runtime")
            subprocess.run(["bash", str(project / "tools/sdk-build.sh")],
                           env=env, check=True, capture_output=True)
            calls = [json.loads(line) for line in trace.read_text().splitlines()]
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0][-1], "build-init")
            self.assertIn("target=Synthetic-aarch64", calls[1])
            self.assertIn("no-pull-build-requires", calls[1])
            self.assertIn("rpmbuild", calls[1])
            self.assertIn("-ba", calls[1])
            self.assertIn("_sourcedir " + str(project / "sources"), calls[1])

    @unittest.skipUnless((ROOT / "sailfish-password-store/tools/sdk-build.sh").is_file(),
                         "Requires sibling password-store checkout")
    def test_pass_builds_all_four_staged_recipes_in_its_own_project(self):
        with tempfile.TemporaryDirectory(prefix="sailfish-sdk-entry-test-") as temporary:
            project, trace, env = self.fixture(temporary, "sailfish-password-store")
            subprocess.run(["bash", str(project / "tools/sdk-build.sh")],
                           env=env, check=True, capture_output=True)
            calls = [json.loads(line) for line in trace.read_text().splitlines()]
            expected = ["sailfish-pass-tree", "oath-toolkit", "sailfish-pass", "sailfish-pass-otp"]
            self.assertEqual(len(calls), len(expected) + 1)
            self.assertEqual(calls[0][-1], "build-init")
            self.assertIn("target=Synthetic-aarch64", calls[0])
            for call, recipe in zip(calls[1:], expected):
                self.assertIn("target=Synthetic-aarch64", call)
                self.assertIn("no-pull-build-requires", call)
                self.assertIn("_sourcedir " + str(project / "sources"), call)
                self.assertEqual(call[-1], str(project / "rpm" / (recipe + ".spec")))

if __name__ == "__main__":
    unittest.main()
