#!/usr/bin/env python3
"""SDK synthetic fixture launcher, not a product runtime."""
import hashlib
import json
import os
from pathlib import Path
import sys

if os.geteuid() != 1000:
    raise RuntimeError('fixture-uid')
environment = json.loads(sys.argv[1])
directory = Path(sys.argv[2]).resolve()
if directory.parent != Path('/home/ubuntu') or not directory.name.startswith('sailfish-public-backend-'):
    raise RuntimeError('fixture-directory')
os.chdir(directory)  # Existing build-tree RnpCore RUNPATH has an empty component.
if any(name.startswith('LD_') or name.startswith('OPENSSL_') for name in environment):
    raise RuntimeError('unreviewed-native-environment')
manifest = json.loads(Path(sys.argv[3]).read_text())
for path, expected in manifest['artifacts'].items():
    if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
        raise RuntimeError('fixture-artifact-identity')
password = sys.stdin.buffer.readline(4096)
if not password or not password.endswith(b'\n'):
    raise RuntimeError('fixture-password-input')
reader, writer = os.pipe()
os.write(writer, password)
os.close(writer)
del password
os.set_inheritable(reader, True)
environment['FIXTURE_PASSWORD_FD'] = str(reader)
command = ['/usr/bin/timeout', '--signal=KILL', '90'] + sys.argv[4:]
os.execve(command[0], command, environment)
