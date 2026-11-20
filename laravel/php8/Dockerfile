ARG PHP_VERSION=8.5.12-fpm-alpine3.24
ARG COMPOSER_IMAGE=composer:2
ARG PHP_IMAGE=php:${PHP_VERSION}
FROM ${COMPOSER_IMAGE} AS composer
FROM ${PHP_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"
ARG UID=1000
ARG GID=1000
ENV UID=${UID} GID=${GID}

# Keep known security floors; allow later stable PHP 8 branches, excluding previews.
RUN php -r '$minimum = ["8.2" => "8.2.35", "8.3" => "8.3.36", "8.4" => "8.4.27", "8.5" => "8.5.12"]; $version = PHP_VERSION; $branch = implode(".", array_slice(explode(".", $version), 0, 2)); if (!preg_match("/^8\\.[0-9]+\\.[0-9]+$/D", $version) || version_compare($version, $minimum[$branch] ?? "8.6.0", "<")) { fwrite(STDERR, "Unsupported or unpatched PHP base: " . $version . PHP_EOL); exit(1); }'

# PHP 8.6 no longer ships the PECL installer.
RUN set -eux; \
    apk upgrade --no-cache; \
    apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS imap-dev openssl-dev krb5-dev; \
    curl -fL --retry 3 --connect-timeout 15 -o /tmp/imap.tgz https://pecl.php.net/get/imap-1.0.3.tgz; \
    echo '0c2c0b1f94f299004be996b85a424e3d11ff65ac0a3c980db3213289a4a3faaf  /tmp/imap.tgz' | sha256sum -c -; \
    curl -fL --retry 3 --connect-timeout 15 -o /tmp/redis.tgz https://pecl.php.net/get/redis-6.3.0.tgz; \
    echo '0d5141f634bd1db6c1ddcda053d25ecf2c4fc1c395430d534fd3f8d51dd7f0b5  /tmp/redis.tgz' | sha256sum -c -; \
    docker-php-source extract; \
    mkdir -p /usr/src/php/ext/imap /usr/src/php/ext/redis; \
    tar -xzf /tmp/imap.tgz -C /usr/src/php/ext/imap --strip-components=1 imap-1.0.3; \
    tar -xzf /tmp/redis.tgz -C /usr/src/php/ext/redis --strip-components=1 redis-6.3.0; \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl; \
    docker-php-ext-install -j"$(nproc)" pdo_mysql imap redis; \
    run_deps="$(scanelf --needed --nobanner --format '%n#p' --recursive /usr/local/lib/php/extensions \
        | tr ',' '\n' | sort -u \
        | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }')"; \
    apk add --no-cache --virtual .php-rundeps $run_deps; \
    apk del --no-network .build-deps; \
    docker-php-source delete; \
    rm -f /tmp/imap.tgz /tmp/redis.tgz

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
