ARG PHP_VERSION=8.5.12-fpm-alpine3.24
FROM composer:2 AS composer
FROM php:${PHP_VERSION}

LABEL org.opencontainers.image.authors="liuweitao"
ARG UID=1000
ARG GID=1000
ENV UID=${UID} GID=${GID}

# Fail closed when an overridden base tag still contains vulnerable PHP.
RUN php -r '$minimum = ["8.2" => "8.2.35", "8.3" => "8.3.36", "8.4" => "8.4.27", "8.5" => "8.5.12"]; $branch = PHP_MAJOR_VERSION . "." . PHP_MINOR_VERSION; if (!isset($minimum[$branch]) || version_compare(PHP_VERSION, $minimum[$branch], "<")) { fwrite(STDERR, "Unpatched or unreviewed PHP base: " . PHP_VERSION . PHP_EOL); exit(1); }'

RUN set -eux; \
    apk upgrade --no-cache; \
    apk add --no-cache --virtual .build-deps \
        $PHPIZE_DEPS imap-dev openssl-dev krb5-dev; \
    docker-php-ext-install -j"$(nproc)" pdo_mysql; \
    pecl install imap-1.0.3; \
    pecl install redis-6.3.0; \
    docker-php-ext-enable imap redis; \
    run_deps="$(scanelf --needed --nobanner --format '%n#p' --recursive /usr/local/lib/php/extensions \
        | tr ',' '\n' | sort -u \
        | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }')"; \
    apk add --no-cache --virtual .php-rundeps $run_deps; \
    apk del --no-network .build-deps; \
    docker-php-source delete; \
    rm -rf /tmp/pear

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
