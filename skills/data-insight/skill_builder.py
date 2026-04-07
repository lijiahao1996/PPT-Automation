# -*- coding: utf-8 -*-
"""
Skill 构建器 - 根据实际图表配置动态生成 SKILL.md
"""
import json
import os
from datetime import datetime

def build_skill_from_config(stats_rules_path: str, placeholders_path: str, output_path: str):
    """
    根据配置文件动态生成 SKILL.md
    
    Args:
        stats_rules_path: stats_rules.json 路径
        placeholders_path: placeholders.json 路径
        output_path: 生成的 SKILL.md 路径
    """
    
    # 加载配置
    with open(stats_rules_path, 'r', encoding='utf-8') as f:
        stats_config = json.load(f)
    
    with open(placeholders_path, 'r', encoding='utf-8') as f:
        placeholders_config = json.load(f)
    
    # 提取统计表信息
    stats_sheets = stats_config.get('stats_sheets', {})
    
    # 提取图表配置
    charts = placeholders_config.get('placeholders', {}).get('charts', {})
    
    # 生成数据结构表格
    data_tables = []
    for sheet_name, config in stats_sheets.items():
        if not config.get('enabled', True):
            continue
        
        description = config.get('description', sheet_name)
        metrics = config.get('metrics', [])
        group_by = config.get('group_by', [])
        
        # 构建字段说明
        fields = []
        if group_by:
            fields.extend(group_by)
        for m in metrics:
            fields.append(m.get('alias', m.get('field')))
        
        data_tables.append({
            'name': sheet_name,
            'description': description,
            'fields': fields
        })
    
    # 生成图表 - 洞察映射
    chart_insight_mapping = []
    for chart_key, chart_config in charts.items():
        chart_name = chart_key.replace('CHART:', '')
        data_source = chart_config.get('data_source', '')
        chart_type = chart_config.get('chart_type', '')
        title = chart_config.get('title', '')
        slide_index = chart_config.get('slide_index', 0)
        
        chart_insight_mapping.append({
            'chart_key': chart_key,
            'chart_name': chart_name,
            'data_source': data_source,
            'chart_type': chart_type,
            'title': title,
            'slide_index': slide_index
        })
    
    # 生成 SKILL.md
    skill_content = generate_skill_content(data_tables, chart_insight_mapping)
    
    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(skill_content)
    
    print(f"OK: SKILL.md generated: {output_path}")
    print(f"   - Stats tables: {len(data_tables)}")
    print(f"   - Charts: {len(chart_insight_mapping)}")


