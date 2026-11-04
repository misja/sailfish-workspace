"""Protected synthetic OpenPGP data for the standard password-agent route."""
import hashlib

def prepare_unlock(root, config, keys, gpg, require, generator, password):
    if not password:
        raise RuntimeError('protected-fixture-password-required')
    file=root/'fixture-password'
    file.write_bytes(password)
    file.chmod(0o600)
    store=root/'store'
    store.mkdir(mode=0o700)
    (store/'.gpg-id').write_text(keys['a']['primary']+'\n')
    plain=(b'synthetic password\nnotes before\n'
           b'otpauth://totp/RFC6238?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&digits=8&period=30\n'
           b'notes after\n')
    (root/'text').write_bytes(plain)
    for name,tag in [('entry','a'),('wrong','b')]:
        path=store/(name+'.gpg')
        path.write_bytes(require(gpg('seed-protected-'+name,generator,
            ['--encrypt','--recipient',keys[tag]['primary'],'--output','-'],plain)))
        path.chmod(0o600)
    symmetric=store/'symmetric.gpg'
    symmetric.write_bytes(require(gpg('seed-protected-symmetric',generator,
        ['--symmetric','--cipher-algo','AES256','--output','-'],plain)))
    symmetric.chmod(0o600)
    recovered=require(gpg('validate-symmetric-positive',generator,['--decrypt',str(symmetric)]))
    if recovered!=plain:
        raise RuntimeError('invalid-symmetric-fixture')
    config.update(store=str(store),entry=str(store/'entry.gpg'))
    return {'guards':{str(path):hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in store.glob('*.gpg')},
            'outputs':[('store/entry.gpg',plain,{'a'}),('store/wrong.gpg',plain,{'b'})]}
