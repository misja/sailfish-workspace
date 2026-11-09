# OpenPGP architecture study

Started: 2026-10-18. Feasibility study closed: 2026-11-01; separate final source/reuse assessment complete. No product architecture adopted.
Owner: primary assistant. Separate architecture reviewer: reviewer agent.
Decision owner: the maintainer. Related existing work: [password-store #2](https://github.com/misja/sailfish-password-store/issues/2)
and [runtime #4](https://github.com/misja/sailfish-gnupg-runtime/issues/4).
No architecture or migration is accepted by this document.


## Final recommendation — feasibility study closed, 2026-11-01

RNP/OpenSSL is a demonstrated viable engine for the intended Sailfish OTP consumer:
the pinned engine and optional existing backend build and pass the bounded SDK/LXC
runtime experiment. Carry the tested libpgpfactory entry/policy subset, two reviewed
research patches and fixtures forward as reuse material. Before a long-running
product app, fix the concrete native ownership/error paths and define app unlock
lifetime and OTP entry behavior. Unchanged wholesale backend adoption is not
recommended. No new crypto/store/service framework is justified.

Separate closing source assessment is complete. No more feasibility experiment is
needed for this decision. Product integration, device and distribution acceptance
are later work; no architecture/migration is accepted here. The final section
contains exact findings and handoff. Earlier chronological sections retain their
original evidence boundaries and are superseded by later completed results.

Implementation follow-up (2026-11-01): maintainer agreed to develop the Secrets/RNP
direction. Critical source review of the existing plugin is complete; see the
latest quality/security section for P1 corrections before product use. This does
not reopen engine feasibility or authorize real-key activation.

## Scope, preference and acceptance

The maintainer's clarified objective (2026-10-18) is a clear reusable backend with
functionality comparable to pass, on which consumers can be built. A general
password-store management GUI is not the goal. The first intended consumer is an
app to use and manage OTP codes. Browser integration, possibly Browserpass-like,
is a longer-term separate topic, not a current integration deliverable.

Use pass as functional reference and existing implementation baseline. Retaining
the exact Bash program, every extension or GnuPG-specific interface is not an
implicit requirement. Compare the existing pass/OTP command interface, a bounded
pass/RNP adaptation, reusable existing RNP backend code, and direct librnp versus
existing Sailfish Secrets crypto facilities. Existing GUI projects supply source
references; adopting or porting their full UI is not the default research route.

Separate store operations, cryptography/key access and OTP logic. Establish actual
platform consumers separately from plugin availability. Separate RPM package
verification, repository metadata verification and signing. Record pinned evidence,
capability coverage, failure behavior, secret ownership, dependency/lifecycle and
maintenance costs. Do not choose library, subprocess CLI, D-Bus or a daemon before
consumer requirements justify that boundary. No new uniform API/framework is
implied merely by requesting reuse.

Acceptance: a source-supported comparison, concrete remaining gaps, conditional
recommendation, and bounded synthetic experiments proposed for a later decision;
separate assessment must challenge simpler alternatives and invented requirements.
Scope review passed before findings were drafted. No builds, installations,
device operations, real keys/stores, implementation, new repositories, pushes or
publication. Existing release drafts and source pins remain unchanged. SDK access
below queried installed package metadata only; it is not device evidence.

## Executive finding

RNP is a credible alternative OpenPGP engine. Existing pass-compatible applications
already use it: UTPass and pass-simple. Therefore a native RNP client would not be
an unprecedented design, and writing our own crypto adapter first is unjustified.
Neither inspected application is currently established as a complete Sailfish
replacement for our pass/OTP CLI. UTPass targets read-only mobile access; pass-simple
has a Qt 6.5 requirement and distinct recipient/OTP conventions.

The current CLI runtime remains the lowest-change baseline when retaining pass.
RNP can remove the private GnuPG agent/pinentry/Assuan lifecycle for operations
implemented by RNP. It substitutes application or Secrets-daemon key/passphrase
handling, additional library packaging and interoperability work. No measured
claim about total complexity, performance or stronger security follows yet.

Also correct the overly broad earlier suggestion that GnuPG is peripheral to the
platform: the actual inspected SDK has libzypp -> GPGME -> gnupg2 dependencies.
A new RNP password client would not justify removing/replacing stock GnuPG.

## Evidence ledger

All sources inspected 2026-10-18. Remote latest heads are observations, not new
approved packaging pins. Existing release/source locks remain authoritative.

| Input | Examined revision / evidence | What it establishes |
| --- | --- | --- |
| Current package sources | [source lock](../../../sailfish-password-store/sources.lock.json): pass upstream `1078f2514d579178d5df7042c6a790e9c9b731ad`, adaptation `24d4ab48afcc66dcccc14591c41c6fd2c750a4a3`; OTP adaptation `e5dc12c98c3b134eb8e65f00afabee9b525fac93` | Released source identities; current working branches may have later documentation commits. |
| Sailfish Secrets | local adaptation `3e79aaec2092ecc1ddd449d36b9ebc2bd724713b`, README and RPM recipe | Plugin architecture; GnuPG plugins separate from default SQLCipher/OpenSSL plugins. Not proof of installed device consumers. |
| RNP | [`v0.18.1` headers](https://github.com/rnpgp/rnp/blob/v0.18.1/include/rnp/rnp.h), [CMake](https://github.com/rnpgp/rnp/blob/v0.18.1/CMakeLists.txt), [installation](https://github.com/rnpgp/rnp/blob/v0.18.1/docs/installation.adoc); observed main `96f35e38d4f8303317392cd213b649f37d753839` dated 2026-09-26 | FFI library and own CLI; Botan/OpenSSL backends; GPG/KBX/G10 keystores and password callbacks. Main not selected for packaging. |
| Sailfish RNP POC | [`effb3a471738fddf221bc68136bb9789011b2355`](https://github.com/dcaliste/sailfish-crypto-plugins/tree/effb3a471738fddf221bc68136bb9789011b2355), 2026-09-03 | Secrets plugin, separate QMF plugin, direct librnp calls and UI callback. Initial demonstration per [issue #199](https://github.com/sailfishos/sailfish-secrets/issues/199#issuecomment-5440101334). |
| UTPass | [`64f74314a5eb7baa1705d89380b56ff635b590fb`](https://github.com/QRouland/UTPass/tree/64f74314a5eb7baa1705d89380b56ff635b590fb), 2026-06-02; [publisher listing](https://open-store.io/app/utpass.qrouland/) | Existing Qt5 mobile password-store client using RNP; listing explains move away from GPGME due to confined-agent problems. |
| pass-simple | [`1d1e787cf4a3233823f62d3c1c4ae1af7122e069`](https://github.com/shemeshg/pass-simple-qt/tree/1d1e787cf4a3233823f62d3c1c4ae1af7122e069), 2026-10-03; [author documentation](https://shemeshg.github.io/pass-simple-mdbook/) | Existing desktop client offering GPGME or RNP; active recent source, not demonstrated Sailfish support. |
| gopass | [`32231f6de531975874bd33bbf77f12881166258a`](https://github.com/gopasspw/gopass/tree/32231f6de531975874bd33bbf77f12881166258a), 2026-10-16 | README offers default GPG plus other backends, e.g. age; not evidence of an RNP backend. |
| Ripasso | [`25f855dfc3232e6e2a641896b5f9773d76311004/Cargo.toml`](https://github.com/cortex/ripasso/blob/25f855dfc3232e6e2a641896b5f9773d76311004/Cargo.toml), 2026-07-27 | GPGME and Sequoia dependencies; not an RNP example. |
| libzypp | Sailfish wrapper [`cf76fc78834193afb4cc5b8e26233a71be61753a`](https://github.com/sailfishos/libzypp/tree/cf76fc78834193afb4cc5b8e26233a71be61753a), upstream submodule `8b25b2c97e037b4b270271ded44a4af909e6b37b` | Old-GPGME compatibility patch and [KeyManager verification](https://github.com/sailfishos-mirror/libzypp/blob/8b25b2c97e037b4b270271ded44a4af909e6b37b/zypp/KeyManager.cc) using `gpgme_op_verify`, OpenPGP protocol and configured engine. Exact SDK source provenance not established by matching repo name. |
| RPM | [4.16.1 signature parser/verification source](https://github.com/rpm-software-management/rpm/blob/rpm-4.16.1-release/rpmio/rpmpgp.c) | In-process OpenPGP verification path, distinct from signing with external GnuPG and Secrets plugins. Not an exact vendor-source pin. |

### Actual SDK observations

Read-only query through existing SDK 3.13.5 target SailfishOS-5.1.0.11-aarch64:

- `rpm` 4.16.1.3+git20-1.13.2.jolla; QtCore 5.6.3+git60-1.19.5.jolla;
  `gnupg2` 2.0.4+git6-1.8.4.jolla; `gpgme` 1.2.0+git9-1.8.2.jolla.
- `rpm -q --whatrequires gnupg2` reports GPGME in this installed SDK database.
  This misses consumers of shared-library capabilities, optional subprocess
  calls and packages not installed in this target; it is not a device inventory.
- `rpm -q --requires libzypp` includes `libgpgme-pthread.so.11` and librpm;
  `rpm --requires` includes `libcrypto.so.3` and librpmio. Combined with the
  inspected source, this is real evidence against removing stock GnuPG merely
  because RPM itself can verify signatures internally.
- Queried package names `rnp`, `librnp`, `botan`, `botan2` and
  `sailfishsecretsdaemon-cryptoplugins-gnupg` were not installed. That does not
  establish repository availability or differently named packages.
- JSON-C 0.18, zlib 1.3.1 and bzip2-libs 1.0.8 are installed; libcrypto.so.3
  appears in installed dependencies. Wrong-name queries for old OpenSSL packages
  do not establish absence of OpenSSL. No RNP build/ABI compatibility claimed.

The GnuPG Secrets plugin is real cryptographic functionality, separately packaged;
its presence in source does not prove default or frequent app use. Neither an
SDK package query nor the POC establishes what Jolla Mail invokes on Sailfish
5.2. The QMF wrapper points to a separate upstream submodule; default consumer
selection remains a named gap. Avoid conclusions that the plugin is ornamental
or that all native cryptography uses it.

RPM source evidence here concerns package-signature verification. The libzypp
metadata and KeyManager source establish a genuine GPGME dependency and detached
verification facility. A concrete caller trace from repository refresh into that
facility is still open; do not label the exact default repository-verification
route proven by dependency metadata alone. Package signing is a third operation
and can invoke an external signer independently of these verification paths.

## Compatibility dimensions

1. Ciphertext: existing `.gpg` files, recipient/subkey algorithms, compression,
   integrity mechanisms, signatures and multi-recipient messages. Shared OpenPGP
   ancestry is necessary but not a complete interoperability test.
2. Store semantics: relative paths, first-line password/multiline text, nested
   `.gpg-id`, full fingerprint or email recipient resolution, optional signed
   recipient files, re-encryption, concurrent writes and recovery.
3. CLI/extension semantics: exit codes, pipes, GnuPG status/colon output, groups,
   hooks and Bash-sourced extensions. Native format clients need not reproduce
   every extension; record any chosen reduction instead of silently redefining pass.
4. OTP: pass-otp stores `otpauth://` data within encrypted entries; preserving
   its text conventions and HOTP counter writes differs from offering a TOTP
   field with an application-specific YAML schema. OTP need not depend on RNP
   beyond protecting the entry contents. Existing OATH facilities can remain.
5. Git: encrypted files can be transported without decrypting them. Commit
   signing, encrypted textconv and SSH authentication are additional consumers,
   not implied by Git clone support; GUI Git support is not pass CLI parity.
6. Keys: OpenPGP export/import, on-disk key database layout and hardware-token
   stubs are different interfaces. RNP supports more keystore formats than the
   POC currently selects; do not attribute POC limitations to the whole library.
   Smartcard/agent-backed keys remain unverified for the proposed RNP routes.

## Existing alternatives before new implementation

### UTPass

README explicitly targets read-only compatibility. Its CMake uses Qt5 and C++11;
this is a closer starting point than Qt6, not proof of Sailfish buildability.
UI/Click packaging, Ubuntu Touch integration, Git transport and storage locations
need adaptation. Publisher documentation says Git HTTP cloning is supported and
SSH is not. The build bundles RNP/Botan with additional Git/ZIP dependencies.

Source `plugins/Pass/jobs/rnpjob.cpp` creates a GPG-format RNP FFI and manages
its own keyring files. No whole GnuPG-agent replacement is required for those
operations. A placeholder-looking `passProvider` exists in that file; its actual
registration and production decrypt path must be traced before reuse. This is
not a security finding or a production password behavior claim.

No checked source establishes write/re-encryption, pass-otp/HOTP parity or full
CLI/extensions. Use as a read-path and architecture reference; adopting read-only
as the product outcome would need the maintainer's agreement. Recent commit/non-archived
status alone is not a support commitment or security assessment.

### pass-simple

Current source requires Qt 6.5 Quick/Widgets and includes Qt6-specific build APIs;
inspected Sailfish SDK Qt is 5.6.3. This is a concrete porting gap. Its gpgfactory
backend is a submodule, not all functionality in the main repository. Linux
packaging still lists pass/GnuPG/GPGME dependencies: an RNP mode does not by
itself prove a fully GnuPG-free deployment.

Author docs describe RNP recipient lookup restrictions (16-character-or-shorter
key IDs in the recipient file), TOTP in YAML and a GnuPG-based external-command
recipe for security-card integration. Treat these as that application's
conventions, not inherent RNP restrictions. Verify code against current docs
before relying on them. It is a candidate for backend reuse or upstream learning,
not an established drop-in Sailfish package or pass-otp-compatible client.

### Other nearby clients

gopass and Ripasso are useful controls against a false GnuPG-versus-RNP binary
choice. The examined evidence does not establish an RNP backend in either.
An age backend changes ciphertext format; Sequoia is another OpenPGP engine.
Neither should be presented as an already available RNP solution. This search
found two relevant examples; it does not prove a complete ecosystem inventory.

## Focused pass/RNP follow-up — 2026-10-18

The maintainer clarified that read-only access is unattractive and pass-simple is too broad
for the intended use case, independently of its Qt requirement. Neither should
be a leading whole-application adoption candidate on the current evidence;
their backend code can still supply reference material. Actual pass remains baseline.

A narrower search covered indexed pass mailing-list pages, GitHub code queries
for `rnp` with `password-store`, `filename:password-store.sh` and `GPG_OPTS`,
repository searches and direct issue-search API queries. No concrete working
Bash-pass/RNP adapter or fork was identified. Some initial `gh search issues`
queries were rejected by CLI query parsing; those failed searches are not negative
evidence. Direct API searches were then used. Search indexing, fork coverage and
non-GitHub/unpublished work limit any absence claim; this is not evidence that
nobody has tried it. No mailing-list contact or upstream message was sent.

One relevant active exploration was found in [QtPass #2005](https://github.com/IJHack/QtPass/issues/2005),
opened 2026-10-11 and last updated 2026-10-12 at observation. The author reports
an Android build/run probe and explicitly proposes an in-process RNP backend
alongside RealPass and ImitatePass. The [2026-10-12 research comment](https://github.com/IJHack/QtPass/issues/2005#issuecomment-6116308926)
recommends RNP and describes that backend as future work, not planned for 2.0.
This proves a contemporaneous related proposal, not an implemented RNP backend,
Bash-pass compatibility, or applicability of every Android restriction to Sailfish.
Claims in the comment about unrelated products/platform rules are not adopted as
verified facts here. The probe's reported Android success is author evidence, not
an independently reproduced test in this workspace.

The narrower next research question is therefore whether pass's actual
GnuPG-specific calls can be adapted directly to maintained RNP CLI behavior with
a bounded delta, preserving write/re-encryption and packaged OTP behavior. Do not
start a generic gpg emulation layer or a new UI merely because no adapter was found.
The QtPass proposal is a useful upstream direction to track and inspect further,
not a ready dependency to adopt. This addendum adds search evidence and user
preference, not an accepted architecture or implementation authorization.

## Architecture comparison

| Route | Existing facilities and retained behavior | Gap / maintenance ownership | Initial fit with pass baseline |
| --- | --- | --- | --- |
| A. pass/OTP + private GnuPG | Packaged pass/OTP semantics and existing bounded runtime evidence; user-provided extensions disabled by this packaging; stock packages preserved | Maintain private GnuPG/library updates, wrappers, packaging and agent lifecycle; existing device evidence has bounded scope | Strongest immediate fit; baseline for comparison, not an irreversible commitment |
| B. Adapt pass to RNP | Reuse shell store/CLI/OTP behavior; RNP CLI or FFI can do OpenPGP operations | GnuPG-specific recipient resolution, groups, status/colon parsing, signing and re-encryption need explicit adaptation; a generic gpg emulator would become a substantial new interface | Investigate minimal native RNP operations first; no evidence a small executable swap suffices |
| C1. Reuse/adapt existing RNP client | UTPass mobile Qt5 read path; pass-simple existing read/write desktop functionality and dual backends | Port UI/packaging, verify source license/submodules, fill product-specific compatibility gaps; upstream collaboration potential | Must be examined before writing a new client; neither currently proves complete fit |
| C2. New native pass-format client + librnp | Use maintained library APIs; own UI without GnuPG process/agent | Own key/passphrase lifetime, callbacks, storage, store semantics, Git/OTP/UI and security testing; direct library loading adds ordinary ABI/dependency lifecycle | More freedom but more application code; fallback only after reuse assessment |
| D. Native pass-format client + Secrets/RNP | Reuse platform request/plugin/authentication facilities and Damien's POC; cryptographic key handling can live outside client | POC maturity, API/plugin-version compatibility, authorization, daemon lifetime, key layout, store/Git/OTP still need proof | Potential native integration path; not automatically less code or safer than C |

For D, the POC constructs `GPG_COMPAT`, selecting `.gnupg/pubring.gpg` and
`.gnupg/secring.gpg`, and uses Sailfish Secrets interaction requests. Passphrase
cache code is commented out and multiple plugin methods return unsupported.
It is not a modern-key-store migration implementation or complete GnuPG replacement.
RNP's G10 support means the broader library is not inherently limited to that
layout. Running in the daemon also changes where key material resides and what
access-control boundaries must be checked; absence of gpg-agent does not establish
an equivalent hardware-backed or authorization model.

## Dependencies, lifecycle and security ownership

RNP v0.18.1 CMake supports Botan (default) or OpenSSL; building against an existing
supported system library is the first option to investigate, not automatic private
bundling of an entire crypto stack. Inspect actual library versions and algorithm
coverage before choosing a backend. CMake, JSON-C, compression libraries, compiler
and test dependencies still need target verification. Pass-simple's Qt6 gap is
separate from whether librnp itself can build on the SDK.

A direct RNP client removes private GnuPG executables, helper resolution and its
agent sockets for that client. Native library updates instead follow ordinary
process lifetime; an already running client/daemon may retain old loaded code.
Do not invent a coordinator or global exclusion guarantee. Use platform packaging
and upstream lifecycle behavior first. Stock GnuPG/GPGME remains installed for
other consumers. Public pass ownership/Bash conflicts remain for route B when the
CLI is retained; a new separately named GUI need not inherit those conflicts.

Existing CLI acceptance cannot be transferred to RNP. Library CVE tracking,
backend advisories, dependency versions, supported algorithms and key-material
handling require a fresh, scoped review if a route is selected. RNP's maintained
upstream and use in other products are evidence of real deployment, not proof
that a new integration is audited or secure. Licenses of reused code, dependencies
and distribution artifacts must be checked component by component; permissive
RNP licensing does not settle the license of a complete app or vendor integration.

## Backend-first objective and capability questions

This supersedes any earlier suggestion that adopting an entire existing GUI is
the preferred outcome. The reviewed source findings remain useful; the product
objective is a reusable functional backend. Candidate boundaries below are
research questions, not an accepted API or implementation plan.

| Responsibility | Capability to compare | Boundary to resolve from actual consumers |
| --- | --- | --- |
| Password-store access | Enumerate/find entries, read plaintext, insert/update, delete/rename; preserve pass-format and failure-safe writes | Keep presentation outside backend; declare supported subset and errors instead of promising total CLI parity |
| Recipient/store policy | Nested recipient selection, multiple recipients and re-encryption; signed recipient-file behavior where required | Store semantics are not provided by a bare OpenPGP library; identify which pass behavior consumers need |
| Crypto/key access | Encrypt/decrypt, identify usable keys, unlock/cancel; key import/ownership policy | Distinguish using a key from providing an entire key-management application; compare existing facilities first |
| OTP | Discover/read codes, calculate supported OTP types, add/change/remove entries; HOTP counter updates where selected | Separate OTP calculation and entry conventions from encryption engine; specify which operations first app actually needs |
| Synchronization | Preserve store layout for existing Git workflows; identify any needed sync operations | Git implementation/transport/signing is separate from OpenPGP; do not add a new sync framework by default |
| Future consumers | Usable result/error semantics and clear ownership of secret data | Browser connection protocol, access authorization and transport remain later decisions; no current Browserpass protocol commitment |

Read/write support matters; read-only UTPass is source/reference material rather
than the intended product. Pass-simple's application breadth is also not the
objective, independently of Qt6. Its backend may still contain reusable work.
Existing pass provides a real command interface consumers can invoke today; that
is the simpler comparison baseline before designing another API. A library can
be reusable without a persistent process, and a command interface can be reusable
without a generic GnuPG emulator. Secrets supplies crypto/authentication facilities,
not automatically all password-store or OTP operations.

## Recommendation and next decision

Keep current pass/OTP plus private GnuPG as the operational baseline while
studying a backend boundary. Compare observable capabilities and maintenance cost,
not whole-app feature lists. The next technical artifact should be a capability
and call matrix mapping consumer operations to (1) packaged pass/OTP, (2) concrete
RNP CLI/library functions and existing reusable code, and (3) Secrets facilities
where useful. This establishes whether a bounded pass adaptation or reusable
module is worthwhile before choosing process/API shape.

No migration, new service, library repository, general gpg emulator, GUI port or
browser integration is accepted. A substantial scope/design choice needs separate
review and the maintainer's decision after evidence. Existing RNP client code is a reuse
candidate; lack of a ready pass/RNP fork is not itself justification to build a
framework or a replacement application.

Proposed next evidence, not authorized execution of builds/installs here:

- Map backend capabilities to pass operations at locked source, then trace the
  current UTPass decrypt/passphrase path plus pass-simple gpgfactory backend.
  Determine actual gaps before drafting an adapter.
- Inspect SDK package availability and exact library/compiler versions read-only;
  if feasible, propose one bounded RNP build using existing facilities and a
  selected release/backend. No upstream HEAD or new dependency silently adopted.
- With synthetic fixtures only, compare decrypt/encrypt round trips against
  GnuPG: RSA and Curve25519, multiple recipients/subkeys, wrong/cancelled password,
  nested recipient files, signed recipient changes and failure-safe writes.
  Add OTP text/HOTP cases only for the functionality proposed; no blanket retest.
- Compare key import formats, passphrase cancellation/cache lifetime, and Git/SSH
  and commit-signing requirements separately. Hardware-token behavior remains
  a research question until an actual implementation path is identified.
- Map actual Jolla Mail/Secrets consumers and current-target package dependencies
  using source and, only with scoped permission, device metadata. Do not inspect
  real keys/password stores or infer use from a plugin being shipped.

## Verification and limitations

Performed: upstream source/docs inspection, dated commit/API metadata, read-only
SDK package metadata queries, and local scope recording. Not performed: any RNP
or candidate build, executable interoperability test, application port, live
consumer trace, device inventory, security audit or legal clearance. Separate
assistant review found no architecture blocker after correcting overbroad
extension-acceptance wording and distinguishing a libzypp verification facility
from an untraced repository caller. Review is not a human security audit or
implementation approval. Reviewer independently checked local pass semantics
and RNP CMake; remote UTPass/pass-simple blob fetches failed in its web tool,
so those application claims received evidence/consistency review rather than
a repeated independent full source trace. Primary author retrieved their pinned
source through the GitHub API. Existing release publication remains separate.

## Repository availability check — 2026-10-18

Queried existing SailfishOS-5.1.0.11-aarch64 SDK metadata without refresh or
installation: `zypper --no-refresh search -s rnp` and `search -s --provides librnp`
returned no matching items (search exit 104). Enabled repositories were
adaptation-common, apps, customer-jolla, hotfixes, jolla and sdk. The repository
solv-cache timestamps are 2026-06-30; installed-system cache is 2026-10-14.
Therefore no RNP package was found in this SDK snapshot, but this does not
establish absence in current Sailfish 5.2 repositories or community repositories.
No cache refresh, repository change, package installation or device query occurred.

## Bounded feasibility probe — 2026-10-24

The maintainer explicitly authorized exploring the proposed limited synthetic route.
Owner: primary coordinator; implementation: separate Builder; independent scope
and resulting-script/results assessment: reviewer. This extends the historical
2026-10-18 research-only scope without accepting a migration or backend design.
Software installation still requires concrete scoped maintainer approval.

Objective: measure how much existing CLI behavior already supplies the minimal
read/write/re-encryption/OTP substrate before designing any API or service.
No production adapter, GUI, device changes, source-pin update, push or release.

### Capability/call matrix for the first probe

Locked source remains the study source ledger; local line numbers below are
locators, not replacement release pins.

| Consumer operation | Existing pass/OTP behavior | Existing RNP/OATH facility | Concrete remaining gap / probe boundary |
| --- | --- | --- | --- |
| Read entry | pass show/edit/grep invokes GPG decrypt; otp code decrypts text first | RNP `--decrypt --output -`, explicit home/keyring | Byte-for-byte GPG-created entry recovery; keep errors separate from plaintext. This is engine interoperability, not full pass execution. |
| Write/update entry | pass insert/edit/generate invokes GPG encrypt; OTP insert encrypts URI-containing multiline text | RNP `--encrypt --recipient` and output options | RNP-written bytes must decrypt with GPG and preserve fixture content. Application/store mutation policy remains ours. |
| Recipient resolution | `set_gpg_recipients` climbs to nearest `.gpg-id`, strips comments and supports multiple recipients | RNP recipient locators/key lookup; explicit repeated recipients | The crypto library does not implement directory policy. Initially explicit known fixture recipients; nested-policy parsing remains untested, not silently dropped. |
| Re-encrypt | `reencrypt_path` queries GPG groups, colon key data and decrypt/list-only diagnostics, then writes temporary ciphertext and renames on success | Direct decrypt then encrypt to selected new recipient, no need to emulate GPG diagnostics for feasibility | Verify new recipient can read and old-only identity cannot; preservation on failure. Optimizing no-change re-encryption/groups/status parsing remains compatibility work. |
| OTP value | pass-otp parses `otpauth://` and calls OATH, separate from encryption | Existing host oathtool with published RFC6238 fixed-time vector | Encrypt/decrypt the published vector entry and confirm expected code; no inference that RNP computes OTP. |
| OTP change | pass-otp insert/append updates entry, HOTP increments stored counter then encrypts | Existing text mutation plus RNP encrypt | Change a synthetic entry and recover exact content; full parser/HOTP persistence/concurrency remains later evidence. |
| Failed operation | pass uses nonzero status and temporary ciphertext replacement for some paths | Nonzero CLI status, staged output under fixture directory | Missing recipient, wrong password and invalid ciphertext must not replace the previous fixture. Not a production atomicity/recovery guarantee. |
| Key access | GnuPG home/agent semantics | RNP key import with explicit isolated home and password FD callback path | Self-generated synthetic RSA identities only initially; no real key migration or agent behavior equivalence. Curve25519 is separately reported if exercised. |

Upstream manuals inspected 2026-10-24: [rnp 0.18.1](https://www.rnpgp.org/docs/rnp-1/)
and [rnpkeys 0.18.1](https://www.rnpgp.org/docs/rnpkeys-1/). They provide explicit
home/keyfile selection, stdin/stdout, recipient encryption, import and password
FDs. Use these maintained operations before introducing translation mechanisms.
Actual installed binary help will be checked before execution.

### Environment and installation proposal

Read-only host checks: `/usr/bin/gpg` reports GnuPG 2.4.9/libgcrypt 1.12.2;
`/usr/bin/oathtool` exists. `rnp`/`rnpkeys` are absent, and apt reports rnp/librnp0
0.18.1-1.1build1 as candidates in Ubuntu stonking/universe. An executed apt
simulation (`apt-get --simulate --no-install-recommends install rnp=0.18.1-1.1build1`)
proposes five NEW packages and no upgrades/removals:

- rnp and librnp0 0.18.1-1.1build1;
- libbotan-3-12 3.12.0+dfsg-2;
- libsexpp0 0.8.7-4build1;
- libtspi1 0.3.15-1ubuntu2.

This is a concrete proposed host installation, not authorization or execution.
No apt refresh/autoremove, SDK install or device operation is part of it.

### Acceptance and reporting

Script must use only self-created temporary homes and fixture paths; explicitly
select both tools' homes, never discover/import default keys. Passphrases travel
through fixture stdin/FDs, not command-line arguments or logs. Fixture agents are
cleaned only by their own explicit home, then fixture files removed. Public
RFC test data and self-generated fixture keys are the only key material allowed.
Evidence records versions, case IDs/status and limitations, not keys, entry
contents or password values. No skip/unexecuted case may be called passed.

Acceptance for this round is a separately reviewed runnable bounded probe plus
actual results if the needed installation is approved. A missing prerequisite
is reported as such. Builder self-tests and independent assistant review remain
distinct; neither approves product security or migration. Compare actual missing
capabilities and owned code, not hypothetical performance/maintenance numbers.

### Prepared probe and current execution blocker

Builder artifact: `tools/research/rnp_probe.py`. Primary executed syntax compilation
without bytecode writes; passed. Independent script review on 2026-10-24 found no
remaining blocker after recovered-URI OTP calculation, both-tool version guards
and concrete CLI staged-output failure checks were corrected. These checks model
caller replacement-on-success, not production pass atomicity or crash recovery.
Only synthetic RSA cases are prepared; Curve25519 and full pass/OTP remain outside
this first execution. Initial tool check returned exit 2/missing prerequisites
(rnp, rnpkeys), not a passing crypto test. Evidence:
`.local-artifacts/rnp-probe-20261024/check-tools.json` includes script hash.

The concrete sudo/apt installation attempt stopped at
`sudo: interactive authentication is required` before apt ran. No package was
installed or upgraded. Interactive authentication must be completed by the maintainer in
a local terminal; no password is requested through this assistant. No workaround
installation, key generation or interoperability execution was attempted.
After prerequisites exist, Builder can run the already reviewed synthetic probe
and submit results to the separate reviewer. No additional product/backend
implementation or migration is implied.

### Execution-location correction and host cleanup — 2026-10-24

Following the maintainer's feedback, the proposed Ubuntu-host installation is withdrawn.
Use an explicitly scoped LXC environment for the synthetic Ubuntu interoperability
probe; subsequent Sailfish toolchain compatibility remains a separate SDK check.
No container creation or installation has yet been performed. The earlier host
command is historical, not the next action.

Read-only host verification: dpkg reports none of rnp, librnp0, libbotan-3-12,
libsexpp0 or libtspi1 installed. No matching package-install records in today's
dpkg log and no owned /tmp/sailfish-rnp-probe-* directories were found. Thus no
removal was necessary. Existing research/script/evidence files are retained.

## Executed LXC feasibility result — 2026-10-24

The prepared bounded probe was executed in a separate normal unprivileged LXC
container, `sailfish-rnp-probe-20261024`, as user ubuntu (UID/GID1000), with no
host-directory mounts. Image: Ubuntu26.04 LTS amd64, serial20261016, fingerprint
`278bb60fb5e20a059924f02334fbdd591ae1ec908795bc96738751c49cd60dd6`.
Limits:2CPU,2GiB RAM,8GiB root. Existing SDK/device and host packages unchanged.

Only inside that container apt metadata was refreshed and the simulated scoped
installation performed:7new packages,0upgrades,0removals. Exact versions:
rnp/librnp0 0.18.1-1build1, Botan3 library3.10.0+dfsg-2, sexpp0.8.7-4build1,
tspi0.3.15-1, oathtool/liboath0t64 2.6.14-1. Image GnuPG/gpgconf2.4.8-4ubuntu3.1
and Python3.14.3-0ubuntu2 were used. This differs intentionally from the withdrawn
Ubuntu-host proposal; upstream RNP remains0.18.1. Actual installed help confirmed
needed CLI options before execution.

The first attempt failed during synthetic GPG key generation, before any case: an
FD option appended after quick-gen-key positionals was not treated as an option.
A separate minimal diagnostic confirmed that usage/ordering error. Builder's
one-line correction inserts the FD option before command/positionals; separate
review approved it before the correction-driven rerun. This was a harness error,
not evidence of RNP/GnuPG cryptographic incompatibility. First-failure evidence
is preserved alongside corrected results. No unrelated tests were repeated.

Corrected run: exit0,11cases passed:

| Measured behavior | Result |
| --- | --- |
| GnuPG-encrypted synthetic RSA entry recovered exactly by RNP | Pass |
| RNP-encrypted synthetic RSA entry recovered exactly by GnuPG | Pass |
| Decrypt then encrypt for a new recipient; new recipient reads | Pass |
| Old-only secret key cannot decrypt replacement ciphertext | Pass |
| Empty RNP keyring returns failure; caller's original preserved | Pass |
| Wrong fixture password returns failure; caller's original preserved | Pass |
| Invalid ciphertext returns failure; caller's original preserved | Pass |
| Missing encryption recipient returns failure; caller's original preserved | Pass |
| Original encrypted OTP/multiline entry recovered exactly | Pass |
| Edited encrypted OTP/multiline entry recovered exactly | Pass |
| Code computed by OATH from actually recovered URI matches RFC6238 at59s | Pass |

Failure cases exercise real CLI staged-file output and conditional replacement
by this harness. They do not establish full pass save semantics, atomicity after
crashes, general recovery or concurrency safety. Keys/passwords/entries were
self-generated fixtures or published RFC data only; none retained in reports.

Separate source/result assistant review found no blocking finding. It checked
script identity, environment/version consistency, preserved first failure and
argument diagnosis, final cases and cleanup claims without unnecessary rerun.
This is not a human security audit or acceptance of an architecture/migration.
Not tested: Curve25519, full pass/pass-otp execution, nested/signed recipient
policy, GPG groups, HOTP persistence, smartcards, concurrency or Sailfish builds.

Evidence under `.local-artifacts/rnp-probe-20261024/`: lxc-environment.json,
lxc-check-tools.json, lxc-evidence-first.json, fd-order-diagnostic.jsonl,
fd-order-fix.json, lxc-evidence-after-fd-order.json, independent-review.json and
postrun-cleanup.json. Both original and corrected script identities are recorded;
current source is tools/research/rnp_probe.py. Postrun check found0fixturetemp
directories and0gpg-agent processes in the fresh container. It is stopped and
retained for reproducibility; no default home or stock keys were inspected.
Host rnp/librnp0 remain uninstalled.

### What the result changes

The limited engine/entry/OTP path is now executed evidence rather than only
source-based feasibility. Existing RNP operations suffice for those cases without
a generic gpg emulator or new daemon. The probe is not a reusable productbackend
and its size is not an estimate of complete backend maintenance.

The concrete remaining decision is store semantics: recipient selection and
re-encryption decisions, failure behavior, key interaction and exact first-OTP
consumer operations. Quantify those against the locked pass/OTP sources and
existing RNP APIs before choosing a small pass adaptation or a reusable module.
Modern-key interoperability and Sailfish dependency/toolchain checks remain
separate evidence, not silently assumed from the RSA Ubuntu result. Keep current
pass/GnuPG operational; no migration, browser integration or new service accepted.

## Vertical slice scope — 2026-10-24

The maintainer authorized the proposed thin reusable-backend experiment, including
Curve25519, after the successful RSA engine probe. Accountable owner: primary
coordinator; implementation: separate Builder; required independent scope, code
and results reviewer. Scope review completed before implementation. Existing
pass/OTP remains operational; no production architecture/API or migration accepted.

One small research module exposes entry enumeration/finding, read/write, nearest
parent `.gpg-id` recipient selection and TOTP entry/code operations. Use existing
RNP CLI/OATH facilities, Python standard library and ciphertext staging, not a
new daemon/framework. No UI/browser/Git synchronization/key-management product.
The prototype's API is not stable/public. Explicitly bound path/symlink handling,
recipient locator subset, unsupported signed policy/groups and concurrency; do
not silently claim complete pass compatibility or impose new product constraints.

Acceptance: real pinned pass1.7.4/pass-otp1.2.0 code and RNP operate sequentially
on the same self-created synthetic store. Record original source hashes and all
fixture patches; no fake pass implementation. Fixture changes only select explicit
GPG/OATH/extension paths and match Linux installation's platform-line removal.
Fixed OTP time is supplied by a fixture-local OATH wrapper, not changed hostclock.
Read/write in both directions, nearest nested policy override and root-policy
inheritance, multiple recipients each tested with only its own secret key, known
TOTP vectors and entry add/update, and representative failed operations preserving
the original ciphertext. Include own Ed25519 primary/cv25519 encryption subkey;
retain earlier RSA evidence instead of rerunning unrelated cases. Any difference
from pass is a finding or declared subset, not hidden by relaxed crypto settings.

Use existing isolated Ubuntu26.04 LXC, installed pinned RNP0.18.1/GPG2.4.8/OATH2.6.14,
unprivileged ubuntu user and explicit fixture homes only. Preserve snapshots and
cleanup own fixtures/agents then stop container. Source/diff review before run;
separate results review after. No host install, SDK/device change, new repository,
push, release, real keys/stores or production source changes.

Prerequisite query found only tree missing for actual pass list/find; apt simulation
inside the container proposes tree2.3.1-1,1new0upgrade0remove. This Ubuntu tree
version is not the Sailfish-packaged tree2.3.2; no target parity is implied.
Baseline sources exported from existing Git pins into
`.local-artifacts/pass-rnp-slice-20261024/baseline/`, with sources.json SHA256 pins.

### Research-first refinement before vertical-slice implementation

The maintainer reiterated the firm instruction to keep researching known implementations
and avoid invented mechanisms. The provisional Python Store draft was paused
and not written/executed. A separate reviewer challenged each proposed own
recipient/list/write/OTP function before implementation proceeded.

Primary sources inspected2026-10-24:

| Existing implementation | What already solves the problem | Reuse boundary / concrete remaining gap |
| --- | --- | --- |
| [QtPass RealPass](https://github.com/IJHack/QtPass/blob/47fd42102f3d1aceb1f4fe2c9c26976c99a83806/src/realpass.cpp) | Delegates operations to existing pass; no store implementation needed for those calls | Supports starting from pass as an already reusable CLI; its Qt UI is not needed for this probe |
| [QtPass ImitatePass](https://github.com/IJHack/QtPass/blob/47fd42102f3d1aceb1f4fe2c9c26976c99a83806/src/imitatepass.cpp), [shared policy](https://github.com/IJHack/QtPass/blob/47fd42102f3d1aceb1f4fe2c9c26976c99a83806/src/pass.cpp) | Implements recipient selection, file writes and crypto calls itself, including broader signed policy | Considerably larger Qt/executor/policy integration; do not copy its additional rules as requirements |
| [pass-simple's standalone backend](https://github.com/shemeshg/gpgme-cmake-example/tree/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory) | C++17 PassFileRnp/RnpCore encrypt/decrypt/re-encrypt and GpgIdManage nearest-policy/comment parsing exist separately from GUI | Earlier whole-app Qt6 exclusion does not exclude this library. Linux CMake additionally requires GPGMEpp/libgpg-error and RnpCore fetches RNPv0.18.1. Direct reuse remains credible but requires deliberate build/dependency/API review; no automatic fetch or library adoption here |
| [gopass recipient implementation](https://github.com/gopasspw/gopass/blob/8b7c43edab00c079ebf50845612dcda203e48b36/internal/store/leaf/recipients.go), [OTP](https://github.com/gopasspw/gopass/blob/8b7c43edab00c079ebf50845612dcda203e48b36/pkg/otp/otp.go) | Existing store-policy code and use of maintained pquerna/otp library | Part of larger Go store/config infrastructure; not demonstrated as an existing RNP drop-in or reason to adopt a new runtime |
| Locked pass/OTP baseline | Already provides nearest `.gpg-id`, comment handling, multiple recipients, list/find, store commands and OTP parsing/OATH invocation | Native RNP options/subprocess behavior differ; test a small source adaptation before rewriting those functions |

Detailed immutable source references/findings: local
`.local-artifacts/pass-rnp-slice-20261024/upstream-research.json`. These are
research references, not silently adopted packaging pins. None of these projects
received a complete security audit; no referenced source was built or executed.

The smaller revised experiment supersedes the earlier proposed Python Store:
compare real pinned pass+OTP using GPG against the same store/OTP source using
native RNP crypto calls. No new recipient walker, file finder, writer policy or
OTP parser. The research harness merely calls those two CLI variants on the same
synthetic store and records exact transformations. The separate reviewer accepted
this narrower direction before code.

Concrete call differences to verify: GPG_OPTS must use native RNP options,
GPG `-o` crypto callsites must use documented RNP `--output`, and decrypt callsites
need explicit `--output -` because RNP file-input defaults differ from GPGstdout.
The launcher only sets the fixture RNP home and passphrase FD; it must not become
a general GPG-argument emulator. Every removed option needs a recorded effect:
GPGyes maps to overwrite, compress-none to RNP-z0, quiet is replaced by captured
stdout/stderr. GPGno-encrypt-to has no asserted exact replacement; the bounded
probe uses fresh config-free key homes, explicit recipients and independent
recipient checks. No broad trust/config/security-equivalence claim follows.

Unsupported GPGmetadata/signed-policy/init/move/re-encryption paths stay explicitly
outside this subset; do not let untested code silently fall back to GPG or fake
metadata. Nested/multiple recipient tests prepare `.gpg-id` fixturefiles and
exercise real insert/show policy, not complete pass-init or recipientmanagement.
Actual pass insert writes directly to its destination; negative write tests must
observe that behavior and report differences, not add a new staging policy merely
to make the experiment pass. No production code/security rule changes occur.

Session-limit checkpoint: refined slice has not been implemented or executed.
Only exact baseline exports, primary-source research and container tree dependency
are prepared. Container stopped/retained; see local pass-rnp-slice-20261024/handoff.json.
The earlier11passed cases concern the separate RSAengineprobe only.

## Fresh-session handoff — 2026-10-24

The maintainer requested continuation in a new session due to context/session
limits. STATUS.md is the current concise handoff. Container stopped/retained.
A source-only preparer, tools/research/prepare_pass_rnp_fixture.py, has been saved
and syntax-compiled only: NOT reviewed or executed. It prepares pinned-source
fixture copies/diffs, not a backend or complete harness. No pass_rnp_slice.py
exists and no new vertical-slice/Curve25519 tests have run. Preserve existing
uncommitted work and baseline/research evidence. Next is separate source/diff
review plus completion of the real-source harness before any crypto execution.

## Executed real-pass/RNP slice — 2026-10-24

The separate Builder completed `tools/research/pass_rnp_slice.py`; the independent
reviewer checked scope, preparer, complete source and exact fixture transformations
before execution, then reviewed results without rerunning crypto. The preparer's
fixture-prefix check now uses a safe-character allowlist. Existing pass/OTP policy,
list/find, writers and parsers were retained; no own Store/parser or staging added.

Reviewed/executed harness SHA256:
`9af655e3ca203bffcdd060c02203e4cf41c4013da3d8b87c6ef5faaff8004961`;
preparer `c3df3459beb9cf6f3650a075dd51395bf962549804e25bcd2756dbc88a77c09f`.
Pinned baseline hashes remain unchanged. Scripts/baselines were copied into the
retained Ubuntu LXC and individually hash-verified before execution as ubuntu.
Image/package versions match the earlier environment; actual OATH help confirmed
`--now`. No installation, host/SDK/device change or production source edit.

First execution returned exit0 with32distinct passing checks: two self-generated
Ed25519 primary/cv25519 encryption identities; both directions of real pass
write/read on the same store; root inheritance and nearest nested recipient
override; two recipients each decrypted with only its own secret key; actual OTP
insert, append, existing-token label update and RFC6238 SHA1 code at59seconds;
matching real list/find; failed reads for empty keyring, wrong password and invalid
ciphertext, and nonzero missing-recipient write exits. Fixed-time OATH and explicit
key homes/password FDs were fixture-only. Existing-token update changed its label,
not its secret/algorithm; no wider OTP-update coverage is claimed.

The suite status is NOT failed-write preservation acceptance. Four separate
observations expose two material gaps:

| Actual operation | GPG baseline | Native RNP variant |
| --- | --- | --- |
| Direct insert over existing entry with missing recipient | exit1; original ciphertext preserved | exit1; destination absent |
| OTP append with wrong decrypt password | exit0; original ciphertext changed | exit0; original ciphertext changed |

The append observation establishes non-preservation and a misleading success
status; resulting plaintext content was not measured independently. Pinned OTP
append reads via process substitution without propagating the decrypt status,
which is a source-supported explanation, not a newly introduced RNP behavior.
No preservation fix was added. The RNP manual documents overwrite/output options
but does not establish preservation-on-error; do not treat `--overwrite` as a
transactional save facility ([RNP0.18.1 manual](https://www.rnpgp.org/docs/rnp-1/),
rechecked2026-10-24). Root policy used fingerprint-only lines. Inline-comment
locator whitespace compatibility remains unmeasured.

Evidence in `.local-artifacts/pass-rnp-slice-20261024/`: slice-execution-inputs.json
(image/package/copied hashes), slice-first-execution.json, slice-first-results.json
(commands, cases, observations, exact fixture patches and wrapper hashes),
slice-postrun-cleanup.json and independent-review.json. Independent review
reproduced all four generated hashes and exact diffs in memory and found no
blocking evidence inconsistency. External cleanup verified zero own fixture
temporary directories and zero gpg-agent processes; container STOPPED/retained.
Only reviewed nonsecret source copies remain in its research directory.

Conclusion for this round: existing pass/OTP plus native RNP handles the measured
normal modern-key/store/OTP subset, but a direct CLI option substitution is not
a safe production adaptation because failed writes differ and OTP append already
has a baseline failure-propagation gap. Next inspect pinned upstream RNP output
handling, pass/pass-otp failure handling and existing reuse candidates' save
behavior before proposing a bounded solution. No new API, custom writer, library
adoption, architecture or migration accepted. Sailfish build/dependency acceptance,
init/reencrypt/mv, metadata/groups/signed policy, HOTP, Git, smartcards, concurrency
and crash recovery remain untested. Assistant source/results review is not a
human security audit or release authorization.

## Failed-save source investigation and reviewed next proposal — 2026-10-24

Owner: primary coordinator/researcher. Scope recorded in STATUS before proposal:
explain the two measured failures, inspect existing implementations, compare
maintenance tradeoffs and obtain separate review before any implementation.
This round fetched public source and checked shell control flow only. No crypto
rerun, container start, installation or production source change.

### Immutable evidence and actual causes

RNP v0.18.1 annotated tag object
`b643e4bb02908dc37d6777c832cc843d59bb1f45` resolves to commit
`aad1892e4d8423398a0b973bd0a7e4544c359afc` (tagger2025-11-21). The GitHub API
returned an unsigned tag, not an authenticated signature. Source identity is pinned;
this is not new package provenance verification. Observed container package remains
0.18.1-1build1; its distribution patch series was not reconstructed this round.
Local `source-research/manifest.json` records17retrieved files with SHA256/Git blob
IDs, plus a failed guessed stream-dest.cpp path; stream-common.cpp was subsequently
located and retrieved. A separate reviewer verified all17hashes and blob IDs.

**RNP direct output.** In [fficli.cpp](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/rnp/fficli.cpp#L2979),
`cli_rnp_protect_file` initializes IO before encryption/recipient lookup. The output
helper passes OVERWRITE alone to `rnp_output_to_file`.
[Library output cleanup](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/lib/rnp.cpp#L2204)
and [file destination handling](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/librepgp/stream-common.cpp#L767)
explain the observation: direct output truncates the destination; recipient lookup
can fail before successful execution marks output to keep; destroy discards it by
unlinking. Removing `--overwrite` would refuse normal replacement, not implement
a successful safe update. Prechecking recipients alone would leave later failures
unaddressed. No transactional-output CLI option was found in this version's option
table. This is a source explanation consistent with measured behavior, not a new
execution of the packaged source.

**Existing librnp facility.** The [0.18.1 API](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/include/rnp/rnp.h#L3546)
already offers `RNP_OUTPUT_FILE_RANDOM | RNP_OUTPUT_FILE_OVERWRITE`. It creates a
random adjacent temporary output; successful operation can be followed by checked
`rnp_output_finish` and rename. Caller must gate commit on operation success.
[Upstream output tests](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/tests/ffi.cpp#L2793)
assert that original size stays unchanged before finish and successful overwrite
changes it. These tests were inspected, not run by us.

Limits matter: the inspected finish path does not fsync. `dst_finish` marks an
output finished even when its finish callback fails; the temporary close path
then skips unlink. Consequently automatic leftover cleanup on failed finish and
a meaningful retry via a second finish call are not established. Do not invent a
recovery framework: first measure this API's actual success/error/leftover behavior
in the bounded synthetic environment. No crash-durability or concurrency claim.

**OTP append.** The [pinned adaptation](https://github.com/misja/pass-otp/blob/e5dc12c98c3b134eb8e65f00afabee9b525fac93/otp.bash#L243)
parses decrypt output through process substitution, without checking the producer's
exit. Encryption can therefore proceed after failure. Pass already enables
`pipefail`; it does not propagate asynchronous process-substitution status.
Current upstream develop was resolved read-only to
[7bb50dbc4b6073f12f40be66a5ee371b9652a646](https://github.com/pass-extension/pass-otp/blob/7bb50dbc4b6073f12f40be66a5ee371b9652a646/otp.bash#L283),
dated2025-08-09, on2026-10-24. It captures old contents first but still does not
guard decrypt status; it is not an existing fix to adopt. No upstream update applied.

Host Bash5.3.9 minimal-environment control-flow checks, with only false/synthetic
text and no keys/files/crypto: process substitution under pipefail continued with
status0; unguarded capture continued; checked capture rejected a producer that
returned partial output and exit1 before the write branch. These establish shell
behavior only, not a tested OTP patch. Official GNU Bash manual web retrieval
timed out; no successful manual verification is claimed. A future append correction
should check the complete decrypt result before the existing parser/writer; mere
staging cannot prevent a successful encryption of incomplete input. Retain current
multiline semantics and avoid accidentally masking status with local declaration.
OTP code/URI paths also warrant later error review; they were not silently added
to this append task.

### What existing implementations already solve

| Existing route | Useful existing behavior | Concrete gap and maintenance implication |
| --- | --- | --- |
| [Pinned pass](https://github.com/misja/sailfish-pass/blob/24d4ab48afcc66dcccc14591c41c6fd2c750a4a3/src/password-store.sh#L135) | Re-encryption and in-place generation already use ciphertext temp plus conditional rename | Smallest short-term CLI adaptation can reuse that pattern at supported write sites, with checked commit/cleanup; it still owns shell patches at every covered mutation site and does not solve OTP decrypt status by itself. No complete writer safety follows from these source examples. |
| Native librnp | Existing adjacent temporary output and explicit finish result | Avoids implementing another output mechanism; needs demonstrated error ownership, key/password/resource integration and later Sailfish build evidence. Not yet a reusable pass backend or proven maintenance win. |
| [pass-simple standalone RnpCore](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/RnpCore/RnpCoreBal.cpp#L195) | Existing standalone encrypt/decrypt/re-encrypt APIs outside Qt GUI | Ordinary encryption creates direct rnp_output_to_path output before recipient lookup. Re-encryption's backup/restore uses a separate plaintext file. Thus wholesale reuse does not itself demonstrate solving this save gap. Linux CMake still requires GPGMEpp/libgpg-error and fetches RNPv0.18.1; no build/dependency adoption or runtime failure test performed. |
| [QtPass ImitatePass](https://github.com/IJHack/QtPass/blob/47fd42102f3d1aceb1f4fe2c9c26976c99a83806/src/imitatepass.cpp#L205) and [placement utility](https://github.com/IJHack/QtPass/blob/47fd42102f3d1aceb1f4fe2c9c26976c99a83806/src/util.cpp#L665) | Encrypts in scratch space, places only after success; adjacent temporary, checked copy, sync and replacement utility already exist | Useful precedent, not an RNP backend. Whole utility includes Qt/platform/link policies beyond this research scope; copying them creates extra maintenance and is not justified by the bounded gap. |

### Reviewed recommendation and next bounded evidence

Keep the operational GPG baseline. Separate the backend-independent OTP append
error from engine-output behavior. For an immediate Bash adaptation, extending
pass's existing ciphertext-temp/conditional-rename pattern is the smaller source
delta. For the stated reusable native backend objective, the next evidence should
instead validate librnp's existing random-output/finish facility before creating a
writer or adopting pass-simple. This is a research priority, not a production route
selection or claim that native integration is cheaper overall.

Proposed bounded follow-up: explicit synthetic homes and the retained pinned LXC;
original unchanged before commit; successful encryption+finish replaces it and
decrypts exactly; missing recipient and crypto failure preserve it; deliberate
finish failure returns an error, preserves the original and records any temporary
leftover. Verify prerequisite availability before selecting the smallest probe
implementation; no silent install or product API. An append-only follow-up should
reject failed/partial decrypt before any writer call and preserve multiline success
behavior with the actual pinned OTP parser. Separate Builder, source review before
execution and independent result review remain required.

Independent reviewer `save_review` checked causes,17source identities, simpler
alternatives and maintenance costs, and accepted this bounded research proposal
with the stated caveats. No implementation, migration, dependency adoption, human
security audit or release approval follows. Review evidence lives alongside the
existing feature under `source-research/independent-review.json`; no new backlog.

## Executed native librnp output probe — 2026-10-25

The maintainer authorized this bounded experiment after the source investigation. Owner:
primary coordinator. Separate Builder `builder` implemented
`tools/research/librnp_output_probe.py`; independent reviewer `reviewer` accepted
the approach, reviewed the exact source before execution and checked results and
cleanup without rerunning crypto. No product backend/writer or OTP change.

Existing Python ctypes and installed librnp sufficed; no compiler, dependency
installation or upstream source execution was needed. Actual prerequisite query
confirmed UID1000, librnp0.18.1 and required symbols. The retained LXC image and
package versions were recorded again; only the reviewed script was copied and
hash-verified. Executed as ubuntu with minimal environment, explicit synthetic
GPG home, fresh Ed25519primary/cv25519encryption identity, password FD to GPG and
a bounded wrong-password callback to native librnp. Native FFI started empty in
memory and loaded only freshly created synthetic key bytes. No default keys.

Reviewed/copied/executed script SHA256:
`e553b7a89e8137964f78ab96133978be12386786598192d413e2b7b898c93096`.
Executed process identified `/usr/lib/x86_64-linux-gnu/librnp.so.0.18.1`, version
0.18.1, SHA256`5e1e6aa430bda07ee83a0ae9457a0becf9331bdd6b60a471690f6f32b8af6963`.
This is harness-observed loaded-library identity, not independently reconstructed
distribution source/patch provenance. Package librnp0 remains0.18.1-1build1;
GPG2.4.8 and Python3.14.3 were retained.

First run exit0:4cases passed,34native API calls and9GPG commands recorded.

| Case | Measured result |
| --- | --- |
| Native RANDOM\|OVERWRITE encryption and checked finish | Original unchanged after output open and after encryption before finish;1adjacent temporary. Finish returned0; replacement decrypted exactly through GPG;0temporaries after destroy. |
| Missing recipient | Locate returned0 with a null key handle: preparation failure, not a nonzero native API error. No operation/finish; original preserved;0temporaries after destroy. |
| Actual crypto failure | Native decrypt with wrong fixture password returned301989892; callback invoked once. No finish; original preserved;0temporaries after destroy. This tests decrypt failure, not every encryption failure mode. |
| Induced finish failure | Successful encryption followed by making only its own fixture directory0500 under UID1000. Finish returned301989888; original preserved;1adjacent temporary remained after native output destruction. Permissions restored before fixture cleanup. |

All outputs used the existing native random-file mechanism; no custom writer,
commit/retry or recovery framework was added. Native diagnostics were suppressed
in a temporary diagnostic file; reports contain return codes/counts/comparisons,
not raw key material, entry contents or passwords. Fixture cleanup removed its
whole temporary root, including the measured failed-finish leftover. Independent
external check found0own fixture directories and0gpg-agent processes. Container
is STOPPED/retained; only reviewed nonsecret script copies remain.

An important lifecycle rule from inspected source remains: destroy can automatically
finish successful output and ignore the finish result. The probe explicitly
checked finish; it did not test or establish destroying successful output as abort.
Failed finish was not retried and native automatic leftover cleanup is disproven
for the induced case. Ordinary output destruction returned success despite the
preceding finish failure, so that return alone is insufficient to report save success.

Evidence, beside the existing feature:
`.local-artifacts/pass-rnp-slice-20261024/native-output-20261025/` contains
execution-inputs.json, first-execution.json, first-results.json,
postrun-cleanup.json and independent-review.json. Source investigation pins remain
under source-research/. Independent reviewer checked identities, all four cases,
call/result consistency and external cleanup; no unresolved finding in the bounded
evidence. Assistant review is not a human security audit or release approval.

This closes the narrow native-output evidence gap: existing librnp can preserve
the original and explicitly report commit failure for the measured paths. It does
not repair the earlier direct CLI adaptation or the separate OTP append decrypt
status bug. No complete backend/API, general save safety, cleanup/recovery policy,
concurrency, fsync/crash durability, Sailfish dependency/toolchain compatibility or
migration has been accepted. Any future integration of this native facility needs explicit operation/finish/
resource-error handling; destroying output alone cannot establish success.
Choose and review a bounded integration scope before building it.

## First OTP consumer: operation mapping and public reuse boundary — 2026-10-25

User authorized this comparison and then the proposed public-backend experiment.
Owner: primary coordinator; independent scope/design reviewer: `save_review`.
The supplied product objective is reusable pass-like read/write functionality for
an OTP app. The following is a bounded integration scope, not a finalized product
API or complete feature specification. Candidate entry paths are not automatically
a complete OTP inventory. HOTP, OTP discovery, removal/rename, import, synchronization
and key-management UI remain product questions rather than excluded requirements.
No index, whole-store decryption, new service or parser is implied.

### Important correction to the earlier native-save inference

At the same inspected backend pin
`e53cd22c365ce170ebeaed70984207a8206d00eb`,
[InterfacePassFile::encrypt](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/InterfacePassFile.cpp#L24)
already creates an adjacent UUID-named temporary, calls low-level encryption there,
removes it on an encryption exception, then renames it to the entry. Earlier
conclusions about direct ordinary output apply to `encryptStringToFile`/RnpCore,
not to this public higher-level save. This corrects an incomplete reuse-boundary
assessment, not a change in upstream version. Test the existing public route
before proposing its replacement or forcing native RANDOM output into it.

Limits are still concrete: rename occurs outside its encryption catch, so a rename
error may leave temporary output; the object assigns its decrypted field before
save succeeds, so cached plaintext does not establish disk success. Existing
recipient validation and actual error propagation need runtime evidence. None of
this public backend has been built or executed by this research yet.

### Operation and ownership comparison

| First-consumer operation in bounded experiment | Existing pass/OTP baseline or small CLI adaptation | Existing native reuse candidate and remaining gap |
| --- | --- | --- |
| List/find candidate encrypted entries | Real pass list/find already exercised; uses current filename/store semantics | FileSearch/searchDown supplies traversal, with path-only search avoiding decrypt; caller filters using existing isGpgFile because path-only search itself is not .gpg-only. No new walker needed. Native filtering behavior remains unexecuted. |
| Read selected entry; unlock or refuse before write | pass show decrypts through existing GPG runtime; RNP variant measured isolated CLI homes/FDs, not app unlock UX | Public getPassFile/decrypt/getDecrypted and callback/prompt hooks exist. Test refusal in a fresh process before any successful unlock; callback counters and no save invocation establish that checkpoint, not arbitrary cancellation or a product cache policy. |
| Interpret selected URI and calculate TOTP | Existing pass-otp parser and OATH invocation already exercised with recovered entries | Native crypto/store interfaces do not themselves perform OTP. Separate existing QtTotp app code accepts URI and generates codes; its Qt dependencies and differing validation policy need review/tests before adoption. No own parser justified. |
| Add or update entry without losing notes | Actual OTP insert/append supplies URI/multiline composition; known append decrypt-status bug must be corrected separately. CLI RNP write sites need deliberate preservation handling. | Public encrypt accepts complete entry text and stages ciphertext. This preserves supplied bytes if roundtrip succeeds, but does not itself locate/replace an OTP URI within notes. Probe precomposed full-entry fixtures first; this is entry IO for the consumer, not implemented native OTP mutation. |
| Respect nearest and multiple recipients | Actual pass recipient logic already exercised with nested/multi policies | The public GpgIdManage constructor uses nearest-policy search and resolves records. Its existing ensureValidGpgIdFile must guard unresolved/ambiguous entries before using encryptTo; silently using only resolved recipients would change policy. Missing policy and no usable recipients must be observed. |
| Surface crypto/save failure | CLI exit/stdout/stderr exists; prior direct RNP write and OTP append failures remain material | Native calls/exceptions and public save provide existing error paths. Test disk state separately from object state; auth refusal before save and commit errors are different checkpoints. No arbitrary post-encryption abort promise. |

Source references: [public helper](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/export/InterfacePassHelper.h),
[recipient policy](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/GpgIdManage.cpp),
[search composition](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/InterfacePassHelper.cpp#L159).
These describe existing capabilities, not passing integration tests.

### Key access, dependencies and maintenance

The baseline keeps the current GPG agent/runtime and real pass/OTP behavior. A small
pass/RNP adaptation remains the smaller source delta for retaining this CLI; it
still owns changed crypto calls, each supported write path and the separate OTP
status correction. No generic GPG emulator or full Bash compatibility is required
by the reusable-backend objective.

The standalone native library already offers helper/file/policy interfaces without
the GUI. Its Linux CMake retains GPGMEpp/libgpg-error and builds RNP via FetchContent;
C++17 is required, and the selected RNP Botan3 path sets C++20 internally. Reuse
does not automatically remove GPGME dependencies or prove lower total maintenance.
The factory caches the first backend/home/callback in a singleton; bound one home
per fixture process rather than redesign it. FfiRaII has its rnp_ffi_destroy call
commented out, and the string password provider returns true rather than exposing
a direct refusal result. Existing retry/refusal prompt paths require an actual
exercise. Process exit can bound the experiment, not establish production secret
lifetime, memory wiping or key migration support.

A separate [QtTotp URI parser/generator](https://github.com/shemeshg/pass-simple-qt/blob/1d1e787cf4a3233823f62d3c1c4ae1af7122e069/QtTotp/totp.cpp)
and [entry point](https://github.com/shemeshg/pass-simple-qt/blob/1d1e787cf4a3233823f62d3c1c4ae1af7122e069/QtTotp/getTotp.cpp)
exist outside the backend: SHA1/256/512 selection and URI settings already exist.
This narrows earlier YAML-storage observations to application conventions; they
are not an engine requirement. The parser clamps period/digits and defaults unknown
algorithms to SHA1, so those choices must not become our product requirements.
The wrapper includes Qt/QML registration; actual Sailfish Qt5.6 compatibility has
not been established. Source notices differ: backend root MIT and inspected TOTP
file GPL2-or3 notice; preserve notices and review actual adopted subset if selected.
No dependency or code adoption has occurred.

### Reviewed smallest useful integration experiment

Prefer testing the existing public native entry route now over another own-output
helper: a small no-GUI C++ fixture links unchanged libpgpfactory, composes its
FileSearch/GpgIdManage/getPassFile/decrypt/encrypt on the same synthetic store, and
checks exact full-entry roundtrips and policy/auth failures. Existing pass/GPG and
pinned pass-otp remain baseline/oracle where needed. Native OTP URI mutation or a
fully native OTP calculator is not the acceptance claim. No stable new API.

Fresh process/home for auth refusal, explicit unresolved-recipient guard, supplied
multiline/URI fixtures and no save after read refusal are required test discipline.
An optional naturally conflicting-directory rename case measures exception and
leftover behavior; it cannot establish original-ciphertext preservation at a file
target. Do not add races/hooks just to emulate the earlier native finish test.

Full immutable backend/RNP archives were fetched and safely extracted, not run.
Source-research manifest now contains33individually inspected files; archive
manifest records full inputs separately. Build through original CMake targets,
using local pinned FETCHCONTENT_SOURCE_DIR_RNP and disconnected mode, existing
SYSTEM_LIBSEXPP and Botan3 options. No extraction, dependency removal or imported
target shim. Existing version.cmake is present, avoiding its mutable fallback.
Actual compiler/CMake/pkg-config/dev headers are absent from retained LXC. A pinned
apt simulation proposes52new packages and3dependency upgrades (liblzma5, zlib1g,
xz-utils),0removals. No install performed; scoped human approval is required before
that container-only change. Full plan: public-backend-20261025/prerequisite-proposal.json.

Independent reviewer accepted this comparison/probe scope with the above caveats
and verified33file hashes/blob IDs plus complete source archives. Builder is
preparing concrete source/build artifacts; separate exact-source review precedes
any execution. No native product route, GUI port, host/SDK/device change or migration
is accepted.

## Public-backend build, first failure and session checkpoint — 2026-10-25

The user authorized execution of the reviewed public-entry experiment. Exact
CMake/C++/runner/README source review completed before action. Explicit scoped
container-only installation approval covered52new packages and3dependency updates
(liblzma5,zlib1g,xz-utils). The first configure failed because Gpgmepp's CMake
configuration required GPGME C development files absent from its distro package
dependency list. Failure preserved; a second explicit approval added libgpgme-dev
2.0.1-2build1 and libassuan-dev3.0.2-2build1,0updates/removals. Total54new3updated
packages in research container only. No host/SDK/device package changes.

Unchanged-source configure and target-only build then succeeded with CMake4.2.3,
GCC15.2, Botan3.10, sexpp0.8.7 and GPGME2.0.1. Original1086archive files remain
byte-identical. Clean-env loader verification resolves RnpCore and RNP to build
paths, while GPGME/Assuan remain real linked dependencies. Binary SHA256
84c4c196307cf67a620368783dd78e7ad9fdd91a0be54ccfa499c457f1397718. This rebuilt
RNP environment differs from the earlier distro-librnp probe. No upstream test
suite or GUI was built/run; compiler warnings are retained in build log.

First public runner exit1/error: fresh unlock refusal passed with one password
callback, one refusing prompt, zero save and unchanged originals. Path-only list/
find/no-authentication and exact selected-entry decrypt passed. Normal mode then
threw before its first policy assertion/save. Public writes, successful recipient
policy, independent-B and external OTP oracle remain UNEXECUTED, not passed.

Source diagnosis: RnpCoreBal::listKeys accepts fingerprint through initial native
lookup but filters results again over getKeyStr (keyid/name/email, no fingerprint).
Thus full-fingerprint .gpg-id may be classified unresolved. This source-supported
compatibility hypothesis fits the failure but has not yet been runtime-confirmed
by the diagnostic. It is not a fixture error or reason to silently change a store.

Builder saved limited numeric/fixed-stage/error-category diagnostics; reviewer
independently cleared exact CPPc9a853c124b5fe49f3964175488716aeaf96657854959bc07d359d1716b47e4d
and runner32cd959a1ae9bcc5b1c9a2ff8f57ff56c0757699a0c6dbfcf5722afe10f98faf.
Original fullfingerprint policy and backend source remain unchanged. These diagnostic
versions are NOT copied, rebuilt or executed. First-run source and prepared
diagnostic snapshots are preserved separately.

User reported5%session remaining. No new diagnostic run was started. External
cleanup verified0own fixture dirs/0agents; retained container STOPPED. All build
and source artifacts remain. Resume from STATUS and existing local
public-backend-20261025/checkpoint-20261025.json. First copy/rebuild/hash-check the
reviewed diagnostics, then run against original policy. A separately labelled
16char-keyid fixture may later measure supported behavior, but no such patch exists
yet; preserve fingerprint incompatibility and review exact changes before use.
No production route/API/parser/writer, migration, native OTP mutation, complete
save safety, resource-lifetime, Sailfish build or human security audit accepted.

## Public backend: confirmed policy gap and completed key-ID subset — 2026-10-25

After the checkpoint the maintainer instructed continuation. The already reviewed diagnostic
was copied/hash-verified and rebuilt. Original full-fingerprint policy diagnostic
returned exit1 at policy-validation: direct helper fingerprint lookup0, corresponding
key-ID lookup1;2public/1private keys loaded,0resolved policy records,1unresolved,
0recipient vector and0saves. This confirms the fingerprint compatibility issue:
the extra listKeys display-string filter excludes the fingerprint. This is not a
harness error; unchanged public reuse does not support this common pass policy
as exercised. No recipient-file migration or restriction was adopted.

A separately reviewed runner option `--policy-identifiers {fingerprints,keyids}`
keeps fingerprints as the default and explicitly reports the selected variant.
Only synthetic recipient-file values switch; backend sources remain unchanged.
The first key-ID run reached all normal policy checks and saves but a combined
negative check failed. The harness used allzero16hex as an absent key: pinned
[RNP KeyIDSearch::matches](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/lib/key-provider.cpp#L124)
treats that as a wildcard, so it was an invalid negative fixture, not evidence of
a public-save defect. That run and initial assertions are preserved.

The independently reviewed fixture correction uses a nonzero ID verified absent
from every generated primary/subkey ID and from helper lookup. It reports exception,
destination existence and original-ciphertext equality separately. Completed normal
runs can collect downstream oracles even if a check fails; false checks still make
the overall result fail. No assertion was relaxed and no backend patch was applied.

Final corrected key-ID run: exit0;16runner checks passed, all3native modes passed
(with2/12/3internal checks; these overlap runner summaries, not33independent tests),
41command records. Exact reviewed/current/copied identities:

- CPP36d3ebf7edba5c8008d3f51930324b6fce030d8fe087b60eb0e7638d18b4bb85;
- runner03fc86264202fb4a90189d8120cb67686802f5b29c371beb1e31cc8a840a9b02;
- final binaryfbd083c83b65686ec1f4aa824fe864eb1b02f59bb2b3330fdda39e623bab34cb.

| Measured public route | Result |
| --- | --- |
| Fresh unlock refusal | Password callback1,prompt1,save0; external original ciphertext unchanged |
| Existing path-only list/find | Matches fixture candidates; no unlock/decryption for enumeration |
| Selected entry decrypt | Exact original multiline content |
| Public save with root inheritance/nested override/multiple recipients | Four precomposed full-entry updates; policy vectors match fixture |
| Independent recovery | Five exact GPG reads across root/inherited/nested/multi, including each multi-recipient identity; nativeB independently reads nested+multi |
| Actual pinned pass-otp oracle | Native-saved root+nested entries produce RFC6238 SHA1@59 expected code through real GPG/pass-otp/OATH |
| Mixed valid/unresolved policy | Existing guard rejects before save; ciphertext preserved |
| Verified absent nonzero direct public save | Exception, destination exists, original ciphertext equal,0temporary leftovers |
| Conflicting nonempty directory destination | Rename exception; marker preserved;1adjacent ciphertext temporary remains; not an existing encrypted-file rename failure test |

Two state/cleanup caveats remain observed: after failed save the public object's
decrypted field already holds proposed new text; callers cannot infer persistence
from that cache. Rename conflict leaves a temporary despite source staging. The
own whole-fixture cleanup removed that leftover, not an accepted recovery policy.
Fingerprint lookup still reports0vs1key-ID in the final run. Native OTP parsing/
multiline URI mutation was not implemented: writes used precomposed text and the
OTP checks were external existing-code interoperability.

Independent reviewer checked all run boundaries, source/build/result identities,
fixture hashes/diffs and final results without crypto rerun. Original fullfingerprint
failures and wildcard-fixture failure stay intact. External final cleanup found
0own fixture directories and0agents; retained container STOPPED. Source/build files
remain under /home/ubuntu/public-backend-20261025; installed build prerequisites
remain there (54new/3updated,0removed over both approved installations). No reinstall
or broad repetition is needed in a later session.

Evidence in public-backend-20261025/: diagnostic-results/execution/build/loader,
keyid-results/execution (zero wildcard case), corrected-keyid-results/execution,
corrected-negative-build, source-first/, source-diagnostic-prepared/, keyid-runner.py,
source-corrected-negative/, final-independent-review.json and final-cleanup.json.
The earlier checkpoint is superseded by this result; STATUS carries current state.

Conclusion: existing public native backend code demonstrably supplies a useful
entry/policy/auth/write subset for the first OTP consumer; no new store/writer/API
was needed to measure it. It is not a drop-in pass replacement: fullfingerprint
policy remains a concrete integration gap. Before adoption, decide a separately
reviewed bounded correction/reuse scope for that gap and resource/error handling,
keeping the CLI baseline operational. No native product architecture, dependency
removal, OTP parser adoption, production migration, general save safety, concurrency/
crash/fsync guarantees, Sailfish build support or human security audit accepted.

## Bounded native-backend corrections executed — 2026-10-25

The maintainer authorized the complete proposal/review/implementation/regression sequence.
Owner: primary coordinator; separate Builder `builder`; scope/source/results
reviewer `save_review`. Current upstream default HEAD was queried first and remains
e53cd22c365ce170ebeaed70984207a8206d00eb (2026-05-25); no newer merged default-
branch correction was available to adopt. This is a dated observation, not a future
upstream support guarantee. Upstream state was not updated locally.

A research patch changes exactly2vendor files on a separate copied tree:

- RnpCoreBal.cpp retains its existing final locator predicate and also admits
  matches against the already fetched fingerprint. Canonical fullfingerprint
  lookup now works without dropping the old selector or adding UID/case policy.
- InterfacePassFile.cpp uses the existing UUID ciphertext staging; encrypt and
  rename are both inside its error path. Cleanup uses preconstructed path and
  nonthrowing error-code remove, then rethrows the original exception. Cache uses
  nonallocating string swap only after successful rename. A preflight rejects a
  preexisting generated temporary path before touching it; this is not atomic
  ownership/exclusive creation or a race-safety guarantee.

No new API/writer/framework, dependency change, software installation or unrelated
OTP/lifetime fix. Pristine archive/extracted sources remain byte-identical. Patch:
`tools/research/public_backend/corrections.patch`, SHA256
f85500e1865c774aaf8c1dfb4f46de911272ed93c404a78a921a562b79ffcd60.
First patch artifact had an incorrect final hunkcount from trimmed context;
independent read-only applycheck caught it before use. Invalid bytes are preserved;
only hunkcounts changed, then gitapplycheck passed before source gate.

The reviewed existing probe gained explicit `--expect-corrections` (default off).
It primes failed-save cache by real decrypt, tests success cache after save, requires
old cache on genuine absent-recipient failure, and requires unchanged cache and
0own temporaries after the directory-conflict rename error. Original oracles and
assertions were retained. Host/guest/test/source identities are recorded; a patch
hash in the runner report is only the expected artifact reference, so source-variant
metadata explicitly distinguishes the unpatched control from applied source.

The same new assertions were built against pristine backend for a meaningful
negative control: key-ID policy lets the operation sequence complete; exit1/fail
with exactly4native regression failures (fingerprint lookup, failed-save cache,
rename-conflict cache, rename cleanup). All existing GPG/nativeB/pass-otp/auth/policy
oracles still passed. This is expected failure evidence, not a passing correction.

Separately copied2file-patched backend configured/built successfully with existing
prepared dependencies. Fullfingerprints/default policy and correction expectations:
exit0,19runner checks and all3native modes passed;41commands recorded.

| Measured comparison | Pristine control | Patched fullfingerprint run |
| --- | --- | --- |
| Fingerprint vs key-ID helper lookup | 0vs1 | 1vs1 |
| Successful saves/cache + external recovery | Existing IO oracles pass | Cache matches saved input;5exact GPG reads,2nativeB reads and2real pass-otp codes pass |
| Genuine missing-recipient failure | Original ciphertext preserved but primed cache replaced by proposed text | Exception, original ciphertext and old primed cache preserved;0temporary leftovers |
| Conflicting nonempty-directory rename | Filesystem exception, cache changed,1temporary | Filesystem exception, cache unchanged,0temporary |

The last row remains an intentionally invalid directory destination; it is not a
rename-failure test over an existing encrypted file. Preexisting-path collision
branch and cleanup failure were source-reviewed but not runtime-exercised. Cleanup
is best effort; if removal is denied a temporary can remain. No retry/recovery,
concurrency, crash/fsync, key-lifetime or general save-safety guarantee follows.
No native OTP parser/mutation or Sailfish target acceptance has been added.

Exact reviewed probe CPPfbe01417f6efba09fdec2edbe22a52e8e4d5dee021c8b6a6b1ebe9206b7938e5;
runner2c29293535985ad370e4820984b5e9c42c8adf42762703727aa9cc62761ec508;
patched binary62a636d331d306aa7b136c844a11a78c6ad035339b608ef681284221553170ed.
Clean-env loader verification points to corrected-build RnpCore/RNP.1086original
archive files remain unchanged; only2factory-copy files differ as intended.
GPGME/Assuan dependencies remain; no built library was installed system-wide.

Evidence beside this feature: public-backend-corrections-20261025/ contains
upstream-check, patch-first-invalid.patch, patch-check, reviewed-sources/,
applied-inputs, control-build/results/execution, patched-configure/build/loader-
sources/results/execution, independent-review and final-cleanup records. Independent
review reconstructed the2filepatch and fixture diffs/hashes in memory, checked
source/build/result identities and comparison, without crypto rerun. No unresolved
evidence inconsistency. Assistant assessment is not a human security audit.

External cleanup verified0own fixture directories,0agents; container STOPPED and
retained. Original /home/ubuntu/public-backend-20261025 and separate corrected
/home/ubuntu/public-backend-corrections-20261025 source/build copies remain.
The three bounded observed gaps are corrected in this reviewable research patch;
production dependency adoption, repository/fork choice, platform build, broader
native lifetime and product integration remain maintainer decisions. No commit,
push, merge or publication. Existing CLI baseline and separate OTP append bug
are unchanged.

## Actual Sailfish SDK readiness and draft minimal build probe — 2026-10-25

User requested steps1(actual compiler/library availability check) and2(preparation
of the smallest build experiment). Primary coordinator owns the work. Only known
SDK metadata was queried; no compiler input, CMake configure/build, test execution,
package installation, repository refresh or device operation. Existing SDK
container was already running and remains so; the separate Ubuntu research
container was not started. An initial sfdk query from login home failed because
build-shell needs an existing build context. The successful read-only queries used
existing /home/ubuntu/gnupg-runtime solely as sfdk context, without source changes
or build-init. This failure and both query scripts/raw results are preserved.

### Observed target and gaps

Actual SDK3.13.5 target SailfishOS-5.1.0.11-aarch64, not an inferred device or5.2
sysroot. Compiler reports aarch64-meego-linux-gnu GCC13.4.0; target libstdc++13.4.0
is installed. Actual help advertises C++17/C++20/gnu++20 options. This is version/
option evidence, not successful C++20 compilation, complete language/library support
or Botan build acceptance. [GCC's implementation table](https://gcc.gnu.org/projects/cxx-status.html)
was checked as context; target compiler/library behavior still needs the proposed
compile/link probe. CMake3.31.8 exceeds pinned RNP minimum3.18 and sexpp minimum3.14.

| Component | Actual SDK evidence | Readiness implication |
| --- | --- | --- |
| Compiler/CMake | GCC13.4 cross target aarch64; CMake3.31.8; Make4.4.1 | No version-age blocker established; compiler/link tests not run. Toolchain provides cross-search paths; absent target libstdc++-devel RPM is not proof its toolchain headers are absent. |
| OpenSSL | openssl-devel/libs3.5.6+git1-1.14.1.jolla, headers/libcrypto.so/CMake config/pkg-config3.5.6 present | Maintained RNP OpenSSL backend(min1.1.1) is a credible lower-dependency first probe. Missing openssl executable is not missing library. |
| Botan | No queried Botan2/3 package or pkg-config module installed; none in cached package search | Previous Ubuntu Botan3 choice/C++20 is not a product requirement. A Botan route would need separately scoped dependency work. |
| sexpp | Not installed or found in cached package search | Use RNP's existing bundled static-submodule facility in draft first probe, with exact gitlink pin; not a new vendoring framework. System mode remains an alternative if package evidence changes. |
| GPGMEpp | No installed package, gpgme++/context.h, GpgmeppConfig.cmake or cached candidate | Current unchanged public backend's required CMake dependency is unresolved; first engine probe does not solve that gate. |
| GPGME C | gpgme-devel/runtime1.2.0+git9-1.8.2.jolla; gpgme-config1.2.0; gpgme.h and Clibrary symlinks present | Missing .pc is not missing devel. Old Cinterface does not supply GPGMEpp; do not replace stock GPGME/GnuPG to fit the experiment. |
| Other development inputs | libgpg-error-devel1.42,zlib-devel1.3.1 present; JSON-C0.18/bzip2libs1.0.8 runtime present but respective headers absent | Cached json-c-devel0.18+git1-1.5.2.jolla and bzip2-devel1.0.8+git3-1.7.2.jolla exist. Installation was not authorized/executed. GPGMEpp version-specific libgpg-error requirements remain separate. |

Repository searches used --no-refresh across existing adaptation-common/apps/
customer-jolla/hotfixes/jolla/sdk only. Solv snapshots date2026-06-30; installed
cache2026-10-14. Absence there does not establish current5.2/community availability.
No refresh, source update, repository addition or package change occurred.

Actual platform facility inspected: installed /etc/rpm/macros.cmake sets standard
Sailfish flags, aarch64 target/lib64 and shared libraries; default is in-source
CMake and build macro currently expands to-j32. Inspecting macro output did not
execute it. Future use must operate on a disposable source copy, not preserved
archives or the existing GnuPG tree. Container has about1006MiB free/95%used; assess
space for the chosen scratch build first. No arbitrary minimum or automatic cleanup
is imposed; do not delete prior evidence or install tooling merely for this draft.

### Prepared minimal probe (revised after independent review; not executed)

Initial independent scope advice challenged treating Botan3 as mandatory and
separated RNP engine readiness from public backend readiness. After an initial
service usage limit, the reviewer resumed at the maintainer's explicit request and assessed
the inventory and plan. Inventory is supported; one material scope correction was
identified and incorporated below: OpenSSL configuration builds AND RUNS a feature
helper, so this is not a compile/link-only build. No execution has occurred.
The concept remains conditional on complete source/package/scratch-recipe review
and separately scoped authorization before later execution.

1. After independent review and any separately approved SDK package changes,
   prepare one owned SDK scratch build using standard sfdk/RPM build facilities.
   Preserve all current target packages; do not replace GPGME, GnuPG or OpenSSL.
   Revalidate exact target/tool versions, free space and cached package identities.
   Missing json-c-devel and bzip2-devel are concrete prerequisites; obtain a pinned
   dependency/transaction proposal before any installation. No update/refresh implied.
2. Stage existing pinned RNP0.18.1 commit
   aad1892e4d8423398a0b973bd0a7e4544c359afc and its actual src/libsexpp gitlink
   c641a2f36520bab783657a58650d9fda548b9dec from rnpgp/sexpp. No tag/latest
   substitution. RNP default SYSTEM_LIBSEXPP=OFF already builds that submodule
   statically with CLI/tests off. Inspected sexpp CMake uses CMake>=3.14 and
   cxx_std_11 for its library, includes cmake/version.cmake; ensure complete pinned
   source/version inputs exist before configuration. Stage outside unrelated Git
   ancestry so version detection cannot pick up the GnuPG/workspace repository.
   Full sexpp archive/hash intake
   remains future work; only its exact pinned CMake metadata was fetched this round.
3. First compile/link-only smoke inputs should check actual C++17 filesystem;
   optional C++20 concepts/span input documents that mode if keeping Botan3 as
   an alternative. Verify AArch64 ELF and toolchain paths, not host compiler output.
   These inputs have NOT been compiled. A smoke result would not prove Botan3.
4. Configure/build ONLY upstream librnp using OpenSSL and upstream sexpp mechanism.
   This narrows the first build to cryptographic-engine feasibility; it does not
   remove GPGMEpp from libpgpfactory or establish the complete public backend.
   Use actual RPM %cmake with the standard options below inside a scratch %build
   context; use existing cmake target selection, no custom cross-toolchain/provider
   shim. Macro is in-source, so the source must be a disposable verified copy.

   Important reviewed scope: pinned cmake/Modules/FindOpenSSLFeatures.cmake writes
   a nested C99 project, configures/builds findopensslfeatures, then directly
   executes it for hashes, ciphers, curves, publickey and providers. Target-only
   build/BUILD_TESTING=OFF does not prevent that configure-time source execution.
   Any later authorization/recipe must explicitly cover this normal upstream
   helper and verify SDK target-execution handling and selected OpenSSL instance.
   Record helper ELF architecture, linked library provenance, commands/results
   and feature output; reject host-library feature inference. The module invokes
   the helper directly, so do not assume a generic CMake emulator variable alone
   makes it work. Use actual existing SDK facilities; stop for review if they do
   not suffice. Do not fake feature answers, bypass detection, silently weaken
   algorithm settings or introduce a custom execution shim.

   Proposed RPM build-body excerpt (not an executed command or complete release spec):

   ```spec
   %global _smp_mflags -j1
   %build
   %cmake -DCRYPTO_BACKEND=openssl \
       -DSYSTEM_LIBSEXPP=OFF \
       -DBUILD_TESTING=OFF -DDOWNLOAD_GTEST=OFF \
       -DENABLE_DOC=Off \
       -DFETCHCONTENT_FULLY_DISCONNECTED=ON \
       -DFETCHCONTENT_UPDATES_DISCONNECTED=ON
   cmake --build . --target librnp --parallel 1
   ```

   Explicit low parallelism is a resource choice for this measured SDK/container,
   not a new project requirement. Do not evaluate %cmake's raw --eval output as a
   shell script: it contains spec-preprocessor conditionals. Use RPM facilities
   in an independently reviewed scratch recipe. No %install, system ldconfig, RPM
   installation, RNP CLI execution or device deployment is part of this first
   probe. The configure-time OpenSSL helper execution described above IS part of
   the proposed build and must be included in any later approved scope.
5. Acceptance for that later build: captured configure/compiler/link status and
   logs, recorded source/dependency hashes/versions, AArch64 ELF, correct SONAME/
   NEEDED against target OpenSSL3 and expected target libraries, no host artifacts
   or unplanned fetch. Stop on unsupported features/dependency failures instead
   of silently relaxing crypto settings. Building OpenSSL-backed RNP does not
   inherit Ubuntu Botan-backed crypto acceptance; any later synthetic runtime
   check is a separate reviewed step. No tests currently passed/unexecuted as passed.

Public backend phase remains a separate gate: choose a justified compatible
GPGMEpp/dependency route or explicitly review another adaptation, without silently
removing the native library's requirements or replacing stock Jolla dependencies.
No such architecture change is accepted by this draft. It is currently premature
to promise an unchanged full native-backend Sailfish build.

Evidence: existing feature sailfish-sdk-readiness-20261025/ contains inventory/
metadata/platform query source and raw outputs, sdk-inventory.json, sdk-metadata.json,
sdk-platform-facilities.json, compiler-language-help.json, pinned sexpp-CMakeLists
metadata and readiness-summary.json. Initial query-context failure is retained.
Steps1and2 prepared; independent review resumed and its material helper-execution
finding is incorporated. No build/install/runtime authorization is implied.
Complete scratch-recipe/source review and package-transaction approval remain
future execution gates; see independent-review.json for final review disposition.

Independent final wording check completed: the reviewer confirmed the helper-
execution correction resolves the material finding and found no unresolved issue
in the inventory/revised concept within preparation scope. Complete source intake,
full scratch recipe review, package-transaction approval and explicit execution
authorization remain future gates. No configure, build, helper execution or
installation performed during this review.

## Completed SDK engine build — 2026-10-25

RNP 0.18.1 successfully built as an AArch64 shared library with SDK 3.13.5,
SailfishOS-5.1.0.11-aarch64, GCC 13.4.0 and target OpenSSL 3.5.6. Owner: root;
Builder: builder; separate reviewer: save_review. Final results review pending.
Pinned RNP aad1892e and bundled sexpp c641a2f3; all 1,089 original source files
match their archives. Final spec SHA256:
736d58c309c3c6ae0bce57468a508f91f8a79f6da3fc26b5b84258f825d501de.

Upstream findopensslfeatures actually compiled and ran for all five categories;
21 hashes, 137 ciphers, 39 curves, 74 publickey entries and 2 providers reported.
Helper and librnp both have AArch64 ELF machine 183. librnp SONAME is librnp.so.0;
NEEDED includes libcrypto.so.3, libjson-c.so.5, libbz2.so.1 and libz.so.1.
Target libcrypto package/hash and compiler/link/cache/feature trace are retained.
Library SHA256: 61896370e630ba0b0327d7193651336e97180bb30c9d14da38aa695531c07fc8.
Artifact: /home/ubuntu/rnp-sdk-probe-20261025-r2/BUILD/rnp-sdk-probe-0.18.1/src/lib/librnp.so.0.18.1
inside local:sailfish-sdk. Evidence: .local-artifacts/pass-rnp-slice-20261024/
sailfish-sdk-readiness-20261025/{sdk-build-r2,sdk-build-artifacts,
sdk-target-crypto-and-packages}.json and sdk-build-r2.log.

Scoped approved SDK additions: json-c-devel, bzip2-devel, git-core, less, openssh
and openssh-clients; six new packages, no upgrade/removal/repository refresh.
Existing NOKEY warnings retained; no signature-policy change or authentication
claim. First scratch attempt stalled in upstream version discovery without Git;
exact cached git-core resolves that observed SDK issue without a source patch.
Original attempt and diagnosis preserved; Git is a build workaround, not an app
runtime requirement. Successful rpmbuild -bc exit 0 used fresh scratch r2.

This completes engine build feasibility only. No produced library installation,
RPM packaging, device action or cryptographic runtime test occurred. Full public
backend still needs its GPGMEpp dependency resolved; no product integration or
new service/API is adopted. Existing SDK remains running as found; separate
Ubuntu probe remains stopped. Local dirty changes are preserved.

## SDK result review and full-backend API investigation — 2026-11-01

Owner: primary coordinator (root). Required independent reviewer: sdk_review.
Bounded scope: assess retained SDK engine build results, then inspect the pinned
factory's existing dependency surface against the actual SDK. Acceptance: resolve
pending result assessment, identify concrete API gaps before any build adaptation,
and retain limitations. No new installation/build/device scope is authorized.

Separate assistant result review supports the bounded RNP engine build-feasibility
claim, with no material evidence inconsistency. Reviewer independently recomputed
the spec hash, checked build log/archive identities, helper execution and counts,
AArch64 artifact metadata and target OpenSSL evidence. The 1,089-file original-source
comparison was assessed from the retained record, not independently repeated live.
This is not a human security audit, runtime acceptance or release approval.
The probe document's stale opening is corrected to distinguish preparation from
completed execution. Earlier approval/invocation text is historical.

Pinned factory e53cd22c source inspection finds Gpgmepp required/linked on UNIX,
but no gpgme++ includes or GpgME:: references in its C/C++ sources. Its GPG branch
uses the C API. Existing RNP classes and shared store logic already exist; no new
backend/service framework is justified by this dependency question.

Read-only SDK header inspection on 2026-11-01 confirms GPGME_VERSION 1.2.0.
Of 51 distinct gpgme_* source tokens, only gpgme_op_keysign is absent from that
header. libpgpfactory.cpp:224 calls it unconditionally in trustPublicKey, also
reachable through importPublicKey(doTrust). Thus changing only CMake to link
GPGME C directly does not make the unchanged full backend buildable. Installing
a C++ wrapper alone would not demonstrate resolving that missing C API either.
Token presence is not proof of full API/structure-field/link compatibility.

The independent reviewer supports inspecting direct C linkage as the simpler
conditional candidate, but requires checking actual API compatibility first.
Any later full-backend probe must link an executable consumer, since building
only a static archive can conceal unresolved symbols. Do not stub trust/import,
drop GPG sources, spoof the OS or describe an RNP-only subset as the full backend.

Library-symbol inspection remains incomplete: guessed target usr/lib64 and
usr/lib paths did not contain libgpgme.so. This is not evidence of an absent
library; earlier package evidence lists /usr/lib64 in the actual target build
context. No target execution, configure, build, installation, refresh or device
action occurred. Header/token evidence is retained in the existing SDK evidence
directory as gpgme-api-investigation-20261101.json.

Next research: locate actual target library context and audit required API/fields;
compare maintaining a small explicit RNP-only build option using existing classes
against providing a compatible isolated GPGME stack. A feature/architecture choice
requires separate scope review and maintainer agreement before implementation;
neither option is adopted here. Preserve existing local work and source pins.

## Optional existing-backend RNP-only experiment — 2026-11-01

Owner: root; required independent scope/source/results reviewer: sdk_review.
Maintainer directed continuation of the optional RNP-only route. Bounded scope:
a downstream research patch retaining existing RNP classes, common store logic
and public API, with GnuPG build support optional. Acceptance: exactly two vendor
files, apply to pinned original and separately corrected tree, default OFF retains
existing platform behavior, explicit GPG selection refusal before singleton lookup,
RNP unlock callback preserved. No product adoption or new dependency decision.

Separate scope review found a callback regression in the initial branch concept;
the prepared patch instead adds an explicit RNP_ONLY branch assigning the existing
callback, and preserves the historical platform branches. This resolves that
preimplementation finding. Existing upstream RNP classes already supply the
implementation; adding a small build option has less immediate scope than adding
a compatible GPGME stack just to compile an unused backend. It still incurs a
downstream patch maintenance cost and remains an experiment.

Artifact: tools/research/public_backend/rnp-only.patch, against factory e53cd22c.
LIBPGPFACTORY_RNP_ONLY defaults OFF. ON skips UNIX GPG dependency discovery,
GPG-only source additions and GPG linking, and defines a private compile macro.
It throws invalid_argument on an explicit GPG request, before singleton access.
No stubs, OS spoofing, new factory, parser or source extraction. Existing
corrections.patch stays separate and is needed for the prior save regressions.

Initial pristine git apply --check passed. Corrected-tree apply/source review and
compile/link evidence remain pending. The host has neither CMake nor a C++
compiler; no host installation is proposed. An eventual SDK probe must link the
public harness executable, inspect ELF dependencies and preserve the pinned
OpenSSL/bundled-sexpp recipe. A static archive alone cannot establish successful
linkage. No build, crypto execution, SDK/device/package change occurred here.

## Executed optional RNP-only SDK executable build — 2026-11-01

Owner: root; separate scope/source/recipe/results reviewer: sdk_review.
The preceding preparation-only checkpoint is superseded by this result.
Maintainer continued the RNP-only route; scoped outside-sandbox tool approvals
covered artifact writes, staging, upstream OpenSSL helper execution and SDK build.

Outcome: SDK3.13.5 / SailfishOS-5.1.0.11-aarch64 compiled and linked the existing
public_backend_probe executable against the optional existing RNP backend.
Fresh r2 rpmbuild -bc exited0 in169.24s. No produced artifact was installed.
RNP0.18.1 aad1892e, sexpp c641a2f3, factory e53cd22c remain pinned. The original
corrections.patch is unchanged; rnp-only.patch changes exactly two additional
vendor files. Default-OFF behavior is preserved by source review, not a new
executed default build. ON callback propagation and selection refusal are source
reviewed/compiled, not runtime-tested.

Final recipe SHA256:
aaa943827f0b9a60dd02baac0956ebaa3b72173253224cc617089a45200be9f4.
RNP-only patch SHA256:
d3540aa9d212dbd86893a40690eb5c16f06cd810a85e43c5cfc48bcf8abaf235.
SDK driver SHA256:
b6ba050d5c1c28b7a75eb6c348cece0f5e7eff673675af9a4d54b307ba8fb46e.
Executable SHA256:
93b42f99b3be172d6659bb1bbee4952ea6db81a44261e3402ffb6472476585a9.

All eight staged input identities verified before execution. Comparison against
original archives plus the two reviewed patches checked1,154 original files with
zero mismatches; exactly four factory files differ from original. The reviewer
independently reconstructed those four modified files and matched their hashes;
the broader audit was reviewed as retained evidence, not repeated live.

Executable, RnpCore, librnp and upstream findopensslfeatures helper are AArch64.
Actual helper configure/build and five category executions all returned0; feature
counts21hashes/137ciphers/39curves/74publickey/2providers. Cache selects OpenSSL3.5.6,
bundled sexpp and local pinned RNP. Twelve objects in the recursive static
DT_NEEDED closure resolve with no GPGME/Assuan entries; actual target libcrypto
hash matches the earlier engine probe. This is static dependency evidence, not
loader verification or coverage of dlopen/provider behavior.

The first attempt failed in preparation: GNU patch --fuzz=0 applied one correction
file and rejected the RnpCoreBal hunk. No configure/build ran in that attempt.
Exact cause remains unestablished. Its partial tree/log are preserved.
Separately reviewed recipe correction uses the already required Git tool for
git apply --check followed by git apply; no fuzz/whitespace relaxation or patch
byte change. Fresh r2 preserves the failed attempt. Actual target GNU patch2.7.6
was present. Sandbox snap-confine errors in read-only preflight were resolved by
approved outside-sandbox invocation, without security configuration changes.

Evidence in existing sailfish-sdk-readiness-20261025/:
rnp-only-{staging,staging-r2,sdk-build,sdk-build-r2}-20261101.json and build logs,
rnp-only-sdk-artifacts-20261101.json,
rnp-only-target-dependencies-20261101.json, and final review record.
Scratch /home/ubuntu/pass-rnp-only-sdk-probe-20261101-r2/BUILD/
pass-rnp-only-sdk-probe-0.18.1 inside local:sailfish-sdk; failed first scratch
retained beside it.732MiB free afterward; no deletion or package change.

Separate assistant final review found no material unresolved evidence inconsistency.
It is not a human security audit or release approval. Sixteen compiler warnings
remain in the log; no runtime correctness conclusion follows from build success.
Build-tree RPATHs, including RnpCore's trailing empty component, are not accepted
for distribution. No public-harness/selection/callback/crypto runtime test,
installation, RPM creation, device action or package-isolation acceptance occurred.
Existing native lifetime concerns, OTP append bug and broader behavior stay open.

Next: separately scope/review a synthetic runtime experiment of the built backend
and explicit selection/callback behavior; reuse prior fixtures and existing API.
No new backend service, app integration, repository, dependency installation or
publication is adopted. Preserve all existing uncommitted work.

## SDK/LXC-only synthetic runtime scope — 2026-11-01

Owner: root; required separate scope/source/recipe/results reviewer: runtime_review.
Maintainer authorized continuation and explicitly confirmed all experiment execution
stays inside existing SDK/LXC. Host activity is limited to research sources and
evidence files. No device, host installation, package addition or security changes.

Objective: exercise existing public RNP backend with synthetic fixtures in actual
Sailfish build-shell; acceptance: demonstrate intended library loading, existing
refuse/normal/read-b modes and independent GPG byte oracles, missing-recipient and
directory-conflict preservation/cache regressions, explicit disabled-GPG selection
before and after RNP selection, preserved original artifacts, isolated fixture
homes and cleanup. No OTP/runtime lifetime/crash/concurrency/package acceptance.

Read-only inventory: target UID1000, Python3.11.15, gpg absent, rnpkeys absent,
oathtool absent, gpgconf2.0.4, bash5.0.18. Ubuntu side of the SAME SDK LXC has
UID1000, Python3.14.4, GPG/gpgconf2.4.8; rnpkeys/oathtool absent.732MiB free.
The original Ubuntu research container is not needed and remains untouched.

Existing pinned FfiRaII detects/loads GPG pubring.gpg and secring.gpg; rnpkeys was
only a fixture import convenience. Proposed explicit SDK runner profile reuses
GPG-generated protected synthetic exports directly in those rings, native cases
through sfdk build-shell, and Ubuntu-side GPG for byte comparisons. Missing oath
means actual pass-otp code oracle explicitly unexecuted here, not replaced.
Default historical runner requirements remain unchanged. The runtime fixture
extension and concrete build/launch recipe require separate review before use.

## Executed SDK/LXC synthetic runtime probe — 2026-11-01

Owner: root; separate scope/source/recipe/results reviewer: runtime_review.
The preceding preparation checkpoint is superseded. Maintainer authorized the
runtime step and explicitly retained the SDK/LXC-only execution boundary.
All cryptographic fixture activity occurred in existing local:sailfish-sdk:
Ubuntu GPG2.4.8 generated/tested synthetic data; the AArch64 backend ran via the
SailfishOS-5.1.0.11-aarch64 build-shell of SDK3.13.5. No host crypto execution,
device action, package addition, installation or security change occurred.

Result: first runtime execution exited0 in19.25s. All20runner checks passed;
four native modes passed: disabled-GPG selection3checks, fresh refusal2,
normal22, independent-B3. Their summaries overlap runner checks; do not sum them
as independent cases. Exact GPG plaintext oracles passed for five recipient/file
combinations; independent B read two entries. Full-fingerprint lookup and root,
inherited, nested and multiple-recipient policies passed.

Existing native keyring loading accepts protected synthetic GPG export packets
directly in pubring.gpg/secring.gpg. No rnpkeys installation/build was needed.
Missing oathtool means actual pass-otp code oracle explicitly unexecuted; no
replacement OTP implementation was added. OTP URI/notes are unchanged byte
payload fixtures, not native OTP parsing/mutation acceptance.

Actual loader listing resolved the intended original build-tree RnpCore/librnp
and target libraries. Each native launch used verified artifact hashes, a clean
explicit environment, target-side password FD and a controlled temporary working
directory. The distinct sfdk infrastructure HOME only serves SDK configuration;
native/GPG HOME and GNUPGHOME stay within the synthetic fixture. Source/recipe
review required exact SDK release and explicit known project/no-session context.

Fresh refusal recorded1password callback,1login prompt and0save calls; external
ciphertext preservation passed. Successful native reads record password callbacks
without refusal prompts. Missing-recipient failure preserved original ciphertext
and primed old cache, with0own leftovers. Directory conflict reported an error,
kept cache empty and left0own temporary. That directory case is not replacement
failure over an existing encrypted file or arbitrary post-encryption cancellation.

The fixture-only build exited0 in5.66s and linked actual original backend
artifacts without rebuilding vendor code or replacing the prior executable.
New public_backend_sdk_probe SHA256:
373d7013279533ab1fca1e95403523856d2e658488a0fce32d9390e06fccff85.
Reviewed runner:
3b3ecbca1bb64d80a947d5dd5a8d7c5aeaedc128b56715e8189f76fdc0329a8f.
Reviewed probe source:
857e0a1eb5bfad71e7923d68f5e54ddb383cc4f4dab91cc12b274857252f7a72.
Reviewed launcher:
c0976be4bf4a1d8c8c01b574a32c5287844ce9199b6390f05b5ec70470026d61.
Fixture spec:
3f495a4493313360705b6b2bb071c81f307362f0316231fbd00f0a67fc329361.

Ten staged inputs and four original artifacts verified before build; target
manifest verifies15identities before native launches and all15 match postrun.
External postrun evidence records0fixture directories and0matching fixture
GPG-agents; own cleanup succeeded and outer stderr is empty.723MiB free afterward.
SDK and retained build artifacts remain available; the other research LXC was
untouched. Synthetic homes/keys/store were removed, not retained as artifacts.

Evidence remains in sailfish-sdk-readiness-20261025/:
sdk-runtime-{staging,build,build-artifacts,first,first-execution,postrun}-20261101.json,
sdk-runtime-build-20261101.log, sdk-runtime-first-20261101.stderr,
sdk-runtime-reviewed-source-20261101/ and final-independent review record.
Fixture build/controller retained inside SDK at /home/ubuntu/rnp-sdk-runtime-20261101;
only its temporary sailfish-public-backend-* homes/store were cleaned.

Separate final reviewer independently checked the retained reviewed-source hashes,
build/ELF identity, per-mode results, oracles, loader and postrun records. No material
unresolved evidence inconsistency found. Reviewer assessed recorded execution/
cleanup rather than rerunning crypto or repeating live cleanup. This is separate
assistant assessment, not human security audit or release approval.

Limits: only explicit SDK profile executed; historical default runner path was
source-preserved but not rerun. No native-hardware/device, general native lifetime,
crash/concurrency/fsync, all provider/dlopen, package isolation or distribution
acceptance. Existing build-tree RPATHs remain research-only. The known OTP append
baseline bug is unchanged. No product backend/API/service/repository adoption.

Next: maintainer can assess reuse based on demonstrated build and bounded runtime
feasibility. Before product adoption, separately scope existing native resource/
error-lifetime gaps and the OTP consumer slice using pinned upstream/platform
behavior; do not invent a service framework or assume complete pass compatibility.
Preserve all local uncommitted work.

## Closing assessment scope — 2026-11-01

Owner: root; required separate reviewer: runtime_review; decision owner: the maintainer.
Maintainer asked to continue but bring this feasibility study to an end.
Bounded objective: one source-based assessment of native ownership/error lifetime
in the tested entry IO path and fit for the intended OTP consumer, then a concrete
reuse recommendation and explicit research closure. Acceptance: cite pinned
upstream ownership contracts and candidate call sites, distinguish demonstrated
feasibility from product blockers, challenge simpler reuse/maintenance alternatives,
and identify only necessary subsequent product work. No new crypto test, code
patch, installation, container/device action or architecture adoption in this step.
Existing study and STATUS remain the single artifact/handoff set.

## Closing source assessment and reuse decision proposal — 2026-11-01

Research owner: root. Separate closing reviewer: runtime_review. Decision owner:
the maintainer. Feasibility-study acceptance is met; research is closed at this checkpoint.
This is a recommendation for the next product decision, not architecture adoption,
a human security audit or release approval. No new experiment or runtime change
was necessary to establish this conclusion.

**Recommendation:** use the demonstrated RNP0.18.1/OpenSSL direction for the next
bounded product implementation. Retain the tested libpgpfactory store/entry/policy
subset, reviewed corrections.patch, RNP-only option and synthetic fixtures as the
reuse basis. Do not adopt the entire pinned backend as product-ready unchanged.
Correct its concrete ownership/error handling before long-running app use; decide
the maintained subset in that implementation scope. A new crypto engine, generic
GPG emulator, store/service framework or daemon is not justified by these findings.
Existing pass/OTP remains the operational baseline.

### Evidence sufficient to close this study

| Research question | Established result / boundary |
| --- | --- |
| Can RNP build on the actual Sailfish target? | Pinned upstream RNP/sexpp with the existing OpenSSL backend builds as AArch64 using standard SDK/RPM facilities. |
| Can existing native backend code run without GPGME? | The optional RNP-only two-file patch builds and runs the existing public entry/policy interfaces; actual loader evidence resolves the intended libraries without GPGME/Assuan in the inspected chain. |
| Does representative pass-format entry IO interoperate? | SDK synthetic full-fingerprint policy, recipient variants, exact GPG recovery, callbacks/refusal and bounded save/cache errors pass; earlier Linux pass-otp code oracles remain separately scoped evidence. |
| Is the candidate a ready-made OTP app backend? | Whole-entry crypto/store IO is demonstrated. App ownership/unlock lifetime and native OTP interpretation/editing remain product implementation, not demonstrated full pass/OTP equivalence. |
| Must more open-ended feasibility research precede a product decision? | No. Specific implementation gaps are identified below; release/device/distribution evidence belongs to the later product stage. |

### Concrete product gaps from pinned source

Findings are source-based; they are not newly observed exploits, memory-growth
measurements or a claim that the passing synthetic results were invalid.

1. **Own and release native resources on every path.** In factory e53cd22c,
   [FfiRaII.h:14](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/RnpCore/FfiRaII.h#L14)
   leaves rnp_ffi_destroy commented out. In
   [RnpCoreBal.cpp:123](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/RnpCore/RnpCoreBal.cpp#L123)
   the verification operation is not destroyed; line146 replaces the live callback
   output handle with a new memory output. Encryption's destroy at line267 is
   bypassed by preceding exceptions. listKeys/getPrimaryKey retain raw search
   handles, including early-return paths. These are ordinary read/list/error paths
   relevant to a repeatedly used OTP app, not just optional bulk features.
2. **Surface initialization and callback failures.**
   [FfiRaII.cpp:189](https://github.com/shemeshg/gpgme-cmake-example/blob/e53cd22c365ce170ebeaed70984207a8206d00eb/libpgpfactory/RnpCore/FfiRaII.cpp#L189)
   returns silently on initialization failures and ignores keyring/provider setup
   results. The password provider ignores key-ID lookup failure and uses strncpy
   without guaranteeing a terminating NUL for an overlong supplied password
   (lines29–38). RNP's pinned callback contract requires a NUL-terminated result.
   Successful/refusing short fixture passwords do not cover these paths.
3. **Make app session ownership/unlock lifetime deliberate.** The existing
   InterfacePassHelper singleton retains the first home/backend/callback and has
   no explicit public reset/lock operation. InterfacePassFile retains plaintext
   in std::string; process-exit-bounded tests do not establish an app's locking or
   clearing behavior. Resolve ownership using ordinary object lifetime and the
   existing library contracts, not a new service/lifecycle framework.
4. **Implement the selected OTP consumer behavior using existing references.**
   The tested backend reads/writes complete entries; it does not locate/edit one
   otpauth URI among notes or calculate codes itself. Pinned pass-otp/OATH supplies
   the existing functional baseline (including the separately recorded append
   decrypt-status defect). Inspected QtTotp code is a reuse candidate, not an
   adopted dependency: it clamps settings and defaults unknown algorithms, and its
   actual Sailfish compatibility/selected source terms were not established.
   Supported OTP types/validation are a product choice; those candidate defaults
   must not silently become requirements. No new OTP parser was created here.

Upstream already supplies the required ownership mechanism:
[RNP0.18.1 header](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/include/rnp/rnp.h)
documents rnp_op_verify_destroy and handle cleanup; the corresponding
[src/examples/verify.c](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/examples/verify.c#L153)
and [encrypt.c](https://github.com/rnpgp/rnp/blob/aad1892e4d8423398a0b973bd0a7e4544c359afc/src/examples/encrypt.c#L119)
use common cleanup paths. Pinned rnp.cpp:2254 directly allocates a new output in
rnp_output_to_memory; it does not release a pre-existing supplied handle. The
candidate's rnpcpp.hpp also has owning FFI/Key wrappers. A small reviewed cleanup/
error patch can therefore use existing native facilities/ordinary C++ ownership.
No measured total-maintenance-cost advantage or fixed correction effort is claimed.

### Closing review and handoff

Separate reviewer runtime_review independently reached the same conclusion:
RNP is viable for this intended consumer; candidate code is useful reuse material
and a demonstrated prototype, with concrete product ownership/error/OTP gaps.
The reviewer checked simpler upstream facilities and did not require device or
release checks to finish research. There is no unresolved blocker to closing this
feasibility study; the findings above are implementation prerequisites before
claiming product readiness. Source identities and reviewer disposition are retained
beside existing evidence as study-closing-assessment-20261101.json.

Next decision: the maintainer reviews this recommendation and chooses the bounded product
implementation scope. No additional research experiment is queued automatically.
No new repository/API/service architecture, package install, device/system change,
commit, push, merge or publication was performed/authorized by this closure.
All existing source changes and evidence remain local and preserved.

## Secrets/RNP plugin implementation-quality review scope — 2026-11-01

Owner: root; required separate security/source reviewer: runtime_review.
Maintainer requested critical code-quality, best-practice, style and security
review of existing dcaliste Secrets/RNP plugin as implementation candidate.
Bounded scope: pinned Secrets plugin, shared RNP helper, build/RPM metadata and
actual relevant Sailfish/RNP contracts. QMF/mail behavior is not a full audit
target; note build coupling only. Acceptance: prioritized reproducible source
findings with line/version evidence, distinguish confirmed defects from platform
unknowns/style, challenge unnecessary mechanisms, and give concrete reuse/fix
advice. Static review only; no plugin activation/build/install, real secrets,
device/OS mutation or publication. Closed engine feasibility study stays closed.

## Secrets/RNP plugin quality and security review — 2026-11-01

Owner: root. Separate security/source reviewer: runtime_review. Maintainer agreed
to develop the Secrets/RNP integration direction and requested a critical source
review before implementation. The engine feasibility study remains closed.
This assessment concerns the proposed integration code, not a new engine study.

**Verdict:** useful native integration proof of concept; unsuitable for unchanged
product adoption or activation with real keyrings. Keep its platform integration
and native RNP approach, but correct the P1 groups below before product use.
This does not justify rewriting the cryptographic engine or creating a service.
Explicitly unsupported optional APIs may stay unsupported; they must fail honestly.

### Inputs and method

- Candidate: dcaliste/sailfish-crypto-plugins, commit
  effb3a471738fddf221bc68136bb9789011b2355 (2026-09-03).
  Retained archive SHA256:
  c398c529f76a6f2ceb8c1d7c37231bab36c58d413b9269e935fa01b14d8bf921.
  Seventeen source/metadata files were safely retained and hash-checked.
- Contracts: retained pinned RNP0.18.1 aad1892e header and implementation; local
  Sailfish Secrets adaptation 3e79aaec2092ecc1ddd449d36b9ebc2bd724713b,
  clean working tree during review. This is not proof that a device daemon has
  precisely that source/build.
- Scope: Secrets plugin, shared RNP helper and build/RPM metadata. QMF is noted
  for build coupling; mail behavior was not comprehensively audited.
- Validation: source tracing, native/platform contract checks and separate assistant
  assessment. No plugin build, activation, crypto/key operation, device action,
  software install, exploit demonstration, fuzzing or dynamic analyzer run.

Priority P1 means correct before enabling the affected product behavior; P2 means
a concrete correctness/security-hardening/maintenance issue to address in the
selected implementation. These are review priorities, not CVSS/exploit ratings.

### P1-01 — Stored-key references are not bound to the actual decrypt operation

Locations: secrets/rnp/rnpffi.cpp:680–686; rnp/rnp.cpp:655,444–500.
The plugin checks the requested key's plugin name, then calls decrypt against
the whole loaded secret keyring. The requested identifier is not used to
restrict the actual recipient. It is also used later as signer-matching metadata,
which is distinct from selecting the decryption key.

toCryptoKey puts the literal marker "Rnp" in privateKey. In the inspected platform,
cryptorequestprocessor.cpp:1956–2035 distinguishes a stored-key reference from
supplied key material using whether privateKey/secretKey are empty. Nonempty
components take the full-key path, skipping the stored-key useKeyPreCheck; the
wrapper's decrypt path similarly skips collection unlock for supplied components.
The plugin nevertheless ignores those bytes and uses stored private keys.
DecryptRequest's documented key contract identifies the key requested for use.

Consequently, metadata for key A need not constrain a ciphertext for key B, and
a fabricated nonempty component can be interpreted differently by daemon and
plugin. This is a concrete confused-deputy/integration-boundary mismatch, not a
demonstrated unauthorized plaintext extraction or claim that every caller has
unrestricted access. Existing GPG plugin code has a similar inherited pattern;
that is not evidence that it is safe for this new integration.

Correction: distinguish key references from actual supplied key material, honour
the referenced/authorized key, and use the existing daemon authorization/unlock
path. Evaluate the real deployed API and request flow before activation. No new
authentication service is justified; passphrase prompting alone does not prove
that the requesting application is authorized to use a stored key.

### P1-02 — Key deletion and persistence can report success before safe storage

Locations: secrets/rnp/rnpkeys.cpp:216–247; rnp/rnp.cpp:623–638,751–767,833–836.
removeSecret returns success after an in-memory mutation. Persistence is deferred
to Keyring's destructor, and rnp_save_keys errors are ignored. The current output
path directly overwrites the existing keyring; actual RNP0.18.1 uses
init_file_dest(..., true), reaching O_TRUNC. A failed save can therefore destroy
the prior file after the caller has already received success.

Only the public Keyring is marked modified by publicKeyring().remove(). Key::remove
may remove both public and loaded secret material, so the secret ring can remain
unchanged on disk despite successful deletion being reported. Destructor-only
saving also loses successful in-memory changes on abnormal termination.
Underlying importKeys never populates its returned list or marks rings dirty;
the public import APIs are separately stubbed (P1-04).

Correction: explicit checked persistence before reporting completion, correct
dirty tracking for every affected ring and preservation of the original on error.
Use existing native/platform staged-write facilities. RNP random-output/finish
has known cleanup/auto-finish caveats recorded earlier in this study; its use must
follow checked commit/abort semantics, not merely replace one output call.
No crash-durability or concurrent-writer guarantee is established by this review.

### P1-03 — Native key-handle ownership is inconsistent

Locations: rnp/rnp.cpp:508–555,562–570,643–674,819–825.
Keyring::key(Crypto::Key) creates local primary wrapper k, then can return
k.subkey(...). The subkey constructor borrows k.m_primary, while destruction of k
frees that handle. The returned subkey thus contains a dangling primary pointer;
a later keyid()/toCryptoKey() call dereferences it. Immediate encryption currently
uses the separate m_key handle, so this is not a claim that every encrypt crashes.

Separately located primary handles are never destroyed, move assignment drops
previous ownership, and UID handles obtained in toCryptoKey lack destruction.
The top-level owning Rnp type also has no explicit copy prohibition despite raw
owning native/context pointers. These are lifetime/maintenance defects; no exploit
or dynamic leak measurement was executed.

Correction: define ownership/borrowing explicitly and use existing native destroy
APIs with ordinary C++ ownership. Do not simply destroy both pointers: primary
and selected handles can alias. Add focused ownership/move/subkey regression
coverage when making the correction; a wholesale wrapper rewrite is not required.

### P1-04 — Unimplemented operations falsely report successful completion

Locations: secrets/rnp/rnpffi.cpp:267–316,442–493.
generateKey, generateAndStoreKey, importKey, importAndStoreKey and storedKey can
return default Result() without generating/importing/retrieving a usable key or
initializing outputs. Actual Sailfish Crypto Result defaults to Succeeded.
The header advertises storage capability. In generateKey, default success also
causes an unused temporary directory to be retained via setAutoRemove(false).

Correction: return the existing explicit unsupported result until an operation is
implemented; validate inputs and set outputs on supported successful paths.
Do not require a complete key-generation UI or every optional API just to begin
the pass/OTP product slice. Distinguish incomplete features from dishonest results.

### P2-01 — Callback and error transport need explicit success/failure semantics

Locations: rnp/rnp.cpp:85–113,116–130; rnpffi.cpp:685–689.
An overlong passphrase is not copied, yet unlock returns true when UI interaction
succeeded. This violates the callback's success contract; return false/error if
it cannot fit. No buffer overflow or passphrase disclosure is demonstrated here.
Initialization/provider-registration errors are ignored.

QByteArray::fill overwrites a local copy; InteractionRequest::userInput returns
its retained data by value, so this is not evidence that every Qt/request copy
has been securely erased. Avoid the stronger implication in the comment and
follow actual supported secret-buffer ownership/clearing semantics.

The helper returns byte arrays without a separate operation status; the plugin
treats empty decrypted bytes as failure. Valid empty plaintext is therefore
indistinguishable from failure, and cancellation/key/ciphertext failures collapse
to generic messages. Preserve status separately from bytes and map cancellation
using the existing API. Test empty-entry and long/canceled password paths in the
eventual correction; no new parser or framework is needed.

### P2-02 — Key lookup, filters and signature/expiry metadata are wrong

Locations: secrets/rnp/rnpkeys.cpp:151–162,181–187; rnp/rnp.cpp:281–306,676–714.
- findSecrets reverses its intended "import means all collections" condition:
  "import" selects a literal non-key ID, while a specific collection enumerates
  all primary IDs. Returned keys are not confined to the requested collection.
  This is a selection defect, not a proven daemon-wide authorization bypass.
- canSign unconditionally matches; canEncrypt uses AlgorithmUnknown as a
  placeholder, rejecting RSA even when it can encrypt. Filtering primary
  fingerprints through primary.subkey also yields invalid primary results.
- Signature conversion retrieves a subkey ID when it has located the primary,
  then overwrites the signature's actual subkey fingerprint with the primary
  fingerprint. Caller/signature matching can fail or identify the wrong level.
  No signature-verification bypass was demonstrated.
- Every nonzero expiration is labelled expired; seconds/lifetime values are
  passed to a millisecond timestamp API. Key size is assigned the subkey count,
  although Sailfish Key::size is a bit-size property. Non-RSA/DSA algorithms
  become Unknown.

Correction: use actual key operations/identity and the existing rnp_key_is_expired,
rnp_key_get_bits and timestamp contracts; keep primary/subkey identities distinct.
These are product metadata/selection bugs, not reasons to impose new OTP limits.

### P2-03 — Reported protection level exceeds implemented facilities

Location: secrets/rnp/rnpffi.h:26–27.
The provider advertises TrustedExecutionSoftwareEncryption. The actual platform
enum documents this as a TEE application. The inspected plugin is ordinary
in-process librnp software; no TEE implementation is present. The inherited GPG
provider uses the same declaration, but copying it does not establish protection.

Correction: advertise the actual software capability and avoid implying hardware/
TEE isolation. Platform authorization and native key lifetime still need explicit
implementation verification; being a Secrets plugin does not establish either.

### Style, best practices and maintenance

Positive: standard Qt plugin interfaces/Secrets interaction requests are reused;
cryptographic operations are delegated to RNP rather than invented; principal
sign/verify/encrypt/decrypt paths have common native cleanup exits. A goto-based
cleanup path, Qt multiple inheritance here, or explicit unsupported optional APIs
is not inherently a defect.

Maintenance work should prioritize behavior over formatting:
- Remove large dead copied GPG implementations and stale pinentry/GnuPG comments;
  they obscure which operations actually work and contributed to misleading stubs.
- Make resource ownership, result/error types and supported capabilities explicit;
  keep override annotations and pointer/null/move conventions consistent.
- Root CMake and RPM force QMF/email dependencies alongside Secrets. Make that
  existing component optional for a Secrets-only build instead of pulling mail
  functionality into the pass/OTP requirements.
- The retained snapshot contains no focused automated tests for these plugin
  contracts. Existing libpgpfactory tests are useful behavioral references, not
  proof that this separate plugin passes them.
- Existing daemon crypto/secrets worker pools are serialized (max thread count1)
  in the inspected source. A blanket race or inevitable interaction deadlock was
  not established; do not add locks/coordinators on that assumption.
- The hardcoded daemon HOME/.gnupg layout must be made deliberate for integration
  and synthetic testing. The directory name is not a GnuPG executable dependency.
  Avoid accidental use of a real user's keyring; no real keys were accessed here.

### Disposition and next bounded implementation work

Separate reviewer runtime_review confirmed the source/contract findings and
priorities, with the qualifications above. This is assistant source review, not
a human security audit or runtime security certification. No code was patched,
built, activated or tested against keys in this review.

Keep Secrets/RNP as the implementation direction, using this POC as source and
architecture reference. First correct honest API results, key-reference/access
semantics, native ownership and checked keyring persistence; supported operations
need focused synthetic regression checks. Then connect the existing pass-format
entry/policy/OTP layer through actual Sailfish Crypto requests. Multiple-recipient
pass writes remain a concrete plugin integration gap; they must not be silently
replaced with a single-recipient/read-only definition of the central objective.

Detailed pinned inputs and separate disposition are retained under the existing
feature evidence directory secrets-plugin-review-20261101/. No external issue
comment, upstream message, publication, new repository or real-key/device action
was made. The review is complete; corrections are subsequent scoped implementation.

## Secrets/RNP bounded correction implementation — 2026-11-01

Owner: root; separate scope/source/results reviewer: runtime_review. Maintainer
authorized continuation after review. Scope: honest unsupported key provisioning/
mutation APIs, necessary reference metadata lookup, exact request-local PRIVATE
key binding for decrypt/sign, ordinary native ownership, no destructor writes,
and honest software capability. Public encryption retains RNP suitable-subkey
semantics; exact-primary-family policy mapping is not silently changed.

Separate plan review accepted this safe first slice: provisioned synthetic
keyrings are read-only; pass-entry encrypt/decrypt remain supported. Key onboarding/
deletion is explicitly unavailable rather than attempting a new two-file storage
transaction. Full recipient-policy/OTP/daemon authorization integration remains
the central product objective, not acceptance of this direct-class fixture.

Acceptance: source review; exact staged identities; actual SDK module/fixture
build; meaningful pristine failure controls and corrected key-reference/raw-key,
other-primary/sibling/primary-secret refusal, sign/decrypt, ownership, unsupported
API and unchanged-keyring tests; separate results assessment. No existing daemon
activation, host crypto test, installation/device action or real secrets.
Tests execute only in SDK/LXC. Do not claim all P2 review findings resolved.

Actual target inventory Qt5.6.3/Secrets0.2.44: three development interfaces missing.
No-refresh dry-run of three exact devel packages proposes5new packages, all
0.2.44-1.14.2.jolla,208.7KiBdownload/263KiBinstalled,0upgrades/0removals.
Concrete reviewed source/recipe precedes any separate installation approval.


## Secrets/RNP correction build and regression results — 2026-11-03

Owner: root; separate scope/source/results reviewer: runtime_review.
The bounded correction is implemented as a reviewable six-file upstream patch,
not an adopted fork or activated daemon plugin. Recipe, tests and scope:
[secrets_plugin/README.md](../../tools/research/secrets_plugin/README.md).
Earlier pending-install/build wording records historical checkpoints.

### Implementation and additional review finding

The patch disables unsupported key mutation/provisioning and destructor writes;
provisioned keyrings are read-only. Metadata references replace fabricated key
bytes, operations reject raw key material, native handles have explicit ownership/
move behavior and capabilities report software encryption. Public encryption
retains RNP suitable-subkey selection; no exact-primary encryption claim is made.

Decrypt/sign use a native request-local FFI containing exactly one selected secret
key. Existing RNP export/import/remove facilities preserve public primary context
without granting authority over sibling secret keys. No custom key service or
crypto is introduced. An exact primary reference authorizes that primary only.

The separate resulting-source review found an additional symmetric fallback:
RNP can request a password with a null key for SKESK input. The scoped callback
now refuses null-key requests before forwarding to Secrets. Successful keyed
decrypt also requires a non-null used-recipient handle. No key-ID equality check
is imposed, avoiding an unnecessary restriction on hidden recipient identifiers;
hidden-recipient runtime behavior itself was not tested. Generic/QMF helper paths
are unchanged and outside this slice. Empty plaintext uses a checked native
output callback, separating successful empty output from failure.

### Actual platform/build and meaningful regressions

Scoped approval installed five exact SDK packages, all 0.2.44-1.14.2.jolla:
libsailfishcrypto-devel, libsailfishcryptopluginapi,
libsailfishcryptopluginapi-devel, libsailfishsecretspluginapi and
libsailfishsecretspluginapi-devel. Five new, zero upgrades/removals, no repository
refresh or signature-policy change. Download208.7KiB/installed263KiB.
Install NOKEY warnings are retained; authenticated signature verification is
not claimed. The package action stayed inside the existing SDK LXC.

Fresh r5 target build completed exit0/33.14s using SDK3.13.5,
SailfishOS5.1.0.11-aarch64, actual Qt5.6.3/Secrets0.2.44 and retained
RNP0.18.1/OpenSSL3.5.6. Test-named module and two direct-class executables are
AArch64; source and staged identities were audited against pinned inputs.
Module build does not establish plugin-loader/daemon integration: the module
was never loaded, installed or activated. Actual runtime loader evidence resolves
the retained librnp and target Qt/Secrets libraries, not a substitute API.

SDK-only runtime completed exit0/24.2s:

- Pristine control: 17 assertions, 16 genuine regression failures; own-key positive
  passes. It decrypts B under A's reference, accepts raw-key requests and reports
  false-success unsupported APIs. Its public ring changes on destruction.
- Corrected control:18/18 pass, including honest unsupported results, metadata,
  reference/raw-key refusal and software capability.
- Protected fixture:23/23 pass, including exact primary and encryption/signing
  subkeys; other primary/sibling/primary secret refusal; refusal after success;
  empty plaintext; native move/self-move and returned subkey-parent behavior.
- Symmetric and signed-only generic positives pass. The same input is refused
  through selected-key decrypt with empty output and no forwarded password
  callback, even with a deliberately willing symmetric provider.
- Runner9/9 pass, including independent GPG exact plaintext and exact signing-subkey
  VALIDSIG oracles. GPG2.4.8 runs only as fixture generator/oracle inside this LXC;
  this is not a runtime GnuPG dependency for the corrected plugin.

Corrected keyrings stay byte-identical in both fixture groups. All46 manifest
identities remain unchanged postrun; zero fixture directories/matching GPG agents,
empty outer stderr. Original source17files and corrected source17files are retained.
Earlier missing-header builds, first empty-plaintext runtime failure, r4 preceding
the fallback finding, and their evidence were preserved rather than overwritten.

### Identities, evidence and bounded disposition

Patch SHA256:
`9ac9c8385d936b069d90f54d7a7b21711b6806d49ccda23c6fc7397414d74c51`.
Probe:
`612a03beb7bdd10a11422694f4c89b3bfa48f1c0bbc85c14a048f7e3fcbac2d6`.
Runner:
`cb4ae1556ea4bbadf9a42932faddc38f56789c90b218ee47718092e5ae2322d2`.
Corrected executable:
`4af206d895b36ea9cda35c9b67bc82d9d1a9865378eeb7e81722db7437e55a8b`.
Test module:
`fbf58b5c1715111977e92f91ccbcb444660d9f2ea5a59c061ef125d9b4020b94`.

Evidence remains in the existing local secrets-plugin-review-20261101 directory:
sdk-package-install-20261103.json/log, sdk-staging/build/artifacts-r5-20261103.json,
sdk-build-r5-20261103.log, runtime-keyed-final-20261103.json/stderr,
runtime-keyed-final-execution-20261103.json, postrun-keyed-final-20261103.json.
Retained SDK root: /home/ubuntu/secrets-rnp-corrections-20261103-r5.
Full input/ELF identities and compiler/link evidence are in sdk-artifacts-r5.

Separate final reviewer runtime_review reconstructed all six corrected files and
checked build/result/manifest consistency. No unresolved material finding remains
within this bounded slice; the r4 symmetric-fallback finding is resolved. Review
record: final-independent-review-r5-20261103.json. Reviewer inspected evidence
and source without rerunning crypto/cleanup. No human security audit or release
approval is claimed. Unexecuted/outstanding: actual daemon
authorization/unlock/UI and plugin loading, key management, multiple-recipient
plugin API/pass-policy integration, remaining P2 metadata/filter/signature behavior,
ASAN/Valgrind/leak-size/error-injection coverage, QMF, native OTP calculation,
device/package/distribution acceptance. The central pass/OTP objective is not
silently reduced to read-only entries or a single-recipient store.

The next product slice is actual Sailfish Crypto request integration and explicit
recipient-policy support; it needs bounded scope/review before implementation.
No additional feasibility experiment is automatically queued. No real secrets,
host crypto, device changes, new repository, commit/push or publication.

## Public Crypto requests and multiple recipients — prepared checkpoint, 2026-11-03

Owner root; separate required reviewer runtime_review. Maintainer authorized
the next implementation slice. Previous r5 result is preserved. This continuation
prepared code and recipes only: no new build, crypto, test daemon or install.

Actual pinned daemon/API inspection: EncryptRequest accepts one Key and forwards
customParameters; stored-reference precheck covers that main key only.
Additional stored refs in arbitrary parameters would not inherit that precheck.
Same-plugin StoredKeyRequest dispatches directly with TODO accesscontrol
(cryptorequestprocessor.cpp1091+), so its use must not be presented as demonstrated
caller authorization. Public material in Key is the existing standard public
encrypt path; it grants no stored private authority.

Separately reviewed implementation extends public-only export and encryption:
integration.patch layered over unchanged corrections.patch. Main public Key and
namespaced org.sailfishos.crypto.rnp.additionalRecipients list carry public
packets and expected full fingerprints. Per-payload native FFI imports both public
and secret to detect/reject secret packets, resolves its own fingerprint, then
loads the verified public payload into aggregate context. All imports finish
before aggregate handles are retained; every recipient must resolve/add before
execution. Native fingerprint parsing and suitable-key selection are reused.
Primary public export includes subkeys; cert/sign primaries with encryption
subkeys remain supported. Private export/sign/decrypt boundaries remain unchanged.
This is explicit public-encryption capability, not a generic multi-key API.

Separate source review found/fixed an unnecessary handwritten fingerprint-width
restriction and preservation of the existing raw-secret unsupported error code.
Final source patch6b89da5fed8e50e6caf68e7c66f2ac4030a8f5b3efa539abc4a79ecb4ac8f52f
has no unresolved material source finding within this scope.

Prepared fixture builds actual local pinned upstream daemon3e79aaec with only
main's plugin paths bound to scratch. Standard --test filtering occurs after
loading plugins and alone is insufficient. A private session bus, XDG_RUNTIME_DIR,
XDG_DATA_HOME, HOME and plugin directory isolate the fixture; existing daemon/P2P
dispatch and actual public request objects are used, not a replacement service.
Imported collection defaults have NoAccessControlMode; fixture success will not
prove production caller authorization or lock/unlock UI.

Concrete preexecution review remains OPEN: api-run outer115s timeout is shorter
than target worstcase127s plus SDK startup; detached owned fixture processes could
survive while TemporaryDirectory deletes their root. Fix margin and explicit
owned-process verification/cleanup before root deletion, preserving evidence/root
when cleanup cannot be proved, then obtain recipe re-review. Do not execute the
current pending controller. Nested QVariantList/Map transport must be tested with
real requests; standard QtDBus decoding may be necessary, no actual defect proven.

Target read-only inventory confirms dbus-daemon/dbus-run-session/qmake and actual
systemsettings0.10.19.1, dbus1.16.2, QtSql/Concurrent5.6.3 interfaces. No daemon
binary. Existing sqlite driver is not a replacement for QSQLCIPHER. Exact cached
qt5-plugin-sqldriver-sqlcipher0.2.44-1.14.2.jolla dryrun succeeds:1new,
58KiBdownload/132KiBinstalled,0up/remove,no refresh. NOT installed/authorized.
Initial dryrun without standard SDK --maintain failed root requirement; corrected
--maintain dryrun succeeded. No security-policy workaround.

Files in tools/research/secrets_plugin: integration.patch, daemon-fixture.patch,
integration.cmake/spec, api-probe.cpp, api-target.py, api-run.py. Full working
integration-source and api-preparation-20261103.json live in the existing local
feature evidence directory. Python AST parsing and git diff --check pass only.
Next steps and acceptance are in STATUS: fix/review cleanup; fresh staged SDK build,
explicit exactdriver installation approval, actual API+retained regression suite,
independent A/B/C oracle checks, identity/cleanup audit and separate final review.
No full pass walker/file writer, native OTP or unlockUI acceptance yet.

## Real Crypto API and multiple-recipient result — 2026-11-03

Owner root; separate scope/source/recipe/results reviewer runtime_review.
This bounded slice is complete: actual StoredKeyRequest/EncryptRequest/
DecryptRequest through the pinned upstream discovery/P2P dispatcher, loaded
corrected RNP module and standard SQLCipher. Final build exit0/138.93s;
actual API runtime exit0/5.0s. All22client+7target+14outer checks pass.

A/B use cert/sign-only primaries with encryption subkeys. Both retrieve real
public packets, encrypt to two recipients, and independently decrypt through
actual stored-subkey requests. Separate GPG homes with only A/B/C secret material
prove A/B byte-exact recovery on2outputs and C refusal without plaintext.
Malformed list/fields, missing/invalid packets, mismatched full fingerprints,
keyids, private components and secret packets (main/additional) refuse with empty
ciphertext. Distinct errors prove intended field/native branches; subsequent
success and single stored-reference encrypt pass. No recipient silently omitted.

The extension validates every payload independently with native PUBLIC|SECRET
loading, zero-secret count and exact native fingerprint lookup before aggregate
public encryption. Primary export includes subkeys; native suitable-key selection
retained. Real D-Bus execution exposed the QVariantList-only assumption; actual
Qt5.6.3 currentSignature/qdbus_cast now handles exact av/a{sv} containers with the
same strict schema. Oldr6 negative checks that only hit list rejection are NOT
accepted as payload-validation evidence. No custom codec/dispatcher introduced.

Final direct suite rerun exit0/25.62s:18control+23protected+9runner checks pass.
Pristine16genuine failures/17 with own-key positive. Exact private key/callback,
sibling/other-primary, empty plaintext, ownership and symmetric/signed-only
refusal controls remain intact. All549staged/source/ELF identities and provisioned
keyrings unchanged postrun; zero fixture directories/matching bus/daemon/agents.

### Actual SDK facilities and scoped security exception

Target D-Bus cannot resolve UID1000/root in development sysroot; native dbus-send
also failed. Existing Ubuntu D-Bus1.16.2 in the SAME SDK LXC supplies only its
private session bus. Target daemon/plugin/public client/P2P remain native.
LXC AppArmor then denied even Hello. Installed1.16.2 manpage and actual standard
session.conf document the per-bus setting and EXTERNAL authentication.

After concrete independent review, scoped human execution approval permitted
sdk-session-bus.conf: include standard session policy and disable AppArmor
mediation ONLY for the disposable private Unix bus. EXTERNAL Unix-UID auth
remains. No global D-Bus/AppArmor/LXC/device configuration changes or anonymous/
TCP authentication. This is a hybrid SDK facility; successful tests do not prove
production confinement, caller authorization or protected-key UI. Default runner
does not enable optional --sdk-bus-config. Configuration hash is in API results.

Standard QSQLCIPHER driver installed with scoped approval:
qt5-plugin-sqldriver-sqlcipher0.2.44-1.14.2.jolla,1new58KiB/132KiB,0up/removals,
no refresh/signature-policy change. NOKEY warning retained; authenticated
signature verification not claimed. Driver hash checked inside build-shell,
where SDK translated paths are available; initial outer-path assumption corrected.
No SQLite substitute or daemon metadata/precheck bypass.

Outer owns bus/GPG fixtures, target owns daemon; private HOME/XDG/runtime/plugin
paths and0700root. Root deletion requires all cleanup proofs; uncertainty
preserves root/fails. Outer210s allows bounded target work and cleanup.
SDK root511MiBfree at final check; all previous builds/failures retained.

### Identities and bounded disposition

Pinned plugin effb3a471738fddf221bc68136bb9789011b2355,
daemon3e79aaec2092ecc1ddd449d36b9ebc2bd724713b and RNP0.18.1aad1892e unchanged.
Foundation corrections.patch9ac9c838 remains; incremental integration.patch:
3c1faa60fa1d76477583e7264a0a8a2515fd6e732e3f310b8e2c1cce1fbaebbb.
Optional bus config:
ad00bebc169828b0e0641b29aec0ad7edebfdccd3c85d5928c392e39b3d026d9.
Driver:
47308c88d13ddea045f68f819b7440e73b6f084d97a18c3a46abfd553ab9f2c6.
Final module:
6f735f402811242c117a5d1bb43c98afdb46dd24f88d9c397375160d19581611.
API client:
fa1b9b82e0e8939e8b1bb28649554b3ba5aa12e6fde2c52be0a3d6a12cc3bea1.

Existing local evidence directory secrets-plugin-review-20261101:
api-transport-{staging,build,artifacts,artifacts-with-driver,runtime,postrun}-20261103.json,
build log, runtime execution record, api-transport-direct-regression/execution
records and api-final-independent-review-20261103.json. Full491upstream originals
with only main path patch,17pristine+17integration sources and5AArch64 ELF/cache/
link identities retained. Fresh build root /home/ubuntu/secrets-rnp-api-20261103-r2.
Earlier source/patch/controllers and initialbuild/APIr1-r6 failures preserved.
[Request schema/recipe](../../tools/research/secrets_plugin/README.md).

Separate final reviewer supports bounded acceptance, no blocking finding, after
source/build/result/negative/oracle/cleanup assessment. Reviewer did not rerun
crypto; separate assistant review is not human security audit or release approval.

Remaining product slice: existing pass policy/store/OTP logic through these
requests, all-recipient resolution before writes, protected-key unlock/session
ownership and production authorization. Upstream same-plugin StoredKey TODO
accesscontrol and imported NoAccessControl defaults remain explicit limitations.
Key onboarding, other P2 metadata/filter/signature issues, exhaustive error/leak
and device/distribution acceptance unestablished. No engine feasibility reopened.
No real secrets, existing daemon activation, product install, device action,
new repository, push or publication.

## Selected-entry pass/TOTP consumer result — 2026-11-03

Owner root; separate scope/source/recipe/results reviewer runtime_review.
The concrete consumer path now reuses pinned factorye53cd22 policy/file interfaces,
pinned QtTotp1d1e787 parser/generator and actual Sailfish Crypto requests through
the retained real RNP daemon/module. No new walker/OTP crypto/parser/service.
[Source, contracts and recipe](../../tools/research/secrets_plugin/consumer/README.md).

Source seams: split unchanged singleton/factory into its own translation unit;
borrowed policy-only helper initialization retains existing parser and refresh
behavior without fabricated private enumeration. Missing/unreadable/empty policy
fails. InterfacePassFile encrypt is virtual, and the Secrets override resolves all
public recipients before encrypt/output, uses checked QSaveFile with direct-write
fallback disabled, and updates plaintext cache only after commit. Decrypt clears
stale plaintext first. Explicit private-subkey reference remains independent of
encryption policy. Canonical containment is ordinary validation, not race-proof.
The virtual seam changes ABI: fresh-build consumers; no drop-in binary claim.

Existing default factory body/CMake path is preserved, not fully rebuilt in this
slice. Consumer compiles generic sources only; original MIT license and QtTotp
notices retained. Qt5.6 Clock adaptation uses actual toTime_t API, not own clock.
Basic locator matching is implemented for the pinned plugin; advanced GPG groups/
signed/environment policy and general symlink semantics remain outside acceptance.
QtTotp clamping/unknown-algorithm and HOTP conformance remain explicit limitations.

Build exit0/41.98s; runtime exit0/33.63s on actual SDK3.13.5/
SailfishOS5.1.0.11-aarch64/Qt5.6.3/GCC13.4.49client+22outer+7target checks pass.
Root/inherited/nested replacement/multiple policies, readable policy errors,
successful save/cache/fresh read, and second-recipient read pass. Failed atomic
output OPEN in read-only parent preserves original ciphertext/cache despite
writable existing file; no forced commit-stage/crash guarantee is claimed.
Wrong-key/corrupt reads and outside/symlink/changed paths refuse without stale
plaintext. All guard ciphertexts and provisioned keyrings remain unchanged.

All18 SHA1/256/512 [RFC6238 Appendix B](https://www.rfc-editor.org/rfc/rfc6238.html#appendix-B)
values match through actual decrypted selected entries at six fixed timestamps,
including20000000000. Entry notes/full bytes are preserved during tested saves.
Independent GPG A/B/C homes verify five expected byte-exact decryptions and seven
refusals on four outputs, including nested replacement and both multi recipients.
GPG remains synthetic oracle only, never a consumer dependency.

Consumer ELF directly needs Qt5Core, SailfishCrypto and standard C++/C/math/GCC/
loader; no RNP/GPGME/Assuan or helper-spawn imports. Consumer runtime maps confirm
no OpenPGP engine loaded locally; actual daemon uses retained RNP module/SQLCipher.
All632 staged/source/ELF identities unchanged postrun,0fixture dirs and owned
client/daemon/bus/GPG agents,empty outerstderr,492MiB SDK root free.
Inherited source precedence/copied-whitespace warnings retained, not hidden.

Same explicitly approved SDK private Ubuntu bus/AppArmor exception ad00 applies,
EXTERNAL UID auth retained,no global/LXC/device policy change. No host key/OTP
execution, real keys/stores/seeds, product installation,newrepo,push/publication.

Evidence existing secrets-plugin-review-20261101:
consumer-preparation/staging/build/artifacts/runtime/runtime-execution/postrun
records/logs and consumer-final-independent-review-20261103.json. Final consumer
binary c1cd124798fae3f318a3af0307e44ae3664b70042b73187ed0ad0764a80a8bf2;
fresh SDK root /home/ubuntu/secrets-pass-consumer-20261103.
Native module/build reused unchanged from API transport acceptance; no additional
engine-feasibility experiments or new dependency installation.

Separate final reviewer supports this bounded slice with no blocking finding,
based on source/compiled-input/runtime/oracle/ELF/cleanup evidence; reviewer did
not rerun crypto. Assistant review is not human security audit or release approval.
A selected-entry pass/TOTP path is working; protected daemon unlock/session,
production authorization, general OTP/HOTP, full-store and device/distribution
remain material product work. They were not silently replaced by fixture success.
