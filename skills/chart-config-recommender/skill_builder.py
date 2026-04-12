# -*- coding: utf-8 -*-
"""
Skill 构建器 - 根据 stats_rules.json 动态生成 chart-config-recommender SKILL.md
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
    
    print(f"[OK] chart-config-recommender SKILL.md generated: {output_path}")
    print(f"   - Stats tables: {len(stats_sheets)}")


def generate_skill_content(stats_sheets: dict) -> str:
    """生成 SKILL.md 内容"""
    
    # 生成图表类型映射（基于统计类型）
    chart_type_mapping = {
        'kpi': {'type': 'text', 'name': '文本卡片', 'reason': 'KPI 适合用文本卡片展示核心指标'},
        'ranking': {'type': 'bar_horizontal', 'name': '横向条形图', 'reason': '排名适合用横向条形图对比'},
        'composition': {'type': 'pie', 'name': '环形饼图', 'reason': '占比适合用饼图/环形图展示'},
        'comparison': {'type': 'column_clustered', 'name': '分组柱状图', 'reason': '对比适合用分组柱状图'},
        'trend': {'type': 'line', 'name': '折线图', 'reason': '趋势适合用折线图展示'},
        'distribution': {'type': 'histogram', 'name': '直方图', 'reason': '分布适合用直方图展示'},
        'matrix': {'type': 'heatmap', 'name': '热力图', 'reason': '矩阵适合用热力图展示'},
        'outlier': {'type': 'boxplot', 'name': '箱线图', 'reason': '异常检测适合用箱线图'}
    }
    
    # 生成图表推荐规则表格
    rules_md = ""
    for sheet_name, config in stats_sheets.items():
        if not config.get('enabled', True):
            continue
        
        stat_type = config.get('type', 'unknown')
        chart_info = chart_type_mapping.get(stat_type, {'type': 'bar_vertical', 'name': '柱状图', 'reason': '默认柱状图'})
        
        group_by = config.get('group_by', [])
        metrics = config.get('metrics', [])
        
        group_by_str = ', '.join(group_by) if group_by else '-'
        metrics_str = ', '.join([f"{m.get('alias', m.get('field'))}" for m in metrics])
        
        rules_md += f"| {sheet_name} | {stat_type} | {chart_info['name']} | {group_by_str} | {metrics_str} |\n"
    
    # 生成示例图表配置
    example_charts = []
    for sheet_name, config in list(stats_sheets.items())[:3]:  # 最多取 3 个示例
        if not config.get('enabled', True):
            continue
        
        stat_type = config.get('type', 'unknown')
        chart_info = chart_type_mapping.get(stat_type, {'type': 'bar_vertical'})
        
        chart_rec = {
            "chart_key": sheet_name.replace(' ', '_').lower(),
            "chart_type": chart_info['type'],
            "title": f"{sheet_name}分析",
            "data_source": sheet_name,
            "reason": chart_info['reason']
        }
        
        # 根据统计类型添加字段配置
        if stat_type == 'ranking':
            chart_rec['x_field'] = config.get('metrics', [{}])[0].get('alias', '总销售额')
            chart_rec['y_field'] = config.get('group_by', [''])[0] if config.get('group_by') else ''
        elif stat_type == 'composition':
            chart_rec['category_field'] = config.get('group_by', [''])[0] if config.get('group_by') else ''
            chart_rec['value_field'] = config.get('metrics', [{}])[0].get('alias', '销售额')
        elif stat_type == 'trend':
            chart_rec['x_field'] = '年月'
            chart_rec['y_field'] = config.get('metrics', [{}])[0].get('alias', '总销售额')
        
        example_charts.append(chart_rec)
    
    import json as json_lib
    example_json = json_lib.dumps({"chart_recommendations": example_charts}, ensure_ascii=False, indent=2) if example_charts else "{}"
    
    # 生成完整的 SKILL.md
    skill_md = f"""---
name: chart-config-recommender
description: 图表配置推荐技能（动态版）- 根据统计规则推荐合适的图表配置
version: 2.0.0-dynamic
author: PPT Report Generator
trigger: 根据统计规则推荐图表配置
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# 图表配置推荐专家（动态配置版）

