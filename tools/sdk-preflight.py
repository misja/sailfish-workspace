#!/usr/bin/env python3
"""Read-only inventory of known public build inputs; does not run SDK tools."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]

def inspect_file(project, relative, digest=None):
    path = project / relative
    result = {"path": relative}
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        return dict(result, status="unsafe_path")
    if any(p.is_symlink() for p in [path, *path.parents] if p != project.parent):
        return dict(result, status="symlink_refused")
    if not path.is_file():
        return dict(result, status="missing")
    if digest is None:
        return dict(result, status="present_unverified")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        return dict(result, status="invalid_digest_pin")
    try:
        sha = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                sha.update(chunk)
    except OSError:
        return dict(result, status="unreadable")
    return dict(result, status="sha256_matches" if sha.hexdigest() == digest
                else "sha256_mismatch")

def inspect_component(root, component):
    name = "sailfish-gnupg-runtime" if component == "runtime" else "sailfish-password-store"
    project = root / name
    lock_check = inspect_file(project, "sources.lock.json")
    if lock_check["status"] != "present_unverified":
        return {"repository": name, "files": [lock_check]}
    try:
        lock = json.loads((project / "sources.lock.json").read_text())
    except (OSError, ValueError):
        return {"repository": name, "files": [{"path": "sources.lock.json", "status": "invalid_lock"}]}
    files = []
    if component == "runtime":
        for entry in lock["sources"]:
            filename = f"{entry['name']}-{entry['version']}.tar.bz2"
            files.append(inspect_file(project, "sources/" + filename, entry["sha256"]))
            files.append(inspect_file(project, "sources/" + filename + ".sig"))
        for path in ("sources/signature_key.asc", "evidence/source-verification.json"):
            files.append(inspect_file(project, path))
    else:
        for key in ("pass", "tree", "oath_toolkit", "pass_otp"):
            entry = lock[key]
            filename = entry.get("archive") or f"pass-otp-{entry['version']}.tar.gz"
            files.append(inspect_file(project, "sources/" + filename, entry["sha256"]))
        for path in ("sources/pass-release-key.asc",
                     "evidence/pass-tag-verification.json",
                     "evidence/tree-source.json",
                     "evidence/oath-source.json",
                     "evidence/pass-otp-source.json",
                     "sources/oath-toolkit-" + lock["oath_toolkit"]["version"] + ".tar.gz.sig",
                     "sources/oath-release-key.asc"):
            files.append(inspect_file(project, path))
        notice = lock.get("bootstrap", {}).get("oath_lgpl_notice")
        if notice:
            files.append(inspect_file(project, "sources/oath-COPYING.LESSER", notice["sha256"]))
    return {"repository": name, "files": files}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=WORKSPACE.parent)
    parser.add_argument("--component", choices=("all", "runtime", "password-store"), default="all")
    parser.add_argument("--sdk-root", type=Path, help="Explicit SDK installation directory")
    parser.add_argument("--target", help="Exact SDK target; selected here, not verified or installed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.target and not re.fullmatch(r"[A-Za-z0-9_.+-]+", args.target):
        parser.error("Expected an exact SDK target name")
    root = args.root.expanduser().absolute()
    components = ("runtime", "password-store") if args.component == "all" else (args.component,)
    sources = [inspect_component(root, c) for c in components]
    cli_present = bool(args.sdk_root and
                       (args.sdk_root.expanduser() / "bin/sfdk").is_file() and
                       os.access(args.sdk_root.expanduser() / "bin/sfdk", os.X_OK))
    blockers = sum(f["status"] not in ("present_unverified", "sha256_matches")
                   for c in sources for f in c["files"])
    report = {
        "scope": "Known input files and SDK path only; no authentication or build acceptance",
        "components": sources,
        "input_blockers": blockers,
        "sdk_cli": "present_not_executed" if cli_present else
                   ("missing_or_not_executable" if args.sdk_root else "not_supplied"),
        "sdk_target": args.target,
        "target_installation": "not_verified",
        "signature_authentication": "not_performed",
        "native_pinentry": "not_covered; exact vendor source and relink inputs are separate gates",
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(report["scope"])
        for component in sources:
            print(component["repository"] + ":")
            for file in component["files"]:
                print("  " + file["status"] + ": " + file["path"])
        print(f"Input blockers: {blockers}; SDK CLI: {report['sdk_cli']}; "
              f"target: {args.target or 'not selected'} (not verified)")
        print("Signatures, target installation, native packaging and builds are not verified.")
    return 0 if blockers == 0 and cli_present and args.target else 1

if __name__ == "__main__":
    raise SystemExit(main())
