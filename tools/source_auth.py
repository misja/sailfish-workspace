"""Public-source transport and signature verification; no personal keyrings."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path

def safe_path(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Expected a project-relative public-source path")
    path = root / relative
    if root.is_symlink() or any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError("Refusing public-source symlink: " + str(relative))
    return path

def digest(path):
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()

def write(path, data):
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("Refusing output symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    temporary.chmod(0o644)
    temporary.replace(path)

def record(path, data):
    write(path, (json.dumps(data, indent=2) + "\n").encode())

class HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        if not new_url.startswith("https://"):
            raise ValueError("Refusing an HTTP redirect")
        return super().redirect_request(request, response, code, message, headers, new_url)

def fetch(url, path, offline=False, expected=None):
    if expected and not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Expected a locked SHA-256 digest")
    if not url.startswith("https://"):
        raise ValueError("Public sources require HTTPS")
    if not offline and (expected is None or not path.exists()):
        request = urllib.request.Request(url, headers={"User-Agent": "sailfish-source-bootstrap/1"})
        with urllib.request.build_opener(HTTPSRedirects()).open(request, timeout=30) as response:
            if not response.geturl().startswith("https://"):
                raise ValueError("Refusing an HTTP redirect")
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                try:
                    shutil.copyfileobj(response, stream)
                    stream.flush()
                    if expected and digest(temporary) != expected:
                        raise ValueError("Downloaded archive digest mismatch: " + path.name)
                    temporary.chmod(0o644)
                    temporary.replace(path)
                finally:
                    temporary.unlink(missing_ok=True)
    if not path.is_file():
        raise ValueError("Missing offline public input: " + path.name)
    if expected and digest(path) != expected:
        raise ValueError("Archive digest mismatch: " + path.name)
    return path

def accepted_signatures(status, returncode, allowed):
    if returncode:
        raise ValueError("Public source signature verification failed")
    bad = {"BADSIG", "ERRSIG", "EXPSIG", "EXPKEYSIG", "REVKEYSIG",
           "NO_PUBKEY", "NODATA", "FAILURE", "ERROR"}
    signatures = []
    for line in status.splitlines():
        fields = line.split()
        if len(fields) < 2 or fields[0] != "[GNUPG:]":
            continue
        if fields[1] in bad:
            raise ValueError("Rejected signature status: " + fields[1])
        if fields[1] == "VALIDSIG":
            args = fields[2:]
            if len(args) < 9:
                raise ValueError("Malformed VALIDSIG status")
            signer = args[0]
            primary = args[9] if len(args) >= 10 else signer
            if not all(re.fullmatch(r"[0-9A-F]{40}|[0-9A-F]{64}", f)
                       for f in (signer, primary)):
                raise ValueError("Malformed signer fingerprint")
            if primary not in allowed or args[7] not in {"8", "9", "10", "11"}:
                raise ValueError("Signer fingerprint or signature digest is not accepted")
            signatures.append({"signer_fingerprint": signer, "primary_fingerprint": primary})
    if not signatures:
        raise ValueError("No accepted VALIDSIG status")
    return signatures

class PublicVerifier:
    """Temporary public-only GPG home; no agent, options file or key retrieval."""
    def __init__(self, keys):
        self.temporary = tempfile.TemporaryDirectory(prefix="sailfish-public-verifier-")
        self.home = Path(self.temporary.name)
        self.gpg = shutil.which("gpg")
        if not self.gpg:
            self.close()
            raise ValueError("Install GnuPG separately before verifying public sources")
        self.command = [self.gpg, "--no-options", "--homedir", str(self.home),
                        "--batch", "--no-tty", "--no-autostart"]
        keyring = bytearray()
        for path in keys:
            armor = path.read_bytes()
            if b"BEGIN PGP PUBLIC KEY BLOCK" not in armor or b"PRIVATE KEY" in armor:
                self.close()
                raise ValueError("Expected published public-key armor only")
            result = subprocess.run(self.command + ["--dearmor"], input=armor,
                                    capture_output=True, check=True)
            keyring.extend(result.stdout)
        self.keyring = self.home / "public-keys.gpg"
        self.keyring.write_bytes(keyring)

    def verify(self, signature, payload, allowed):
        result = subprocess.run(self.command + [
            "--no-default-keyring", "--keyring", str(self.keyring),
            "--no-auto-key-retrieve", "--no-auto-check-trustdb",
            "--status-fd", "1", "--verify", str(signature), str(payload)],
            capture_output=True, text=True)
        signatures = accepted_signatures(result.stdout, result.returncode, allowed)
        return signatures, result.stdout

    def close(self):
        self.temporary.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
