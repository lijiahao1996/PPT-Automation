# PPT 报告生成系统

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 5.0 Web 版  
> **最后更新**: 2026-04-11

---

## 🚀 快速开始

### 方式 1: Web 界面（推荐）

#### 本地运行

```bash
cd C:\Users\50319\Desktop\n8n
python -m streamlit run scripts/config_tool/app.py --server.port 8501
```

#### Docker 运行

```bash
# 克隆项目
git clone https://github.com/lijiahao1996/PPT-Automation.git
cd PPT-Automation

# 配置 API Key
echo "QWEN_API_KEY=sk-your-key" > .env

# 启动服务
docker-compose up -d
```

#### 访问界面

打开浏览器：**http://localhost:8501/**

### 方式 2: 命令行

```bash
cd C:\Users\50319\Desktop\n8n
.\Run.bat
```

---

## 📁 目录结构

```
n8n/
├── scripts/                 # 核心脚本
│   ├── config_tool/         # Web 配置工具
│   ├── core/                # 核心引擎
│   ├── ai/                  # AI 模块
│   └── fanruan/             # 帆软模块
├── templates/               # PPT 模板
├── skills/                  # AI Skill
├── docs/                    # 文档
├── resources/               # 资源文件
├── output/                  # 输出目录
├── artifacts/               # 临时文件
├── logs/                    # 日志目录
├── Dockerfile               # Docker 镜像配置
├── docker-compose.yml       # Docker 编排配置
├── requirements.txt         # Python 依赖
├── config.ini               # 配置文件
├── Run.bat                  # 一键运行
└── README.md                # 项目文档
```

---

## ⚙️ 配置说明

### 通过 Web 界面配置（推荐）

1. 访问 http://localhost:8501/
2. 进入 **"⚙️ 项目配置"** 页签
3. 配置以下内容：
   - **API Key 配置** - Qwen API Key（用于 AI 洞察）
   - **路径配置** - 一般使用默认值即可
   - **高级配置** - 会话有效期、日志级别

### 配置文件

`config.ini` 已通过 Web 界面管理，无需手动编辑。

**必要配置**:
- `qwen_api_key` - 阿里云百炼 Qwen API Key

---

## 📊 使用流程

### 1. 上传数据
进入 **"📋 统计规则配置"** 页签，上传 Excel 数据文件。

### 2. 配置统计规则
添加需要的统计规则（KPI、排名、占比等）。

### 3. 配置图表
进入 **"📈 图表配置"** 页签，为每个统计配置图表。

### 4. 配置 AI 洞察
进入 **"💡 洞察配置"** 页签，配置每个图表的 AI 分析维度。

### 5. 生成 PPT
进入 **"🚀 生成 PPT 报告"** 页签，点击"▶️ 开始生成 PPT 报告"。

---

## 🐳 Docker 部署

详细文档：**[docs/Docker 部署指南.md](docs/Docker 部署指南.md)**

### 快速部署

```bash
# 配置 API Key
echo "QWEN_API_KEY=sk-your-key" > .env

# 启动服务
docker-compose up -d

# 访问界面
http://localhost:8501/

# 停止服务
docker-compose down
```

---

## 🔑 获取 API Key

1. 访问：https://bailian.console.aliyun.com/
2. 登录阿里云账号
3. 创建 API Key
4. 在 Web 界面或 `.env` 文件中配置

---

## 📝 日志查看

### 本地运行

日志文件位置：`logs/ppt_YYYYMMDD.log`

例如：`logs/ppt_20260411.log`

### Docker 运行

```bash
# 查看容器日志
docker logs -f ppt-report-generator

# 查看应用日志
docker exec ppt-report-generator cat logs/ppt_$(date +%Y%m%d).log
```

---

## 📚 文档

- **[使用示例](docs/使用示例.md)** - 完整的使用流程演示
- **[Docker 部署指南](docs/Docker 部署指南.md)** - Docker 部署详细说明

---

## ❓ 常见问题

**Q: Web 界面无法启动？**  
A: 确保已安装 Streamlit：`pip install streamlit`

**Q: Docker 容器启动失败？**  
A: 查看日志：`docker logs ppt-report-generator`

**Q: API Key 在哪里获取？**  
A: 阿里云百炼控制台：https://bailian.console.aliyun.com/

**Q: 日志文件在哪里？**  
A: `logs/` 目录下，按日期命名

**Q: 如何修改配置？**  
A: 通过 Web 界面的 **"⚙️ 项目配置"** 页签

**Q: 如何备份数据？**  
A: 备份 `output/` 和 `logs/` 目录

---

## 🌍 支持的平台

- ✅ Windows
- ✅ macOS
- ✅ Linux
- ✅ Docker（任何支持 Docker 的系统）

---

**最后更新**: 2026-04-11  
**版本**: 5.0 Web 版  
**状态**: ✅ 生产就绪
