#!/usr/bin/env python3
"""Prepare source-only research fixtures; does not execute crypto or install tools.
Preserves pinned pass/OTP logic; fixture wrappers must be supplied by a reviewed
runner with isolated homes/password FDs. Not a production pass backend.
"""
import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path

PINS = {
    'pass': '30452550a9183b09d5d688d8ae093282c2710464bc9a682774584500f4150a26',
    'otp.bash': '1c0b08efecdf5180e78b11e0554affd0d1bf39c9063db1bcb16119cf214fff48',
}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def prepare(original, name, engine, prefix):
    text = original.decode()
    if name == 'pass':
        substitutions = [
            ('GPG="/usr/bin/sailfish-gpg"', 'GPG="' + str(prefix / ('fixture-' + engine)) + '"'),
            ('SYSTEM_EXTENSION_DIR=""', 'SYSTEM_EXTENSION_DIR="' + str(prefix / engine / 'extensions') + '"'),
        ]
        for old, new in substitutions:
            if text.count(old) != 1:
                raise ValueError('unexpected pinned baseline')
            text = text.replace(old, new)
        lines = text.splitlines(keepends=True)
        if sum('PLATFORM_FUNCTION_FILE' in line for line in lines) != 1:
            raise ValueError('unexpected Linux installation marker')
        text = ''.join(line for line in lines if 'PLATFORM_FUNCTION_FILE' not in line)
        if engine == 'rnp':
            old = 'GPG_OPTS=( $PASSWORD_STORE_GPG_OPTS "--quiet" "--yes" "--compress-algo=none" "--no-encrypt-to" )'
            if text.count(old) != 1:
                raise ValueError('unexpected GPG options')
            text = text.replace(old, 'GPG_OPTS=( "--notty" "--overwrite" "-z" "0" )')
    else:
        old = 'OATH=/usr/libexec/sailfish-oath/bin/oathtool'
        if text.count(old) != 1:
            raise ValueError('unexpected OATH baseline')
        text = text.replace(old, 'OATH=' + str(prefix / 'fixture-oath'))
    if engine == 'rnp':
        text = text.replace('$GPG -d "${GPG_OPTS[@]}" "$passfile"',
                            '$GPG -d --output - "${GPG_OPTS[@]}" "$passfile"')
        text = ''.join(line.replace(' -o ', ' --output ') if '$GPG' in line else line
                       for line in text.splitlines(keepends=True))
    return text.encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--fixture-prefix', required=True, type=Path)
    args = parser.parse_args()
    prefix = str(args.fixture_prefix)
    if not args.fixture_prefix.is_absolute() or not re.fullmatch(r'/[A-Za-z0-9_./-]+', prefix):
        parser.error('fixture prefix must be a simple absolute research path')
    originals = {name: (args.sources / name).read_bytes() for name in PINS}
    for name, value in originals.items():
        if digest(value) != PINS[name]:
            raise ValueError('pinned source mismatch: ' + name)
    args.output.mkdir(parents=True, exist_ok=False)
    records = {}
    for engine in ('gpg', 'rnp'):
        records[engine] = {}
        for name, original in originals.items():
            final = prepare(original, name, engine, args.fixture_prefix)
            target = args.output / engine / ('pass' if name == 'pass' else 'extensions/otp.bash')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(final)
            target.chmod(0o600)  # Source-only; wrappers/execution intentionally absent.
            records[engine][name] = {
                'original_sha256': digest(original), 'fixture_sha256': digest(final),
                'patch': ''.join(difflib.unified_diff(original.decode().splitlines(True),
                               final.decode().splitlines(True), fromfile=name + '-pinned',
                               tofile=engine + '/' + name)),
            }
    (args.output / 'manifest.json').write_text(json.dumps({
        'state': 'source fixtures only; not executed or production-ready',
        'fixture_prefix': prefix, 'records': records,
        'supported_probe_subset': ['list', 'find', 'show', 'insert', 'otp insert/append/code'],
        'not_supported_or_tested': ['init/reencrypt/mv', 'GPG groups or signed policy',
                                   'Git', 'HOTP', 'untrusted paths', 'production API'],
    }, indent=2) + '\n')
    print('Prepared source-only fixtures and exact diff manifest; no crypto executed.')


if __name__ == '__main__':
    main()
