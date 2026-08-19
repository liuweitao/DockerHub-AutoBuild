ARG CADDY_VERSION=latest
FROM caddy:${CADDY_VERSION}-builder AS builder

ARG CADDY_MODULES
RUN xcaddy build ${CADDY_MODULES}

FROM caddy:${CADDY_VERSION}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
