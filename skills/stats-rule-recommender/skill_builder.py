# -*- coding: utf-8 -*-
"""
Skill 构建器 - 根据 stats_rules.json 动态生成 SKILL.md
"""
import json
import os
from datetime import datetime

def build_skill_from_config(stats_rules_path: str, output_path: str):
    """
    根据配置文件动态生成 SKILL.md
    
    Args:
        stats_rules_path: stats_rules.json 路径
        output_path: 生成的 SKILL.md 路径
    """
    
    # 加载配置
    with open(stats_rules_path, 'r', encoding='utf-8') as f:
        stats_config = json.load(f)
    
    # 提取统计表信息
    stats_sheets = stats_config.get('stats_sheets', {})
    
    # 生成 SKILL.md
    skill_content = generate_skill_content(stats_sheets)
    
    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(skill_content)
    
    print(f"[OK] SKILL.md generated: {output_path}")
    print(f"   - Stats tables: {len(stats_sheets)}")


def generate_skill_content(stats_sheets: dict) -> str:
    """生成 SKILL.md 内容"""
    
    # 生成可用统计类型说明
    types_md = ""
    type_examples = {
        'kpi': '核心 KPI - 汇总指标（如总销售额、总订单数）',
        'ranking': '排名统计 - 按维度排名（如销售员排名、城市排名）',
        'composition': '占比分析 - 各部分占比（如产品占比、客户占比）',
        'comparison': '对比分析 - 多维度对比（如新老客对比）',
        'trend': '趋势分析 - 时间趋势（如月度趋势、季度趋势）',
        'distribution': '分布分析 - 数据分布（如星期分布、价格带分布）',
        'matrix': '矩阵分析 - 双维度矩阵（如销售员 - 产品矩阵）',
        'outlier': '异常检测 - 异常值识别（如异常订单）'
    }
    
    for type_key, type_desc in type_examples.items():
        types_md += f"- `{type_key}`: {type_desc}\n"
    
    # 生成当前配置中的统计规则表格
    rules_md = ""
    for sheet_name, config in stats_sheets.items():
        if not config.get('enabled', True):
            continue
        
        rule_type = config.get('type', 'unknown')
        description = config.get('description', '')
        group_by = config.get('group_by', [])
        metrics = config.get('metrics', [])
        
        group_by_str = ', '.join(group_by) if group_by else '-'
        metrics_str = ', '.join([f"{m.get('field')}({m.get('agg')})" for m in metrics])
        
        rules_md += f"| {sheet_name} | {rule_type} | {group_by_str} | {metrics_str} | {description} |\n"
    
    # 生成动态示例
    example_rules = []
    for sheet_name, config in list(stats_sheets.items())[:3]:  # 最多取 3 个示例
        if not config.get('enabled', True):
            continue
        
        example_rules.append({
            "name": sheet_name,
            "type": config.get('type', 'kpi'),
            "enabled": True,
            "description": config.get('description', ''),
            "group_by": config.get('group_by', []),
            "metrics": config.get('metrics', [])
        })
    
    import json
    example_json = json.dumps({"recommendations": example_rules}, ensure_ascii=False, indent=2)
    
    # 生成完整的 SKILL.md
    skill_md = f"""---
name: stats-rule-recommender
description: 统计规则推荐技能（动态版）- 根据 Excel 数据结构推荐统计规则配置
version: 2.0.0-dynamic
author: PPT Report Generator
trigger: 分析 Excel 数据结构，推荐统计规则
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# 统计规则推荐专家（动态配置版）

你是数据分析专家，专门根据 Excel 数据结构推荐合适的统计规则配置。

**重要**：本规范根据实际配置文件动态生成，请严格按照以下规则推荐统计规则。

---

## 📊 输入数据

你的输入包含：

1. **Excel 文件信息**
   - 文件名
   - 列名列表
   - 数据样本（前 5 行）
   - 数据类型推断

2. **可用统计类型**

{types_md}
---

## ✍️ 推荐规则

### 1. 识别数值字段
- 查找所有数值类型的列（如：销售额、订单数、数量、金额等）
- 这些字段适合用于聚合统计（sum/count/mean/max/min）

### 2. 识别分类字段
- 查找所有文本类型的列（如：销售员、产品、城市、客户类型等）
- 这些字段适合用于分组统计（group_by）

### 3. 识别时间字段
- 查找所有日期/时间类型的列（如：订单时间、日期等）
- 这些字段适合用于趋势分析（月度/季度/年度）

### 4. 推荐统计规则

根据字段组合推荐：

| 字段组合 | 推荐统计类型 | 说明 |
|---------|------------|------|
| 数值字段 | kpi | 核心 KPI 统计（总和/平均/最大/最小） |
| 分类字段 + 数值字段 | ranking | 按分类排名（如销售员业绩排名） |
| 分类字段 + 数值字段 | composition | 占比分析（如产品占比） |
| 2 个分类字段 + 数值字段 | comparison | 对比分析（如新老客对比） |
| 时间字段 + 数值字段 | trend | 趋势分析（如月度趋势） |
| 时间字段（星期）+ 数值字段 | distribution | 分布分析（如星期分布） |
| 2 个分类字段 + 数值字段 | matrix | 矩阵分析（如销售员 - 产品矩阵） |
| 数值字段（大数值差异） | outlier | 异常检测（如异常订单） |

---

## 📤 输出格式规范

**必须输出 JSON 格式，包含推荐的统计规则列表！**

### 正确格式

```json
{{
  "recommendations": [
    {{
      "name": "核心 KPI",
      "type": "kpi",
      "enabled": true,
      "description": "核心经营指标汇总",
      "metrics": [
        {{"field": "销售额", "agg": "sum", "alias": "总销售额"}},
        {{"field": "销售额", "agg": "count", "alias": "总订单数"}},
        {{"field": "销售额", "agg": "mean", "alias": "平均客单价"}}
      ]
    }},
    {{
      "name": "销售员业绩",
      "type": "ranking",
      "enabled": true,
      "description": "销售员业绩排名统计",
      "group_by": ["销售员"],
      "metrics": [
        {{"field": "销售额", "agg": "sum", "alias": "总销售额"}},
        {{"field": "销售额", "agg": "count", "alias": "订单数"}}
      ]
    }}
  ]
}}
```

### 关键要求

1. **必须输出 JSON 对象**，包含 `recommendations` 数组
2. **每个推荐**包含：
   - `name`: 统计表格名称（中文，简洁明了）
   - `type`: 统计类型（从可用类型中选择）
   - `enabled`: 是否启用（默认 true）
   - `description`: 描述说明
   - `group_by`: 分组字段列表（ranking/composition 等需要）
   - `metrics`: 指标配置列表

---

## 💡 当前配置示例

当前系统配置了以下统计规则（供参考）：

| 规则名称 | 类型 | 分组字段 | 指标字段 | 描述 |
|---------|------|---------|---------|------|
{rules_md}

### 示例输出

{example_json}

---

## ⚠️ 注意事项

1. **字段名必须与 Excel 列名完全一致**
2. **聚合函数从以下选择**：sum, count, mean, max, min, median
3. **分组字段必须是分类字段**（文本类型）
4. **指标字段必须是数值字段**
5. **不要推荐空配置**（如没有数值字段时不要推荐 kpi）
6. **type 字段必须从可用统计类型中选择**（见上方列表）

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: 2.0.0-dynamic
**状态**: ✅ 动态生成，与实际配置同步
"""
    
    return skill_md


if __name__ == '__main__':
    # 示例用法
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    build_skill_from_config(
        stats_rules_path=os.path.join(base_dir, 'artifacts', 'stats_rules.json'),
        output_path=os.path.join(base_dir, 'skills', 'stats-rule-recommender', 'SKILL.md')
    )
