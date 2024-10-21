# Nextcloud Docker 镜像

这是一个自定义的 Nextcloud Docker 镜像,包含额外的扩展和优化。

## 快速开始

使用以下命令运行 Nextcloud 镜像:

```bash
docker run -d -p 8080:80 liuweitao/nextcloud:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例:

```yaml
services:
  nextcloud:
    image: liuweitao/nextcloud:latest
    ports:
      - "8080:80"
    volumes:
      - ./nextcloud:/var/www/html
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud_password
    depends_on:
      - db
    restart: always

  db:
    image: mariadb:10.5
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - ./db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud_password
    restart: always
```

## 配置说明

- Nextcloud 服务使用自定义镜像,并将 8080 端口映射到容器的 80 端口。
- 使用 MariaDB 作为数据库。
- 两个服务都使用 Docker volumes 来持久化数据。

## 启动服务

执行以下命令启动 Nextcloud 服务:

```
docker compose up -d
```

这将从 Docker Hub 拉取预构建的镜像并启动容器。

## 访问 Nextcloud

启动服务后,你可以通过浏览器访问 `http://your_server_ip:8080` 来使用 Nextcloud。

## 验证效果

要查看 Nextcloud 的运行日志,可以使用以下命令:

```
docker compose logs -f
```

这将实时显示日志输出。

## 自定义

你可以通过修改 `compose.yaml` 文件来自定义 Nextcloud 的配置。更多配置选项,请参考 [Nextcloud 官方文档](https://docs.nextcloud.com/server/latest/admin_manual/installation/docker.html)。

## 注意事项

- 请确保在生产环境中更改所有的默认密码。
- 考虑使用 HTTPS 来加强安全性。
- 定期备份你的数据。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新,请访问 GitHub 仓库。
