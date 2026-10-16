# Clean public-checkout SDK build, 2026-10-15

The merged public source-bootstrap PRs were reviewed by Misja. This build exposed
two additional packaging/bootstrap fixes, subsequently approved and merged in
workspace PR #8, runtime PR #9 and password-store PR #6. This dated record
preserves its tested inputs; it is not a build of runtime candidate 0.6.
The implementing assistant ran the builds and checks below; this is not an
independent human security audit.

## Result and tested scope

Six public repositories were freshly cloned inside the existing SDK environment.
Source archives and verification material were obtained anew, preserving every
locked upstream version/digest/signer. No original local source cache or trial
evidence was copied. The environment was SDK 3.13.5 with the already installed
SailfishOS-5.1.0.11-aarch64 target, using the maintainer's optional outer
LXC/Ubuntu container and Docker SDK. The ordinary SDK interface remains the
baseline; the outer container is not a prerequisite.

The corrected build route produced six main binary packages and five matching
source RPMs: private GnuPG, tree, pass, OATH library/tool and OTP. OATH has two
binary packages from one source RPM. Six additional debug/debugsource packages
were generated and have not been release-validated.

See the bounded [machine-readable record](build-records/clean-sdk-20261015.json)
for initial public commit IDs, hashes of tested fix files, package hashes,
dependencies, ELF results and inspection outcomes. Raw logs and binary artifacts
remain in the isolated test directory; they were not published.

## Findings and fixes

A fresh pass project failed before compilation because build-shell requires a
build tree. Add explicit build-init when .sfdk is missing. The fake-SDK tests
checked argument forwarding; the actual SDK run established this additional
initialization requirement.

The original runtime build made a binary RPM, but its Source0 named only a build
script and source-RPM assembly failed. Add a complete source capsule from tracked
public project files, seven locked upstream archives, detached signatures,
public key and regenerated verification JSON. It records the base Git commit,
worktree state and exact input hashes. Untracked files and symlinks are excluded/
rejected. Tar ownership/timestamps and public file modes are normalized.

The runtime recipe unpacks this capsule with the standard RPM setup step.
Both build entrypoints use explicit SDK/target selection and standard
build-shell rpmbuild -ba, with automatic build-dependency pulling disabled.
Source versions and source adaptation patches were not changed.

## Checks actually run

- Runtime: 14 AArch64 ELF objects, private-only RUNPATH, exact wrapper/policy
  payloads, retained platform requirements, no public private-library SONAME
  provides/requires, no RPM scriptlets, expected project/component notices.
- Runtime source RPM: exact recipe and capsule bytes, all 106 input-file hashes,
  seven matching upstream archives and required source/notices/verification files.
  The source capsule preserves its exact build input hashes; the read-only
  inspector was extended after compilation and is identified in the JSON record.
- Isolated source-RPM input preparation check: extracted only the recipe and
  capsule from the source RPM into an empty directory and ran rpmbuild -bp.
  All seven upstream components prepared successfully without a Git repository,
  sibling workspace or external old source cache. A second full SRPM rebuild
  was not performed.
- pass/tree: exact wrappers/private-engine binding, payload paths, dependency and
  notice checks, matching source inputs and source-RPM hashes. The built tree
  utility's version was exercised under the SDK.
- OATH/OTP: private library/backend binding, ELF paths, exact upstream notices,
  matching source inputs, and OTP payload equal to upstream plus both recorded
  patches. Packaged crypto programs were not executed by the inspectors.
- Repository tests: 23 workspace, five runtime and four password-store checks
  passed (32 total), including source-capsule completeness/determinism/rejection
  and SDK initialization/argument checks.
- OATH upstream make-check: 10 passed, one skipped (tst_usersfile.sh), zero failed/
  errors. The skip is recorded, not counted as a pass.

No binary package, dependency or target was installed. Existing SDK build
dependencies/toolchain were reused; provisioning a new SDK was not repeated.
No device, real keys/stores/OTP material, OBS write or upstream submission was used.

## Remaining limits

The SDK debugsource collector warned that it could not find
build/libksba-1.8.1-build/src/asn1-parse.c. The locked upstream archive contains
both the parser C and Y sources, retained in the complete source capsule.
Auxiliary debug-package delivery still needs review; do not label those packages
release-ready based on this build.

This establishes the tested source/build and static package checks on the
selected historical toolchain. It does not establish Sailfish 5.2/device support,
production lifecycle, provider/upgrade behavior or release/distribution acceptance.
[Issue #5](https://github.com/misja/sailfish-workspace/issues/5) owns bootstrap
review state; the separate component/distribution gates remain open.
