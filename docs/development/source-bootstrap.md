# Recreate public package sources

From the six public sibling checkouts, use Git, Python 3.9+ and an existing GnuPG
installation. No Sailfish SDK, Docker or LXC is needed to prepare sources.

~~~sh
python3 sailfish-workspace/tools/fetch-sources.py
python3 sailfish-workspace/tools/fetch-sources.py --offline
python3 sailfish-workspace/tools/packaging-patches.py
python3 sailfish-workspace/tools/sdk-preflight.py
~~~

--root selects another checkout parent; --component runtime or --component
password-store limits the source set. The first run downloads public sources,
signatures and public keys. --offline requires the resulting cache and repeats
signature/digest checks without downloading anything. The preflight still needs
an explicit SDK path and target to return success; zero input blockers alone
does not establish SDK readiness.

The implementation lives once in workspace tools/source_auth.py and
tools/fetch-sources.py. Runtime tools/fetch-sources.py delegates to it. Component
repositories retain their own locks, recipes, staging and tests.

## Source identity and authentication

| Inputs | Verification |
| --- | --- |
| Seven GnuPG runtime components | Existing SHA-256 pins and detached signatures from the existing primary-fingerprint allowlist |
| pass 1.7.4 | Exact annotated tag object and target commit, signature from the existing pinned primary key, then git archive with the existing prefix and exact archive digest |
| tree 2.3.2 and pass-otp 1.2.0 | Publisher HTTPS and existing archive digests; no signature verification is claimed |
| OATH Toolkit 2.6.14 | Existing archive digest, detached signature, exact pinned primary and signing-subkey fingerprints |
| OATH LGPL notice | Existing notice digest, now recorded in the component bootstrap metadata |

There are eleven upstream archives. Source versions, archive hashes, pass tag/
commit and signing fingerprints have not been updated. Source archives are the
unpatched upstream inputs: RPM recipes apply the snapshots derived from forks.

Verification uses a new temporary public-only GPG home and explicit public
keyring for each verifier. It does not use personal config/keyrings, start a GPG
agent or retrieve keys automatically. Invalid, expired, revoked, unapproved or
SHA-1-digest signatures stop the run. HTTPS redirects to HTTP are refused.
The machine's GnuPG policy still applies; dependency/security review remains a
separate release requirement.

OATH's historical publisher key is expired. Fetch renewed self-signatures via
the public key service at the already pinned full fingerprint; retain the
publisher key-reference URL as provenance. Fingerprint and signing-subkey checks
remain mandatory. This renews public key metadata, not the permitted identity.
Network failure stops preparation; no verification is fabricated or bypassed.

Primary references checked 2026-10-14:
[pass signed releases](https://www.passwordstore.org/),
[GnuPG signatures](https://gnupg.org/signature_key.html),
[OATH downloads](https://oath-toolkit.codeberg.page/download.html),
[GnuPG status format](https://github.com/gpg/gnupg/blob/master/doc/DETAILS).

## Generated inputs and records

Component sources/ contains locked upstream archives, public verification
material and recipe support files. evidence/ contains regenerated verification
records and logs. Both are local generated inputs, ignored by Git; do not copy
the maintainer's historical evidence or old caches to make a fresh clone work.

Records use stable names such as pass-tag-verification.json, tree-source.json
and oath-source.json rather than filenames tied to a previous trial date.
prepare-package.py validates identities/digests and stages all four pass/tree/
OTP/OATH recipes, including patches and project/upstream notices. It does not
authenticate a file just because a JSON record exists: first run the verifier,
or its offline mode, to recreate the source evidence.

## Select the ordinary SDK separately

Follow [SDK bootstrap](sdk-bootstrap.md). Use a normal documented SDK installation,
normally Docker directly on the Linux host. Set SAILFISH_SDK_ROOT when installed
outside ~/SailfishOS and always select SAILFISH_SDK_TARGET explicitly:

~~~sh
export SAILFISH_SDK_ROOT="$HOME/SailfishOS"
export SAILFISH_SDK_TARGET=SailfishOS-5.1.0.11-aarch64
bash sailfish-gnupg-runtime/tools/sdk-build.sh
bash sailfish-password-store/tools/sdk-build.sh
~~~

These build commands require an installed, reviewed target and the approved
build scope. The shown target is the historically available target, not proof
of Sailfish 5.2 support. Build entry points use the current checkout paths,
disable automatic build-dependency pulling and do not install generated RPMs.
Both entry points initialize a fresh SDK build tree and use rpmbuild -ba to
produce binary and source packages. The pass entry point builds tree, OATH, pass
and OTP recipes in its own project.

Runtime source packaging creates a self-contained capsule from Git-tracked
worktree files, locked archives/signatures and regenerated verification material.
Add new intended source files to Git before packaging them; untracked files are
not swept into the capsule. Its SOURCE-PROVENANCE.json records exact hashes,
base commit and any tracked-worktree changes. The source RPM contains those build inputs; its prep phase was also tested
without a sibling workspace or Git history.
This source-capsule stability does not claim byte-reproducible binary RPMs.

The optional LXC -> Ubuntu -> Docker route has additional setup needs; it is
not required for these source commands or the SDK interface. Exact vendor-source/
native pinentry delivery and complete source/binary RPM acceptance remain
separate gates. Follow [issue #5](https://github.com/misja/sailfish-workspace/issues/5)
for the fresh SDK-build acceptance state.
