ARG ALPINE_IMAGE=alpine:latest
FROM ${ALPINE_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

ARG VERSION
ARG TARGETARCH
ARG SHA256_AMD64
ARG SHA256_ARM64
ARG SHA256_ARMV7

WORKDIR /xray

RUN apk add --no-cache curl && \
    if [ "$TARGETARCH" = "arm64" ]; then \
        ARCH="arm64-v8a"; \
    elif [ "$TARGETARCH" = "arm" ]; then \
        ARCH="arm32-v7a"; \
    else \
        ARCH="64"; \
    fi && \
    curl -fL --retry 3 --connect-timeout 15 https://github.com/XTLS/Xray-core/releases/download/v${VERSION}/Xray-linux-${ARCH}.zip -o /tmp/upstream-asset && \
    case "$TARGETARCH" in amd64) EXPECTED="$SHA256_AMD64" ;; arm64) EXPECTED="$SHA256_ARM64" ;; arm) EXPECTED="$SHA256_ARMV7" ;; *) exit 1 ;; esac && \
    if [ -n "$EXPECTED" ]; then echo "$EXPECTED  /tmp/upstream-asset" | sha256sum -c -; fi && \
    unzip /tmp/upstream-asset && \
    rm /tmp/upstream-asset && \
    mv xray /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    mkdir -p /usr/local/share/xray && \
    mv geoip.dat geosite.dat /usr/local/share/xray/ && \
    mkdir /etc/xray && \
    rm -rf /xray/* && \
    apk del curl

ENTRYPOINT ["/usr/local/bin/xray", "-config", "/etc/xray/config.json"] 