#!/bin/sh
set -eux
run_deps="$(scanelf --needed --nobanner --format '%n#p' --recursive /usr/local \
    | tr ',' '\n' | sort -u \
    | awk 'system("[ -e /usr/local/lib/" $1 " ]") == 0 { next } { print "so:" $1 }')"
apk add --no-cache --virtual .php-rundeps $run_deps
apk del --no-network .build-deps
docker-php-source delete
rm -rf /tmp/pear /tmp/php2shell.patch
php -v
rm -f /tmp/rebuild-php74.sh /tmp/cleanup-php74.sh
