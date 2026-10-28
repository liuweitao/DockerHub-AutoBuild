ARG ALPINE_IMAGE=alpine:latest
FROM ${ALPINE_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

ARG VERSION
ARG TARGETARCH
ARG SHA256_AMD64
ARG SHA256_ARM64
ARG SHA256_ARMV7

WORKDIR /realm

RUN apk add --no-cache curl && \
    if [ "$TARGETARCH" = "arm64" ]; then \
        ARCH="aarch64"; \
    else \
        ARCH="x86_64"; \
    fi && \
    curl -fL --retry 3 --connect-timeout 15 https://github.com/zhboner/realm/releases/download/v${VERSION}/realm-${ARCH}-unknown-linux-musl.tar.gz -o /tmp/upstream-asset && \
    case "$TARGETARCH" in amd64) EXPECTED="$SHA256_AMD64" ;; arm64) EXPECTED="$SHA256_ARM64" ;; arm) EXPECTED="$SHA256_ARMV7" ;; *) exit 1 ;; esac && \
    if [ -n "$EXPECTED" ]; then echo "$EXPECTED  /tmp/upstream-asset" | sha256sum -c -; fi && \
    tar xzf /tmp/upstream-asset -C /usr/local/bin && \
    rm /tmp/upstream-asset && \
    chmod +x /usr/local/bin/realm && \
    mkdir /etc/realm && \
    apk del curl

ENTRYPOINT ["/usr/local/bin/realm", "-c", "/etc/realm/config.toml"]
