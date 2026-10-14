#!/usr/bin/env python3
"""Verify RPM patches against pinned fork trees, or export them from fork commits."""
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

workspace = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--root", type=Path, default=workspace.parent)
parser.add_argument("--export", action="store_true",
                    help="Regenerate patch snapshots from the pinned fork commits")
args = parser.parse_args()
root = args.root.resolve()

def git(checkout, *argv, data=None, env=None):
    return subprocess.check_output(["git", "-C", str(checkout), *argv],
                                   input=data, env=env)

maps = json.loads((workspace / "docs/development/upstream-forks.json").read_text())
configuration = json.loads((workspace / "tools/packaging-patches.json").read_text())
pending = []
for config in configuration:
    source = next(s for s in maps["source_forks"]
                  if s["fork"].rsplit("/", 1)[1] == config["fork"])
    checkout = root / config["fork"]
    base, head = source["upstream_commit"], source["commit"]
    package = root / config["package"]
    manifest = json.loads((workspace / "manifest.yml").read_text())
    fork_entry = next(p for p in manifest["projects"] if p["name"] == config["fork"])
    if fork_entry["commit"] != head:
        raise SystemExit("Manifest/source-map pin mismatch: " + config["fork"])
    if config["fork"] == "sailfish-secrets":
        lock = json.loads((package / "integrations/native-pinentry/sources.json").read_text())
        locked_base = lock["upstream_commit"]
        locked_head = lock["fork_variants"]["compat"]["commit"]
    else:
        lock = json.loads((package / "sources.lock.json").read_text())
        component = "pass" if config["fork"] == "sailfish-pass" else "pass_otp"
        locked_base = lock[component]["downstream_fork"]["base_commit"]
        locked_head = lock[component]["downstream_fork"]["commit"]
    if (locked_base, locked_head) != (base, head):
        raise SystemExit("Package/source-map pin mismatch: " + config["fork"])
    git(checkout, "merge-base", "--is-ancestor", base, head)
    commits = git(checkout, "rev-list", "--reverse", base + ".." + head).decode().splitlines()
    if len(commits) != len(config["patches"]):
        raise SystemExit("Commit/patch count mismatch: " + config["fork"])
    patches = []
    for commit, relative in zip(commits, config["patches"]):
        path = root / config["package"] / relative
        if path.is_symlink() or not path.resolve().is_relative_to((root / config["package"]).resolve()):
            raise SystemExit("Unsafe patch path: " + str(path))
        if args.export:
            data = git(checkout, "format-patch", "--stdout", "--no-signature",
                       "--no-stat", "--zero-commit", "--no-numbered", "-1", commit)
            pending.append((path, data))
        else:
            data = path.read_bytes()
        patches.append(data)
    # A private index/object directory keeps source checkouts intact.
    object_path = git(checkout, "rev-parse", "--git-path", "objects").decode().strip()
    objects = (checkout / object_path).resolve()
    with tempfile.TemporaryDirectory(prefix="sailfish-patch-check-") as temporary:
        temp = Path(temporary)
        (temp / "objects").mkdir()
        env = dict(os.environ, GIT_INDEX_FILE=str(temp / "index"),
                   GIT_OBJECT_DIRECTORY=str(temp / "objects"),
                   GIT_ALTERNATE_OBJECT_DIRECTORIES=str(objects))
        git(checkout, "read-tree", base, env=env)
        for data in patches:
            git(checkout, "apply", "--cached", "--whitespace=nowarn", "-", data=data, env=env)
        actual = git(checkout, "write-tree", env=env).strip()
        expected = git(checkout, "rev-parse", head + "^{tree}").strip()
        if actual != expected:
            raise SystemExit("Packaged source tree differs from fork: " + config["fork"])
    print("PASS complete patched tree matches " + config["fork"] + "@" + head)
# Validate every proposed export before replacing any packaging snapshot.
for path, data in pending:
    path.write_bytes(data)
if pending:
    print("Exported", len(pending), "patch snapshots; source pins and RPM recipes unchanged")
