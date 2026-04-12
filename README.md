# PPT 报告生成系统

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 6.0 Web 版（支持原生可编辑图表）  
> **最后更新**: 2026-04-12

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
│   ├── __init__.py             # 包初始化 (v6.0.0)
│   ├── generate_report.py      # PPT 生成主流程
│   │
│   ├── core/                   # 核心引擎
│   │   ├── __init__.py
│   │   ├── data_loader.py      # 数据加载器
│   │   ├── stats_engine.py     # 统计引擎 (配置化)
│   │   ├── chart_engine.py     # 图表引擎 (17 种图片图表)
│   │   ├── ppt_chart_engine.py # PPT 原生图表引擎 (新增)
│   │   ├── template_engine.py  # PPT 模板引擎
│   │   ├── validator.py        # 数据校验器
│   │   └── styles/             # 样式文件
│   │
│   ├── ai/                     # AI 模块
│   │   ├── __init__.py
│   │   └── qwen_client.py      # Qwen API 客户端
│   │   └── insight_generator.py  # AI 洞察生成
│   │
│   └── config_tool/            # Web 配置工具 (Streamlit)
│       ├── __init__.py
│       ├── app.py              # Streamlit 主程序 (8 Tabs)
│       ├── streamlit.bat       # 启动脚本
│       └── tabs/               # 8 个功能页签
│
├── templates/                  # 模板和配置
│   ├── stats_rules.json        # 统计规则配置
│   ├── placeholders.json       # PPT 占位符配置
│   └── *.pptx                  # PPT 模板文件
│
├── skills/                     # AI Skill 规范
│   ├── data-insight/           # 数据洞察 Skill
│   │   └── SKILL.md            # 运行时动态生成
│   ├── stats-rule-recommender/ # 统计规则推荐 Skill
│   │   └── SKILL.md
│   └── chart-config-recommender/ # 图表配置推荐 Skill
│       └── SKILL.md
│
├── resources/                  # 资源文件
│   └── images/                 # 用户上传图片
│
├── output/                     # 输出目录 (运行时生成)
│   ├── *.xlsx                  # 原始数据 + 统计汇总
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

### 2. AI 推荐统计规则（可选）
勾选 "✨ 使用 AI 自动推荐统计规则"，AI 会根据数据结构推荐合适的统计规则。

### 3. 配置图表
进入 **"📈 图表配置"** 页签：
- 手动添加图表配置
- 或使用 AI 自动推荐图表配置
- **选择图表渲染方式**：
  - 🖼️ **图片方式**（不可编辑）- 生成 PNG 插入 PPT
  - 📊 **原生方式**（可编辑）- 在 PPT 中创建可编辑图表

### 4. 配置 AI 洞察
进入 **"💡 洞察配置"** 页签，配置每个图表的 AI 分析维度、风格、字数。

### 5. 自定义变量（可选）
进入 **"⚙️ 自定义变量"** 页签，添加文本、日期、图片、链接、表格变量。

### 6. 生成 PPT
进入 **"🚀 生成 PPT 报告"** 页签，点击"▶️ 开始生成 PPT 报告"。

---

## 🎨 图表渲染模式

### 🖼️ 图片方式（默认）

**流程**：
```
Excel 数据 → Matplotlib → PNG 图片 → 插入 PPT
```

**优势**：
- ✅ 支持所有 17 种图表类型
- ✅ 生成速度快
- ✅ 样式统一美观

**限制**：
- ❌ 不可在 PPT 中编辑

**适用场景**：
- 复杂图表（热力图、箱线图等）
- 批量生成报告
- 不需要后期修改

---

### 📊 原生方式（可编辑）

**流程**：
```
Excel 数据 → PPTChartEngine → PPT 原生 Chart 对象
```

**优势**：
- ✅ 可在 PPT 中编辑（修改数据/样式/颜色）
- ✅ 与 PPT 主题同步
- ✅ 支持动画效果
- ✅ 文件体积更小

**限制**：
- ❌ 仅支持 5 种基础图表类型
  - 柱状图/条形图
  - 饼图
  - 折线图
  - 面积图
  - 散点图

**适用场景**：
- 需要后期修改的图表
- 需要与 PPT 主题保持一致
- 需要添加动画效果

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

