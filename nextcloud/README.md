# Nextcloud

这是一个 Nextcloud 服务器的 Docker 镜像配置。

## 使用方法

1. 复制 `compose.yaml` 到你的项目目录中。
2. 根据需要修改 `compose.yaml` 中的环境变量和端口映射。
3. 运行 `docker compose up -d` 来启动服务。

## 配置说明

### compose.yaml

- Nextcloud 服务使用自定义镜像，并映射了 8080 端口到容器的 80 端口。
- 使用 MariaDB 作为数据库。
- 两个服务都使用 Docker volumes 来持久化数据。

## 启动服务

执行以下命令启动 Nextcloud 服务：

```
docker compose up -d
```

这将从 Docker Hub 拉取预构建的镜像并启动容器。

## 访问 Nextcloud

启动服务后，你可以通过浏览器访问 `http://your_server_ip:8080` 来使用 Nextcloud。

## 验证效果

要查看 Nextcloud 的运行日志，可以使用以下命令：

```
docker compose logs -f
```

这将实时显示日志输出。

## 自定义

你可以通过修改 `compose.yaml` 文件来自定义 Nextcloud 的配置。更多配置选项，请参考 [Nextcloud 官方文档](https://docs.nextcloud.com/server/latest/admin_manual/installation/docker.html)。

## 注意事项

- 请确保在生产环境中更改所有的默认密码。
- 考虑使用 HTTPS 来加强安全性。
- 定期备份你的数据。
