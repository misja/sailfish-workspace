# Session handoff

Updated: 2026-11-04. Decision owner: the maintainer.







## Active task — protected daemon unlock and caller assessment, 2026-11-03

Owner root; separate reviewer runtime_review. User authorized continue.
Scope/plan reviewed: UNMODIFIED pinned PasswordAgentPlugin test build using
existing SDK nemodevicelock0.4.7 (present, no install); scripted separate UI agent
on standard p2pSocket-agent/RegisterSessionAgent/QueryPassword/ValidatePassword.
Retain real RNP default callback -> InteractionRequest -> actual Secrets userInput
and native authentication plugin. No password-provider shortcut or new service.

Acceptance: protected selected entry success/TOTP, wrong/cancel after success,
empty/oversize refusal, later success prompts again, no prompts for wrong key or
symmetric fallback; ciphertext/cache/rings preserved on failures. Fixed phase
actions prevent retries consuming a future correct answer. Duplicate UI agent
registration and foreign-connection validation refuse. Record actual agent caller
PID/appId vs consumer/daemon identities, not password/input contents.

Use existing imported shared-OpenPGP policy/prechecks, compare stock GnuPG source;
do not invent per-app ACL requirement or spoof original caller. RNP requests input
from daemon connection so original consumer attribution is unproved. Headless UI
stand-in is not device graphical/passwordagent trust certification.
Qt async ValidatePassword must finish before QueryPassword reply; cancellation
uses stock contract. Agent+daemon owned/cleaned on every path; timeout margin.
Standard private SDK bus/ad00 exception reused with existing scoped approval.

Build and runtime executed in the retained SDK/LXC using synthetic fixtures only.
Fresh native fixture build exit0/50.34s. Initial runtime timed out at the scripted
UI disconnect: retained Qt connection copies kept the fixture transport alive.
Fixture-only correction exits the UI process; targeted agent rebuild exit0/2.1s.
Retry exit0/20.8s: protected decrypt/TOTP and refusal/recovery cases passed,
including agent disconnect/unavailable, duplicate registration and foreign
validation refusal. No native authentication/RNP callback replacement.
External postrun: all728 identities unchanged, no fixture roots or owned processes.
Observed authentication caller is the daemon PID/application path, not the original
consumer. Device UI and production session/per-app authorization remain untested.
Native PasswordAgent remove() iterator concern remains unmodified.
Evidence: existing secrets-plugin-review-20261101/unlock-*20261104*.json,
especially runtime-retry, runtime-retry-execution and postrun-final.
Separate resulting review runtime_review completed: no blocking finding;
34client+16outer+9target checks supported. This is an assistant review, not a
human security audit or release approval. Local research commit authorized.
Staged whitespace check flags retained upstream patch context/CRLF; patches
kept byte-identical to tested hashes. Non-patch staged whitespace check passes.

## Latest result — selected-entry pass/TOTP consumer, 2026-11-03

Owner root; separate reviewer runtime_review completed scope/source/recipe/results
review: bounded acceptance supported, no blocking finding.
Fresh SDK AArch64 build exit0/41.98s; runtime exit0/33.63s,
49client+22outer+7target checks pass incl18published RFC6238 SHA1/256/512 vectors
through real encrypted entries. Root/inherited/nested replacement/multi policies,
successful controlled save/cache/fresh reads, unknown/ambiguous/missing/empty/
unreadable policy refusals, wrong-key/corrupt/no-stale-cache and path guards pass.
Five independentGPG byte reads+seven refusals verify four saved policy outputs.
Failed atomic-output OPEN preserves ciphertext/cache; forced commit-stage failure
not tested. All632identities/keyrings unchanged;0fixture dirs/ownedprocesses,
empty outerstderr,492MiBfree. No directRNP/GPGME/Assuan consumer ELF/maps or
helper-spawn imports. RNP remains in unchanged real daemon/plugin.

Code/schema tools/research/secrets_plugin/consumer/README.md; factory-seams.patch
reuses existing policy/helpers with borrowed injection and virtual save seam.
ABI changed: fresh source build only, no old factory binary mixing.
Default singleton body preserved; full default backend build not rerun.
QtTotp pinned1d1e787, one Qt5.6 Clock API adaptation; no new OTP/parser/crypto.
Existing native API build reused; no new package install or engine experiment.
Evidence existing secrets-plugin-review-20261101/consumer-*20261103* and
consumer-final-independent-review-20261103.json. Retained SDK root:
 /home/ubuntu/secrets-pass-consumer-20261103; binaryc1cd124798fae3f3.

SDK-only synthetic keys/stores/publishedvectors; sameexplicitlyapproved disposable
Ubuntu busconfigad00 AppArmor exception, EXTERNAL auth preserved, no globalchange.
No real secrets,device,product install,newrepo,push/publication.
Separate assistant review is not human security audit or release approval.

