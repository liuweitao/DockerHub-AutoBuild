# 自用 Docker 镜像构建仓库

这个仓库包含了我个人使用的 Docker 镜像的自动构建配置。所有的构建过程都是开源的，并且由 GitHub Actions 自动完成，确保了构建的安全性和透明度。

## 支持的镜像

- Nextcloud
- CoreDNS
- FRP（服务器端和客户端）
- Endlessh
- Realm
- Caddy-CF（带有 Cloudflare DNS 插件的 Caddy）

## 特性

- 每日自动检查软件的新版本
- 多架构构建（支持 amd64 和 arm64）
- 自动将新镜像推送到 Docker Hub
- 为每个软件进行版本跟踪

## 项目结构

每个项目都包含以下文件：
- `Dockerfile`: 用于构建 Docker 镜像
- `compose.yaml`: Docker Compose 配置文件
- `README.md`: 项目说明文件
- 配置文件示例（如适用）

## 使用方法

1. 克隆此仓库
2. 进入所需项目的目录
3. 按照项目 README.md 中的说明进行配置
4. 使用 `docker compose up -d` 启动服务

## 镜像列表

要使用这些镜像，您可以从 Docker Hub 拉取：

```
docker pull liuweitao/nextcloud:latest
docker pull liuweitao/coredns:latest
docker pull liuweitao/frps:latest
docker pull liuweitao/frpc:latest
docker pull liuweitao/endlessh:latest
docker pull liuweitao/realm:latest
docker pull liuweitao/caddy-cf:latest

## 安全性

所有的构建过程都在 GitHub Actions 中进行，您可以在工作流程文件中查看具体的构建步骤。这确保了构建过程的透明度和安全性。

## 贡献和需求

这是一个个人使用的项目，但如果您发现任何问题或有改进建议，欢迎提出 Issue 或 Pull Request。

虽然我平时比较忙，但我会尽量抽出时间来满足那些提出需求的人。如果您有任何特殊需求或建议，请随时在 Issues 中提出。我会在有空的时候尽力满足这些需求。

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

## 致谢

- [Nextcloud](https://nextcloud.com/)
- [CoreDNS](https://coredns.io/)
- [FRP](https://github.com/fatedier/frp)
- [Endlessh](https://github.com/skeeto/endlessh)
- [Realm](https://github.com/realm/realm)
- [Caddy](https://caddyserver.com/)

感谢这些优秀的开源项目，本仓库仅用于个人使用目的的自动化构建。
