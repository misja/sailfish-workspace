# Public native-backend feasibility fixture

Prepared 2026-10-25. This is a research client of unchanged upstream public APIs,
not an adopted backend, package or native OTP implementation. Primary coordinator
owns the task; Builder prepares sources and a separate reviewer assesses source
before execution and evidence afterwards. No build or execution is implied by
this document. Installation needs the maintainer's explicit approval of the concrete plan.

Inputs are the complete immutable archives already retained in the existing
feature's `source-research/full-sources/` directory:

- `shemeshg/gpgme-cmake-example` commit
  `e53cd22c365ce170ebeaed70984207a8206d00eb`;
- `rnpgp/rnp` commit `aad1892e4d8423398a0b973bd0a7e4544c359afc` (RNP 0.18.1).

Use the existing archive manifest for archive SHA256 and extracted-file checks.
Archive identity is not an upstream signature/security audit. Copy complete
verified trees into an isolated container path outside any Git checkout, so RNP's
version discovery uses its pinned `version.txt` rather than an ancestor repository.
Retain original source bytes. Do not fetch, update, patch, extract selected classes
or install these sources. The fixture's small CMake project adds the original
`libpgpfactory` subdirectory; the parent GUI project is not configured.

## Actual build requirements

The retained Ubuntu 26.04 LXC has runtime tools/libraries but lacks its C++ build
toolchain and development headers. Required requested packages are `cmake`, `g++`,
`make`, `pkg-config`, `libgpgmepp-dev`, `libgpg-error-dev`, `libbotan-3-dev`,
`libjson-c-dev`, `libbz2-dev`, `zlib1g-dev` and `libsexpp-dev`. The coordinator's
existing `public-backend-20261025/prerequisite-proposal.json` records exact pins
and the simulated dependency closure: 52 new packages, 3 dependency upgrades,
0 removals. The upgrades are liblzma5, zlib1g and xz-utils; `--no-upgrade` did not
prevent dependency-driven upgrades. No installation has been performed by Builder.
Do not silently substitute fresh apt candidates if this proposal changes.

Evidence in the actual pinned recipes:

- `libpgpfactory/CMakeLists.txt` is C++17 and Linux requires Gpgmepp plus
  LibGpgError. These requirements remain even though the fixture selects RNP.
- `RnpCore/CMakeLists.txt` normally FetchContents RNP by tag. The fixture uses
  standard `FETCHCONTENT_SOURCE_DIR_RNP` to select the verified local full tree,
  with fully disconnected/update-disconnected mode. No replacement dependency
  provider, source extraction or fake imported target is introduced.
- RNP's maintained `SYSTEM_LIBSEXPP=ON` accepts system `sexpp>=0.8.7` through
  pkg-config; the existing distro runtime is 0.8.7. Installing matching headers
  uses that supported route instead of inventing or fetching the archive's absent
  libsexpp submodule. Verify the actual dev-package version from the install plan.
- `CRYPTO_BACKEND=botan3` requires Botan >=3.0.0; installed runtime is 3.10.0.
  RNP itself selects C++20 for Botan3. The client/public library remain C++17.
  RNP needs BZip2, zlib and JSON-C headers; OpenSSL is the alternate backend,
  so libssl-dev is not directly requested for this choice (the actual apt closure
  includes it transitively through Botan development dependencies). No librnp-dev is needed because
  the unchanged pinned RNP tree supplies its headers and is built in the build tree.
- Pinned `cmake/version.cmake` exists, avoiding its fallback web download.
  Upstream tests/GTest download and documentation are disabled with existing
  options. No source tree or runtime package is installed or replaced.

After scoped installation approval and independent source review, the coordinator
can stage the reviewed source layout and use the following build recipe as ubuntu
UID1000 in the retained container. Set the four task-specific paths to the copied,
hash-verified locations; keep the source/build paths outside any Git checkout.

