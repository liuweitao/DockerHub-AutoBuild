"""Check release selection, immutable rule inputs and cross-compiler behavior."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_upstreams import upstream, DIGEST

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'a' * 40
RULES = 'b' * 40
CHECKSUM = 'c' * 64


class XraySelectionTests(unittest.TestCase):
    def resolve(self, go_mod=b'module example\n\ngo 1.27\n', checksum=CHECKSUM):
        def request(url):
            if url.endswith('/go.mod'):
                self.assertIn('/' + SOURCE + '/', url)
                return go_mod, {}
            self.assertIn('/' + RULES + '/', url)
            return (checksum + '  data.dat\n').encode(), {}
        with patch.object(upstream, 'release', return_value={'tag_name': 'v26.11.9', 'assets': []}) as release, \
             patch.object(upstream, 'commit', side_effect=[SOURCE, RULES]) as commit, \
             patch.object(upstream, 'request', side_effect=request), \
             patch.object(upstream, 'pin_image', side_effect=lambda name: name + '@' + DIGEST), \
             patch.object(upstream, 'read_version', return_value='26.10.31'):
            result = upstream.resolve('xray')
        release.assert_called_once_with('XTLS/Xray-core', '')
        self.assertEqual(commit.call_args_list[0].args, ('XTLS/Xray-core', 'v26.11.9'))
        self.assertEqual(commit.call_args_list[1].args, ('XTLS/Xray-rules-dat', 'release'))
        return result

    def test_source_release_does_not_need_prebuilt_architecture_assets(self):
        state, builds, latest = self.resolve()
        args = dict(line.split('=', 1) for line in builds[0]['args'].splitlines())
        self.assertTrue(latest)
        self.assertEqual(builds[0]['platforms'], 'linux/amd64,linux/arm64,linux/arm/v7')
        self.assertEqual(builds[0]['tags'], '26.11.9\nlatest')
        self.assertEqual(args['XRAY_COMMIT'], SOURCE)
        self.assertEqual(args['GO_IMAGE'], 'golang:1.27-alpine@' + DIGEST)
        self.assertEqual(args['ALPINE_IMAGE'], 'alpine:latest@' + DIGEST)
        for name in ('GEOIP', 'GEOSITE'):
            self.assertIn('/' + RULES + '/', args[name + '_URL'])
            self.assertEqual(args[name + '_SHA256'], CHECKSUM)
        self.assertEqual(state['versions'], {'main': '26.11.9', 'source': SOURCE, 'rules': RULES})
        self.assertEqual(state['assets'], {'geoip.dat': CHECKSUM, 'geosite.dat': CHECKSUM})
        self.assertEqual(state['records'], {'.xray-version': '26.11.9'})

    def test_historical_release_selects_its_own_compiler(self):
        state, builds, _ = self.resolve(go_mod=b'go 1.25.3\n')
        self.assertIn('GO_IMAGE=golang:1.25.3-alpine@' + DIGEST, builds[0]['args'])

    def test_missing_go_directive_stops_resolution(self):
        with self.assertRaisesRegex(ValueError, 'Go version'):
            self.resolve(go_mod=b'module example\n')

    def test_invalid_rule_checksum_stops_resolution(self):
        for checksum in ('', 'error', '0' * 63):
            with self.subTest(checksum=checksum), self.assertRaisesRegex(ValueError, 'digest'):
                self.resolve(checksum=checksum)


class XrayCompilerTests(unittest.TestCase):
    def build(self, arch, variant='', compiler_status=0):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            compiler = base / 'go'
            compiler.write_text("""#!/usr/bin/env python3
import json, os, pathlib, sys
pathlib.Path(os.environ['CAPTURE']).write_text(json.dumps({
    'args': sys.argv[1:], 'env': {k: os.environ.get(k) for k in ('GOOS', 'GOARCH', 'GOARM', 'CGO_ENABLED')}
}))
sys.exit(int(os.environ['COMPILER_STATUS']))
""")
            compiler.chmod(0o755)
            capture = base / 'capture.json'
            output = base / 'out/xray'
            env = {**os.environ, 'PATH': str(base) + os.pathsep + os.environ['PATH'],
                   'TARGETOS': 'linux', 'TARGETARCH': arch, 'TARGETVARIANT': variant,
                   'XRAY_COMMIT': SOURCE, 'GOARM': '5', 'CAPTURE': str(capture),
                   'COMPILER_STATUS': str(compiler_status)}
            result = subprocess.run(['sh', str(ROOT / 'xray/build-xray.sh'), str(output)],
                                    env=env, capture_output=True, text=True)
            data = json.loads(capture.read_text()) if capture.exists() else None
            if data:
                self.assertEqual(data['args'][-3:], ['-o', str(output), './main'])
            return result, data

    def test_supported_platforms_compile_static_binaries_with_correct_arm_version(self):
        for arch, variant, arm in (('amd64', '', None), ('arm64', '', None), ('arm', 'v7', '7')):
            with self.subTest(arch=arch):
                result, data = self.build(arch, variant)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(data['env'], {'GOOS': 'linux', 'GOARCH': arch, 'GOARM': arm, 'CGO_ENABLED': '0'})
                for arg in ('-mod=readonly', '-trimpath', '-buildvcs=false', '-gcflags=all=-l=4'):
                    self.assertIn(arg, data['args'])
                self.assertTrue(any('core.build=' + SOURCE in arg for arg in data['args']))

    def test_unsupported_platform_is_rejected_before_compilation(self):
        for arch, variant in (('arm', 'v6'), ('386', '')):
            with self.subTest(arch=arch):
                result, data = self.build(arch, variant)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Unsupported Xray platform', result.stderr)
                self.assertIsNone(data)

    def test_compiler_failure_is_propagated(self):
        result, _ = self.build('amd64', compiler_status=42)
        self.assertEqual(result.returncode, 42)
