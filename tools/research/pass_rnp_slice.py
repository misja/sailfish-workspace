#!/usr/bin/env python3
"""Synthetic real-pass/GPG versus native-RNP slice; not a production backend.

Run only in the approved isolated container as its unprivileged fixture user:
  python3 pass_rnp_slice.py --sources /reviewed/baseline --run
The adjacent pinned-source preparer is required. JSON contains no key material,
plaintext, password values or raw tool output. All fixture data is self-created
or the published RFC6238 SHA1 vector. No default keyring is accessed.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

import prepare_pass_rnp_fixture as preparer

PASSWORD = b'public-synthetic-slice-password\n'
TEXT = b'synthetic entry\nnotes: multiline fixture\n'
URI = b'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&digits=8&period=30'
TOOLS = ('bash', 'gpg', 'gpgconf', 'rnp', 'rnpkeys', 'oathtool', 'tree', 'git', 'getopt')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--run', action='store_true', required=True)
    args = parser.parse_args()
    report = {'probe': 'real-pass-native-rnp-slice', 'status': 'not-run',
              'commands': [], 'cases': [], 'observations': [], 'versions': {},
              'source_sha256': {}, 'not_tested': [
                  'Sailfish build/dependency acceptance', 'production migration/API',
                  'init/reencrypt/mv', 'GPG metadata/groups/signed policy',
                  'HOTP', 'Git integration', 'smartcards', 'untrusted paths',
                  'concurrency/crash recovery', 'agent equivalence']}
    report['recipient_subset'] = 'exact fingerprints; root inheritance, nearest nested policy and multiple recipients; inline comments not exercised'
    report['gpg_fixture_trust'] = 'always for self-created synthetic recipients only; no production trust equivalence claimed'
    paths = {tool: shutil.which(tool) for tool in TOOLS}
    missing = [tool for tool, path in paths.items() if path is None]
    if missing:
        report.update(status='missing-prerequisites', missing=missing)
        print(json.dumps(report, indent=2))
        return 2
    originals = {name: (args.sources / name).read_bytes() for name in preparer.PINS}
    if any(sha(value) != preparer.PINS[name] for name, value in originals.items()):
        report['status'] = 'source-pin-mismatch'
        print(json.dumps(report, indent=2))
        return 2
    report['source_sha256'] = {name: sha(value) for name, value in originals.items()}
    report['harness_sha256'] = sha(Path(__file__).read_bytes())
    report['preparer_sha256'] = sha(Path(preparer.__file__).read_bytes())
    with tempfile.TemporaryDirectory(prefix='sailfish-pass-rnp-slice-') as temp:
        root = Path(temp)
        root.chmod(0o700)
        store = root / 'store'
        store.mkdir(mode=0o700)
        env = {'PATH': '/usr/bin:/bin', 'HOME': temp, 'LANG': 'C', 'LC_ALL': 'C',
               'GNUPGHOME': str(root / 'unused'), 'PASSWORD_STORE_DIR': str(store),
               'PASSWORD_STORE_ENABLE_EXTENSIONS': 'false', 'TERM': 'dumb'}
        homes = {}
        for name in ('g-a', 'g-b', 'r-a', 'r-b', 'g-empty', 'r-empty'):
            homes[name] = root / name
            homes[name].mkdir(mode=0o700)

        def call(label, command, data=b'', password=None, extra=None, timeout=90):
            childenv = dict(env)
            if extra:
                childenv.update(extra)
            fd = None
            try:
                if password is not None:
                    fd, writefd = os.pipe()
                    try:
                        os.write(writefd, password)
                    finally:
                        os.close(writefd)
                    childenv['FIXTURE_PASSWORD_FD'] = str(fd)
                process = subprocess.Popen([str(x) for x in command], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           env=childenv, pass_fds=() if fd is None else (fd,),
                                           start_new_session=True)
                try:
                    stdout, stderr = process.communicate(data, timeout=timeout)
                except subprocess.TimeoutExpired:
                    # Only this command's newly created process group is killed;
                    # separately spawned fixture GPG agents are handled below.
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

        def require(result):
            if result.returncode:
                raise RuntimeError('fixture-command-failed')
            return result.stdout

        def check(label, condition):
            report['cases'].append({'id': label, 'status': 'pass' if condition else 'fail'})

        def gpg(label, home, options, data=b'', password=PASSWORD):
            # Wrapper receives the password descriptor through the environment;
            # no secret is placed in command arguments or reports.
            return call(label, [root / 'fixture-gpg'] + list(options), data, password,
                        {'FIXTURE_CRYPTO_HOME': str(homes[home])})

        def rkeys(label, home, key):
            return call(label, [paths['rnpkeys'], '--homedir', homes[home],
                                '--notty', '--import', key])

        def runpass(label, engine, options, data=b'', identity='a', password=PASSWORD):
            return call(label, [paths['bash'], root / engine / 'pass'] + list(options),
                        data, password, {'FIXTURE_CRYPTO_HOME': str(homes[engine[0] + '-' + identity])})

        try:
            # Fixed absolute tool paths and native arguments only. These launchers
            # do not parse or translate GPG options or emulate its metadata.
            wrappers = {
                'fixture-gpg': '#!/bin/sh\nexec ' + paths['gpg'] +
                    ' --no-options --homedir "$FIXTURE_CRYPTO_HOME" --batch --no-tty'
                    ' --pinentry-mode loopback --passphrase-fd "$FIXTURE_PASSWORD_FD"'
                    ' --trust-model always "$@"\n',
                'fixture-rnp': '#!/bin/sh\nexec ' + paths['rnp'] +
                    ' --homedir "$FIXTURE_CRYPTO_HOME" --pass-fd "$FIXTURE_PASSWORD_FD" "$@"\n',
                'fixture-oath': '#!/bin/sh\nexec ' + paths['oathtool'] + ' --now=@59 "$@"\n',
            }
            report['wrapper_sha256'] = {}
            for name, content in wrappers.items():
                target = root / name
                target.write_text(content)
                target.chmod(0o700)
                report['wrapper_sha256'][name] = sha(target.read_bytes())
            report['fixture_sha256'] = {}
            report['fixture_patches'] = {}
            for engine in ('gpg', 'rnp'):
                report['fixture_sha256'][engine] = {}
                report['fixture_patches'][engine] = {}
                for name, original in originals.items():
                    content = preparer.prepare(original, name, engine, root)
                    target = root / engine / ('pass' if name == 'pass' else 'extensions/otp.bash')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                    # pass requires executable extensions even though it sources them.
                    target.chmod(0o700 if name == 'otp.bash' else 0o600)
                    report['fixture_sha256'][engine][name] = sha(content)
                    report['fixture_patches'][engine][name] = ''.join(difflib.unified_diff(
                        original.decode().splitlines(True), content.decode().splitlines(True),
                        fromfile=name + '-pinned', tofile=engine + '/' + name))
            for tool in TOOLS:
                result = call('version-' + tool, [paths[tool], '--version'])
                require(result)
                report['versions'][tool] = result.stdout.decode(errors='replace').splitlines()[0]
            if any('0.18.1' not in report['versions'][tool] for tool in ('rnp', 'rnpkeys')):
                raise RuntimeError('unexpected-rnp-version')
            if '2.4.8' not in report['versions']['gpg'] or '2.6.14' not in report['versions']['oathtool']:
                raise RuntimeError('unexpected-fixture-tool-version')
            fingerprints, public = {}, {}
            for tag in ('a', 'b'):
                home = 'g-' + tag
                uid = 'Synthetic ' + tag + ' <' + tag + '@fixture.invalid>'
                require(gpg('generate-' + tag, home,
                            ['--quick-gen-key', uid, 'ed25519', 'cert,sign', '0']))
                listing = require(gpg('fingerprint-' + tag, home, ['--with-colons', '--list-keys']))
                fingerprints[tag] = next(line.split(b':')[9].decode() for line in listing.splitlines()
                                         if line.startswith(b'fpr:'))
                require(gpg('add-encryption-subkey-' + tag, home,
                            ['--quick-add-key', fingerprints[tag], 'cv25519', 'encr', '0']))
                listing = require(gpg('verify-curves-' + tag, home, ['--with-colons', '--list-keys']))
                check('ed25519-cv25519-' + tag,
                      any(line.startswith(b'pub:') and b':ed25519:' in line for line in listing.splitlines()) and
                      any(line.startswith(b'sub:') and b':cv25519:' in line for line in listing.splitlines()))
                secret = require(gpg('export-secret-' + tag, home,
                                     ['--export-secret-keys', fingerprints[tag]]))
                public[tag] = require(gpg('export-public-' + tag, home, ['--export', fingerprints[tag]]))
                key = root / 'synthetic-transfer.key'
                key.write_bytes(secret)
                key.chmod(0o600)
                require(rkeys('import-secret-' + tag, 'r-' + tag, key))
                key.unlink()
                del secret
            for tag in ('a', 'b'):
                other = 'b' if tag == 'a' else 'a'
                require(gpg('import-peer-public-' + tag, 'g-' + tag, ['--import'], public[other]))
                key = root / 'synthetic-transfer.key'
                key.write_bytes(public[other])
                require(rkeys('import-peer-public-' + tag, 'r-' + tag, key))
                key.unlink()
            (store / '.gpg-id').write_text(fingerprints['a'] + '\n')
            for dirname, recipients in [('nested', ['b']), ('multi', ['a', 'b'])]:
                directory = store / dirname
                directory.mkdir()
                (directory / '.gpg-id').write_text(''.join(fingerprints[x] + '\n' for x in recipients))
            for engine in ('gpg', 'rnp'):
                peer = 'rnp' if engine == 'gpg' else 'gpg'
                # The second engine operates on exactly the same store and paths.
                require(runpass(engine + '-write-root', engine, ['insert', '-m', '-f', 'plain'], TEXT))
                result = runpass(engine + '-peer-read-root', peer, ['show', 'plain'])
                check(engine + '-write-peer-read', result.returncode == 0 and result.stdout == TEXT)
                require(runpass(engine + '-write-inherited', engine,
                                ['insert', '-m', '-f', 'inherited/deep/item'], TEXT))
                result = runpass(engine + '-read-inherited', peer, ['show', 'inherited/deep/item'])
                check(engine + '-root-policy-inheritance', result.returncode == 0 and result.stdout == TEXT)
                require(runpass(engine + '-write-nested', engine, ['insert', '-m', '-f', 'nested/item'], TEXT))
                allowed = runpass(engine + '-nested-b', peer, ['show', 'nested/item'], identity='b')
                denied = runpass(engine + '-nested-a-denied', peer, ['show', 'nested/item'])
                check(engine + '-nearest-nested-policy', allowed.returncode == 0 and allowed.stdout == TEXT and
                      denied.returncode != 0)
                require(runpass(engine + '-write-multi', engine, ['insert', '-m', '-f', 'multi/item'], TEXT))
                for identity in ('a', 'b'):
                    result = runpass(engine + '-multi-' + identity, peer, ['show', 'multi/item'], identity=identity)
                    check(engine + '-multi-independent-' + identity, result.returncode == 0 and result.stdout == TEXT)
                require(runpass(engine + '-otp-insert', engine, ['otp', 'insert', '-e', '-f', 'token'], URI + b'\n'))
                result = runpass(engine + '-otp-peer-code', peer, ['otp', 'code', 'token'])
                check(engine + '-otp-insert-peer-code', result.returncode == 0 and result.stdout == b'94287082\n')
                updated_uri = URI.replace(b'/RFC6238?', b'/RFC6238-updated?')
                # yesno accepts a non-terminal fixture stdin; pass-otp's force
                # option alone does not bypass this existing-token prompt.
                require(runpass(engine + '-otp-update', peer, ['otp', 'append', '-e', '-f', 'token'],
                                updated_uri + b'\n'))
                result = runpass(engine + '-otp-update-read', engine, ['show', 'token'])
                check(engine + '-otp-existing-token-update', result.returncode == 0 and
                      result.stdout == updated_uri + b'\n')
                result = runpass(engine + '-otp-update-code', engine, ['otp', 'code', 'token'])
                check(engine + '-otp-update-code', result.returncode == 0 and result.stdout == b'94287082\n')
                require(runpass(engine + '-otp-append-base', engine, ['insert', '-m', '-f', 'append'], TEXT))
                require(runpass(engine + '-otp-append', engine, ['otp', 'append', '-e', '-f', 'append'], URI + b'\n'))
                result = runpass(engine + '-otp-append-peer-read', peer, ['show', 'append'])
                check(engine + '-otp-append-preserves-text', result.returncode == 0 and result.stdout == TEXT + URI + b'\n')
                result = runpass(engine + '-otp-append-peer-code', peer, ['otp', 'code', 'append'])
                check(engine + '-otp-append-peer-code', result.returncode == 0 and result.stdout == b'94287082\n')
            for command in (['list'], ['find', 'item']):
                left = runpass('gpg-' + command[0], 'gpg', command)
                right = runpass('rnp-' + command[0], 'rnp', command)
                check('real-pass-' + command[0] + '-matches', left.returncode == right.returncode == 0 and
                      left.stdout == right.stdout and b'item' in left.stdout)
            for engine in ('gpg', 'rnp'):
                existing = store / 'plain.gpg'
                original = existing.read_bytes()
                result = runpass(engine + '-empty-keyring', engine, ['show', 'plain'], identity='empty')
                check(engine + '-empty-keyring-failure', result.returncode != 0 and existing.read_bytes() == original)
                # Kill only this fixture's GPG agent so cached passphrases cannot
                # turn the wrong-password test into a false positive.
                require(call(engine + '-clear-fixture-agent', [paths['gpgconf'], '--homedir', homes['g-a'],
                                                               '--kill', 'gpg-agent']))
                result = runpass(engine + '-wrong-password', engine, ['show', 'plain'], password=b'wrong\n')
                check(engine + '-wrong-password-failure', result.returncode != 0 and existing.read_bytes() == original)
                invalid = store / 'invalid.gpg'
                invalid.write_bytes(b'invalid synthetic ciphertext\n')
                result = runpass(engine + '-invalid-ciphertext', engine, ['show', 'invalid'])
                check(engine + '-invalid-ciphertext-failure', result.returncode != 0)
                invalid.unlink()
                (store / '.gpg-id').write_text('absent@fixture.invalid\n')
                result = runpass(engine + '-missing-recipient-write', engine, ['insert', '-m', '-f', 'plain'], TEXT)
                after = existing.read_bytes() if existing.exists() else None
                check(engine + '-missing-recipient-failure-exit', result.returncode != 0)
                report['observations'].append({'id': engine + '-direct-write-missing-recipient',
                                               'exit': result.returncode,
                                               'original_ciphertext_preserved': after == original,
                                               'destination_exists': existing.exists()})
                # Restore fixture state only after measuring the real command.
                existing.write_bytes(original)
                (store / '.gpg-id').write_text(fingerprints['a'] + '\n')
                require(call(engine + '-clear-append-agent', [paths['gpgconf'], '--homedir', homes['g-a'],
                                                             '--kill', 'gpg-agent']))
                # Existing pass-otp uses process substitution for append reads;
                # record whether it propagates decrypt failure or overwrites.
                result = runpass(engine + '-wrong-password-otp-append', engine,
                                 ['otp', 'append', '-e', '-f', 'plain'], URI + b'\n', password=b'wrong\n')
                after = existing.read_bytes() if existing.exists() else None
                report['observations'].append({'id': engine + '-append-after-decrypt-failure',
                                               'exit': result.returncode,
                                               'original_ciphertext_preserved': after == original,
                                               'destination_exists': existing.exists()})
                existing.write_bytes(original)
            report['status'] = 'pass' if all(x['status'] == 'pass' for x in report['cases']) else 'fail'
            if any(not x['original_ciphertext_preserved'] for x in report['observations']):
                report['write_preservation_finding'] = True
        except (RuntimeError, OSError, subprocess.TimeoutExpired, StopIteration, ValueError) as error:
            report['status'] = 'error'
            report['error_type'] = type(error).__name__
        finally:
            cleanup = True
            for tag in ('a', 'b', 'empty'):
                try:
                    result = call('cleanup-agent-' + tag,
                                  [paths['gpgconf'], '--homedir', homes['g-' + tag], '--kill', 'gpg-agent'], timeout=15)
                    cleanup = cleanup and result.returncode == 0
                except (OSError, subprocess.TimeoutExpired):
                    cleanup = False
            report['fixture_agent_cleanup'] = cleanup
            if not cleanup:
                report['status'] = 'error'
    report['temporary_files_removed'] = not root.exists()
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
