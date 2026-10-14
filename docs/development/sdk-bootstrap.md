# From public sources to a package build

Work owner and current status: [workspace issue #5](https://github.com/misja/sailfish-workspace/issues/5).
The source workspace is portable. SDK provisioning and complete public source
staging are still being prepared. This is the first implementation slice.

## Inspect before changing the environment

With Git and Python 3.9 or later:

~~~sh
python3 sailfish-workspace/tools/workspace.py status
python3 sailfish-workspace/tools/sdk-preflight.py
python3 sailfish-workspace/tools/sdk-preflight.py --json
~~~

Run from the directory containing the six checkouts. The preflight also accepts
--root elsewhere and --component runtime or --component password-store.
It checks only explicit public archive and record filenames. It does not scan
user homes, stores or keyrings; source symlinks are refused. Archives are hashed
against the source locks. Existing evidence files are marked present_unverified:
presence and archive digests do not prove signature authentication.

For an SDK installed on the machine running this command, supply its path and
an explicitly selected target:

~~~sh
python3 sailfish-workspace/tools/sdk-preflight.py --sdk-root /path/to/SailfishOS --target SailfishOS-5.1.0.11-aarch64
~~~

The checker does not run sfdk or virtualization commands. Exit 1 means known
files or explicit SDK/target settings are missing or invalid. Exit 0 means only
those preliminary checks passed; it does not confirm target installation, source
signatures, native pinentry inputs or a working package build. An SDK inside an
LXD container is not found by checking the host's filesystem.

## SDK route and target selection

Use the [official SDK installation guide](https://docs.sailfishos.org/Tools/Sailfish_SDK/Installation/)
and [local package workflow](https://docs.sailfishos.org/Tools/Sailfish_SDK/Building_packages/)
as primary references, checked 2026-10-14. Select a host and virtualization route
supported by that documentation before provisioning. The documented SDK routes
use Docker or VirtualBox for the build engine. Our outer LXD container and image
adaptation are a local experiment, not a required public-workspace layout.

The recorded SDK is 3.13.5. The existing build scripts use
SailfishOS-5.1.0.11-aarch64. That is historical build evidence, not verification
for the intended Sailfish OS 5.2 release or the maintainer's current device.
Keep [target selection](release-targets.md) explicit. Record installed tooling
and a reviewed SDK-to-release mapping before changing targets.

Host checkouts keep their GitHub names. Existing prototype scripts still expect
/home/ubuntu/gnupg-runtime and /home/ubuntu/password-store inside the SDK. Do not
rename the host directories back to satisfy those guards. Parameterizing SDK
project paths and removing dated record dependencies is follow-up implementation.

SDK downloads, virtualization/system configuration and installations require
their own concrete approval. No install command is run by the preflight.

## Source staging gaps

| Component | Existing public implementation | Remaining reproducibility work |
| --- | --- | --- |
| GnuPG runtime | Locked digests and signer allowlist; fetch-sources.py fetches public sources/signatures into a dedicated verification home | Remove fixed SDK path guard safely; reproduce public signature evidence and test the complete build |
| pass/tree | Locked archive identities; prepare-package.py checks selected authentication fields and stages inputs | Recreate signed-tag/archive and tree provenance records without dated private evidence; export authenticated base archives consistently |
| pass-otp/OATH | Version/digest pins and recipes | Provide public fetch/authentication/staging for archives, OATH notices and patches |
| Native pinentry | Pinned fork commits, materializer and full-tree patch equality | Establish exact vendor-source identity and prepare all provenance/relink inputs separately |

Do not fabricate a successful verification JSON to satisfy an old script.
Recreate evidence from the selected public sources with an isolated public-key
verification home. Do not apply packaging patches to an already patched fork
archive. The preflight intentionally does not label native pinentry ready.

A source audit found the runtime RPM's component-license directory staging was
broken; its separate fix has a synthetic test of the actual install fragment.
A full SDK build and resulting binary/source-RPM notice inspection remain due.

## Completion evidence

Before closing issue #5, demonstrate a fresh public checkout, authenticated
source staging and clean package build in the approved SDK. Record exact Git
revisions, source digests/signers, SDK/target, commands and actual outputs.
Do not reuse private local caches as unexplained prerequisites.

Work status and review blockers stay in the issue and project board. This
document describes the reproducibility contract, not a second task tracker.
