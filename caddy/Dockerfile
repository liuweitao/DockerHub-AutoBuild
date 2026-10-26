ARG CADDY_VERSION=latest
FROM caddy:${CADDY_VERSION}-builder AS builder

ARG CADDY_VERSION
ARG CADDY_MODULES
ARG CADDY_NAIVE_VERSION
COPY build-caddy.sh /usr/local/bin/build-caddy
RUN sh /usr/local/bin/build-caddy ${CADDY_MODULES}

FROM caddy:${CADDY_VERSION}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
