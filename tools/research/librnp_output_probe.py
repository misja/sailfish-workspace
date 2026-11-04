#!/usr/bin/env python3
"""Bounded synthetic RNP0.18.1 native RANDOM-output experiment.

Run only as ubuntu UID1000 in the approved isolated research container:
    python3 librnp_output_probe.py --run
Uses installed librnp via Python ctypes, no installation or compilation.
All keys/passwords/content are self-created synthetic fixtures. Reports contain
only return codes, counts, identity hashes and comparisons, never key/plaintext
or raw diagnostics. No custom writer, retry or recovery implementation is tested.
"""
import argparse
import ctypes as C
import ctypes.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

SOURCE_COMMIT = 'aad1892e4d8423398a0b973bd0a7e4544c359afc'
PASSWORD = b'public-synthetic-native-output-password\n'
ORIGINAL_TEXT = b'synthetic original entry\nnotes: original\n'
NEW_TEXT = b'synthetic changed entry\nnotes: changed\n'
RNP_OUTPUT_FILE_OVERWRITE = 1 << 0
RNP_OUTPUT_FILE_RANDOM = 1 << 1
RNP_LOAD_SAVE_PUBLIC_KEYS = 1 << 0
RNP_LOAD_SAVE_SECRET_KEYS = 1 << 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', required=True)
    parser.parse_args()
    report = {'probe': 'librnp-native-random-output', 'status': 'not-run',
              'source_commit': SOURCE_COMMIT, 'uid': os.geteuid(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'commands': [], 'native_calls': [], 'cases': [],
              'not_tested': ['Sailfish toolchain/packages', 'production backend/API',
                             'crash durability/fsync', 'concurrency', 'recovery/retry policy',
                             'general save safety', 'OTP decrypt-status correction']}
    tools = {name: shutil.which(name) for name in ('gpg', 'gpgconf')}
    library = ctypes.util.find_library('rnp')
    if os.geteuid() != 1000 or not library or not all(tools.values()):
        report.update(status='prerequisites-not-met', librnp_found=bool(library), tools=tools)
        print(json.dumps(report, indent=2))
        return 2
    lib = C.CDLL(library)
    V, S, U, Z, B = C.c_void_p, C.c_char_p, C.c_uint32, C.c_size_t, C.c_bool
    P = C.POINTER
    PASS_CB = C.CFUNCTYPE(B, V, V, V, S, V, Z)
    signatures = {
        'rnp_ffi_create': ([P(V), S, S], U),
        'rnp_ffi_destroy': ([V], U),
        'rnp_ffi_set_pass_provider': ([V, PASS_CB, V], U),
        'rnp_input_from_memory': ([P(V), V, Z, B], U),
        'rnp_input_destroy': ([V], U),
        'rnp_load_keys': ([V, S, V, U], U),
        'rnp_locate_key': ([V, S, S, P(V)], U),
        'rnp_key_handle_destroy': ([V], U),
        'rnp_output_to_file': ([P(V), S, U], U),
        'rnp_output_finish': ([V], U),
        'rnp_output_destroy': ([V], U),
        'rnp_op_encrypt_create': ([P(V), V, V, V], U),
        'rnp_op_encrypt_add_recipient': ([V, V], U),
        'rnp_op_encrypt_execute': ([V], U),
        'rnp_op_encrypt_destroy': ([V], U),
        'rnp_decrypt': ([V, V, V], U),
        'rnp_version_string': ([], S),
    }
    for name, (arguments, result) in signatures.items():
        function = getattr(lib, name)
        function.argtypes, function.restype = arguments, result
    report['librnp_version'] = lib.rnp_version_string().decode('ascii')
    if report['librnp_version'] != '0.18.1':
        report['status'] = 'unexpected-librnp-version'
        print(json.dumps(report, indent=2))
        return 2
    # Hash the actual loaded shared object rather than guessing a distro path.
    loaded = {line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
              if '/librnp.so.' in line}
    if len(loaded) != 1:
        report['status'] = 'ambiguous-loaded-library'
        print(json.dumps(report, indent=2))
        return 2
    libpath = Path(loaded.pop())
    report['librnp_path'] = str(libpath)
    report['librnp_sha256'] = hashlib.sha256(libpath.read_bytes()).hexdigest()

    def native(label, name, *arguments):
        result = int(getattr(lib, name)(*arguments))
        report['native_calls'].append({'id': label, 'api': name, 'result': result})
        return result

    def require(result):
        if result != 0:
            raise RuntimeError('fixture-command-failed')

    def memory(label, data):
        handle = V()
        buffer = C.create_string_buffer(data)
        require(native(label, 'rnp_input_from_memory', C.byref(handle), buffer, len(data), True))
        return handle

    with tempfile.TemporaryDirectory(prefix='sailfish-librnp-output-') as temp:
        root = Path(temp)
        root.chmod(0o700)
        home = root / 'synthetic-gpg'
        home.mkdir(mode=0o700)
        env = {'PATH': '/usr/bin:/bin', 'HOME': temp, 'GNUPGHOME': str(home),
               'LANG': 'C', 'LC_ALL': 'C'}

        def gpg(label, arguments, data=b'', password=None, tool='gpg'):
            command = [tools[tool]]
            if tool == 'gpg':
                command += ['--no-options', '--homedir', str(home), '--batch', '--no-tty',
                            '--pinentry-mode', 'loopback']
            fd = None
            try:
                if password is not None:
                    fd, writer = os.pipe()
                    try:
                        os.write(writer, password)
                    finally:
                        os.close(writer)
                    command += ['--passphrase-fd', str(fd)]
                command += [str(x) for x in arguments]
                result = subprocess.run(command, input=data, env=env,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        pass_fds=() if fd is None else (fd,), timeout=90)
                report['commands'].append({'id': label, 'exit': result.returncode})
                require(result.returncode)
                return result.stdout
            finally:
                if fd is not None:
                    os.close(fd)

        ffi, key = V(), V()
        password_calls = [0]

        @PASS_CB
        def wrong_password(_ffi, _context, _key, _reason, buffer, length):
            password_calls[0] += 1
            wrong = b'wrong-synthetic-password\0'
            if not buffer or length < len(wrong):
                return False
            C.memmove(buffer, wrong, len(wrong))
            return True

        # Native diagnostics can include paths/content; suppress the process FD,
        # not only Python stderr. Never read or copy this ephemeral diagnostic file.
        with tempfile.TemporaryFile(dir=root) as diagnostics:
            saved_stderr = os.dup(2)
            os.dup2(diagnostics.fileno(), 2)
            try:
                report['gpg_version'] = gpg('gpg-version', ['--version']).decode().splitlines()[0]
                if '2.4.8' not in report['gpg_version']:
                    raise RuntimeError('unexpected-gpg-version')
                gpg('generate-modern-primary', ['--quick-gen-key', 'Synthetic <native@fixture.invalid>',
                                                'ed25519', 'cert,sign', '0'], password=PASSWORD)
                listing = gpg('primary-fingerprint', ['--with-colons', '--list-keys'])
                fingerprint = next(line.split(b':')[9] for line in listing.splitlines()
                                   if line.startswith(b'fpr:'))
                gpg('generate-modern-encryption-subkey', ['--quick-add-key', fingerprint.decode(),
                                                         'cv25519', 'encr', '0'], password=PASSWORD)
                listing = gpg('verify-modern-curves', ['--with-colons', '--list-keys'])
                modern = (any(line.startswith(b'pub:') and b':ed25519:' in line for line in listing.splitlines()) and
                          any(line.startswith(b'sub:') and b':cv25519:' in line for line in listing.splitlines()))
                if not modern:
                    raise RuntimeError('unexpected-fixture-key-type')
                report['modern_key_verified'] = True
                secret = gpg('export-synthetic-secret', ['--export-secret-keys', fingerprint.decode()], password=PASSWORD)
                require(native('ffi-create', 'rnp_ffi_create', C.byref(ffi), b'GPG', b'GPG'))
                imported = memory('synthetic-import-input', secret)
                try:
                    require(native('load-synthetic-key', 'rnp_load_keys', ffi, b'GPG', imported,
                                   RNP_LOAD_SAVE_PUBLIC_KEYS | RNP_LOAD_SAVE_SECRET_KEYS))
                finally:
                    require(native('destroy-import-input', 'rnp_input_destroy', imported))
                del secret
                require(native('set-wrong-password-callback', 'rnp_ffi_set_pass_provider', ffi, wrong_password, None))
                require(native('locate-own-key', 'rnp_locate_key', ffi, b'fingerprint', fingerprint, C.byref(key)))
                if not key:
                    raise RuntimeError('synthetic-key-not-found')
                original = gpg('encrypt-original', ['--trust-model', 'always', '--recipient', fingerprint.decode(),
                                                   '--encrypt', '--output', '-'], ORIGINAL_TEXT)
                for case in ('success', 'missing-recipient', 'crypto-failure', 'finish-failure'):
                    directory = root / case
                    directory.mkdir(mode=0o700)
                    target = directory / 'entry.gpg'
                    target.write_bytes(original)
                    output, input_handle, operation, absent = V(), V(), V(), V()
                    record = {'id': case, 'finish_called': False}
                    report['cases'].append(record)
                    try:
                        require(native(case + '-output', 'rnp_output_to_file', C.byref(output), os.fsencode(target),
                                       RNP_OUTPUT_FILE_RANDOM | RNP_OUTPUT_FILE_OVERWRITE))
                        record['original_after_open'] = target.read_bytes() == original
                        if case == 'missing-recipient':
                            rc = native(case + '-locate', 'rnp_locate_key', ffi, b'fingerprint', b'0' * 40,
                                        C.byref(absent))
                            record.update(locate_result=rc, recipient_found=bool(absent))
                            # No operation or finish after a missing recipient.
                        elif case == 'crypto-failure':
                            input_handle = memory(case + '-input', original)
                            before = password_calls[0]
                            rc = native(case + '-decrypt', 'rnp_decrypt', ffi, input_handle, output)
                            record.update(crypto_result=rc, password_callback_calls=password_calls[0] - before)
                            # No finish after failed decryption.
                        else:
                            input_handle = memory(case + '-input', NEW_TEXT)
                            require(native(case + '-create', 'rnp_op_encrypt_create', C.byref(operation), ffi,
                                           input_handle, output))
                            require(native(case + '-recipient', 'rnp_op_encrypt_add_recipient', operation, key))
                            rc = native(case + '-encrypt', 'rnp_op_encrypt_execute', operation)
                            record['crypto_result'] = rc
                            require(rc)
                            record['original_before_finish'] = target.read_bytes() == original
                            record['temporaries_before_finish'] = len(list(directory.glob('entry.gpg.rnp-tmp.*')))
                            if case == 'finish-failure':
                                directory.chmod(0o500)
                            record['finish_called'] = True
                            record['finish_result'] = native(case + '-finish', 'rnp_output_finish', output)
                            # Destroy after success can auto-finish: every successful
                            # encryption therefore receives an explicit checked finish.
                    finally:
                        cleanup_results = []
                        try:
                            if operation:
                                cleanup_results.append(native(case + '-destroy-op', 'rnp_op_encrypt_destroy', operation))
                            if input_handle:
                                cleanup_results.append(native(case + '-destroy-input', 'rnp_input_destroy', input_handle))
                            if output:
                                cleanup_results.append(native(case + '-destroy-output', 'rnp_output_destroy', output))
                            if absent:
                                cleanup_results.append(native(case + '-destroy-absent-key', 'rnp_key_handle_destroy', absent))
                        finally:
                            directory.chmod(0o700)
                        if any(cleanup_results):
                            raise RuntimeError('native-resource-cleanup-failed')
                    record['original_after_destroy'] = target.read_bytes() == original
                    record['temporaries_after_destroy'] = len(list(directory.glob('entry.gpg.rnp-tmp.*')))
                    if case == 'success':
                        recovered = gpg('decrypt-committed-output', ['--decrypt', target], password=PASSWORD)
                        record['committed_plaintext_exact'] = recovered == NEW_TEXT
                        passed = (record['finish_result'] == 0 and record['original_before_finish'] and
                                  not record['original_after_destroy'] and record['committed_plaintext_exact'] and
                                  record['temporaries_after_destroy'] == 0)
                    elif case == 'missing-recipient':
                        passed = rc == 0 and not record['recipient_found'] and record['original_after_destroy']
                    elif case == 'crypto-failure':
                        passed = (rc != 0 and record['password_callback_calls'] > 0 and
                                  record['original_after_destroy'])
                    else:
                        passed = (record['finish_result'] != 0 and record['crypto_result'] == 0 and
                                  record['original_before_finish'] and record['original_after_destroy'])
                    record['status'] = 'pass' if passed and record['original_after_open'] else 'fail'
                report['status'] = 'pass' if all(x['status'] == 'pass' for x in report['cases']) else 'fail'
            except (OSError, RuntimeError, StopIteration, ValueError, subprocess.TimeoutExpired) as error:
                report['status'] = 'error'
                report['error_type'] = type(error).__name__
            finally:
                try:
                    cleanup_results = []
                    if key:
                        cleanup_results.append(native('destroy-own-key', 'rnp_key_handle_destroy', key))
                    if ffi:
                        cleanup_results.append(native('destroy-ffi', 'rnp_ffi_destroy', ffi))
                    gpg('cleanup-own-agent', ['--homedir', home, '--kill', 'gpg-agent'], tool='gpgconf')
                    report['fixture_agent_cleanup'] = True
                    if any(cleanup_results):
                        report['status'] = 'error'
                except (OSError, RuntimeError, subprocess.TimeoutExpired):
                    report['fixture_agent_cleanup'] = False
                    report['status'] = 'error'
                finally:
                    os.dup2(saved_stderr, 2)
                    os.close(saved_stderr)
    report['temporary_root_removed'] = not root.exists()
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