[ai]
enable_ai_insight = True  # 是否启用 AI 洞察生成
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
| `chart_engine.py` | 企业级图表生成器（Matplotlib），支持 17 种图片图表 |
| `ppt_chart_engine.py` | PPT 原生图表引擎，支持 5 种可编辑图表 |
| `template_engine.py` | PPT 模板加载与占位符填充 |
| `validator.py` | 数据质量校验器 |

### AI 模块 (`scripts/ai/`)

| 模块 | 功能 |
|------|------|
| `qwen_client.py` | Qwen API 统一客户端 |
| `insight_generator.py` | 调用 Qwen API 生成商业洞察 |

### AI Skills (`skills/`)

| Skill | 功能 |
|-------|------|
| `data-insight/SKILL.md` | 数据洞察生成规范（动态生成） |
| `stats-rule-recommender/SKILL.md` | 统计规则推荐规范 |
| `chart-config-recommender/SKILL.md` | 图表配置推荐规范 |

### Web 配置工具 (`scripts/config_tool/`)

8 个功能页签：

| Tab | 功能 | 配置文件 |
|-----|------|---------|
| 1️⃣ 统计规则配置 | AI 推荐 + 手动添加统计规则 | `stats_rules.json` |
| 2️⃣ 图表配置 | AI 推荐 + 手动添加图表，选择渲染模式 | `placeholders.json` |
| 3️⃣ 洞察配置 | 配置 AI 分析维度 | `placeholders.json` |
| 4️⃣ 自定义变量 | 文本/日期/图片/链接/表格变量 | `placeholders.json` |
| 5️⃣ AI 综合洞察 | 自定义结论、策略等 | `placeholders.json` |
| 6️⃣ PPT 变量总览 | 查看所有已配置变量 | - |
| 7️⃣ 项目配置 | 管理 `config.ini` | `config.ini` |
| 8️⃣ 生成 PPT 报告 | 一键执行完整流程 | - |

---

## 📈 支持的图表类型

### 图片图表（17 种）

| 类型 | 图表 |
|------|------|
| **基础图表** | 横向条形图、纵向柱状图、饼图/环形图、折线图、热力图、多列柱状图 |
| **分布图表** | 散点图、直方图、箱线图、小提琴图、气泡图 |
| **高级图表** | 面积图、误差棒图、极坐标图、瀑布图、漏斗图 |

### 原生图表（5 种）

| 类型 | 图表 |
|------|------|
| **基础图表** | 柱状图/条形图、饼图、折线图 |
| **其他** | 面积图、散点图 |

---

## 📝 日志查看

日志文件位置：`logs/ppt_YYYYMMDD.log`

例如：`logs/ppt_20260412.log`

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

**Q: 原生图表创建失败？**  
A: 检查：
1. PPT 模板中是否有对应的 `[CHART:xxx]` 占位符
2. 图表类型是否支持原生模式
3. 数据源字段名是否与 Excel 列名一致

**Q: 如何选择图表渲染模式？**  
A: Tab 2 → 展开图表配置 → 选择「图表渲染方式」：
- 不支持原生模式的图表会自动显示提示
- 已选择的图表会自动保存配置

---

## 🌍 支持的平台

- ✅ Windows
- ✅ macOS
- ✅ Linux

---

## 📊 更新日志

### v6.0.0 (2026-04-12)

**新增功能**：
- 🎨 图表渲染模式可选（图片方式/原生方式）
- 📊 PPT 原生图表引擎（支持 5 种可编辑图表）
- 🤖 AI Skill 规范化（统计规则推荐 + 图表配置推荐）
- ⚙️ Tab 2 自动禁用不支持的图表类型的原生模式

**优化改进**：
- 📝 日志输出优化（区分图片图表和原生图表）
- 🔧 移除误导性警告
- 🐛 修复 Unicode 编码问题（兼容 Windows GBK）

**技术改进**：
- 📦 新增 `ppt_chart_engine.py` 模块
- 🔗 优化图表配置字段名转换逻辑
- 🎯 支持 AI 输出的多种字段名格式

---

**最后更新**: 2026-04-12  
**版本**: 6.0 Web 版  
**状态**: ✅ 生产就绪
