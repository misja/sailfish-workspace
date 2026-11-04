#!/usr/bin/env python3
"""Run only a scratch upstream test daemon and real public client inside SDK."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time

def stop(process):
    if process is None or process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=3)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--session-bus-address', required=True)
    p.add_argument('--client', type=Path, help='Optional manifest-pinned consumer client')
    p.add_argument('--session-agent', type=Path, help='Optional standard session-agent fixture UI')
    p.add_argument('--password-agent-plugin', type=Path)
    a = p.parse_args()
    root = a.root.resolve()
    if os.geteuid() != 1000 or root.parent != Path('/home/ubuntu') or not root.name.startswith('sailfish-rnp-api-fixture-'):
        raise RuntimeError('boundary')
    manifest = json.loads(a.manifest.read_text())
    for path, expected in manifest['artifacts'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise RuntimeError('artifact-identity')
    client = a.client.resolve() if a.client else a.build / 'secrets_rnp_api_probe'
    if str(client) not in manifest['artifacts']:
        raise RuntimeError('unreviewed-client')
    if (a.session_agent is None) != (a.password_agent_plugin is None):
        raise RuntimeError('incomplete-agent-fixture')
    for path in (a.session_agent, a.password_agent_plugin):
        if path is not None and str(path.resolve()) not in manifest['artifacts']:
            raise RuntimeError('unreviewed-agent-fixture')
    home, runtime, data, plugins = (root / n for n in ('home', 'runtime', 'data', 'plugins'))
    for path in (runtime, data, plugins, plugins / 'sqldrivers', root / 'tmp', root / 'config'):
        path.mkdir(mode=0o700, exist_ok=True)
    module = (a.build / 'libsailfishcrypto-rnp-corrected.so').resolve()
    driver = Path('/usr/lib64/qt5/plugins/sqldrivers/libqsqlcipher.so')
    if not driver.is_file():
        raise RuntimeError('standard-sqlcipher-driver-missing')
    if hashlib.sha256(driver.read_bytes()).hexdigest() != manifest['sqlcipher_driver_sha256']:
        raise RuntimeError('standard-driver-identity')
    (plugins / module.name).symlink_to(module)
    if a.password_agent_plugin is not None:
        (plugins / a.password_agent_plugin.name).symlink_to(a.password_agent_plugin.resolve())
    (plugins / 'sqldrivers' / driver.name).symlink_to(driver)
    env = {'PATH': '/usr/bin:/bin', 'HOME': str(home), 'USER': 'ubuntu', 'LANG': 'C', 'LC_ALL': 'C',
           'XDG_RUNTIME_DIR': str(runtime), 'XDG_DATA_HOME': str(data),
           'XDG_CONFIG_HOME': str(root / 'config'), 'TMPDIR': str(root / 'tmp'),
           'QT_LOGGING_TO_CONSOLE': '1',
           'DBUS_SYSTEM_BUS_ADDRESS': 'unix:path=' + str(root / 'nonexistent-system-bus'),
           'SAILFISH_RNP_FIXTURE_PLUGINS': str(plugins)}
    report = {'status': 'fail', 'checks': {}, 'client': {}, 'boundary': 'private SDK test daemon'}
    daemon = agent = None
    if a.session_agent is not None:
        env['QT_LOGGING_RULES'] = 'org.sailfishos.secrets.plugin.authentication.passwordagent.debug=true'
    try:
        address = a.session_bus_address
        if not address.startswith('unix:path=' + str(root / 'session-bus') + ','):
            raise RuntimeError('private-bus-address')
        env['DBUS_SESSION_BUS_ADDRESS'] = address
        report['private_bus_address'] = address
        report['session_bus_owner'] = 'outer SDK Ubuntu controller'
        report['private_bus_socket_exists'] = (root / 'session-bus').is_socket()
        if Path('/usr/bin/dbus-send').is_file():
            probe = subprocess.run(['/usr/bin/dbus-send', '--session', '--print-reply',
                '--dest=org.freedesktop.DBus', '/org/freedesktop/DBus',
                'org.freedesktop.DBus.ListNames'], capture_output=True, env=env, timeout=10, text=True)
            report['bus_probe'] = {'exit': probe.returncode, 'stdout': probe.stdout, 'stderr': probe.stderr}
        with (root / 'daemon.stdout').open('wb') as out, (root / 'daemon.stderr').open('wb') as err:
            daemon = subprocess.Popen([str(a.build / 'secrets_rnp_fixture_daemon'), '--test'],
                                      stdout=out, stderr=err, env=env, start_new_session=True)
            deadline = time.monotonic() + 15
            socket = runtime / 'sailfishsecretsd/p2pSocket'
            while not socket.exists():
                if daemon.poll() is not None:
                    raise RuntimeError('daemon-startup-exit')
                if time.monotonic() > deadline:
                    raise RuntimeError('daemon-startup-timeout')
                time.sleep(0.05)
            if a.session_agent is not None:
                with (root / 'agent.stdout').open('wb') as agent_out, (root / 'agent.stderr').open('wb') as agent_err:
                    agent = subprocess.Popen([str(a.session_agent), str(root)], stdout=agent_out,
                                             stderr=agent_err, env=env, start_new_session=True)
                deadline = time.monotonic() + 15
                trace_path = root / 'agent-trace.json'
                while not trace_path.exists():
                    if agent.poll() is not None:
                        raise RuntimeError('session-agent-startup-exit')
                    if time.monotonic() > deadline:
                        raise RuntimeError('session-agent-startup-timeout')
                    time.sleep(0.05)
                config_path = root / 'config.json'
                config = json.loads(config_path.read_text())
                config['daemonPid'] = daemon.pid
                config_path.write_text(json.dumps(config))
            maps = Path('/proc') / str(daemon.pid) / 'maps'
            report['daemon_maps_before_client'] = maps.read_text()
            result = subprocess.run([str(client), str(root / 'config.json')],
                                    capture_output=True, env=env, timeout=90, text=True)
            report['client_exit'] = result.returncode
            report['client_stderr'] = result.stderr
            report['client'] = json.loads(result.stdout)
            report['daemon_maps_after_client'] = maps.read_text()
            if a.password_agent_plugin is not None:
                report['checks']['standard-passwordagent-mapped'] = str(a.password_agent_plugin.resolve()) in report['daemon_maps_after_client']
                events = json.loads((root / 'agent-trace.json').read_text()).get('events', [])
                intentional = any(event.get('kind') == 'agent-disconnect' for event in events)
                if intentional:
                    try:
                        agent.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        pass
                report['checks']['scripted-ui-agent-lifecycle'] = agent.poll() == 0 if intentional else agent.poll() is None
            report['checks']['actual-module-mapped'] = str(module) in report['daemon_maps_after_client']
            report['checks']['standard-sqlcipher-mapped'] = 'libqsqlcipher.so' in report['daemon_maps_after_client']
            report['checks']['public-requests'] = result.returncode == 0 and report['client']['status'] == 'pass'
            report['checks']['private-p2p-socket'] = socket.is_socket()
            report['checks']['daemon-still-running'] = daemon.poll() is None
            report['checks']['private-data-written'] = any(data.rglob('*.db'))
            report['metadata_files'] = [str(p.relative_to(root)) for p in data.rglob('*') if p.is_file()]
    except Exception as error:
        report['error_type'] = type(error).__name__
        report['error'] = str(error)
    finally:
        report['daemon_exit_before_cleanup'] = daemon.poll() if daemon else None
        cleanup_errors = []
        for process in (agent, daemon):
            try:
                stop(process)
            except Exception as error:
                cleanup_errors.append(type(error).__name__)
        report['process_cleanup'] = not cleanup_errors and all(
            process is None or process.poll() is not None for process in (agent, daemon))
        report['cleanup_errors'] = cleanup_errors
        if a.session_agent is not None and (root / 'agent-trace.json').exists():
            report['agent_trace'] = json.loads((root / 'agent-trace.json').read_text())
        report['agent_stderr'] = (root / 'agent.stderr').read_text() if (root / 'agent.stderr').exists() else ''
        report['daemon_stdout'] = (root / 'daemon.stdout').read_text() if (root / 'daemon.stdout').exists() else ''
        report['daemon_stderr'] = (root / 'daemon.stderr').read_text() if (root / 'daemon.stderr').exists() else ''
        report['checks']['fixture-processes-stopped'] = report['process_cleanup']
    if report['checks'] and all(report['checks'].values()) and 'error' not in report:
        report['status'] = 'pass'
    print(json.dumps(report))
    return 0 if report['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