Next material product work: protected-key daemon unlock/session/UI and production
caller authorization, then general URI/HOTP/full-store and device/distribution.
Private selection remains explicit provisioned subkey; metadata is not private
availability proof. Canonical paths not malicious-race sandbox. Imported metadata
NoAccessControl / StoredKey TODO accesscontrol remain qualifications, not resolved
by consumer success. Existing parser clamping/default semantics are not adopted
as new product requirements. No repeated engine feasibility queued.
Earlier checkpoints/results below remain historical.

## Latest result — real Crypto API / multiple recipients, 2026-11-03

Owner root; separate reviewer runtime_review completed scope/source/recipe/results
assessment: bounded acceptance supported, no blocking finding.
Actual SDK AArch64 build exit0/138.93s; real public StoredKey/Encrypt/Decrypt/
discovery/P2P API suite exit0/5.0s,22client+7target+14outer checks pass.
A/B native stored-subkey decrypt and separate GPG byte recovery on2outputs pass;
C refuses. Intended invalid/missing/secret/mismatched recipient controls pass.
Single stored-ref encrypt and success after refusals retained; rings unchanged.
QtDBus transport fixed with standard qdbus_cast exactav/a{sv}, no custom codec.

Final direct suite exit0/25.62s:18control+23protected+9runner checks pass.
Pristine16genuine failures/17, own-key positive passes.549identities unchanged;
0fixture dirs/buses/daemons/GPG agents.491upstream+17pristine+17integration
sources audited. SDK root511MiBfree; both builds and failures1-r6 preserved.

Explicit scoped exception: Ubuntu D-Bus1.16.2 in SAME SDK LXC, optional configad00
disables AppArmor mediation ONLY for disposable private Unix bus; EXTERNAL UID
auth remains. No global/LXC/device policy change. Actual target daemon/module/
client/SQLCipher preserved. Does NOT establish production confinement/auth.
Exact SQLCipher driver0.2.44-1.14.2.jolla installed with scoped approval:
1new58KiB/132KiB0up/remove,no refresh/policy change; NOKEY retained.

Evidence existing secrets-plugin-review-20261101/api-transport-*20261103* and
api-final-independent-review-20261103.json. Code/schema:
tools/research/secrets_plugin/README.md; corrections.patch then integration.patch
3c1faa60. Scratch /home/ubuntu/secrets-rnp-api-20261103-r2 retained.
Study latest result section records measured failures and exact limitations.
Separate assistant review is not human audit/release approval.
No real secrets,existing service activation,product install/device/newrepo/push.

Next product work: existing pass policy/store/OTP consumer through these requests,
all-recipient resolution before writes, protected-key unlock/session ownership and
production authorization. Same-plugin StoredKey TODO accesscontrol/imported
NoAccessControl defaults and remaining P2 findings explicit. No repeated engine
feasibility queued; no new consumer scope adopted. Earlier checkpoints historical.

## Active task checkpoint — real Crypto requests / multiple recipients, 2026-11-03

Owner: root; required separate scope/source/results reviewer: runtime_review.
User resumed implementation after checkpoint. Timeout/root-preservation fix\nprepared; separate recipe re-review completed; no unresolved material finding. Previous checkpoints below historical.
No new build/crypto/daemon execution or package install in this continuation.
Previous r5 acceptance remains intact. Do not restart feasibility research.

Prepared tools/research/secrets_plugin:
integration.patch (layered ON corrections.patch), api-probe.cpp, api-target.py,
api-run.py, integration.cmake, integration.spec, daemon-fixture.patch.
Full working tree: existing evidence secrets-plugin-review-20261101/integration-source.
Preparation/source hashes and findings: api-preparation-20261103.json there.
Source extension6b89da5fed8e50e6caf68e7c66f2ac4030a8f5b3efa539abc4a79ecb4ac8f52f
separately reviewed: no material source finding; fixture recipe re-review completed; prior blocker resolved.

Implementation: real public-only storedKey export, primary includes subkeys;
public EncryptRequest.key plus namespaced additionalRecipients typed public
packets/fingerprints. Per-payload fresh native FFI imports PUBLIC|SECRET and
rejects any secret count or missing/mismatched fingerprint, then aggregate public
encryption with all recipients. Native fingerprint parser/selection reused.
No extra stored refs in custom params; no changes to private decrypt/sign.
Keep ordinary cert/sign primary+encryption-subkey support; no primary-encrypt gate.
StoredKeyRequest same-plugin path has upstream TODO accesscontrol: standard
retrieval is NOT caller authorization. Product authorization remains unaccepted.

Real test harness prepared: pinned upstream daemon3e79aaec (local clean repo),
only main plugin-path fixture patch; actual public StoredKey/Encrypt/Decrypt
requests. Private bus/HOME/XDG/runtime/plugin paths; actual SQLCipher, no substitute.
A/B certsign primary+encsub positives, independent GPGA/B and wrongC oracles,
malformed/missing/wrongfp/secret payload negatives, unchanged rings; rerun r5suite.
Nested QtDBus QVariant decoding remains measured question, not established defect.

