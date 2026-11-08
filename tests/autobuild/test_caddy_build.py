"""Exercise the build script with local Git upstreams and real patch application."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CaddyBuildTests(unittest.TestCase):
    def build(self, native_idle=False, broken_quic=False):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            core, plugin, bin_dir = [base / name for name in ('core', 'plugin', 'bin')]
            for repo in (core, plugin):
                repo.mkdir()
                self.git(repo, 'init', '-q')
                self.git(repo, 'config', 'user.name', 'test')
                self.git(repo, 'config', 'user.email', 'test@example.com')
            http = core / 'modules/caddyhttp'
            http.mkdir(parents=True)
            (http / 'idletimeout.go').write_text(
                'func IdleTimeoutsFromContext() {}\n' if native_idle else 'package caddyhttp\n')
            original = 'first\nsecond\nthird\nold-quic\nfourth\nfifth\nsixth\n'
            source = core / 'server.go'
            source.write_text(original)
            self.git(core, 'add', '.')
            self.git(core, 'commit', '-qm', 'core')
            source.write_text(original.replace('old-quic', 'patched-quic'))
            (plugin / 'caddy-sing-quic-bbrv1.patch').write_text(self.git(core, 'diff'))
            self.git(core, 'checkout', '--', '.')
            idle = http / 'idletimeout.go'
            idle.write_text('func IdleTimeoutsFromContext() {}\n')
            # On a new core this deliberately invalid patch must be skipped.
            (plugin / 'caddy-read-idle-timeout.patch').write_text(
                'invalid backport\n' if native_idle else self.git(core, 'diff'))
            self.git(core, 'checkout', '--', '.')
            # A new import outside the two retained context lines is harmless.
            if native_idle:
                source.write_text(original.replace('sixth', 'new-import'))
            if broken_quic:
                source.write_text(original.replace('old-quic', 'incompatible-quic'))
            self.git(core, 'add', '.')
            self.git(core, 'commit', '--allow-empty', '-qm', 'selected release')
            self.git(core, 'tag', 'v2.11.9')
            self.git(plugin, 'add', '.')
            self.git(plugin, 'commit', '-qm', 'pinned patches')
            sha = self.git(plugin, 'rev-parse', 'HEAD').strip()
            bin_dir.mkdir()
            xcaddy = bin_dir / 'xcaddy'
            xcaddy.write_text('''#!/usr/bin/env python3
import json, os, pathlib, sys
core = pathlib.Path(next(arg.split('=', 1)[1] for arg in sys.argv if arg.startswith('github.com/caddyserver/caddy/v2=')))
assert 'patched-quic' in (core / 'server.go').read_text()
assert 'func IdleTimeoutsFromContext(' in (core / 'modules/caddyhttp/idletimeout.go').read_text()
pathlib.Path(os.environ['BUILD_CAPTURE']).write_text(json.dumps(sys.argv[1:]))
''')
            xcaddy.chmod(0o755)
            capture = base / 'capture.json'
            env = {**os.environ, 'PATH': str(bin_dir) + os.pathsep + os.environ['PATH'],
                   'CADDY_VERSION': '2.11.9', 'CADDY_NAIVE_VERSION': sha,
                   'BUILD_CAPTURE': str(capture), 'GIT_CONFIG_COUNT': '2'}
            for index, (repo, url) in enumerate(((core, 'https://github.com/caddyserver/caddy.git'),
                                               (plugin, 'https://github.com/klzgrad/forwardproxy.git'))):
                env[f'GIT_CONFIG_KEY_{index}'] = f'url.{repo.as_uri()}.insteadOf'
                env[f'GIT_CONFIG_VALUE_{index}'] = url
            result = subprocess.run(['sh', str(ROOT / 'caddy/build-caddy.sh'), '--with', 'test/plugin@' + sha],
                                    env=env, capture_output=True, text=True)
            if broken_quic:
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(capture.exists(), result.stdout + result.stderr)
            else:
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                args = json.loads(capture.read_text())
                self.assertEqual(args[:2], ['build', 'v2.11.9'])
                self.assertEqual(args[-2:], ['--with', 'test/plugin@' + sha])

    def git(self, repo, *args):
        return subprocess.run(['git', '-C', str(repo), *args], check=True,
                              capture_output=True, text=True).stdout

    def test_old_core_receives_both_patches(self):
        self.build()

    def test_new_core_keeps_native_idle_api_and_tolerates_unrelated_context_change(self):
        self.build(native_idle=True)

    def test_incompatible_quic_change_stops_before_compilation(self):
        self.build(broken_quic=True)
