# Paperless-ngx Docker 镜像

这是一个基于官方 Paperless-ngx 镜像的定制版本，添加了中文 OCR 支持。

## 特性

- 基于官方 Paperless-ngx 镜像
- 支持中文简体和繁体 OCR
- 自动更新到最新版本

## 快速开始

1. 创建项目目录并下载配置文件：
```bash
mkdir paperless-ngx
cd paperless-ngx

# 下载 compose 文件
wget -O compose.yaml https://raw.githubusercontent.com/paperless-ngx/paperless-ngx/refs/heads/main/docker/compose/docker-compose.postgres-tika.yml

# 将镜像地址替换为本镜像地址
sed -i 's/ghcr.io\/paperless-ngx\/paperless-ngx:latest/liuweitao\/paperless-ngx:latest/g' compose.yaml

# 下载环境配置文件
wget https://raw.githubusercontent.com/liuweitao/DockerHub-AutoBuild/master/paperless-ngx/.env
wget https://raw.githubusercontent.com/liuweitao/DockerHub-AutoBuild/master/paperless-ngx/docker-compose.env

# 修改 docker-compose.env 中的域名配置
sed -i 's/paperless.example.com/your-domain.com/g' docker-compose.env
```

2. 启动服务：
```bash
# 拉取镜像
docker compose pull

# 创建管理员用户
docker compose run --rm webserver createsuperuser

# 启动服务
docker compose up -d
```

## 环境变量说明

- `USERMAP_UID` 和 `USERMAP_GID`: 运行服务的用户和组 ID
- `PAPERLESS_OCR_LANGUAGES`: 安装的 OCR 语言包
- `PAPERLESS_URL`: 服务访问地址
- `PAPERLESS_TIME_ZONE`: 时区设置
- `PAPERLESS_OCR_LANGUAGE`: OCR 识别使用的语言

## 存储卷

- `data`: 数据库和索引文件
- `media`: 处理后的文档存储
- `export`: 文档导出目录
- `consume`: 文档导入目录

## 中文 OCR 支持

本镜像已预装中文 OCR 支持，包括：
- 简体中文 (chi_sim)
- 繁体中文 (chi_tra)

## 注意事项

1. 首次运行前请修改环境配置中的域名地址
2. 确保为文档存储预留足够的磁盘空间
3. 建议配置数据备份策略
4. 如果需要使用 HTTPS，请配置反向代理

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分：
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和配置说明，请访问 GitHub 仓库。
