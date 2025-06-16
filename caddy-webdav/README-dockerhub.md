# Caddy-WebDAV Docker 镜像

这是一个包含 Cloudflare DNS 插件和 WebDAV 模块的 Caddy 服务器 Docker 镜像。

## 快速开始

使用以下命令运行 Caddy-WebDAV 镜像:

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

以下是 `compose.yaml` 文件示例:

```yaml
services:
  caddy:
    image: liuweitao/caddy-webdav:latest
    network_mode: host
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./data:/data # Caddy 数据，包括证书
      - ./config:/config # Caddy 配置
      - ./webdav_data:/srv/webdav # WebDAV 数据目录
    environment:
      - CLOUDFLARE_API_TOKEN=your_cloudflare_api_token # 如果使用 Cloudflare 获取 TLS 证书，请保留
    restart: unless-stopped
```

## 配置说明

- 使用 host 网络模式，直接使用主机的网络栈。
- Caddyfile、数据目录、配置目录和 WebDAV 数据目录都被挂载到容器中。
- 通过环境变量设置 Cloudflare API 令牌 (如果需要)。
- WebDAV 服务配置在 `Caddyfile` 中。

## 注意事项

- 确保在生产环境中使用有效的 Cloudflare API 令牌 (如果使用 Cloudflare)。
- 考虑为 WebDAV 启用 HTTPS 和身份验证来加强安全性。
- 定期备份你的数据和配置。
- 确保 `./webdav_data` 目录存在并且 Docker 用户有适当的权限访问。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
