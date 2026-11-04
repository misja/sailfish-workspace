#!/usr/bin/env python3
"""Synthetic public libpgpfactory fixture runner; never builds/installs/fetches.

Requires separately reviewed/authorized binary built from pinned public sources.
Only self-generated modern keys and the published RFC6238 fixture are used.
No store/recipient/OTP implementation belongs to this runner.
"""
import argparse
import difflib
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

import prepare_pass_rnp_fixture as preparer

PASSWORD = b'public-synthetic-public-backend-password\n'
URI = b'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&digits=8&period=30'
ORIGINAL = b'synthetic password\nnotes: before\n' + URI + b'\nnotes: after\n'
UPDATED = b'synthetic password\nnotes: changed\n' + URI.replace(b'/RFC6238?', b'/RFC6238-updated?') + b'\nnotes: after\n'
ABSENT_KEYID = 'DEADBEEFDEADBEEF'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True, type=Path)
    parser.add_argument('--pass-sources', required=True, type=Path)
    parser.add_argument('--policy-identifiers', choices=('fingerprints', 'keyids'), default='fingerprints',
                        help='Explicit fixture .gpg-id locator variant; default preserves fingerprint compatibility test')
    parser.add_argument('--expect-corrections', action='store_true',
                        help='Require reviewed fingerprint/cache/rename-cleanup regressions; baseline remains available')
    parser.add_argument('--sdk-target', choices=('SailfishOS-5.1.0.11-aarch64',))
    parser.add_argument('--sdk-artifacts-manifest', type=Path)
    parser.add_argument('--sdk-sfdk', type=Path, default=Path('/home/ubuntu/SailfishOS/bin/sfdk'))
    parser.add_argument('--run', action='store_true', required=True)
    args = parser.parse_args()
    sdk = args.sdk_target is not None
    if sdk and (not args.sdk_artifacts_manifest or not args.expect_corrections):
        parser.error('SDK profile requires artifact manifest and --expect-corrections')
    report = {'probe': 'public-libpgpfactory-feasibility', 'status': 'not-run',
              'policy_identifiers': args.policy_identifiers,
              'expect_corrections': args.expect_corrections,
              'negative_recipient_fixture': 'verified-absent-nonzero-keyid',
              'gpgfactory_commit': 'e53cd22c365ce170ebeaed70984207a8206d00eb',
              'rnp_commit': 'aad1892e4d8423398a0b973bd0a7e4544c359afc',
              'commands': [], 'process_results': {}, 'checks': {}, 'versions': {},
              'not_tested': ['native OTP URI parsing/mutation', 'production adoption/API',
                             'crash/concurrency/fsync', 'general save safety',
                             'rename failure over an existing encrypted file',
                             'Sailfish toolchain/dependencies', 'singleton multi-home use',
                             'signed policy/Git/HOTP/key-management product']}
    names = ('gpg', 'gpgconf', 'bash') if sdk else ('gpg', 'gpgconf', 'rnpkeys', 'bash', 'oathtool')
    tools = {name: shutil.which(name) for name in names}
    if sdk:
        tools['sfdk'] = str(args.sdk_sfdk) if args.sdk_sfdk.is_file() else None
        report.update(profile='sdk-lxc', sdk_target=args.sdk_target,
                      execution_boundary='same SDK LXC; target backend / Ubuntu GPG oracle',
                      otp_oracle='not-executed: oathtool absent; no substitute')
        report['not_tested'].remove('Sailfish toolchain/dependencies')
        report['not_tested'].extend(['pass-otp code in SDK profile', 'device/native-hardware runtime'])
    binary = args.binary.resolve()
    if os.geteuid() != 1000 or not binary.is_file() or not all(tools.values()):
        report.update(status='prerequisites-not-met', uid=os.geteuid(), tools=tools)
        print(json.dumps(report, indent=2))
        return 2
    originals = {name: (args.pass_sources / name).read_bytes() for name in preparer.PINS}
    if any(digest(data) != preparer.PINS[name] for name, data in originals.items()):
        report['status'] = 'pass-source-pin-mismatch'
        print(json.dumps(report, indent=2))
        return 2
    report['source_sha256'] = {name: digest(data) for name, data in originals.items()}
    report['binary_sha256'] = digest(binary.read_bytes())
    report['runner_sha256'] = digest(Path(__file__).read_bytes())
    report['preparer_sha256'] = digest(Path(preparer.__file__).read_bytes())
    if args.expect_corrections:
        report['corrections_patch_sha256'] = digest((Path(__file__).parent / 'public_backend/corrections.patch').read_bytes())
    if sdk:
        identity = json.loads(args.sdk_artifacts_manifest.read_text())
        for path, expected in identity['artifacts'].items():
            if digest(Path(path).read_bytes()) != expected:
                raise RuntimeError('sdk-artifact-identity-mismatch')
        if identity['artifacts'].get(str(binary)) != report['binary_sha256']:
            raise RuntimeError('sdk-binary-not-in-reviewed-manifest')
        report['sdk_artifact_sha256'] = identity['artifacts']
        report['sdk_manifest_sha256'] = digest(args.sdk_artifacts_manifest.read_bytes())
    with tempfile.TemporaryDirectory(prefix='sailfish-public-backend-',
                                     dir='/home/ubuntu' if sdk else None) as temp:
        root = Path(temp)
        root.chmod(0o700)
        store = root / 'store'
        store.mkdir(mode=0o700)
        homes = {}
        for name in ('g-a', 'g-b', 'r-a', 'r-b'):
            homes[name] = root / name
            homes[name].mkdir(mode=0o700)
        env = {'PATH': '/usr/bin:/bin', 'HOME': temp, 'GNUPGHOME': str(root / 'unused'),
               'LANG': 'C', 'LC_ALL': 'C', 'TERM': 'dumb',
               'PASSWORD_STORE_DIR': str(store), 'PASSWORD_STORE_ENABLE_EXTENSIONS': 'false'}

        def call(label, command, data=b'', password=None, extra=None, sdk_dispatch=False):
            # Infrastructure HOME is only for sfdk; backend/GPG use fixture homes.
            childenv = ({'PATH': '/usr/bin:/bin', 'HOME': '/home/ubuntu', 'USER': 'ubuntu',
                         'LANG': 'C', 'LC_ALL': 'C', 'TERM': 'dumb'} if sdk_dispatch else dict(env))
            if extra:
                childenv.update(extra)
            fd = None
            try:
                if password is not None:
                    fd, writer = os.pipe()
                    try:
                        os.write(writer, password)
                    finally:
                        os.close(writer)
                    childenv['FIXTURE_PASSWORD_FD'] = str(fd)
                process = subprocess.Popen([str(x) for x in command], stdin=subprocess.PIPE, env=childenv,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           pass_fds=() if fd is None else (fd,), start_new_session=True,
                                           cwd=root if sdk else None)
                try:
                    stdout, stderr = process.communicate(data, timeout=120)
                except subprocess.TimeoutExpired:
                    # Only this command's newly created process group; own
                    # separately spawned fixture agents are cleaned below.
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.communicate()
                    report['commands'].append({'id': label, 'status': 'timeout'})
                    raise
                result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
                report['commands'].append({'id': label, 'exit': result.returncode})
                return result
            finally:
                if fd is not None:
                    os.close(fd)

        def native(label, command, extra=None):
            if not sdk:
                return call(label, command, password=PASSWORD, extra=extra)
            target_env = dict(env)
            if extra:
                target_env.update(extra)
            launcher = Path(__file__).parent / 'public_backend/sdk_fixture_launch.py'
            result = call(label, [tools['sfdk'], '--quiet', '--no-session',
                                  '-C', '/home/ubuntu/gnupg-runtime',
                                  '-c', 'target=' + args.sdk_target,
                                  'build-shell', 'python3', launcher, json.dumps(target_env),
                                  root, args.sdk_artifacts_manifest.resolve()] + list(command),
                          data=PASSWORD, sdk_dispatch=True)
            report.setdefault('sdk_native_diagnostics', {})[label] = {
                'exit': result.returncode,
                'stderr': result.stderr.decode(errors='replace')[-16384:]}
            return result

        def require(result):
            if result.returncode:
                raise RuntimeError('fixture-command-failed')
            return result.stdout

        def gpg(label, home, options, data=b'', password=None):
            # Descriptor number is set by call; fixture wrapper reads it.
            return call(label, [root / 'fixture-gpg'] + list(options), data,
                        PASSWORD if password is None else password,
                        {'FIXTURE_CRYPTO_HOME': str(homes[home])})

        try:
            wrappers = {
                'fixture-gpg': '#!/bin/sh\nexec ' + tools['gpg'] +
                    ' --no-options --homedir "$FIXTURE_CRYPTO_HOME" --batch --no-tty'
                    ' --pinentry-mode loopback --passphrase-fd "$FIXTURE_PASSWORD_FD"'
                    ' --trust-model always "$@"\n',
            }
            if not sdk:
                wrappers['fixture-oath'] = '#!/bin/sh\nexec ' + tools['oathtool'] + ' --now=@59 "$@"\n'
            report['wrapper_sha256'] = {}
            for name, content in wrappers.items():
                path = root / name
                path.write_text(content)
                path.chmod(0o700)
                report['wrapper_sha256'][name] = digest(path.read_bytes())
            report['pass_fixture_patches'] = {}
            report['pass_fixture_sha256'] = {}
            for name, original in (originals.items() if not sdk else []):
                content = preparer.prepare(original, name, 'gpg', root)
                path = root / 'gpg' / ('pass' if name == 'pass' else 'extensions/otp.bash')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                path.chmod(0o700 if name == 'otp.bash' else 0o600)
                report['pass_fixture_sha256'][name] = digest(content)
                report['pass_fixture_patches'][name] = ''.join(difflib.unified_diff(
                    original.decode().splitlines(True), content.decode().splitlines(True),
                    fromfile=name + '-pinned', tofile='gpg/' + name))
            for tool in tools:
                report['versions'][tool] = require(call('version-' + tool, [tools[tool], '--version'])).decode().splitlines()[0]
            if '2.4.8' not in report['versions']['gpg'] or (not sdk and '0.18.1' not in report['versions']['rnpkeys']):
                raise RuntimeError('unexpected-fixture-tool-version')
            if sdk and report['versions']['sfdk'] != 'SDK_RELEASE=3.13.5':
                raise RuntimeError('unexpected-sdk-version')
            fingerprints, keyids, publics = {}, {}, {}
            observed_keyids = set()
            for tag in ('a', 'b'):
                require(gpg('generate-' + tag, 'g-' + tag, ['--quick-gen-key', 'Synthetic <' + tag + '@fixture.invalid>',
                                                           'ed25519', 'cert,sign', '0']))
                listing = require(gpg('list-primary-' + tag, 'g-' + tag, ['--with-colons', '--list-keys']))
                fingerprints[tag] = next(line.split(b':')[9].decode() for line in listing.splitlines() if line.startswith(b'fpr:'))
                keyids[tag] = next(line.split(b':')[4].decode() for line in listing.splitlines() if line.startswith(b'pub:'))
                require(gpg('add-cv25519-' + tag, 'g-' + tag, ['--quick-add-key', fingerprints[tag], 'cv25519', 'encr', '0']))
                listing = require(gpg('verify-curves-' + tag, 'g-' + tag, ['--with-colons', '--list-keys']))
                observed_keyids.update(line.split(b':')[4].decode() for line in listing.splitlines()
                                       if line.startswith((b'pub:', b'sub:')))
                report['checks']['modern-key-' + tag] = (
                    any(line.startswith(b'pub:') and b':ed25519:' in line for line in listing.splitlines()) and
                    any(line.startswith(b'sub:') and b':cv25519:' in line for line in listing.splitlines()))
                secret = require(gpg('export-secret-' + tag, 'g-' + tag, ['--export-secret-keys', fingerprints[tag]]))
                publics[tag] = require(gpg('export-public-' + tag, 'g-' + tag, ['--export', fingerprints[tag]]))
                if sdk:
                    ring = homes['r-' + tag] / 'secring.gpg'
                    ring.write_bytes(secret)
                    ring.chmod(0o600)
                    (homes['r-' + tag] / 'pubring.gpg').write_bytes(publics[tag])
                else:
                    keyfile = root / 'synthetic-transfer.key'
                    keyfile.write_bytes(secret)
                    keyfile.chmod(0o600)
                    require(call('import-native-secret-' + tag,
                                 [tools['rnpkeys'], '--homedir', homes['r-' + tag], '--notty', '--import', keyfile]))
                    keyfile.unlink()
                del secret
            for tag in ('a', 'b'):
                peer = 'b' if tag == 'a' else 'a'
                require(gpg('import-gpg-public-' + tag, 'g-' + tag, ['--import'], publics[peer]))
                if sdk:
                    ring = homes['r-' + tag] / 'pubring.gpg'
                    ring.write_bytes(ring.read_bytes() + publics[peer])
                else:
                    keyfile = root / 'synthetic-transfer.key'
                    keyfile.write_bytes(publics[peer])
                    require(call('import-native-public-' + tag,
                                 [tools['rnpkeys'], '--homedir', homes['r-' + tag], '--notty', '--import', keyfile]))
                    keyfile.unlink()
            if sdk:
                inventory = native('sdk-target-inventory', ['python3', '-c',
                    'import json,os,platform,sys; print(json.dumps({"uid":os.geteuid(),"python":platform.python_version(),"executable":sys.executable}))'])
                report['sdk_target_inventory'] = json.loads(require(inventory))
                if report['sdk_target_inventory']['uid'] != 1000:
                    raise RuntimeError('unexpected-sdk-target-context')
                loader = native('sdk-loader-list', ['/lib/ld-linux-aarch64.so.1', '--list', binary])
                loader_text = require(loader).decode()
                report['sdk_loader_output'] = loader_text
                project_paths = dict(re.findall(r'\s+(libRnpCore\.so|librnp\.so\.0) => (\S+)', loader_text))
                for soname, key in [('libRnpCore.so', 'rnp_core_path'), ('librnp.so.0', 'librnp_path')]:
                    found = project_paths.get(soname)
                    report['checks']['sdk-loader-' + soname] = bool(found) and Path(found).resolve() == Path(identity[key]).resolve()
                if not all(report['checks'][key] for key in ('sdk-loader-libRnpCore.so', 'sdk-loader-librnp.so.0')):
                    raise RuntimeError('sdk-loader-mapping-mismatch')
                selected = native('sdk-disabled-gpg-selection', [binary, 'disabled-gpg-selection', homes['r-a']])
                record = json.loads(selected.stdout)
                report['process_results']['disabled-gpg-selection'] = record
                report['checks']['sdk-disabled-gpg-selection'] = selected.returncode == 0 and record.get('status') == 'pass'
            report['checks']['negative-recipient-absent-from-generated-keys'] = ABSENT_KEYID not in observed_keyids
            if not report['checks']['negative-recipient-absent-from-generated-keys']:
                raise RuntimeError('negative-fixture-key-present')
            identifiers = fingerprints if args.policy_identifiers == 'fingerprints' else keyids
            (store / '.gpg-id').write_text(identifiers['a'] + '\n')
            for name, recipients in [('nested', [identifiers['b']]),
                                     ('multi', [identifiers['a'], identifiers['b']]),
                                     ('guard', [identifiers['a'], ABSENT_KEYID]), ('inherited', [])]:
                directory = store / name
                directory.mkdir()
                if recipients:
                    (directory / '.gpg-id').write_text(''.join(x + '\n' for x in recipients))
            initial = {}
            for name, tag in [('plain.gpg', 'a'), ('inherited/item.gpg', 'a'), ('nested/item.gpg', 'b'),
                              ('multi/item.gpg', 'a'), ('guard/item.gpg', 'a'), ('missing.gpg', 'a')]:
                content = require(gpg('seed-' + name, 'g-' + tag,
                                      ['--encrypt', '--recipient', fingerprints[tag], '--output', '-'], ORIGINAL))
                (store / name).write_bytes(content)
                initial[name] = content
            (store / 'readme.txt').write_text('synthetic non-entry\n')
            (store / '.hidden.gpg').write_bytes(initial['plain.gpg'])
            expected_file, updated_file = root / 'original.txt', root / 'updated.txt'
            expected_file.write_bytes(ORIGINAL)
            updated_file.write_bytes(UPDATED)
            for mode, tag in [('refuse', 'a'), ('normal', 'a'), ('read-b', 'b')]:
                result = native('public-' + mode, [binary, mode, homes['r-' + tag], store,
                                expected_file, updated_file, keyids['a'], keyids['b']],
                              extra={'FIXTURE_A_FINGERPRINT': fingerprints['a'],
                                     'FIXTURE_EXPECT_CORRECTIONS': '1' if args.expect_corrections else '0'})
                record = json.loads(result.stdout)
                report['process_results'][mode] = record
                report['checks']['public-' + mode] = result.returncode == 0 and record.get('status') == 'pass'
                report['checks']['expectation-mode-' + mode] = record.get('expect_corrections') == args.expect_corrections
                if mode == 'refuse':
                    report['checks']['external-refusal-preservation'] = all((store / name).read_bytes() == content for name, content in initial.items())
                    if not report['checks']['public-refuse'] or not report['checks']['external-refusal-preservation']:
                        raise RuntimeError('refusal-fixture-failed')
                elif mode == 'normal' and (record.get('exception') is not False or record.get('stage') != 'completed'):
                    # A completed process can report a failed check while still
                    # producing measurable successful outputs. Keep its false
                    # check/final failure and collect the independent oracles.
                    raise RuntimeError('normal-fixture-incomplete')
            for name, tag in [('plain.gpg', 'a'), ('inherited/item.gpg', 'a'), ('nested/item.gpg', 'b'),
                              ('multi/item.gpg', 'a'), ('multi/item.gpg', 'b')]:
                recovered = require(gpg('gpg-oracle-' + name + '-' + tag, 'g-' + tag, ['--decrypt', store / name]))
                report['checks']['gpg-exact-' + name + '-' + tag] = recovered == UPDATED
            for name in ('guard/item.gpg', 'missing.gpg'):
                target = store / name
                report['checks']['external-failure-preservation-' + name] = target.is_file() and target.read_bytes() == initial[name]
            for name, tag in ([] if sdk else [('plain', 'a'), ('nested/item', 'b')]):
                result = call('pinned-pass-otp-' + name, [tools['bash'], root / 'gpg/pass', 'otp', 'code', name],
                              password=PASSWORD, extra={'FIXTURE_CRYPTO_HOME': str(homes['g-' + tag])})
                report['checks']['pinned-pass-otp-code-' + name] = result.returncode == 0 and result.stdout == b'94287082\n'
            report['status'] = 'pass' if all(report['checks'].values()) else 'fail'
        except (OSError, RuntimeError, ValueError, StopIteration, subprocess.TimeoutExpired) as error:
            report['status'] = 'error'
            report['error_type'] = type(error).__name__
        finally:
            cleanup = True
            for tag in ('a', 'b'):
                try:
                    result = call('cleanup-agent-' + tag, [tools['gpgconf'], '--homedir', homes['g-' + tag], '--kill', 'gpg-agent'])
                    cleanup = cleanup and result.returncode == 0
                except (OSError, subprocess.TimeoutExpired):
                    cleanup = False
            report['fixture_agent_cleanup'] = cleanup
            if not cleanup:
                report['status'] = 'error'
    report['temporary_root_removed'] = not root.exists()
    if not report['temporary_root_removed']:
        report['status'] = 'error'
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