RESOLVED reviewer finding (historical description): outer api-run timeout115 may expire
before target bounded127+SDKstartup, leaving detached fixture daemon/bus alive
while TemporaryDirectory deletes root. Fix outer margin AND verify/stop own
scratch processes before deletion; preserve root/evidence if cleanup unproven.
Resolution reviewed: outer210s, private bus socket in root, delete fixture only\nwith target process_cleanup AND agent cleanup proof; otherwise preserve/fail.\nEstablished sfdk -C context retained. Fresh SDK build is next.
Python syntax parsing and git diff --check passed; no runtime claimed.

Target inventory: dbus-daemon/dbus-run-session/qmake and actual systemsettings,
dbus-1/QtSql/Concurrent build interfaces present. No sailfishsecretsd binary.
QSQLCIPHER driver missing; cached exact qt5-plugin-sqldriver-sqlcipher
0.2.44-1.14.2.jolla dryrun1new58KiBdownload/132KiBinstalled0up/remove,no refresh.
Installation NOT authorized/performed; request scoped approval only after concrete
source/recipe ready. No stock modification or SQLite/security bypass.
SDK root666MiBfree at inventory; retain existing artifacts.

Next: fix/review controller cleanup; record all final hashes; then fresh SDK
rpmbuild -bc staging (actual upstream full archive+reviewed plugin), exactdriver
approval/install, actual public API+retained direct regressions, source/artifact/
cleanup audit and separate results review. No execution evidence yet for new API.
All local/uncommitted; no real secrets/device/newrepo/push/publication.

## Latest result — bounded Secrets/RNP corrections, 2026-11-03

Owner: root; separate reviewer: runtime_review. Scope/source/results reviews completed;
separate assistant assessment supports bounded acceptance with no material finding. Six-file correction patch and
SDK fixture retained in tools/research/secrets_plugin; study latest section.
Actual AArch64 module/direct-class build exit0/33.14s; runtime exit0/24.2s.
Corrected18/18+protected23/23+runner9/9 pass; pristine16genuine failures/17.
Includes exact private sign/decrypt, raw-key and sibling/other-primary refusal,
honest unsupported results, empty output, ownership, symmetric-fallback and
signed-only refusal; independent GPG byte/exact-signature oracle checks pass.

Provisioned keyrings read-only/no destructor writes; pass-entry writes unaffected.
Public encryption retains native recipient semantics. Module built, never loaded.
Five exact0.2.44-1.14.2.jolla SDK packages installed with scoped approval;
0up/remove/no refresh/security-policy change; NOKEY warnings preserved.
46identities unchanged postrun;0fixture dirs/agents,empty outerstderr.
Evidence existing secrets-plugin-review-20261101/sdk-*-r5 and runtime-keyed-final*.
SDK scratch secrets-rnp-corrections-20261103-r5 retained; earlier failures preserved.

No live daemon/UI/key onboarding/multi-recipient API/native OTP/device/release
acceptance. Remaining P2 findings explicit; no human audit or release approval.
Next: maintainer considers actual Crypto API/pass-policy integration scope. No repeated engine feasibility study queued.
All work local/uncommitted; no real secrets, device, push or publication.

## Latest review — Secrets/RNP candidate, 2026-11-01

Owner: root; separate security/source reviewer: runtime_review. Review completed.
Maintainer agreed Secrets/RNP implementation direction and requested critical code
review. Pinned dcaliste plugin effb3a47 retained (17files; manifest in existing
.local-artifacts/pass-rnp-slice-20261024/secrets-plugin-review-20261101/).
Checked actual RNP0.18.1 contracts and clean local Secrets3e79aaec source.

Verdict: useful POC, do not adopt/activate unchanged with real keyrings.
P1 groups: stored-key reference/actual-key boundary; destructor-only truncating
keyring persistence/secret dirty tracking; ambiguous native handle ownership;
unimplemented APIs returning success. P2: callback/error semantics, key selection/
metadata, and false TEE capability. No exploit or runtime failure demonstrated.
Separate reviewer confirms source findings with exact qualifications in study's
latest quality/security section. No blanket race/deadlock or universal auth bypass
is claimed. Existing platform/native facilities address mechanisms; no new service.

Scope was static only: no plugin build/activation/crypto/install/device action,
real secrets, external messaging or publication. Engine feasibility remains closed.
Next: bounded correction implementation for P1 groups plus synthetic regressions,
then actual Crypto API integration; retain central pass/OTP semantics including
recipient policy. Existing libpgpfactory tests are references, not plugin evidence.
No code fixes or architecture/code adoption beyond agreed direction performed.
Earlier pending/closed feasibility handoffs below retain historical scope.

## Historical implementation-candidate review scope — 2026-11-01

