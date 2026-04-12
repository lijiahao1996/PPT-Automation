# -*- coding: utf-8 -*-
"""
Skill 构建器 - 根据上传的 Excel 文件动态生成 SKILL.md
不依赖 stats_rules.json（因为它是这个 Skill 的产出物）
"""
import json
import os
import pandas as pd
from datetime import datetime

def build_skill_from_excel(uploaded_dir: str, output_path: str):
    """
    根据上传的 Excel 文件动态生成 SKILL.md
    
    Args:
        uploaded_dir: 上传的 Excel 文件目录
        output_path: 生成的 SKILL.md 路径
    """
    
    # 查找最新上传的 Excel 文件
    excel_file = find_latest_excel(uploaded_dir)
    
    # 提取 Excel 的列名和数据特征
    excel_info = extract_excel_info(excel_file) if excel_file else None
    
    # 生成 SKILL.md
    skill_content = generate_skill_content(excel_info)
    
    # 保存
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(skill_content)
    
    print(f"[OK] SKILL.md generated: {output_path}")
    if excel_info:
        print(f"   - Excel file: {os.path.basename(excel_file)}")
        print(f"   - Columns: {len(excel_info['columns'])}")
    else:
        print("   - No Excel file found, using generic template")


def find_latest_excel(uploaded_dir: str) -> str:
    """查找最新上传的 Excel 文件"""
    if not os.path.exists(uploaded_dir):
        return None
    
    excel_files = [f for f in os.listdir(uploaded_dir) 
                   if f.endswith(('.xlsx', '.xls')) and not f.startswith('~')]
    
    if not excel_files:
        return None
    
    # 按修改时间排序，返回最新的
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(uploaded_dir, x)), reverse=True)
    return os.path.join(uploaded_dir, excel_files[0])


def extract_excel_info(excel_path: str) -> dict:
    """提取 Excel 文件信息"""
    try:
        # 读取前 5 行数据作为样本
        df = pd.read_excel(excel_path, nrows=5)
        
        # 分析每列的数据类型
        columns_info = []
        for col in df.columns:
            sample_values = df[col].dropna().head(3).tolist()
            dtype = str(df[col].dtype)
            
            # 推断列类型
            col_type = 'unknown'
            if 'int' in dtype or 'float' in dtype:
                col_type = 'numeric'
            elif 'datetime' in dtype:
                col_type = 'datetime'
            elif 'bool' in dtype:
                col_type = 'boolean'
            else:
                # 文本类型，进一步判断
                col_lower = col.lower()
                if any(kw in col_lower for kw in ['时间', '日期', 'date', 'time']):
                    col_type = 'datetime'
                elif any(kw in col_lower for kw in ['金额', '销售额', '价格', '数', '价']):
                    col_type = 'numeric'
                elif any(kw in col_lower for kw in ['销售', '产品', '城市', '客户', '名称']):
                    col_type = 'category'
                else:
                    col_type = 'text'
            
            columns_info.append({
                'name': col,
                'type': col_type,
                'dtype': dtype,
                'sample': sample_values[:2]
            })
        
        return {
            'filename': os.path.basename(excel_path),
            'columns': columns_info,
            'row_count': len(pd.read_excel(excel_path))
        }
    except Exception as e:
        print(f"[WARN] Failed to extract Excel info: {e}")
        return None


