FROM docker.m.daocloud.io/library/python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY requirements.txt .

# 配置pip国内源并安装Python依赖
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV C_FORCE_ROOT=1

# 创建数据目录
RUN mkdir -p /app/data

# 默认命令（会被docker-compose覆盖）
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info"]
