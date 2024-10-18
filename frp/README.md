# FRP (Fast Reverse Proxy)

这是 FRP 服务器端（frps）和客户端（frpc）的 Docker 镜像配置。

## 使用方法

1. 复制 `compose.yaml`、`frps.toml` 和 `frpc.toml` 到你的项目目录中。
2. 根据你的需求修改 `frps.toml` 和 `frpc.toml`。
3. 运行 `docker compose up -d` 来启动服务。

## 配置说明

### compose.yaml

- frps 服务使用端口映射模式，开放了 7000 和 7500 端口。
- frpc 服务使用 host 网络模式，直接使用主机网络。
- 两个服务都将各自的配置文件以只读方式挂载到容器中。

### frps.toml 示例

```toml
bindPort = 7000
```

### frpc.toml 示例

```toml
server_addr = x.x.x.x
server_port = 7000

[[proxies]]
name = "ssh"
type = "tcp"
local_ip = "127.0.0.1"
local_port = 22
remote_port = 6000
```

## 启动服务

执行以下命令启动 FRP 服务：

```
docker compose up -d
```

这将从 Docker Hub 拉取预构建的镜像并启动容器。

## 验证效果

要查看 FRP 的运行日志，可以使用以下命令：

```
docker compose logs -f
```

这将实时显示日志输出。

## 自定义

你可以通过修改 `frps.toml` 和 `frpc.toml` 来自定义 FRP 的行为。更多配置选项，请参考 [FRP GitHub 仓库](https://github.com/fatedier/frp)。
