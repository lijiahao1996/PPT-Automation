# 2026-04-09 - 图表占位符兼容性问题修复

## ✅ 问题已解决

### 问题：`[CHART:customer_city]` 没有成功插入到 PPT 模板中

**原因**：
1. 用户的 PPT 模板 `销售分析报告_标准模板.pptx` 中使用的是双方括号占位符：`[[CHART:customer_city]]`
2. 代码中只支持单方括号：`[CHART:customer_city]`
3. 占位符查找和替换逻辑不兼容双方括号格式

**修复**：
1. 修改 `template_engine.py` 中的正则表达式，兼容单方括号和双方括号
2. 修改 `find_placeholder_positions` 函数，使用正则表达式匹配占位符
3. 修改 `generate_report.py`，同时生成单方括号和双方括号的占位符映射

### 修改的文件

#### 1. `scripts/core/template_engine.py`
```python
# 正则表达式（兼容单方括号和双方括号）
chart_pattern = re.compile(r'\[\[?CHART:(\w+)\]\]?')
table_pattern = re.compile(r'\[\[?TABLE:(\w+)\]\]?')
text_pattern = re.compile(r'\[\[?TEXT:(\w+)\]\]?')
kpi_pattern = re.compile(r'\[\[?KPI:(\w+)\]\]?')

# find_placeholder_positions 函数使用正则表达式匹配
regex_pattern = rf'\[\[?CHART:{re.escape(chart_name)}\]\]?'
regex = re.compile(regex_pattern)
if regex.search(text):
    # 找到占位符
```

#### 2. `scripts/generate_report.py`
```python
# 同时生成单方括号和双方括号的占位符映射
placeholder_map[f'[{key}]'] = chart_paths[chart_key]
placeholder_map[f'[[{key}]]'] = chart_paths[chart_key]  # 兼容双方括号
```

---

## 📊 验证结果

### 所有 7 个图表已成功插入 PPT

```
Slide 4: 1 picture(s)  - sales_by_person
Slide 5: 1 picture(s)  - product_pie
Slide 6: 1 picture(s)  - city_ranking
Slide 7: 1 picture(s)  - customer_comparison
Slide 8: 1 picture(s)  - monthly_trend
Slide 9: 1 picture(s)  - heatmap
Slide 14: 1 picture(s) - customer_city ✅
```

### 日志输出
```
[OK] 生成 7 个图表
[OK] 动态构建 14 个图表占位符映射
[OK] 图表占位符已替换
[OK] 已生成异常订单表格 (slide 10)
```

---

## ⚠️ 关于 `{{INSIGHT:customer_city}}`

### 当前状态
- **AI 洞察已成功生成**：`ai_insights.json` 包含第 9 条洞察（customer_city）
- **PPT 模板中没有洞察占位符**：第 14 页只有 `[[CHART:customer_city]]`，没有 `{{INSIGHT:customer_city}}`

### 解决方案

如果需要在第 14 页显示 customer_city 的洞察，需要在 PPT 模板中添加洞察占位符：

1. 打开 `templates/销售分析报告_标准模板.pptx`
2. 导航到第 14 页
3. 插入文本框
4. 输入：`{{INSIGHT:customer_city}}`
5. 保存 PPT 模板
6. 重新运行 `Run.bat`

### 或者修改 placeholders.json

如果希望 customer_city 的洞察显示在其他页面，可以修改 `templates/placeholders.json` 中的 `slide_index`：

```json
"CHART:customer_city": {
  "description": "客户属性与城市销售分析",
  "data_source": "客户城市分析",
  "chart_type": "bar_horizontal",
  "title": "客户属性与城市销售分析",
  "slide_index": 10  // 修改为其他页码
}
```

---

## 🎉 总结

### 已修复的问题
1. ✅ 图表占位符兼容单方括号和双方括号
2. ✅ 所有 7 个图表成功插入 PPT
3. ✅ `customer_city` 图表成功插入第 14 页

### 待用户确认
- 是否需要在第 14 页添加 `{{INSIGHT:customer_city}}` 洞察占位符？
- 如果需要，请在 PPT 模板中手动添加

---

**修复时间**: 2026-04-09 02:40  
**修复人**: AI Assistant  
**状态**: ✅ 图表插入问题已解决