你是数据可视化专家，专门根据统计规则推荐合适的图表配置。

**重要**：本规范根据实际配置文件动态生成，请严格按照以下规则推荐图表。

---

## 📊 当前统计规则配置

系统已配置以下统计规则，请为每个规则推荐合适的图表：

| 统计名称 | 统计类型 | 推荐图表 | 分组字段 | 指标字段 |
|---------|---------|---------|---------|---------|
{rules_md}
---

## 📈 图表类型映射规则

根据统计类型自动推荐图表：

| 统计类型 | 推荐图表 | 说明 |
|---------|---------|------|
| kpi | text | 核心 KPI 适合用文本卡片展示 |
| ranking | bar_horizontal | 排名适合用横向条形图对比 |
| composition | pie | 占比适合用饼图/环形图展示 |
| comparison | column_clustered | 对比适合用分组柱状图 |
| trend | line | 趋势适合用折线图展示 |
| distribution | histogram | 分布适合用直方图展示 |
| matrix | heatmap | 矩阵适合用热力图展示 |
| outlier | boxplot | 异常检测适合用箱线图 |

---

## 📤 输出格式规范

**必须输出 JSON 格式，包含推荐的图表配置列表！**

### 正确格式

```json
{{
  "chart_recommendations": [
    {{
      "chart_key": "sales_by_person",
      "chart_type": "bar_horizontal",
      "title": "销售员业绩分析",
      "data_source": "销售员业绩",
      "x_field": "总销售额",
      "y_field": "销售员",
      "reason": "排名适合用横向条形图对比"
    }},
    {{
      "chart_key": "product_pie",
      "chart_type": "pie",
      "title": "产品销售占比分析",
      "data_source": "产品占比",
      "category_field": "产品",
      "value_field": "销售额",
      "reason": "占比适合用饼图/环形图展示"
    }}
  ]
}}
```

### 关键要求

1. **必须输出 JSON 对象**，包含 `chart_recommendations` 数组
2. **每个推荐**包含：
   - `chart_key`: 图表唯一标识（英文，下划线分隔）
   - `chart_type`: 图表类型（从映射表中选择）
   - `title`: 图表标题
   - `data_source`: 数据源（对应统计规则名称）
   - `reason`: 推荐原因
   - 根据图表类型添加对应字段：
     - 条形图/柱状图：`x_field`, `y_field`
     - 饼图：`category_field`, `value_field`
     - 折线图：`x_field`（时间）, `y_field`（指标）

---

## 💡 基于当前配置的推荐示例

{example_json}

---

## 🎨 图表渲染模式

推荐时需考虑渲染模式：

- **🖼️ 图片方式**：支持所有 17 种图表类型，不可编辑
- **📊 原生方式**：仅支持 5 种基础图表（柱状图、条形图、饼图、折线图、面积图），可在 PPT 中编辑

**推荐策略**：
- 简单图表（柱状图、条形图、饼图、折线图）→ 优先推荐原生方式
- 复杂图表（热力图、箱线图、瀑布图等）→ 使用图片方式

---

## ⚠️ 注意事项

1. **chart_key 必须是英文**，使用下划线分隔
2. **data_source 必须与统计规则名称一致**
3. **字段名必须与统计结果的列名一致**
4. **图表类型必须从映射表中选择**
5. **优先推荐业务价值高的图表**：
   - 核心 KPI → 文本卡片
   - 排名 → 横向条形图
   - 占比 → 环形饼图
   - 趋势 → 折线图

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: 2.0.0-dynamic
**状态**: ✅ 动态生成，与统计规则配置同步
"""
    
    return skill_md


if __name__ == '__main__':
    # 示例用法
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    build_skill_from_config(
        stats_rules_path=os.path.join(base_dir, 'artifacts', 'stats_rules.json'),
        output_path=os.path.join(base_dir, 'skills', 'chart-config-recommender', 'SKILL.md')
    )
