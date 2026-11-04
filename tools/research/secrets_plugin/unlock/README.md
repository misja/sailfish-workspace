# Protected selected-entry SDK fixture

Uses the pinned, unmodified Sailfish Secrets PasswordAgentPlugin through its
standard session-agent protocol. Only the graphical UI endpoint is scripted.
The real RNP default callback, InteractionRequest, daemon and consumer remain in
the path. Uses synthetic protected keys and published RFC6238 input only.

Run through the parent api-run.py with --consumer-client, --unlock-agent and
--password-agent-plugin and the reviewed SDK fixture manifest. Versions and
source hashes are recorded in the existing research evidence, not resolved live.

2026-11-04: native fixture build succeeded; runtime retry succeeded in20.8s.
Protected decrypt/TOTP, wrong/cancel/empty/oversize responses, no-prompt wrong-key
and symmetric refusal, recovery, session binding and agent loss were exercised.
The initial disconnect timeout was a scripted-agent lifetime error; exiting that
process fixed it without changing native authentication. Only that agent was
rebuilt (2.1s). All728 retained identities were unchanged after execution, with
no fixture roots or owned processes remaining.

Authentication sees the daemon caller, not the original consumer. This headless
fixture establishes neither graphical device UI behavior nor production
session/per-app authorization. No real secret data or device acceptance.
Canonical scope, review handoff and evidence links remain in STATUS.md.
