# 国内镜像源配置指南

为了提高在中国大陆地区的下载速度，本项目已配置使用国内镜像源。

## 🚀 已配置的镜像源

### Docker 镜像源

所有 Docker 镜像都已配置使用 DaoCloud 容器镜像服务（免费无需登录）：

| 原始镜像 | 国内镜像源 |
|---------|-----------|
| `python:3.10-slim` | `docker.m.daocloud.io/library/python:3.10-slim` |
| `redis:7-alpine` | `docker.m.daocloud.io/library/redis:7-alpine` |
| `mongo:7` | `docker.m.daocloud.io/library/mongo:7` |
| `minio/minio:latest` | `docker.m.daocloud.io/minio/minio:latest` |
| `mongo-express:latest` | `docker.m.daocloud.io/library/mongo-express:latest` |
| `postgres:15` | `docker.m.daocloud.io/library/postgres:15` |

### APT 软件源

Dockerfile 中已配置使用中科大 APT 镜像源：
```bash
sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
```

### Python pip 源

Dockerfile 中已配置使用清华大学 PyPI 镜像源：
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

## 🔧 本地开发配置

### 配置 Docker 镜像加速器

#### 1. Docker Desktop (Windows/Mac)

在 Docker Desktop 设置中添加镜像加速器：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://reg-mirror.qiniu.com"
  ]
}
```

#### 2. Linux 系统

编辑 `/etc/docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.mirrors.ustc.edu.cn", 
    "https://reg-mirror.qiniu.com"
  ]
}
```

重启 Docker 服务：
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 配置 pip 镜像源

#### 临时使用
```bash
pip install -i https://mirrors.aliyun.com/pypi/simple/ package_name
```

#### 永久配置

**Linux/Mac:**
```bash
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
EOF
```

**Windows:**
```cmd
mkdir %APPDATA%\pip
echo [global] > %APPDATA%\pip\pip.ini
echo index-url = https://mirrors.aliyun.com/pypi/simple/ >> %APPDATA%\pip\pip.ini
echo trusted-host = mirrors.aliyun.com >> %APPDATA%\pip\pip.ini
```

### 配置 npm 镜像源

如果需要安装前端依赖：

```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或使用 cnpm
npm install -g cnpm --registry=https://registry.npmmirror.com
```

## 📊 镜像源对比

### Docker 镜像源

| 镜像源 | 地址 | 速度 | 稳定性 |
|-------|------|------|--------|
| **阿里云** | `registry.cn-hangzhou.aliyuncs.com` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 腾讯云 | `mirror.ccs.tencentyun.com` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 中科大 | `docker.mirrors.ustc.edu.cn` | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 七牛云 | `reg-mirror.qiniu.com` | ⭐⭐⭐ | ⭐⭐⭐ |

### Python pip 源

| 镜像源 | 地址 | 速度 | 稳定性 |
|-------|------|------|--------|
| **阿里云** | `mirrors.aliyun.com/pypi/simple/` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 清华大学 | `pypi.tuna.tsinghua.edu.cn/simple/` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中科大 | `pypi.mirrors.ustc.edu.cn/simple/` | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 豆瓣 | `pypi.douban.com/simple/` | ⭐⭐⭐ | ⭐⭐⭐ |

## 🔄 切换镜像源

### 临时切换到官方源

如果需要临时使用官方源，可以修改 docker-compose.yml：

```yaml
# 将
image: registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim
# 改为
image: python:3.10-slim
```

### 使用其他国内源

#### 腾讯云镜像源
```yaml
image: mirror.ccs.tencentyun.com/library/python:3.10-slim
```

#### 网易云镜像源
```yaml
image: hub-mirror.c.163.com/library/python:3.10-slim
```

## 🚀 构建优化

### 多阶段构建优化

```dockerfile
# 使用国内源的基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim as builder

# 配置国内源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
```

### 缓存优化

```bash
# 预拉取基础镜像
docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim
docker pull registry.cn-hangzhou.aliyuncs.com/library/redis:7-alpine
docker pull registry.cn-hangzhou.aliyuncs.com/library/mongo:7

# 构建时使用缓存
docker-compose build --parallel
```

## 🔍 故障排除

### 镜像拉取失败

如果遇到镜像拉取失败，可以尝试：

1. **检查网络连接**
   ```bash
   ping mirrors.aliyun.com
   ```

2. **清理 Docker 缓存**
   ```bash
   docker system prune -f
   ```

3. **手动拉取镜像**
   ```bash
   docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.10-slim
   ```

4. **切换到其他镜像源**
   ```bash
   # 修改 docker-compose.yml 中的镜像地址
   ```

### pip 安装失败

如果 pip 安装失败：

1. **检查镜像源连接**
   ```bash
   ping mirrors.aliyun.com
   ```

2. **临时使用其他源**
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name
   ```

3. **清理 pip 缓存**
   ```bash
   pip cache purge
   ```

## 📚 相关资源

- [阿里云容器镜像服务](https://cr.console.aliyun.com/)
- [阿里云 PyPI 镜像](https://mirrors.aliyun.com/pypi/)
- [Docker 官方镜像加速器配置](https://docs.docker.com/registry/recipes/mirror/)
- [pip 配置文档](https://pip.pypa.io/en/stable/topics/configuration/)

---

💡 **提示**: 使用国内镜像源可以显著提高构建和部署速度，建议在生产环境中也使用相应的镜像源配置。
