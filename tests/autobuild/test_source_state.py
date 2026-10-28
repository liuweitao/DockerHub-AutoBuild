import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_upstreams import upstream


class SourceStateTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        previous = Path.cwd()
        os.chdir(self.folder.name)
        self.addCleanup(os.chdir, previous)
        self.git('init', '--initial-branch=master')
        self.git('config', 'user.name', 'test')
        self.git('config', 'user.email', 'test@example.com')
        self.git('config', 'core.autocrlf', 'false')
        self.git('config', 'core.filemode', 'true')
        self.builds = [{'file': './laravel/nginx/Dockerfile', 'context': './laravel/nginx'}]
        self.commit_file('laravel/nginx/Dockerfile', 'FROM nginx:stable-alpine\n')

    def git(self, *args):
        return subprocess.run(['git', *args], check=True, capture_output=True, text=True).stdout

    def commit_file(self, path, contents):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        self.git('add', '--', str(path))
        self.git('commit', '-m', 'Change ' + str(path))

    def digest(self):
        return upstream.source_digest('nginx', self.builds)

    def test_failed_source_build_retries_until_success_is_recorded(self):
        state = {'target': 'nginx', 'source_digest': self.digest()}
        self.commit_file('.build-state/nginx.json', json.dumps(state))
        self.assertFalse(upstream.build_needed('nginx', state, 'schedule'))
        self.commit_file('laravel/nginx/Dockerfile', 'FROM nginx:stable-alpine\nENV FOO=bar\n')
        changed = {**state, 'source_digest': self.digest()}
        self.assertNotEqual(state, changed)
        # A failed build must leave the successful publication record untouched.
        self.assertTrue(upstream.build_needed('nginx', changed, 'push'))
        for _ in range(2):
            self.assertTrue(upstream.build_needed('nginx', changed, 'schedule'))
        self.commit_file('.build-state/nginx.json', json.dumps(changed))
        self.assertEqual(self.digest(), changed['source_digest'])
        self.assertFalse(upstream.build_needed('nginx', changed, 'schedule'))

    def test_old_publication_record_migrates(self):
        self.commit_file('.build-state/nginx.json', json.dumps({'target': 'nginx'}))
        state = {'target': 'nginx', 'source_digest': self.digest()}
        self.assertTrue(upstream.build_needed('nginx', state, 'schedule'))

    def test_unrelated_and_publication_commits_do_not_change_digest(self):
        initial = self.digest()
        for path in ('.nginx-version', '.nginx-digest', '.build-state/nginx.json',
                     'README.md', 'caddy/Dockerfile', '.github/workflows/build-caddy-images.yml'):
            with self.subTest(path=path):
                self.commit_file(path, 'unrelated')
                self.assertEqual(initial, self.digest())

    def test_shared_and_target_inputs_change_digest(self):
        previous = self.digest()
        for path in ('laravel/nginx/nginx.conf', 'scripts/resolve-upstream.py',
                     'tests/php/health.php', '.dockerignore', '.gitattributes',
                     '.github/workflows/build-images.yml',
                     '.github/workflows/build-laravel-nginx-docker.yml'):
            with self.subTest(path=path):
                self.commit_file(path, 'new input')
                current = self.digest()
                self.assertNotEqual(previous, current)
                previous = current
        self.git('mv', 'laravel/nginx/nginx.conf', 'laravel/nginx/default.conf')
        self.git('commit', '-m', 'Rename input')
        renamed = self.digest()
        self.assertNotEqual(previous, renamed)
        Path('laravel/nginx/default.conf').chmod(0o755)
        self.git('add', 'laravel/nginx/default.conf')
        self.git('commit', '-m', 'Change mode')
        executable = self.digest()
        self.assertNotEqual(renamed, executable)
        self.git('rm', 'laravel/nginx/default.conf')
        self.git('commit', '-m', 'Remove input')
        self.assertNotEqual(executable, self.digest())

    def test_legacy_php_root_context_tracks_shared_backports_only(self):
        builds = [{'file': './laravel/php7.4/Dockerfile', 'context': '.'}]
        self.commit_file('laravel/php7.4/Dockerfile', 'FROM php:7.4\n')
        initial = upstream.source_digest('php74', builds)
        self.commit_file('php/common/security.patch', 'backport')
        patched = upstream.source_digest('php74', builds)
        self.assertNotEqual(initial, patched)
        self.commit_file('nextcloud/Dockerfile', 'unrelated')
        self.assertEqual(patched, upstream.source_digest('php74', builds))