Owner: root; separate reviewer: runtime_review. Scope: pinned Secrets/RNP plugin
plus shared helper/build metadata; critical quality/API/style/security assessment.
Acceptance: prioritized source-supported defects, platform contracts, bounded
unknowns and reuse advice. No build/activation/install/real secrets/device action.
Engine feasibility remains closed; this is review of the proposed integration code.

## Study closed — RNP alternative feasibility, 2026-11-01

Owner: root; separate final source/reuse reviewer: runtime_review.
Decision owner / next decision: the maintainer reviews the product implementation direction.
Acceptance met: pinned-source/platform comparison, actual Sailfish AArch64 build,
bounded SDK/LXC synthetic runtime and separate results/closing assessments.
No unresolved research blocker; no further experiment automatically queued.

Recommendation: RNP0.18.1/OpenSSL is viable for the intended OTP consumer. Carry
tested libpgpfactory entry/policy code, corrections.patch, RNP-only option and
fixtures forward as reuse basis; do not adopt the entire backend unchanged.
Concrete product prerequisites: native handle/operation cleanup on success/error,
initialization/password-provider error handling, deliberate app unlock/session
ownership, and selected OTP entry/code behavior using existing references.
Existing upstream destroy APIs/cleanup examples already solve the mechanism;
no new lifecycle/service framework or own crypto implementation is justified.

Study final section records source locations, evidence and simpler alternatives.
Final source/reuse reviewer agrees study can close; assistant assessment is not
human security audit, architecture adoption or release approval. Previous bounded
build/runtime checks remain valid; no new build/crypto/container/device action in
this closing step. Existing pass/OTP stays operational; native product not adopted.
All local changes/evidence preserved; no commit/push/publication.
Earlier active/pending handoffs below are historical.

## Historical closing scope — 2026-11-01

Owner: root; separate reviewer: runtime_review. Maintainer requested closure.
Scope: source-based ownership/error-lifetime and OTP fit assessment, pinned API
evidence, concrete reuse recommendation, distinguish product gaps from feasibility.
No new experiment/build/crypto/install/device action. Final review completed; see study closure above.

## Latest completed task — SDK/LXC runtime probe, 2026-11-01

Owner: root; separate scope/source/recipe/results reviewer: runtime_review.
Maintainer-authorized SDK/LXC-only synthetic experiment completed: target AArch64
backend plus Ubuntu GPG oracle inside SAME SDK LXC. Runtime exit0/19.25s,
all20runner checks and4native modes pass. Actual loader maps intended original
RnpCore/RNP; full-fingerprint policies,5exact GPG reads,2nativeBreads, callback/
fresh refusal, disabled-GPG selection and bounded failed-save/cache checks pass.
Direct GPG export rings work; no RNP CLI needed. OTP code oracle NOT executed
(oath absent); no substitute implementation.

Separate final assistant review supports bounded evidence,no material open
inconsistency; not human audit/release approval. New executable373d7013279533ab;
runner3b3ecbca1bb64d80; full hashes in study/evidence.15identities unchanged
postrun;0fixture dirs/0matching fixture agents,empty outer stderr. No host crypto,
device,package install,artifact installation,RPM creation or publication.
SDK fixture build/controller retained /home/ubuntu/rnp-sdk-runtime-20261101;
723MiBfree. Evidence existing SDK readiness dir/sdk-runtime-*20261101*.
Earlier active/preparation checkpoints below are historical.

Next decision owner: the maintainer; accountable research owner remains root.
Build+bounded runtime feasibility now demonstrated. Before product adoption,
separately scope native resource/error-lifetime gaps and OTP consumer slice.
Historical runner default not rerun; no general safety/device/package acceptance.
Preserve all local uncommitted work; no product route/API/service adopted.

## Active task — SDK/LXC synthetic runtime probe, 2026-11-01

Owner: root; required separate reviewer: runtime_review.
Maintainer authorized continue, explicitly keeping execution inside SDK/LXC.
Scope/criteria: loader evidence for existing project libs; native refuse/normal/
read-b plus GPG byte oracles; failed-save/cache checks; explicit disabled GPG
selection before/after RNP; preserve prior binaries and clean synthetic homes.
Read-only inventory shows target lacks gpg/rnpkeys/oath; same SDK Ubuntu has
GPG2.4.8. Use existing GPG-format ring loading, no new tool installation.
Explicit SDK fixture profile proposed; OTP code oracle remains unexecuted.
Scope/source/recipe review pending; no synthetic crypto executed this task yet.
Existing prior build artifacts remain accepted only as bounded compile/link evidence.

## Latest result — RNP-only SDK backend build completed, 2026-11-01

Owner: root; separate scope/source/recipe/results reviewer: sdk_review.
Bounded SDK executable compile/link experiment completed: RNP-only optional backend
using existing classes builds on SailfishOS5.1.0.11-aarch64/SDK3.13.5 with OpenSSL.
Eight staged hashes verified;1,154 original files checked against expected
originals+two reviewed patches,zero mismatches/exactly4modified factory files.
Executable,RnpCore,librnp/helper all AArch64; static12-object dependency closure
contains no GPGME/Assuan. No public fixture or crypto runtime execution.

