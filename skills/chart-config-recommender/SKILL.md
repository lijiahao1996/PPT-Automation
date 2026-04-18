---
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
| 核心 KPI | kpi | 纵向柱状图 | - | 总销售额, 订单总数, 平均单笔销售额 |
| 按销售员排名 | ranking | 横向条形图 | 销售员 | 总销售额 |
| 按城市销售占比 | composition | 环形饼图 | 城市 | 城市销售额 |
| 按产品销售对比 | comparison | 分组柱状图 | 产品 | 产品销售额 |
| 月度销售趋势 | trend | 折线图 | 年月 | 月度总销售额 |
| 销售员-产品矩阵 | matrix | 热力图 | 销售员, 产品 | 销售额 |

---

## 📈 图表类型映射规则

根据统计类型自动推荐图表（AI 可以灵活选择其他图表类型）：

| 统计类型 | 推荐图表 | 说明 |
|---------|---------|------|
| kpi | bar_vertical | KPI 指标适合用柱状图对比 |
| ranking | bar_horizontal | 排名适合用横向条形图对比 |
| composition | pie | 占比适合用饼图/环形图展示 |
| comparison | column_clustered | 对比适合用分组柱状图 |
| trend | line | 趋势适合用折线图展示 |
| distribution | histogram | 分布适合用直方图展示 |
| matrix | heatmap | 矩阵适合用热力图展示 |
| outlier | boxplot | 异常检测适合用箱线图 |

---

## 🎨 所有支持的图表类型（16种）

AI 可以根据数据特征自由选择最合适的图表类型：

### 基础图表（6种）

#### 1. `bar_horizontal` - 横向条形图（适合排名对比）
**JSON 配置格式：**
```json
{
  "chart_key": "salesperson_ranking",
  "chart_type": "bar_horizontal",
  "title": "销售员业绩排名",
  "data_source": "按销售员排名",
  "render_mode": "native",
  "x_field": "总销售额",
  "y_field": "销售员"
}
```
**参数说明：**
- `x_field`: 数值字段（条形长度）
- `y_field`: 分类字段（Y 轴标签）

#### 2. `bar_vertical` - 纵向柱状图（适合指标对比）
**JSON 配置格式：**
```json
{
  "chart_key": "core_kpi",
  "chart_type": "bar_vertical",
  "title": "核心 KPI 对比",
  "data_source": "核心 KPI",
  "render_mode": "native",
  "x_field": "指标名称",
  "y_field": "指标值"
}
```
**参数说明：**
- `x_field`: 分类字段（X 轴标签）
- `y_field`: 数值字段（柱子高度）

#### 3. `pie` - 环形饼图（适合占比分析）
**JSON 配置格式：**
```json
{
  "chart_key": "city_composition",
  "chart_type": "pie",
  "title": "城市销售占比",
  "data_source": "按城市占比",
  "render_mode": "native",
  "category_field": "城市",
  "value_field": "城市销售额"
}
```
**参数说明：**
- `category_field`: 分类字段（扇区标签）
- `value_field`: 数值字段（扇区大小）

#### 4. `line` - 折线图（适合趋势分析）
**JSON 配置格式：**
```json
{
  "chart_key": "monthly_trend",
  "chart_type": "line",
  "title": "月度销售趋势",
  "data_source": "月度销售趋势",
  "render_mode": "native",
  "x_field": "年月",
  "y_field": "月度总销售额"
}
```
**参数说明：**
- `x_field`: 时间/顺序字段（X 轴）
- `y_field`: 数值字段（支持多指标，可用逗号分隔）

#### 5. `heatmap` - 热力图（适合矩阵数据、二维对比）
**JSON 配置格式：**
```json
{
  "chart_key": "product_matrix",
  "chart_type": "heatmap",
  "title": "产品-销售员销售矩阵",
  "data_source": "销售员-产品矩阵",
  "render_mode": "image",
  "y_field": "销售员"
}
```
**参数说明：**
- `y_field`: 行字段（Y 轴标签）
- **注意**：columns（列字段）会自动从数据中提取（排除 y_field 列后的所有列）
- **不要配置** x_field、value_field、category_field

#### 6. `column_clustered` / `multi_column` - 分组柱状图（适合多系列对比）
**JSON 配置格式：**
```json
{
  "chart_key": "product_comparison",
  "chart_type": "column_clustered",
  "title": "产品销售对比",
  "data_source": "按产品销售对比",
  "render_mode": "native",
  "category_field": "产品类别",
  "series": ["销售额", "订单数", "客户数"]
}
```
**参数说明：**
- `category_field`: 分类字段（X 轴分组）
- `series`: 数值字段列表（每个系列一个柱子）

### 分布图表（5种）

#### 7. `scatter` - 散点图（适合相关性分析）
**JSON 配置格式：**
```json
{
  "chart_key": "price_sales_correlation",
  "chart_type": "scatter",
  "title": "价格与销量相关性",
  "data_source": "产品销售数据",
  "render_mode": "image",
  "x_field": "单价",
  "y_field": "销量"
}
```
**参数说明：**
- `x_field`: X 轴数值字段
- `y_field`: Y 轴数值字段

