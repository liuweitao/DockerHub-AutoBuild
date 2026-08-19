# Caddy-WebDAV Docker 镜像

这是一个包含 Cloudflare DNS 插件和 WebDAV 模块的 Caddy 服务器 Docker 镜像。为兼容已有部署，`latest` 会继续包含这两个模块。

只使用 WebDAV 时，无需设置 Cloudflare API token，也不要在 Caddyfile 中配置 `dns cloudflare`。

## 快速开始

```bash
docker run -d --network host \
  -v ./Caddyfile:/etc/caddy/Caddyfile \
  -v ./data:/data \
  -v ./config:/config \
  -v ./webdav_data:/srv/webdav \
  -e CLOUDFLARE_API_TOKEN=your_cloudflare_api_token \
  liuweitao/caddy-webdav:latest
```

## Docker Compose

```yaml
services:
  caddy:
    image: liuweitao/caddy-webdav:latest
    network_mode: host
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./data:/data
      - ./config:/config
      - ./webdav_data:/srv/webdav
    environment:
      - CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
    restart: unless-stopped
```

如果不使用 Cloudflare DNS，可以删除 `environment` 配置。

## 注意事项

- 使用 WebDAV 前应启用 HTTPS 和身份验证。
- 定期备份 Caddy 数据、配置和 WebDAV 数据。
- 确保 `./webdav_data` 目录存在，并且容器用户有适当的访问权限。

## 源码

此镜像是 [DockerHub-AutoBuild](https://github.com/liuweitao/DockerHub-AutoBuild/) 项目的一部分。