Separate final assistant review supports bounded build evidence,no material open
inconsistency. Not human security audit/release approval. Spec aaa943827f0b9a60;
patch d3540aa9d212dbd8; executable93b42f99b3be172d. Full hashes in study/evidence.
First GNU-patch prep failure retained; fresh r2 uses reviewed Git application.
Compiler warnings retained; build RPATHs not distribution-accepted.
Evidence existing SDK readiness dir:rnp-only-*20261101*.json/log.
Scratch /home/ubuntu/pass-rnp-only-sdk-probe-20261101-r2 retained;732MiB free.
No package install,produced-artifact installation,RPM,device or publication action.
Next: separately reviewed synthetic runtime/selection/callback experiment using
existing fixtures. No product adoption. Preserve all local work.
All earlier pending-source/build checkpoints below are historical.

## Active RNP-only experiment — 2026-11-01

Owner: root; required reviewer: sdk_review. Maintainer directed this route.
Scope/acceptance: optional two-file research patch using existing RNP classes;
default OFF unchanged, ON removes GPG build dependencies, retains unlock callback
and refuses explicit GPG selection before singleton lookup. Separate scope review
caught callback propagation; explicit RNP_ONLY branch resolves it.
Prepared tools/research/public_backend/rnp-only.patch; pristine apply check passed.
Corrected-tree application, source review and executable compile/link pending.
No build/install/runtime/device action. Study latest section has handoff.
This supersedes the earlier undecided next-route wording below; no product adoption.

## Latest continuation — 2026-11-01

Owner: root; required independent reviewer: sdk_review.
Scope/acceptance: close retained SDK engine build result review, inspect full
factory dependency/API gap before any adaptation, record bounded findings.
Separate assistant review supports the RNP AArch64/OpenSSL build feasibility;
no material inconsistency. Not human audit/runtime/package/device acceptance.
Earlier "final results review pending" statements below are historical.

Full backend gap is more than GPGMEpp: pinned factory uses GPGME C API, yet
unconditionally calls gpgme_op_keysign, absent from actual SDK GPGME1.2.0 header.
CMake-only relinking is insufficient. No patch/build/install was attempted.
Library export/complete field audit remains open; guessed host-side target library
paths failed and establish no absence claim. See study's 2026-11-01 section and
existing SDK evidence/gpgme-api-investigation-20261101.json.
Next: complete target API investigation; compare explicit existing-class RNP-only
build option versus compatible isolated GPGME dependency, then separately review
scope before implementation. No option adopted; no new dependency authorized.

## Active objective — read this first

Explore a reusable backend with functionality comparable to pass. First intended
consumer is an app to use/manage OTP codes. General password-store management GUI
is not the objective. Browserpass-like integration is future separate work.
Keep pass as functional/implementation baseline; do not assume full Bash/GnuPG
compatibility or design a new API/service in advance.

The maintainer authorized the next thin vertical-slice experiment and explicitly reiterated:
keep researching known implementations; do not invent unnecessary mechanisms.
Current owner: primary coordinator. Separate Builder implements; separate reviewer
checks substantial scope, source/diffs before execution and results afterwards.
Assistant assessment is not a human security audit or release authorization.
Read parent/child AGENTS baseline1.3.0, accepted ADR0001 and governance/workflow.

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

## SDK inventory and revised build concept reviewed — 2026-10-25

User requested ONLY1actualSDKdependencycheck and2prepare smallestbuildprobe.
Owner: primary coordinator. Actual SDK3.13.5/SailfishOS-5.1.0.11-aarch64 read-only
queries: GCC13.4 crosscompiler offersC++17/20 flags; CMake3.31.8. NO compile/link
proof. OpenSSL3.5.6devel present. Botan2/3,sexpp,GPGMEpp absent in installed/cached
metadata. GPGME C1.2 devel present but no C++wrapper; json-c/bzip2devel missing
but exact cached candidates found. Cache2026-06-30 stale, not current5.2absence.
No refresh/install/configure/build/probe/device action. ExistingSDKleftRUNNING
as found; separate Ubuntu researchcontainer remainsSTOPPED.

Prepared smallestbuild concept in study latest SDKreadiness section: first pinned
RNP0.18.1+its exactsexppsubmodule using maintainedOpenSSL backend/nativeRPMcmake
facilities, targetlibrnp only. Not Botan3bydefault or owncrossframework; public
backendGPGMEpp gap NOT solved/removed by engine-only probe. Need later exactSDK
packageproposal/permission forjson-c-devel,bzip2-devel and spacecheck(~1GiBfree).
Sourcepinsexppc641a2f36520bab783657a58650d9fda548b9dec; no source build run.

