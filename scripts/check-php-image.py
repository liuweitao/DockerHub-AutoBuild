#!/usr/bin/env python3
"""Exercise the PHP binary and the actual FPM/Apache worker before publishing."""
import json
import pathlib
import socket
import struct
import subprocess
import sys
import time
import urllib.request


def docker(*args, check=True):
    return subprocess.run(['docker', *args], check=check, text=True, capture_output=True)


def validate(payload, profile, sapi):
    data = json.loads(payload)
    assert data['sapi'] == sapi, data
    assert data['upload_progress'] in ('', '0'), data
    required = {
        'php74': {'PDO', 'pdo_mysql', 'bcmath', 'gd', 'redis', 'mongodb', 'openssl'},
        'phpcms': {'mysqli', 'gd', 'openssl'},
        'php8': {'PDO', 'pdo_mysql', 'imap', 'redis', 'openssl'},
        'nextcloud': {'bz2', 'gd', 'intl', 'pdo_mysql', 'zip'},
    }[profile]
    assert required <= set(data['extensions']), (required - set(data['extensions']))
    version = tuple(int(part) for part in data['version'].split('.'))
    if profile in ('php74', 'phpcms'):
        assert version == (7, 4, 33), version
    else:
        minimum = {(8, 2): (8, 2, 35), (8, 3): (8, 3, 36),
                   (8, 4): (8, 4, 27), (8, 5): (8, 5, 12)}
        assert version[:2] in minimum and version >= minimum[version[:2]], version
    if profile == 'phpcms' and sapi == 'fpm-fcgi':
        assert data['uid'] == 1000 and data['gid'] == 1000, data
    return data


def fcgi(port):
    def record(kind, body):
        padding = (-len(body)) % 8
        return struct.pack('!BBHHBB', 1, kind, 1, len(body), padding, 0) + body + b'\0' * padding

    params = {'SCRIPT_FILENAME': '/var/www/html/health.php', 'SCRIPT_NAME': '/health.php',
              'REQUEST_METHOD': 'GET', 'SERVER_PROTOCOL': 'HTTP/1.1',
              'SERVER_NAME': 'localhost', 'SERVER_PORT': '80', 'QUERY_STRING': '',
              'CONTENT_LENGTH': '0', 'REDIRECT_STATUS': '200'}
    encoded = b''
    for key, value in params.items():
        key, value = key.encode(), value.encode()
        encoded += bytes([len(key), len(value)]) + key + value
    wire = record(1, struct.pack('!HB5x', 1, 0)) + record(4, encoded) + record(4, b'') + record(5, b'')
    output = b''
    with socket.create_connection(('127.0.0.1', port), timeout=5) as client:
        client.sendall(wire)
        def read(size):
            data = b''
            while len(data) < size:
                chunk = client.recv(size - len(data))
                if not chunk:
                    raise RuntimeError('Incomplete FastCGI response')
                data += chunk
            return data
        while True:
            _, kind, _, length, padding, _ = struct.unpack('!BBHHBB', read(8))
            body = read(length)
            read(padding)
            if kind == 6:
                output += body
            if kind == 3:
                break
    return output.split(b'\r\n\r\n', 1)[1]


def main():
    image, profile = sys.argv[1:]
    fixtures = pathlib.Path(__file__).resolve().parent.parent / 'tests/php'
    mount = f'{fixtures}:/var/www/html:ro'
    cli = docker('run', '--rm', '--entrypoint', 'php', '-v', mount, image, '/var/www/html/health.php')
    print('CLI:', validate(cli.stdout, profile, 'cli'))
    if profile in ('php74', 'phpcms'):
        # The official 7.4 backport must exit immediately on OOM. The old engine
        # instead unwinds through request shutdown and invokes this callback.
        oom = docker('run', '--rm', '--entrypoint', 'php', image,
                     '-d', 'memory_limit=16M', '-r',
                     'register_shutdown_function(function () { echo "SHUTDOWN_RAN"; }); str_repeat("x", 32 * 1024 * 1024);',
                     check=False)
        assert oom.returncode == 1, (oom.returncode, oom.stdout, oom.stderr)
        assert 'Allowed memory size' in oom.stdout + oom.stderr, oom.stderr
        assert 'SHUTDOWN_RAN' not in oom.stdout + oom.stderr, 'Unpatched OOM shutdown behavior'
    else:
        # Both updated engines must still enforce finite memory limits.
        oom = docker('run', '--rm', '--entrypoint', 'php', image,
                     '-d', 'memory_limit=16M', '-r', 'str_repeat("x", 32 * 1024 * 1024);', check=False)
        assert oom.returncode != 0, 'Memory limit no longer enforced'
        assert 'memory' in (oom.stdout + oom.stderr).lower(), oom.stderr
    if profile != 'nextcloud':
        if profile != 'phpcms':
            docker('run', '--rm', '--entrypoint', 'composer', image, '--version')
        docker('run', '--rm', '--entrypoint', 'php-fpm', image, '-t')
    port = 80 if profile == 'nextcloud' else 9000
    entrypoint = 'apache2-foreground' if profile == 'nextcloud' else 'php-fpm'
    container = docker('run', '-d', '--entrypoint', entrypoint, '-p', f'127.0.0.1::{port}',
                       '-v', mount, image).stdout.strip()
    try:
        mapped = json.loads(docker('inspect', container).stdout)[0]['NetworkSettings']['Ports'][f'{port}/tcp'][0]['HostPort']
        for attempt in range(30):
            try:
                if profile == 'nextcloud':
                    with urllib.request.urlopen(f'http://127.0.0.1:{mapped}/health.php', timeout=5) as response:
                        payload = response.read()
                else:
                    payload = fcgi(int(mapped))
                break
            except (OSError, RuntimeError):
                if attempt == 29:
                    raise
                time.sleep(1)
        print('Web:', validate(payload, profile, 'apache2handler' if profile == 'nextcloud' else 'fpm-fcgi'))
    finally:
        print(docker('logs', container, check=False).stderr)
        docker('rm', '-fv', container, check=False)
    print(f'{profile}: security and runtime checks passed')


if __name__ == '__main__':
    main()
