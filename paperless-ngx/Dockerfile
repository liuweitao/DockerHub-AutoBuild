ARG PAPERLESS_VERSION=latest
ARG PAPERLESS_IMAGE=ghcr.io/paperless-ngx/paperless-ngx:${PAPERLESS_VERSION}
FROM ${PAPERLESS_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

# 安装中文 OCR 支持
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-tra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*