User requested independent reviewer finish. save_review resumed after usage limit:
inventory supported; material finding corrected in plan: RNP OpenSSL configure
builds AND RUNS findopensslfeatures for5feature categories. This is not a compile/
link-only build. Future scope must explicitly include that helper and actual SDK
target-execution/library handling; no fakefeature answers/emulator shim.
No helper/configure/build executed. Reviewer confirmed revised concept; no open
material preparation finding. Future gates remain:
complete source/hash intake, exact missing-package transaction, complete scratch
recipe/source review and scoped authorization required before future execution.
Evidence `.local-artifacts/pass-rnp-slice-20261024/sailfish-sdk-readiness-20261025/`.
Keep existingCLI/nativepatch and local dirty changes; no newrepo/push/publication.

## Latest bounded correction result — 2026-10-25

Owner: primary coordinator; Builder `builder`; independent scope/source/results
reviewer `save_review`. User-authorized correction sequence completed. Upstream
HEAD remains pinned e53cd22c; no newer merged fix. Reviewable research patch:
`tools/research/public_backend/corrections.patch`,SHA256
f85500e1865c774aaf8c1dfb4f46de911272ed93c404a78a921a562b79ffcd60.
Exactly2vendor files in separate copy: fingerprint predicate extended; cache swap
after successful rename; existing staging error path includes rename and best-
effort nonthrowing cleanup/rethrow. No new writer/API/dependency/install/OTP fix.

Meaningful pristine control with SAME new assertions: expectedexit1/exactly4native
regression failures across3gaps; existing oracles pass. Patched defaultfullfinger-
print run:exit0,19runner checks/all3native modes pass.5exact GPG reads+2nativeB
reads+2actual pass-otp codes pass. Missingrecipient preserves original AND primed
cache; directoryconflict preserves cache/reports fs error/leaves0own temp.
Initial malformed patch artifact caught before use/preserved; corrected patch
applycheck/source gate passed. Original1086sourcefiles unchanged; only2copyfiles
differ. Independent resultreview found no unresolved evidence inconsistency.

Current reviewed regression source:CPPfbe01417f6efba09fdec2edbe22a52e8e4d5dee021c8b6a6b1ebe9206b7938e5;
runner2c29293535985ad370e4820984b5e9c42c8adf42762703727aa9cc62761ec508.
Patchedbinary62a636d331d306aa7b136c844a11a78c6ad035339b608ef681284221553170ed.
--expect-corrections is explicit/defaultoff; defaultpolicy remains fingerprints.
Pristine control's expectedpatchhash is NOT appliedsource provenance; buildrecords
label control/patched separately. All earlier failures/source snapshots preserved.

Evidence: `.local-artifacts/pass-rnp-slice-20261024/public-backend-corrections-20261025/`;
study latest bounded-corrections section. ContainerSTOPPED,0fixture dirs/0agents
externally verified. Retained original and corrected dirs:
/home/ubuntu/public-backend-20261025 and /home/ubuntu/public-backend-corrections-20261025.
No reinstall needed. Currenttask made NO extra package change; previous54new3up
container-only approvals remain historical. No upstream checkout/adoption change.

Limits: collision branch/cleanup failure unexecuted; preflight not raceproof;
cleanup best effort. Directory conflict is NOT existing-file rename failure.
No concurrency/crash/fsync/native-lifetime/general-safety/Sailfish/product release
acceptance. No newrepo,commit,push,merge/publication. Maintainer next reviews patch/
reuse/adoption/platform scope; existing CLI and OTPappend bug remain unchanged.
Preserve all local uncommitted work.

## Latest public-backend result — 2026-10-25

Owner: primary coordinator; separate Builder `builder`; independent scope/source/
results reviewer `save_review`. User instructed continuation after session checkpoint.
Unchanged public libpgpfactory+RNP built successfully outside GUI.54new/3updated/
0removed packages in retained LXC under two explicit approvals; no reinstall needed.
Initial configure failure(missing GPGMEdev) preserved. Source1086files byte-unchanged,
loader resolves buildtreeRnpCore/RNP and still links GPGME/Assuan.

Confirmed compatibility gap: original full-fingerprint .gpg-id is rejected by
listKeys display-string postfilter. Diagnostic lookupfpr0/keyid1,policyunresolved1,
save0. Do not label this harness failure or silently require keyids for product.
Separate explicit keyid fixture now completed. First negative used allzero keyid,
which RNP treats as wildcard; preserved as test-fixture error, NOT save defect.
Corrected verified-absent NONZERO locator run:exit0,16runner checks pass,3native
modes pass. Public list/find/decrypt/save,root/inherited/nested/multi policies,
fresh auth refusal,no-save on unresolved policy and missing-recipient preservation
measured.5exact GPG reads+2nativeBreads+2actual pinnedpass-otp codes pass.
Caveats: failedsave cache holds new proposed text; rename-directory conflict leaves
1temporary (fixture cleanup removed it). No native URI mutation/fullpass/Sailfish/
production/general safety acceptance. Reviewer found no evidence inconsistency.

