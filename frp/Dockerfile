ARG ALPINE_IMAGE=alpine:latest
FROM ${ALPINE_IMAGE} AS builder

ARG TARGETARCH
ARG SHA256_AMD64
ARG SHA256_ARM64
ARG SHA256_ARMV7
ARG TYPE="s"
ARG VERSION

RUN apk add --no-cache curl && \
    mkdir -p /tmp/frp && \
    curl -fL --retry 3 --connect-timeout 15 https://github.com/fatedier/frp/releases/download/v${VERSION}/frp_${VERSION}_linux_${TARGETARCH}.tar.gz -o /tmp/upstream-asset && \
    case "$TARGETARCH" in amd64) EXPECTED="$SHA256_AMD64" ;; arm64) EXPECTED="$SHA256_ARM64" ;; arm) EXPECTED="$SHA256_ARMV7" ;; *) exit 1 ;; esac && \
    if [ -n "$EXPECTED" ]; then echo "$EXPECTED  /tmp/upstream-asset" | sha256sum -c -; fi && \
    tar xzf /tmp/upstream-asset -C /tmp/frp --strip-components=1 && \
    mv /tmp/frp/frp${TYPE} /tmp/frp${TYPE} && \
    mv /tmp/frp/frp${TYPE}.toml /tmp/config.toml

FROM ${ALPINE_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

ARG TYPE="s"
ENV FRP_TYPE=${TYPE}

COPY --from=builder /tmp/frp${FRP_TYPE} /usr/local/bin/frp
COPY --from=builder /tmp/config.toml /etc/frp/config.toml

RUN addgroup -S frp && adduser -S frp -G frp && \
    chmod +x /usr/local/bin/frp && \
    chown -R frp:frp /etc/frp

USER frp

ENTRYPOINT ["/usr/local/bin/frp", "-c", "/etc/frp/config.toml"]
