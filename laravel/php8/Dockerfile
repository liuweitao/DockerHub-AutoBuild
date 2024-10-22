ARG PHP_VERSION
ARG UID=1000
ARG GID=1000

FROM php:${PHP_VERSION}

LABEL maintainer="liuweitao"

ENV UID=${UID}
ENV GID=${GID}

RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    && apk add --no-cache \
        imap-dev \
        openssl-dev \
    && docker-php-ext-configure imap --with-imap --with-imap-ssl \
    && docker-php-ext-install pdo pdo_mysql imap \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apk del .build-deps

RUN delgroup dialout \
    && addgroup -g ${GID} --system laravel \
    && adduser -G laravel --system -D -s /bin/sh -u ${UID} laravel \
    && sed -i "s/user = www-data/user = laravel/g" /usr/local/etc/php-fpm.d/www.conf \
    && sed -i "s/group = www-data/group = laravel/g" /usr/local/etc/php-fpm.d/www.conf \
    && echo "php_admin_flag[log_errors] = on" >> /usr/local/etc/php-fpm.d/www.conf

RUN mkdir -p /var/www/html
WORKDIR /var/www/html

COPY --from=composer:latest /usr/bin/composer /usr/local/bin/composer

USER laravel

CMD ["php-fpm", "-y", "/usr/local/etc/php-fpm.conf", "-R"]
