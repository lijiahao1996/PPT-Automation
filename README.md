# 帆软数据 → PPT 报告（企业版）

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 4.5 Enterprise - 核心模块重构  
> **最后更新**: 2026-04-07  
> **特性**: 零硬编码，所有配置从 placeholders.json 读取

---

## 🚀 快速开始

### 1️⃣ 首次配置

**首次运行前，需要配置 API Key 和账号密码**：

```bash
# 方法 1：复制模板（推荐）
copy config.ini.example config.ini

# 方法 2：手动创建
# 创建 config.ini 文件，参考 config.ini.example 填写
```

**编辑 `config.ini`，填写以下必填项**：

```ini
 # 替换为你的帆软密码
[fanruan]
username = YOUR_USERNAME_HERE
password = YOUR_PASSWORD_HERE 

[api_keys]
qwen_api_key = sk-YOUR_API_KEY_HERE  # ← 替换为你的 Qwen API Key
```

**获取 API Key**：
1. 访问：https://bailian.console.aliyun.com/
2. 登录阿里云账号
3. 创建 API Key
4. 复制到 config.ini

---

### 2️⃣ 一键运行

**Windows**: 双击 `启动器.bat`

**PowerShell**: `.\Run.ps1`

**EXE**: 双击 `PPT 生成.exe`

ℹ️ **提示**: 首次运行时，如果 `config.ini` 不存在，会自动从 `config.ini.example` 创建并提示你填写。

### 执行流程

```
原始数据 (output/帆软销售明细.xlsx)
   ↓
fanruan_analyze.py - 数据清洗 + 校验 + 统计
   ↓
output/销售统计汇总.xlsx (11 个统计表)
   ↓
generate_report.py - 主流程
   ├── 生成 AI 洞察 (Qwen API)
   ├── 生成 6 个图表 (Matplotlib)
   ├── 填充 PPT 模板
   └── 输出最终报告
   ↓
output/销售分析报告_YYYYMMDD_HHMMSS_v1.pptx ⭐
```

---

## 📁 目录结构

```
n8n/
├── 启动器.bat                        # 一键启动 ⭐
├── Run.ps1                          # 主执行脚本
├── config.ini                       # 配置文件 ⭐（需手动创建）
├── config.ini.example               # 配置模板 ⭐
├── README.md                        # 本文件
│
└── docs/                            # 【文档目录】
    └── architecture_final.drawio    # 流程图（draw.io）
│
├── templates/                       # PPT 模板目录
│   ├── 销售分析报告_标准模板.pptx
│   ├── placeholders.json            # 占位符配置（v4.0 完全配置化）⭐
│   ├── stats_rules.json             # 统计规则配置 ⭐
│   └── 完整配置指南.md               # 配置文档
│

│
├── skills/                          # AI Skill 规范
│   └── data-insight/
│       └── SKILL.md                 # AI 洞察生成规范
│
├── scripts/                         # 脚本目录
│   ├── core/                        # 核心模块 ⭐
│   │   ├── styles/                  # 企业样式配置
│   │   │   ├── enterprise.mplstyle  # Matplotlib 样式
│   │   │   └── color_palette.json   # 配色方案
│   │   │
│   │   ├── data_loader.py           # 数据加载器
│   │   ├── chart_engine.py          # 图表引擎
│   │   ├── template_engine.py       # PPT 模板引擎
│   │   ├── validator.py             # 数据校验器
│   │   └── stats_engine.py          # 统计引擎 ⭐
│   │
│   ├── ai/                          # AI 模块
│   │   └── insight_generator.py     # AI 洞察生成器
│   │
│   ├── fanruan/                     # 帆软数据模块
│   │   ├── fanruan_login.py         # 帆软登录
│   │   ├── fanruan_scrape.py        # 数据爬取
│   │   └── fanruan_analyze.py       # 数据清洗 + 统计
│   │
│   └── generate_report.py           # 【主流程】报告生成 ⭐
│
└── output/                          # 最终文件目录
    └── 销售分析报告_*.pptx          # 生成的报告（保留最新版）
```

---

## ⚙️ 配置说明

### 1. API Key 配置

编辑 `config.ini`:

```ini
[api_keys]
qwen_api_key = sk-xxx  # 替换为你的 Qwen API Key
```

**获取地址**: https://bailian.console.aliyun.com/

### 2. 帆软登录配置

```ini
[fanruan]
username = 13021020077
password = your_password
data_url = https://demo.fanruan.com/webroot/decision#/datacenter/config/table/xxx
```

### 3. 路径配置

```ini
[paths]
work_dir = C:\Users\50319\Desktop\n8n
output_dir = C:\Users\50319\Desktop\n8n\output
artifacts_dir = C:\Users\50319\Desktop\n8n\artifacts
logs_dir = C:\Users\50319\Desktop\n8n\logs
```

---

## 📊 占位符系统（v3.0 完全配置化）

### 零硬编码

所有配置从 `templates/placeholders.json` 读取：

- **文本占位符**: 标题、副标题、统计周期（自动从数据提取）
- **图表占位符**: 图表类型、字段、标题（完全配置化）
- **洞察占位符**: AI 生成的 10 条洞察
- **表格占位符**: 列名自动从数据提取

### 修改配置

**只需编辑 JSON**，无需修改 Python 代码！

```json
"CHART:sales_by_person": {
  "data_source": "销售员业绩",
  "chart_type": "bar_horizontal",
  "title": "销售员业绩表现分析"  // ← 直接修改标题
}
```

### 📖 配置文档

