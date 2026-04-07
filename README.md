# 帆软数据 → PPT 报告（企业版）

> 📊 **架构**: 模板引擎 + 图表引擎 + AI 洞察  
> **版本**: 4.5 Enterprise  
> **最后更新**: 2026-04-07

---

## 🚀 快速开始

### 📊 配置工具（推荐）⭐

**位置**：`scripts/config_tool/`

**1. 安装依赖（首次使用）**：
```bash
pip install streamlit pandas openpyxl xlsxwriter
```

**2. 启动工具**：
```bash
# 双击运行
scripts\config_tool\streamlit.bat

# 或命令行
streamlit run scripts\config_tool\app.py
```

**3. 浏览器访问**：
```
http://localhost:8501
```

**4. 图形化配置**：
- 📋 统计规则配置
- 📈 图表配置
- 📊 数据预览
- 💾 导出配置

**详细文档**：`scripts/config_tool/README.md`

---

### ⚙️ 配置 API Key

**编辑 `config.ini`**：
```ini
[fanruan]
username = 13021020077
password = YOUR_PASSWORD_HERE  # ← 替换为你的密码

[api_keys]
qwen_api_key = sk-YOUR_API_KEY_HERE  # ← 替换为你的 API Key
```

**获取 API Key**：https://bailian.console.aliyun.com/

---

### ▶️ 运行

```bash
# 双击运行
Run.bat

# 或 PowerShell
.\Run.ps1

# 或 EXE
PPT 生成.exe
```

---

## 📁 目录结构

```
n8n/
├── Run.bat                 # 一键运行
├── Run.ps1                 # 主执行脚本
├── config.ini              # 配置文件
├── config.ini.example      # 配置模板
├── README.md               # 项目文档
├── .gitignore              # Git 配置
│
├── scripts/                # 核心脚本
│   ├── config_tool/        # 📊 配置工具
│   │   ├── app.py
│   │   ├── streamlit.bat
│   │   └── README.md
│   ├── core/               # 核心模块
│   ├── ai/                 # AI 模块
│   └── fanruan/            # 帆软模块
│
├── templates/              # PPT 模板
├── skills/                 # AI 规范
├── docs/                   # 文档
├── output/                 # 输出目录
├── logs/                   # 日志目录
└── artifacts/              # 临时文件
```

---

## 📊 配置工具 - 最佳实践 Demo

### 场景：新增"客户城市分析"图表

**步骤 1：配置统计规则**

打开配置工具 → 📋 统计规则配置

```
表格名称：客户城市分析
统计类型：排名统计
描述：客户属性与城市交叉分析
分组字段：
  客户属性
  城市
统计指标：
  [
    {"field": "销售额", "agg": "sum", "alias": "总销售额"},
    {"field": "订单数", "agg": "count", "alias": "订单数"}
  ]
```

点击"添加统计规则"

---

**步骤 2：配置图表**

打开配置工具 → 📈 图表配置

```
图表 Key：customer_city
图表标题：客户属性与城市销售分析
图表类型：横向条形图
数据源：客户城市分析
X 轴字段：总销售额
Y 轴字段：城市
描述：客户属性与城市交叉分析
```

点击"添加图表配置"

---

**步骤 3：导出配置**

打开配置工具 → 💾 导出配置

- 点击"保存 stats_rules.json"
- 点击"保存 placeholders.json"

---

**步骤 4：配置 PPT 模板**

1. 打开 `templates/销售分析报告_标准模板.pptx`
2. 找到要放置图表的页面
3. 插入文本框
4. 输入：`[CHART:customer_city]`
5. 保存 PPT

---

**步骤 5：运行生成**

```bash
Run.bat
```

**完成！** 🎉

---

## 📋 配置参考

### 图表类型

| 类型 | 用途 | 需要字段 |
|------|------|---------|
| bar_horizontal | 横向条形图 | x_field, y_field |
| bar_vertical | 纵向柱状图 | x_field, y_field |
| pie | 环形饼图 | category_field, value_field |
| column_clustered | 多列柱状图 | category_field, series |
| line | 折线图 | x_field, y_field |
| heatmap | 热力图 | index_field, columns |

### 统计类型

| 类型 | 用途 | 示例 |
|------|------|------|
| kpi | 核心指标汇总 | 总销售额、订单数 |
| ranking | 排名统计 | 销售员 TOP10 |
| composition | 占比分析 | 产品销售占比 |
| comparison | 对比分析 | 新老客对比 |
| trend | 趋势分析 | 月度销售趋势 |
| distribution | 分布分析 | 星期分布 |
| matrix | 矩阵分析 | 销售员 - 产品矩阵 |
| outlier | 异常检测 | 异常订单 |

---

## ❓ 常见问题

**Q: 图表不显示？**  
A: 检查数据源名称是否与统计规则一致

**Q: 字段找不到？**  
A: 在"数据预览"中查看实际生成的字段名

**Q: 如何修改配置？**  
A: 展开配置项，点击"编辑"按钮

**Q: streamlit 未安装？**  
A: 运行 `pip install streamlit`

---

## 📚 文档

| 文档 | 位置 |
|------|------|
| 配置工具说明 | `scripts/config_tool/README.md` |
| Git 配置指南 | `GIT_CONFIG_GUIDE.md` |
| 项目文档 | `README.md` |

---

**最后更新**: 2026-04-07  
**版本**: 4.5 Enterprise  
**状态**: ✅ 生产就绪
