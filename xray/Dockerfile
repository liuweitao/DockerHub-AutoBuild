FROM alpine:latest

LABEL org.opencontainers.image.authors="liuweitao"

ARG VERSION
ARG TARGETARCH

WORKDIR /xray

RUN apk add --no-cache curl && \
    if [ "$TARGETARCH" = "arm64" ]; then \
        ARCH="arm64-v8a"; \
    elif [ "$TARGETARCH" = "arm" ]; then \
        ARCH="arm32-v7a"; \
    else \
        ARCH="64"; \
    fi && \
    curl -L https://github.com/XTLS/Xray-core/releases/download/v${VERSION}/Xray-linux-${ARCH}.zip -o xray.zip && \
    unzip xray.zip && \
    mv xray /usr/local/bin/ && \
    chmod +x /usr/local/bin/xray && \
    mkdir -p /usr/local/share/xray && \
    mv geoip.dat geosite.dat /usr/local/share/xray/ && \
    mkdir /etc/xray && \
    rm -rf /xray/* && \
    apk del curl

ENTRYPOINT ["/usr/local/bin/xray", "-config", "/etc/xray/config.json"] 