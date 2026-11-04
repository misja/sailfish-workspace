# Pass entry / TOTP consumer adapter

Original adapter code: GPL-3.0-or-later. Existing factory and QtTotp sources keep
their original notices and licenses. This is a selected-entry consumer source
slice, not an installed application or replacement service.

## Inputs and source seams

- Factory: shemeshg/gpgme-cmake-example e53cd22c365ce170ebeaed70984207a8206d00eb.
- QtTotp: shemeshg/pass-simple-qt 1d1e787cf4a3233823f62d3c1c4ae1af7122e069.
- Existing accepted RNP Secrets module/daemon from the preceding API slice.

factory-seams.patch moves the original singleton/factory implementation unchanged
to its own translation unit, with normal upstream CMake still including it.
Generic file/policy helpers can then compile without engine code. GpgIdManage
has a borrowed policy-only helper constructor; existing default construction still
uses the original factory. The new constructor skips unused private enumeration.
Missing/unreadable/empty policies fail explicitly.

InterfacePassFile::encrypt becomes virtual. This CHANGES THE INTERFACE ABI:
fresh-build source consumers; never mix these headers with an older factory
binary. The full default backend build was not rerun in this slice.
qttotp-qt56.patch only replaces Clock's unavailable toSecsSinceEpoch with the
actual Qt5.6 toTime_t API; no clock or OTP implementation is replaced.

## Adapter behavior

SecretsPassHelper owns an actual CryptoManager. A helper must outlive its returned
files and any borrowed GpgIdManage instance. Configure the canonical store root,
RNP plugin name and explicit selected private-subkey identifier. Public Decrypt
flags are not proof of private availability; private enumeration is unsupported.

recipientsFor reuses existing FileSearch/GpgIdManage nearest-policy lookup,
line/comment parsing and nested replacement. Supported basic locators are full
fingerprints, unambiguous 8/16-digit keyids and primary-UID substring matches.
Advanced GPG groups/signing/environment policy is not implemented or accepted.
Canonical entry validation provides ordinary store containment, not a sandbox
against concurrent malicious filesystem replacement.

The adapter resolves/exports EVERY recipient before EncryptRequest or output
creation. Real public packets use the plugin's existing multiple-recipient
extension. The selected private reference is independent of encryption policy.
Failed decrypt clears cached plaintext before any read/request. Successful save
uses QSaveFile, direct-write fallback disabled, checked write and commit; cache
changes only after commit. Broader export/folder/signing/key-management paths
outside this slice fail explicitly. No GPG or RNP engine fallback exists.

selectedTotp decrypts the selected entry and sends its first OTP URI to pinned
QtTotp parsing/generation. HOTP is explicitly unavailable. Base32/HMAC and URI
parsing are reused, not reimplemented. Existing QtTotp parameter clamping and
unknown-algorithm behavior remain conformance limitations; valid-vector success
does not establish arbitrary URI acceptance. Complete entry bytes/notes survive
the tested save path.

## Verification completed 2026-11-03

Build exit0/41.98s on SDK3.13.5/SailfishOS5.1.0.11-aarch64/Qt5.6.3/GCC13.4.
All generic factory sources are freshly compiled against patched headers.
Client DT_NEEDED: Qt5Core, SailfishCrypto, standard C++/C/math/GCC/loader.
No direct RNP/GPGME/Assuan dependencies or helper-spawn imports. Actual consumer
maps likewise contain no OpenPGP engine; the separate daemon loads RNP normally.

Runtime exit0/33.63s,49client+22outer+7target checks pass:

- Root/inherited/nested-replacement/multiple-recipient policies and original
  FileSearch; unknown/ambiguous/empty/missing/unreadable policies refuse.
- Successful replace/cache/fresh reads and second recipient read.
- Failed atomic-output OPEN preserves ciphertext/cache when parent is read/execute
  only and the existing ciphertext file remains writable. This proves fallback
  refusal; it is not a forced commit-stage/crash test.
- Wrong private key, corrupt ciphertext and changed/outside/symlink paths refuse
  without stale plaintext; guard files and provisioned rings stay unchanged.
- All18 SHA1/SHA256/SHA512 values from
  [RFC6238 Appendix B](https://www.rfc-editor.org/rfc/rfc6238.html#appendix-B),
  through real encrypted selected entries at six fixed times.
- Separate same-SDK GPG homes: five expected byte-exact reads and seven refusals
  over four saved entries, verifying nested replacement and both multi recipients.

All632 shared source/input/ELF identities unchanged postrun; zero fixture roots
or owned clients/daemons/buses/agents. Outer stderr empty. Original generic-source
precedence and copied-whitespace build warnings remain in the log.

The original real daemon/plugin is reused unchanged, with the existing private
SDK Ubuntu D-Bus and explicitly approved per-disposable-bus AppArmor exception.
Standard EXTERNAL UID authentication remains; no global policy changes.
Tests remain entirely inside SDK/LXC, using synthetic keys/stores and public
vectors. GPG is fixture/oracle only, not a consumer runtime dependency.

Existing feature evidence: consumer-*20261103* under local
secrets-plugin-review-20261101; exact inputs and source hashes in
consumer-preparation/staging/artifacts records. Independent final reviewer
runtime_review supports bounded acceptance without a blocking finding.
This assistant assessment is not a human security audit or release approval.

Outstanding product work: protected-key unlock UI/session ownership and
production caller authorization, general OTP/HOTP conformance, full-store
operations and device/distribution. No real secrets, device operation, product
installation, new repository or publication occurred.
