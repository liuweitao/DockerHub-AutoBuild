#!/bin/sh
set -eu

# Keep the compiled core on the same version as the runtime image.
case "$CADDY_VERSION" in
    [0-9]*) CADDY_VERSION="v$CADDY_VERSION" ;;
esac

if [ -z "${CADDY_NAIVE_VERSION:-}" ]; then
    exec xcaddy build "$CADDY_VERSION" "$@"
fi

# Naive's forwardproxy requires patches to Caddy itself, not just --with.
# Fetch the patches from the exact same commit as the plugin in CADDY_MODULES.
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT
git init "$build_dir/forwardproxy"
git -C "$build_dir/forwardproxy" fetch --depth=1 \
    https://github.com/klzgrad/forwardproxy.git "$CADDY_NAIVE_VERSION"
git -C "$build_dir/forwardproxy" -c core.autocrlf=false checkout --detach FETCH_HEAD
git -c core.autocrlf=false clone --depth=1 --branch "$CADDY_VERSION" \
    https://github.com/caddyserver/caddy.git "$build_dir/caddy"

# Match https://github.com/klzgrad/forwardproxy/blob/naive/.github/workflows/build.yml.
# Fail if a future core/plugin pair cannot apply these patches cleanly.
git -C "$build_dir/caddy" apply \
    "$build_dir/forwardproxy/caddy-sing-quic-bbrv1.patch" \
    "$build_dir/forwardproxy/caddy-read-idle-timeout.patch"

xcaddy build "$CADDY_VERSION" \
    --replace "github.com/caddyserver/caddy/v2=$build_dir/caddy" "$@"
