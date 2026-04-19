# PPT 报告自动生成系统

**版本**: v2.0  
**最后更新**: 2026-04-19  
**技术栈**: Python + Streamlit + Matplotlib + python-pptx + 千问 AI

基于 Excel 数据自动生成带图表和 AI 洞察的 PPT 分析报告，支持 16 种图表类型、AI 智能推荐和灵活的模板系统。

---

## 🚀 快速开始

### 方式一：本地运行（推荐用于开发调试）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key（可选，用于 AI 功能）
# 编辑 config.ini，填入 qwen_api_key

# 3. 启动
streamlit run scripts/config_tool/app.py --server.port 8501

# 4. 访问 http://localhost:8501
```

**Windows 快捷启动**：
```bash
start.bat
```

### 方式二：Docker 部署（推荐用于生产环境）

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

---

## ✨ 核心功能

### 📊 智能数据分析
- **AI 推荐统计规则** - 根据数据特征自动推荐统计维度
- **16 种图表类型** - 柱状图、条形图、饼图、折线图、热力图、散点图等
- **双渲染模式** - 图片模式（所有图表）+ 原生模式（6 种基础图表可编辑）

### 🤖 AI 洞察生成
- **基于千问 API** - 自动生成商业分析文案
- **多种分析维度** - 趋势分析、异常检测、策略建议
- **可配置风格** - 正式、简洁、详细等多种输出风格

### 🎨 灵活模板系统
- **自定义 PPT 模板** - 支持上传企业模板
- **占位符驱动** - `[CHART:xxx]`、`{{INSIGHT:xxx}}`、`{{TEXT:xxx}}`
- **自动模板生成** - 一键生成包含所有占位符的模板 Demo

### ⚙️ Web 配置界面
- **8 个功能页签** - 从数据上传到 PPT 生成的完整流程
- **实时预览** - 数据源预览、配置即时生效
- **配置持久化** - JSON 格式保存，支持版本管理

---

## 📁 项目结构详解

```
n8n/
│
├── 📂 scripts/                           # 核心代码
│   ├── 📂 config_tool/                   # Web 配置界面（Streamlit）
│   │   ├── app.py                        # 主入口，8 个页签的路由和布局
│   │   ├── app_config.py                 # 应用配置管理、路径解析、环境检测
│   │   └── 📂 tabs/                      # 8 个功能页签
│   │       ├── tab1_stats_rules.py       # 统计规则配置：上传 Excel、AI 推荐统计维度、执行统计
│   │       ├── tab2_chart_config.py      # 图表配置：AI 推荐图表、手动添加、渲染模式选择
│   │       ├── tab3_insight_config.py    # 洞察配置：设置 AI 分析维度、风格、触发条件
│   │       ├── tab4_custom_vars.py       # 自定义变量：文本变量、KPI 卡片配置
│   │       ├── tab5_conclusion_strategy.py # 结论策略：报告结论和建议模板
│   │       ├── tab6_ppt_vars.py          # PPT 变量总览：查看所有占位符、下载模板 Demo
│   │       ├── tab7_project_config.py    # 项目配置：API Key、AI 开关、全局设置
│   │       └── tab8_generate_report.py   # 生成报告：上传模板、一键生成 PPT
│   │
│   ├── 📂 core/                          # 核心引擎
│   │   ├── 📂 charts/                    # 图表生成模块（16 种）
│   │   │   ├── basic_charts.py           # 基础图表：条形图、柱状图、饼图、折线图、热力图、多列柱状图
│   │   │   ├── distribution_charts.py    # 分布图表：散点图、直方图、箱线图、小提琴图、气泡图
│   │   │   └── advanced_charts.py        # 高级图表：面积图、误差棒图、极坐标图、瀑布图、漏斗图
│   │   ├── chart_engine.py               # 图表引擎总入口，整合所有图表类型
│   │   ├── chart_recommender.py          # 图表推荐器：根据统计类型推荐合适的图表
│   │   ├── ppt_chart_engine.py           # PPT 原生图表引擎：在 PPT 中创建可编辑图表
│   │   ├── stats_engine.py               # 统计引擎：数据聚合、分组统计、指标计算
│   │   ├── stats_recommender.py          # 统计推荐器：AI 推荐统计规则
│   │   ├── data_loader.py                # 数据加载器：Excel 读取、数据校验、字段检测
│   │   ├── field_detector.py             # 字段检测器：自动识别日期、数值、分类字段
│   │   ├── template_engine.py            # 模板引擎：占位符替换、PPT 操作
│   │   ├── validator.py                  # 数据校验器：配置验证、数据完整性检查
│   │   └── 📂 styles/                    # 样式配置
│   │       ├── enterprise.mplstyle       # Matplotlib 企业风格样式
│   │       └── color_palette.json        # 企业配色方案
│   │
│   ├── 📂 ai/                            # AI 模块
│   │   ├── qwen_client.py                # 千问 API 客户端：对话、JSON 解析
│   │   └── insight_generator.py          # 洞察生成器：基于统计数据生成分析文案
│   │
│   └── generate_report.py                # PPT 生成主脚本：完整报告生成流程
│
├── 📂 skills/                            # AI Skill 规范（动态生成）
│   ├── 📂 chart-config-recommender/      # 图表配置推荐技能
│   │   ├── SKILL.md                      # 图表推荐规则（动态生成，包含 16 种图表详细说明）
│   │   └── skill_builder.py              # SKILL.md 生成器：根据统计规则动态构建
│   ├── 📂 data-insight/                  # 数据洞察技能
│   │   ├── SKILL.md                      # 洞察生成规则
│   │   └── skill_builder.py              # 洞察 SKILL 生成器
│   └── 📂 stats-rule-recommender/        # 统计规则推荐技能
│       ├── SKILL.md                      # 统计推荐规则
│       └── skill_builder.py              # 统计 SKILL 生成器
│
├── 📂 docker/                            # Docker 部署配置
│   ├── Dockerfile                        # 镜像构建文件（基于 python:3.12-slim）
│   ├── docker-compose.yml                # 容器编排配置
│   ├── config.ini                        # Docker 环境配置文件
│   ├── build_and_run.bat                 # Windows 快捷构建脚本
│   ├── README.md                         # Docker 部署详细说明
│   └── 📂 artifacts/                     # Docker 配置挂载点
│       ├── placeholders.json             # 占位符配置
│       └── stats_rules.json              # 统计规则配置
│
├── 📂 artifacts/                         # 运行时配置和缓存
│   ├── stats_rules.json                  # 统计规则配置（Tab 1 生成）
│   ├── placeholders.json                 # 图表/洞察/文本占位符配置（Tab 2-6 生成）
│   ├── ai_insights.json                  # AI 洞察缓存
│   └── 📂 temp/                          # 临时图表图片（PNG）
│
├── 📂 output/                            # 生成结果（运行时创建）
│   ├── 📂 uploaded/                      # 用户上传的 Excel 文件
│   ├── 📂 summary/                       # 统计汇总 Excel 文件
│   └── 📂 report/                        # 生成的 PPT 报告
│
├── 📂 templates/                         # PPT 模板
│   ├── 原生报告模板.pptx                  # 默认 PPT 模板（支持原生图表）
│   └── PPT模板_Demo.pptx                 # 占位符模板 Demo（Tab 6 生成）
│
├── 📂 resources/                         # 用户上传资源
│   ├── 📂 images/                        # 图片资源
│   └── 📂 videos/                        # 视频资源
│
├── 📂 logs/                              # 日志文件（按日期分割）
│   ├── ppt_20260419.log                  # PPT 生成日志
│   └── analyze_20260411.log              # 数据分析日志
│
├── config.ini                            # 全局配置文件（API Key、AI 开关等）
├── requirements.txt                      # Python 依赖列表
├── start.bat                             # Windows 快捷启动脚本
├── start.sh                              # Linux/Mac 快捷启动脚本
├── .gitignore                            # Git 忽略规则
├── .dockerignore                         # Docker 忽略规则
└── README.md                             # 项目说明文档
```

---

## 🔄 使用流程

### 完整工作流

```
1. Tab 1: 上传 Excel → AI 推荐统计规则 → 执行统计
   ↓
