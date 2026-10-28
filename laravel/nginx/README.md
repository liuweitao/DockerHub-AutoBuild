# Laravel Nginx Docker Image

这个目录包含了用于构建 Laravel Nginx Docker 镜像的文件。该镜像专为 Laravel 应用程序优化，提供了高性能的 Web 服务器环境。

## 特性

- 基于最新的 Alpine Linux 的 Nginx
- 针对 Laravel 应用程序优化的配置
- 支持自定义 UID 和 GID
- 自动更新到最新的稳定版本

## 自动更新

GitHub Actions 每天检查官方 `nginx:stable-alpine` 的镜像摘要（digest），
并使用对应的 `stable-alpine<版本>` 标签构建。即使标签名不变，只要官方更新
Nginx 或 Alpine 基础镜像，摘要变化也会触发重新构建。构建使用摘要锁定上游镜像，
通过 Nginx 配置和 Laravel 用户检查后，发布 `latest` 和原有的 Alpine 版本标签。

仅在发布成功后更新仓库根目录的 `.nginx-version` 和 `.nginx-digest`。
手动运行工作流或修改构建相关文件会强制重建。

