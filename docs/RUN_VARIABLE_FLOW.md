# Run.bat 变量流转说明

## 📋 配置文件

### config.ini
```ini
[paths]
raw_data_file = 帆软销售明细.xlsx      # 原始数据文件（输入）
summary_file = 销售统计汇总.xlsx       # 统计汇总文件（输出）
```

**关系**：`summary_file` 由 `raw_data_file` 经过统计引擎生成

---

## 🔄 变量流转图

```
┌──────────────────────────────────────────────────────────────────┐
│                        config.ini                                 │
│  [paths]                                                          │
│  ├─ raw_data_file = 帆软销售明细.xlsx                             │
│  └─ summary_file = 销售统计汇总.xlsx                              │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                          Run.bat                                  │
│                     (调用 Run.ps1)                                │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                          Run.ps1                                  │
│  1. 读取 config.ini                                               │
│     $rawDataFileName = config.paths.raw_data_file                │
│     $summaryFileName = config.paths.summary_file                 │
│                                                                  │
│  2. 构建完整路径                                                  │
│     $rawDataFile = $outputDir + $rawDataFileName                 │
│     $summaryFile = $outputDir + $summaryFileName                 │
│                                                                  │
│  3. 检查文件存在性                                                 │
│     if (Test-Path $rawDataFile) { 跳过爬取 }                     │
│     else { 执行爬取 }                                             │
│                                                                  │
│  4. 调用 Python 脚本                                               │
│     python scripts/fanruan/fanruan_login.py                      │
│     python scripts/fanruan/fanruan_scrape.py                     │
│     python scripts/fanruan/fanruan_analyze.py                    │
│     python scripts/generate_report.py                            │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    fanruan_login.py                               │
│  输入：config.ini (fanruan.username, fanruan.password)           │
│  输出：artifacts/fanruan_session.json (会话状态)                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                   fanruan_scrape.py                               │
│  输入：                                                           │
│    - config.ini.paths.raw_data_file (文件名)                     │
│    - artifacts/fanruan_session.json (会话)                       │
│                                                                  │
│  处理：                                                           │
│    OUTPUT_FILE = OUTPUT_DIR + RAW_DATA_FILE_NAME                │
│                                                                  │
│  输出：output/帆软销售明细.xlsx                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                  fanruan_analyze.py                               │
│  输入：                                                           │
│    - config.ini.paths.raw_data_file (输入文件名)                │
│    - config.ini.paths.summary_file (输出文件名)                 │
│    - output/帆软销售明细.xlsx                                    │
│                                                                  │
│  处理：                                                           │
│    RAW_FILE = OUTPUT_DIR + RAW_DATA_FILE_NAME                   │
│    SUMMARY_FILE = OUTPUT_DIR + SUMMARY_FILE_NAME                │
│    1. 读取 RAW_FILE                                              │
│    2. 数据清洗 → artifacts/销售分析数据.xlsx                     │
│    3. 统计引擎 → SUMMARY_FILE                                    │
│                                                                  │
│  输出：                                                           │
│    - output/销售统计汇总.xlsx                                    │
│    - artifacts/销售分析数据.xlsx                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                   generate_report.py                              │
│  输入：                                                           │
│    - output/销售统计汇总.xlsx                                    │
│    - templates/销售分析报告_标准模板.pptx                        │
│    - templates/placeholders.json                                 │
│    - templates/stats_rules.json                                  │
│                                                                  │
│  处理：                                                           │
│    1. 加载统计数据                                                │
│    2. 生成 AI 洞察                                                 │
│    3. 生成图表                                                    │
│    4. 填充 PPT 模板                                                 │
│                                                                  │
│  输出：output/销售分析报告_时间戳_v1.pptx                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 文件清单

### 输入文件
| 文件 | 位置 | 说明 |
|------|------|------|
| `config.ini` | 根目录 | 配置文件（文件名、路径、API Key 等） |
| `帆软销售明细.xlsx` | `output/` | 原始数据（爬取或上传） |
| `销售分析报告_标准模板.pptx` | `templates/` | PPT 模板 |
| `stats_rules.json` | `templates/` | 统计规则配置 |
| `placeholders.json` | `templates/` | PPT 占位符配置 |

### 输出文件
| 文件 | 位置 | 说明 |
|------|------|------|
| `销售统计汇总.xlsx` | `output/` | 统计汇总（由统计引擎生成） |
| `销售分析报告_时间戳_v1.pptx` | `output/` | 最终 PPT 报告 |
| `销售分析数据.xlsx` | `artifacts/` | 清洗后的数据（中间文件） |
| `ai_insights.json` | `artifacts/` | AI 生成的洞察 |
| `temp/*.png` | `artifacts/` | 生成的图表（中间文件） |

### 配置文件
| 文件 | 位置 | 说明 |
|------|------|------|
| `fanruan_session.json` | `artifacts/` | 帆软会话状态（7 天有效） |
| `api_debug_full.json` | `artifacts/` | API 调试信息 |

---

## 🔧 修改文件名

如需修改输入/输出文件名，编辑 `config.ini`：

```ini
[paths]
# 原始数据文件名（从帆软爬取或手动上传）
raw_data_file = 我的销售数据.xlsx

# 统计汇总文件名（由原始数据生成）
summary_file = 我的统计汇总.xlsx
```

**注意**：两个文件名建议保持关联性，便于识别。

---

## 🎯 使用场景

### 场景 1：使用默认文件名
```ini
raw_data_file = 帆软销售明细.xlsx
summary_file = 销售统计汇总.xlsx
```
直接运行 `Run.bat` 即可。

### 场景 2：使用自定义文件名
```ini
raw_data_file = 2026 年 4 月销售数据.xlsx
summary_file = 2026 年 4 月统计汇总.xlsx
```
运行 `Run.bat` 会自动使用新文件名。

### 场景 3：多个项目并行
为每个项目创建独立的目录和 `config.ini`：
```
project_april/config.ini (raw_data_file = 4 月数据.xlsx)
project_may/config.ini (raw_data_file = 5 月数据.xlsx)
```

---

## ✅ 验证

运行后检查输出：
```bash
# 检查原始数据
ls output/帆软销售明细.xlsx

# 检查统计汇总
ls output/销售统计汇总.xlsx

# 检查 PPT 报告
ls output/销售分析报告_*.pptx
```

所有文件都应存在且大小合理（>10KB）。
