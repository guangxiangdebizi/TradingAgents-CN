# Agent Service Dockerfile
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app:/app/backend
ENV PYTHONUNBUFFERED=1

# 配置国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制共享模块
COPY shared /app/backend/shared

# 复制requirements文件
COPY agent-service/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY agent-service/ .

# 暴露端口
EXPOSE 8008

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]
