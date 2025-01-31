# FRP (Fast Reverse Proxy) Docker 镜像

这是 FRP 服务器端（frps）和客户端（frpc）的 Docker 镜像。

## 快速开始

使用以下命令运行 FRP 服务器端镜像：

```bash
docker run -d -p 7000:7000 -p 7500:7500 \
  -v ./frps.toml:/etc/frp/config.toml:ro \
  liuweitao/frps:latest
```

使用以下命令运行 FRP 客户端镜像：

```bash
docker run -d --network host \
  -v ./frpc.toml:/etc/frp/config.toml:ro \
  liuweitao/frpc:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例:
#### 服务端
```yaml
services:
  frps:
    image: liuweitao/frps:latest
    container_name: frps
    restart: always
    volumes:
      - ./frps.toml:/etc/frp/config.toml:ro
    network_mode: "host"
```
#### 客户端
```yaml
services:
  frpc:
    image: liuweitao/frpc:latest
    container_name: frpc
    restart: always
    volumes:
      - ./frpc.toml:/etc/frp/config.toml:ro
    network_mode: "host"
```

## 配置说明

- frps 服务使用 host 网络模式，直接使用主机网络。
- frpc 服务使用 host 网络模式，直接使用主机网络。
- 两个服务都将各自的配置文件以只读方式挂载到容器中。

## 注意事项

- 确保在生产环境中使用安全的配置，包括身份验证和加密。
- 定期更新 FRP 以获取最新的功能和安全补丁。
- 谨慎配置防火墙规则，只开放必要的端口。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
