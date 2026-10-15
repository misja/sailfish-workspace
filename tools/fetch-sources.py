#!/usr/bin/env python3
"""Recreate locked public source archives and evidence, without SDK or installs."""
import argparse
import hashlib
import sys
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from source_auth import PublicVerifier, digest, fetch, record, safe_path, write

WORKSPACE = Path(__file__).resolve().parents[1]

def runtime(root, offline):
    project = root / "sailfish-gnupg-runtime"
    lock = json.loads((project / "sources.lock.json").read_text())
    key = safe_path(project, "sources/signature_key.asc")
    fetch("https://gnupg.org/signature_key.asc", key, offline)
    records = []
    with PublicVerifier([key]) as verifier:
        for item in lock["sources"]:
            filename = f"{item['name']}-{item['version']}.tar.bz2"
            url = f"https://gnupg.org/ftp/gcrypt/{item['name']}/{filename}"
            archive = fetch(url, safe_path(project, "sources/" + filename), offline, item["sha256"])
            signature = fetch(url + ".sig", safe_path(project, "sources/" + filename + ".sig"), offline)
            signatures, status = verifier.verify(signature, archive, lock["allowed_primary_fingerprints"])
            records.append(dict(item, url=url, signature_sha256=digest(signature),
                                signers=[s["primary_fingerprint"] for s in signatures],
                                signatures=signatures, verification="gpg-detached-signature",
                                verified_at=datetime.now(timezone.utc).isoformat()))
            write(safe_path(project, "evidence/" + filename + ".verification.txt"), status.encode())
            print("Authenticated " + filename, flush=True)
    record(safe_path(project, "evidence/source-verification.json"), records)

def password_store(root, offline):
    project = root / "sailfish-password-store"
    lock = json.loads((project / "sources.lock.json").read_text())
    bootstrap = lock["bootstrap"]
    checkout = root / "sailfish-pass"
    source = lock["pass"]
    def git(*args):
        return subprocess.check_output(["git", "-C", str(checkout), *args])
    tag = source["tag_object"]
    if git("cat-file", "-t", tag).strip() != b"tag":
        raise ValueError("Expected the pinned annotated pass tag")
    if git("rev-parse", tag + "^{commit}").decode().strip() != source["commit"]:
        raise ValueError("Pass tag/commit mismatch")
    key = fetch(bootstrap["pass_key_url"], safe_path(project, "sources/pass-release-key.asc"), offline)
    message, marker, signature = git("cat-file", "tag", tag).partition(b"-----BEGIN PGP SIGNATURE-----")
    if not marker:
        raise ValueError("Pinned pass tag has no OpenPGP signature")
    with tempfile.TemporaryDirectory(prefix="sailfish-pass-tag-") as directory:
        payload = Path(directory) / "tag.txt"
        detached = Path(directory) / "tag.asc"
        payload.write_bytes(message)
        detached.write_bytes(marker + signature)
        with PublicVerifier([key]) as verifier:
            signatures, status = verifier.verify(detached, payload, [source["primary_fingerprint"]])
    data = git("archive", "--format=tar", "--prefix=password-store-" + source["version"] + "/", source["commit"])
    archive = safe_path(project, "sources/" + source["archive"])
    if hashlib.sha256(data).hexdigest() != source["sha256"]:
        raise ValueError("Regenerated pass archive differs from the source lock")
    write(archive, data)
    record(safe_path(project, "evidence/pass-tag-verification.json"),
           dict(tag=source["tag"], tag_object=tag, commit=source["commit"],
                allowed_primary_fingerprint=source["primary_fingerprint"],
                gpg_verify_exit=0, status=status, verified_archive_sha256=digest(archive),
                signatures=signatures, verification="signed-tag-and-git-archive",
                signature_command="gpg --verify detached-tag-signature tag-payload"))
    print("Authenticated signed pass tag and reproduced locked archive", flush=True)
    for component in ("tree", "pass_otp"):
        entry = lock[component]
        filename = entry.get("archive") or f"pass-otp-{entry['version']}.tar.gz"
        url = entry.get("archive_url") or bootstrap["pass_otp_archive_url"]
        archive = fetch(url, safe_path(project, "sources/" + filename), offline, entry["sha256"])
        record(safe_path(project, "evidence/" + component.replace("_", "-") + "-source.json"),
               dict(component=component, archive_url=url, archive_sha256=digest(archive),
                    commit=entry.get("commit") or entry["downstream_fork"]["base_commit"],
                    authentication="publisher-https-and-locked-digest; no signature verified"))
        print("Pinned HTTPS/digest source: " + filename, flush=True)
    entry = lock["oath_toolkit"]
    filename = entry["archive"]
    url = bootstrap["oath_archive_base"] + filename
    archive = fetch(url, safe_path(project, "sources/" + filename), offline, entry["sha256"])
    signature = fetch(url + ".sig", safe_path(project, "sources/" + filename + ".sig"), offline)
    key = fetch(bootstrap["oath_key_url"], safe_path(project, "sources/oath-release-key.asc"), offline)
    with PublicVerifier([key]) as verifier:
        signatures, status = verifier.verify(signature, archive, [entry["primary_fingerprint"]])
    if any(s["signer_fingerprint"] != entry["signer_fingerprint"] for s in signatures):
        raise ValueError("OATH signing subkey differs from the pin")
    record(safe_path(project, entry["verification_record"]),
           dict(version=entry["version"], archive_url=url, archive_sha256=digest(archive),
                signature_sha256=digest(signature), primary_fingerprint=entry["primary_fingerprint"],
                signer_fingerprint=entry["signer_fingerprint"], verification="gpg-detached-signature",
                signatures=signatures, status=status, key_url=bootstrap["oath_key_url"]))
    notice = bootstrap["oath_lgpl_notice"]
    fetch(notice["url"], safe_path(project, "sources/oath-COPYING.LESSER"), offline, notice["sha256"])
    print("Authenticated OATH archive and pinned LGPL notice", flush=True)
    subprocess.run([sys.executable, str(project / "tools/prepare-package.py")], check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=WORKSPACE.parent)
    parser.add_argument("--component", choices=("all", "runtime", "password-store"), default="all")
    parser.add_argument("--offline", action="store_true", help="Reverify existing public cache without downloads")
    args = parser.parse_args()
    root = args.root.expanduser().absolute()
    if args.component in ("all", "runtime"):
        runtime(root, args.offline)
    if args.component in ("all", "password-store"):
        password_store(root, args.offline)

if __name__ == "__main__":
    main()
