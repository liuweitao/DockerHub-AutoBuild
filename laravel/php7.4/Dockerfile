FROM composer:2.2 AS composer
FROM php:7.4.33-fpm-alpine3.16

LABEL org.opencontainers.image.authors="liuweitao" \
      org.opencontainers.image.php2shell-patch="712e60f9edfd03f0960fc4fc3c2c375f42b90aa2"

ARG UID=1000
ARG GID=1000
ENV UID=${UID} GID=${GID}

COPY patches/php2shell.patch /tmp/php2shell.patch

# Rebuild the PHP engine itself. Rebuilding extensions or changing php.ini alone
# does not repair CVE-2026-109618 / CVE-2026-109619.
RUN set -eux; \
    apk upgrade --no-cache; \
    apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS argon2-dev coreutils curl-dev gnu-libiconv-dev \
        libsodium-dev libxml2-dev linux-headers oniguruma-dev openssl-dev \
        readline-dev sqlite-dev zlib-dev freetype-dev libpng-dev \
        libjpeg-turbo-dev patch; \
    echo "5fe57ca6ee96d59b36c6e0ca842843c50884f177bef1e85234cf669b577f5e48  /tmp/php2shell.patch" | sha256sum -c -; \
    docker-php-source extract; \
    cd /usr/src/php; \
    patch --batch --fuzz=0 -p1 < /tmp/php2shell.patch; \
    rm -f /usr/include/iconv.h; \
    ln -sf /usr/include/gnu-libiconv/*.h /usr/include/; \
    export CFLAGS="$PHP_CFLAGS" CPPFLAGS="$PHP_CPPFLAGS" LDFLAGS="$PHP_LDFLAGS"; \
    configure_options="$(php-config --configure-options)"; \
    eval "./configure $configure_options"; \
    make -j"$(nproc)"; \
    make install; \
    make clean; \
    docker-php-ext-configure gd --with-freetype --with-jpeg; \
    docker-php-ext-install -j"$(nproc)" pdo_mysql bcmath gd; \
    pecl install redis-6.3.0; \
    pecl install mongodb-1.20.1; \
    docker-php-ext-enable redis mongodb; \
    run_deps="$(scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
        | tr ',' '\n' | sort -u \
        | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }')"; \
    apk add --no-cache --virtual .php-rundeps $run_deps; \
    apk del --no-network .build-deps; \
    docker-php-source delete; \
    rm -rf /tmp/pear /tmp/php2shell.patch; \
    php -v

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
