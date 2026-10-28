ARG CADDY_VERSION=latest
ARG CADDY_BUILDER_IMAGE=caddy:${CADDY_VERSION}-builder
ARG CADDY_IMAGE=caddy:${CADDY_VERSION}
FROM --platform=$BUILDPLATFORM ${CADDY_BUILDER_IMAGE} AS builder

ARG CADDY_VERSION
ARG CADDY_MODULES
ARG CADDY_NAIVE_VERSION
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT
COPY build-caddy.sh /usr/local/bin/build-caddy
RUN set -eu; \
    export GOOS="$TARGETOS" GOARCH="$TARGETARCH" CGO_ENABLED=0; \
    if [ "$TARGETARCH" = arm ]; then export GOARM="${TARGETVARIANT#v}"; fi; \
    sh /usr/local/bin/build-caddy ${CADDY_MODULES}

FROM ${CADDY_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
