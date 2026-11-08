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

# Keep two context lines so unrelated new imports (Caddy 2.11.9's httpguts)
# don't invalidate the pinned QUIC patch. Changed code must still match.
git -C "$build_dir/caddy" apply -C2 \
    "$build_dir/forwardproxy/caddy-sing-quic-bbrv1.patch"

# Caddy 2.11.9 already includes this API and the corresponding server wiring.
# Older cores still need the pinned upstream backport; patch failures stay fatal.
if ! git -C "$build_dir/caddy" grep -q '^func IdleTimeoutsFromContext(' \
    -- modules/caddyhttp/idletimeout.go; then
    git -C "$build_dir/caddy" apply \
        "$build_dir/forwardproxy/caddy-read-idle-timeout.patch"
fi

xcaddy build "$CADDY_VERSION" \
    --replace "github.com/caddyserver/caddy/v2=$build_dir/caddy" "$@"
