"""Fail-closed source checks with synthetic status output and public fixtures."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "tools/source_auth.py"
SPEC = importlib.util.spec_from_file_location("source_auth", FILE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PRIMARY = "A" * 40
SIGNER = "B" * 40
VALID = f"[GNUPG:] VALIDSIG {SIGNER} 2026-01-01 1 0 4 0 1 8 00 {PRIMARY}\n"

class SignaturePolicyTests(unittest.TestCase):
    def test_primary_and_subkey_identity_are_distinct(self):
        result = MODULE.accepted_signatures(VALID, 0, [PRIMARY])
        self.assertEqual(result, [{"signer_fingerprint": SIGNER, "primary_fingerprint": PRIMARY}])

    def test_unknown_future_fields_do_not_change_primary_pin(self):
        result = MODULE.accepted_signatures(VALID.rstrip() + " future-field\n", 0, [PRIMARY])
        self.assertEqual(result[0]["primary_fingerprint"], PRIMARY)

    def test_unapproved_primary_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.accepted_signatures(VALID, 0, ["C" * 40])

    def test_bad_revoked_and_expired_status_rejected_even_with_validsig(self):
        for status in ("BADSIG", "REVKEYSIG", "EXPKEYSIG", "EXPSIG", "ERRSIG", "NO_PUBKEY"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                MODULE.accepted_signatures(VALID + "[GNUPG:] " + status + " synthetic\n", 0, [PRIMARY])

    def test_missing_validsig_and_nonzero_exit_rejected(self):
        for status, code in [("[GNUPG:] GOODSIG synthetic\n", 0), (VALID, 1)]:
            with self.subTest(code=code), self.assertRaises(ValueError):
                MODULE.accepted_signatures(status, code, [PRIMARY])

    def test_sha1_signature_digest_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.accepted_signatures(VALID.replace(" 1 8 00 ", " 1 2 00 "), 0, [PRIMARY])

class SourceTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sailfish-source-auth-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_offline_cache_rehashed_and_corruption_rejected(self):
        path = self.root / "archive.tar"
        path.write_bytes(b"synthetic public archive")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(MODULE.fetch("https://example.invalid/archive.tar", path, True, sha), path)
        path.write_bytes(b"corrupt synthetic archive")
        with self.assertRaises(ValueError):
            MODULE.fetch("https://example.invalid/archive.tar", path, True, sha)

    def test_redirect_to_http_is_rejected_before_contact(self):
        handler = MODULE.HTTPSRedirects()
        with self.assertRaises(ValueError):
            handler.redirect_request(None, None, 302, "redirect", {}, "http://example.invalid")

    def test_http_and_missing_offline_input_rejected(self):
        for url in ("http://example.invalid/file", "https://example.invalid/file"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                MODULE.fetch(url, self.root / "missing", True)

    def test_output_symlink_and_parent_escape_rejected(self):
        (self.root / "linked").symlink_to(self.root / "elsewhere")
        for relative in ("linked/file", "../outside"):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                MODULE.safe_path(self.root, relative)

if __name__ == "__main__":
    unittest.main()