#### 8. `histogram` - 直方图（适合分布分析）
**JSON 配置格式：**
```json
{
  "chart_key": "age_distribution",
  "chart_type": "histogram",
  "title": "年龄分布",
  "data_source": "客户数据",
  "render_mode": "image",
  "y_field": "年龄"
}
```
**参数说明：**
- `y_field`: 数值字段（分析分布的字段）
- bins: 可选，默认 20

#### 9. `boxplot` - 箱线图（适合异常值检测）
**JSON 配置格式：**
```json
{
  "chart_key": "salary_by_department",
  "chart_type": "boxplot",
  "title": "各部门薪资分布",
  "data_source": "部门薪资数据",
  "render_mode": "image",
  "category_field": "部门",
  "value_field": "薪资"
}
```
**参数说明：**
- `category_field`: 分类字段（每个箱子一个类别）
- `value_field`: 数值字段（分析分布的值）

#### 10. `violin` - 小提琴图（适合分布密度）
**JSON 配置格式：**
```json
{
  "chart_key": "score_by_class",
  "chart_type": "violin",
  "title": "各班成绩分布",
  "data_source": "学生成绩数据",
  "render_mode": "image",
  "category_field": "班级",
  "value_field": "成绩"
}
```
**参数说明：**
- `category_field`: 分类字段
- `value_field`: 数值字段

#### 11. `bubble` - 气泡图（适合三维数据）
**JSON 配置格式：**
```json
{
  "chart_key": "market_analysis",
  "chart_type": "bubble",
  "title": "市场分析",
  "data_source": "市场数据",
  "render_mode": "image",
  "x_field": "市场份额",
  "y_field": "增长率",
  "size_field": "营收规模"
}
```
**参数说明：**
- `x_field`: X 轴数值字段
- `y_field`: Y 轴数值字段
- `size_field`: 气泡大小字段

### 高级图表（5种）

#### 12. `area` - 面积图（适合累计趋势）
**JSON 配置格式：**
```json
{
  "chart_key": "revenue_trend",
  "chart_type": "area",
  "title": "收入趋势",
  "data_source": "月度收入数据",
  "render_mode": "image",
  "x_field": "月份",
  "y_field": ["产品收入", "服务收入", "其他收入"]
}
```
**参数说明：**
- `x_field`: 时间/顺序字段
- `y_field`: 数值字段列表（多个系列叠加）

#### 13. `errorbar` - 误差棒图（适合误差分析）
**JSON 配置格式：**
```json
{
  "chart_key": "experiment_results",
  "chart_type": "errorbar",
  "title": "实验结果",
  "data_source": "实验数据",
  "render_mode": "image",
  "x_field": "实验组",
  "y_field": "平均值",
  "error_field": "标准差"
}
```
**参数说明：**
- `x_field`: 分类字段
- `y_field`: 数值字段（主值）
- `error_field`: 误差字段（误差棒长度）

#### 14. `polar` - 极坐标图（适合周期数据）
**JSON 配置格式：**
```json
{
  "chart_key": "seasonal_sales",
  "chart_type": "polar",
  "title": "季节性销售",
  "data_source": "月度销售数据",
  "render_mode": "image",
  "x_field": "月份角度",
  "y_field": "销售额"
}
```
**参数说明：**
- `x_field`: 角度字段（0-360 度）
- `y_field`: 半径字段（距离中心的距离）

#### 15. `waterfall` - 瀑布图（适合增减分析）
**JSON 配置格式：**
```json
{
  "chart_key": "profit_waterfall",
  "chart_type": "waterfall",
  "title": "利润增减分析",
  "data_source": "利润数据",
  "render_mode": "image",
  "category_field": "项目",
  "value_field": "变动金额"
}
```
**参数说明：**
- `category_field`: 分类字段（每个步骤）
- `value_field`: 数值字段（正数增加，负数减少）

#### 16. `funnel` - 漏斗图（适合流程转化）
**JSON 配置格式：**
```json
{
  "chart_key": "conversion_funnel",
  "chart_type": "funnel",
  "title": "转化漏斗",
  "data_source": "转化数据",
  "render_mode": "image",
  "category_field": "阶段",
  "value_field": "用户数"
}
```
**参数说明：**
- `category_field`: 阶段字段（漏斗层级）
- `value_field`: 数值字段（每层级的值，从上到下递减）

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

{
  "chart_recommendations": [
    {
      "chart_key": "核心_kpi",
      "chart_type": "bar_vertical",
      "title": "核心 KPI分析",
      "data_source": "核心 KPI",
      "reason": "KPI 指标适合用柱状图对比",
      "x_field": "指标名称",
      "y_field": "总销售额"
    },
    {
      "chart_key": "按销售员排名",
      "chart_type": "bar_horizontal",
      "title": "按销售员排名分析",
      "data_source": "按销售员排名",
      "reason": "排名适合用横向条形图对比",
      "x_field": "总销售额",
      "y_field": "销售员"
    },
    {
      "chart_key": "按城市销售占比",
      "chart_type": "pie",
      "title": "按城市销售占比分析",
      "data_source": "按城市销售占比",
      "reason": "占比适合用饼图/环形图展示",
      "category_field": "城市",
      "value_field": "城市销售额"
    }
  ]
}

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

**最后更新**: 2026-04-19 06:01:24
**版本**: 2.0.0-dynamic
**状态**: ✅ 动态生成，与统计规则配置同步