2. Tab 2: AI 推荐图表配置 → 选择渲染模式（图片/原生）
   ↓
3. Tab 3: 配置 AI 洞察维度 → 设置分析风格
   ↓
4. Tab 4-5: 配置自定义变量 → 设置结论策略
   ↓
5. Tab 6: 查看所有占位符 → 下载模板 Demo（可选）
   ↓
6. Tab 8: 上传 PPT 模板 → 一键生成报告
```

### 快速示例（5 分钟生成报告）

1. **上传数据** - Tab 1 上传 `销售表.xlsx`
2. **执行统计** - 点击"▶ 执行统计"（自动生成图表配置）
3. **生成 PPT** - Tab 8 点击"🚀 生成 PPT 报告"
4. **下载结果** - 获取 `销售表_报告_20260419.pptx`

---

## 📊 支持的图表类型

### 基础图表（6 种，支持原生模式）
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `bar_horizontal` | 横向条形图 | 排名对比 |
| `bar_vertical` | 纵向柱状图 | 指标对比 |
| `pie` | 环形饼图 | 占比分析 |
| `line` | 折线图 | 趋势分析 |
| `column_clustered` | 分组柱状图 | 多系列对比 |
| `area` | 面积图 | 累计趋势 |

### 分布图表（5 种，仅图片模式）
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `scatter` | 散点图 | 相关性分析 |
| `histogram` | 直方图 | 分布分析 |
| `boxplot` | 箱线图 | 异常值检测 |
| `violin` | 小提琴图 | 分布密度 |
| `bubble` | 气泡图 | 三维数据 |

### 高级图表（5 种，仅图片模式）
| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `heatmap` | 热力图 | 矩阵数据、二维对比 |
| `errorbar` | 误差棒图 | 误差分析 |
| `polar` | 极坐标图 | 周期数据 |
| `waterfall` | 瀑布图 | 增减分析 |
| `funnel` | 漏斗图 | 流程转化 |

---

## ⚙️ 配置说明

### config.ini 配置项

```ini
[api_keys]
qwen_api_key = sk-xxx  # 千问 API Key（可选）

