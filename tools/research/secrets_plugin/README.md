# Bounded Secrets/RNP correction fixture

Research patch against dcaliste/sailfish-crypto-plugins commit
`effb3a471738fddf221bc68136bb9789011b2355` (2026-09-03).
Accountable owner: root. Required separate reviewer: runtime_review.
Scope and acceptance are recorded in the existing
[OpenPGP study](../../../docs/development/openpgp-architecture-study-20261018.md)
under the Secrets/RNP correction sections.

The foundation sections below describe r5. The public-recipient extension and
actual public-API fixture are recorded in the final section.

## What the foundation slice changes

- Unsupported key generation/import/export/deletion returns explicit failure.
  Provisioned keyrings remain read-only; destruction never saves keyrings.
  This restriction concerns key management, not pass-entry encryption/writes.
- Stored-key lookup returns identifiers/metadata without fabricated key bytes.
  Operations reject caller-supplied raw key material.
- Decrypt/sign use a request-local RNP context containing exactly the selected
  secret key. A primary reference does not authorize its secret subkeys.
  Symmetric password fallback and signed-only inputs cannot satisfy keyed decrypt.
- Native handle ownership and move behavior are explicit; software capabilities
  are reported honestly. Empty plaintext is distinguished from native failure.
- Public encryption retains RNP suitable-subkey semantics.

This is not a complete adopted plugin or product. Remaining metadata/filter/signature work,
key provisioning, multiple-recipient plugin API, live daemon authorization/unlock,
pass/OTP consumer integration, QMF and distribution need their own bounded work.
No new service or cryptographic implementation is introduced.

## Files and actual execution

`corrections.patch` modifies six pinned upstream files. Apply it to a pristine
tree with `git apply`; never apply it to an already corrected tree.
`CMakeLists.txt` builds a test-named module plus pristine and corrected direct-class
executables against actual Qt/Secrets headers. It references the retained
RNP 0.18.1 SDK build explicitly; it is a research recipe, not distributable packaging.
`sdk-fixture.spec` uses ordinary SDK CMake facilities with `rpmbuild -bc`.
The module is built but never installed, loaded or activated.

`run.py --build BUILD --manifest MANIFEST --launcher LAUNCHER --run` is the
explicit SDK/LXC-only controller, run as SDK Ubuntu UID 1000. The launcher is
`../public_backend/sdk_fixture_launch.py`. The manifest must list the SHA256
identities of the staged inputs, both source trees, retained RNP and three ELF
artifacts; the runner verifies it before executing. It requires the retained
SDK 3.13.5, SailfishOS-5.1.0.11-aarch64 and GPG 2.4.8 inside the same SDK LXC.
The AArch64 probe uses Qt 5.6.3/Secrets 0.2.44/RNP 0.18.1/OpenSSL 3.5.6.
GPG is a synthetic fixture generator and independent output oracle only;
the corrected plugin does not invoke GPG.

The controller generates isolated disposable unprotected and protected RSA
fixtures, including primary, encryption sibling and signing-subkey cases.
Both A and B secret keys are present, making wrong-reference tests meaningful.
A willing symmetric password provider and generic native positives establish
that the symmetric/signed-only negatives exercise the selected-key boundary.
All homes, keyrings and callback inputs are synthetic; no real daemon is contacted.

Completed on 2026-11-03: fresh r5 build exit 0; runtime exit 0.
Corrected control 18/18, protected 23/23 and runner 9/9 pass.
Pristine control has 16 genuine failures out of 17 checks, with its own-key
positive passing. Independent GPG byte and exact signing-subkey oracles pass.
Corrected keyrings remain byte-identical; all 46 manifest identities unchanged;
no temporary fixture directories or matching agents remain.
No ASAN/Valgrind or exhaustive error-injection/leak measurement was performed.

Machine-specific evidence is retained locally under
`.local-artifacts/pass-rnp-slice-20261024/secrets-plugin-review-20261101/`:
`sdk-{staging,build,artifacts}-r5-20261103.json`, build log,
`runtime-keyed-final{-execution,}-20261103.json`, and
`postrun-keyed-final-20261103.json`.
Separate reviewer runtime_review independently checked source reconstruction and
result consistency: no unresolved material finding within this bounded slice.
The record is final-independent-review-r5-20261103.json.
Earlier failed builds, the empty-plaintext runtime failure and r4 predecessor
are preserved. Separate assistant assessment is not a human security audit
or release approval.

