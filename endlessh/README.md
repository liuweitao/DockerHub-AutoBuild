# Endlessh

这是一个 Endlessh SSH 蜜罐的 Docker 镜像配置。

## 使用方法

1. 复制 `compose.yaml` 和 `endlessh_config` 到你的项目目录中。
2. 修改 `endlessh_config` 以满足你的需求。
3. 修改系统 SSH 的端口号（见下方说明）。
4. 运行 `docker compose up -d` 来启动服务。

## 配置说明

### compose.yaml

服务配置使用自定义的 Endlessh 镜像，并映射了标准 SSH 端口 22。endlessh_config 被挂载到容器中，使用只读模式以提高安全性。

### endlessh_config 示例

```
# 监听端口
Port 22

# 延迟时间范围（毫秒）
DelayMin 10000
DelayMax 30000

# 最大线程数
MaxClients 4096

# 最大行长度
MaxLineLength 32

# 最大连接数
MaxLines 32

# 日志详细程度
LogLevel 1

```

## 修改系统 SSH 端口

在启动 Endlessh 之前，需要修改系统的 SSH 端口，以避免与 Endlessh 冲突：

1. 修改 `/etc/ssh/sshd_config` 文件：
   - 找到 `#Port 22` 这一行
   - 去掉 `#` 号，将端口改为自定义端口，例如：`Port 2222`

2. 重启 SSH 服务以使修改生效：
   ```
   systemctl restart sshd.service
   ```

3. 在另一个终端中使用新端口测试 SSH 连接，确保修改成功。

## 启动 Endlessh

执行以下命令启动 Endlessh：

```
docker compose up -d
```

这将从 Docker Hub 拉取预构建的镜像并启动容器。整个过程通常很快，除非是首次下载镜像时可能需要一些时间，具体取决于您的网络速度。

## 验证效果

要查看 Endlessh 的运行日志，可以使用以下命令：

```
docker compose logs -f
```

这将实时显示日志输出。如果有 SSH 连接尝试，你将在日志中看到相关信息。

你也可以使用另一个终端，尝试连接到 22 端口，以测试 Endlessh 是否正常工作。

## 自定义

你可以通过修改 `endlessh_config` 来自定义 Endlessh 的行为。更多配置选项，请参考 [Endlessh GitHub 仓库](https://github.com/skeeto/endlessh)。
