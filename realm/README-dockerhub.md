# Realm Docker 镜像

这是一个 Realm 代理服务器的 Docker 镜像。

## 快速开始

使用以下命令运行 Realm 镜像：

```bash
docker run -d --network host \
  -v ./config.toml:/etc/realm/config.toml:ro \
  liuweitao/realm:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例:

```yaml
services:
  realm:
    image: liuweitao/realm:latest
    network_mode: host
    volumes:
      - ./config.toml:/etc/realm/config.toml:ro
    restart: always
```

## 配置说明

- Realm 服务使用 host 网络模式，直接使用主机网络。
- config.toml 被挂载到容器中，使用只读模式以提高安全性。

## 注意事项

- 确保在生产环境中使用安全的配置。
- 定期更新 Realm 以获取最新的功能和安全补丁。
- 谨慎配置网络规则，只开放必要的端口和服务。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
