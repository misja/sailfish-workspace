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

The [artifact manifest](release-candidate-20261016.json) identifies six binary
RPMs and five matching source RPMs, copied locally with SHA256SUMS. Runtime
2.5.24-0.6, pass 1.7.4-0.5 and OTP 1.2.0-0.5 use their reviewed build outputs;
tree 2.3.2-0.1 and OATH 2.6.14-0.3 are unchanged. All eleven hashes match the
existing records; RPM digest checks pass and binary SOURCERPM links match the
included source packages. The RPM files are unsigned. SHA256SUMS has since been signed locally with
Misja's Ed25519 key `F48588CC6061DAC0C4C09F8734370471919C29A5`; a separate
reviewer verified it using only the public certificate and rechecked all eleven
hashes. This authenticates the checksum file against that key, not the separately
mutable README/JSON or an independently established publisher identity. It does
not add signatures inside the RPMs. The existing SDK signing route cannot use
this key (GnuPG 2.0.4; upstream RPM 4.16 signer accepts RSA/DSA only). No key was
copied and no package/tool was installed. Digests alone do not authenticate a publisher.

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
  requires avoiding interference with Jolla packages; local unsigned RPMs are
  not a completed Chum submission. Its documented route is OBS build followed
  by submission to Testing, then maintainer promotion
  ([official developer guide](https://github.com/sailfishos-chum/main#developers-guide)).
- Obtain separate release-evidence assessment and Misja's approval of the exact
  artifacts, target and publication action. No key operation, OBS write, external
  request, device change or binary publication has been performed here.

Do not rebuild the candidate or repeat historical lifecycle/algorithm trials
merely to regenerate a record. The next executable experiment needs a named target,
exact inputs/paths and authorization; no general installer is proposed here.

A separate reviewer recomputed all eleven local RPM hashes and checked the
source mapping, handoff and explicit open gates. No blocker was found for
maintainer review of this candidate; this is not release authorization.

## Signing decision

Signed checksums authenticate downloaded RPM bytes against the trusted signing
key; they do not supply RPM signatures checked by the package manager. This is
a fallback, not completion of package signing. Existing SDK signing cannot use
the selected Ed25519 key. Before choosing another signer, establish whether the
target RPM verifier supports that algorithm. If supported, a modern host signer
could sign copies of the reviewed RPMs using the local agent, without rebuilding
or copying private keys. Tool installation and replacement release assets need
scoped authorization and review. No signing bridge or new key is proposed.

Current CLI drafts are on GitHub with eleven RPMs, per-release signed checksums
and the public certificate. They remain drafts; signing and publication decisions
are tracked in workspace #2.
