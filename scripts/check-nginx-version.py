#!/usr/bin/env python3
"""Select the official stable Alpine image and detect mutable-tag updates."""

import json
import os
from pathlib import Path
import re
import sys


def select_image(payload):
    tags = payload["results"]
    stable = next(tag for tag in tags if tag["name"] == "stable-alpine")
    digest = stable.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("Official stable-alpine image has no valid SHA256 digest")

    # Keep the existing Alpine-version tag, but follow the current stable image.
    # Older Alpine aliases can still exist after the stable image moves on.
    candidates = []
    for tag in tags:
        match = re.fullmatch(r"stable-alpine([0-9]+)\.([0-9]+)", tag["name"])
        if match and tag.get("digest") == digest:
            candidates.append((tuple(map(int, match.groups())), tag["name"]))
    if not candidates:
        raise ValueError("No Alpine-version tag matches the official stable digest")
    return max(candidates)[1], digest


def read_record(path):
    return path.read_text().strip() if path.exists() else ""


def main():
    version, digest = select_image(json.loads(Path(sys.argv[1]).read_text()))
    current_version = read_record(Path(".nginx-version"))
    current_digest = read_record(Path(".nginx-digest"))
    # Explicit dispatches and source changes rebuild even if upstream is unchanged.
    force = os.environ.get("GITHUB_EVENT_NAME") in {"push", "workflow_dispatch"}
    needed = force or (version, digest) != (current_version, current_digest)
    print(f"Published upstream: {current_version}@{current_digest or '(unrecorded)'}")
    print(f"Latest upstream: {version}@{digest}; build needed: {needed}")
    with Path(os.environ["GITHUB_ENV"]).open("a") as output:
        output.write(f"BUILD_NEEDED={str(needed).lower()}\n")
        output.write(f"NGINX_VERSION={version}\nNGINX_DIGEST={digest}\n")
        output.write(f"NGINX_BASE_REF={version}@{digest}\n")


if __name__ == "__main__":
    main()
