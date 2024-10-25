FROM alpine:latest AS builder

ARG TARGETARCH
ARG TYPE="s"
ARG VERSION

RUN apk add --no-cache curl && \
    mkdir -p /tmp/frp && \
    curl -L https://github.com/fatedier/frp/releases/download/v${VERSION}/frp_${VERSION}_linux_${TARGETARCH}.tar.gz | tar xz -C /tmp/frp --strip-components=1 && \
    mv /tmp/frp/frp${TYPE} /tmp/frp${TYPE} && \
    mv /tmp/frp/frp${TYPE}.toml /tmp/config.toml

FROM alpine:latest

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
