ARG NEXTCLOUD_VERSION=35.0.2
ARG NEXTCLOUD_IMAGE=nextcloud:${NEXTCLOUD_VERSION}
FROM ${NEXTCLOUD_IMAGE}

LABEL org.opencontainers.image.authors="liuweitao"

# apt upgrade cannot update the /usr/local PHP supplied by the parent image.
# Refuse to publish until Nextcloud has rebuilt its parent with patched PHP.
# Later stable PHP 8 branches inherit the fixes; previews and other majors require review.
RUN php -r '$minimum = ["8.2" => "8.2.35", "8.3" => "8.3.36", "8.4" => "8.4.27", "8.5" => "8.5.12"]; $version = PHP_VERSION; $branch = implode(".", array_slice(explode(".", $version), 0, 2)); if (!preg_match("/^8\\.[0-9]+\\.[0-9]+$/D", $version) || version_compare($version, $minimum[$branch] ?? "8.6.0", "<")) { fwrite(STDERR, "Unsupported or unpatched PHP base: " . $version . PHP_EOL); exit(1); }'

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends libbz2-dev libbz2-1.0 ffmpeg; \
    docker-php-ext-install -j"$(nproc)" bz2; \
    apt-get purge -y --auto-remove libbz2-dev; \
    docker-php-source delete; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*; \
    printf '%s\n' 'session.upload_progress.enabled=Off' 'expose_php=Off' \
        > "$PHP_INI_DIR/conf.d/zz-security.ini"; \
    php --ri bz2
