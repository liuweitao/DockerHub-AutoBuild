ARG ALPINE_IMAGE=alpine:latest
FROM ${ALPINE_IMAGE} AS builder

ARG TARGETARCH
ARG SHA256_AMD64
ARG SHA256_ARM64
ARG SHA256_ARMV7
ARG VERSION

RUN apk add --no-cache ca-certificates curl && \
    curl -fSL --retry 3 --connect-timeout 15 https://github.com/coredns/coredns/releases/download/v${VERSION}/coredns_${VERSION}_linux_${TARGETARCH}.tgz -o /tmp/upstream-asset && \
    case "$TARGETARCH" in amd64) EXPECTED="$SHA256_AMD64" ;; arm64) EXPECTED="$SHA256_ARM64" ;; arm) EXPECTED="$SHA256_ARMV7" ;; *) exit 1 ;; esac && \
    if [ -n "$EXPECTED" ]; then echo "$EXPECTED  /tmp/upstream-asset" | sha256sum -c -; fi && \
    tar xzf /tmp/upstream-asset -C /tmp && \
    mv /tmp/coredns /usr/local/bin/coredns

FROM ${ALPINE_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

COPY --from=builder /usr/local/bin/coredns /usr/local/bin/coredns
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

RUN addgroup -S coredns && \
    adduser -S coredns -G coredns && \
    mkdir -p /etc/coredns && \
    chown -R coredns:coredns /etc/coredns

USER coredns

EXPOSE 53 53/udp

ENTRYPOINT ["/usr/local/bin/coredns", "-conf", "/etc/coredns/Corefile"]