## Real public API and multiple recipients — completed 2026-11-03

Apply corrections.patch first, then integration.patch to the pinned pristine
plugin. The extension adds public-only StoredKey export and public encryption;
private export/provisioning remains unavailable. Valid public material is an
explicit encryption capability; private operations still require stored references.

Request each recipient with StoredKeyRequest and MetaData | PublicKeyData.
Supply the first returned Key to EncryptRequest::setKey. The plugin extension
org.sailfishos.crypto.rnp.additionalRecipients accepts a QVariantList of maps:

| Field | Type | Meaning |
|---|---|---|
| fingerprint | QString | Expected full native OpenPGP fingerprint |
| publicKey | QByteArray | Real exported public OpenPGP packets |

Each payload is independently loaded with PUBLIC and SECRET flags to reject
secret packets and missing/mismatched fingerprints. Only verified public packets
reach the aggregate context. No recipient is silently dropped; failures return
no ciphertext. Primary public export includes subkeys and retains native suitable
key selection. QtDBus containers use native types or exact av/a{sv} signatures
with standard qdbus_cast; no custom serialization format is introduced.

integration.cmake/spec builds the actual pinned upstream daemon, plugin,
api-probe.cpp public client and retained direct fixtures. daemon-fixture.patch
only replaces plugin search paths. Actual discovery/P2P dispatch remains active.
api-run.py/controller executes inside the existing SDK LXC as UID1000, with
private HOME/XDG/runtime/plugin/socket paths. The target controller owns its
native daemon; outer controller owns its bus/GPG fixtures. Root deletion requires
all cleanup proofs; uncertain cleanup preserves the root and fails.

The SDK target lacks ordinary NSS account entries. An existing Ubuntu-side
D-Bus1.16.2 in the SAME LXC supplies the session bus; native daemon/plugin/client
and QSQLCIPHER remain actual target components. LXC AppArmor denied the initial
Hello. Explicit scoped approval allowed the OPTIONAL --sdk-bus-config
sdk-session-bus.conf: standard session policy and EXTERNAL Unix-UID authentication,
with AppArmor mediation disabled ONLY for this disposable bus process.
No global D-Bus/AppArmor/LXC policy changes. Default runner execution does not
enable this exception. Future use requires applicable explicit approval; this
test does not establish production confinement or caller authorization.

Standard qt5-plugin-sqldriver-sqlcipher0.2.44-1.14.2.jolla was installed under scoped
approval:1new,58KiBdownload/132KiBinstalled,0upgrades/removals,no refresh or
signature-policy change. NOKEY warning retained. Driver identity is verified
inside the build-shell; its translated path is inaccessible from outer Ubuntu.

Final build exit0/138.93s; actual API runtime exit0/5.0s,22client+7target+14outer
checks pass. A/B recover identical bytes via native stored-subkey requests and
separate GPG oracle homes; C cannot decrypt. Intended malformed/missing/secret/
mismatched-recipient negatives and success after refusal pass. Single stored-ref
encryption remains supported. Final direct suite exit0/25.62s,18control+
23protected+9runner checks pass; pristine16genuine failures/17 with own-key positive.
All549shared identities and provisioned keyrings unchanged; zero fixture roots,
matching buses/daemons or fixture GPG agents remain.

Evidence: existing local secrets-plugin-review-20261101/api-transport-*20261103*
and api-final-independent-review-20261103.json. Earlier build/controller failures
r1-r6 remain preserved. Separate reviewer runtime_review found no blocking finding
within this bounded slice; this is not a human audit or release approval.

Still outside acceptance: production authorization/confinement, protected-key UI
through the daemon, full pass policy/file writes/OTP calculation, provisioning,
remaining P2 metadata/filter/signature behavior, exhaustive error/leak testing,
device and distribution. Same-plugin StoredKey retrieval has upstream TODO
accesscontrol; imported collections default to NoAccessControl. Public retrieval
must not be described as demonstrated per-caller authorization.

## Selected-entry consumer

The [pass-entry/TOTP adapter](consumer/README.md) now reuses the existing store
policy/file interfaces through these real requests. Its independent build/runtime
results and ABI, unlock and authorization limits are documented there.
