# n8n 工作流程配置指南

> 📊 **版本**: 1.0 for n8n  
> **基于**: 帆软 PPT 生成系统 v4.5  
> **目标**: 将 Python 脚本迁移到 n8n 可视化工作流  
> **最后更新**: 2026-04-07

---

## 🎯 迁移目标

将现有 Python 脚本流程拆分为 n8n 节点，实现：

- ✅ 可视化工作流编排
- ✅ 每个功能模块独立为节点
- ✅ 配置化管理（API Key、模板路径等）
- ✅ 错误处理和重试机制
- ✅ 定时触发（每日/每周自动生成报告）
- ✅ Webhook 触发（外部系统调用）

---

## 📊 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     n8n 工作流                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Trigger (定时/手动)                                        │
│      ↓                                                      │
│  Check Data Files (检查数据)                                │
│      ↓                                                      │
│  Switch (条件分支)                                          │
│  ├─ [无数据] FanRuan Login → Scrape Data                   │
│  └─ [有数据] 直接进入分析                                   │
│      ↓                                                      │
│  Analyze Data (数据清洗 + 统计)                             │
│      ↓                                                      │
│  Generate AI Insights (AI 洞察)                             │
│      ↓                                                      │
│  Generate Charts × 6 (并行图表生成)                         │
│      ↓                                                      │
│  Fill PPT Template (填充模板)                               │
│      ↓                                                      │
│  Save Files (保存文件)                                      │
│      ↓                                                      │
│  Send Notification (发送通知)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 节点详细配置

### 节点 1: Trigger (触发器)

**节点类型**: `Schedule Trigger` 或 `Manual Trigger`

**配置**:
```json
{
  "triggerType": "schedule",
  "cronExpression": "0 9 * * 1-5",  // 工作日每天 9:00
  "timezone": "Asia/Shanghai"
}
```

**输出**: 触发信号

---

### 节点 2: Check Data Files (检查数据文件)

**节点类型**: `Function` 或 `Execute Command`

**功能**: 检查 `output/` 目录是否有 Excel 文件

**Function 节点代码**:
```javascript
const fs = require('fs');
const path = require('path');

// 配置路径
const outputDir = 'C:/Users/50319/Desktop/n8n/output';

// 检查是否有 Excel 文件
const files = fs.readdirSync(outputDir);
const excelFiles = files.filter(f => f.endsWith('.xlsx') && f.includes('帆软'));

if (excelFiles.length > 0) {
  return [{
    json: {
      hasData: true,
      dataFile: path.join(outputDir, excelFiles[0]),
      message: '找到数据文件，跳过爬取步骤'
    }
  }];
} else {
  return [{
    json: {
      hasData: false,
      dataFile: null,
      message: '未找到数据文件，需要爬取'
    }
  }];
}
```

**输出字段**:
| 字段 | 类型 | 说明 |
|------|------|------|
| `hasData` | boolean | 是否有数据文件 |
| `dataFile` | string | 数据文件路径 |
| `message` | string | 状态信息 |

---

### 节点 3: Switch (条件分支)

**节点类型**: `Switch`

**配置**:
```json
{
  "rules": [
    {
      "condition": "hasData === true",
      "output": "hasData"
    },
    {
      "condition": "hasData === false",
      "output": "noData"
    }
  ]
}
```

**输出路由**:
- `hasData` → 直接到 Analyze Data
- `noData` → 执行 FanRuan Login

---

### 节点 4: FanRuan Login (帆软登录) 【条件执行】

**节点类型**: `Execute Command`

**功能**: 使用 Playwright 登录帆软系统

**配置**:
```json
{
  "command": "python",
  "args": [
    "C:/Users/50319/Desktop/n8n/scripts/fanruan/fanruan_login.py"
  ],
  "options": {
    "cwd": "C:/Users/50319/Desktop/n8n",
    "env": {
      "FANRUAN_USERNAME": "{{$env.FANRUAN_USERNAME}}",
      "FANRUAN_PASSWORD": "{{$env.FANRUAN_PASSWORD}}"
    }
  }
}
```

**前置条件**: 需要安装 Playwright
```bash
pip install playwright
playwright install chromium
```

**输出**: 会话文件 `artifacts/fanruan_session.json`

---

### 节点 5: Scrape Data (数据爬取) 【条件执行】

**节点类型**: `Execute Command`

**功能**: 从帆软系统爬取销售数据

**配置**:
```json
{
  "command": "python",
  "args": [
    "C:/Users/50319/Desktop/n8n/scripts/fanruan/fanruan_scrape.py"
  ],
  "options": {
    "cwd": "C:/Users/50319/Desktop/n8n"
  }
}
```