def generate_skill_content(excel_info: dict) -> str:
    """生成 SKILL.md 内容"""
    
    # 生成列信息表格
    columns_md = ""
    if excel_info:
        for col in excel_info['columns']:
            sample_str = ', '.join([str(v) for v in col['sample']]) if col['sample'] else '-'
            columns_md += f"| `{col['name']}` | {col['type']} | {sample_str} |\n"
    else:
        columns_md = "| 列名 | 数据类型 | 示例值 |\n|------|----------|--------|\n"
    
    # 生成动态示例（如果有 Excel 信息）
    example_recommendations = []
    if excel_info:
        # 根据实际列名生成推荐示例
        numeric_cols = [c['name'] for c in excel_info['columns'] if c['type'] == 'numeric']
        category_cols = [c['name'] for c in excel_info['columns'] if c['type'] in ['category', 'text']]
        datetime_cols = [c['name'] for c in excel_info['columns'] if c['type'] == 'datetime']
        
        # KPI 推荐
        if numeric_cols:
            example_recommendations.append({
                "name": "核心 KPI",
                "type": "kpi",
                "enabled": True,
                "description": "核心经营指标汇总",
                "metrics": [
                    {"field": numeric_cols[0], "agg": "sum", "alias": f"总{numeric_cols[0]}"},
                    {"field": numeric_cols[0], "agg": "count", "alias": f"{numeric_cols[0]}次数"}
                ]
            })
        
        # 排名推荐
        if category_cols and numeric_cols:
            example_recommendations.append({
                "name": f"按{category_cols[0]}排名",
                "type": "ranking",
                "enabled": True,
                "description": f"按{category_cols[0]}维度的排名统计",
                "group_by": [category_cols[0]],
                "metrics": [
                    {"field": numeric_cols[0], "agg": "sum", "alias": f"总{numeric_cols[0]}"}
                ]
            })
        
        # 趋势推荐
        if datetime_cols and numeric_cols:
            example_recommendations.append({
                "name": "时间趋势",
                "type": "trend",
                "enabled": True,
                "description": "按时间维度的趋势分析",
                "group_by": ["年月"],  # 需要从日期提取
                "metrics": [
                    {"field": numeric_cols[0], "agg": "sum", "alias": f"总{numeric_cols[0]}"}
                ]
            })
    
    import json as json_lib
    example_json = json_lib.dumps({"recommendations": example_recommendations}, ensure_ascii=False, indent=2) if example_recommendations else "{}"
    
    # 生成完整的 SKILL.md
    skill_md = f"""---
name: stats-rule-recommender
description: 统计规则推荐技能（动态版）- 根据上传的 Excel 数据结构推荐统计规则配置
version: 2.0.0-dynamic
author: PPT Report Generator
trigger: 分析 Excel 数据结构，推荐统计规则
generated_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
excel_file: {excel_info['filename'] if excel_info else '未检测到'}
---

# 统计规则推荐专家（动态配置版）

你是数据分析专家，专门根据 Excel 数据结构推荐有价值的统计规则配置。

**重要**：本规范根据实际上传的 Excel 文件动态生成，请仔细分析数据结构后推荐统计规则。

---

## 📊 当前上传的 Excel 文件

**文件名**: `{excel_info['filename'] if excel_info else '未检测到'}`
**数据行数**: `{excel_info['row_count'] if excel_info else '未知'}`

### 列结构分析

| 列名 | 数据类型 | 示例值 |
|------|----------|--------|
{columns_md}
---

## ✍️ 推荐规则（核心逻辑）

### 1. 识别数值字段（用于聚合计算）
查找所有数值类型的列，例如：
- 销售额、订单数、数量、金额、价格、利润、成本等
- 这些字段适合用于：sum/count/mean/max/min 等聚合

### 2. 识别分类字段（用于分组维度）
查找所有文本类型的列，例如：
- 销售员、产品、城市、客户、地区、类别等
- 这些字段适合用于：group_by 分组统计

### 3. 识别时间字段（用于趋势分析）
查找所有日期/时间类型的列，例如：
- 订单时间、日期、创建时间、支付时间等
- 这些字段适合用于：按月/季度/年度趋势分析

### 4. 推荐统计规则（根据字段组合）

| 字段组合 | 推荐统计类型 | 说明 | 示例 |
|---------|------------|------|------|
| 数值字段 | kpi | 核心 KPI 统计 | 总销售额、总订单数、平均客单价 |
| 分类字段 + 数值字段 | ranking | 按分类排名 | 销售员业绩排名、城市销售排名 |
| 分类字段 + 数值字段 | composition | 占比分析 | 产品占比、客户占比 |
| 2 个分类字段 + 数值字段 | comparison | 对比分析 | 新老客对比、男女对比 |
| 时间字段 + 数值字段 | trend | 趋势分析 | 月度销售趋势、季度趋势 |
| 时间字段（星期）+ 数值字段 | distribution | 分布分析 | 星期分布、时段分布 |
| 2 个分类字段 + 数值字段 | matrix | 矩阵分析 | 销售员 - 产品矩阵 |
| 数值字段（差异大） | outlier | 异常检测 | 异常订单、异常值识别 |

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
        {{"field": "订单数", "agg": "count", "alias": "总订单数"}},
        {{"field": "客单价", "agg": "mean", "alias": "平均客单价"}}
      ]
    }},
    {{
      "name": "销售员业绩",
      "type": "ranking",
      "enabled": true,
      "description": "销售员业绩排名统计",
      "group_by": ["销售员"],
      "metrics": [
        {{"field": "销售额", "agg": "sum", "alias": "总销售额"}}
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

## 💡 基于当前数据的推荐示例

{example_json}

---

## ⚠️ 注意事项

1. **字段名必须与 Excel 列名完全一致**
2. **聚合函数从以下选择**：sum, count, mean, max, min, median
3. **分组字段必须是分类字段**（文本类型）
4. **指标字段必须是数值字段**
5. **不要推荐空配置**（如没有数值字段时不要推荐 kpi）
6. **优先推荐业务价值高的统计**：
   - 管理层关心的核心 KPI
   - 能发现问题的排名/占比
   - 能指导行动的趋势/对比

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**版本**: 2.0.0-dynamic
**状态**: ✅ 动态生成，与上传的 Excel 文件同步
"""
    
    return skill_md


if __name__ == '__main__':
    # 示例用法
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    uploaded_dir = os.path.join(base_dir, 'output', 'uploaded')
    
    build_skill_from_excel(
        uploaded_dir=uploaded_dir,
        output_path=os.path.join(base_dir, 'skills', 'stats-rule-recommender', 'SKILL.md')
    )
