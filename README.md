# PPT 报告生成系统

**版本**: v2.0  
**最后更新**: 2026-04-13

基于 Excel 数据自动生成带图表和 AI 洞察的 PPT 分析报告。

---

## 快速开始

### 方式一：Docker（推荐）

```bash
# 1. 配置 API Key
cp docker/.env.example docker/.env
# 编辑 docker/.env，填入 QWEN_API_KEY

# 2. 启动
cd docker
docker compose up -d --build

# 3. 访问 http://localhost:8501
```

详细配置见 [docker/README.md](docker/README.md)

### 方式二：本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
# 复制 config.ini.example 为 config.ini，填入 qwen_api_key

# 3. 启动
streamlit run scripts/config_tool/app.py --server.port 8501

# 4. 访问 http://localhost:8501
```

---

## 功能

- 📊 **统计规则配置** - AI 推荐或手动定义统计维度
- 📈 **图表生成** - 17 种图表类型，支持图片/PPT 原生两种渲染模式
- 💡 **AI 洞察** - 基于千问 API 自动生成商业分析文案
- 🎨 **模板系统** - 可自定义 PPT 模板和占位符
- ⚙️ **配置化工具** - Web 界面管理所有配置

---

## 项目结构

```
.
├── docker/                 # Docker 部署文件
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── scripts/
│   ├── config_tool/        # Web 配置界面（Streamlit）
│   │   ├── app.py
│   │   └── tabs/           # 8 个功能页签
│   ├── core/               # 核心引擎
│   │   ├── chart_engine.py       # 图表生成（17 种）
│   │   ├── ppt_chart_engine.py   # PPT 原生图表
│   │   ├── template_engine.py    # 模板加载
│   │   ├── stats_engine.py       # 统计规则
│   │   └── data_loader.py        # 数据加载
│   └── ai/                 # AI 模块
│       ├── qwen_client.py        # Qwen API 客户端
│       └── insight_generator.py  # 洞察生成
├── templates/              # PPT 模板和占位符配置
├── skills/                 # AI Skill 规范
├── output/                 # 生成的 PPT/Excel（运行时创建）
├── logs/                   # 日志文件（运行时创建）
├── resources/              # 用户上传资源（需手动创建）
├── config.ini.example      # 配置文件模板
├── requirements.txt        # Python 依赖
└── README.md
```

---

## 使用流程

1. **上传 Excel 数据** - Tab 1 上传销售明细等数据
2. **配置统计规则** - AI 推荐或手动添加统计维度
3. **配置图表** - Tab 2 添加图表，选择渲染模式（图片/原生）
4. **配置洞察** - Tab 3 设置 AI 分析维度和风格
5. **生成 PPT** - Tab 8 一键执行

---

## 配置说明

### API Key

需要阿里云百炼 Qwen API Key：

1. 访问 https://bailian.console.aliyun.com/
2. 创建 API Key
3. 填入 `config.ini` 的 `[api_keys]` 部分

### 图表渲染模式

| 模式 | 支持类型 | 可编辑 | 适用场景 |
|------|----------|--------|----------|
| 图片 | 17 种 | ❌ | 复杂图表、批量生成 |
| 原生 | 5 种 | ✅ | 需后期修改、添加动画 |

原生模式支持：柱状图、条形图、饼图、折线图、面积图、散点图

---

## Docker 部署

详见 [docker/README.md](docker/README.md)

**快速命令：**

```bash
# 启动
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止
docker compose down

# 重新构建
docker compose up -d --build --force-recreate
```

---

## 依赖

```
streamlit==1.32.0
pandas==2.2.1
openpyxl==3.1.2
python-pptx==0.6.23
requests==2.31.0
numpy==1.26.4
XlsxWriter==3.2.0
```

---

## 常见问题

**Q: Web 界面打不开？**  
A: 检查端口 8501 是否被占用，或更换端口启动

**Q: AI 洞察不生成？**  
A: 检查 `config.ini` 中 API Key 是否正确，网络是否通畅

**Q: 图表渲染失败？**  
A: 原生模式仅支持 5 种基础图表，复杂图表请切换到图片模式

**Q: 如何修改模板？**  
A: 编辑 `templates/` 目录下的 PPT 文件和 `placeholders.json`

**Q: 日志在哪里？**  
A: `logs/` 目录，按日期分割

---

## License

MIT
