import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

upstream = module('upstream', 'resolve-upstream.py')
recorder = module('recorder', 'record-build-state.py')
DIGEST = 'sha256:' + 'a' * 64
OTHER = 'sha256:' + 'b' * 64


class SelectionTests(unittest.TestCase):
    def test_php_follows_official_alias_across_pages_instead_of_first_page_maximum(self):
        first = {'results': [{'name': '8.3.36-fpm-alpine3.23', 'digest': OTHER}],
                 'next': 'https://hub.docker.com/v2/repositories/library/php/tags?page=2'}
        second = {'results': [{'name': '8.5.12-fpm-alpine3.24', 'digest': DIGEST}], 'next': None}
        with patch.object(upstream, 'pin_image', return_value='php:8-fpm-alpine@' + DIGEST), \
             patch.object(upstream, 'get_json', side_effect=[first, second]) as get:
            version, image = upstream.stable_tag('php', '8-fpm-alpine', r'8\.\d+\.\d+-fpm-alpine\d+\.\d+')
        self.assertEqual(version, '8.5.12-fpm-alpine3.24')
        self.assertEqual(image, 'php:' + version + '@' + DIGEST)
        self.assertEqual(get.call_count, 2)

    def test_unpublished_official_alias_fails_instead_of_selecting_an_old_tag(self):
        with patch.object(upstream, 'pin_image', return_value='caddy:latest@' + DIGEST), \
             patch.object(upstream, 'get_json', return_value={'results': [{'name': '2.11.6', 'digest': OTHER}]}):
            with self.assertRaisesRegex(ValueError, 'No versioned tag'):
                upstream.stable_tag('caddy', 'latest', r'\d+\.\d+\.\d+')

    def test_downgrades_are_rejected_and_numeric_upgrades_are_allowed(self):
        for old, new in [('8.5.12-fpm-alpine3.24', '8.3.36-fpm-alpine3.23'), ('26.10.21', '26.9.30')]:
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'downgrade'):
                upstream.prevent_downgrade(new, old)
        upstream.prevent_downgrade('8.5.13-fpm-alpine3.24', '8.5.12-fpm-alpine3.24')

    def test_empty_error_and_prerelease_responses_are_rejected(self):
        for data in ({'message': 'rate limited'}, {'tag_name': ''}, {'tag_name': 'v1.2.3', 'prerelease': True}):
            with self.subTest(data=data), patch.object(upstream, 'get_json', return_value=data):
                with self.assertRaises(ValueError):
                    upstream.release('some/upstream')

    def test_missing_or_invalid_assets_stop_resolution(self):
        for data in ({'assets': []}, {'assets': [{'name': 'binary', 'digest': None}]}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                upstream.asset(data, 'binary')

    def test_manual_old_release_only_publishes_its_version(self):
        release = {'tag_name': 'v26.9.1', 'assets': [
            {'name': 'Xray-linux-' + arch + '.zip', 'digest': DIGEST} for arch in ('64', 'arm64-v8a', 'arm32-v7a')]}
        with patch.object(upstream, 'release', return_value=release), \
             patch.object(upstream, 'pin_image', return_value='alpine:latest@' + DIGEST), \
             patch.object(upstream, 'read_version', return_value='26.10.21'):
            state, builds, latest = upstream.resolve('xray', '26.9.1')
        self.assertFalse(latest)
        self.assertEqual(builds[0]['tags'], '26.9.1')
        self.assertEqual(state['records'], {})

    def test_changed_base_and_replaced_assets_trigger_scheduled_builds(self):
        state = {'target': 'naiveproxy', 'images': {'debian': DIGEST}, 'assets': {'binary': DIGEST}}
        with tempfile.TemporaryDirectory() as folder:
            old = Path.cwd()
            try:
                os.chdir(folder)
                Path('.build-state').mkdir()
                Path('.build-state/naiveproxy.json').write_text(json.dumps(state))
                self.assertFalse(upstream.build_needed('naiveproxy', state, 'schedule'))
                self.assertTrue(upstream.build_needed('naiveproxy', state, 'workflow_dispatch'))
                for key in ('images', 'assets'):
                    changed = json.loads(json.dumps(state))
                    changed[key][next(iter(changed[key]))] = OTHER
                    self.assertTrue(upstream.build_needed('naiveproxy', changed, 'schedule'))
            finally:
                os.chdir(old)

    def test_query_and_resolution_do_not_write_publication_records(self):
        with tempfile.TemporaryDirectory() as folder:
            old = Path.cwd()
            try:
                os.chdir(folder)
                with patch.object(upstream, 'pin_image', return_value='alpine:latest@' + DIGEST), \
                     patch.object(upstream, 'source_digest', return_value=DIGEST):
                    state, builds, _ = upstream.resolve('adb')
                self.assertTrue(upstream.build_needed('adb', state, 'schedule'))
                self.assertEqual(list(Path('.').iterdir()), [])
                self.assertIn(DIGEST, builds[0]['args'])
            finally:
                os.chdir(old)


class RecordTests(unittest.TestCase):
    def test_failed_push_rebases_and_retries(self):
        state = {'target': 'xray', 'records': {'.xray-version': '26.10.21'}}
        pushes = iter([subprocess.CompletedProcess([], 1), subprocess.CompletedProcess([], 0)])
        calls = []
        def git(*args, **kwargs):
            calls.append(args)
            if args[0] == 'diff': return subprocess.CompletedProcess([], 1)
            if args[0] == 'push': return next(pushes)
            return subprocess.CompletedProcess([], 0)
        with tempfile.TemporaryDirectory() as folder, patch.object(recorder, 'git', side_effect=git), \
             patch.object(recorder.time, 'sleep'):
            old = Path.cwd()
            try:
                os.chdir(folder)
                recorder.record(state)
                self.assertEqual(Path('.xray-version').read_text(), '26.10.21\n')
                self.assertEqual(json.loads(Path('.build-state/xray.json').read_text()), state)
            finally:
                os.chdir(old)
        self.assertEqual(sum(call[0] == 'pull' for call in calls), 2)
        self.assertEqual(sum(call[0] == 'push' for call in calls), 2)

    def test_recording_rebases_over_another_workflows_commit(self):
        def git(*args, cwd):
            return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            origin, first, second = [base / name for name in ('origin.git', 'first', 'second')]
            git('init', '--bare', '--initial-branch=master', str(origin), cwd=base)
            git('clone', str(origin), str(first), cwd=base)
            for path in (first,):
                git('config', 'user.name', 'test', cwd=path)
                git('config', 'user.email', 'test@example.com', cwd=path)
            (first / 'README').write_text('seed')
            git('add', '.', cwd=first); git('commit', '-m', 'seed', cwd=first); git('push', 'origin', 'master', cwd=first)
            git('clone', str(origin), str(second), cwd=base)
            git('config', 'user.name', 'test', cwd=second); git('config', 'user.email', 'test@example.com', cwd=second)
            (second / '.other-version').write_text('2')
            git('add', '.', cwd=second); git('commit', '-m', 'other workflow', cwd=second); git('push', 'origin', 'master', cwd=second)
            old = Path.cwd()
            try:
                os.chdir(first)
                recorder.record({'target': 'realm', 'records': {'.realm-version': '2.9.6'}})
            finally:
                os.chdir(old)
            self.assertTrue((first / '.other-version').exists())
            self.assertEqual(git('rev-parse', 'HEAD', cwd=first), git('rev-parse', 'master', cwd=origin))


if __name__ == '__main__':
    unittest.main()
