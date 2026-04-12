# Docker 部署指南

## 快速启动

### 1. 准备环境变量

复制环境变量文件并配置 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Qwen API Key：

```
QWEN_API_KEY=sk-your-api-key-here
```

### 2. 启动服务

```bash
docker compose up -d --build
```

### 3. 访问界面

打开浏览器访问：**http://localhost:8501**

### 4. 查看日志

```bash
docker compose logs -f ppt-generator
```

### 5. 停止服务

```bash
docker compose down
```

---

## 目录说明

启动后会自动创建以下目录（已配置持久化）：

| 目录 | 用途 |
|------|------|
| `output/` | 生成的 PPT 和 Excel 文件 |
| `artifacts/` | 临时文件、AI 洞察缓存 |
| `logs/` | 日志文件 |
| `resources/` | 用户上传的资源（需手动创建） |

---

## 手动创建资源目录

首次使用前，创建资源目录：

```bash
mkdir resources
```

该目录用于存放用户上传的图片等资源，**不会被 Git 追踪**。

---

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `QWEN_API_KEY` | 阿里云百炼 Qwen API Key | 空 |
| `LOG_LEVEL` | 日志级别 | `INFO` |

### 挂载卷

默认配置已将以下目录挂载到宿主机：

- `./output` → `/app/output`
- `./artifacts` → `/app/artifacts`
- `./logs` → `/app/logs`
- `./resources` → `/app/resources`
- `./templates` → `/app/templates`
- `./config.ini` → `/app/config.ini`

修改模板或配置文件后无需重启，直接生效。

---

## 常见问题

**Q: 容器启动失败？**  
A: 检查 `.env` 文件是否配置正确，查看日志：`docker compose logs ppt-generator`

**Q: 如何更新镜像？**  
A: 重新构建并启动：`docker compose up -d --build`

**Q: 如何进入容器？**  
A: `docker compose exec ppt-generator bash`

**Q: 生成的文件在哪里？**  
A: 宿主机的 `output/` 目录