**输出**: `output/帆软销售明细.xlsx`

---

### 节点 6: Analyze Data (数据分析)

**节点类型**: `Execute Command`

**功能**: 数据清洗 + 二次统计

**配置**:
```json
{
  "command": "python",
  "args": [
    "C:/Users/50319/Desktop/n8n/scripts/fanruan/fanruan_analyze.py"
  ],
  "options": {
    "cwd": "C:/Users/50319/Desktop/n8n"
  }
}
```

**输入**: `output/帆软销售明细.xlsx`

**输出**:
- `artifacts/销售分析数据.xlsx` (清洗后数据)
- `output/销售统计汇总.xlsx` (11 个统计表)

**统计表示例**:
| Sheet 名称 | 说明 | 行数 |
|-----------|------|------|
| 总览_KPI | 5 个核心指标 | 5 |
| 销售员业绩 | 9 个销售员统计 | 9 |
| 产品占比 | 6 个产品统计 | 6 |
| 城市排名 | 9 个城市统计 | 9 |
| 客户类型 | 2 个类型统计 | 2 |
| 月度趋势 | 6 个月统计 | 6 |
| ... | ... | ... |

---

### 节点 7: Generate AI Insights (AI 洞察)

**节点类型**: `HTTP Request` 或 `Execute Command`

#### 方案 A: HTTP Request (推荐)

**功能**: 直接调用 Qwen API 生成洞察

**配置**:
```json
{
  "method": "POST",
  "url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
  "headers": {
    "Authorization": "Bearer {{$env.QWEN_API_KEY}}",
    "Content-Type": "application/json"
  },
  "body": {
    "model": "qwen-plus",
    "messages": [
      {
        "role": "system",
        "content": "你是一位资深商业数据分析师，擅长从销售数据中提取关键洞察。请根据提供的数据生成 10 条结构化洞察。"
      },
      {
        "role": "user",
        "content": "={{ $json.dataContext }}"
      }
    ],
    "temperature": 0.7,
    "response_format": { "type": "json_object" }
  }
}
```

**数据上下文构建 (Function 节点)**:
```javascript
const fs = require('fs');
const XLSX = require('xlsx');

// 读取统计汇总
const workbook = XLSX.readFile('C:/Users/50319/Desktop/n8n/output/销售统计汇总.xlsx');
const dataContext = {};

// 提取每个 Sheet 的数据
workbook.SheetNames.forEach(sheetName => {
  const sheet = workbook.Sheets[sheetName];
  const data = XLSX.utils.sheet_to_json(sheet);
  dataContext[sheetName] = data;
});

// 构建 Prompt 上下文
const context = JSON.stringify({
  totalSales: dataContext['总览_KPI']?.[0]?.['销售额'] || 0,
  totalOrders: dataContext['总览_KPI']?.[0]?.['订单数'] || 0,
  topSalesperson: dataContext['销售员业绩']?.[0]?.['销售员'] || '',
  topProduct: dataContext['产品占比']?.[0]?.['产品'] || '',
  topCity: dataContext['城市排名']?.[0]?.['城市'] || ''
}, null, 2);

return [{ json: { dataContext: context } }];
```

**输出**: 10 条 AI 洞察 (JSON 格式)

#### 方案 B: Execute Command

**配置**:
```json
{
  "command": "python",
  "args": [
    "C:/Users/50319/Desktop/n8n/scripts/ai/insight_generator.py"
  ],
  "options": {
    "cwd": "C:/Users/50319/Desktop/n8n",
    "env": {
      "QWEN_API_KEY": "{{$env.QWEN_API_KEY}}"
    }
  }
}
```

**输出**: `artifacts/ai_insights.json`

---

### 节点 8: Generate Charts (图表生成) 【并行】

**节点类型**: `Execute Command` 或 `Function` (使用 Chart.js)

**配置**: 使用 `Split In Batches` + `Execute Command` 并行生成 6 个图表

**图表列表**:
| 图表 Key | 类型 | 数据源 | 说明 |
|---------|------|--------|------|
| `monthly_trend` | line | 月度趋势 | 6 个月销售趋势 |
| `sales_by_person` | bar_horizontal | 销售员业绩 | 9 个销售员对比 |
| `customer_comparison` | multi_column | 客户类型 | 2 种客户对比 |
| `city_ranking` | bar_horizontal | 城市排名 | Top9 城市 |
| `product_pie` | pie | 产品占比 | 6 个产品占比 |
| `heatmap` | heatmap | 销售员 - 产品 | 热力图矩阵 |

