# Project release targets

Owner: Architect. Updated: 2026-10-10 following maintainer clarification.

The workspace manifest maintains an extensible `release_targets` list. Sailfish OS 5.2.0.18/aarch64 is the current active release target for our projects and their future releases. Its active lifecycle expresses release intent; build/runtime verification remains pending. It is not an immutable workspace-wide OS version.

`target_policy.default_release_targets` defines the initial selection for new project release plans. Each project's release plan records its own project version and the target IDs it supports. Project release versions and Sailfish OS versions are independent. The infrastructure workspace itself does not produce a device RPM.

Add future OS versions or architectures as new target entries with stable IDs, explicit lifecycle and separate verification state. Existing entries and their historical release evidence remain. Adding a target does not automatically retire an older one or claim compatibility. Change default selection and retirement deliberately with the maintainer; support claims require target-specific evidence.

For each project release, record source revision, project version, release target IDs, actual SDK/build target, artifact hashes and build/runtime validation results. A single artifact may serve multiple release targets if compatibility is verified for each. This does not require a separate repository, branch, SDK installation or container for every target.

`sdk_build_target` is the actual toolchain mapping, distinct from the release target. The current 5.2 entry has no approved mapping yet (`null`). The observed SailfishOS-5.1.0.11-aarch64 smoke build belongs to environment verification and does not add 5.1 to the project's release target list. If a 5.1 toolchain is later approved for a 5.2 release, record that mapping and compatibility evidence explicitly.

See [manifest](../../manifest.yml) and SDK evidence (not included in this initial source export). No future target is added by automatic tracking of `latest`.
