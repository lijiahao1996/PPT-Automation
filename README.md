# PPT 报告生成系统

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 5.0 Web 版  
> **最后更新**: 2026-04-11

---

## 🚀 快速开始

### 方式 1: Web 界面（推荐）

```bash
cd C:\Users\50319\Desktop\n8n
python -m streamlit run scripts/config_tool/app.py --server.port 8501
```

访问界面：**http://localhost:8501/**

### 方式 2: 命令行

```bash
cd C:\Users\50319\Desktop\n8n
.\Run.bat
```

---

## 📁 目录结构

```
n8n/
├── Run.bat                     # Windows 入口脚本
├── Run.ps1                     # PowerShell 入口脚本
├── config.ini                  # 主配置文件
├── requirements.txt            # Python 依赖
├── README.md                   # 项目文档
├── .gitignore                  # Git 配置
│
├── scripts/                    # 核心代码
│   ├── __init__.py             # 包初始化 (v5.0.0)
│   ├── generate_report.py      # PPT 生成主流程
│   ├── ppt_report_executor.py  # Web 执行器
│   │
│   ├── core/                   # 核心引擎
│   │   ├── __init__.py
│   │   ├── data_loader.py      # 数据加载器
│   │   ├── stats_engine.py     # 统计引擎 (配置化)
│   │   ├── chart_engine.py     # 图表引擎 (17 种图表)
│   │   ├── template_engine.py  # PPT 模板引擎
│   │   ├── validator.py        # 数据校验器
│   │   └── styles/             # 样式文件
│   │       ├── enterprise.mplstyle
│   │       └── color_palette.json
│   │
│   ├── ai/                     # AI 模块
│   │   ├── __init__.py
│   │   └── insight_generator.py  # AI 洞察生成 (Qwen)
│   │
│   ├── fanruan/                # 帆软模块
│   │   ├── fanruan_login.py    # 帆软登录 (Playwright)
│   │   ├── fanruan_scrape.py   # 帆软数据抓取
│   │   └── fanruan_analyze.py  # 数据分析 + 统计
│   │
│   └── config_tool/            # Web 配置工具 (Streamlit)
│       ├── __init__.py
│       ├── app.py              # Streamlit 主程序 (8 Tabs)
│       ├── streamlit.bat       # 启动脚本
│       └── tabs/               # 8 个功能页签
│           ├── __init__.py
│           ├── tab1_stats_rules.py      # 统计规则配置
│           ├── tab2_chart_config.py     # 图表配置
│           ├── tab3_insight_config.py   # 洞察配置
│           ├── tab4_custom_vars.py      # 自定义变量
│           ├── tab5_conclusion_strategy.py  # 结论&策略
│           ├── tab6_ppt_vars.py         # PPT 变量总览
│           ├── tab7_project_config.py   # 项目配置
│           └── tab8_generate_report.py  # 生成 PPT 报告
│
├── templates/                  # 模板和配置
│   ├── stats_rules.json        # 统计规则配置
│   ├── placeholders.json       # PPT 占位符配置
│   └── *.pptx                  # PPT 模板文件
│
├── skills/                     # AI Skill 规范
│   └── data-insight/
│       └── SKILL.md            # 数据洞察 Skill (运行时生成)
│
├── resources/                  # 资源文件
│   └── images/                 # 用户上传图片
│
├── output/                     # 输出目录 (运行时生成)
│   ├── 帆软销售明细.xlsx       # 原始数据
│   ├── *_统计汇总.xlsx         # 统计汇总
│   └── *_报告_*.pptx           # 生成的 PPT
│
└── artifacts/                  # 临时文件 (运行时生成)
    ├── temp/                   # 临时图表
    └── ai_insights.json        # AI 洞察缓存
```

---

## 📊 使用流程

### 1. 上传数据
进入 Web 界面 **"📋 统计规则配置"** 页签，上传 Excel 数据文件。

### 2. 配置统计规则
添加需要的统计规则（KPI、排名、占比、对比、趋势、分布、矩阵、异常检测）。

### 3. 配置图表
进入 **"📈 图表配置"** 页签，为每个统计配置图表（支持 17 种图表类型）。

### 4. 配置 AI 洞察
进入 **"💡 洞察配置"** 页签，配置每个图表的 AI 分析维度、风格、字数。

