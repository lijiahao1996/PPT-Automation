# data-insight Skill 规范

> 📊 动态洞察生成规范 - 根据实际图表配置自动生成

---

## 🎯 功能说明

本 Skill 规范用于指导 AI 生成 PPT 洞察文案，具有以下特点：

### ✅ 动态生成

- **自动检测图表配置**：根据 `templates/placeholders.json` 动态生成
- **图表 - 洞察一一映射**：每个图表对应一条洞察
- **配置更新自动重建**：图表配置变化时自动重新生成 SKILL.md

### ✅ 灵活适配

- **不限制统计表数量**：支持任意数量的统计表
- **不限制图表数量**：支持任意数量的图表
- **不限制 PPT 页面**：根据实际配置动态调整

---

## 📁 文件结构

```
skills/data-insight/
├── SKILL.md              # 洞察生成规范（动态生成）
├── skill_builder.py      # SKILL 构建器（自动生成 SKILL.md）
└── README.md             # 本文件
```

---

## 🔄 工作流程

```
1. 运行 Run.bat
   ↓
2. generate_report.py 检测图表配置
   ↓
3. 如果配置变化 → 运行 skill_builder.py
   ↓
4. 生成新的 SKILL.md
   ↓
5. insight_generator.py 读取 SKILL.md
   ↓
6. 调用 Qwen API 生成洞察
   ↓
7. 填充 PPT
```

---

## 📊 配置文件

### templates/placeholders.json

定义图表配置，格式：

```json
{
  "placeholders": {
    "charts": {
      "CHART:customer_city": {
        "data_source": "客户城市分析",
        "chart_type": "bar_horizontal",
        "x_field": "总销售额",
        "y_field": "城市",
        "title": "客户属性与城市销售分析",
        "slide_index": 9
      }
    }
  }
}
```

### templates/stats_rules.json

定义统计规则，格式：

```json
{
  "stats_sheets": {
    "客户城市分析": {
      "description": "客户属性与城市交叉分析",
      "type": "ranking",
      "enabled": true,
      "group_by": ["客户属性", "城市"],
      "metrics": [
        {"field": "销售额", "agg": "sum", "alias": "总销售额"}
      ]
    }
  }
}
```

---

## 🔧 修改配置

### 新增图表

1. **在 stats_rules.json 中添加统计规则**
2. **在 placeholders.json 中添加图表配置**
3. **运行 Run.bat**（自动重新生成 SKILL.md）

### 修改图表

1. **编辑 placeholders.json 中的图表配置**
2. **运行 Run.bat**（自动重新生成 SKILL.md）

### 删除图表

1. **在 placeholders.json 中删除图表配置**
2. **运行 Run.bat**（自动重新生成 SKILL.md）

---

## 💡 最佳实践

### 图表命名规范

- **格式**: `CHART:{图表名称}`
- **示例**: `CHART:sales_by_person`
- **建议**: 使用英文下划线命名

### 数据源匹配

- **必须一致**: 图表的 `data_source` 必须与 stats_rules.json 中的 Sheet 名称一致
- **示例**: 
  - stats_rules.json: `"客户城市分析"`
  - placeholders.json: `"data_source": "客户城市分析"`

### 洞察质量

- **数据准确**: 基于实际数据，不虚构
- **对比清晰**: 包含同比/环比/头部尾部对比
- **洞察深入**: 指出"为什么"和"意味着什么"
- **建议具体**: 给出可执行的业务建议

---

## 📚 相关文档

| 文档 | 位置 |
|------|------|
| 图表类型说明 | `scripts/config_tool/图表类型说明.md` |
| 配置工具文档 | `scripts/config_tool/README.md` |
| 项目文档 | `README.md` |

---

**最后更新**: 2026-04-08  
**版本**: 3.1.0-dynamic  
**状态**: ✅ 动态生成，与实际配置同步
