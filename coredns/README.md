# CoreDNS

这是一个 CoreDNS 服务器的 Docker 镜像配置。

## 使用方法

1. 复制 `compose.yaml` 和 `Corefile` 到你的项目目录中。
2. 修改 `Corefile` 以满足你的需求。
3. 运行 `docker compose up -d` 来启动服务。

## 配置说明

### compose.yaml

服务配置使用官方的 CoreDNS 镜像，并映射了 53 端口的 TCP 和 UDP。Corefile 被挂载到容器中，使用 cached 模式以提高性能。

## Corefile 示例

项目中包含了一个 `Corefile` 示例，其中包含了一些常用的配置选项。你可以根据需要修改这个文件。主要的配置包括：

- 日志记录和错误日志
- 健康检查
- Prometheus 指标收集
- DNS 缓存
- 查询转发到上游 DNS 服务器
- 本地域名解析示例
- 特定域名使用不同的上游 DNS 服务器

请根据你的需求调整 `Corefile` 的内容。更多配置选项，请参考 [CoreDNS 文档](https://coredns.io/manual/toc/).
