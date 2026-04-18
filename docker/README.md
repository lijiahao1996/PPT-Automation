# Docker 部署指南

## 快速开始

### 1. 构建镜像
```bash
cd docker
docker-compose build
```

### 2. 启动服务
```bash
docker-compose up -d
```

### 3. 访问应用
打开浏览器访问：http://localhost:8501

### 4. 查看日志
```bash
docker-compose logs -f
```

### 5. 停止服务
```bash
docker-compose down
```

## 目录结构

```
docker/
├── output/          # 运行时生成（自动创建）
│   ├── uploaded/    # 用户上传的 Excel
│   ├── summary/     # 统计汇总文件
│   └── report/      # 生成的 PPT 报告
├── artifacts/       # 临时文件和配置
├── logs/            # 日志文件
├── resources/       # 用户上传的资源（图片、视频）
├── templates/       # PPT 模板
├── config.ini       # 配置文件（可编辑）
└── docker-compose.yml
```

## 配置说明

### 方式一：Web 界面配置（推荐）
启动后通过 Streamlit Web 平台的 **Tab 7: 项目配置** 修改：
- API 密钥
- AI 洞察开关
- 日志级别

### 方式二：编辑配置文件
直接编辑 `docker/config.ini`：
```ini
[api_keys]
qwen_api_key = sk-your-api-key-here

[ai]
enable_ai_insight = False

[advanced]
log_level = INFO
```

修改后重启容器：
```bash
docker-compose restart
```

## 环境变量

可在 `docker-compose.yml` 或 `.env` 文件中配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LOG_LEVEL` | 日志级别 | `INFO` |
| `N8N_SCRIPTS_BASE_DIR` | 项目根目录 | `/app` |

## 数据持久化

通过 Docker volumes 实现数据持久化：
- `./output` → `/app/output`
- `./artifacts` → `/app/artifacts`
- `./logs` → `/app/logs`
- `./resources` → `/app/resources`

所有数据保存在 `docker/` 目录下，删除容器不会丢失数据。

## 常见问题

### 1. 中文字体显示问题
已内置文泉驿中文字体，无需额外配置。

### 2. Playwright 浏览器
镜像已预装 Chromium，如需更新：
```bash
docker-compose exec ppt-generator playwright install --with-deps chromium
```

### 3. 端口冲突
如果 8501 端口被占用，修改 `docker-compose.yml`：
```yaml
ports:
  - "8502:8501"  # 主机端口:容器端口
```

### 4. 查看容器状态
```bash
docker-compose ps
```

### 5. 进入容器调试
```bash
docker-compose exec ppt-generator bash
```

## 更新镜像

```bash
# 停止并删除旧容器
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 启动新容器
docker-compose up -d
```

## 生产环境建议

1. **配置 API 密钥**：在 `config.ini` 中设置真实的 `qwen_api_key`
2. **启用 AI 洞察**：将 `enable_ai_insight` 设为 `True`
3. **日志级别**：生产环境建议使用 `INFO`，调试时使用 `DEBUG`
4. **定期备份**：备份 `docker/output` 和 `docker/artifacts` 目录