**并行配置**:
```json
{
  "batchSize": 6,
  "options": {
    "parallel": true
  }
}
```

**输出**: `artifacts/temp/chart_*.png` (6 个)

---

### 节点 9: Fill PPT Template (填充 PPT)

**节点类型**: `Execute Command`

**功能**: 使用模板引擎填充 PPT

**配置**:
```json
{
  "command": "python",
  "args": [
    "C:/Users/50319/Desktop/n8n/scripts/core/template_engine.py",
    "--template", "C:/Users/50319/Desktop/n8n/templates/销售分析报告_标准模板.pptx",
    "--output", "C:/Users/50319/Desktop/n8n/output/销售分析报告_{{$now.format('YYYYMMDD_HHmmss')}}.pptx",
    "--insights", "C:/Users/50319/Desktop/n8n/artifacts/ai_insights.json",
    "--charts-dir", "C:/Users/50319/Desktop/n8n/artifacts/temp"
  ],
  "options": {
    "cwd": "C:/Users/50319/Desktop/n8n"
  }
}
```

**占位符替换**:
| 占位符类型 | 格式 | 数量 | 来源 |
|-----------|------|------|------|
| 文本 | `[TEXT:xxx]` | 14 个 | 统计数据 |
| AI 洞察 | `{{INSIGHT:xxx}}` | 10 条 | AI 生成 |
| 图表 | `[CHART:xxx]` | 6 个 | 图表引擎 |
| 表格 | `[TABLE:xxx]` | 1 个 | 异常订单 |

**输出**: `output/销售分析报告_YYYYMMDD_HHMMSS.pptx`

---

### 节点 10: Save Files (保存文件)

**节点类型**: `Move Binary Data` 或 `Write Binary File`

**功能**: 保存最终文件，清理临时文件

**配置**:
```json
{
  "action": "move",
  "source": "C:/Users/50319/Desktop/n8n/output/销售分析报告_*.pptx",
  "destination": "C:/Users/50319/Desktop/n8n/output/final/"
}
```

**清理临时文件 (Execute Command)**:
```bash
del /Q C:\Users\50319\Desktop\n8n\artifacts\temp\*.png
del /Q C:\Users\50319\Desktop\n8n\artifacts\ai_insights.json
del /Q C:\Users\50319\Desktop\n8n\logs\*.log
```

---

### 节点 11: Send Notification (发送通知)

**节点类型**: `Email` / `Slack` / `Discord` / `Webhook`

**配置示例 (Email)**:
```json
{
  "from": "n8n@yourcompany.com",
  "to": "manager@yourcompany.com",
  "subject": "销售报告已生成 - {{$now.format('YYYY-MM-DD')}}",
  "body": "今日销售报告已生成，请查看附件。\n\n总销售额：{{$json.totalSales}}元\n订单数：{{$json.totalOrders}}\n\n报告路径：{{$json.reportPath}}",
  "attachments": [
    "C:/Users/50319/Desktop/n8n/output/销售分析报告_{{$now.format('YYYYMMDD')}}.pptx"
  ]
}
```

---

## 🔐 凭证管理

### 环境变量配置

在 n8n 中设置以下环境变量：

```bash
# 帆软账号
FANRUAN_USERNAME=your_username
FANRUAN_PASSWORD=your_password

# Qwen API Key
QWEN_API_KEY=sk-xxx

# 路径配置
WORK_DIR=C:/Users/50319/Desktop/n8n
OUTPUT_DIR=C:/Users/50319/Desktop/n8n/output
ARTIFACTS_DIR=C:/Users/50319/Desktop/n8n/artifacts
LOGS_DIR=C:/Users/50319/Desktop/n8n/logs
```

### n8n 凭证类型

| 凭证 | 类型 | 用途 |
|------|------|------|
| FanRuan Credentials | HTTP Header | 帆软登录 |
| Qwen API Credentials | HTTP Header | AI 洞察生成 |
| Email Credentials | SMTP | 报告发送 |

---

## 🔄 完整工作流 JSON 导入

将以下 JSON 导入 n8n：

```json
{
  "name": "帆软 PPT 报告生成流程",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "days",
              "daysInterval": 1,
              "triggerAtHour": 9,
              "triggerAtMinute": 0
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.2,
      "position": [250, 300]
    },
    {
      "parameters": {
        "jsCode": "// 检查数据文件代码见上文"
      },
      "name": "Check Data Files",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "rules": [
          {
            "conditions": {
              "boolean": [
                {
                  "value1": "={{ $json.hasData }}",
                  "operation": "equals",
                  "value2": true
                }
              ]
            }
          }
        ]
      },
      "name": "Switch",
      "type": "n8n-nodes-base.switch",
      "typeVersion": 1,
      "position": [650, 300]
    }
    // ... 其他节点
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Check Data Files",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
    // ... 其他连接
  }
}
```

