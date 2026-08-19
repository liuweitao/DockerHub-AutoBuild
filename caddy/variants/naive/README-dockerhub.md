# Caddy-Naïve Docker 镜像

这是一个包含 NaïveProxy 服务端所需 `forward_proxy` 模块的 Caddy 镜像。此镜像不包含 Cloudflare DNS 或 WebDAV 模块。

## 快速开始

使用前必须修改示例 Caddyfile 中的域名和 ACME 邮箱，并设置高强度用户名与密码：

```bash
docker run -d --network host \
  -v ./Caddyfile:/etc/caddy/Caddyfile:ro \
  -v ./data:/data \
  -v ./config:/config \
  -v ./site:/srv:ro \
  -e NAIVE_USERNAME=change-me \
  -e NAIVE_PASSWORD=change-me \
  liuweitao/caddy-naive:latest
```

## Docker Compose

```yaml
services:
  caddy:
    image: liuweitao/caddy-naive:latest
    network_mode: host
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./data:/data
      - ./config:/config
      - ./site:/srv:ro
    environment:
      - NAIVE_USERNAME=change-me
      - NAIVE_PASSWORD=change-me
    restart: unless-stopped
```

## 安全提示

- 不要保留示例用户名或密码，否则代理可能被第三方滥用。
- 上游将 `forward_proxy` 标记为实验性功能，并提示可能出现破坏性变更。
- 配置和安全说明请参考 [NaïveProxy 服务端文档](https://github.com/klzgrad/naiveproxy#server-setup)。

## 源码

此镜像是 [DockerHub-AutoBuild](https://github.com/liuweitao/DockerHub-AutoBuild/) 项目的一部分。
