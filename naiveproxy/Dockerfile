# syntax=docker/dockerfile:1

FROM debian:bookworm-slim AS downloader

ARG TARGETARCH
ARG TARGETVARIANT
ARG NAIVE_VERSION
ARG NAIVE_SHA256_AMD64
ARG NAIVE_SHA256_ARM64
ARG NAIVE_SHA256_ARMV7

RUN set -eux; \
    apt-get update; \
    apt-get install --yes --no-install-recommends ca-certificates curl xz-utils; \
    rm -rf /var/lib/apt/lists/*; \
    case "${TARGETARCH}/${TARGETVARIANT}" in \
      amd64/*) NAIVE_ARCH='x64'; EXPECTED_SHA256="${NAIVE_SHA256_AMD64}" ;; \
      arm64/*) NAIVE_ARCH='arm64'; EXPECTED_SHA256="${NAIVE_SHA256_ARM64}" ;; \
      arm/v7) NAIVE_ARCH='arm'; EXPECTED_SHA256="${NAIVE_SHA256_ARMV7}" ;; \
      *) echo "Unsupported platform: ${TARGETARCH}/${TARGETVARIANT}" >&2; exit 1 ;; \
    esac; \
    test -n "${NAIVE_VERSION}"; \
    test -n "${EXPECTED_SHA256}"; \
    ASSET="naiveproxy-${NAIVE_VERSION}-linux-${NAIVE_ARCH}"; \
    curl --fail --location --show-error \
      --retry 3 --retry-delay 2 --retry-all-errors \
      --output /tmp/naiveproxy.tar.xz \
      "https://github.com/klzgrad/naiveproxy/releases/download/${NAIVE_VERSION}/${ASSET}.tar.xz"; \
    echo "${EXPECTED_SHA256}  /tmp/naiveproxy.tar.xz" | sha256sum --check --strict; \
    mkdir /tmp/naiveproxy; \
    tar --extract --xz --file /tmp/naiveproxy.tar.xz \
      --directory /tmp/naiveproxy --strip-components 1; \
    test -x /tmp/naiveproxy/naive

FROM debian:bookworm-slim

ARG NAIVE_VERSION

LABEL org.opencontainers.image.authors="liuweitao" \
      org.opencontainers.image.title="NaiveProxy client" \
      org.opencontainers.image.source="https://github.com/liuweitao/DockerHub-AutoBuild" \
      org.opencontainers.image.version="${NAIVE_VERSION}"

RUN set -eux; \
    apt-get update; \
    apt-get install --yes --no-install-recommends ca-certificates; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd --system naive; \
    useradd --system --gid naive --home-dir /nonexistent --shell /usr/sbin/nologin naive; \
    install --directory --owner naive --group naive /etc/naive

COPY --from=downloader /tmp/naiveproxy/naive /usr/local/bin/naive
COPY --from=downloader /tmp/naiveproxy/LICENSE /usr/share/doc/naiveproxy/LICENSE

USER naive

RUN /usr/local/bin/naive --version

EXPOSE 1080

ENTRYPOINT ["/usr/local/bin/naive"]
CMD ["/etc/naive/config.json"]
