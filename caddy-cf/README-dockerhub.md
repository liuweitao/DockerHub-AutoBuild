# Caddy-CF Docker 镜像

这是一个包含 Cloudflare DNS 插件的 Caddy 服务器 Docker 镜像，专为没有 80 和 443 端口可用的场景设计。

## 快速开始

使用以下命令运行 Caddy-CF 镜像:

```bash
docker run -d --network host \
  -v ./Caddyfile:/etc/caddy/Caddyfile \
  -v ./data:/data \
  -v ./config:/config \
  -e CLOUDFLARE_API_TOKEN=your_cloudflare_api_token \
  liuweitao/caddy-cf:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例:

```yaml
services:
  caddy:
    image: liuweitao/caddy-cf:latest
    network_mode: host
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./data:/data
      - ./config:/config
    environment:
      - CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
    restart: unless-stopped
```

## 配置说明

- 使用 host 网络模式，直接使用主机的网络栈。
- Caddyfile、数据目录和配置目录都被挂载到容器中。
- 通过环境变量设置 Cloudflare API 令牌。

## 注意事项

- 确保在生产环境中使用有效的 Cloudflare API 令牌。
- 考虑使用 HTTPS 来加强安全性。
- 定期备份你的数据和配置。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
