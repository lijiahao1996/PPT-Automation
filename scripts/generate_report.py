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
def build_skill_always():
    """每次运行时都重新生成 SKILL.md（确保包含最新的 special_insights 配置）"""
    stats_rules_path = os.path.join(BASE_DIR, 'templates', 'stats_rules.json')
    placeholders_path = os.path.join(BASE_DIR, 'templates', 'placeholders.json')
    skill_path = os.path.join(BASE_DIR, 'skills', 'data-insight', 'SKILL.md')
    skill_builder_path = os.path.join(BASE_DIR, 'skills', 'data-insight', 'skill_builder.py')
    
    logger.info("正在重新生成 SKILL.md (包含最新的 special_insights 配置)...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("skill_builder", skill_builder_path)
        skill_builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(skill_builder)
        
        skill_builder.build_skill_from_config(
            stats_rules_path=stats_rules_path,
            placeholders_path=placeholders_path,
            output_path=skill_path
        )
        logger.info("✅ SKILL.md 已重新生成")
    except Exception as e:
        logger.warning(f"⚠️ SKILL.md 生成失败：{e}，使用现有文件")

# 在生成报告前构建 SKILL（每次都重新生成）
build_skill_always()
# ====================================


# 注意：图表配置已从 placeholders.json 读取
# CHART_CONFIGS 已移除


def _generate_single_chart(args: Tuple) -> Tuple[str, str]:
    """生成单个图表（用于并行执行）"""
    chart_key, config, data_summary, chart_engine, temp_dir = args
    
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
                logger.info(f"      [INFO] 热力图自动检测到 {len(product_cols)} 个产品：{product_cols}")
            chart_engine.create_heatmap(df, **params)
        elif chart_type in ['multi_column', 'column_clustered']:
            chart_engine.create_multi_column(df, **params)
        else:
            logger.warning(f"      [SKIP] 未知图表类型：{chart_type}")
            return (chart_key, None)
        
        return (chart_key, output_path)
    
    except Exception as e:
        logger.error(f"      [ERROR] 生成图表 {chart_key} 失败：{e}")
        return (chart_key, None)


def _get_date_range_from_data(data_loader) -> str:
    """从原始数据中动态提取日期范围"""
    import pandas as pd
    try:
        df = data_loader.load_raw_data('帆软销售明细.xlsx')
        if '订单时间' in df.columns:
            df['订单时间'] = pd.to_datetime(df['订单时间'], errors='coerce')
            min_date = df['订单时间'].min().strftime('%Y年%m月%d日')
            max_date = df['订单时间'].max().strftime('%Y年%m月%d日')
            return f'{min_date} - {max_date}'
    except Exception as e:
        logger.warning(f"日期范围提取失败：{e}, 使用默认值")
    return "未知"


def _build_text_replacements_from_config(placeholders: Dict, data_loader, insights: list, today: str) -> Dict:
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
            date_range = _get_date_range_from_data(data_loader)
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
                logger.info("      [OK] KPI 卡片已从实际数据生成")
            except Exception as e:
                logger.warning(f"      [WARN] KPI 数据加载失败：{e}, 使用空值")
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
                logger.warning(f"      图片文件不存在：{img_path}")
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
                logger.warning(f"      视频文件不存在：{video_path}")
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
            logger.warning(f"      洞察数量不足：{full_key}")
    
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
        logger.warning(f"      洞察数量不足，期望{insight_count+2}条，实际{len(insights)}条")
    
    logger.info(f"      动态构建 {len(replacements)} 个文本占位符替换规则（{len(insight_placeholders)} 个洞察 + 结论 + 策略 + 文本变量）")
    return replacements


def _build_chart_placeholder_map_from_config(placeholders: Dict, chart_paths: Dict) -> Dict:
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
            logger.warning(f"      图表未生成：[{key}] (缺少数据：{config.get('data_source', '未知')})")
    
    logger.info(f"      动态构建 {len(placeholder_map)} 个图表占位符映射")
    return placeholder_map


def generate_report(template_name: str = None, output_name: str = None, 
                    parallel_charts: bool = True, regenerate_placeholders: bool = False):
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
        logger.info("\n[1/5] 加载销售统计数据...")
        data_loader = DataLoader(BASE_DIR)
        
        # 自动查找统计汇总文件
        summary_file = None
        output_dir = os.path.join(BASE_DIR, 'output')
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                summary_file = f
                break
        
        data_summary = data_loader.load_summary(filename=summary_file)
        logger.info(f"      已加载 {len(data_summary)} 个统计表（文件：{summary_file}）")
        
        validator = PresetValidators.summary_data_validator(data_summary)
        logger.info("      [OK] 数据校验通过")
        
        # ========== 2. 初始化引擎 ==========
        logger.info("\n[2/5] 初始化引擎...")
        chart_engine = ChartEngine(BASE_DIR)
        template_engine = TemplateEngine(BASE_DIR, auto_scan=True)
        insight_generator = InsightGenerator(BASE_DIR)
        
        # 可选：重新生成占位符配置
        if regenerate_placeholders and template_name:
            logger.info("      [INFO] 重新生成占位符配置...")
            template_engine.regenerate_placeholders_from_template(template_name)
        
        # 获取占位符配置
        placeholders = template_engine.get_placeholder_config()
        logger.info(f"      [OK] 引擎初始化完成 (占位符：{len(placeholders.get('placeholders', {}))} 类)")
        
        # ========== 3. 生成 AI 洞察 ==========
        logger.info("\n[3/5] 生成 AI 洞察...")
        insights_file = os.path.join(BASE_DIR, 'artifacts', 'ai_insights.json')
        insights = insight_generator.generate(data_summary, insights_file)
        logger.info(f"      [OK] 生成 {len(insights)} 条洞察")
        
        # ========== 4. 生成图表（支持并行） ==========
        logger.info("\n[4/5] 生成图表...")
        temp_dir = os.path.join(BASE_DIR, 'artifacts', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        chart_paths = {}
        
        # 从 placeholders.json 读取图表配置
        chart_placeholders = placeholders.get('placeholders', {}).get('charts', {})
        
        if parallel_charts:
            logger.info("      [INFO] 使用并行模式生成图表...")
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
                
                tasks.append((chart_key, task_config, data_summary, chart_engine, temp_dir))
            
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {executor.submit(_generate_single_chart, task): task[0] for task in tasks}
                
                for future in as_completed(futures):
                    chart_key, path = future.result()
                    if path and os.path.exists(path):
                        chart_paths[chart_key] = path
                        logger.info(f"      [OK] {chart_key}: {path}")
        else:
            # 串行生成（略，同上）
            logger.warning("      [WARN] 串行模式暂不支持动态配置，请使用并行模式")
        
        logger.info(f"      [OK] 共生成 {len(chart_paths)} 个图表")
        
        # ========== 5. 填充模板（动态占位符） ==========
        logger.info("\n[5/5] 填充 PPT 模板...")
        
        if template_name is None:
            template_name = '销售分析报告_标准模板.pptx'
        
        prs = template_engine.load_template(template_name)
        
        # 准备日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 动态构建文本替换字典（传入 data_loader 以获取实际 KPI 数据）
        text_replacements = _build_text_replacements_from_config(placeholders, data_loader, insights, today)
        logger.info(f"      {len(insights)} 条洞察已全部添加到替换列表")
        
        # 替换文本占位符
        template_engine.replace_text_placeholders(prs, text_replacements)
        logger.info("      [OK] 文本占位符已替换")
        
        # 动态构建图表占位符映射（只循环一次）
        placeholder_map = _build_chart_placeholder_map_from_config(placeholders, chart_paths)
        
        replaced_count = 0
        for placeholder, chart_path in placeholder_map.items():
            if chart_path and os.path.exists(chart_path):
                if template_engine.replace_with_chart(prs, placeholder, chart_path):
                    replaced_count += 1
        
        logger.info(f"      [OK] 图表占位符已替换 ({replaced_count} 个图表)")
        
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
                                        
                                        logger.info(f"      [OK] 已生成表格 {table_name} (slide {slide_idx+1})")
                                        table_created = True
                                        break
            else:
                logger.warning(f"      [WARN] 表格数据源不存在：{data_source}")
        
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
                                        logger.info(f"      [OK] 已插入图片 {img_name} (slide {slide_idx+1})")
                                        img_created = True
                                        break
                else:
                    logger.warning(f"      [WARN] 图片文件不存在：{img_path}")
        
        # ========== 处理 LINK 类型变量（添加超链接） ==========
        link_placeholders = placeholders.get('placeholders', {}).get('links', {})
        
        if link_placeholders:
            logger.info(f"      检测到 {len(link_placeholders)} 个链接变量")
        
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
                                            logger.info(f"      [OK] 已添加超链接 {link_name} (slide {slide_idx+1})")
                                            link_found = True
                                        except Exception as e:
                                            logger.warning(f"      [WARN] 超链接添加失败：{e}")
                                            link_found = True
                
                if not link_found:
                    logger.warning(f"      [WARN] 未找到链接占位符 {link_name}，请检查 PPT 模板中是否有该文本")
        
        # 保存输出
        if output_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # 基于统计汇总文件名生成 PPT 报告名
            summary_file_name = None
            output_dir = os.path.join(BASE_DIR, 'output')
            for f in os.listdir(output_dir):
                if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                    summary_file_name = f
                    break
            
            if summary_file_name:
                # 从统计汇总文件名提取原始数据文件名
                # 例如：要测试的数据_统计汇总.xlsx → 要测试的数据
                base_name = summary_file_name.replace('_统计汇总.xlsx', '')
                output_name = f'{base_name}_报告_{timestamp}_v1.pptx'
            else:
                output_name = f'销售分析报告_{timestamp}_v1.pptx'
        
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
        logger.error(f"数据质量校验失败：{e}")
        print(f"\n[ERROR] 数据质量校验失败：{e}")
        return False
        
    except Exception as e:
        logger.error(f"生成失败：{e}", exc_info=True)
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
