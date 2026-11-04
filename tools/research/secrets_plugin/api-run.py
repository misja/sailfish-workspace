#!/usr/bin/env python3
"""Synthetic public Crypto API integration, existing SDK LXC only."""
import argparse
import hashlib
import json
import os
import select
import signal
from pathlib import Path
import shutil
import subprocess
import tempfile

TEXT = b'synthetic pass entry\nnotes before\nfixture OTP field\nnotes after\n'
def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--target-controller', type=Path, required=True)
    p.add_argument('--run', action='store_true', required=True)
    p.add_argument('--consumer-client', type=Path,
                   help='Optional manifest-pinned pass consumer fixture client')
    p.add_argument('--unlock-agent', type=Path, help='Optional manifest-pinned standard session UI fixture')
    p.add_argument('--password-agent-plugin', type=Path, help='Unmodified native PasswordAgent test module')
    p.add_argument('--sdk-bus-config', type=Path,
                   help='Optional per-bus SDK security exception; explicit maintainer approval required')
    a = p.parse_args()
    if (a.unlock_agent is None) != (a.password_agent_plugin is None) or (a.unlock_agent is not None and a.consumer_client is None):
        p.error('unlock fixtures require both agent/module and consumer client')
    protected_password = b'protected-sdk-fixture-password\n' if a.unlock_agent is not None else None
    sfdk = Path('/home/ubuntu/SailfishOS/bin/sfdk')
    if os.geteuid() != 1000 or not sfdk.is_file() or not all(shutil.which(t) for t in ('gpg', 'gpgconf')):
        raise RuntimeError('SDK-boundary')
    manifest = json.loads(a.manifest.read_text())
    for path, expected in manifest['artifacts'].items():
        if digest(Path(path).read_bytes()) != expected:
            raise RuntimeError('artifact-identity')
    report = {'date': '2026-11-03', 'status': 'fail', 'checks': {}, 'native': {}, 'commands': [],
              'not_tested': ['unlock UI', 'production authorization', 'full pass policy walker/file writer',
                             'OTP calculation', 'key management', 'device/distribution']}
    temporary = tempfile.mkdtemp(prefix='sailfish-rnp-api-fixture-', dir='/home/ubuntu')
    cleanup_proven = True
    agents_cleaned = False
    try:
        root = Path(temporary)
        root.chmod(0o700)
        env = {'PATH': '/usr/bin:/bin', 'HOME': str(root), 'LANG': 'C', 'LC_ALL': 'C'}
        homes = []
        bus = None
        bus_stopped = True
        def home(name):
            h = root / name
            h.mkdir(mode=0o700)
            homes.append(h)
            return h
        generator = home('generator')
        def call(label, argv, data=b'', target=False, timeout=120, password=None):
            childenv = {'PATH': '/usr/bin:/bin', 'HOME': '/home/ubuntu', 'USER': 'ubuntu',
                        'LANG': 'C', 'LC_ALL': 'C'} if target else env
            descriptor = None
            try:
                if password is not None:
                    descriptor, writer = os.pipe()
                    os.write(writer, password)
                    os.close(writer)
                actual = [str(x).replace('@PASSWORD_FD@', str(descriptor)) for x in argv]
                r = subprocess.run(actual, input=data, capture_output=True, cwd=root,
                                   env=childenv, timeout=timeout,
                                   pass_fds=() if descriptor is None else (descriptor,))
            finally:
                if descriptor is not None:
                    os.close(descriptor)
            report['commands'].append({'id': label, 'exit': r.returncode})
            return r
        def gpg(label, h, options, data=b''):
            password_options = ['--passphrase', ''] if protected_password is None else ['--passphrase-fd', '@PASSWORD_FD@']
            return call(label, ['gpg', '--no-options', '--homedir', h, '--batch', '--no-tty',
                               '--pinentry-mode', 'loopback'] + password_options +
                               ['--trust-model', 'always'] + options, data, password=protected_password)
        def require(result):
            if result.returncode:
                raise RuntimeError('fixture-command-failed')
            return result.stdout
        try:
            report['versions'] = {
                'gpg': require(call('gpg-version', ['gpg', '--version'])).decode().splitlines()[0],
                'sfdk': require(call('sdk-version', [sfdk, '--version'], target=True)).decode().splitlines()[0]}
            if report['versions'] != {'gpg': 'gpg (GnuPG) 2.4.8', 'sfdk': 'SDK_RELEASE=3.13.5'}:
                raise RuntimeError('version-pin')
            keys = {}
            for tag in ('a', 'b', 'c'):
                uid = 'API fixture ' + tag + ' <api-' + tag + '@fixture.invalid>'
                require(gpg('generate-' + tag, generator,
                            ['--quick-gen-key', uid, 'rsa2048', 'cert,sign', '0']))
                listing = require(gpg('primary-' + tag, generator,
                                      ['--with-colons', '--with-subkey-fingerprint', '--list-keys', uid]))
                fp = next(line.split(b':')[9].decode() for line in listing.splitlines() if line.startswith(b'fpr:'))
                require(gpg('add-encryption-subkey-' + tag, generator,
                            ['--quick-add-key', fp, 'rsa2048', 'encr', '0']))
                listing = require(gpg('list-' + tag, generator,
                                      ['--with-colons', '--with-subkey-fingerprint', '--list-keys', fp]))
                fps = [line.split(b':')[9].decode() for line in listing.splitlines() if line.startswith(b'fpr:')]
                primary = next(line.split(b':') for line in listing.splitlines() if line.startswith(b'pub:'))
                # Lowercase flags are primary's own usage; uppercase may include subkeys.
                if len(fps) != 2 or b'e' in primary[11]:
                    raise RuntimeError('ordinary-primary-shape')
                keys[tag] = {'primary': fps[0], 'sub': fps[1], 'id': primary[4].decode(),
                             'public': require(gpg('export-public-' + tag, generator, ['--export', fp])),
                             'secret': require(gpg('export-synthetic-secret-' + tag, generator, ['--export-secret-keys', fp]))}
            nativehome = root / 'home'
            nativehome.mkdir(mode=0o700)
            ring = nativehome / '.gnupg'
            ring.mkdir(mode=0o700)
            (ring / 'pubring.gpg').write_bytes(keys['a']['public'] + keys['b']['public'])
            (ring / 'secring.gpg').write_bytes(keys['a']['secret'] + keys['b']['secret'])
            for f in ring.iterdir():
                f.chmod(0o600)
            before = {f.name: digest(f.read_bytes()) for f in ring.iterdir()}
            config = {'text': str(root / 'text'), 'cipherOut': str(root / 'multi.gpg'),
                      'cipherAgain': str(root / 'again.gpg'), 'singleOut': str(root / 'single.gpg')}
            (root / 'text').write_bytes(TEXT)
            for tag in ('a', 'b'):
                config.update({tag + 'Primary': keys[tag]['primary'], tag + 'Sub': keys[tag]['sub'], tag + 'Id': keys[tag]['id']})
                payload = root / (tag + '-synthetic-secret-payload')
                payload.write_bytes(keys[tag]['secret'])
                payload.chmod(0o600)
                config[tag + 'SecretPayload'] = str(payload)
            consumer_data = None
            if a.consumer_client is not None:
                if str(a.consumer_client.resolve()) not in manifest['artifacts']:
                    raise RuntimeError('unreviewed-consumer-client')
                if a.unlock_agent is None:
                    from consumer_fixture import prepare_consumer
                    consumer_data = prepare_consumer(root, config, keys, gpg, require, generator)
                    report['profile'] = 'pass-entry-totp-consumer'
                    report['not_tested'] = ['protected-key unlock UI', 'production authorization',
                        'full-store operations', 'general OTP URI/HOTP conformance',
                        'key management', 'device/distribution']
                else:
                    from unlock_fixture import prepare_unlock
                    consumer_data = prepare_unlock(root, config, keys, gpg, require, generator, protected_password)
                    report['profile'] = 'protected-standard-passwordagent'
                    report['not_tested'] = ['graphical device UI', 'production session trust/per-app authorization',
                        'full-store operations', 'general OTP URI/HOTP conformance',
                        'key management', 'device/distribution']
            (root / 'config.json').write_text(json.dumps(config))
            # The SDK target lacks UID/NSS entries; use its existing Ubuntu
            # session-bus facility with normal authentication, inside this LXC.
            bus_stopped = False
            bus_options = ['--session']
            if a.sdk_bus_config is not None:
                config_path = str(a.sdk_bus_config.resolve())
                if config_path not in manifest['artifacts']:
                    raise RuntimeError('unreviewed-bus-config')
                bus_options = ['--config-file', config_path]
                report['sdk_bus_exception_config_sha256'] = manifest['artifacts'][config_path]
            bus = subprocess.Popen(['/usr/bin/dbus-daemon'] + bus_options + ['--nofork',
                '--nopidfile', '--address=unix:path=' + str(root / 'session-bus'),
                '--print-address=1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, start_new_session=True)
            if not select.select([bus.stdout], [], [], 10)[0]:
                raise RuntimeError('private-bus-timeout')
            address = bus.stdout.readline().decode().strip()
            if not address.startswith('unix:path=' + str(root / 'session-bus') + ','):
                raise RuntimeError('private-bus-address')
            report['session_bus'] = 'SDK Ubuntu dbus-daemon1.16.2; normal authentication'
            command = [sfdk, '--quiet', '--no-session', '-C', '/home/ubuntu/gnupg-runtime', '-c', 'target=SailfishOS-5.1.0.11-aarch64',
                       'build-shell', 'python3', a.target_controller, '--root', root,
                       '--build', a.build, '--manifest', a.manifest, '--session-bus-address', address]
            if a.consumer_client is not None:
                command += ['--client', a.consumer_client]
            if a.unlock_agent is not None:
                for path in (a.unlock_agent, a.password_agent_plugin):
                    if str(path.resolve()) not in manifest['artifacts']:
                        raise RuntimeError('unreviewed-passwordagent-fixture')
                command += ['--session-agent', a.unlock_agent, '--password-agent-plugin', a.password_agent_plugin]
            cleanup_proven = False
            native = call('actual-daemon-public-requests', command, target=True, timeout=210)
            report['target_stderr'] = native.stderr.decode()
            report['native'] = json.loads(native.stdout)
            cleanup_proven = report['native'].get('process_cleanup') is True
            report['checks']['actual-public-request-suite'] = native.returncode == 0 and report['native']['status'] == 'pass'
            after = {f.name: digest(f.read_bytes()) for f in ring.iterdir()}
            report['ring_hashes'] = {'before': before, 'after': after}
            report['checks']['provisioned-keyrings-unchanged'] = before == after
            if not report['checks']['actual-public-request-suite']:
                raise RuntimeError('actual-public-request-suite-failed')
            outputs = consumer_data['outputs'] if consumer_data else [
                ('multi.gpg', TEXT, {'a', 'b'}), ('again.gpg', TEXT, {'a', 'b'})]
            if consumer_data:
                from consumer_fixture import check_consumer
                report['checks'].update(check_consumer(root, consumer_data, report['native']['client']))
            for tag in ('a', 'b', 'c'):
                oracle = home('oracle-' + tag)
                require(gpg('import-oracle-' + tag, oracle, ['--import'], keys[tag]['secret']))
                for name, expected, allowed in outputs:
                    result = gpg('independent-' + tag + '-' + name, oracle, ['--decrypt', str(root / name)])
                    report['checks'][tag + '-' + name + '-oracle'] = (
                        result.returncode == 0 and result.stdout == expected) if tag in allowed else (
                        result.returncode != 0 and result.stdout == b'')
            report['checks']['a-ordinary-primary-with-encryption-subkey'] = True
            report['checks']['b-ordinary-primary-with-encryption-subkey'] = True
            report['checks']['artifacts-unchanged'] = all(digest(Path(p).read_bytes()) == h for p, h in manifest['artifacts'].items())
        except Exception as error:
            report['error_type'] = type(error).__name__
            report['error'] = str(error)
        finally:
            cleaned = []
            try:
                for h in homes:
                    try:
                        cleaned.append(call('cleanup-own-agent-' + h.name,
                            ['gpgconf', '--homedir', h, '--kill', 'gpg-agent'], timeout=10).returncode == 0)
                    except Exception:
                        cleaned.append(False)
            finally:
                try:
                    if bus is not None:
                        try:
                            os.killpg(bus.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        try:
                            bus.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            os.killpg(bus.pid, signal.SIGKILL)
                            bus.wait(timeout=3)
                        report['bus_stderr'] = bus.stderr.read().decode()
                        bus_stopped = bus.poll() is not None
                except Exception as error:
                    report['bus_cleanup_error'] = str(error)
                    bus_stopped = False
            agents_cleaned = all(cleaned)
            report['checks']['fixture-agents-cleaned'] = agents_cleaned
            report['checks']['outer-bus-stopped'] = bus_stopped
    finally:
        # A lost controller cannot prove its detached servers stopped. Preserve
        # their owned directory for diagnosis instead of unlinking live sockets.
        if cleanup_proven and agents_cleaned and bus_stopped:
            shutil.rmtree(temporary)
        else:
            report['preserved_fixture_root'] = temporary
    report['checks']['fixture-root-removed'] = not root.exists()
    if report['checks'] and all(report['checks'].values()) and 'error' not in report:
        report['status'] = 'pass'
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
