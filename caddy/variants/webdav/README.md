# Caddy-WebDAV

这是一个包含 Cloudflare DNS 插件和 WebDAV 模块的 Caddy 服务器 Docker 镜像。为兼容现有用户，`liuweitao/caddy-webdav` 会继续保留这两个模块。

只使用 WebDAV 时，无需设置 Cloudflare API token，也不要在 Caddyfile 中配置 `dns cloudflare`。

## 使用方法

1. 复制 `compose.yaml` 和 `Caddyfile` 到你的项目目录中。
2. 在项目目录中创建 `data`、`config` 和 `webdav_data` 文件夹。
3. 修改 `Caddyfile` 以满足你的需求，特别是 WebDAV 部分的配置。
4. 如果使用 Cloudflare DNS，在 `compose.yaml` 中设置你的 Cloudflare API token。
5. 运行 `docker compose up -d` 来启动服务。

## 网络模式

这个配置使用 Docker 的 host 网络模式，直接使用主机的网络栈。这意味着 Caddy 将直接绑定到主机的网络接口上，而不是通过 Docker 的网络隔离。

## 目录结构

- `Caddyfile`: Caddy 的主配置文件，包括 WebDAV 设置。
- `data/`: Caddy 的数据目录，包括自动获取的 SSL 证书等。
- `config/`: Caddy 的配置目录。
- `webdav_data/`: WebDAV 服务的数据存储目录。

请确保这些目录存在并且 Docker 用户有适当的权限访问。

## Caddyfile WebDAV 示例

```caddy
yourdomain.com/webdav/* {
  # 可选：使用 `caddy hash-password` 生成密码哈希
  # basic_auth {
  #   username $2a$14$example-hash
  # }

  webdav {
    root /srv/webdav
    prefix /webdav
  }
}
```

更多配置选项，请参考 [Caddy 官方文档](https://caddyserver.com/docs/) 和 [caddy-webdav 插件文档](https://github.com/mholt/caddy-webdav)。
