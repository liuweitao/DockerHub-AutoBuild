# Laravel PHP 8 Docker Image

这个目录包含了用于构建 Laravel PHP 8 Docker 镜像的文件。该镜像提供了一个优化的 PHP-FPM 8.x 环境，专为运行 Laravel 应用程序而设计。

## 特性

- 基于 Alpine Linux 的最新 PHP 8.x-FPM
- 包含常用的 PHP 扩展
- 支持自定义 UID 和 GID
- 预装 Composer
- 自动更新到最新的 PHP 8.x 版本

## 已安装的 PHP 扩展

- pdo
- pdo_mysql
- imap
- openssl
- redis


## PHP2Shell 安全修复（2026-10-22）

默认基础镜像更新为 `php:8.5.12-fpm-alpine3.24`。
覆盖 `PHP_VERSION` 时也会检查实际 PHP 版本：最低为 8.2.35、8.3.36、8.4.27 或 8.5.12；
未审核的新分支或旧版本直接构建失败，避免发布未修复的镜像。
参考 [PHP 官方安全公告](https://www.php.net/index.php#2026-10-21-1)。

默认加载生产配置，并在 php.ini 和 FPM 池禁用上传进度，普通文件上传继续可用。
扩展编译后自动保留所需运行库、删除编译依赖，避免 IMAP 等扩展因缺库无法加载。

本目录或验证脚本修改、手动触发及每日任务都会使用新拉取的基础镜像重新构建，
即使 PHP 标签没有变化也会重建。扩展、Composer、内存限制和实际 FPM 请求验证通过后才发布。
标签保持 `laravel-php:8` 和对应完整版本标签。
发布完成后，使用方必须重新拉取镜像并重建容器。