```sh
cmake -S "$probe_sources/public_backend" -B "$probe_build" -G 'Unix Makefiles' \
  -DGPGFACTORY_SOURCE_DIR="$factory_sources" -DRNP_SOURCE_DIR="$rnp_sources" \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$probe_build" --target public_backend_probe --parallel 2
env -i PATH=/usr/bin:/bin HOME=/home/ubuntu LANG=C LC_ALL=C \
  ldd "$probe_build/public_backend_probe"
readelf -d "$probe_build/public_backend_probe"
python3 "$probe_sources/public_backend_probe.py" \
  --binary "$probe_build/public_backend_probe" --pass-sources "$pass_sources" --run
```

Here `probe_sources` is the copied `tools/research` directory (including the
existing preparer); `factory_sources` and `rnp_sources` are the extracted archive
roots; `pass_sources` is the existing immutable `baseline/` pass/OTP export;
`probe_build` is a new owned build directory. Capture configure/build status and
failure output separately; never call an unbuilt/unexecuted case passed. Check
the link closure and hash the actual build-tree native libraries/executable.
Record the actual CMake generator, compiler and package versions, configure cache
and source/archive hashes. The clean-environment `ldd` result must resolve both
RnpCore and librnp to this owned build tree. Resolve and hash those precise files,
and capture their `readelf -d` RPATH/RUNPATH/NEEDED records too before crypto.
Do not infer the loaded-library identity from a matching SONAME, hardcoded commit
or executable hash alone; the installed librnp0 has the same SONAME. The runner
clears inherited loader environment variables. If resolution differs, stop and
review the build configuration instead of silently injecting a loader override.
There is no `cmake --install`. The fixture runner neither builds nor installs.

## What the fixture measures

The runner creates two protected Ed25519-primary/cv25519-encryption identities,
separate explicit GPG/native homes and one synthetic store. Only each identity's
own secret plus its peer's public key is imported. Passwords use an inherited
fixture FD, not arguments/logs. Raw crypto diagnostics, entry text and keys are
never copied to reports; only the reviewed fixture constants contain public
synthetic/RFC data. All native processes use one home/callback binding, respecting
the library factory's singleton behavior.

`refuse` is a fresh process before any successful native unlock. An empty password
callback and refusing login prompt exercise the existing public decrypt failure;
the client gates save after successful decrypt. Counters and independent ciphertext
comparisons record whether a save occurred. No auth-context redesign or retry loop.

`normal` uses actual helper `searchDown` with path-only list/narrow-find matching and `isGpgFile`,
without a custom entry walker. Actual `GpgIdManage` public construction invokes
its private `init`; `ensureValidGpgIdFile` must succeed before its `encryptTo`
recipients are used. Root inheritance, nearest nested override and multiple
recipients are checked against the synthetic expected key IDs. A mixed valid/
unresolved policy must reject before save. Public `getPassFile`, `decrypt` and
`encrypt` operate on complete precomposed OTP/multiline text; no URI parser or
native OTP mutation is implemented. The existing public `encrypt` already writes
UUID ciphertext then renames: it is tested unchanged, without adding RANDOM output
or another writer. A direct missing-recipient public save tests failure preservation
and counts leftover files; its in-memory decrypted cache is observed separately.

A bounded case uses a naturally conflicting nonempty target directory:
it measures the public rename exception and any adjacent leftover. This is **not**
evidence of preservation when rename over an existing encrypted file fails.
The source has no custom permission/race/callback injection to manufacture that case.

Fresh `read-b` independently decrypts nested and multiple-recipient outputs with
only B's secret key. GPG independently checks all changed plaintext exactly and
both multiple-recipient identities. The actual pinned pass-otp extension computes
the RFC6238 SHA1 code at 59 seconds from native-saved ciphertext using the existing
source preparer/fixed-time OATH wrapper; exact fixture hashes/diffs are reported.
This is an external OTP oracle, not proof that libpgpfactory implements OTP.

