# 自用 Docker 镜像构建仓库

这个仓库包含了我个人使用的 Docker 镜像的自动构建配置。所有的构建过程都是开源的，并且由 GitHub Actions 自动完成，确保了构建的安全性和透明度。

## 支持的镜像

- Nextcloud
- CoreDNS
- FRP（服务器端和客户端）
- Endlessh
- Realm

## 特性

- 每日自动检查软件的新版本（除 Endlessh 外）
- 多架构构建（支持 amd64 和 arm64）
- 自动将新镜像推送到 Docker Hub
- 为每个软件进行版本跟踪（除 Endlessh 外）

## 工作流程

### Nextcloud

- 文件：`.github/workflows/build-nextcloud-docker.yml`
- 构建最新版本的 Nextcloud
- 包含额外的 PHP 扩展和 ffmpeg

### CoreDNS

- 文件：`.github/workflows/build-coredns-docker.yml`
- 构建最新版本的 CoreDNS

### FRP

- 文件：`.github/workflows/build-frp-docker.yml`
- 同时构建 FRP 服务器（frps）和客户端（frpc）
- 使用单一的 Dockerfile，通过构建参数区分服务器和客户端版本

### Endlessh

- 文件：`.github/workflows/build-endlessh-docker.yml`
- 构建 Endlessh SSH 蜜罐

### Realm

- 文件：`.github/workflows/build-realm-docker.yml`
- 构建最新版本的 Realm
- 支持 amd64 和 arm64 架构

## 使用方法

要使用这些镜像，您可以从 Docker Hub 拉取：

```
docker pull liuweitao/nextcloud:latest
docker pull liuweitao/coredns:latest
docker pull liuweitao/frps:latest
docker pull liuweitao/frpc:latest
docker pull liuweitao/endlessh:latest
docker pull liuweitao/realm:latest
```

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

感谢这些优秀的开源项目，本仓库仅用于个人使用目的的自动化构建。
