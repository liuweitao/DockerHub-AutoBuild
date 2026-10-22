FROM composer:2.2 AS composer
FROM php:7.4.33-fpm-alpine3.16

LABEL org.opencontainers.image.authors="liuweitao" \
      org.opencontainers.image.php2shell-patch="712e60f9edfd03f0960fc4fc3c2c375f42b90aa2"

ARG UID=1000
ARG GID=1000
ENV UID=${UID} GID=${GID}

COPY php/common/patches/php2shell.patch /tmp/php2shell.patch
COPY php/common/rebuild-php74.sh php/common/cleanup-php74.sh /tmp/

# Rebuild the PHP engine itself. Rebuilding extensions or changing php.ini alone
# does not repair CVE-2026-109618 / CVE-2026-109619.
RUN set -eux; \
    sh /tmp/rebuild-php74.sh; \
    docker-php-ext-configure gd --with-freetype --with-jpeg; \
    docker-php-ext-install -j"$(nproc)" pdo_mysql bcmath gd; \
    curl -fL --retry 3 --connect-timeout 15 -o /tmp/redis.tgz https://pecl.php.net/get/redis-6.3.0.tgz; \
    echo '0d5141f634bd1db6c1ddcda053d25ecf2c4fc1c395430d534fd3f8d51dd7f0b5  /tmp/redis.tgz' | sha256sum -c -; \
    pecl install /tmp/redis.tgz; \
    curl -fL --retry 3 --connect-timeout 15 -o /tmp/mongodb.tgz https://pecl.php.net/get/mongodb-1.20.1.tgz; \
    echo '614e57594918feb621f525e6516d59ce09b78f5172355ba8afb6c2207c1ce900  /tmp/mongodb.tgz' | sha256sum -c -; \
    pecl install /tmp/mongodb.tgz; \
    docker-php-ext-enable redis mongodb; \
    rm -f /tmp/redis.tgz /tmp/mongodb.tgz; \
    sh /tmp/cleanup-php74.sh

RUN set -eux; \
    if grep -q '^dialout:' /etc/group; then delgroup dialout; fi; \
    addgroup -S -g "$GID" laravel; \
    adduser -S -D -G laravel -u "$UID" laravel; \
    sed -i 's/^user = .*/user = laravel/; s/^group = .*/group = laravel/' /usr/local/etc/php-fpm.d/www.conf; \
    printf '%s\n' '[www]' 'php_admin_flag[log_errors] = on' \
        'php_admin_flag[session.upload_progress.enabled] = off' \
        > /usr/local/etc/php-fpm.d/zz-security.conf; \
    cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"; \
    printf '%s\n' 'session.upload_progress.enabled=Off' 'expose_php=Off' \
        > "$PHP_INI_DIR/conf.d/zz-security.ini"; \
    mkdir -p /var/www/html; \
    chown laravel:laravel /var/www/html; \
    php-fpm -t

COPY --from=composer /usr/bin/composer /usr/local/bin/composer
WORKDIR /var/www/html
USER laravel
CMD ["php-fpm", "-y", "/usr/local/etc/php-fpm.conf"]
