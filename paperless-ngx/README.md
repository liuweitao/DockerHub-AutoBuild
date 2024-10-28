# Paperless-ngx Docker Image

这个目录包含了用于构建 Paperless-ngx Docker 镜像的文件。该镜像在官方镜像的基础上添加了中文 OCR 支持。

## 特性

- 基于官方 Paperless-ngx 镜像
- 添加中文简体和繁体 OCR 支持
- 自动更新到最新版本
- 支持 PostgreSQL 数据库
- 集成 Apache Tika 用于文档解析

## 使用方法

### 快速开始

1. 创建项目目录：
```bash
mkdir paperless-ngx
cd paperless-ngx
```

2. 下载并配置 compose 文件：
```bash
# 下载 compose 文件
wget -O compose.yaml https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/refs/heads/main/docker/compose/docker-compose.postgres-tika.yml

# 将镜像地址替换为本镜像地址
sed -i 's/ghcr.io\/paperless-ngx\/paperless-ngx:latest/liuweitao\/paperless-ngx:latest/g' compose.yaml
```

3. 下载并配置环境文件：
```bash
# 下载环境配置文件
wget https://raw.githubusercontent.com/liuweitao/DockerHub-AutoBuild/master/paperless-ngx/.env
wget https://raw.githubusercontent.com/liuweitao/DockerHub-AutoBuild/master/paperless-ngx/docker-compose.env

# 修改 docker-compose.env 中的域名配置
sed -i 's/paperless.example.com/your-domain.com/g' docker-compose.env
```

4. 启动服务：
```bash
# 拉取镜像
docker compose pull

# 创建管理员用户
docker compose run --rm webserver createsuperuser

# 启动服务
docker compose up -d
```

## 配置说明

### 环境变量

- `USERMAP_UID` 和 `USERMAP_GID`: 运行服务的用户和组 ID
- `PAPERLESS_OCR_LANGUAGES`: 安装的 OCR 语言包
- `PAPERLESS_URL`: 服务访问地址
- `PAPERLESS_TIME_ZONE`: 时区设置
- `PAPERLESS_OCR_LANGUAGE`: OCR 识别使用的语言

### 目录结构

compose 文件会创建以下卷：
- `data`: 数据库和索引文件
- `media`: 处理后的文档存储
- `export`: 文档导出目录
- `consume`: 文档导入目录

## 中文 OCR 支持

本镜像已预装中文 OCR 支持，包括：
- 简体中文 (chi_sim)
- 繁体中文 (chi_tra)

可以通过 `PAPERLESS_OCR_LANGUAGE` 环境变量配置使用的语言。

## 注意事项

1. 首次运行前请修改环境配置中的域名地址
2. 确保为文档存储预留足够的磁盘空间
3. 建议配置数据备份策略
4. 如果需要使用 HTTPS，请配置反向代理

## 故障排除

如果遇到问题，可以通过以下命令查看日志：
```bash
docker compose logs -f
```

## 更新说明

镜像会通过 GitHub Actions 自动检查并构建最新版本。您可以通过以下命令更新到最新版本：

```bash
docker compose pull
docker compose up -d
```

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分：
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
