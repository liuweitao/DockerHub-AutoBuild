# Caddy 镜像

本目录统一维护项目中的自定义 Caddy 镜像。不同镜像共用一个 Dockerfile 和一套自动构建流程，但仍按功能发布到独立的 Docker Hub 仓库。

## 镜像与模块

| 镜像 | 编译模块 | 说明 |
| --- | --- | --- |
| `liuweitao/caddy-cf` | `github.com/caddy-dns/cloudflare` | 支持 Cloudflare DNS challenge |
| `liuweitao/caddy-webdav` | `github.com/caddy-dns/cloudflare`、`github.com/mholt/caddy-webdav` | 保持既有 CF + WebDAV 组合，兼容现有用户 |
| `liuweitao/caddy-naive` | `github.com/caddyserver/forwardproxy=github.com/klzgrad/forwardproxy@naive` | 支持 NaïveProxy 服务端 |

`caddy-webdav` 中的 Cloudflare DNS 模块是既有镜像行为，不会移除。只使用 WebDAV 的用户无需配置 Cloudflare；未在 Caddyfile 中使用的模块不会自行启用。

## 目录结构

每个 `variants` 子目录提供对应镜像的配置和 Compose 示例：

- [`cf`](./variants/cf)
- [`webdav`](./variants/webdav)
- [`naive`](./variants/naive)

镜像由 [build-caddy-images.yml](../.github/workflows/build-caddy-images.yml) 统一检查 Caddy 和插件版本、构建并发布。定时检查采用按依赖选择构建：

- Caddy 更新：构建全部镜像。
- Cloudflare 插件更新：构建 `caddy-cf` 和 `caddy-webdav`。
- WebDAV 插件更新：只构建 `caddy-webdav`。
- Naïve `forwardproxy` 更新：只构建 `caddy-naive`。
- 没有任何更新：跳过构建。

构建时会使用检测到的完整 commit SHA 固定插件版本，全部选中镜像成功后才更新仓库中的版本记录。代码推送或手动触发工作流时会完整构建三个镜像。

`caddy-naive` 还需要修改 Caddy 核心，不能只通过 `xcaddy --with` 添加插件。构建脚本会从同一个 forwardproxy commit 获取并应用[上游构建](https://github.com/klzgrad/forwardproxy/blob/e747854e78743dba85c039b38ed185fb11d93667/.github/workflows/build.yml)使用的两个补丁，再用 `xcaddy --replace` 编译指定版本的 Caddy：

- `caddy-sing-quic-bbrv1.patch`：QUIC BBRv1 拥塞控制。
- `caddy-read-idle-timeout.patch`：认证 CONNECT 隧道的空闲超时覆盖 API。

后一个补丁提供 Caddy 2.11.7 尚未包含的 `caddyhttp.IdleTimeoutsFromContext`，是 forwardproxy `e747854e78743dba85c039b38ed185fb11d93667` 起的编译依赖。补丁应用失败会终止构建，避免发布不兼容的组合。

## 本地构建

以 Cloudflare 版本为例：

```bash
docker build \
  --build-arg CADDY_VERSION=2.10.2 \
  --build-arg CADDY_MODULES="--with github.com/caddy-dns/cloudflare" \
  -t caddy-cf:local \
  .
```

`CADDY_MODULES` 由构建流程维护。修改模块组合时，应同时更新本页中的模块表以及构建工作流的矩阵配置。

构建 Naïve 版本时，需要用同一个完整 SHA 设置插件模块和 `CADDY_NAIVE_VERSION`，以便同步获取配套补丁：

```bash
NAIVE_VERSION=e747854e78743dba85c039b38ed185fb11d93667
docker build \
  --build-arg CADDY_VERSION=2.11.7 \
  --build-arg CADDY_NAIVE_VERSION="$NAIVE_VERSION" \
  --build-arg CADDY_MODULES="--with github.com/caddyserver/forwardproxy=github.com/klzgrad/forwardproxy@$NAIVE_VERSION" \
  -t caddy-naive:local \
  .
```
