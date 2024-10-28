FROM ghcr.io/paperless-ngx/paperless-ngx:latest

LABEL org.opencontainers.image.authors="liuweitao"

# 安装中文 OCR 支持
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-tra \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*
