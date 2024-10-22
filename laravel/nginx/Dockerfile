ARG NGINX_VERSION=stable-alpine
FROM nginx:${NGINX_VERSION}

ARG UID
ARG GID

ENV UID=${UID}
ENV GID=${GID}

# MacOS staff group's gid is 20, so is the dialout group in alpine linux. We're not using it, let's just remove it.
RUN delgroup dialout

RUN addgroup -g ${GID} --system laravel && \
    adduser -G laravel --system -D -s /bin/sh -u ${UID} laravel && \
    sed -i "s/user  nginx/user laravel/g" /etc/nginx/nginx.conf && \
    mkdir -p /var/www/html

COPY ./default.conf /etc/nginx/conf.d/

USER laravel

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
