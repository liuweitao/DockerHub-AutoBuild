FROM php:7.4-fpm-alpine

ARG PHP_VERSION
ARG UID
ARG GID

ENV UID=${UID}
ENV GID=${GID}

RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    openssl-dev \
    freetype-dev \
    libpng-dev \
    libjpeg-turbo-dev \
 && apk add --no-cache \
    openssl \
    freetype \
    libpng \
    libjpeg-turbo \
 && docker-php-ext-configure gd --with-freetype=/usr/include/ --with-jpeg=/usr/include/ \
 && docker-php-ext-install -j$(nproc) pdo pdo_mysql bcmath gd \
 && pecl install redis mongodb \
 && docker-php-ext-enable redis mongodb \
 && apk del .build-deps \
 && rm -rf /var/cache/apk/*

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
