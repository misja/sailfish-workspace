# From public sources to a package build

Work owner and current status: [workspace issue #5](https://github.com/misja/sailfish-workspace/issues/5).
The source workspace is portable. SDK provisioning and complete public source
staging are being completed in separate reviewed slices. See
[source bootstrap](source-bootstrap.md) for the reproducible source preparation.

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
use Docker or VirtualBox for the build engine. For Linux, document Docker
directly on the development host as the normal route; follow the official
requirements rather than reproducing the maintainer's machine.

### Optional LXC/LXD variant

Misja's setup is an outer LXC container, an Ubuntu image and Docker running the
SDK inside it. The outer container is optional. It needs extra nesting, storage,
permissions and SDK image/device-node adaptation; it is not the baseline and
must not become a prerequisite for contributors or reproducible package builds.
The dated scripts in infrastructure/sdk/ describe that local variant.
Record any additional adaptations separately from the ordinary SDK instructions.
Check SDK paths from the environment where the SDK actually runs; a host-side
preflight cannot see an SDK inside a container.

The recorded SDK is 3.13.5. The existing build scripts use
SailfishOS-5.1.0.11-aarch64. That is historical build evidence, not verification
for the intended Sailfish OS 5.2 release or the maintainer's current device.
Keep [target selection](release-targets.md) explicit. Record installed tooling
and a reviewed SDK-to-release mapping before changing targets.

Host checkouts keep their GitHub names. Source and build entrypoints derive
their project directories, accept an explicit SDK path and require a selected
installed target. Historical device/test harnesses remain separately scoped.
See the [actual clean build](clean-sdk-build-20261015.md) and its pending fixes.

SDK downloads, virtualization/system configuration and installations require
their own concrete approval. No install command is run by the preflight.

## Source staging gaps

| Component | Existing public implementation | Remaining reproducibility work |
| --- | --- | --- |
| GnuPG runtime | Shared portable fetcher verifies pinned digests/signatures in temporary public-only keyrings | Test the full source-to-package build in the selected SDK |
| pass/tree | Signed pass tag and exact archive regeneration; tree HTTPS/digest record; stable evidence names | Test clean package builds and source/binary notice delivery |
| pass-otp/OATH | Pinned HTTPS/digest OTP input; signed OATH input and LGPL notice; complete recipe staging | Test the selected SDK build and affected synthetic behavior |
| Native pinentry | Pinned fork commits, materializer and full-tree patch equality | Establish exact vendor-source identity and prepare all provenance/relink inputs separately |

Do not fabricate a successful verification JSON to satisfy an old script.
Recreate evidence from the selected public sources with an isolated public-key
verification home. Do not apply packaging patches to an already patched fork
archive. The preflight intentionally does not label native pinentry ready.

A source audit found the runtime RPM's component-license directory staging was
broken; its separate fix has a synthetic test of the actual install fragment.
The [clean build record](clean-sdk-build-20261015.md) now contains the actual
main binary/source-RPM notice inspections and the remaining debug-package limit.

## Completion evidence

Before closing issue #5, demonstrate a fresh public checkout, authenticated
source staging and clean package build in the approved SDK. Record exact Git
revisions, source digests/signers, SDK/target, commands and actual outputs.
Do not reuse private local caches as unexplained prerequisites.

Work status and review blockers stay in the issue and project board. This
document describes the reproducibility contract, not a second task tracker.