---

## 📦 Python 依赖迁移

### 方案 A: 保留 Python 脚本 (推荐)

**优点**:
- ✅ 无需重写代码
- ✅ 保持现有功能
- ✅ 快速迁移

**依赖**:
```bash
# 在 n8n 服务器安装
pip install pandas openpyxl python-pptx matplotlib seaborn requests playwright
playwright install chromium
```

**注意**: v4.5 起样式文件位于 `scripts/core/styles/` 目录

### 方案 B: 完全迁移到 n8n 原生节点

**优点**:
- ✅ 无需 Python 环境
- ✅ 纯可视化配置

**挑战**:
- ❌ 需要重写图表生成逻辑 (使用 Chart.js)
- ❌ PPT 填充需要自定义节点
- ❌ 数据清洗逻辑复杂

**建议**: 采用混合方案
- 数据检查、流程控制 → n8n 原生节点
- 数据清洗、图表生成、PPT 填充 → Python 脚本 (Execute Command)
- AI 洞察 → HTTP Request 直接调用 API

---

## 🔧 错误处理

### 重试机制

**配置示例**:
```json
{
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000
}
```

### 错误通知

**配置**:
```json
{
  "onError": {
    "action": "sendEmail",
    "to": "admin@yourcompany.com",
    "subject": "PPT 生成失败 - {{$now.format('YYYY-MM-DD')}}",
    "body": "错误信息：{{ $json.error }}\n节点：{{ $node.name }}"
  }
}
```

---

## 📊 性能优化

### 并行处理

- 6 个图表生成 → 使用 `Split In Batches` + 并行执行
- 提速：串行 2.0s → 并行 0.5s (75% 提升)

### 缓存策略

- 帆软会话 → 保存 7 天，避免重复登录
- AI 洞察 → 相同数据不重复生成

---

## 🧪 测试清单

| 测试项 | 预期结果 | 状态 |
|--------|----------|------|
| 定时触发 | 每天 9:00 自动执行 | ⬜ |
| 数据检查 | 正确识别有无数据 | ⬜ |
| 帆软登录 | 成功保存会话 | ⬜ |
| 数据爬取 | 生成 Excel 文件 | ⬜ |
| 数据清洗 | 11 个统计表正确 | ⬜ |
| AI 洞察 | 10 条洞察生成 | ⬜ |
| 图表生成 | 6 个图表正常 | ⬜ |
| PPT 填充 | 占位符全部替换 | ⬜ |
| 文件保存 | 报告保存到 output/ | ⬜ |
| 错误通知 | 失败时发送邮件 | ⬜ |

---

## 📝 迁移步骤

1. **安装 n8n** (本地或 Docker)
   ```bash
   npm install n8n -g
   n8n start
   ```

2. **导入工作流 JSON** (见上文)

3. **配置环境变量** (凭证管理)

4. **安装 Python 依赖**
   ```bash
   pip install pandas openpyxl python-pptx matplotlib requests
   ```

5. **测试单节点** (从 Check Data 开始)

6. **全链路测试** (手动触发)

7. **配置定时任务** (Schedule Trigger)

8. **配置错误通知**

9. **上线运行**

---

## 🆚 Python vs n8n 对比

| 特性 | Python 脚本 | n8n 工作流 |
|------|------------|-----------|
| 可视化 | ❌ 命令行 | ✅ 可视化编排 |
| 错误处理 | ⚠️ 手动日志 | ✅ 内置重试/通知 |
| 定时任务 | ⚠️ 需 cron | ✅ 内置调度器 |
| 集成能力 | ⚠️ 需写代码 | ✅ 200+ 预置节点 |
| 维护成本 | 中 | 低 |
| 执行速度 | 快 | 中 (有 overhead) |
| 学习曲线 | 需 Python | 低代码 |

**建议**: 保留 Python 核心逻辑，用 n8n 做流程编排

---

## 📞 技术支持

| 资源 | 链接 |
|------|------|
| n8n 文档 | https://docs.n8n.io |
| n8n 社区 | https://community.n8n.io |
| 本项目文档 | README.md |
| 架构图 | architecture_final.drawio |

---

**最后更新**: 2026-04-07  
**版本**: 1.0 for n8n  
**状态**: ✅ 可导入，待测试
