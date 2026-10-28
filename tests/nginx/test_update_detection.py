"""Exercise update decisions using Docker Hub responses and saved build state."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/check-nginx-version.py"
OLD = "sha256:" + "a" * 64
NEW = "sha256:" + "b" * 64
VERSION = "stable-alpine3.24"


def response(digest=NEW, version=VERSION):
    return {"results": [
        {"name": "stable-alpine", "digest": digest},
        {"name": version, "digest": digest},
        {"name": "stable-alpine99.99", "digest": OLD},
        {"name": "stable-alpine3.24-slim", "digest": digest},
    ]}


class UpdateDetectionTests(unittest.TestCase):
    def run_check(self, payload, version=VERSION, digest=OLD, event="schedule"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tags.json").write_text(json.dumps(payload))
            if version is not None:
                (root / ".nginx-version").write_text(version + "\n")
            if digest is not None:
                (root / ".nginx-digest").write_text(digest + "\n")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(root / "tags.json")],
                cwd=root, capture_output=True, text=True,
                env={**os.environ, "GITHUB_EVENT_NAME": event,
                     "GITHUB_ENV": str(root / "env")},
            )
            output = (root / "env").read_text() if (root / "env").exists() else ""
            # Detection must never mark an image as published before a build succeeds.
            self.assertEqual((root / ".nginx-digest").exists(), digest is not None)
            if digest is not None:
                self.assertEqual((root / ".nginx-digest").read_text(), digest + "\n")
            return result, output

    def assert_decision(self, expected, **kwargs):
        result, output = self.run_check(response(), **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"BUILD_NEEDED={str(expected).lower()}\n", output)
        self.assertIn(f"NGINX_BASE_REF={VERSION}@{NEW}\n", output)

    def test_changed_digest_under_same_tag_rebuilds(self):
        self.assert_decision(True)

    def test_unchanged_upstream_skips_scheduled_build(self):
        self.assert_decision(False, digest=NEW)

    def test_missing_digest_migrates_existing_record(self):
        self.assert_decision(True, digest=None)

    def test_missing_records_builds_initial_image(self):
        self.assert_decision(True, version=None, digest=None)

    def test_new_alpine_tag_rebuilds(self):
        self.assert_decision(True, version="stable-alpine3.23", digest=NEW)

    def test_manual_and_source_changes_force_rebuild(self):
        for event in ("push", "workflow_dispatch"):
            with self.subTest(event=event):
                self.assert_decision(True, digest=NEW, event=event)

    def test_invalid_api_responses_fail_without_build_outputs(self):
        for payload in ({"message": "rate limit"}, {"results": []},
                        response(""), response("sha256:invalid"),
                        {"results": [{"name": "stable-alpine", "digest": NEW}]}):
            with self.subTest(payload=payload):
                result, output = self.run_check(payload)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output, "")

    def test_matching_alpine_tags_sort_numerically(self):
        payload = response(version="stable-alpine3.9")
        payload["results"].append({"name": VERSION, "digest": NEW})
        result, output = self.run_check(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"NGINX_VERSION={VERSION}\n", output)


if __name__ == "__main__":
    unittest.main()
