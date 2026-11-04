# Minimal Sailfish librnp build probe

Prepared and executed 2026-10-25; independent result review completed 2026-11-01.
Owner: primary coordinator. The preparation/invocation text below is historical.
Use the existing SDK3.13.5 / SailfishOS-5.1.0.11-aarch64 target. The reviewed
readiness evidence observed GCC13.4.0, CMake3.31.8 and OpenSSL3.5.6 development
files. This probe builds upstream librnp only, with its OpenSSL backend and exact
bundled sexpp; it does not build/adapt libpgpfactory or solve its GPGMEpp gate.

Inputs already retained beside the existing study:

- RNP commit `aad1892e4d8423398a0b973bd0a7e4544c359afc`, archive
  `rnp-aad1892e4d8423398a0b973bd0a7e4544c359afc.tar.gz`, SHA256
  `ca0f1b82ea0867c7b9ec62f29e70edc2b609cc591cf574d38a30e9947f21594d`.
- Actual RNP sexpp gitlink `c641a2f36520bab783657a58650d9fda548b9dec`, archive
  `sexpp-c641a2f36520bab783657a58650d9fda548b9dec.tar.gz`, SHA256
  `67ccd41f678d4b1e3daa434709f8810fc57c7405a907bd5e62ee505c8364c7de`.

The spec verifies both hashes, extracts only to its new scratch build directory,
and uses actual installed RPM `%cmake` facilities. That macro configures in-source
and selects platform flags/shared libraries; no preserved tree is configured.
The upstream bundled-sexpp path is used unchanged. Existing version.cmake files
avoid fallback downloads. Tests, documentation and automatic fetch/update are off;
only `librnp` is requested with one build job. No new cross framework or feature
answers are supplied. No C++20/Botan smoke test is needed for this OpenSSL route.

## Approval and invocation

The existing supported `sfdk build-shell --maintain` dry-run proposes only two new
target packages: json-c-devel `0.18+git1-1.5.2.jolla` and bzip2-devel
`1.0.8+git3-1.7.2.jolla`, 96.3 KiB download / 241.2 KiB installed, no other planned
changes. This is not installation approval. Use the existing recorded transaction;
do not refresh repositories or substitute versions. `--maintain` is required by
actual sfdk help for inspecting/modifying the target installation. Normal build
execution uses build-shell without that installation-maintenance option.

Before execution, obtain the scoped two-package installation plus build/helper-
execution approval, verify target/tool/source identities and current scratch space
(last observed about 1 GiB free), and retain logs. No arbitrary space threshold or
automatic cleanup is introduced. Stop on a changed transaction or insufficient
space; preserve existing evidence and SDK work.

Stage the reviewed spec and both archives under a **new**, owned absolute scratch
topdir outside any Git checkout, for example `/home/ubuntu/rnp-sdk-probe-20261025`.
Create its standard `SOURCES`, `SPECS`, `BUILD`, `BUILDROOT`, `RPMS` and `SRPMS`
directories; copy the archives to `SOURCES` and spec to `SPECS`. This does not create
a repository. Do not use the default `/home/mersdk/rpmbuild` or run build-init.

Use existing `/home/ubuntu/gnupg-runtime` only as the sfdk build-shell context; do
not copy/configure/build there or modify it. From that context, after the separate
authorization and staging, the coordinator can invoke:

```sh
/home/ubuntu/SailfishOS/bin/sfdk -c target=SailfishOS-5.1.0.11-aarch64 build-shell \
  rpmbuild -bc --target aarch64 \
  --define '_topdir /home/ubuntu/rnp-sdk-probe-20261025' \
  /home/ubuntu/rnp-sdk-probe-20261025/SPECS/rnp-sdk-build-probe.spec
```

Capture the real exit status and complete logs. RPM checks build requirements;
do not bypass them with `--nodeps`. There is no `%install`, `%files`, package
installation, ldconfig, device action or RNP CLI execution. Keep the scratch build
on failure for diagnosis instead of rerunning over it or cleaning unrelated data.

## Configure execution and acceptance

**CMake configuration builds and directly runs upstream `findopensslfeatures`**
for hashes, ciphers, curves, publickey and providers. Disabling tests and selecting
only librnp does not prevent this. This execution is explicitly part of the later
approved probe, not a compile-only claim. The existing SDK must handle target
execution; do not add an emulator shim or assume a generic CMake emulator setting
is enough for this module's direct execute_process calls.

The spec retains the expanded feature-module trace (including feature values),
verbose compiler/link commands, helper and librnp ELF headers/dynamic sections and
artifact hashes. Also retain CMakeCache.txt, fossl/build/CMakeCache.txt and helper
link.txt. Verify BOTH helper and librnp are AArch64; host-built helper results are
not target feature evidence. Resolve the selected crypto library from actual
cache/link/SDK loader evidence, record its package/hash and verify target
OpenSSL3.5.6 / libcrypto.so.3 rather than host OpenSSL. Record the actual helper
execution status and feature output; inspect retained helper artifacts even if
configuration fails before the spec's final readelf commands.

Acceptance is captured configure/build success and correct target provenance,
SONAME/NEEDED and expected target library resolution, with no unplanned fetch or
source change. A helper-execution, feature or dependency failure is a finding;
do not fake answers or silently weaken algorithms. This is not synthetic crypto
runtime, Sailfish device, full public-backend, package-isolation or production
acceptance. No built library is installed anywhere by this recipe.

First SDK attempt: upstream version.cmake stalled at
`execute_process(COMMAND GIT_EXECUTABLE-NOTFOUND describe ...)`; a bounded full-
trace diagnostic returned timeout 124. The original spec/build evidence is
preserved in the coordinator's existing SDK evidence. The reviewed workaround
adds the real cached Git build tool, pinned to `2.50.1+git1-1.9.8.jolla`; it changes
no upstream source, version answers or crypto-feature detection. This is a build-
environment workaround for the observed SDK behavior, not a new RNP runtime
requirement. Its actual installation transaction still needs scoped approval.
Use a fresh `rnp-sdk-probe-20261025-r2` scratch topdir for the next attempt; keep
the first scratch tree and logs. All earlier build/helper-execution and provenance
scope remains unchanged.

Executed outcome (2026-10-25): scoped installation approved and completed using
minimal git-core closure (git-core, less, openssh, openssh-clients). Fresh r2
rpmbuild -bc completed exit 0; helper and librnp are AArch64, using target
OpenSSL 3.5.6. No original source change, produced-library installation or crypto
runtime test. Full evidence and limits are recorded in STATUS.md and the study.
