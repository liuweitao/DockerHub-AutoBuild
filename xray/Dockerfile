ARG GO_IMAGE=golang:1.27-alpine
ARG ALPINE_IMAGE=alpine:latest
# Download inputs and run the compiler on the host CPU, including ARM builds.
FROM --platform=$BUILDPLATFORM ${GO_IMAGE} AS source

RUN apk add --no-cache curl
WORKDIR /src
ARG XRAY_COMMIT
RUN test -n "$XRAY_COMMIT" && \
    curl -fL --retry 5 --retry-all-errors --connect-timeout 15 --max-time 300 \
      "https://codeload.github.com/XTLS/Xray-core/tar.gz/${XRAY_COMMIT}" -o /tmp/source.tar.gz && \
    tar -xzf /tmp/source.tar.gz --strip-components=1 && rm /tmp/source.tar.gz

ARG GEOIP_URL
ARG GEOIP_SHA256
ARG GEOSITE_URL
ARG GEOSITE_SHA256
RUN test -n "$GEOIP_SHA256" && test -n "$GEOSITE_SHA256" && \
    mkdir -p /out/assets && \
    curl -fL --retry 5 --retry-all-errors --connect-timeout 15 --max-time 300 \
      "$GEOIP_URL" -o /out/assets/geoip.dat && \
    echo "$GEOIP_SHA256  /out/assets/geoip.dat" | sha256sum -c - && \
    curl -fL --retry 5 --retry-all-errors --connect-timeout 15 --max-time 300 \
      "$GEOSITE_URL" -o /out/assets/geosite.dat && \
    echo "$GEOSITE_SHA256  /out/assets/geosite.dat" | sha256sum -c -

FROM source AS builder
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT
ENV CGO_ENABLED=0 GOTOOLCHAIN=local
COPY build-xray.sh /usr/local/bin/build-xray
RUN sh /usr/local/bin/build-xray

FROM ${ALPINE_IMAGE}
LABEL org.opencontainers.image.authors="liuweitao"
RUN apk add --no-cache ca-certificates tzdata && mkdir -p /etc/xray
WORKDIR /xray
COPY --from=builder /out/xray /usr/local/bin/xray
COPY --from=source /out/assets/ /usr/local/share/xray/
COPY --from=source /src/LICENSE /usr/share/licenses/xray/LICENSE
ENTRYPOINT ["/usr/local/bin/xray", "-config", "/etc/xray/config.json"]
