# Android Debug Bridge (ADB) Docker 镜像

这是一个基于 Alpine Linux 的轻量级 ADB（Android Debug Bridge）Docker 镜像。它提供了一个隔离的环境来运行 ADB 命令，适用于自动化测试、CI/CD 流程或远程设备管理。

## 特性

- 基于轻量级的 Alpine Linux
- 包含完整的 ADB 工具集
- 支持 USB 设备连接
- 包含常用工具（curl、wget、usbutils）
- 自动化构建和更新

## 使用方法

### 快速开始

```bash
# 拉取镜像
docker pull liuweitao/adb:latest

# 运行容器
docker run -d --name adb \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  liuweitao/adb:latest
```

### 使用 Docker Compose

本项目已提供了预配置的 `compose.yaml` 文件，您可以直接使用：

1. 克隆仓库或下载 `compose.yaml` 文件
2. 在包含 `compose.yaml` 的目录中运行：
```bash
docker compose up -d
```

## 进入容器

```bash
docker exec -it adb sh
```

## ADB 命令示例

```bash
# 列出已连接的设备
adb devices

# 安装 APK
adb install app.apk

# 推送文件到设备
adb push local_file.txt /sdcard/

# 从设备拉取文件
adb pull /sdcard/remote_file.txt ./
```

## 注意事项

1. 容器需要以 privileged 模式运行才能访问 USB 设备
2. 确保主机系统已正确安装 USB 驱动
3. 如果设备无法识别，可能需要在主机系统上设置 udev 规则

## 构建信息

本镜像通过 GitHub Actions 自动构建并发布到 Docker Hub。您可以在 [GitHub 仓库](https://github.com/liuweitao/DockerHub-AutoBuild) 查看源代码和构建过程。

## 许可证

本项目采用 MIT 许可证。 