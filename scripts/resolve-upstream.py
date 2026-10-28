#!/usr/bin/env python3
"""Resolve stable upstreams, immutable build inputs, and post-publication state."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

SHA256 = re.compile(r'sha256:[0-9a-f]{64}')
VERSION = re.compile(r'v?[0-9]+(?:\.[0-9]+)+(?:-[0-9]+)?')
ACCEPT = ', '.join(['application/vnd.oci.image.index.v1+json',
                    'application/vnd.docker.distribution.manifest.list.v2+json',
                    'application/vnd.oci.image.manifest.v1+json',
                    'application/vnd.docker.distribution.manifest.v2+json'])
WORKFLOW_FILES = {
    'adb': 'build-adb-docker.yml', 'caddy': 'build-caddy-images.yml',
    'coredns': 'build-coredns-docker.yml', 'endlessh': 'build-endlessh-docker.yml',
    'frp': 'build-frp-docker.yml', 'nginx': 'build-laravel-nginx-docker.yml',
    'php74': 'build-laravel-php74-docker.yml', 'php8': 'build-laravel-php8-docker.yml',
    'naiveproxy': 'build-naiveproxy-docker.yml', 'nextcloud': 'build-nextcloud-docker.yml',
    'paperless': 'build-paperless-ngx-docker.yml', 'phpcms': 'build-phpcms-docker.yml',
    'realm': 'build-realm-docker.yml', 'xray': 'build-xray-docker.yml',
}


def source_digest(target, builds):
    """Hash relevant committed file names, modes and contents, excluding build state.

    Both resolve and build check out the event commit. Hash its Git tree instead
    of HEAD itself so publication-only commits cannot cause a rebuild loop.
    """
    paths = {'.dockerignore', '.gitattributes', 'scripts', 'tests',
             '.github/workflows/build-images.yml',
             '.github/workflows/' + WORKFLOW_FILES[target]}
    for build in builds:
        paths.add(Path(build['file']).as_posix())
        if Path(build['context']) == Path('.'):
            # Legacy PHP builds use root context to COPY shared backport sources.
            paths.update({Path(build['file']).parent.as_posix(), 'php/common'})
        else:
            paths.add(Path(build['context']).as_posix())
    tree = subprocess.check_output(
        ['git', 'ls-tree', '-rz', '--full-tree', 'HEAD', '--', *sorted(paths)])
    if not tree:
        raise ValueError('No committed build sources found')
    return 'sha256:' + hashlib.sha256(b'build-sources-v1\0' + tree).hexdigest()


def request(url, headers=None):
    headers = {'User-Agent': 'DockerHub-AutoBuild', **(headers or {})}
    if url.startswith('https://api.github.com/') and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as response:
                return response.read(), response.headers
        except urllib.error.HTTPError as error:
            if error.code not in (403, 408, 429, 500, 502, 503, 504) or attempt == 3:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(2 ** attempt)


def get_json(url, headers=None):
    return json.loads(request(url, headers)[0])


def valid_digest(value):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f'Missing or invalid image/asset digest: {value!r}')
    return value


def pin_image(image):
    """Resolve the manifest-list digest, preserving all configured platforms."""
    repository, tag = image.rsplit(':', 1)
    if repository.startswith('ghcr.io/'):
        repository = repository.removeprefix('ghcr.io/')
        query = urllib.parse.urlencode({'service': 'ghcr.io', 'scope': f'repository:{repository}:pull'})
        token = get_json('https://ghcr.io/token?' + query)['token']
        body, headers = request(f'https://ghcr.io/v2/{repository}/manifests/{tag}',
                                {'Accept': ACCEPT, 'Authorization': 'Bearer ' + token})
        digest = headers.get('Docker-Content-Digest') or 'sha256:' + hashlib.sha256(body).hexdigest()
    else:
        if '/' not in repository:
            repository = 'library/' + repository
        digest = get_json(f'https://hub.docker.com/v2/repositories/{repository}/tags/{tag}')['digest']
    return image + '@' + valid_digest(digest)


def stable_tag(repository, alias, pattern):
    """The official moving alias selects the channel; pages only identify its version."""
    pinned = pin_image(f'{repository}:{alias}')
    digest = pinned.rsplit('@', 1)[1]
    url = f'https://hub.docker.com/v2/repositories/library/{repository}/tags?page_size=100'
    # Hub sorts by update time, not software version. Follow every required page.
    while url:
        if not url.startswith('https://hub.docker.com/v2/repositories/'):
            raise ValueError('Unexpected Docker Hub pagination URL')
        payload = get_json(url)
        matches = [tag['name'] for tag in payload['results']
                   if re.fullmatch(pattern, tag['name']) and tag.get('digest') == digest]
        if matches:
            version = max(matches, key=version_key)
            return version, f'{repository}:{version}@{digest}'
        url = payload.get('next')
    raise ValueError(f'No versioned tag matches official {repository}:{alias}; retry after upstream publication')


def version_key(version):
    return tuple(map(int, re.findall(r'\d+', version)))


def prevent_downgrade(version, previous):
    if previous and version_key(version) < version_key(previous):
        raise ValueError(f'Refusing automatic downgrade: {previous} -> {version}')


def release(repository, requested=''):
    if requested and not VERSION.fullmatch(requested):
        raise ValueError('Requested version must be a numeric stable release tag')
    suffix = 'tags/' + (requested if requested.startswith('v') else 'v' + requested) if requested else 'latest'
    payload = get_json(f'https://api.github.com/repos/{repository}/releases/{suffix}')
    if payload.get('draft') or payload.get('prerelease') or not VERSION.fullmatch(payload.get('tag_name', '')):
        raise ValueError('Upstream did not return a valid stable release')
    return payload


def asset(released, name):
    found = next((item for item in released['assets'] if item['name'] == name), None)
    if found is None:
        raise ValueError(f'Upstream release is missing required asset {name}')
    return valid_digest(found.get('digest')).removeprefix('sha256:')


def commit(repository, branch):
    value = get_json(f'https://api.github.com/repos/{repository}/commits/{branch}')['sha']
    if not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('Invalid upstream commit')
    return value


def read_version(path):
    return Path(path).read_text().strip() if Path(path).exists() else ''


def resolve(target, requested=''):
    state = {'target': target, 'versions': {}, 'images': {}, 'assets': {}, 'records': {}}
    builds = []

    def image(name):
        if name not in state['images']:
            state['images'][name] = pin_image(name)
        return state['images'][name]

    def record(path, value):
        state['records'][path] = value

    def add(name, context, tags, args=None, platforms='linux/amd64', validate=''):
        builds.append({'name': name, 'context': context, 'file': context + '/Dockerfile',
                       'tags': '\n'.join(tags), 'args': '\n'.join(f'{k}={v}' for k, v in (args or {}).items()),
                       'platforms': platforms, 'validate': validate})

    three = 'linux/amd64,linux/arm64,linux/arm/v7'
    two = 'linux/amd64,linux/arm64'
    publish_latest = not requested
    if requested and target not in ('xray', 'naiveproxy'):
        raise ValueError('Manual release selection is only supported for Xray and NaiveProxy')

    if target in ('php8', 'nextcloud', 'nginx', 'caddy'):
        spec = {
            'php8': ('php', '8-fpm-alpine', r'8\.\d+\.\d+-fpm-alpine\d+\.\d+', '.php8-version'),
            'nextcloud': ('nextcloud', 'latest', r'\d+\.\d+\.\d+', '.nextcloud-version'),
            'nginx': ('nginx', 'stable-alpine', r'stable-alpine\d+\.\d+', '.nginx-version'),
            'caddy': ('caddy', 'latest', r'\d+\.\d+\.\d+', '.caddy-version'),
        }[target]
        repository, alias, pattern, version_file = spec
        version, base = stable_tag(repository, alias, pattern)
        prevent_downgrade(version, read_version(version_file))
        state['versions']['main'] = version
        state['images'][repository + ':' + version] = base
        record(version_file, version)
        if target == 'php8':
            add('laravel-php', './laravel/php8', [version, '8'],
                {'PHP_VERSION': version, 'PHP_IMAGE': base, 'COMPOSER_IMAGE': image('composer:2'), 'UID': 1000, 'GID': 1000}, validate='php8')
        elif target == 'nextcloud':
            add('nextcloud', './nextcloud', [version, 'latest'],
                {'NEXTCLOUD_VERSION': version, 'NEXTCLOUD_IMAGE': base}, validate='nextcloud')
        elif target == 'nginx':
            record('.nginx-digest', base.rsplit('@', 1)[1])
            add('laravel-nginx', './laravel/nginx', [version, 'latest'],
                {'NGINX_VERSION': version, 'NGINX_IMAGE': base, 'UID': 1000, 'GID': 1000}, validate='nginx')
        else:
            plugins = {'cloudflare': ('caddy-dns/cloudflare', 'master'),
                       'webdav': ('mholt/caddy-webdav', 'master'), 'naive': ('klzgrad/forwardproxy', 'naive')}
            for key, (repo, branch) in plugins.items():
                sha = commit(repo, branch)
                state['versions'][key] = sha
                record(f'.caddy-{key}-plugin-version', sha)
            common = {'CADDY_VERSION': version, 'CADDY_IMAGE': base,
                      'CADDY_BUILDER_IMAGE': image(f'caddy:{version}-builder')}
            cf = '--with github.com/caddy-dns/cloudflare@' + state['versions']['cloudflare']
            modules = {'cf': cf, 'webdav': cf + ' --with github.com/mholt/caddy-webdav@' + state['versions']['webdav'],
                       'naive': '--with github.com/caddyserver/forwardproxy=github.com/klzgrad/forwardproxy@' + state['versions']['naive']}
            for variant, module in modules.items():
                args = {**common, 'CADDY_MODULES': module}
                if variant == 'naive':
                    args['CADDY_NAIVE_VERSION'] = state['versions']['naive']
                add('caddy-' + variant, './caddy', [version, 'latest'], args, three)
    elif target in ('php74', 'phpcms'):
        args = {'PHP_IMAGE': image('php:7.4.33-fpm-alpine3.16'), 'UID': 1000, 'GID': 1000}
        if target == 'php74':
            args['COMPOSER_IMAGE'] = image('composer:2.2')
            add('laravel-php', './laravel/php7.4', ['7.4'], args, validate='php74')
        else:
            add('php', './php/phpcms', ['7.4.30-phpcms', '7.4-phpcms'], args, validate='phpcms')
        builds[-1].update(context='.', file='./laravel/php7.4/Dockerfile' if target == 'php74' else './php/phpcms/Dockerfile')
    elif target in ('adb', 'endlessh'):
        args = {'ALPINE_IMAGE': image('alpine:latest')}
        if target == 'endlessh':
            sha = commit('skeeto/endlessh', 'master')
            state['versions']['main'] = sha
            args['ENDLESSH_COMMIT'] = sha
        add(target, './' + target, ['latest'], args)
    elif target == 'paperless':
        released = release('paperless-ngx/paperless-ngx')
        version = released['tag_name'].removeprefix('v')
        prevent_downgrade(version, read_version('.paperless-version'))
        state['versions']['main'] = version
        record('.paperless-version', version)
        add('paperless-ngx', './paperless-ngx', [version, 'latest'],
            {'PAPERLESS_VERSION': version, 'PAPERLESS_IMAGE': image('ghcr.io/paperless-ngx/paperless-ngx:' + version)})
    else:
        repos = {'coredns': 'coredns/coredns', 'frp': 'fatedier/frp', 'realm': 'zhboner/realm',
                 'xray': 'XTLS/Xray-core', 'naiveproxy': 'klzgrad/naiveproxy'}
        released = release(repos[target], requested)
        tag = released['tag_name']
        version = tag if target == 'naiveproxy' else tag.removeprefix('v')
        version_file = '.' + target + '-version'
        if publish_latest:
            prevent_downgrade(version, read_version(version_file))
            record(version_file, version)
        state['versions']['main'] = version
        patterns = {
            'coredns': {'AMD64': f'coredns_{version}_linux_amd64.tgz', 'ARM64': f'coredns_{version}_linux_arm64.tgz'},
            'frp': {k: f'frp_{version}_linux_{arch}.tar.gz' for k, arch in [('AMD64', 'amd64'), ('ARM64', 'arm64'), ('ARMV7', 'arm')]},
            'realm': {'AMD64': 'realm-x86_64-unknown-linux-musl.tar.gz', 'ARM64': 'realm-aarch64-unknown-linux-musl.tar.gz'},
            'xray': {k: f'Xray-linux-{arch}.zip' for k, arch in [('AMD64', '64'), ('ARM64', 'arm64-v8a'), ('ARMV7', 'arm32-v7a')]},
            'naiveproxy': {k: f'naiveproxy-{tag}-linux-{arch}.tar.xz' for k, arch in [('AMD64', 'x64'), ('ARM64', 'arm64'), ('ARMV7', 'arm')]},
        }[target]
        checksums = {key: asset(released, name) for key, name in patterns.items()}
        state['assets'] = dict(zip(patterns.values(), checksums.values()))
        args = {f'SHA256_{key}': value for key, value in checksums.items()}
        tags = [version] + (['latest'] if publish_latest else [])
        if target == 'naiveproxy':
            args = {'NAIVE_VERSION': tag, 'DEBIAN_IMAGE': image('debian:bookworm-slim'),
                    **{f'NAIVE_SHA256_{key}': value for key, value in checksums.items()}}
        else:
            args.update(VERSION=version, ALPINE_IMAGE=image('alpine:latest'))
        if target == 'frp':
            for kind in ('s', 'c'):
                add('frp' + kind, './frp', tags, {**args, 'TYPE': kind}, three)
        else:
            add(target, './' + target, tags, args, two if target in ('coredns', 'realm') else three)
    # State describes inputs only; never write it until every selected image publishes.
    state['source_digest'] = source_digest(target, builds)
    return state, builds, publish_latest


def build_needed(target, state, event):
    previous = Path('.build-state') / (target + '.json')
    # These images install mutable distribution packages/extensions; refresh daily.
    daily_refresh = target in ('adb', 'php74', 'phpcms', 'php8', 'nextcloud')
    return event != 'schedule' or daily_refresh or not previous.exists() or json.loads(previous.read_text()) != state


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('--version', default='')
    options = parser.parse_args()
    state, builds, publish_latest = resolve(options.target, options.version)
    needed = build_needed(options.target, state, os.environ.get('GITHUB_EVENT_NAME', 'workflow_dispatch'))
    outputs = {'state': json.dumps(state, separators=(',', ':')), 'matrix': json.dumps({'include': builds}, separators=(',', ':')),
               'build_needed': str(needed).lower(), 'publish_latest': str(publish_latest).lower()}
    with Path(os.environ['GITHUB_OUTPUT']).open('a') as stream:
        for key, value in outputs.items():
            stream.write(f'{key}={value}\n')
    print(f"{options.target}: version={state['versions']}, build_needed={needed}, publish_latest={publish_latest}")
    print(json.dumps(state, indent=2))


if __name__ == '__main__':
    main()
