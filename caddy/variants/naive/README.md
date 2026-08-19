# Caddy-Naïve

这是一个包含 NaïveProxy 服务端所需 `forward_proxy` 模块的 Caddy 镜像。模块使用 NaïveProxy 上游维护的 fork 编译：

```text
github.com/caddyserver/forwardproxy=github.com/klzgrad/forwardproxy@naive
```

此镜像不包含 Cloudflare DNS 或 WebDAV 模块。

## 使用方法

1. 复制 `compose.yaml` 和 `Caddyfile` 到你的项目目录中。
2. 创建 `data`、`config` 和 `site` 文件夹。
3. 将 `Caddyfile` 中的 `example.com` 和 ACME 邮箱替换为真实值。
4. 在 `compose.yaml` 中设置高强度的 `NAIVE_USERNAME` 和 `NAIVE_PASSWORD`。
5. 运行 `docker compose up -d`。

示例使用 host 网络模式，使 Caddy 可以直接监听主机的 80/443 端口。

## 安全提示

- 不要保留示例用户名或密码，否则代理可能被第三方滥用。
- `forward_proxy` 上游将该模块标记为实验性功能，并提示可能出现破坏性变更。
- NaïveProxy 用于高风险场景前，应自行评估上游实现、部署环境和威胁模型。
- 请参考 [NaïveProxy 服务端配置文档](https://github.com/klzgrad/naiveproxy#server-setup)。
