FROM docker.m.daocloud.io/library/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 配置国内镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm main" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制共享模块
COPY shared /app/backend/shared

# 复制requirements文件
COPY analysis-engine/requirements.txt .

# 配置pip国内源并安装Python依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY analysis-engine/ .

# 设置环境变量
ENV PYTHONPATH=/app:/app/backend
ENV ANALYSIS_ENGINE_PORT=8001
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8001

# 启动命令
CMD ["python", "app/main.py"]