def generate_skill_content(data_tables: list, chart_insight_mapping: list) -> str:
    """生成 SKILL.md 内容"""
    
    # 生成数据结构表格
    tables_md = ""
    for table in data_tables:
        fields_str = "、".join(table['fields'])
        tables_md += f"| {table['name']} | {table['description']} | {fields_str} |\n"
    
    # 生成图表 - 洞察映射
    chart_insight_md = ""
    for i, mapping in enumerate(chart_insight_mapping, 1):
        chart_insight_md += f"#### 第{mapping['slide_index']}页：{mapping['title']}\n"
        chart_insight_md += f"**图表 Key**: `{mapping['chart_key']}`\n"
        chart_insight_md += f"**数据源**: {mapping['data_source']}\n"
        chart_insight_md += f"**图表类型**: {mapping['chart_type']}\n"
        chart_insight_md += f"**分析要点**:\n"
        chart_insight_md += f"- 基于{mapping['data_source']}数据生成洞察\n"
        chart_insight_md += f"- 分析趋势、对比、占比等业务含义\n"
        chart_insight_md += f"- 给出具体数据和业务建议\n\n"
    
    # 生成完整的 SKILL.md
    skill_md = f"""---
name: data-insight
description: 销售数据洞察生成规范（动态版）- 根据实际图表配置生成洞察
version: 3.1.0-dynamic
author: Senior Data Analyst
trigger: 生成销售洞察，分析销售数据，PPT 洞察填充
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# 销售数据洞察专家（动态配置版）

你是高级数据分析师，专门为销售分析报告生成 PPT 洞察文案。

**重要**：本规范根据实际配置文件动态生成，请严格按照以下数据结构和分析要求生成洞察。

---

## 📊 已知数据结构

你的输入包含以下统计表：

| Sheet 名称 | 内容说明 | 关键字段 |
|-----------|---------|---------|
{tables_md}
---

## ✍️ 洞察生成核心规则

### 1. 必须用数据说话
- ❌ 错误："销售额表现良好"
- ✅ 正确："Q2 销售额 21.3 万元，环比 Q1 增长 190%"

### 2. 必须有对比
- 同比/环比、目标 vs 实际、头部 vs 尾部、实际 vs 平均

### 3. 必须具体
- 精确到具体数字、具体人名、具体产品、具体城市

### 4. 必须有洞察
- 不仅描述"是什么"，还要指出"为什么"和"意味着什么"

### 5. 文案质量要求 ⭐⭐⭐⭐⭐

#### 字数要求（严格执行）
- **第 1 页（核心指标）**: 120-180 字
- **其他页（图表洞察）**: 每条 50-100 字，3 条合计 150-300 字
- **核心结论页**: 每段 60-100 字，4 段合计 240-400 字
- **落地策略页**: 每段 80-120 字，4 段合计 320-480 字

#### 内容要求
- 使用完整句子，不要简单罗列数据
- 包含**数据 + 对比 + 洞察**三层结构
- 避免"显著"、"明显"等模糊词汇，用具体倍数/百分比
- 每条洞察必须有**业务含义**或**行动建议**

---

## 📤 输出格式规范（重要！）

### ⚠️ 严格输出格式 - 必须遵守！

**必须输出 JSON 数组，每个元素对应一个图表的洞察！**

❌ **错误格式**（会导致解析失败）:
```json
[
  "第 1 页洞察",
  ["• 第 2 页洞察 1", "• 第 2 页洞察 2", "• 第 2 页洞察 3"],
  ...
]
```

✅ **正确格式**（必须这样输出）:
```json
[
  "第 1 页洞察（单条，100-150 字）",
  "• 第 2 页洞察 1\\n• 第 2 页洞察 2\\n• 第 2 页洞察 3",
  "• 第 3 页洞察 1\\n• 第 3 页洞察 2\\n• 第 3 页洞察 3",
  ...
]
```

### 关键要求

1. **数组元素数量 = 图表数量**
2. **不能嵌套数组**，所有洞察都必须是字符串
3. 列表式洞察用 `\\n` 连接 3 条，如：`"• 洞察 1\\n• 洞察 2\\n• 洞察 3"`
4. 结构化洞察用 `\\n\\n` 分隔 4 个段落
5. 直接输出 JSON 数组，不要任何其他文字

---

## 📊 图表 - 洞察映射

根据当前配置，需要生成以下洞察：

{chart_insight_md}
---

## 🔧 技术实现要求

### JSON 输出格式

```json
[
  "总销售额 285,696 元中，Q2 贡献...（100-150 字）",
  "• 孙林以 39,601 元总销售额位列业绩 TOP1...\\n• TOP3 销售员贡献了全团队 39% 的销售额...\\n• 头部销售员客单价显著高于团队平均水平...",
  ...
]
```

### 注意事项

1. 所有数字使用阿拉伯数字，千位加分隔符（如 39,601）
2. 百分比保留 1 位小数（如 34.2%）
3. 金额单位统一用"元"或"万元"
4. 人名、产品名、城市名必须与数据一致
5. 列表式洞察用 `•` 符号，每条换行
6. 结构化洞察用小标题 + 冒号格式

---

## 💡 最佳实践示例

### 优秀洞察特征

✅ **数据准确**: "销售额 285,696 元，环比增长 190%"
✅ **对比清晰**: "是老客的 3 倍，超出平均值 45%"
✅ **洞察深入**: "依赖大单明显，业绩结构存在风险"
✅ **建议具体**: "建议通过组合捆绑提升连带率"

### 错误示例

❌ **模糊**: "销售额表现良好"
❌ **无对比**: "孙林销售额最高"
❌ **无洞察**: "牛肉干占比 34.2%"
❌ **建议空洞**: "需要提升销售"

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: 3.1.0-dynamic
**状态**: ✅ 动态生成，与实际配置同步
"""
    
    return skill_md


if __name__ == '__main__':
    # 示例用法
    base_dir = r"C:\Users\50319\Desktop\n8n"
    build_skill_from_config(
        stats_rules_path=os.path.join(base_dir, 'templates', 'stats_rules.json'),
        placeholders_path=os.path.join(base_dir, 'templates', 'placeholders.json'),
        output_path=os.path.join(base_dir, 'skills', 'data-insight', 'SKILL.md')
    )
