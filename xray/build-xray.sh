#!/bin/sh
set -eu
: "${XRAY_COMMIT:?XRAY_COMMIT must identify the selected release source}"
export GOOS="$TARGETOS" GOARCH="$TARGETARCH" CGO_ENABLED=0
unset GOARM
case "$TARGETOS/$TARGETARCH/$TARGETVARIANT" in
    linux/amd64/*|linux/arm64/*) ;;
    linux/arm/v7) export GOARM=7 ;;
    *) echo "Unsupported Xray platform: $TARGETOS/$TARGETARCH/$TARGETVARIANT" >&2; exit 1 ;;
esac
output="${1:-/out/xray}"
mkdir -p "$(dirname "$output")"
go build -mod=readonly -trimpath -buildvcs=false -gcflags=all=-l=4 \
    -ldflags="-s -w -buildid= -X github.com/xtls/xray-core/core.build=${XRAY_COMMIT}" \
    -o "$output" ./main
