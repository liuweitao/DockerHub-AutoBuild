ARG CADDY_VERSION=latest
ARG CADDY_BUILDER_IMAGE=caddy:${CADDY_VERSION}-builder
ARG CADDY_IMAGE=caddy:${CADDY_VERSION}
FROM ${CADDY_BUILDER_IMAGE} AS builder

ARG CADDY_VERSION
ARG CADDY_MODULES
ARG CADDY_NAIVE_VERSION
COPY build-caddy.sh /usr/local/bin/build-caddy
RUN sh /usr/local/bin/build-caddy ${CADDY_MODULES}

FROM ${CADDY_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
