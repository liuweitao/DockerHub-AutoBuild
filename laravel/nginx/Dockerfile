ARG NGINX_VERSION=stable-alpine
FROM nginx:${NGINX_VERSION}

LABEL maintainer="liuweitao"

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


