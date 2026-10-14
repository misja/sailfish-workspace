# Public source bootstrap validation, 2026-10-14

Automated checks by the implementing assistant; no independent human security
audit or package-release acceptance is claimed.

Tested code revisions: workspace 918e4bc, runtime 593126c, password-store e98e34f.
The three source forks and all original version/archive/signer pins were unchanged.

In a new temporary directory, cloned the workspace review branch from GitHub,
used its helper to obtain the other five public repositories, and selected the
two component review branches. Supplied no old archives, verification JSON,
local trial evidence, SDK or personal keyrings.

Results:
- Downloaded and prepared all eleven upstream archives from public sources.
- Verified seven GnuPG component signatures, pass's exact signed tag and
  regenerated archive, and OATH's pinned primary/signing-subkey signature.
- Checked tree and pass-otp against publisher HTTPS and existing digest pins;
  no signature authentication is claimed for those two inputs.
- Obtained the pinned OATH LGPL notice and staged all four pass-component recipes.
- Repeated the complete verification/staging with --offline successfully.
- Confirmed full-tree equality between all packaging snapshots and fork heads.
- Ran 23 workspace tests, four pass staging tests and one runtime notice test:
  all 28 passed. SDK entrypoint tests used fake SDK executables.
- Preflight reported zero missing known source inputs; it still returned 1
  because no SDK path/target was supplied, as expected.
- All six public worktrees remained clean; generated inputs are ignored by Git.
- Syntax, relative document links, shell syntax and whitespace checks passed.

A separate read-only query of the maintainer's existing SDK reported release
3.13.5 and installed 5.1.0.11 targets. No actual SDK package build, dependency/
target installation, system/device change or upstream submission was performed.
This source test does not require LXC and does not validate an SDK host route.

Remaining acceptance: maintainer review of the three preparation PRs, then
clean source-to-package build in the selected approved SDK environment and
inspection of resulting binary/source packages. Exact vendor/native provenance,
lifecycle, provider/upgrade and distribution remain separate open gates.
