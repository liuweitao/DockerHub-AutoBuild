# CoreDNS Docker 镜像

这是一个 CoreDNS 服务器的 Docker 镜像配置。

## 快速开始

使用以下命令运行 CoreDNS 镜像:

```bash
docker run -d -p 53:53/udp -p 53:53/tcp \
  -v ./Corefile:/etc/coredns/Corefile:cached \
  liuweitao/coredns:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例:

```yaml
services:
  coredns:
    image: liuweitao/coredns:latest
    container_name: coredns
    restart: always
    volumes:
      - ./Corefile:/etc/coredns/Corefile:cached
    ports:
      - 53:53/tcp
      - 53:53/udp
```

## 配置说明

服务配置使用官方的 CoreDNS 镜像，并映射了 53 端口的 TCP 和 UDP。Corefile 被挂载到容器中，使用 cached 模式以提高性能。

## 注意事项

- 确保您的防火墙允许 53 端口的 TCP 和 UDP 流量。
- 考虑配置 DNSSEC 以增强安全性。
- 定期更新 CoreDNS 以获取最新的安全补丁。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
