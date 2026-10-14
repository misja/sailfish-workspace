#!/usr/bin/env python3
"""Clone or inspect the Sailfish repositories. Requires Python 3 and Git."""
import argparse
import json
import re
import subprocess
from pathlib import Path

workspace = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("command", choices=("status", "clone"))
parser.add_argument("--root", type=Path, default=workspace.parent)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()
root = args.root.expanduser().resolve()
projects = json.loads((workspace / "manifest.yml").read_text())["projects"]

def git(path, *argv):
    return subprocess.check_output(["git", "-C", str(path), *argv], text=True).strip()

def canonical(url):
    value = url.rstrip("/").removesuffix(".git")
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value[len("git@github.com:"):]
    return value

# Preflight every existing path before any clone or remote change.
for project in projects:
    name = project["name"]
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise SystemExit("Invalid repository directory: " + name)
    path = root / name
    if path.is_symlink():
        raise SystemExit("Refusing repository symlink: " + str(path))
    if path.exists():
        if git(path, "rev-parse", "--show-toplevel") != str(path):
            raise SystemExit("Expected a repository root: " + str(path))
        if canonical(git(path, "remote", "get-url", "origin")) != canonical(project["remote"]):
            raise SystemExit("Unexpected origin: " + str(path))
        if "upstream" in project and "upstream" in git(path, "remote").splitlines():
            if canonical(git(path, "remote", "get-url", "upstream")) != canonical(project["upstream"]):
                raise SystemExit("Unexpected upstream: " + str(path))

for project in projects:
    path = root / project["name"]
    if not path.exists():
        if args.command == "status" or args.dry_run:
            print(project["name"] + ": missing; clone branch " + project["branch"])
            continue
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--branch", project["branch"], "--",
                        project["remote"], str(path)], check=True)
        if "commit" in project:
            subprocess.run(["git", "-C", str(path), "checkout", "--detach",
                            project["commit"]], check=True)
    if args.command == "clone" and "upstream" in project:
        if "upstream" not in git(path, "remote").splitlines():
            if args.dry_run:
                print(project["name"] + ": would add upstream remote")
            else:
                subprocess.run(["git", "-C", str(path), "remote", "add",
                                "upstream", project["upstream"]], check=True)
    head = git(path, "rev-parse", "HEAD")
    branch = git(path, "branch", "--show-current") or "(detached)"
    dirty = bool(git(path, "status", "--porcelain", "--untracked-files=normal"))
    pin = project.get("commit")
    state = "pin matches" if pin == head else ("DIFFERS FROM PIN" if pin else "branch checkout")
    print(f"{project['name']}: {branch} {head[:12]}; {state}; " +
          ("uncommitted changes" if dirty else "clean"))