Current reviewed files:
CPP36d3ebf7edba5c8008d3f51930324b6fce030d8fe087b60eb0e7638d18b4bb85
runner03fc86264202fb4a90189d8120cb67686802f5b29c371beb1e31cc8a840a9b02
binaryfbd083c83b65686ec1f4aa824fe864eb1b02f59bb2b3330fdda39e623bab34cb.
Source: tools/research/public_backend/{CMakeLists.txt,probe.cpp,README.md} and
tools/research/public_backend_probe.py. Original,diagnostic,keyidwildcard and final
runs preserved under `.local-artifacts/pass-rnp-slice-20261024/public-backend-20261025/`.
Read study latest completed-public-backend section and final-independent-review.json.
Earlier checkpoint superseded; diagnostic and corrected subset ARE now executed.
Container local:sailfish-rnp-probe-20261024 STOPPED,0fixture dirs/0agents externally
verified. Source/build dirs retained /home/ubuntu/public-backend-20261025.

Next decision: separately scoped/reviewed fix/reuse proposal for fingerprint
lookup and native lifetime/error handling before adoption. No public API/product
route/migration,parser/writer,dependency removal or source patch accepted.
OTP append baseline bug remains separate/unpatched. No host/SDK/device changes,
real secrets,newrepo,push/merge/publication. Preserve all uncommitted work.

## Latest native output result — 2026-10-25

Owner: primary coordinator; separate Builder `builder`; independent scope/source/
results reviewer `reviewer`. User-authorized ctypes probe executed once as ubuntu
in retained LXC using existing librnp0.18.1. No install/product backend/OTP change.
Four cases passed: original intact before finish; successful finish replaces and
GPG-decrypts exactly; missing recipient and wrong-password native decrypt preserve
without finish; induced finish failure returns error/preserves original.
That failed finish leaves1temporary after native destroy; own fixture cleanup
removed it. Destroy is not a checked commit or abort substitute.
Script: tools/research/librnp_output_probe.py, SHA256
e553b7a89e8137964f78ab96133978be12386786598192d413e2b7b898c93096.
Evidence: `.local-artifacts/pass-rnp-slice-20261024/native-output-20261025/`.
Independent review found no bounded evidence inconsistency. External cleanup:
0fixture dirs/0agents; container STOPPED. No general writer safety/Sailfish/
crash/concurrency acceptance. Study latest native-probe section has full limits.

## Prior real-pass slice result — 2026-10-24

Accountable owner: primary coordinator; separate Builder `builder`; independent
scope/source/results reviewer `reviewer`. Reviewed real-source slice executed once
as ubuntu in retained LXC:32checks passed (modern keys, cross-engine store IO,
nested/multiple recipients, actual OTP insert/append/update/code and list/find).
Two material preservation gaps remain: missing-recipient direct insert preserves
the original with GPG but removes the destination with RNP; wrong-password OTP
append returns success and changes original ciphertext with BOTH variants.
Resulting append plaintext was not independently measured. Suite pass does not
mean failed-write safety acceptance or production readiness. No staging was added.
Independent review found no evidence inconsistency. External cleanup:0fixture
temp directories,0agents; container STOPPED. Full findings are in the study's
latest executed-slice section and local slice-* evidence/independent-review.json.

## Completed and preserved

- Single study: [OpenPGP architecture study](docs/development/openpgp-architecture-study-20261018.md).
  Contains source/platform evidence, source pins, capability matrix, review history,
  architecture alternatives and latest research-first refinement. No migration accepted.
- Initial RSA engine probe: tools/research/rnp_probe.py. Executed in isolated LXC:
  11cases passed, independently reviewed. Exact evidence under
  `.local-artifacts/rnp-probe-20261024/`, including original failure, diagnosed
  FD-option-order correction, final results, versions, review and cleanup.
  This is NOT evidence for the new slice, Curve25519 or Sailfish acceptance.
- Existing retained container: `local:sailfish-rnp-probe-20261024`, default project,
  STOPPED. Ubuntu26.04 image fingerprint
  `278bb60fb5e20a059924f02334fbdd591ae1ec908795bc96738751c49cd60dd6`;
  unprivileged, no host mounts,2CPU/2GiB/8GiB. GPG2.4.8, RNP0.18.1-1build1,
  OATH2.6.14, Python3.14. Earlier7packages installed only here; tree2.3.1-1 added
  for real pass list/find (1new0upgrade0remove). No reinstall needed.
- Host install proposal withdrawn; sudo stopped before apt, RNP/librnp0 remain
  absent on host. Host/SDK/device not modified by package installation/probes.
- New slice preparation: `.local-artifacts/pass-rnp-slice-20261024/` contains
  baseline/pass, baseline/otp.bash, baseline/sources.json, upstream-research.json,
  and handoff.json. Baseline exports are exact immutable Git-source bytes.

## Research decision before implementation

