#!/bin/sh
# Official PHP 7.4.33 source backport; shared by Laravel and PHPCMS.
set -eux
php -r 'if (PHP_VERSION !== "7.4.33") { fwrite(STDERR, "Expected PHP 7.4.33 base\n"); exit(1); }'
apk upgrade --no-cache
apk add --no-cache --virtual .build-deps \
    $PHPIZE_DEPS argon2-dev coreutils curl-dev gnu-libiconv-dev \
    libsodium-dev libxml2-dev linux-headers oniguruma-dev openssl-dev \
    readline-dev sqlite-dev zlib-dev freetype-dev libpng-dev \
    libjpeg-turbo-dev patch
echo '5fe57ca6ee96d59b36c6e0ca842843c50884f177bef1e85234cf669b577f5e48  /tmp/php2shell.patch' | sha256sum -c -
docker-php-source extract
cd /usr/src/php
patch --batch --fuzz=0 -p1 < /tmp/php2shell.patch
rm -f /usr/include/iconv.h
ln -sf /usr/include/gnu-libiconv/*.h /usr/include/
export CFLAGS="$PHP_CFLAGS" CPPFLAGS="$PHP_CPPFLAGS" LDFLAGS="$PHP_LDFLAGS"
configure_options="$(php-config --configure-options)"
eval "./configure $configure_options"
make -j"$(nproc)"
make install
make clean
