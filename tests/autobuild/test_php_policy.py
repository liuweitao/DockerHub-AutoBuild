import json
import unittest

from test_upstreams import ROOT, module

php = module('php_image', 'check-php-image.py')


class PHPPolicyTests(unittest.TestCase):
    def test_stable_branches_security_floors_and_previews(self):
        for case in json.loads((ROOT / 'tests/php/version-policy.json').read_text()):
            with self.subTest(version=case['version']):
                self.assertEqual(php.is_supported_php8(case['version']), case['allowed'])

    def test_future_php_keeps_runtime_requirements(self):
        for profile, extensions in (
                ('php8', ['PDO', 'pdo_mysql', 'imap', 'redis', 'openssl']),
                ('nextcloud', ['bz2', 'gd', 'intl', 'pdo_mysql', 'zip'])):
            with self.subTest(profile=profile):
                data = {'version': '8.6.0', 'sapi': 'cli', 'upload_progress': '0',
                        'extensions': extensions}
                php.validate(json.dumps(data), profile, 'cli')
                for changed in ({'extensions': []}, {'upload_progress': '1'},
                                {'version': '8.6.0RC1'}, {'sapi': 'fpm-fcgi'}):
                    with self.assertRaises(AssertionError):
                        php.validate(json.dumps({**data, **changed}), profile, 'cli')

    def test_legacy_php_stays_on_backported_release(self):
        data = {'version': '7.4.33', 'sapi': 'fpm-fcgi', 'upload_progress': '0',
                'extensions': ['mysqli', 'gd', 'openssl'], 'uid': 1000, 'gid': 1000}
        php.validate(json.dumps(data), 'phpcms', 'fpm-fcgi')
        for changed in ({'version': '7.4.32'}, {'version': '8.6.0'}, {'uid': 0}):
            with self.assertRaises(AssertionError):
                php.validate(json.dumps({**data, **changed}), 'phpcms', 'fpm-fcgi')
