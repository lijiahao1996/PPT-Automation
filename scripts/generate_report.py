# -*- coding: utf-8 -*-
"""
PPT 生成主流程 - 企业版
模板引擎 + 图表引擎 + AI 洞察

优化版本：
- 修复 Matplotlib 样式警告
- 移除重复代码
- 并行图表生成
- 统一日志配置
- 动态占位符配置（从 placeholders.json 读取）
"""
import os
import sys
import logging
import configparser
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, Optional

# 添加脚本目录到路径
# 支持 EXE 打包：使用 EXE_WORK_DIR 环境变量（如果存在）
SCRIPTS_DIR = os.path.dirname(__file__)
BASE_DIR = os.environ.get('EXE_WORK_DIR') or os.path.dirname(SCRIPTS_DIR)
sys.path.insert(0, SCRIPTS_DIR)

from core.data_loader import DataLoader
from core.chart_engine import ChartEngine
from core.template_engine import TemplateEngine
from core.validator import PresetValidators, DataQualityError
from ai.insight_generator import InsightGenerator

# ========== 统一日志配置 ==========
def setup_logging():
    """配置统一日志"""
    logs_dir = os.path.join(BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logger = logging.getLogger('ppt_generator')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)
    
    file_handler = logging.FileHandler(
        os.path.join(logs_dir, f'ppt_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger, logs_dir

logger, logs_dir = setup_logging()
# ====================================

# ========== 动态生成 SKILL.md ==========
def build_skill_always(log_callback=None):
    """根据当前配置动态生成 SKILL.md"""
    import json
    
    skill_path = os.path.join(BASE_DIR, 'skills', 'data-insight', 'SKILL.md')
    placeholders_path = os.path.join(BASE_DIR, 'templates', 'placeholders.json')
    
    if log_callback is None:
        log_callback = lambda x: None
    
    log_callback("正在根据当前配置重新生成 SKILL.md...")
    
    try:
        # 读取当前配置
        if os.path.exists(placeholders_path):
            with open(placeholders_path, 'r', encoding='utf-8') as f:
                placeholders = json.load(f)
            
            # 构建 SKILL 内容
            charts = placeholders.get('placeholders', {}).get('charts', {})
            insights = placeholders.get('placeholders', {}).get('insights', {})
            special_insights = placeholders.get('special_insights', {}).get('variables', [])
            
            skill_content = f"""---
name: data-insight
description: 销售数据洞察生成规范（动态版）- 根据实际图表配置生成洞察
version: 3.2.0-dynamic
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
"""
            
            # 这里应该从 stats_rules.json 读取实际的 Sheet 定义
            # 简化版本：列出所有图表的数据源
            data_sources = set()
            for chart_key, chart_cfg in charts.items():
                data_sources.add(chart_cfg.get('data_source', ''))
            
            for source in data_sources:
                skill_content += f"| {source} | 统计数据 | 动态检测 |\n"
            
            skill_content += f"""
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
  "• 第 2 页洞察 1\n• 第 2 页洞察 2\n• 第 2 页洞察 3",
  ...
]
```

### 关键要求

1. **数组元素数量 = 图表数量**
2. **不能嵌套数组**，所有洞察都必须是字符串
3. 列表式洞察用 `\n` 连接 3 条，如：`"• 洞察 1\n• 洞察 2\n• 洞察 3"`
4. 结构化洞察用 `\n\n` 分隔 4 个段落
5. 直接输出 JSON 数组，不要任何其他文字

---

## 📊 洞察映射（共{len(charts)}个）

根据当前配置，需要生成以下洞察：

"""
            
            for i, (chart_key, chart_cfg) in enumerate(charts.items()):
                chart_name = chart_key.replace('CHART:', '')
                skill_content += f"""#### 第{i}页：{chart_name}
**洞察 Key**: `{chart_key}`
**数据源**: {chart_cfg.get('data_source', '')}
**分析维度**: 排名分析，对比分析
**自定义提示**: {chart_cfg.get('description', '根据数据特征生成洞察')}

"""
            
            # 添加特殊洞察配置
            if special_insights:
                skill_content += "\n\n## 🎯 特殊洞察配置（可自定义）\n\n"
                for var in special_insights:
                    skill_content += f"""#### {var.get('name', var.get('key', ''))}（{{{{INSIGHT:{var.get('key', '')}}}}}）
**分析维度**: {', '.join(var.get('dimensions', []))}
**洞察风格**: {var.get('style', '数据驱动')}
**字数要求**: {var.get('word_count', 300)}字
**自定义提示**: {var.get('custom_prompt', '')}

"""
            
            skill_content += """
---

## 🔧 技术实现要求

### JSON 输出格式

```json
[
  "总销售额 285,696 元中，Q2 贡献...（100-150 字）",
  "• 孙林以 39,601 元总销售额位列业绩 TOP1...\n• TOP3 销售员贡献了全团队 39% 的销售额...\n• 头部销售员客单价显著高于团队平均水平...",
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
**版本**: 3.2.0-dynamic
**状态**: ✅ 动态生成，与实际配置同步
"""
            
            # 保存 SKILL.md
            os.makedirs(os.path.dirname(skill_path), exist_ok=True)
            with open(skill_path, 'w', encoding='utf-8') as f:
                f.write(skill_content)
            
            log_callback("✅ SKILL.md 已根据当前配置重新生成")
        else:
            log_callback("⚠️ placeholders.json 不存在，无法生成 SKILL.md")
    
    except Exception as e:
        log_callback(f"⚠️ SKILL.md 生成失败：{e}，使用现有文件")




# 注意：图表配置已从 placeholders.json 读取
# CHART_CONFIGS 已移除


def _generate_single_chart(args: Tuple) -> Tuple[str, str]:
    """生成单个图表（用于并行执行）"""
    chart_key, config, data_summary, chart_engine, temp_dir, log_callback = args
    if log_callback is None:
        log_callback = lambda x: None
    
    if config['sheet'] not in data_summary:
        return (chart_key, None)
    
    df = data_summary[config['sheet']]
    chart_type = config['type']
    params = config['params'].copy()
    output_path = os.path.join(temp_dir, f'chart_{chart_key}.png')
    params['output_path'] = output_path
    
    try:
        if chart_type == 'bar_horizontal':
            chart_engine.create_bar_horizontal(df, **params)
        elif chart_type == 'bar_vertical':
            chart_engine.create_bar_vertical(df, **params)
        elif chart_type == 'pie':
            chart_engine.create_pie(df, **params)
        elif chart_type == 'multi_column' or chart_type == 'column_clustered':
            chart_engine.create_multi_column(df, **params)
        elif chart_type == 'line':
            chart_engine.create_line(df, **params)
        elif chart_type == 'scatter':
            chart_engine.create_scatter(df, **params)
        elif chart_type == 'area':
            chart_engine.create_area(df, **params)
        elif chart_type == 'histogram':
            chart_engine.create_histogram(df, **params)
        elif chart_type == 'boxplot':
            chart_engine.create_boxplot(df, **params)
        elif chart_type == 'bubble':
            chart_engine.create_bubble(df, **params)
        elif chart_type == 'errorbar':
            chart_engine.create_errorbar(df, **params)
        elif chart_type == 'polar':
            chart_engine.create_polar(df, **params)
        elif chart_type == 'violin':
            chart_engine.create_violin(df, **params)
        elif chart_type == 'waterfall':
            chart_engine.create_waterfall(df, **params)
        elif chart_type == 'funnel':
            chart_engine.create_funnel(df, **params)
        elif chart_type == 'heatmap':
            # 热力图特殊处理：动态提取产品列
            if params.get('columns') is None:
                # 排除非产品列（销售员、Unnamed 等）
                exclude_cols = ['销售员', 'Unnamed: 0', 'index']
                product_cols = [col for col in df.columns if col not in exclude_cols]
                params['columns'] = product_cols
                log_callback(f"      [INFO] 热力图自动检测到 {len(product_cols)} 个产品：{product_cols}")
            chart_engine.create_heatmap(df, **params)
        elif chart_type in ['multi_column', 'column_clustered']:
            chart_engine.create_multi_column(df, **params)
        else:
            log_callback(f"      [SKIP] 未知图表类型：{chart_type}")
            return (chart_key, None)
        
        return (chart_key, output_path)
    
    except Exception as e:
        log_callback(f"      [ERROR] 生成图表 {chart_key} 失败：{e}")
        return (chart_key, None)


def _get_date_range_from_data(data_loader, raw_data_filename=None) -> str:
    """从原始数据中动态提取日期范围"""
    import pandas as pd
    try:
        # 如果没有提供文件名，自动检测 output 目录中的第一个非统计汇总文件
        if raw_data_filename is None:
            output_dir = os.path.join(BASE_DIR, 'output')
            for f in os.listdir(output_dir):
                if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                    raw_data_filename = f
                    break
        
        # 如果还是没找到，使用默认值
        if not raw_data_filename:
            raw_data_filename = '帆软销售明细.xlsx'
        
        df = data_loader.load_raw_data(raw_data_filename)
        if '订单时间' in df.columns:
            df['订单时间'] = pd.to_datetime(df['订单时间'], errors='coerce')
            min_date = df['订单时间'].min().strftime('%Y年%m月%d日')
            max_date = df['订单时间'].max().strftime('%Y年%m月%d日')
            return f'{min_date} - {max_date}'
    except Exception as e:
        log_callback(f"日期范围提取失败：{e}, 使用默认值")
    return "未知"


def _build_text_replacements_from_config(placeholders: Dict, data_loader, insights: list, today: str, log_callback=None) -> Dict:
    """
    从占位符配置动态构建文本替换字典
    
    Args:
        placeholders: 占位符配置字典
        data_loader: 数据加载器（用于获取实际 KPI 数据）
        insights: AI 洞察列表（10 条）
        today: 今天日期字符串
        log_callback: 日志回调函数
    """
    if log_callback is None:
        log_callback = lambda x: None
    """
    从占位符配置动态构建文本替换字典
    
    Args:
        placeholders: 占位符配置字典
        data_loader: 数据加载器（用于获取实际 KPI 数据）
        insights: AI 洞察列表（10 条）
        today: 今天日期字符串
    
    Returns:
        文本替换字典
    """
    replacements = {}
    
    # 1. 处理 TEXT 类型占位符
    text_placeholders = placeholders.get('placeholders', {}).get('text', {})
    for key, config in text_placeholders.items():
        full_key = f'[{key}]'
        
        # 根据 key 设置默认值
        if key == 'TEXT:report_title':
            replacements[full_key] = config.get('default', '销售数据分析报告')
        elif key == 'TEXT:report_subtitle':
            replacements[full_key] = config.get('default', '业绩复盘 · 洞察归因 · 策略建议')
        elif key == 'TEXT:report_date':
            # 动态提取统计周期（从 placeholders.json 读取格式配置）
            date_range = _get_date_range_from_data(data_loader, raw_data_file)
            date_format = placeholders.get('report_settings', {}).get('date_range_format', '统计周期：{start} - {end} | 日期：{today}')
            replacements[full_key] = date_format.format(start=date_range.split(' - ')[0], end=date_range.split(' - ')[1], today=today)
        elif key == 'KPI:cards':
            # 从实际数据动态生成 KPI 卡片（删除硬编码假数据）
            try:
                kpi_dict = data_loader.get_kpi('核心 KPI')
                replacements[full_key] = (
                    f"总销售额：{kpi_dict.get('总销售额', {}).get('value', 0):,.0f} 元\n"
                    f"总订单数：{kpi_dict.get('总订单数', {}).get('value', 0):,} 单\n"
                    f"平均客单价：{kpi_dict.get('平均客单价', {}).get('value', 0):,.0f} 元\n"
                    f"最高单额：{kpi_dict.get('最高单额', {}).get('value', 0):,.0f} 元\n"
                    f"最低单额：{kpi_dict.get('最低单额', {}).get('value', 0):,.0f} 元"
                )
                log_callback("      [OK] KPI 卡片已从实际数据生成")
            except Exception as e:
                log_callback(f"      [WARN] KPI 数据加载失败：{e}, 使用空值")
                replacements[full_key] = config.get('default', '')
        else:
            replacements[full_key] = config.get('default', '')
    
    # 1.5 处理 DATE 类型占位符
    date_placeholders = placeholders.get('placeholders', {}).get('dates', {})
    for key, config in date_placeholders.items():
        full_key = f'[{key}]'
        # 使用配置的默认值（已在 Tab 4 中设置好格式）
        replacements[full_key] = config.get('default', today)
        logger.debug(f"      映射日期变量：{full_key} <- {config.get('default', today)}")
    
    # 1.6 处理 IMAGE 类型占位符（只记录路径，不替换文本，由后续插入逻辑处理）
    image_placeholders = placeholders.get('placeholders', {}).get('images', {})
    for key, config in image_placeholders.items():
        full_key = f'[{key}]'
        img_path = config.get('path', '')
        if img_path:
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(img_path):
                img_path = os.path.join(BASE_DIR, img_path)
            if os.path.exists(img_path):
                # 不添加到 replacements，由后续插入逻辑处理
                logger.debug(f"      记录图片变量：{full_key} <- {img_path}")
            else:
                log_callback(f"      图片文件不存在：{img_path}")
        else:
            pass  # 空路径，后续插入逻辑会跳过
    
    # 1.7 处理 VIDEO 类型占位符（只记录路径，不替换文本，由后续插入逻辑处理）
    video_placeholders = placeholders.get('placeholders', {}).get('videos', {})
    for key, config in video_placeholders.items():
        full_key = f'[{key}]'
        video_path = config.get('path', '')
        if video_path:
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(video_path):
                video_path = os.path.join(BASE_DIR, video_path)
            if os.path.exists(video_path):
                # 不添加到 replacements，由后续插入逻辑处理
                logger.debug(f"      记录视频变量：{full_key} <- {video_path}")
            else:
                log_callback(f"      视频文件不存在：{video_path}")
        else:
            pass  # 空路径，后续插入逻辑会跳过
    
    # 1.8 处理 LINK 类型占位符（不替换文本，由后续超链接逻辑处理）
    link_placeholders = placeholders.get('placeholders', {}).get('links', {})
    for key, config in link_placeholders.items():
        full_key = f'[{key}]'
        link_url = config.get('url', '')
        # 不添加到 replacements，由后续超链接逻辑处理
        logger.debug(f"      记录链接变量：{full_key} <- {link_url}")
    
    # 2. 处理 INSIGHT 类型占位符
    # 洞察与图表一一对应
    insight_placeholders = placeholders.get('placeholders', {}).get('insights', {})
    charts = placeholders.get('placeholders', {}).get('charts', {})
    
    # 使用 insights 配置数量（包括 kpi_summary, abnormal 等额外洞察）
    insight_count = len(insight_placeholders)
    
    # 图表洞察：与图表一一对应
    # insight_placeholders 的 key 是 CHART:xxx，需要转换为 {{INSIGHT:xxx}}
    # 注意：insights 配置可能包含额外的洞察变量（如 kpi_summary, abnormal）
    for i, (insight_key, insight_config) in enumerate(insight_placeholders.items()):
        # 从 insight_key 提取名称（如 CHART:sales_by_person -> sales_by_person）
        insight_name = insight_key.replace('CHART:', '')
        # PPT 模板中的占位符是 {{INSIGHT:sales_by_person}}（可能带空格）
        full_key = '{{INSIGHT:' + insight_name + '}}'
        # 同时添加带空格的变体（兼容 PPT 模板中可能存在的空格）
        full_key_with_space = '{{INSIGHT:' + insight_name + ' }}'
        
        if i < len(insights):
            replacements[full_key] = insights[i]
            replacements[full_key_with_space] = insights[i]  # 兼容带空格的占位符
            logger.debug(f"      映射洞察：{full_key} <- 第{i+1}条洞察")
        else:
            replacements[full_key] = ''
            replacements[full_key_with_space] = ''
            log_callback(f"      洞察数量不足：{full_key}")
    
    # 结论和策略：使用最后 2 条洞察（如果 AI 生成了的话）
    # 注意：AI 返回的洞察数量 = 洞察配置数量 + 2（结论 + 策略）
    if len(insights) >= insight_count + 2:
        replacements['{{INSIGHT:conclusion}}'] = insights[insight_count]
        replacements['{{INSIGHT:strategy}}'] = insights[insight_count + 1]
        logger.debug(f"      映射结论：{{INSIGHT:conclusion}} <- 第{insight_count+1}条洞察")
        logger.debug(f"      映射策略：{{INSIGHT:strategy}} <- 第{insight_count+2}条洞察")
    else:
        # 当前使用默认值，后期由 AI 生成
        replacements['{{INSIGHT:conclusion}}'] = ''
        replacements['{{INSIGHT:strategy}}'] = ''
        log_callback(f"      洞察数量不足，期望{insight_count+2}条，实际{len(insights)}条")
    
    log_callback(f"      动态构建 {len(replacements)} 个文本占位符替换规则（{len(insight_placeholders)} 个洞察 + 结论 + 策略 + 文本变量）")
    return replacements


def _build_chart_placeholder_map_from_config(placeholders: Dict, chart_paths: Dict, log_callback=None) -> Dict:
    if log_callback is None:
        log_callback = lambda x: None
    """
    从占位符配置动态构建图表占位符映射
    
    Args:
        placeholders: 占位符配置字典
        chart_paths: 已生成的图表路径字典 {chart_key: path}
    
    Returns:
        图表占位符映射 {[CHART:xxx]: path}
    """
    placeholder_map = {}
    
    chart_placeholders = placeholders.get('placeholders', {}).get('charts', {})
    for key, config in chart_placeholders.items():
        # key 格式：CHART:xxx
        chart_key = key.split(':')[1] if ':' in key else key
        
        if chart_key in chart_paths:
            # 同时生成单方括号和双方括号的占位符（兼容不同模板）
            placeholder_map[f'[{key}]'] = chart_paths[chart_key]
            placeholder_map[f'[[{key}]]'] = chart_paths[chart_key]  # 兼容双方括号
        else:
            log_callback(f"      图表未生成：[{key}] (缺少数据：{config.get('data_source', '未知')})")
    
    log_callback(f"      动态构建 {len(placeholder_map)} 个图表占位符映射")
    return placeholder_map


def generate_report(template_name: str = None, output_name: str = None, 
                    parallel_charts: bool = True, regenerate_placeholders: bool = False,
                    log_callback=None, raw_data_name: str = None):
    """
    生成销售分析报告
    
    Args:
        template_name: 模板文件名（默认：销售分析报告_标准模板.pptx）
        output_name: 输出文件名（默认：带时间戳的版本）
        parallel_charts: 是否并行生成图表（默认 True）
        regenerate_placeholders: 是否重新生成占位符配置（默认 False）
        log_callback: 日志回调函数，用于实时输出到 Web 界面
    """
    # 如果没有提供 log_callback，使用默认 logger
    if log_callback is None:
        log_callback = logger.info
    
    # 在生成报告前构建 SKILL（每次都重新生成）
    build_skill_always(log_callback)
    """
    生成销售分析报告
    
    Args:
        template_name: 模板文件名（默认：销售分析报告_标准模板.pptx）
        output_name: 输出文件名（默认：带时间戳的版本）
        parallel_charts: 是否并行生成图表（默认 True）
        regenerate_placeholders: 是否重新生成占位符配置（默认 False）
    """
    print("=" * 70)
    print("  销售分析报告生成器 - 企业版")
    print("=" * 70)
    
    try:
        # ========== 1. 加载数据 ==========
        log_callback("\n[1/5] 加载销售统计数据...")
        data_loader = DataLoader(BASE_DIR)
        
        # 使用传入的文件名（如果提供了）
        output_dir = os.path.join(BASE_DIR, 'output')
        
        if raw_data_name:
            # 直接使用传入的文件名构建统计汇总文件名
            if raw_data_name.endswith('.xlsx'):
                summary_file = raw_data_name.replace('.xlsx', '_统计汇总.xlsx')
            else:
                summary_file = raw_data_name + '_统计汇总.xlsx'
            
            # 检查文件是否存在
            if not os.path.exists(os.path.join(output_dir, summary_file)):
                log_callback(f"❌ 统计汇总文件不存在：{summary_file}")
                log_callback("   将尝试自动检测...")
                raw_data_name = None  # 回退到自动检测
        
        # 如果没有传入文件名，自动检测最新的统计汇总文件
        if not raw_data_name:
            summary_files = []
            for f in os.listdir(output_dir):
                if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                    full_path = os.path.join(output_dir, f)
                    mtime = os.path.getmtime(full_path)
                    summary_files.append((f, mtime))
            
            if summary_files:
                summary_files.sort(key=lambda x: x[1], reverse=True)
                summary_file = summary_files[0][0]
            else:
                summary_file = None
        
        if not summary_file or not os.path.exists(os.path.join(output_dir, summary_file)):
            log_callback("❌ 未找到统计汇总文件，请先在 Tab 1 生成")
            return False
        
        data_summary = data_loader.load_summary(filename=summary_file)
        log_callback(f"      已加载 {len(data_summary)} 个统计表（文件：{summary_file}）")
        
        # 如果没有传入 raw_data_name，从统计汇总文件名提取
        if not raw_data_name:
            raw_data_name = summary_file.replace('_统计汇总.xlsx', '')
        
        log_callback(f"      原始数据：{raw_data_name}")
        
        validator = PresetValidators.summary_data_validator(data_summary)
        log_callback("      [OK] 数据校验通过")
        
        # ========== 2. 初始化引擎 ==========
        log_callback("\n[2/5] 初始化引擎...")
        chart_engine = ChartEngine(BASE_DIR)
        template_engine = TemplateEngine(BASE_DIR, auto_scan=True)
        insight_generator = InsightGenerator(BASE_DIR)
        
        # 可选：重新生成占位符配置
        if regenerate_placeholders and template_name:
            log_callback("      [INFO] 重新生成占位符配置...")
            template_engine.regenerate_placeholders_from_template(template_name)
        
        # 获取占位符配置
        placeholders = template_engine.get_placeholder_config()
        log_callback(f"      [OK] 引擎初始化完成 (占位符：{len(placeholders.get('placeholders', {}))} 类)")
        
        # ========== 3. 生成 AI 洞察 ==========
        log_callback("\n[3/5] 生成 AI 洞察...")
        
        # 检查是否禁用 AI
        config = configparser.ConfigParser()
        config_path = os.path.join(BASE_DIR, 'config.ini')
        enable_ai = True
        
        if os.path.exists(config_path):
            config.read(config_path, encoding='utf-8')
            # 读取 AI 开关配置
            ai_section = config.get('ai', 'enable_ai_insight', fallback='True')
            # 兼容多种布尔值表示
            enable_ai = ai_section.lower() in ['true', '1', 'yes', 'on']
            log_callback(f"      [DEBUG] config.ini [ai] enable_ai_insight = {ai_section} -> {enable_ai}")
        else:
            log_callback(f"      [WARN] config.ini 不存在，使用默认值 enable_ai=True")
        
        insights_file = os.path.join(BASE_DIR, 'artifacts', 'ai_insights.json')
        
        if not enable_ai:
            log_callback("      [SKIP] AI 洞察已禁用（节省 Token），将使用空洞察")
            insights = insight_generator.generate(data_summary, insights_file, enable_ai=False)
        else:
            log_callback("      [INFO] 正在调用 Qwen API 生成洞察...")
            insights = insight_generator.generate(data_summary, insights_file, enable_ai=True)
        
        # 检查洞察是否为空
        has_content = any(insight.strip() for insight in insights)
        if has_content:
            log_callback(f"      [OK] 生成 {len(insights)} 条洞察（AI 生成）")
        else:
            log_callback(f"      [OK] 生成 {len(insights)} 条空洞察（AI 已禁用）")
        
        # ========== 4. 生成图表（支持并行） ==========
        log_callback("\n[4/5] 生成图表...")
        temp_dir = os.path.join(BASE_DIR, 'artifacts', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        chart_paths = {}
        
        # 从 placeholders.json 读取图表配置
        chart_placeholders = placeholders.get('placeholders', {}).get('charts', {})
        
        if parallel_charts:
            log_callback("      [INFO] 使用并行模式生成图表...")
            tasks = []
            for key, config in chart_placeholders.items():
                chart_key = key.split(':')[1] if ':' in key else key
                task_config = {
                    'sheet': config.get('data_source'),
                    'type': config.get('chart_type'),
                    'params': {
                        'title': config.get('title', ''),
                        'output_path': os.path.join(temp_dir, f'chart_{chart_key}.png'),
                    }
                }
                # 只添加该图表类型需要的参数
                chart_type = config.get('chart_type')
                if chart_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter', 'area', 'histogram', 'waterfall', 'funnel']:
                    if config.get('x_field'): task_config['params']['x_field'] = config['x_field']
                    if config.get('y_field'): task_config['params']['y_field'] = config['y_field']
                elif chart_type == 'pie':
                    if config.get('category_field'): task_config['params']['category_field'] = config['category_field']
                    if config.get('value_field'): task_config['params']['value_field'] = config['value_field']
                elif chart_type in ['multi_column', 'column_clustered']:
                    if config.get('category_field'): task_config['params']['category_field'] = config['category_field']
                    if config.get('series'): task_config['params']['series'] = config['series']
                elif chart_type == 'heatmap':
                    if config.get('index_field'): task_config['params']['index_field'] = config['index_field']
                    if config.get('columns'): task_config['params']['columns'] = config['columns']
                elif chart_type in ['boxplot', 'violin']:
                    if config.get('category_field'): task_config['params']['category_field'] = config['category_field']
                    if config.get('value_field'): task_config['params']['value_field'] = config['value_field']
                elif chart_type == 'bubble':
                    if config.get('x_field'): task_config['params']['x_field'] = config['x_field']
                    if config.get('y_field'): task_config['params']['y_field'] = config['y_field']
                    if config.get('size_field'): task_config['params']['size_field'] = config['size_field']
                elif chart_type == 'errorbar':
                    if config.get('x_field'): task_config['params']['x_field'] = config['x_field']
                    if config.get('y_field'): task_config['params']['y_field'] = config['y_field']
                    if config.get('error_field'): task_config['params']['error_field'] = config['error_field']
                elif chart_type == 'polar':
                    if config.get('angle_field'): task_config['params']['angle_field'] = config['angle_field']
                    if config.get('radius_field'): task_config['params']['radius_field'] = config['radius_field']
                
                if config.get('figsize'):
                    task_config['params']['figsize'] = tuple(config['figsize'])
                
                tasks.append((chart_key, task_config, data_summary, chart_engine, temp_dir, log_callback))
            
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {executor.submit(_generate_single_chart, task): task[0] for task in tasks}
                
                for future in as_completed(futures):
                    chart_key, path = future.result()
                    if path and os.path.exists(path):
                        chart_paths[chart_key] = path
                        log_callback(f"      [OK] {chart_key}: {path}")
        else:
            # 串行生成（略，同上）
            log_callback("      [WARN] 串行模式暂不支持动态配置，请使用并行模式")
        
        log_callback(f"      [OK] 共生成 {len(chart_paths)} 个图表")
        
        # ========== 5. 填充模板（动态占位符） ==========
        log_callback("\n[5/5] 填充 PPT 模板...")
        
        if template_name is None:
            template_name = '销售分析报告_标准模板.pptx'
        
        prs = template_engine.load_template(template_name)
        
        # 准备日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 动态构建文本替换字典（传入 data_loader 以获取实际 KPI 数据）
        text_replacements = _build_text_replacements_from_config(placeholders, data_loader, insights, today, log_callback)
        log_callback(f"      {len(insights)} 条洞察已全部添加到替换列表")
        
        # 替换文本占位符
        template_engine.replace_text_placeholders(prs, text_replacements)
        log_callback("      [OK] 文本占位符已替换")
        
        # 动态构建图表占位符映射（只循环一次）
        placeholder_map = _build_chart_placeholder_map_from_config(placeholders, chart_paths, log_callback)
        
        replaced_count = 0
        for placeholder, chart_path in placeholder_map.items():
            if chart_path and os.path.exists(chart_path):
                if template_engine.replace_with_chart(prs, placeholder, chart_path):
                    replaced_count += 1
        
        log_callback(f"      [OK] 图表占位符已替换 ({replaced_count} 个图表)")
        
        # ========== 动态处理所有 TABLE 类型变量 ==========
        table_placeholders = placeholders.get('placeholders', {}).get('tables', {})
        for table_key, table_config in table_placeholders.items():
            table_name = f'[{table_key}]'
            data_source = table_config.get('data_source', '')
            
            if data_source and data_source in data_summary:
                df = data_summary[data_source]
                if len(df) > 0:
                    table_created = False
                    
                    for slide_idx, slide in enumerate(prs.slides):
                        if table_created:
                            break
                        for shape in slide.shapes:
                            if hasattr(shape, 'text_frame'):
                                for paragraph in shape.text_frame.paragraphs:
                                    if table_name in paragraph.text:
                                        left = shape.left
                                        top = shape.top
                                        width = shape.width
                                        height = shape.height
                                        
                                        sp = shape.element
                                        sp.getparent().remove(sp)
                                        
                                        rows = len(df) + 1
                                        cols = len(df.columns)
                                        table = slide.shapes.add_table(rows, cols, left, top, width, height).table
                                        
                                        # 动态提取表头（从 DataFrame 列名）
                                        for i, col_name in enumerate(df.columns):
                                            table.cell(0, i).text = col_name
                                        
                                        for i, (_, row) in enumerate(df.iterrows()):
                                            for j in range(min(cols, len(row))):
                                                table.cell(i+1, j).text = str(row.iloc[j])
                                        
                                        log_callback(f"      [OK] 已生成表格 {table_name} (slide {slide_idx+1})")
                                        table_created = True
                                        break
            else:
                log_callback(f"      [WARN] 表格数据源不存在：{data_source}")
        
        # ========== 处理 IMAGE 类型变量（插入图片） ==========
        image_placeholders = placeholders.get('placeholders', {}).get('images', {})
        for img_key, img_config in image_placeholders.items():
            img_name = f'[{img_key}]'
            img_path = img_config.get('path', '')
            
            if img_path:
                if not os.path.isabs(img_path):
                    img_path = os.path.join(BASE_DIR, img_path)
                
                if os.path.exists(img_path):
                    img_created = False
                    
                    for slide_idx, slide in enumerate(prs.slides):
                        if img_created:
                            break
                        for shape in slide.shapes:
                            if hasattr(shape, 'text_frame'):
                                for paragraph in shape.text_frame.paragraphs:
                                    if img_name in paragraph.text:
                                        # 获取占位符位置
                                        left = shape.left
                                        top = shape.top
                                        width = shape.width
                                        height = shape.height
                                        
                                        # 删除占位符文本框
                                        sp = shape.element
                                        sp.getparent().remove(sp)
                                        
                                        # 插入图片
                                        slide.shapes.add_picture(img_path, left, top, width, height)
                                        log_callback(f"      [OK] 已插入图片 {img_name} (slide {slide_idx+1})")
                                        img_created = True
                                        break
                else:
                    log_callback(f"      [WARN] 图片文件不存在：{img_path}")
        
        # ========== 处理 LINK 类型变量（添加超链接） ==========
        link_placeholders = placeholders.get('placeholders', {}).get('links', {})
        
        if link_placeholders:
            log_callback(f"      检测到 {len(link_placeholders)} 个链接变量")
        
        for link_key, link_config in link_placeholders.items():
            link_name = f'[{link_key}]'
            link_url = link_config.get('url', '')
            
            if link_url:
                link_found = False
                for slide_idx, slide in enumerate(prs.slides):
                    if link_found:
                        break
                    for shape in slide.shapes:
                        if link_found:
                            break
                        if hasattr(shape, 'text_frame'):
                            for paragraph in shape.text_frame.paragraphs:
                                if link_found:
                                    break
                                for run in paragraph.runs:
                                    if link_name in run.text:
                                        # 替换为链接文本
                                        run.text = run.text.replace(link_name, link_url)
                                        # 添加超链接（需要 python-pptx 支持）
                                        try:
                                            run.hyperlink.address = link_url
                                            log_callback(f"      [OK] 已添加超链接 {link_name} (slide {slide_idx+1})")
                                            link_found = True
                                        except Exception as e:
                                            log_callback(f"      [WARN] 超链接添加失败：{e}")
                                            link_found = True
                
                if not link_found:
                    log_callback(f"      [WARN] 未找到链接占位符 {link_name}，请检查 PPT 模板中是否有该文本")
        
        # 保存输出
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # 基于统计汇总文件名生成 PPT 报告名
            base_name = summary_file.replace('_统计汇总.xlsx', '')
            output_name = f'{base_name}_报告_{timestamp}_v1.pptx'
        
        output_path = os.path.join(BASE_DIR, 'output', output_name)
        template_engine.save(prs, output_path)
        
        print("\n" + "=" * 70)
        print(f"[OK] 报告生成完成！")
        print(f"[File] {output_path}")
        print(f"[Insights] {insights_file}")
        print(f"[Placeholders] {template_engine.placeholders_file}")
        print("=" * 70)
        
        return True
        
    except DataQualityError as e:
        log_callback(f"数据质量校验失败：{e}")
        print(f"\n[ERROR] 数据质量校验失败：{e}")
        return False
        
    except Exception as e:
        log_callback(f"生成失败：{e}")
        import traceback
        log_callback(traceback.format_exc())
        print(f"\n[ERROR] 生成失败：{e}")
        return False


if __name__ == "__main__":
    import sys
    
    template_name = sys.argv[1] if len(sys.argv) > 1 else None
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    parallel = '--serial' not in sys.argv
    regenerate = '--regenerate-placeholders' in sys.argv
    
    success = generate_report(
        template_name, 
        output_name, 
        parallel_charts=parallel,
        regenerate_placeholders=regenerate
    )
    sys.exit(0 if success else 1)

