# PHPCMS PHP 7.4

将原来的 `liuweitao/php:7.4.30-phpcms` 纳入本仓库维护。保留该部署标签，
镜像内的 PHP 升级到 7.4.33，并应用 PHP 安全团队对 CVE-2026-109618 / CVE-2026-109619
提供的[官方源码回补](https://github.com/php/php-src/commit/712e60f9edfd03f0960fc4fc3c2c375f42b90aa2)。
新增别名 `liuweitao/php:7.4-phpcms` 指向同一镜像。

## 保留的配置

- PHP-FPM，GD（FreeType/JPEG）、mysqli，以及官方 PHP 镜像自带扩展。
- `www` 用户和组，默认 UID/GID 均为 1000。
- 工作目录 `/var/www/html`，使用生产版 php.ini。
- 原池配置的有效参数：dynamic、最大 5 个子进程、启动 2 个、空闲 1～3 个。
- `www.conf` 中的 `127.0.0.1:9000` 仍被官方 `zz-docker.conf` 覆盖为 `9000`，
  与旧镜像一样可供同一 Docker 网络中的反向代理连接。

仅禁用会话上传进度，普通文件上传仍可用。该配置是额外防护，核心修复由重新编译 PHP 完成。
PHP 7.4 和 Alpine 3.16 已停止支持，本次回补不代表其余历史风险均已修复。
回补在 OOM 时直接退出工作进程，当前请求可能返回 502，FPM 会补充工作进程，
该请求的 PHP shutdown 回调不会运行。应继续安排迁移到受支持的 PHP 版本。

## 构建与验证

从仓库根目录构建，复用 `php/common/` 中的补丁和内核编译脚本：

```sh
docker build -f php/phpcms/Dockerfile -t liuweitao/php:7.4.30-phpcms .
python3 scripts/check-php-image.py liuweitao/php:7.4.30-phpcms phpcms
```

修改本目录、公共构建文件或验证脚本时自动构建，也支持手动触发及每周重新构建。
验证 GD/mysqli、实际 FPM 请求、工作进程 UID/GID、上传进度状态和 OOM 安全退出后，
才会登录 Docker Hub 推送上述两个标签。沿用仓库现有的 `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` secrets。

## 更新旧项目

已有 Compose 配置仍可使用 `image: liuweitao/php:7.4.30-phpcms`。
在旧项目目录执行，`php` 替换为实际 PHP 服务名：

```sh
docker compose pull php
docker compose up -d --no-deps --force-recreate php
docker compose exec php php -v
```

应显示 PHP 7.4.33。仅重启旧容器不会换用新镜像，必须重新创建容器。
如果项目挂载了自己的 FPM 或 php.ini 配置，检查实际 FPM 配置是否仍禁用了上传进度；
源码补丁不依赖该配置，但挂载配置可能覆盖额外防护。
