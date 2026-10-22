# Laravel PHP 7.4 Docker Image

这个目录包含了用于构建 Laravel PHP 7.4 Docker 镜像的文件。该镜像提供了一个优化的 PHP-FPM 7.4 环境，专为运行 Laravel 应用程序而设计。

## 特性

- 基于 Alpine Linux 的 PHP 7.4-FPM
- 包含常用的 PHP 扩展
- 支持自定义 UID 和 GID
- 预装 Composer

## 已安装的 PHP 扩展

- pdo
- pdo_mysql
- bcmath
- gd
- redis
- mongodb
- openssl


## PHP2Shell 安全回补（2026-10-22）

镜像保留 PHP 7.4.33，并在官方基础镜像自带源码上应用 PHP 安全团队的
[官方补丁 712e60f](https://github.com/php/php-src/commit/712e60f9edfd03f0960fc4fc3c2c375f42b90aa2)，
重新编译 PHP 内核和扩展，处理 CVE-2026-109618 / CVE-2026-109619。
补丁保存在 `patches/php2shell.patch`，构建时验证 SHA-256，应用失败会终止构建。

这是已停止支持分支的最小安全回补，不代表 PHP 7.4 或 Alpine 3.16 获得持续安全支持。
回补在内存耗尽时直接退出工作进程，当前请求可能出现 502，FPM 会补充工作进程；
该请求的 PHP shutdown 回调不会执行。请安排迁移到受支持的 PHP 版本。

Redis 固定为 6.3.0，MongoDB 固定为仍支持 PHP 7.4 的 1.20.1，Composer 使用 2.2 LTS。
默认 UID/GID 均为 1000，保持原有非 root 运行方式。
同时在 php.ini 和 FPM 池禁用上传进度；普通文件上传继续可用。

推送本目录、公共验证脚本或对应 workflow 的修改会自动重建，也可手动运行
`Build Laravel PHP 7.4 Docker Image`。发布前验证扩展、Composer、FPM 请求，
并检查 OOM 不再进入旧的 shutdown 路径，失败时不会发布镜像。
构建完成后，使用方必须重新拉取 `laravel-php:7.4` 并重建容器。
