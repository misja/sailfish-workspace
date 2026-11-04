"""Synthetic store fixtures; crypto uses existing same-SDK GPG oracle only."""
import base64
import hashlib
from pathlib import Path
import re

def prepare_consumer(root, config, keys, gpg, require, generator):
    store = root / 'store'
    store.mkdir(mode=0o700)
    uri = 'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&algorithm=SHA1&digits=8&period=30'
    original = ('synthetic password\nnotes before\n' + uri + '\nnotes after\n').encode()
    updated = original.replace(b'notes after\n', b'notes after updated\nextra preserved note\n')
    (root / 'text').write_bytes(original)
    (root / 'updated-text').write_bytes(updated)
    config.update(store=str(store), updatedText=str(root / 'updated-text'))
    def policy(directory, lines):
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        path = directory / '.gpg-id'
        path.write_text(lines)
        path.chmod(0o600)
    policy(store, '# existing root policy\n0x' + keys['a']['primary'] + ' # A\n')
    policy(store / 'nested', keys['b']['primary'] + '\n')
    policy(store / 'multi', keys['a']['primary'] + '\n' + keys['b']['primary'] + '\n')
    policy(store / 'unresolved', keys['a']['primary'] + '\n' + '1'*40 + '\n')
    policy(store / 'ambiguous', 'API fixture\n')
    policy(store / 'empty', '# deliberately empty policy\n\n')
    policy(store / 'unreadable', keys['a']['primary'] + '\n')
    def seed(path, recipients, content=original):
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        options = ['--encrypt', '--output', '-']
        for tag in recipients:
            options += ['--recipient', keys[tag]['primary']]
        path.write_bytes(require(gpg('seed-consumer-' + str(path.relative_to(root)),
                                     generator, options, content)))
        path.chmod(0o600)
    cases = [('root.gpg', ['a']), ('child/inherited.gpg', ['a']),
             ('nested/entry.gpg', ['b']), ('multi/entry.gpg', ['a', 'b']),
             ('unresolved/entry.gpg', ['a']), ('ambiguous/entry.gpg', ['a']),
             ('empty/entry.gpg', ['a']), ('unreadable/entry.gpg', ['a']),
             ('blocked/entry.gpg', ['a'])]
    for relative, recipients in cases:
        seed(store / relative, recipients)
    (store / 'corrupt.gpg').write_bytes(b'not an OpenPGP message')
    missing = root / 'missing-policy-store'
    missing.mkdir(mode=0o700)
    seed(missing / 'entry.gpg', ['a'])
    seed(root / 'outside.gpg', ['a'])
    (store / 'escape.gpg').symlink_to(root / 'outside.gpg')
    config.update(missingRoot=str(missing), outside=str(root / 'outside.gpg'))
    # RFC6238 reference seeds (20/32/64 ASCII bytes); standard Base32 encoding only.
    for algorithm, size in [('sha1',20),('sha256',32),('sha512',64)]:
        seed_bytes = (b'1234567890'*7)[:size]
        secret = base64.b32encode(seed_bytes).decode()
        otp_uri = 'otpauth://totp/RFC6238?secret='+secret+'&algorithm='+algorithm.upper()+'&digits=8&period=30'
        seed(store / 'otp' / (algorithm+'.gpg'), ['a'],
             ('synthetic password\nnotes before\n'+otp_uri+'\nnotes after\n').encode())
    guards = [store/'unresolved/entry.gpg',store/'ambiguous/entry.gpg',
              store/'empty/entry.gpg',store/'unreadable/entry.gpg',
              store/'blocked/entry.gpg',store/'corrupt.gpg',missing/'entry.gpg',root/'outside.gpg']
    return {'guards': {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in guards},
            'outputs': [('store/'+relative,updated,set(recipients)) for relative,recipients in cases[:4]]}

def check_consumer(root, data, client):
    maps = client.get('observations', {}).get('consumer_maps','')
    engine = re.search(r'/(?:librnp|libgpgme|libassuan)(?:[.-])',maps)
    # Check only the direct consumer: daemon legitimately loads the RNP module.
    return {'consumer-no-engine-mapped': bool(maps) and engine is None,
            'consumer-guard-ciphertexts-unchanged': all(
                hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
                for p,h in data['guards'].items())}
