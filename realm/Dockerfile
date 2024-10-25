FROM alpine:latest

LABEL org.opencontainers.image.authors="liuweitao"

ARG VERSION
ARG TARGETARCH

WORKDIR /realm

RUN apk add --no-cache curl && \
    if [ "$TARGETARCH" = "arm64" ]; then \
        ARCH="aarch64"; \
    else \
        ARCH="x86_64"; \
    fi && \
    curl -L https://github.com/zhboner/realm/releases/download/v${VERSION}/realm-${ARCH}-unknown-linux-musl.tar.gz | tar xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/realm && \
    mkdir /etc/realm && \
    apk del curl

ENTRYPOINT ["/usr/local/bin/realm", "-c", "/etc/realm/config.toml"]
