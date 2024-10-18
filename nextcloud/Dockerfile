ARG NEXTCLOUD_VERSION=30.0.0
FROM nextcloud:${NEXTCLOUD_VERSION}

LABEL maintainer="liuweitao"

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        libbz2-dev \
        ffmpeg && \
    docker-php-ext-install bz2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
