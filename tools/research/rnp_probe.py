#!/usr/bin/env python3
"""Bounded synthetic RNP 0.18.1 engine probe; not a pass adapter.
Usage: python3 tools/research/rnp_probe.py --check-tools
       python3 tools/research/rnp_probe.py --run > /chosen/evidence.json
Requires separately authorized installed rnp/rnpkeys, gpg/gpgconf, oathtool.
Only self-generated keys and RFC6238 public data. No fixture material survives.
Failure cases exercise real staged CLI output and caller replacement-on-success;
not pass atomicity, power-loss recovery or concurrent-writing acceptance.
Manuals: https://www.rnpgp.org/docs/rnp-1/ and /docs/rnpkeys-1/ (v0.18.1).
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import parse_qs, urlsplit

TOOLS = ('gpg', 'gpgconf', 'rnp', 'rnpkeys', 'oathtool')
PASSWORD = b'public-synthetic-probe-password\n'
TEXT = b'synthetic password\nnotes: multiline fixture\n'
URI = b'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&digits=8&period=30\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-tools', action='store_true')
    mode.add_argument('--run', action='store_true')
    args = parser.parse_args()
    paths = {name: shutil.which(name) for name in TOOLS}
    report = {'probe': 'rnp-cli-v0.18.1', 'tools': paths, 'versions': {},
              'commands': [], 'cases': [], 'status': 'not-run',
              'not_tested': ['Curve25519', 'full pass/pass-otp execution',
                             'nested or signed .gpg-id policy', 'HOTP persistence',
                             'smartcards', 'concurrent writes', 'Sailfish packaging']}
    missing = [name for name, path in paths.items() if path is None]
    if missing:
        report.update(status='missing-prerequisites', missing=missing)
        print(json.dumps(report, indent=2))
        return 2
    with tempfile.TemporaryDirectory(prefix='sailfish-rnp-probe-') as temp:
        root = Path(temp)
        env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': temp,
               'GNUPGHOME': str(root / 'unused'), 'LANG': 'C', 'LC_ALL': 'C'}
        homes = {}
        for name in ('g-old', 'g-new', 'r-old', 'r-new', 'r-empty'):
            home = root / name
            home.mkdir(mode=0o700)
            homes[name] = home

        def call(case, tool, options, data=b'', password=None, timeout=90):
            command = [paths[tool]] + [str(x) for x in options]
            fds = ()
            readfd = None
            if password is not None:
                readfd, writefd = os.pipe()
                os.write(writefd, password)
                os.close(writefd)
                fds = (readfd,)
                flag = '--passphrase-fd' if tool == 'gpg' else '--pass-fd'
                command[1:1] = [flag, str(readfd)]
            try:
                result = subprocess.run(command, input=data, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, env=env, pass_fds=fds,
                                        timeout=timeout, start_new_session=True)
                report['commands'].append({'id': case, 'tool': tool,
                                           'exit': result.returncode})
                return result
            finally:
                if readfd is not None:
                    os.close(readfd)

        def gopts(which):
            return ['--no-options', '--homedir', homes[which], '--batch',
                    '--no-tty', '--pinentry-mode', 'loopback']

        def ropts(which):
            return ['--homedir', homes[which], '--notty']

        def require(result):
            if result.returncode:
                raise RuntimeError('fixture-command-failed')
            return result.stdout

        def check(name, condition):
            report['cases'].append({'id': name, 'status': 'pass' if condition else 'fail'})

        def encrypt(name, home, recipient, content, output='-'):
            return call(name, 'rnp', ropts(home) + ['--encrypt', '--recipient', recipient,
                                                  '--output', output], content)

        def decrypt(name, home, ciphertext, password=PASSWORD, source=None, output='-'):
            path = source if source is not None else root / 'input.gpg'
            if source is None:
                path.write_bytes(ciphertext)
            return call(name, 'rnp', ropts(home) + ['--decrypt', '--output', output, path],
                        password=password)

        try:
            for tool in TOOLS:
                options = gopts('g-old') + ['--version'] if tool == 'gpg' else ['--version']
                version = require(call('version-' + tool, tool, options)).decode(errors='replace')
                report['versions'][tool] = version.splitlines()[0]
            if any('0.18.1' not in report['versions'][tool] for tool in ('rnp', 'rnpkeys')):
                raise RuntimeError('unexpected-rnp-version')
            if args.check_tools:
                report['status'] = 'prerequisites-present-not-executed'
            else:
                recipients = {}
                for tag in ('old', 'new'):
                    gh, rh = 'g-' + tag, 'r-' + tag
                    uid = 'Synthetic ' + tag + ' <' + tag + '@fixture.invalid>'
                    require(call('generate-' + tag, 'gpg', gopts(gh) +
                                 ['--quick-gen-key', uid, 'rsa2048', 'encr', '0'],
                                 password=PASSWORD))
                    listing = require(call('fingerprint-' + tag, 'gpg', gopts(gh) +
                                           ['--with-colons', '--list-keys']))
                    recipients[tag] = next(line.split(b':')[9].decode()
                                           for line in listing.splitlines() if line.startswith(b'fpr:'))
                    secret = require(call('export-secret-' + tag, 'gpg', gopts(gh) +
                                          ['--export-secret-keys', recipients[tag]], password=PASSWORD))
                    public = require(call('export-public-' + tag, 'gpg', gopts(gh) +
                                          ['--export', recipients[tag]]))
                    keyfile = root / (tag + '.key')
                    keyfile.write_bytes(secret)
                    require(call('import-secret-' + tag, 'rnpkeys', ropts(rh) + ['--import', keyfile]))
                    keyfile.write_bytes(public)
                    require(call('import-public-' + tag, 'rnpkeys', ropts('r-old') + ['--import', keyfile]))
                    keyfile.unlink()
                g_cipher = require(call('gpg-encrypt', 'gpg', gopts('g-old') +
                                        ['--trust-model', 'always', '--recipient', recipients['old'],
                                         '--encrypt', '--output', '-'], TEXT))
                recovered = decrypt('gpg-to-rnp', 'r-old', g_cipher)
                check('gpg-to-rnp', recovered.returncode == 0 and recovered.stdout == TEXT)
                r_cipher = require(encrypt('rnp-encrypt', 'r-old', recipients['old'], TEXT))
                result = call('rnp-to-gpg', 'gpg', gopts('g-old') + ['--decrypt'],
                              r_cipher, password=PASSWORD)
                check('rnp-to-gpg', result.returncode == 0 and result.stdout == TEXT)
                plaintext = require(decrypt('reencrypt-read', 'r-old', g_cipher))
                changed = require(encrypt('reencrypt-write', 'r-old', recipients['new'], plaintext))
                new = decrypt('new-recipient', 'r-new', changed)
                old = decrypt('old-recipient-denied', 'r-old', changed)
                check('reencrypt-new-recipient', new.returncode == 0 and new.stdout == TEXT)
                check('reencrypt-old-recipient-denied', old.returncode != 0)
                original = root / 'entry.gpg'
                original.write_bytes(g_cipher)
                staged = root / 'staged.gpg'
                for name, attempt in [
                    ('empty-keyring', lambda: decrypt('empty-keyring', 'r-empty', g_cipher, source=original, output=staged)),
                    ('wrong-password', lambda: decrypt('wrong-password', 'r-old', g_cipher, b'wrong\n', source=original, output=staged)),
                    ('invalid-ciphertext', lambda: decrypt('invalid-ciphertext', 'r-old', b'invalid ciphertext', output=staged)),
                    ('missing-recipient', lambda: encrypt('missing-recipient', 'r-old', 'absent@fixture.invalid', TEXT, output=staged))]:
                    if staged.exists():
                        staged.unlink()
                    result = attempt()
                    # RNP writes a real staged file; caller commits only success.
                    if result.returncode == 0 and staged.is_file():
                        staged.replace(original)
                    check(name + '-failure-exit-staged-preserves-original',
                          result.returncode != 0 and original.read_bytes() == g_cipher)
                    original.write_bytes(g_cipher)
                if staged.exists():
                    staged.unlink()
                entry = URI + b'notes: original\n'
                for label, content in [('original', entry), ('edited', URI + b'notes: changed\n')]:
                    cipher = require(encrypt('otp-encrypt-' + label, 'r-old', recipients['old'], content))
                    result = decrypt('otp-decrypt-' + label, 'r-old', cipher)
                    check('otp-content-' + label, result.returncode == 0 and result.stdout == content)
                # Use the URI recovered from the edited encrypted entry.
                if result.returncode != 0:
                    raise RuntimeError('otp-entry-not-recovered')
                otp = parse_qs(urlsplit(result.stdout.splitlines()[0].decode('ascii')).query)
                if otp.get('period') != ['30'] or otp.get('digits') != ['8']:
                    raise RuntimeError('unexpected-published-vector-parameters')
                code = call('rfc6238-oathtool', 'oathtool',
                            ['--totp=SHA1', '--base32', '--digits=8', '--now=@59', otp['secret'][0]])
                check('rfc6238-fixed-time', code.returncode == 0 and code.stdout.strip() == b'94287082')
                report['status'] = 'pass' if all(x['status'] == 'pass' for x in report['cases']) else 'fail'
        except (RuntimeError, subprocess.TimeoutExpired, OSError, StopIteration, ValueError, KeyError) as error:
            report['status'] = 'error'
            report['error_type'] = type(error).__name__
        finally:
            cleanup = True
            for name in ('g-old', 'g-new'):
                try:
                    result = call('cleanup-' + name, 'gpgconf',
                                  ['--homedir', homes[name], '--kill', 'gpg-agent'], timeout=15)
                    cleanup = cleanup and result.returncode == 0
                except (OSError, subprocess.TimeoutExpired):
                    cleanup = False
            report['fixture_agent_cleanup'] = cleanup
            if not cleanup:
                report['status'] = 'error'
    report['temporary_files_removed'] = not root.exists()
    print(json.dumps(report, indent=2))
    return 0 if report['status'] in ('pass', 'prerequisites-present-not-executed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