The runner removes only its entire owned fixture directory and explicitly stops
its own GPG agents. The coordinator independently checks cleanup and stops the
retained container. Build/source artifacts may remain for reproduction. No
production adoption, complete save safety, concurrent/crash/fsync behavior,
general recovery, native URI mutation, signed policy, Git/HOTP, Sailfish build or
dependency acceptance follows from this experiment.

## Bounded correction experiment — 2026-10-25

The maintainer separately authorized a small correction proposal, independent review,
implementation and synthetic tests. The coordinator checked current upstream:
default HEAD still equals the pinned `e53cd22c365ce170ebeaed70984207a8206d00eb`;
no newer merged fix on that HEAD was available. This local experiment is not an
upstream submission, maintained fork, adoption or production security approval.

`corrections.patch` modifies exactly two upstream source files. It retains the
existing listKeys filter and adds the already-fetched fingerprint to its matching
predicate, still within the existing native selector. It changes no case/UID policy.
The public save still uses its existing UUID ciphertext staging. A preflight rejects
an already-existing generated path (including dangling symlinks) or a status error
before writing or removing it. The temporary path is constructed before the try,
so catch cleanup needs no implicit string-to-path allocation. Rename joins the
existing protected operation; error-code cleanup is best effort and the original
exception is rethrown. Cached text is swapped with the already-by-value argument
only after successful rename, without an allocating postcommit assignment.

Apply only to a separate copy of the hash-verified upstream tree. Preserve pristine
archives/extracted trees, baseline builds and every preceding result. Record patch
identity, changed-file hashes and complete source-copy comparison before rebuilding
with `GPGFACTORY_SOURCE_DIR` pointing to that separate copy. Keep the pinned RNP
tree unchanged. Repeat the existing clean-environment loader/hash verification
against the new build before executing reviewed fixture sources. No dependency
installation, new writer, native RANDOM mechanism or broad lifetime fix is included.

The runner's explicit `--expect-corrections` option defaults to false, so baseline
experiments remain available. The report and each native process record the chosen
expectation mode. Run with default fingerprint policy and `--expect-corrections`
against the reviewed patched build: the previously rejected full fingerprint must
now resolve to its key and traverse all policy/write/oracle cases. Every successful
save checks its cache against the proposed exact text. Before the real missing-
recipient failure, the cache is primed through actual decrypt and must retain the
original text after failure. The nonempty-directory rename conflict must preserve
its marker, retain the expected filesystem exception, keep the object's initially
empty cache unchanged and leave zero adjacent fixture temporaries. Existing GPG,
independent native-B and pinned pass-otp oracles remain required. No check failure
is converted to success to continue collecting the remaining independent evidence.

Earlier full-fingerprint failures and baseline cache/leftover observations remain
the before evidence; do not overwrite or relabel them. The pre-existing-path guard
is source-reviewed unless separately exercised without modifying the UUID facility.
It is not exclusive creation under races. Permission/cleanup failures can still
leave a temporary: error-code cleanup preserves the primary error, not guaranteed
recovery. The conflicting directory is still not an existing-ciphertext rename-
failure test. Concurrency, crash durability/fsync, general resource lifetime, native
OTP parsing/mutation and Sailfish acceptance remain outside this small correction.

## Executed follow-up (2026-10-25)

The initial package plan lacked GPGME C development headers required by the actual
Gpgmepp config. After preserved configure failure, a second scoped approval added
libgpgme-dev2.0.1-2build1 and libassuan-dev3.0.2-2build1. Total54new/3updates/0remove
in the research container. Configure and build succeeded without upstream patches.

Default fingerprint-policy run confirms a real helper lookup incompatibility.
`--policy-identifiers keyids` explicitly selects the separately labelled subset;
it does not change the default or prescribe a product policy. The original zero-ID
negative was invalid because RNP treats it as wildcard. The current nonzero absent
fixture is checked against all generated primary/subkey IDs and helper lookup.
Corrected keyid run passed16runner checks and3native modes, including independent
GPG and real pass-otp oracles. Full-fingerprint incompatibility, failed-save cache
state and rename-conflict temporary remain findings. See study and local
public-backend-20261025/final-independent-review.json; no production adoption.

