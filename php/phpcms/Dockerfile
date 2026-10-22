FROM php:7.4.33-fpm-alpine3.16

LABEL org.opencontainers.image.authors="liuweitao" \
      org.opencontainers.image.php2shell-patch="712e60f9edfd03f0960fc4fc3c2c375f42b90aa2"

ARG UID=1000
ARG GID=1000

COPY php/common/patches/php2shell.patch /tmp/php2shell.patch
COPY php/common/rebuild-php74.sh php/common/cleanup-php74.sh /tmp/

RUN set -eux; \
    sh /tmp/rebuild-php74.sh; \
    docker-php-ext-configure gd --with-freetype --with-jpeg; \
    docker-php-ext-install -j"$(nproc)" gd mysqli; \
    sh /tmp/cleanup-php74.sh

COPY php/phpcms/www.conf /usr/local/etc/php-fpm.d/www.conf

RUN set -eux; \
    if grep -q '^dialout:' /etc/group; then delgroup dialout; fi; \
    addgroup -S -g "$GID" www; \
    adduser -S -D -G www -g www -s /bin/sh -u "$UID" www; \
    cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"; \
    printf '%s\n' 'session.upload_progress.enabled=Off' 'expose_php=Off' \
        > "$PHP_INI_DIR/conf.d/zz-security.ini"; \
    mkdir -p /var/www/html; \
    chown www:www /var/www/html; \
    php-fpm -t

WORKDIR /var/www/html
CMD ["php-fpm"]
