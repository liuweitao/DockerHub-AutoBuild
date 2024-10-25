ARG CADDY_VERSION=latest
FROM caddy:${CADDY_VERSION}-builder AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare

FROM caddy:${CADDY_VERSION}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