| 文档 | 位置 | 用途 |
|------|------|------|
| `templates/统计配置指南.md` | templates/ | 统计规则配置指南 |
| `templates/PPT 新增图表指南.md` | templates/ | PPT 图表配置指南 |
| `templates/配置指南.docx` | templates/ | 配置指南（Word 格式） |

---

## 🧠 AI 集成

### 调用模型
- **平台**: 阿里云百炼（通义千问）
- **模型**: `qwen-plus`
- **规范**: `skills/data-insight/SKILL.md`

### 输出格式

| PPT 页 | 格式 | 内容 |
|--------|------|------|
| 第 4 页（核心指标） | 单条 120-180 字 | 总销售额、订单数、客单价 |
| 第 5-11 页 | 3 条列表式 | 各维度分析 |
| 第 12 页（核心结论） | 4 条结构化 | 业绩结构、增长亮点、核心短板、业务风险 |
| 第 13 页（落地策略） | 4 条结构化 | 客户运营、产品组合、团队管理、营销节奏 |

---

## 🎨 企业样式

### 配色方案

| 颜色 | 色值 | 用途 |
|------|------|------|
| Primary | #1F4E79 | 主色调（标题、重点） |
| Secondary | #2E75B6 | 辅助色 |
| Accent | #E74C3C | 强调色（警告） |
| Success | #27AE60 | 成功/增长 |
| Warning | #F39C12 | 警告/注意 |

### Matplotlib 样式

- 字体：Microsoft YaHei
- DPI: 300（打印级）
- 网格：浅灰色虚线

---

## 🔧 命令行参数

```bash
# 默认运行（并行模式）
python scripts\generate_report.py

# 串行模式（兼容旧版）
python scripts\generate_report.py --serial

# 重新生成占位符配置
python scripts\generate_report.py --regenerate-placeholders

# 指定模板
python scripts\generate_report.py 销售分析报告_高管版.pptx

# 组合使用
python scripts\generate_report.py 新模板.pptx --regenerate-placeholders --serial
```

---

## 🔍 数据质量校验

自动校验规则：

| 规则 | 级别 | 说明 |
|------|------|------|
| 必填字段非空 | Fail | 订单时间、销售员、产品、城市、销售额 |
| 销售额非负 | Fail | 销售额不能为负值 |
| 最小记录数 | Fail | 至少 10 条记录 |
| 日期范围 | Warn | 订单时间在合理范围内 |

**校验失败时自动终止执行**。

---

## 📈 性能优化

### v4.1 优化内容

| 优化项 | 效果 |
|--------|------|
| 并行图表生成 | 提速 75%（2.0s → 0.5s） |
| 动态占位符配置 | 无需修改代码 |
| 统一日志配置 | 集中输出到 `logs/` |
| 删除未使用模块 | 减少 877 行代码 |

### 对比

| 版本 | 代码行数 | 图表生成 | 占位符 |
|------|---------|---------|--------|
| v4.0 | ~3500 行 | 串行 | 硬编码 |
| **v4.1** | **~2200 行** | **并行** | **动态配置** |

---

## 🔧 故障排查

### 问题 1：AI 洞察生成失败

**错误**: `RuntimeError: AI 洞察生成失败：Qwen API 调用无响应`

**解决**:
1. 检查 `config.ini` 中的 `qwen_api_key`
2. 检查网络连接：`ping dashscope.aliyuncs.com`
3. 登录阿里云百炼平台查看 API 额度

### 问题 2：数据校验失败

**错误**: `DataQualityError: 数据校验失败`

**解决**:
1. 查看 `logs/ppt_YYYYMMDD.log`
2. 检查错误信息中的具体校验规则
3. 修复原始数据后重试

### 问题 3：图表不显示

**原因**: 占位符格式不匹配

**解决**:
1. 检查 PPT 模板中的占位符格式
2. 运行 `--regenerate-placeholders` 重新扫描
3. 确保占位符文本框未被删除

### 问题 4：Matplotlib 样式警告

**错误**: `Bad key figure.linewidth`

**说明**: Matplotlib 3.10+ 兼容性问题，**不影响功能**，可忽略。

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| **4.5** | 2026-04-07 | 核心模块重构：styles + stats_engine → core/ ⭐ |
| 4.4 | 2026-04-07 | 配置集中管理：styles → scripts/config/ |
| 4.3 | 2026-04-07 | 生产就绪：清理临时文件，优化目录结构 |
| 4.2 | 2026-04-06 | 完全配置化：零硬编码，所有配置从 JSON 读取 |
| 4.1 | 2026-04-06 | 并行生成 + 动态占位符 + 代码清理 |
| 4.0 | 2026-04-05 | 企业级重构：模板引擎、图表引擎、数据校验 |
| 3.0 | 2026-04-04 | 删除图表版脚本，骨架 PPT 移至 artifacts |
| 2.0 | 2026-04-04 | 临时文件分离，Skill 规范升级 |
| 1.0 | 2026-04-03 | 初始版本 |

---

## 📞 技术支持

| 资源 | 位置 |
|------|------|
| 项目说明 | `README.md` |
| 占位符指南 | `PLACEHOLDERS_GUIDE.md` |
| 配置指南 | `CONFIG_GUIDE.md` |
| 日志文件 | `logs/ppt_YYYYMMDD.log` |
| AI 规范 | `skills/data-insight/SKILL.md` |

---

**最后更新**: 2026-04-07  
**架构**: Template Engine + Chart Engine + AI Insights  
**版本**: 4.5 Enterprise - 核心模块重构  
**状态**: ✅ 已优化，可打包部署