## Correction comparison completed (2026-10-25)

Reviewed patchf85500e... applied only to a separate factory copy. Same updated
assertions on pristine keyid control fail exactly4regressions; patched default
fingerprint run passes19runner checks/all3native modes and existing oracles.
Primed cache stays old on failedsave; directory-conflict error preserves cache
and leaves0temporary under the fixture. Pristine sources remain unchanged.
Source-collision preflight and cleanupfailure remain unexecuted; no race/crash/
fullsave/platform acceptance. Evidence: existing feature's
public-backend-corrections-20261025/independent-review.json. Container stopped;
no library installation, commit or publication.

## Optional RNP-only Sailfish build experiment (2026-11-01)

The separately reviewed rnp-only.patch is against factory e53cd22c and remains
research-only. Apply corrections.patch then rnp-only.patch with git apply --check
and git apply in a disposable copy. It adds LIBPGPFACTORY_RNP_ONLY (default OFF).
ON retains existing common/RNP code and removes UNIX GPG build dependencies,
preserves the unlock callback and rejects explicit GPG selection before singleton
lookup. OFF behavior is source-reviewed, not newly runtime-tested.

sdk-CMakeLists.txt and rnp-only-sdk-probe.spec build the existing probe.cpp into
an AArch64 executable using pinned RNP/OpenSSL/bundled sexpp. They are an
alternative SDK recipe; the earlier Botan/Linux CMakeLists.txt is unchanged.
Use a fresh approved scratch _topdir, verify all eight staged identities, and use
rpmbuild -bc only. The upstream OpenSSL feature helper builds AND RUNS.
Do not infer package installation or fixture/runtime authorization from the recipe.

The recorded r2 executable build succeeded and separate results review supports
that bounded evidence. The first GNU patch preparation failure is retained; the
final recipe uses Git without fuzz or patch changes. No public fixture was run.
Static12-object DT_NEEDED inspection found no GPGME/Assuan; this is not loader or
dlopen/provider verification. Build-tree RPATHs are not accepted for distribution.
Full dated evidence, artifact hashes, limits and next scope are in the existing
study/STATUS and SDK readiness local evidence directory.

## Executed SDK/LXC runtime profile (2026-11-01)

The optional public_backend_probe.py --sdk-target SailfishOS-5.1.0.11-aarch64
profile runs GPG2.4.8 oracles in the Ubuntu side of the SAME SDK LXC and target
backend cases through SDK3.13.5 build-shell. It requires --expect-corrections and
--sdk-artifacts-manifest with reviewed absolute artifact hashes/loader paths.
Historical default behavior remains available and was not rerun in this round.

sdk-runtime-CMakeLists.txt / rnp-sdk-runtime-fixture.spec build a NEW fixture
executable against the actual retained backend archive/core, preserving earlier
binaries and vendor sources. sdk_fixture_launch.py is synthetic test plumbing:
target-side password FD, clean environment, controlled shared temporary cwd,
artifact verification and bounded timeout. It is not an application runtime.

Native rings are protected synthetic GPG exports in pubring.gpg/secring.gpg.
No rnpkeys is required in this profile. OTP code oracle is explicitly unexecuted
when oath is absent; no substitute OTP parser/implementation exists here.

The recorded first run passed20runner checks and all four native modes, with
actual intended loader mappings, five exact GPG byte comparisons and successful
cleanup. Separate results assessment supports only bounded SDK research evidence.
No native-device, package-isolation, general lifetime or distribution acceptance.
Prior build-tree RPATHs are still research-only. Exact reviewed source snapshots,
staging/build/runtime/postrun records and hashes are in existing SDK readiness
evidence; the study/STATUS carry the current handoff.
