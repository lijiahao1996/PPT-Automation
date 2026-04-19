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
    
    # 16 种图表类型及其需要的统计数据结构
    # AI 根据实际 Sheet 的列字段自动判断适合什么图表
    chart_data_requirements = {
        'bar_horizontal': {
            'name': '横向条形图',
            'description': '适合排名对比',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段',
            'example': '销售员 | 总销售额',
            'field_mapping': {'y_field': '分类列', 'x_field': '数值列'}
        },
        'bar_vertical': {
            'name': '纵向柱状图',
            'description': '适合指标对比',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段',
            'example': '指标名称 | 指标值',
            'field_mapping': {'x_field': '分类列', 'y_field': '数值列'}
        },
        'pie': {
            'name': '环形饼图',
            'description': '适合占比分析',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段',
            'example': '产品类别 | 销售额',
            'field_mapping': {'category_field': '分类列', 'value_field': '数值列'}
        },
        'line': {
            'name': '折线图',
            'description': '适合趋势分析',
            'data_structure': '需要 2+ 列：1个时间字段 + 1或多个数值字段',
            'example': '年月 | 总销售额, 订单数',
            'field_mapping': {'x_field': '时间列', 'y_field': '数值列（可多个）'}
        },
        'column_clustered': {
            'name': '多列柱状图',
            'description': '适合多系列对比',
            'data_structure': '需要 3+ 列：1个分类字段 + 2或多个数值字段',
            'example': '性别 | 平均年龄, 平均月薪, 平均消费次数',
            'field_mapping': {'category_field': '分类列', 'series': '数值列列表'}
        },
        'heatmap': {
            'name': '热力图',
            'description': '适合矩阵分析（二维交叉）',
            'data_structure': '需要 3+ 列：1个行分类 + 多个列分类（会自动透视）',
            'example': '销售员 | 产品A, 产品B, 产品C',
            'field_mapping': {'y_field': '行分类列'}
        },
        'scatter': {
            'name': '散点图',
            'description': '适合相关性分析',
            'data_structure': '需要 2 列：2个数值字段',
            'example': '单价 | 销量',
            'field_mapping': {'x_field': 'X轴数值', 'y_field': 'Y轴数值'}
        },
        'histogram': {
            'name': '直方图',
            'description': '适合分布分析',
            'data_structure': '需要 1 列：1个数值字段（使用原始数据，不是统计汇总）',
            'example': '年龄',
            'field_mapping': {'field': '数值列'}
        },
        'boxplot': {
            'name': '箱线图',
            'description': '适合异常检测',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段',
            'example': '部门 | 薪资',
            'field_mapping': {'category_field': '分类列', 'value_field': '数值列'}
        },
        'violin': {
            'name': '小提琴图',
            'description': '适合分布密度',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段',
            'example': '班级 | 成绩',
            'field_mapping': {'category_field': '分类列', 'value_field': '数值列'}
        },
        'bubble': {
            'name': '气泡图',
            'description': '适合三维数据',
            'data_structure': '需要 3 列：3个数值字段',
            'example': '市场份额 | 增长率 | 营收规模',
            'field_mapping': {'x_field': 'X轴数值', 'y_field': 'Y轴数值', 'size_field': '气泡大小'}
        },
        'area': {
            'name': '面积图',
            'description': '适合累计趋势',
            'data_structure': '需要 2+ 列：1个时间字段 + 1或多个数值字段',
            'example': '月份 | 产品收入, 服务收入',
            'field_mapping': {'x_field': '时间列', 'y_field': '数值列列表'}
        },
        'errorbar': {
            'name': '误差棒图',
            'description': '适合误差分析',
            'data_structure': '需要 3 列：1个分类 + 1个数值 + 1个误差',
            'example': '实验组 | 平均值 | 标准差',
            'field_mapping': {'x_field': '分类列', 'y_field': '数值列', 'error_field': '误差列'}
        },
        'polar': {
            'name': '极坐标图',
            'description': '适合周期数据',
            'data_structure': '需要 2 列：1个角度字段 + 1个半径字段',
            'example': '月份角度 | 销售额',
            'field_mapping': {'x_field': '角度列', 'y_field': '半径列'}
        },
        'waterfall': {
            'name': '瀑布图',
            'description': '适合增减分析',
            'data_structure': '需要 2 列：1个分类字段 + 1个数值字段（正负）',
            'example': '项目 | 变动金额',
            'field_mapping': {'category_field': '分类列', 'value_field': '数值列'}
        },
        'funnel': {
            'name': '漏斗图',
            'description': '适合流程转化',
            'data_structure': '需要 2 列：1个阶段字段 + 1个数值字段（递减）',
            'example': '阶段 | 用户数',
            'field_mapping': {'category_field': '阶段列', 'value_field': '数值列'}
        }
    }
    
    # 生成统计规则表格（不推荐具体图表，让 AI 自由选择）
    rules_md = ""
    for sheet_name, config in stats_sheets.items():
        if not config.get('enabled', True):
            continue
        
        stat_type = config.get('type', 'unknown')
        group_by = config.get('group_by', [])
        metrics = config.get('metrics', [])
        
        group_by_str = ', '.join(group_by) if group_by else '-'
        metrics_str = ', '.join([f"{m.get('alias', m.get('field'))}" for m in metrics])
        
        rules_md += f"| {sheet_name} | {stat_type} | {group_by_str} | {metrics_str} |\n"
    
    # 生成图表数据要求表格（16种图表）
    chart_requirements_md = ""
    for chart_type, req in chart_data_requirements.items():
        chart_requirements_md += f"#### {chart_type} - {req['name']}\n"
        chart_requirements_md += f"- **用途**：{req['description']}\n"
        chart_requirements_md += f"- **数据结构**：{req['data_structure']}\n"
        chart_requirements_md += f"- **示例**：{req['example']}\n"
        # 转义 field_mapping 中的花括号
        field_mapping_str = ', '.join([f"{k}={v}" for k,v in req['field_mapping'].items()])
        field_mapping_escaped = field_mapping_str.replace('{', '{{').replace('}', '}}')
        chart_requirements_md += f"- **字段映射**：{field_mapping_escaped}\n\n"
    
    # 生成示例图表配置（多样化示例，不局限于固定映射）
    example_charts = []
    
    # 示例 1: 条形图（排名）
    example_charts.append({
        "chart_key": "salesperson_ranking",
        "chart_type": "bar_horizontal",
        "title": "销售员业绩排名",
        "data_source": "按销售员排名",
        "render_mode": "native",
        "x_field": "总销售额",
        "y_field": "销售员",
        "reason": "排名适合用横向条形图对比"
    })
    
    # 示例 2: 饼图（占比）
    example_charts.append({
        "chart_key": "city_composition",
        "chart_type": "pie",
        "title": "城市销售占比",
        "data_source": "按城市占比",
        "render_mode": "native",
        "category_field": "城市",
        "value_field": "城市销售额",
        "reason": "占比适合用饼图展示"
    })
    
    # 示例 3: 折线图（趋势）
    example_charts.append({
        "chart_key": "monthly_trend",
        "chart_type": "line",
        "title": "月度销售趋势",
        "data_source": "月度销售趋势",
        "render_mode": "native",
        "x_field": "年月",
        "y_field": "总销售额",
        "reason": "趋势适合用折线图展示"
    })
    
    # 示例 4: 热力图（矩阵）
    example_charts.append({
        "chart_key": "product_matrix",
        "chart_type": "heatmap",
        "title": "产品-销售员销售矩阵",
        "data_source": "销售员-产品矩阵",
        "render_mode": "image",
        "y_field": "销售员",
        "reason": "矩阵数据适合用热力图展示二维对比"
    })
    
    import json as json_lib
    example_json = json_lib.dumps({"chart_recommendations": example_charts}, ensure_ascii=False, indent=2) if example_charts else "{}"
    
    # 生成完整的 SKILL.md
    skill_md = """---
name: chart-config-recommender
description: 图表配置推荐技能（动态版）- 根据统计规则推荐合适的图表配置
version: 2.0.0-dynamic
author: PPT Report Generator
trigger: 根据统计规则推荐图表配置
generated_at: {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
---

# 图表配置推荐专家（动态配置版）

你是数据可视化专家，专门根据统计规则推荐合适的图表配置。

**重要**：本规范根据实际配置文件动态生成，请严格按照以下规则推荐图表。

---

## 📊 当前统计 Sheet 数据

| 统计名称 | 统计类型 | 分组字段 | 指标字段 |
|---------|---------|---------|---------|
{rules_md}
---

## 🎯 16 种图表类型及其数据要求

**根据 Sheet 的列字段，选择最适合的图表类型：**

{chart_requirements_md}
---

---

## 🎨 所有支持的图表类型（16种）

AI 可以根据数据特征自由选择最合适的图表类型：

### 基础图表（6种）

#### 1. `bar_horizontal` - 横向条形图（适合排名对比）
**JSON 配置格式：**
```json
{{
  "chart_key": "salesperson_ranking",
  "chart_type": "bar_horizontal",
  "title": "销售员业绩排名",
  "data_source": "按销售员排名",
  "render_mode": "native",
  "x_field": "总销售额",
  "y_field": "销售员"
}}
```
**参数说明：**
- `x_field`: 数值字段（条形长度）
- `y_field`: 分类字段（Y 轴标签）

#### 2. `bar_vertical` - 纵向柱状图（适合指标对比）
**JSON 配置格式：**
```json
{{
  "chart_key": "core_kpi",
  "chart_type": "bar_vertical",
  "title": "核心 KPI 对比",
  "data_source": "核心 KPI",
  "render_mode": "native",
  "x_field": "指标名称",
  "y_field": "指标值"
}}
```
**参数说明：**
- `x_field`: 分类字段（X 轴标签）
- `y_field`: 数值字段（柱子高度）

#### 3. `pie` - 环形饼图（适合占比分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "city_composition",
  "chart_type": "pie",
  "title": "城市销售占比",
  "data_source": "按城市占比",
  "render_mode": "native",
  "category_field": "城市",
  "value_field": "城市销售额"
}}
```
**参数说明：**
- `category_field`: 分类字段（扇区标签）
- `value_field`: 数值字段（扇区大小）

#### 4. `line` - 折线图（适合趋势分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "monthly_trend",
  "chart_type": "line",
  "title": "月度销售趋势",
  "data_source": "月度销售趋势",
  "render_mode": "native",
  "x_field": "年月",
  "y_field": "月度总销售额"
}}
```
**参数说明：**
- `x_field`: 时间/顺序字段（X 轴）
- `y_field`: 数值字段（支持多指标，可用逗号分隔）

#### 5. `heatmap` - 热力图（适合矩阵数据、二维对比）
**JSON 配置格式：**
```json
{{
  "chart_key": "product_matrix",
  "chart_type": "heatmap",
  "title": "产品-销售员销售矩阵",
  "data_source": "销售员-产品矩阵",
  "render_mode": "image",
  "y_field": "销售员"
}}
```
**参数说明：**
- `y_field`: 行字段（Y 轴标签）
- **注意**：columns（列字段）会自动从数据中提取（排除 y_field 列后的所有列）
- **不要配置** x_field、value_field、category_field

#### 6. `column_clustered` / `multi_column` - 分组柱状图（适合多系列对比）
**JSON 配置格式：**
```json
{{
  "chart_key": "product_comparison",
  "chart_type": "column_clustered",
  "title": "产品销售对比",
  "data_source": "按产品销售对比",
  "render_mode": "native",
  "category_field": "产品类别",
  "series": ["销售额", "订单数", "客户数"]
}}
```
**参数说明：**
- `category_field`: 分类字段（X 轴分组）
- `series`: 数值字段列表（每个系列一个柱子）

### 分布图表（5种）

#### 7. `scatter` - 散点图（适合相关性分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "price_sales_correlation",
  "chart_type": "scatter",
  "title": "价格与销量相关性",
  "data_source": "产品销售数据",
  "render_mode": "image",
  "x_field": "单价",
  "y_field": "销量"
}}
```
**参数说明：**
- `x_field`: X 轴数值字段
- `y_field`: Y 轴数值字段

#### 8. `histogram` - 直方图（适合分布分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "age_distribution",
  "chart_type": "histogram",
  "title": "年龄分布",
  "data_source": "客户数据",
  "render_mode": "image",
  "field": "年龄"
}}
```
**参数说明：**
- `field`: 数值字段（分析分布的字段，注意：不是 y_field）
- bins: 可选，默认 20

#### 9. `boxplot` - 箱线图（适合异常值检测）
**JSON 配置格式：**
```json
{{
  "chart_key": "salary_by_department",
  "chart_type": "boxplot",
  "title": "各部门薪资分布",
  "data_source": "部门薪资数据",
  "render_mode": "image",
  "category_field": "部门",
  "value_field": "薪资"
}}
```
**参数说明：**
- `category_field`: 分类字段（每个箱子一个类别）
- `value_field`: 数值字段（分析分布的值）

#### 10. `violin` - 小提琴图（适合分布密度）
**JSON 配置格式：**
```json
{{
  "chart_key": "score_by_class",
  "chart_type": "violin",
  "title": "各班成绩分布",
  "data_source": "学生成绩数据",
  "render_mode": "image",
  "category_field": "班级",
  "value_field": "成绩"
}}
```
**参数说明：**
- `category_field`: 分类字段
- `value_field`: 数值字段

#### 11. `bubble` - 气泡图（适合三维数据）
**JSON 配置格式：**
```json
{{
  "chart_key": "market_analysis",
  "chart_type": "bubble",
  "title": "市场分析",
  "data_source": "市场数据",
  "render_mode": "image",
  "x_field": "市场份额",
  "y_field": "增长率",
  "size_field": "营收规模"
}}
```
**参数说明：**
- `x_field`: X 轴数值字段
- `y_field`: Y 轴数值字段
- `size_field`: 气泡大小字段

### 高级图表（5种）

#### 12. `area` - 面积图（适合累计趋势）
**JSON 配置格式：**
```json
{{
  "chart_key": "revenue_trend",
  "chart_type": "area",
  "title": "收入趋势",
  "data_source": "月度收入数据",
  "render_mode": "image",
  "x_field": "月份",
  "y_field": ["产品收入", "服务收入", "其他收入"]
}}
```
**参数说明：**
- `x_field`: 时间/顺序字段
- `y_field`: 数值字段列表（多个系列叠加）

#### 13. `errorbar` - 误差棒图（适合误差分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "experiment_results",
  "chart_type": "errorbar",
  "title": "实验结果",
  "data_source": "实验数据",
  "render_mode": "image",
  "x_field": "实验组",
  "y_field": "平均值",
  "error_field": "标准差"
}}
```
**参数说明：**
- `x_field`: 分类字段
- `y_field`: 数值字段（主值）
- `error_field`: 误差字段（误差棒长度）

#### 14. `polar` - 极坐标图（适合周期数据）
**JSON 配置格式：**
```json
{{
  "chart_key": "seasonal_sales",
  "chart_type": "polar",
  "title": "季节性销售",
  "data_source": "月度销售数据",
  "render_mode": "image",
  "x_field": "月份角度",
  "y_field": "销售额"
}}
```
**参数说明：**
- `x_field`: 角度字段（0-360 度）
- `y_field`: 半径字段（距离中心的距离）

#### 15. `waterfall` - 瀑布图（适合增减分析）
**JSON 配置格式：**
```json
{{
  "chart_key": "profit_waterfall",
  "chart_type": "waterfall",
  "title": "利润增减分析",
  "data_source": "利润数据",
  "render_mode": "image",
  "category_field": "项目",
  "value_field": "变动金额"
}}
```
**参数说明：**
- `category_field`: 分类字段（每个步骤）
- `value_field`: 数值字段（正数增加，负数减少）

#### 16. `funnel` - 漏斗图（适合流程转化）
**JSON 配置格式：**
```json
{{
  "chart_key": "conversion_funnel",
  "chart_type": "funnel",
  "title": "转化漏斗",
  "data_source": "转化数据",
  "render_mode": "image",
  "category_field": "阶段",
  "value_field": "用户数"
}}
```
**参数说明：**
- `category_field`: 阶段字段（漏斗层级）
- `value_field`: 数值字段（每层级的值，从上到下递减）

---

## 📤 输出格式规范

**必须输出 JSON 格式，包含推荐的图表配置列表！**

### 正确格式

```json
{{{{
  "chart_recommendations": [
    {{{{
      "chart_key": "sales_by_person",
      "chart_type": "bar_horizontal",
      "title": "销售员业绩分析",
      "data_source": "销售员业绩",
      "x_field": "总销售额",
      "y_field": "销售员",
      "reason": "排名适合用横向条形图对比"
    }}}},
    {{{{
      "chart_key": "product_pie",
      "chart_type": "pie",
      "title": "产品销售占比分析",
      "data_source": "产品占比",
      "category_field": "产品",
      "value_field": "销售额",
      "reason": "占比适合用饼图/环形图展示"
    }}}}
  ]
}}}}
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
4. **图表类型必须从 16 种支持的类型中选择**
5. **灵活选择图表**：
   - 不要被固定映射限制
   - 根据数据特征选择最合适的图表
   - 同一统计类型可以用不同图表展示
   - 尝试使用多样化图表（不要总是用相同的）
6. **render_mode 选择**：
   - 简单图表（柱状图、条形图、饼图、折线图）→ 优先 native
   - 复杂图表（热力图、箱线图、瀑布图等）→ 使用 image

---

**最后更新**: {generated_at}
**版本**: 2.0.0-dynamic
**状态**: ✅ 动态生成，与统计规则配置同步
""".format(
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        rules_md=rules_md,
        chart_requirements_md=chart_requirements_md,
        example_json=example_json
    )
    
    return skill_md


if __name__ == '__main__':
    # 示例用法
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    build_skill_from_config(
        stats_rules_path=os.path.join(base_dir, 'artifacts', 'stats_rules.json'),
        output_path=os.path.join(base_dir, 'skills', 'chart-config-recommender', 'SKILL.md')
    )
