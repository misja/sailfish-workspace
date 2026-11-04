#!/usr/bin/env python3
"""SDK/LXC-only synthetic regression controller; no install or daemon activation."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

PASSWORD = b'plugin-synthetic-fixture-password\n'
TEXT = (b'synthetic password\nnotes before\n'
        b'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&digits=8&period=30\n'
        b'notes after\n')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--launcher', required=True, type=Path)
    parser.add_argument('--run', action='store_true', required=True)
    args = parser.parse_args()
    sfdk = Path('/home/ubuntu/SailfishOS/bin/sfdk')
    tools = {name: shutil.which(name) for name in ('gpg', 'gpgconf')}
    if os.geteuid() != 1000 or not all(tools.values()) or not sfdk.is_file():
        raise RuntimeError('prerequisites')
    manifest = json.loads(args.manifest.read_text())
    for path, expected in manifest['artifacts'].items():
        if digest(Path(path).read_bytes()) != expected:
            raise RuntimeError('artifact-identity')
    report = {'date': '2026-11-03', 'status': 'not-run', 'commands': [],
              'checks': {}, 'native': {}, 'boundary': 'existing SDK/LXC only',
              'not_tested': ['live daemon authorization/UI', 'key management', 'multiple-recipient plugin API',
                             'remaining P2 metadata/filter bugs', 'ASAN/Valgrind/leak-size',
                             'QMF', 'device/package/distribution', 'native OTP calculation']}
    with tempfile.TemporaryDirectory(prefix='sailfish-public-backend-secrets-', dir='/home/ubuntu') as temporary:
        root = Path(temporary)
        root.chmod(0o700)
        ghome = root / 'gpg'
        ghome.mkdir(mode=0o700)
        env = {'PATH': '/usr/bin:/bin', 'HOME': str(root), 'GNUPGHOME': str(ghome),
               'LANG': 'C', 'LC_ALL': 'C', 'TERM': 'dumb'}

        def call(label, command, data=b'', password=None, infrastructure=False):
            childenv = ({'PATH': '/usr/bin:/bin', 'HOME': '/home/ubuntu', 'USER': 'ubuntu',
                         'LANG': 'C', 'LC_ALL': 'C', 'TERM': 'dumb'} if infrastructure else dict(env))
            descriptor = None
            try:
                if password is not None:
                    descriptor, writer = os.pipe()
                    os.write(writer, password)
                    os.close(writer)
                actual = [str(item).replace('@PASSWORD_FD@', str(descriptor)) for item in command]
                proc = subprocess.Popen(actual, env=childenv, cwd=root,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        pass_fds=() if descriptor is None else (descriptor,), start_new_session=True)
                try:
                    stdout, stderr = proc.communicate(data, timeout=120)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    proc.communicate()
                    raise
                report['commands'].append({'id': label, 'exit': proc.returncode})
                return subprocess.CompletedProcess(actual, proc.returncode, stdout, stderr)
            finally:
                if descriptor is not None:
                    os.close(descriptor)

        def require(result):
            if result.returncode:
                report['failed_command_stderr'] = result.stderr.decode(errors='replace')[-16384:]
                raise RuntimeError('fixture-command-failed')
            return result.stdout

        def gpg(label, options, data=b'', password=PASSWORD):
            return call(label, [tools['gpg'], '--no-options', '--homedir', ghome, '--batch', '--no-tty',
                               '--pinentry-mode', 'loopback', '--passphrase-fd', '@PASSWORD_FD@',
                               '--trust-model', 'always'] + list(options), data, password)

        def native(label, binary, mode_args, home, case):
            native_env = dict(env, HOME=str(home), GNUPGHOME=str(root / 'unused'),
                              TMPDIR=str(case / 'tmp'),
                              DBUS_SESSION_BUS_ADDRESS='unix:path=' + str(root / 'no-session-bus'),
                              DBUS_SYSTEM_BUS_ADDRESS='unix:path=' + str(root / 'no-system-bus'))
            result = call(label, [sfdk, '--quiet', '--no-session', '-C', '/home/ubuntu/gnupg-runtime',
                                  '-c', 'target=SailfishOS-5.1.0.11-aarch64', 'build-shell',
                                  'python3', args.launcher, json.dumps(native_env), root,
                                  args.manifest.resolve(), binary] + list(mode_args),
                          data=PASSWORD, infrastructure=True)
            report.setdefault('native_stderr', {})[label] = result.stderr.decode(errors='replace')[-16384:]
            return result

        def case_directory(name, public, secret):
            case = root / name
            case.mkdir(mode=0o700)
            home = case / 'home'
            ring = home / '.gnupg'
            ring.mkdir(mode=0o700, parents=True)
            (case / 'tmp').mkdir(mode=0o700)
            for name, data in [('pubring.gpg', public), ('secring.gpg', secret)]:
                path = ring / name
                path.write_bytes(data)
                path.chmod(0o600)
            return case, home, ring

        def listing(label, fingerprint, password):
            data = require(gpg(label, ['--with-colons', '--with-subkey-fingerprint', '--list-keys', fingerprint],
                               password=password))
            fps = [line.split(b':')[9].decode() for line in data.splitlines() if line.startswith(b'fpr:')]
            keyid = next(line.split(b':')[4].decode() for line in data.splitlines() if line.startswith(b'pub:'))
            return fps, keyid

        try:
            versions = {}
            for tool in tools:
                versions[tool] = require(call('version-' + tool, [tools[tool], '--version'])).decode().splitlines()[0]
            versions['sfdk'] = require(call('version-sdk', [sfdk, '--version'])).decode().splitlines()[0]
            report['versions'] = versions
            if '2.4.8' not in versions['gpg'] or versions['sfdk'] != 'SDK_RELEASE=3.13.5':
                raise RuntimeError('unexpected-version')
            textfile = root / 'text'
            textfile.write_bytes(TEXT)
            passwordfile = root / 'password'
            passwordfile.write_bytes(PASSWORD)
            passwordfile.chmod(0o600)
            profiles = {}
            for profile in ('plain', 'protected'):
                password = b'\n' if profile == 'plain' else PASSWORD
                records = {}
                for tag in ('a', 'b'):
                    uid = 'Synthetic ' + profile + ' ' + tag + ' <' + profile + '-' + tag + '@fixture.invalid>'
                    require(gpg('generate-' + profile + '-' + tag,
                                ['--quick-gen-key', uid, 'rsa2048', 'cert,sign,encr', '0'], password=password))
                    fps, keyid = listing('list-' + profile + '-' + tag, uid, password)
                    if len(fps) != 1:
                        raise RuntimeError('unexpected-primary-fixture')
                    primary = fps[0]
                    if profile == 'protected' and tag == 'a':
                        for index, usage in enumerate(('encr', 'encr', 'sign')):
                            require(gpg('subkey-' + str(index), ['--quick-add-key', primary, 'rsa2048', usage, '0'],
                                        password=password))
                        fps, keyid = listing('list-all-subkeys', primary, password)
                        if len(fps) != 4:
                            raise RuntimeError('unexpected-subkey-fixture')
                    public = require(gpg('public-' + profile + '-' + tag, ['--export', primary], password=password))
                    secret = require(gpg('synthetic-secret-' + profile + '-' + tag,
                                         ['--export-secret-keys', primary], password=password))
                    records[tag] = {'primary': primary, 'id': keyid, 'fingerprints': fps,
                                    'public': public, 'secret': secret}
                profiles[profile] = records
                public = records['a']['public'] + records['b']['public']
                secret = records['a']['secret'] + records['b']['secret']
                case_names = ('pristine-control', 'corrected-control') if profile == 'plain' else ('protected',)
                for casename in case_names:
                    case, home, ring = case_directory(casename, public, secret)
                    config = {'aPrimary': records['a']['primary'], 'aId': records['a']['id'],
                              'text': str(textfile), 'passwordFile': str(passwordfile),
                              'signatureOut': str(case / 'signature.asc'), 'cipherOut': str(case / 'native.gpg')}
                    targets = [('aCipher', records['a']['primary'], TEXT),
                               ('bCipher', records['b']['primary'], TEXT)]
                    if profile == 'protected':
                        fps = records['a']['fingerprints']
                        config.update(aSub=fps[1], aSibling=fps[2], aSigning=fps[3])
                        targets += [('subCipher', fps[1], TEXT), ('siblingCipher', fps[2], TEXT),
                                    ('emptyCipher', fps[1], b'')]
                    for label, recipient, content in targets:
                        path = case / (label + '.gpg')
                        path.write_bytes(require(gpg('seed-' + casename + '-' + label,
                            ['--encrypt', '--recipient', recipient + '!', '--output', '-'],
                            content, password=password)))
                        config[label] = str(path)
                    if profile == 'protected':
                        for label, options in [
                                ('symmetricCipher', ['--symmetric', '--cipher-algo', 'AES256', '--output', '-']),
                                ('signedOnly', ['--sign', '--local-user', records['a']['primary'] + '!', '--output', '-'])]:
                            path = case / (label + '.gpg')
                            path.write_bytes(require(gpg('seed-' + label, options, TEXT, password=password)))
                            config[label] = str(path)
                    configfile = case / 'config.json'
                    configfile.write_text(json.dumps(config))
                    before = {p.name: digest(p.read_bytes()) for p in ring.iterdir()}
                    binary = args.build / ('secrets_rnp_pristine_probe' if casename == 'pristine-control'
                                           else 'secrets_rnp_probe')
                    if casename == 'corrected-control':
                        loaded = native('loader-list', '/lib/ld-linux-aarch64.so.1',
                                        ['--list', binary], home, case)
                        report['loader'] = require(loaded).decode()
                        mapping = re.search(r'librnp\.so\.0 => (\S+)', report['loader'])
                        report['checks']['loader-uses-retained-rnp'] = bool(mapping) and str(Path(mapping.group(1)).resolve()) == manifest['rnp_library']
                    result = native(casename, binary, ['control' if profile == 'plain' else 'protected', configfile],
                                    home, case)
                    record = json.loads(result.stdout)
                    report['native'][casename] = record
                    after = {p.name: digest(p.read_bytes()) for p in ring.iterdir()}
                    report.setdefault('ring_observations', {})[casename] = {
                        'before': before, 'after': after,
                        'unchanged': before == after,
                        'retained_temp_count': len(list((case / 'tmp').iterdir()))}
                    if casename == 'pristine-control':
                        report['checks']['pristine-genuine-regressions'] = (
                            result.returncode == 1 and record['status'] == 'fail'
                            and record['checks'].get('own-key-roundtrip') is True
                            and record['checks'].get('other-primary-refused') is False
                            and record['checks'].get('raw-private-refused') is False
                            and record.get('observations', {}).get('other-key-result-success') is True
                            and record.get('observations', {}).get('other-key-plaintext-exact') is True)
                        report['checks']['pristine-persistence-control'] = (
                            before['pubring.gpg'] != after['pubring.gpg']
                            and before['secring.gpg'] == after['secring.gpg'])
                    else:
                        report['checks'][casename] = result.returncode == 0 and record['status'] == 'pass'
                        report['checks'][casename + '-keyrings-unchanged'] = before == after
                        if profile == 'protected':
                            recovered = require(gpg('gpg-native-encryption-oracle',
                                ['--decrypt', config['cipherOut']], password=password))
                            report['checks']['gpg-exact-native-output'] = recovered == TEXT
                            verified = gpg('gpg-native-signature-oracle',
                                           ['--status-fd', '1', '--verify', config['signatureOut'], textfile], password=password)
                            report['checks']['gpg-native-signature'] = verified.returncode == 0 and (
                                b'[GNUPG:] VALIDSIG ' + config['aSigning'].encode() + b' ') in verified.stdout
                            require(verified)
                del secret
                for record in records.values():
                    del record['secret']
                    del record['public']
            report['status'] = 'pass' if all(report['checks'].values()) else 'fail'
        except (OSError, RuntimeError, ValueError, StopIteration, subprocess.TimeoutExpired) as error:
            report['status'] = 'error'
            report['error_type'] = type(error).__name__
        finally:
            cleanup = call('cleanup-own-agent', [tools['gpgconf'], '--homedir', ghome, '--kill', 'gpg-agent'])
            report['fixture_agent_cleanup'] = cleanup.returncode == 0
            if not report['fixture_agent_cleanup']:
                report['status'] = 'error'
    report['temporary_root_removed'] = not root.exists()
    if not report['temporary_root_removed']:
        report['status'] = 'error'
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
