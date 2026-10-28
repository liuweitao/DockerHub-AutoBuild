#!/usr/bin/env python3
"""Commit published inputs, retrying concurrent updates from other workflows."""
import json
import os
from pathlib import Path
import re
import subprocess
import time


def git(*args, check=True):
    return subprocess.run(['git', *args], check=check)


def record(state):
    target = state['target']
    if not re.fullmatch(r'[a-z0-9]+', target):
        raise ValueError('Invalid build target')
    files = {'.build-state/' + target + '.json': json.dumps(state, indent=2, sort_keys=True) + '\n'}
    for path, value in state['records'].items():
        if not re.fullmatch(r'\.[a-z0-9-]+-(?:version|digest)', path):
            raise ValueError('Invalid version record path')
        files[path] = value + '\n'
    for path, content in files.items():
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', 'github-actions[bot]@users.noreply.github.com')
    git('add', '--', *files)
    if git('diff', '--cached', '--quiet', check=False).returncode == 0:
        print('Published inputs are already recorded')
        return
    git('commit', '-m', f'Update published {target} upstream state')
    for attempt in range(5):
        git('pull', '--rebase', 'origin', 'master')
        if git('push', 'origin', 'HEAD:master', check=False).returncode == 0:
            return
        if attempt < 4:
            time.sleep(2 ** attempt)
    raise RuntimeError('Could not record published inputs after five push attempts')


if __name__ == '__main__':
    record(json.loads(os.environ['BUILD_STATE']))
