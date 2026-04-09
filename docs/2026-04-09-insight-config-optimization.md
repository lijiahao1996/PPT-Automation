# 2026-04-09 - PPT 配置工具优化

## 🎯 问题诊断

### 问题 1：`{{INSIGHT:sales_by_person}}` 没有展示
**原因**：
- AI 返回了 10 条洞察，但 `placeholders.json` 中只有 7 个图表配置
- 代码遍历 `charts` (7 个) → 取前 7 条洞察 → 最后 2 条给 conclusion/strategy
- 但实际 AI 返回的洞察顺序可能与图表顺序不匹配

**修复**：
- 修改 `generate_report.py` 遍历 `insights` 配置而不是 `charts`
- 确保洞察与配置一一对应

### 问题 2 & 3：`{{INSIGHT:kpi_summary}}` 和 `{{INSIGHT:abnormal}}` 无定义
**原因**：这两个变量在 `placeholders.json` 中没有配置

**修复**：
- 在 `placeholders.json` 中新增 `CHART:kpi_summary` 和 `CHART:abnormal` 配置
- 现在 insights 配置包含 9 个变量（7 图表 + 2 额外洞察）

### 问题 4：结论和策略硬编码
**原因**：结论和策略的生成提示词写死在代码中

**修复**：
- 新增 `special_insights` 配置项支持自定义结论和策略
- 在配置工具中添加"🎯 结论 & 策略"标签页

---

## ✅ 已完成的修改

### 1. `templates/placeholders.json`
新增洞察配置：
```json
"CHART:kpi_summary": {
  "description": "核心 KPI 洞察",
  "data_source": "核心 KPI",
  "dimensions": ["趋势分析", "对比分析"],
  "metrics": ["总销售额", "总订单数", "客单价"],
  "baseline": "环比",
  "style": "数据驱动",
  "word_count": 150,
  "enabled": true,
  "custom_prompt": "分析核心经营指标的健康度，指出关键风险点",
  "slide_index": 2
},
"CHART:abnormal": {
  "description": "异常订单洞察",
  "data_source": "异常订单",
  "dimensions": ["异常检测", "风险分析"],
  "metrics": ["销售额", "订单数"],
  "baseline": "无对比",
  "style": "问题导向",
  "word_count": 150,
  "enabled": true,
  "custom_prompt": "分析异常订单的类型、分布和潜在风险，给出风控建议",
  "slide_index": 9
}
```

### 2. `scripts/config_tool/app.py`
- 新增 Tab 8："🎯 结论 & 策略配置"
- 支持用户自定义结论和策略的：
  - 说明描述
  - 分析维度（4 条）
  - 洞察风格
  - 字数要求
  - 自定义生成提示词
- 修改 Tab 4（PPT 变量）显示特殊变量的自定义配置

### 3. `scripts/ai/insight_generator.py`
- 新增 `_load_special_insights_config()` 方法
- 修改 `_build_system_prompt()` 使用 insights 数量而不是 charts 数量
- 修改 `_build_user_prompt()` 支持特殊洞察配置（结论 & 策略）
- 修改 `_parse_response()` 使用 insights 数量检查

### 4. `scripts/generate_report.py`
- 修改 `_build_text_replacements_from_config()` 使用 `insight_count` 而不是 `chart_count`
- 确保所有 9 个洞察变量都能正确映射

### 5. `skills/data-insight/SKILL.md`
- 运行 `skill_builder.py` 自动更新（包含 7 个图表映射）

---

## 📊 当前配置状态

| 配置项 | 数量 | 说明 |
|--------|------|------|
| Charts | 7 | 图表配置 |
| Insights | 9 | 洞察配置（7 图表 + kpi_summary + abnormal） |
| Special Insights | 0 | 特殊配置（结论 & 策略，待用户在配置工具中保存） |

**期望 AI 返回洞察数量**：9 + 2 = 11 条

---

## 🚀 测试步骤

### 1. 启动配置工具
```bash
cd C:\Users\50319\Desktop\n8n\scripts\config_tool
streamlit.bat
```

### 2. 配置结论 & 策略
1. 打开 http://localhost:8501/
2. 切换到"🎯 结论 & 策略"标签页
3. 自定义结论和策略的生成提示词
4. 点击"💾 保存结论 & 策略配置"

### 3. 运行 PPT 生成
```bash
cd C:\Users\50319\Desktop\n8n
Run.bat
```

### 4. 检查输出
- 查看 `artifacts/ai_insights.json` - 应该有 11 条洞察
- 查看生成的 PPT - 检查所有占位符是否正确替换

---

## 📝 PPT 模板占位符清单

### 图表变量（7 个）
```
[CHART:sales_by_person]
[CHART:product_pie]
[CHART:city_ranking]
[CHART:customer_comparison]
[CHART:monthly_trend]
[CHART:heatmap]
[CHART:customer_city]
```

### 洞察变量（9 个）
```
{{INSIGHT:sales_by_person}}
{{INSIGHT:kpi_summary}}      ← 新增
{{INSIGHT:abnormal}}          ← 新增
{{INSIGHT:product_pie}}
{{INSIGHT:city_ranking}}
{{INSIGHT:customer_comparison}}
{{INSIGHT:monthly_trend}}
{{INSIGHT:heatmap}}
{{INSIGHT:customer_city}}
```

### 特殊变量（2 个）
```
{{INSIGHT:conclusion}}  - 可在配置工具中自定义
{{INSIGHT:strategy}}    - 可在配置工具中自定义
```

### 其他变量
```
[TEXT:report_title]
[TEXT:report_subtitle]
[TEXT:report_date]
[KPI:cards]
[TABLE:abnormal_orders]
```

---

## 💡 架构优化

### 之前
```
charts (7 个) → AI 生成 7+2=9 条洞察
```

### 现在
```
insights (9 个) → AI 生成 9+2=11 条洞察
  ├─ 7 个图表洞察
  ├─ kpi_summary（额外）
  ├─ abnormal（额外）
  └─ special_insights（结论 & 策略，可自定义）
```

### 优势
1. **灵活性**：支持额外洞察变量，不局限于图表
2. **可配置**：结论和策略支持用户自定义提示词
3. **扩展性**：未来可以轻松添加更多洞察变量

---

## 🔧 后续建议

1. **PPT 模板更新**：确保 PPT 模板中包含所有 9 个洞察占位符
2. **测试验证**：运行一次完整的 PPT 生成流程，检查所有变量是否正确替换
3. **文档更新**：在配置工具中添加帮助文档说明新增功能

---

**修改时间**: 2026-04-09 01:50  
**修改人**: AI Assistant  
**状态**: ✅ 代码已修改，待测试验证
