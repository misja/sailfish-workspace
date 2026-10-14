# Workspace bootstrap validation, 2026-10-14

Automated checks performed by the implementing assistant; no independent human
review or package/device acceptance is claimed.

Tested public code revisions: workspace 8fc7309631c9, runtime e2b2267 and
password-store 1ed99e2. Fork commits remained unchanged.

- Cloned workspace's review branch over HTTPS into a fresh temporary directory.
- Used the checkout helper to obtain all six public repositories, then repeated
  it: all heads and existing branches were preserved. New forks used exact pins
  and had the correct upstream remotes.
- Switched the two packaging checkouts to their documented migration branches.
  All eight packaging snapshots reproduced the complete pinned fork trees.
- Exported snapshots again: their bytes were unchanged.
- Materialized both native pinentry variants and verified the compat header.
- Ran five offline synthetic-repository tests from the fresh public clone:
  clone/pin/upstream, repeated invocation with dirty work, dry-run, wrong origin
  preflight and symlink rejection.
- In disposable source fixtures, rejected a modified but applicable patch,
  a component/source-map pin mismatch and an omitted assuancompat.h before
  generated output was written.
- All six fresh public worktrees stayed clean. No original local repository,
  archived source cache, test evidence or credential/key data was supplied.
- Python syntax, local Markdown links and Git whitespace checks passed.

These checks establish source/planning bootstrap portability for the tested
Git/Python environment. They are not a cross-platform SDK installation test,
package build, crypto audit, device validation or proof of supported targets.
The three migration PRs remain unmerged; main acquires this workflow only after
maintainer review and merge.
