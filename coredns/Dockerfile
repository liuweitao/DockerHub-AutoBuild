FROM alpine:latest AS builder

ARG TARGETARCH
ARG VERSION

RUN apk add --no-cache ca-certificates curl && \
    curl -sSL https://github.com/coredns/coredns/releases/download/v${VERSION}/coredns_${VERSION}_linux_${TARGETARCH}.tgz | tar xz -C /tmp && \
    mv /tmp/coredns /usr/local/bin/coredns

FROM alpine:latest

LABEL maintainer="liuweitao"

COPY --from=builder /usr/local/bin/coredns /usr/local/bin/coredns
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

RUN addgroup -S coredns && \
    adduser -S coredns -G coredns && \
    mkdir -p /etc/coredns && \
    chown -R coredns:coredns /etc/coredns

USER coredns

EXPOSE 53 53/udp

ENTRYPOINT ["/usr/local/bin/coredns", "-conf", "/etc/coredns/Corefile"]
