FROM alpine:latest

RUN apk add --no-cache \
    android-tools \
    curl \
    wget \
    usbutils

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 