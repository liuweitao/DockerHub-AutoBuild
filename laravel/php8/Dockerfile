ARG PHP_VERSION

FROM php:${PHP_VERSION}

ARG UID=1000
ARG GID=1000

LABEL org.opencontainers.image.authors="liuweitao"

ENV UID=${UID}
ENV GID=${GID}

RUN set -eux; \
    apk add --no-cache \
        $PHPIZE_DEPS \
        imap-dev \
        openssl-dev \
        krb5-dev \
        ; \
    docker-php-ext-install -j"$(nproc)" pdo pdo_mysql; \
    pecl install imap redis; \
    docker-php-ext-enable imap redis; \
    apk del $PHPIZE_DEPS krb5-dev

RUN delgroup dialout \
    && addgroup -S -g ${GID} laravel \
    && adduser -S -G laravel -u ${UID} laravel \
    && sed -i "s/user = www-data/user = laravel/g" /usr/local/etc/php-fpm.d/www.conf \
    && sed -i "s/group = www-data/group = laravel/g" /usr/local/etc/php-fpm.d/www.conf \
    && echo "php_admin_flag[log_errors] = on" >> /usr/local/etc/php-fpm.d/www.conf

RUN mkdir -p /var/www/html
WORKDIR /var/www/html

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

USER laravel

CMD ["php-fpm", "-y", "/usr/local/etc/php-fpm.conf", "-R"]
