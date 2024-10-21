# Endlessh Docker 镜像

这是一个 Endlessh SSH 蜜罐的 Docker 镜像。

## 重要提醒

在部署 Endlessh 之前，请务必先修改您系统的 SSH 端口。请严格按照以下步骤操作，以确保您不会失去对服务器的访问：

1. 保持当前的 SSH 连接打开，不要关闭。

2. 编辑 SSH 配置文件:
   ```
   sudo nano /etc/ssh/sshd_config
   ```

3. 找到 `#Port 22` 这一行，取消注释并修改端口号，例如:
   ```
   Port 2222
   ```

4. 保存文件并重启 SSH 服务:
   ```
   sudo systemctl restart sshd
   ```

5. 在不关闭当前 SSH 连接的情况下，打开一个新的终端窗口，尝试使用新端口连接到您的服务器:
   ```
   ssh -p 2222 user@your_server_ip
   ```

6. 只有在确认可以通过新端口成功连接 SSH 后，才能关闭原来的 SSH 连接并继续部署 Endlessh。

请注意：如果无法通过新端口连接，请不要关闭原有的 SSH 连接。使用原有连接修复配置，确保 SSH 服务正常工作。

## 快速开始

只有在确认新的 SSH 端口正常工作后，才能继续以下步骤。

使用以下命令运行 Endlessh 镜像：

```bash
docker run -d -p 22:22 \
  -v ./endlessh_config:/etc/endlessh/endlessh.conf:ro \
  liuweitao/endlessh:latest
```

## Docker Compose

以下是 `compose.yaml` 文件示例：

```yaml
services:
  endlessh:
    image: liuweitao/endlessh:latest
    ports:
      - "22:22"
    restart: always
    volumes:
      - ./endlessh_config:/etc/endlessh/endlessh.conf:ro
```

## 配置说明

服务配置使用自定义的 Endlessh 镜像，并映射了标准 SSH 端口 22。endlessh_config 被挂载到容器中，使用只读模式以提高安全性。

## 注意事项

- 在使用 Endlessh 之前，请确保已经按照上述步骤将您的实际 SSH 服务移动到其他端口，并验证新端口可以正常工作。
- 定期检查日志以监控潜在的攻击尝试。
- 不要在生产环境的关键服务器上使用，除非您完全理解其影响。
- 确保您的防火墙配置正确，允许访问新的 SSH 端口。

## 源码

此镜像是 DockerHub-AutoBuild 项目的一部分:
https://github.com/liuweitao/DockerHub-AutoBuild/

更多信息和更新，请访问 GitHub 仓库。
