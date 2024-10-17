FROM alpine:latest AS builder

# 安装必要的软件包并构建 Endlessh
RUN apk add --no-cache build-base git && \
    git clone https://github.com/skeeto/endlessh.git /endlessh && \
    cd /endlessh && \
    make

FROM alpine:latest

# 复制构建好的二进制文件
COPY --from=builder /endlessh/endlessh /usr/local/bin/

# 创建配置目录并复制配置文件
RUN mkdir -p /etc/endlessh
COPY endlessh_config /etc/endlessh/endlessh.conf

# 暴露端口
EXPOSE 22

# 运行 Endlessh
ENTRYPOINT ["/usr/local/bin/endlessh"]
CMD ["-f", "/etc/endlessh/endlessh.conf"]
