# Release delivery

Updated: 2026-10-17. Owner: separate Release Manager for presentation;
Builder/Packager for packaging. Misja authorizes publication.
Live delivery work: [workspace #2](https://github.com/misja/sailfish-workspace/issues/2).

## Release notes style

Write for people using the release: purpose, contents, relevant changes, source
access and concrete usage limits. Explain component boundaries without assuming
our earlier conversations. Keep review/approval history in issues. The same rule
applies to READMEs and documentation across related repositories.

## Candidate and evidence

The [2026-10-17 candidate](release-candidate-20261017.json) contains
`sailfish-gnupg-runtime` 2.5.24-0.7, pass 1.7.4-0.6 and OTP 1.2.0-0.6.
The [2026-10-16 manifest](release-candidate-20261016.json) retains the identities
of the earlier runtime 0.6 and pass/OTP 0.5 draft assets. Tree 2.3.2-0.1 and OATH 2.6.14-0.3 remain unchanged.
It was built and inspected with SDK 3.13.5 / SailfishOS-5.1.0.11-aarch64.
Existing pass has an exact dependency on the previous runtime: users upgrading
pass/OTP must update all three packages in the same package transaction. An
isolated SDK RPM database check passed for that coordinated transition.
SDK signature verification and separate cryptographic assistant review of all
eleven signed RPMs, including source RPMs, are complete. These checks are not
a human security audit or authorization to publish. The draft refresh, download
verification and separate draft-metadata review are tracked in the live delivery
issue and STATUS.md.

Earlier synthetic Xperia checks remain evidence within their recorded scope.
The final-removal hook was also checked on the dev Xperia 5.2.0.20, using copied
GnuPG 2.5.24 binaries, empty synthetic homes and the exact proposed hook with a
temporary prefix. That confirms native selection/shutdown behavior; it does not
claim an installed new-package transaction or full new device acceptance.
Additional testing must address a named changed behavior, not recreate history.

The runtime starts agents on demand. Updates leave verified old agents running;
new agent fixes become active after those agents exit. The removal hook refuses
detected private clients before requesting shutdown. It does not enforce global
start exclusion or promise completion of every arbitrary agent session. See
[the maintenance notes](https://github.com/misja/sailfish-gnupg-runtime/blob/main/docs/lifecycle-contract.md).

## Signing and delivery

All distributed binary and source RPMs carry V4 EdDSA/SHA256 signatures from
`F48588CC6061DAC0C4C09F8734370471919C29A5`. The delivery consists of those RPMs
and the public certificate; separate checksum/signature files are unnecessary
for this release workflow. Keep unsigned build and signed release hashes in
the evidence record. The existing SDK RPM verified this signature format.
A modern distribution signer is used locally with the existing GPG agent; no
private key is copied. Temporary downloaded/extracted tools are removed afterwards.

Matching source RPMs accompany every binary. Existing notices/source inspections
remain valid within scope; this is not blanket legal clearance. Native graphical
integration and auxiliary debug RPMs are outside this CLI delivery.

Public command ownership and compatible GNU Bash/provider selection remain
component installation considerations. GitHub drafts are not a Chum/OBS
submission; that route has separate platform policy and trust requirements.
Before publication, check exact reviewed assets, current user-facing limitations
and Misja's explicit authorization. Do not invent a service framework to support
an unreviewed extra lifecycle guarantee.

A fallback changing the requested outcome needs maintainer agreement: signing
checksums must not silently replace requested RPM signatures. Use existing
upstream/platform behavior before designing additional requirements.
