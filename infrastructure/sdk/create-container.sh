#!/usr/bin/env bash
# Creates only the approved outer LXD container; does not install Docker/SDK.
set -Eeuo pipefail
export LC_ALL=C
instance=sailfish-sdk
profile=sailfish-sdk-build
script_dir=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
record_dir="$script_dir/../../docs/development/environment-records"

lx() { command lxc --project default "$@"; }
trap 'printf "Stopped at line %s. Partial resources are preserved; nothing is automatically deleted.\n" "$LINENO" >&2' ERR

for tool in lxc python3 ip; do command -v "$tool" >/dev/null; done
# Query failures stop before mutation; never mistake an inaccessible daemon for an empty one.
lx list local: --format=json | python3 -c '
import json,sys
if any(x["name"] == sys.argv[1] for x in json.load(sys.stdin)):
    raise SystemExit("Instance already exists; refusing to overwrite: " + sys.argv[1])
' "$instance"
lx profile list local: --format=json | python3 -c '
import json,sys
if any(x["name"] == sys.argv[1] for x in json.load(sys.stdin)):
    raise SystemExit("Profile already exists; refusing to overwrite: " + sys.argv[1])
' "$profile"
lx storage show local:pool >/dev/null
ip link show br0 >/dev/null

# Resolve the public image once, then use its immutable fingerprint for creation.
image_info=$(lx image info ubuntu:26.04/amd64)
fingerprint=$(printf '%s\n' "$image_info" | python3 -c '
import re,sys
m=re.search(r"^Fingerprint:\s*([0-9a-f]{64})\s*$",sys.stdin.read(),re.M)
if not m: raise SystemExit("No full image fingerprint found; no resources created.")
print(m.group(1))
')
mkdir -p "$record_dir"
record="$record_dir/container-$(date -u +%Y%m%dT%H%M%SZ).txt"
printf 'Image source: ubuntu:26.04/amd64\nFingerprint: %s\nInstance: %s\nProfile: %s\nPool: pool\nBridge: br0\nRoot maximum: 20 GiB (thin)\n' "$fingerprint" "$instance" "$profile" > "$record"
printf '%s\n' "$image_info" >> "$record"

lx profile create "local:$profile"
lx profile edit "local:$profile" <<'YAML'
description: Sailfish build environment; dedicated profile, no host mounts
config:
  limits.cpu: "4"
  limits.memory: 8GiB
  security.privileged: "false"
  security.nesting: "true"
  security.syscalls.intercept.mknod: "true"
  security.syscalls.intercept.setxattr: "true"
devices:
  root:
    type: disk
    path: /
    pool: pool
    size: 20GiB
  eth0:
    type: nic
    name: eth0
    nictype: bridged
    parent: br0
YAML
lx init "ubuntu:$fingerprint" "local:$instance" --profile "$profile"
lx start "local:$instance"
lx config show "local:$instance" --expanded >> "$record"
printf '\nCreated and started %s. Environment record: %s\n' "$instance" "$record"
printf 'No Docker/SDK installation performed. Current state:\n'
lx list "local:$instance" --format compact
printf '\nContainer disk capacity:\n'
lx exec "local:$instance" -- df -h /