### 5. 自定义变量（可选）
进入 **"⚙️ 自定义变量"** 页签，添加文本、日期、图片、链接、表格变量。

### 6. 生成 PPT
进入 **"🚀 生成 PPT 报告"** 页签，点击"▶️ 开始生成 PPT 报告"。

---

## ⚙️ 配置说明

### 配置文件

`config.ini` - 主配置文件，可通过 Web 界面 **"⚙️ 项目配置"** 页签管理：

```ini
[api_keys]
qwen_api_key = sk-xxx  # 阿里云百炼 Qwen API Key

[paths]
output_dir = output
artifacts_dir = artifacts
logs_dir = logs

[advanced]
session_max_age = 7      # 帆软会话有效期 (天)
log_level = INFO         # 日志级别
```

### 必要配置

- **Qwen API Key** - 用于 AI 洞察生成，获取地址：https://bailian.console.aliyun.com/

---

## 🔑 核心模块说明

### 核心引擎 (`scripts/core/`)

| 模块 | 功能 |
|------|------|
| `data_loader.py` | 统一数据加载接口，支持原始数据、统计汇总、KPI 提取 |
| `stats_engine.py` | 配置化统计引擎，从 `stats_rules.json` 读取规则 |
| `chart_engine.py` | 企业级图表生成器，支持 17 种图表类型 + 企业样式 |
| `template_engine.py` | PPT 模板加载与占位符填充，支持动态扫描 |
| `validator.py` | 数据质量校验器，预设销售数据校验规则 |

### AI 模块 (`scripts/ai/`)

| 模块 | 功能 |
|------|------|
| `insight_generator.py` | 调用 Qwen API 生成商业洞察，遵循 `skills/data-insight/SKILL.md` 规范 |

### 帆软模块 (`scripts/fanruan/`)

| 模块 | 功能 |
|------|------|
| `fanruan_login.py` | Playwright 自动登录帆软，保存会话状态 |
| `fanruan_scrape.py` | 拦截 API 抓取帆软数据，支持会话复用 |
| `fanruan_analyze.py` | 数据清洗 + 统计引擎执行 |

### Web 配置工具 (`scripts/config_tool/`)

8 个功能页签，全部在 `tabs/` 目录模块化：

| Tab | 功能 | 配置文件 |
|-----|------|---------|
| 1️⃣ 统计规则配置 | 添加/编辑统计规则，生成统计汇总 | `stats_rules.json` |
| 2️⃣ 图表配置 | 配置图表类型、数据源、字段 | `placeholders.json` |
| 3️⃣ 洞察配置 | 配置 AI 分析维度、风格、字数 | `placeholders.json` |
| 4️⃣ 自定义变量 | 文本/日期/图片/链接/表格变量 | `placeholders.json` |
| 5️⃣ AI 综合洞察 | 自定义结论、策略等综合洞察 | `placeholders.json` |
| 6️⃣ PPT 变量总览 | 查看所有已配置变量 | - |
| 7️⃣ 项目配置 | 管理 `config.ini` | `config.ini` |
| 8️⃣ 生成 PPT 报告 | 一键执行完整流程 | - |

---

## 📈 支持的图表类型

- 📊 **基础图表**: 横向条形图、纵向柱状图、饼图/环形图、折线图
- 📊 **对比图表**: 多列柱状图、热力图、散点图
- 📊 **分布图表**: 直方图、箱线图、小提琴图
- 📊 **高级图表**: 气泡图、误差棒图、极坐标图、瀑布图、漏斗图、面积图

---

## 📝 日志查看

日志文件位置：`logs/ppt_YYYYMMDD.log`

例如：`logs/ppt_20260411.log`

---

## ❓ 常见问题

**Q: Web 界面无法启动？**  
A: 确保已安装依赖：`pip install -r requirements.txt`

**Q: API Key 在哪里获取？**  
A: 阿里云百炼控制台：https://bailian.console.aliyun.com/

**Q: 如何修改配置？**  
A: 通过 Web 界面的 **"⚙️ 项目配置"** 页签

**Q: 文件被占用无法保存？**  
A: 关闭 Excel/WPS 中的相关文件后重试

---

## 🌍 支持的平台

- ✅ Windows
- ✅ macOS
- ✅ Linux

---

**最后更新**: 2026-04-11  
**版本**: 5.0 Web 版  
**状态**: ✅ 生产就绪