[ai]
enable_ai_insight = true  # 是否启用 AI 洞察
enable_ai_recommend = true  # 是否启用 AI 推荐

[report]
default_template = 原生报告模板.pptx  # 默认模板
output_format = pptx  # 输出格式
```

### 占位符格式

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| 图表 | `[CHART:xxx]` | `[CHART:sales_ranking]` | 自动替换为图表图片 |
| 洞察 | `{{INSIGHT:xxx}}` | `{{INSIGHT:sales_trend}}` | AI 生成的分析文案 |
| 文本 | `{{TEXT:xxx}}` | `{{TEXT:report_title}}` | 自定义文本变量 |
| KPI | `{{KPI:cards}}` | `{{KPI:cards}}` | 核心指标卡片 |

---

## 🐳 Docker 部署

### 快速命令

```bash
# 启动
cd docker
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止
docker compose down

# 重新构建
docker compose up -d --build --force-recreate
```

### 目录挂载

Docker 容器挂载以下目录，数据持久化到宿主机：

- `docker/artifacts/` → 配置文件
- `docker/output/` → 生成的文件
- `docker/logs/` → 日志文件
- `docker/templates/` → PPT 模板
- `docker/resources/` → 用户资源

详见 [docker/README.md](docker/README.md)

---

## 🛠️ 开发指南

### 添加新图表类型

1. 在 `scripts/core/charts/` 下创建图表模块
2. 在 `chart_engine.py` 中注册图表类型
3. 更新 `skill_builder.py` 添加图表说明
4. 更新 `chart_recommender.py` 添加推荐规则

### 自定义 AI Skill

编辑 `skills/` 目录下的 SKILL.md 文件，或修改 `skill_builder.py` 自定义生成逻辑。

### 调试模式

```bash
# 开启详细日志
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run scripts/config_tool/app.py
```

---

## ❓ 常见问题

**Q: Web 界面打不开？**  
A: 检查端口 8501 是否被占用，或更换端口：`streamlit run app.py --server.port 8502`

**Q: AI 洞察不生成？**  
A: 检查 `config.ini` 中 `enable_ai_insight = true` 且 API Key 正确

**Q: 热力图生成失败？**  
A: 热力图只需配置 `y_field`（行字段），`columns` 会自动提取

**Q: 如何修改模板？**  
A: 编辑 `templates/` 下的 PPT 文件，使用占位符格式标记位置

**Q: 日志在哪里？**  
A: `logs/` 目录，按日期分割，如 `ppt_20260419.log`

**Q: Docker 构建慢？**  
A: 配置国内镜像源，见 [docker/README.md](docker/README.md)

---

## 📝 更新日志

### v2.0 (2026-04-19)
- ✅ 支持 16 种图表类型
- ✅ AI 智能推荐统计规则和图表配置
- ✅ 双渲染模式（图片/原生）
- ✅ 动态 SKILL.md 生成
- ✅ 完整的热力图、文本卡片支持
- ✅ Docker 部署优化

### v1.0 (2026-04-11)
- 初始版本
- 基础图表生成
- AI 洞察功能

---

## 📄 License

MIT

---

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**技术支持**: 查看 `logs/` 目录下的日志文件排查问题