Do NOT resurrect the provisional custom Python Store/recipient walker/OTP parser.
It was rejected before write/run. The revised separately scoped direction retains
real pass/OTP store, recipient, list/find and OTP logic; only fixture crypto calls
use native RNP. Compare GPGbaseline versus RNPvariant on the SAME synthetic store.

Known implementations inspected at exact dated commits (see upstream-research.json):
QtPass RealPass delegates real pass; ImitatePass is a larger Qt implementation.
Pass-simple has a separate C++17 libpgpfactory/RnpCore backend WITHOUT the QtGUI;
its Linux build also requires GPGMEpp/libgpg-error and FetchContents RNPv0.18.1.
It remains a reuse candidate, not an adopted dependency or audited component.
Gopass has existing store policy and pquerna/otp reuse, not an evidenced RNPbackend.
Do not turn their project-specific rules into our requirements or silently fetch/build them.

## Completed source investigation — 2026-10-24

Owner: primary coordinator/researcher; separate reviewer `save_review`.
RNP0.18.1 CLI opens/truncates output before recipient lookup, then discards failed
output. Existing librnp RANDOM output plus checked finish already supplies adjacent
temp+rename, but failed finish can leave a temporary; no fsync/crash guarantee.
Pinned OTP append loses decrypt status in process substitution; current upstream
7bb50dbc also lacks a guard. Shell-only checks confirm pipefail is insufficient.
Pass already has ciphertext-temp/conditional-rename examples. Standalone
pass-simple lower-level writes use direct output; later public-interface research
found existing staging in InterfacePassFile::encrypt (see latest section). QtPass
has staged placement with broader Qt/platform policy.
17immutable sources/hashes and findings: existing study latest failed-save section,
`.local-artifacts/pass-rnp-slice-20261024/source-research/manifest.json` and review.
No crypto rerun, container start, installation or production code change this round.

## Current artifacts and next investigation

`tools/research/prepare_pass_rnp_fixture.py` and `pass_rnp_slice.py` now exist,
were independently reviewed before execution and have actual slice evidence.
Harness SHA256:9af655e3ca203bffcdd060c02203e4cf41c4013da3d8b87c6ef5faaff8004961;
preparer:c3df3459beb9cf6f3650a075dd51395bf962549804e25bcd2756dbc88a77c09f.
Exact generated-source diffs, wrapper hashes and copied input identities are
recorded in `.local-artifacts/pass-rnp-slice-20261024/`. Original sources remain
pass24d4ab48afcc66dcccc14591c41c6fd2c750a4a3 and
OTP e5dc12c98c3b134eb8e65f00afabee9b525fac93; no backports reapplied.
Historical research artifacts are retained in the local workspace commits.

The reviewed native-output proposal is now executed; do not repeat it as pending.
Existing native RANDOM output+checked finish solves the measured output gap, with
a demonstrated leftover on failed finish and destroy auto-commit caveat.
Next integration needs bounded scope/acceptance and separate review before build;
no product route/API/library integration or recovery framework is adopted.
The direct CLI adaptation remains unsafe as measured. Guarded OTP append decrypt
is still a separate backend-independent correction; no OTP patch was made.
Sailfish build/dependency acceptance and broader features remain unmeasured.

No host install, SDK/device changes, real secrets, new repository, push, merge or
publication. Existing retained container is stopped; no reinstall is needed.

## Prior release handoff (separate from active research)

WorkspacePR16, runtimePR22, password-storePR12 were merged with the maintainer's explicit
permission2026-10-18; merged trees matched reviewed heads. Merge commits recorded
as workspace185d8b5, runtime0b069fa, password-storefc095fb (squash policy).
Runtime2.5.24-0.7/pass1.7.4-0.6/OTP1.2.0-0.6 signed release assets and13downloadchecks
were reviewed; drafts remained unpublished at last verified release handoff.
Do not mutate drafts/tags/assets or infer publication authorization from this study.
Historical manifest/source pins remain in docs/development/release-candidate-20261017.json
and `.local-artifacts/release-20261017-cli/`. Live release records:
[workspace#2](https://github.com/misja/sailfish-workspace/issues/2),
[runtime#3](https://github.com/misja/sailfish-gnupg-runtime/issues/3).
Native/OS-upgrade/provider/distribution limitations retain recorded scope;
no installed-new-RPM device acceptance was established by the synthetic tests.

SDK probe scope extension 2026-11-01: separate recipe review sdk_review completed;
required expanded feature trace retained. Actual target GNU patch2.7.6 available,
858MiB free; sufficient-space success not claimed. Next bounded execution: fresh
scratch rpmbuild -bc links existing public harness with two reviewed patches,
OpenSSL and bundled sexpp. Acceptance: staged hashes, AArch64 executable/link and
transitive ELF evidence, changed-source audit, independent resulting review.
Includes upstream feature-helper execution only; no fixture crypto runtime,
installation, RPM creation or device action. Sandbox snap-confine failures were
resolved by approved outside-sandbox read-only invocation; no security setting
change. Source/hash staging and build authorization via scoped tool approval.
