#!/usr/bin/python3
"""Scoped SDK 3.13.5 workaround: omit image device nodes in unprivileged LXD."""
import hashlib
import os
from pathlib import Path
import sys
import tarfile

EXPECTED = "d297068072a9898897d3af5ab7128720afa2ccf7baf549dffd4a06ec04425e33"
CONTEXT = Path("/home/ubuntu/SailfishOS/mersdk")

def adapt(context):
    source = context / "sailfish.tar.xz"
    if hashlib.file_digest(source.open("rb"), "sha256").hexdigest() != EXPECTED:
        raise RuntimeError("SDK engine archive changed; review required")
    target = context / "sailfish-lxd.tar.gz"
    omitted = []
    with tarfile.open(source, "r|xz") as src, tarfile.open(target, "w|gz", compresslevel=1) as dst:
        for member in src:
            if member.ischr() or member.isblk():
                omitted.append(member.name)
                continue
            dst.addfile(member, src.extractfile(member) if member.isfile() else None)
    dockerfile = context / "Dockerfile"
    original = dockerfile.read_text()
    if "ADD sailfish.tar.xz /" not in original:
        raise RuntimeError("Unexpected SDK Dockerfile; review required")
    (context / "Dockerfile.upstream").write_text(original)
    dockerfile.write_text(original.replace("ADD sailfish.tar.xz /", "ADD sailfish-lxd.tar.gz /", 1))
    print("LXD SDK adaptation: omitted device nodes: " + ", ".join(omitted), flush=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "build" and Path(args[-1]).resolve() == CONTEXT:
        adapt(CONTEXT)
    if args and args[0] == "run" and "sailfish-sdk-build-engine:ubuntu" in args:
        marker = "tar -C /srv/mer --numeric-owner -xpf /host_install/mersdk/sailfish-tools.tar.xz"
        if marker in args[-1]:
            tooling = CONTEXT / "sailfish-tools.tar.xz"
            expected = "0096efac095cab4c82ffd6012ba96ecaf4f52a8ecb07c936d2e214c41af318e0"
            if hashlib.file_digest(tooling.open("rb"), "sha256").hexdigest() != expected:
                raise RuntimeError("SDK tooling archive changed; review required")
            exclusions = " ".join("--exclude='*/dev/" + name + "'" for name in
                                  ("null", "urandom", "random", "full", "ptmx", "tty", "zero"))
            args[-1] = args[-1].replace(marker, "tar " + exclusions + marker[3:], 1)
            print("LXD SDK adaptation: omit tooling target device nodes", flush=True)
    os.execv("/usr/bin/docker", ["/usr/bin/docker", *args])
