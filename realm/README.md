# Realm

这是一个 Realm 代理服务器的 Docker 镜像配置。

## 使用方法

1. 复制 `compose.yaml` 和 `config.toml` 到你的项目目录中。
2. 修改 `config.toml` 以满足你的需求。
3. 运行 `docker compose up -d` 来启动服务。

## 配置说明

### compose.yaml

服务配置使用自定义的 Realm 镜像，并使用 host 网络模式。config.toml 被挂载到容器中，使用只读模式以提高安全性。

### config.toml 示例

```toml
[log]
level = "warn"
output = "realm.log"

[network]
no_tcp = false
use_udp = true

[[endpoints]]
listen = "0.0.0.0:5000"
remote = "1.1.1.1:443"

[[endpoints]]
listen = "0.0.0.0:10000"
remote = "www.google.com:443"
```

## 启动服务

执行以下命令启动 Realm 服务：

```
docker compose up -d
```

这将从 Docker Hub 拉取预构建的镜像并启动容器。

## 验证效果

要查看 Realm 的运行日志，可以使用以下命令：

```
docker compose logs -f
```

这将实时显示日志输出。

## 自定义

你可以通过修改 `config.toml` 来自定义 Realm 的行为。更多配置选项，请参考 [Realm GitHub 仓库](https://github.com/zhboner/realm)。
