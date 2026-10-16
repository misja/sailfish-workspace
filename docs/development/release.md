# Release delivery preparation

Updated: 2026-10-16. Owner: separate Release Manager agent; primary assistant integrates artifacts.
Misja decides scope, target and publication. Live work is tracked by
[workspace #2](https://github.com/misja/sailfish-workspace/issues/2),
[pass #1](https://github.com/misja/sailfish-password-store/issues/1) and the linked
runtime gates. This page describes the concrete candidate, not a second backlog.

## Release notes style

Write for people using the release: contents, relevant changes, source access,
verification and concrete usage limitations. Keep wording brief and factual;
avoid promotional language, repetitive disclaimers and process narration.
Review evidence, role handoffs and approval history belong in the release issue,
not on the download page. Preserve material compatibility and safety limitations.

## Existing candidate

The [artifact manifest](release-candidate-20261016.json) records six binary and
five matching source RPMs. Runtime 2.5.24-0.6 and pass/OTP 0.5 use the reviewed
build outputs; tree and OATH are unchanged. Release copies now carry V4
EdDSA/SHA256 RPM signatures from key
`F48588CC6061DAC0C4C09F8734370471919C29A5`, plus signed checksum lists.
All main headers and payloads remain byte-identical to the unsigned build
outputs. SDK RPM verifies all eleven signatures and package digests.

Existing static inspections cover private payload/library paths, source inputs,
patches and bundled notices. Their scope and separate assistant review remain
as recorded; assembling the files is not a new native test or blanket legal
clearance. The full source packages accompany the binaries in the candidate;
retain clear adjacent source access when selecting the actual distribution route
([GNU source-delivery explanation](https://www.gnu.org/licenses/gpl-faq.en.html#SourceAndBinaryOnDifferentSites)).
Auxiliary debug RPMs are not part of this candidate and remain unvalidated.

The native Jolla compatibility plugin is not in this CLI artifact set. Its exact
vendor-source mapping, static-Assuan source/relink delivery, provider/OS-upgrade
selection and same-name distribution route remain separate unresolved work.
Misja selected CLI-first draft preparation. Native integration remains separate work.

## Before publication

- Reuse the earlier synthetic Xperia tests on Sailfish OS 5.2.0.18 and the
  recorded package-preservation check after updating to 5.2.0.20. Current runtime
  0.6 and pass/OTP 0.5 revisions have SDK build/regression evidence. Assess changes
  against that evidence; require an additional target check only for a named
  uncovered risk, including unresolved provider/command ownership. Do not require
  a complete new device test merely because package revisions changed.
- Resolve the claimed upgrade/removal policy under runtime #3; current source
  has no enforced live update exclusion. Do not turn withdrawn PR #17 into work.
- Select signing/trust and delivery. Chum builds from source through OBS and
  requires avoiding interference with Jolla packages; local RPMs are
  not a completed Chum submission. Its documented route is OBS build followed
  by submission to Testing, then maintainer promotion
  ([official developer guide](https://github.com/sailfishos-chum/main#developers-guide)).
- Obtain separate release-evidence assessment and Misja's approval of the exact
  artifacts, target and publication action. Signing and draft asset replacement are authorized; OBS writes, device changes
  and actual publication are not.

Do not rebuild the candidate or repeat historical lifecycle/algorithm trials
merely to regenerate a record. The next executable experiment needs a named target,
exact inputs/paths and authorization; no general installer is proposed here.

A separate reviewer recomputed all eleven local RPM hashes and checked the
source mapping, handoff and explicit open gates. No blocker was found for
maintainer review of this candidate; this is not release authorization.

## Signing and maintenance

The SDK's old signer cannot use the selected Ed25519 key, but its RPM verifier
can. Ubuntu RPM 6.1.0, temporarily downloaded and extracted locally, signed the
release copies using the existing local GPG agent and `rpmsign --rpmv4` with the
explicit signing fingerprint. No rebuild, private-key copy or system package
installation was needed. SDK RPM 4.16.1.3 verified all eleven signatures; the
initial missing-key control returned NOKEY. This establishes SDK verifier
compatibility, not a new device test.

Signed checksums additionally authenticate downloaded files; they do not replace
RPM signing. Preserve build hashes separately from signed release hashes.
Temporary signer packages, extracted libraries and proof/test files are removed
after delivery verification; keep evidence in the existing manifest and issue.
No signing bridge, permanent helper or additional test suite is maintained.

A fallback that changes the requested outcome requires Misja's agreement.
Record the obstacle, investigate the smallest practical alternative, and ask
before treating it as completion. In particular, signing checksums must not be
substituted for requested RPM signatures without that agreement.
