# PPT 报告生成系统 - Docker 部署指南

> 🐳 **使用 Docker 在任何环境下运行 PPT 报告生成系统**  
> **版本**: 5.0 Docker 版  
> **最后更新**: 2026-04-11

---

## 📋 目录

1. [前提条件](#1-前提条件)
2. [快速开始](#2-快速开始)
3. [配置说明](#3-配置说明)
4. [数据持久化](#4-数据持久化)
5. [环境变量](#5-环境变量)
6. [常见问题](#6-常见问题)

---

## 1. 前提条件

### 1.1 安装 Docker

**Windows**:
- 下载：https://www.docker.com/products/docker-desktop
- 安装 Docker Desktop

**macOS**:
- 下载：https://www.docker.com/products/docker-desktop
- 安装 Docker Desktop

**Linux**:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# CentOS/RHEL
yum install -y docker
systemctl start docker
```

### 1.2 验证安装

```bash
docker --version
docker-compose --version
```

---

## 2. 快速开始

### 2.1 克隆项目

```bash
git clone https://github.com/lijiahao1996/PPT-Automation.git
cd PPT-Automation
```

### 2.2 配置 API Key

**方式 1: 环境变量（推荐）**

创建 `.env` 文件：
```bash
QWEN_API_KEY=sk-your-api-key-here
```

**方式 2: Web 界面配置**

启动后在 Web 界面的"⚙️ 项目配置"中配置。

### 2.3 启动服务

**使用 Docker Compose（推荐）**:
```bash
docker-compose up -d
```

**使用 Docker 命令**:
```bash
# 构建镜像
docker build -t ppt-report-generator .

# 启动容器
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -e QWEN_API_KEY=sk-your-api-key-here \
  --name ppt-report \
  ppt-report-generator
```

### 2.4 访问界面

打开浏览器，访问：**http://localhost:8501/**

### 2.5 停止服务

```bash
docker-compose down
```

---

## 3. 配置说明

### 3.1 配置文件

`config.ini` 会挂载到容器中：
```
./config.ini → /app/config.ini
```

### 3.2 目录挂载

| 本地目录 | 容器目录 | 说明 |
|---------|---------|------|
| `./output` | `/app/output` | PPT 报告输出 |
| `./artifacts` | `/app/artifacts` | 临时文件 |
| `./logs` | `/app/logs` | 日志文件 |
| `./templates` | `/app/templates` | PPT 模板 |
| `./resources` | `/app/resources` | 资源文件 |

### 3.3 网络配置

默认端口：**8501**

如需修改端口，编辑 `docker-compose.yml`：
```yaml
ports:
  - "8502:8501"  # 本地 8502 → 容器 8501
```

---

## 4. 数据持久化

### 4.1 持久化数据

以下目录已配置持久化：
- `output/` - 生成的 PPT 报告
- `logs/` - 日志文件
- `templates/` - PPT 模板
- `resources/` - 资源文件

### 4.2 查看日志

```bash
# 查看容器日志
docker logs -f ppt-report-generator

# 查看应用日志
cat logs/ppt_$(date +%Y%m%d).log
```

### 4.3 备份数据

```bash
# 备份输出文件
tar -czf ppt-output-backup.tar.gz output/

# 备份日志
tar -czf ppt-logs-backup.tar.gz logs/
```

---

## 5. 环境变量

### 5.1 可用环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| `QWEN_API_KEY` | Qwen API Key | 空 |
| `STREAMLIT_SERVER_PORT` | Streamlit 端口 | 8501 |
| `STREAMLIT_SERVER_ADDRESS` | Streamlit 地址 | 0.0.0.0 |
| `PYTHONUNBUFFERED` | Python 输出缓冲 | 1 |

### 5.2 使用环境变量

**方式 1: .env 文件**
```bash
QWEN_API_KEY=sk-your-api-key-here
```

**方式 2: 命令行**
```bash
docker run -e QWEN_API_KEY=sk-your-api-key-here ...
```

**方式 3: docker-compose.yml**
```yaml
environment:
  - QWEN_API_KEY=${QWEN_API_KEY}
```

---

## 6. 常见问题

### Q1: 容器启动失败？

**检查 Docker 是否运行**:
```bash
docker ps
```

**查看容器日志**:
```bash
docker logs ppt-report-generator
```

### Q2: 无法访问 Web 界面？

**检查端口是否被占用**:
```bash
# Windows
netstat -ano | findstr :8501

# Linux/macOS
lsof -i :8501
```

**修改端口**:
编辑 `docker-compose.yml`，修改端口映射。

### Q3: 数据丢失？

**确保目录挂载正确**:
```bash
docker inspect ppt-report-generator | grep Mounts -A 20
```

**检查文件权限**:
```bash
ls -la output/
ls -la logs/
```

### Q4: 如何更新镜像？

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启容器
docker-compose up -d
```

### Q5: 如何在后台运行？

```bash
# 使用 -d 参数
docker-compose up -d

# 查看运行状态
docker-compose ps
```

### Q6: 如何进入容器？

```bash
docker exec -it ppt-report-generator bash
```

### Q7: 如何清理数据？

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi ppt-report-generator

# 清理所有数据（谨慎使用）
docker-compose down -v
```

---

## 📊 完整部署流程

```
1. 安装 Docker
   ↓
2. 克隆项目
   ↓
3. 配置 API Key（.env 文件）
   ↓
4. 启动服务（docker-compose up -d）
   ↓
5. 访问界面（http://localhost:8501/）
   ↓
6. 使用 Web 界面配置和生成 PPT
```

---

## 🎯 优势

### 跨平台
- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ 任何支持 Docker 的系统

### 易部署
- ✅ 一键启动
- ✅ 无需安装 Python
- ✅ 无需配置依赖

### 易维护
- ✅ 数据持久化
- ✅ 日志集中管理
- ✅ 易于备份和迁移

### 易扩展
- ✅ 支持集群部署
- ✅ 支持负载均衡
- ✅ 支持 Kubernetes

---

**祝你部署顺利！** 🎉
