# Caddy-CF

这是一个包含 Cloudflare DNS 插件的 Caddy 服务器 Docker 镜像，专为没有 80 和 443 端口可用的场景设计。

## 使用方法

1. 复制 `compose.yaml` 和 `Caddyfile` 到你的项目目录中。
2. 在项目目录中创建 `data` 和 `config` 文件夹。
3. 修改 `Caddyfile` 以满足你的需求。
4. 在 `compose.yaml` 中设置你的 Cloudflare API token。
5. 运行 `docker compose up -d` 来启动服务。

## 网络模式

这个配置使用 Docker 的 host 网络模式，直接使用主机的网络栈。这意味着 Caddy 将直接绑定到主机的网络接口上，而不是通过 Docker 的网络隔离。这适用于没有 80 和 443 端口可用的场景，允许 Caddy 使用其他端口。

## 目录结构

- `Caddyfile`: Caddy 的主配置文件
- `data/`: Caddy 的数据目录，包括自动获取的 SSL 证书等
- `config/`: Caddy 的配置目录

请确保 `data/` 和 `config/` 目录存在并且 Docker 用户有适当的权限访问这些目录。

## 配置说明

- `Caddyfile`: Caddy 的主配置文件。你可以在这里定义你的网站和路由规则。
- 在 `compose.yaml` 中，确保设置了正确的 `CLOUDFLARE_API_TOKEN`。

### Caddyfile 示例说明

更多配置选项，请参考 [Caddy 官方文档](https://caddyserver.com/docs/).
