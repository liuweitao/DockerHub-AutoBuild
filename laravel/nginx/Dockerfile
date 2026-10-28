ARG NGINX_VERSION=stable-alpine
ARG NGINX_IMAGE=nginx:${NGINX_VERSION}
FROM ${NGINX_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

ARG UID
ARG GID

ENV UID=${UID}
ENV GID=${GID}

RUN delgroup dialout

RUN addgroup -g ${GID} --system laravel && \
    adduser -G laravel --system -D -s /bin/sh -u ${UID} laravel && \
    sed -i "s/user  nginx/user laravel/g" /etc/nginx/nginx.conf && \
    mkdir -p /var/www/html

COPY ./default.conf /etc/nginx/conf.d/


