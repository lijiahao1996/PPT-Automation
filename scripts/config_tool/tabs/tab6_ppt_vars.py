# -*- coding: utf-8 -*-
"""Tab 6: PPT 变量总览"""
import streamlit as st
import pandas as pd
import json
import os

def render_tab6(templates_dir, stats_config, placeholders_config):
    st.header("🔖 PPT 变量总览")
    st.markdown("动态展示所有已配置的变量，方便在 PPT 模板中使用")
    
    # ========== 1. 文本变量 ==========
    st.subheader("📝 文本变量")
    st.markdown("**使用方法**：在 PPT 模板中插入文本框，输入 `[TEXT:xxx]`")
    
    text_vars = placeholders_config.get('placeholders', {}).get('text', {})
    
    if text_vars:
        text_data = []
        for text_key, text_cfg in text_vars.items():
            text_data.append({
                '占位符': f'[{text_key}]',
                '描述': text_cfg.get('description', ''),
                '默认值': text_cfg.get('default', ''),
                'PPT 页码': str(text_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(text_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无文本变量配置")
    
    st.markdown("---")
    
    # ========== 2. 日期变量 ==========
    st.subheader("📅 日期变量")
    st.markdown("**使用方法**：在 PPT 模板中插入文本框，输入 `[DATE:xxx]`")
    
    date_vars = placeholders_config.get('placeholders', {}).get('dates', {})
    
    if date_vars:
        date_data = []
        for date_key, date_cfg in date_vars.items():
            date_data.append({
                '占位符': f'[{date_key}]',
                '描述': date_cfg.get('description', ''),
                '默认值': date_cfg.get('default', ''),
                '格式': date_cfg.get('format', '%Y-%m-%d'),
                'PPT 页码': str(date_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(date_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无日期变量配置")
    
    st.markdown("---")
    
    # ========== 3. 图片变量 ==========
    st.subheader("🖼️ 图片变量")
    st.markdown("**使用方法**：在 PPT 模板中插入图片占位符 `[IMAGE:xxx]`")
    
    img_vars = placeholders_config.get('placeholders', {}).get('images', {})
    
    if img_vars:
        img_data = []
        for img_key, img_cfg in img_vars.items():
            img_data.append({
                '占位符': f'[{img_key}]',
                '描述': img_cfg.get('description', ''),
                '类型': img_cfg.get('type', 'other'),
                '路径': img_cfg.get('path', ''),
                'PPT 页码': str(img_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(img_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无图片变量配置")
    
    st.markdown("---")
    
    # ========== 4. 视频变量 ==========
    st.subheader("🎬 视频变量")
    st.markdown("**使用方法**：在 PPT 模板中插入视频占位符 `[VIDEO:xxx]`")
    
    video_vars = placeholders_config.get('placeholders', {}).get('videos', {})
    
    if video_vars:
        video_data = []
        for video_key, video_cfg in video_vars.items():
            video_data.append({
                '占位符': f'[{video_key}]',
                '描述': video_cfg.get('description', ''),
                '路径': video_cfg.get('path', ''),
                'PPT 页码': str(video_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(video_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无视频变量配置")
    
    st.markdown("---")
    
    # ========== 5. 链接变量 ==========
    st.subheader("🔗 链接变量")
    st.markdown("**使用方法**：在 PPT 模板中插入超链接占位符 `[LINK:xxx]`")
    
    link_vars = placeholders_config.get('placeholders', {}).get('links', {})
    
    if link_vars:
        link_data = []
        for link_key, link_cfg in link_vars.items():
            link_data.append({
                '占位符': f'[{link_key}]',
                '描述': link_cfg.get('description', ''),
                '类型': link_cfg.get('type', 'url'),
                '链接地址': link_cfg.get('url', ''),
                'PPT 页码': str(link_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(link_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无链接变量配置")
    
    st.markdown("---")
    
    # ========== 6. 图表变量 ==========
    st.subheader("📊 图表变量（动态配置）")
    st.markdown("**使用方法**：在 PPT 模板中插入图表占位符 `[CHART:xxx]`")
    
    charts = placeholders_config.get('placeholders', {}).get('charts', {})
    
    if charts:
        chart_data = []
        for chart_key, chart_cfg in charts.items():
            chart_data.append({
                '占位符': f'[CHART:{chart_key.replace("CHART:", "")}]',
                '图表标题': chart_cfg.get('title', ''),
                '数据源': chart_cfg.get('data_source', ''),
                '图表类型': chart_cfg.get('chart_type', ''),
                'PPT 页码': str(chart_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(chart_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无图表配置")
    
    st.markdown("---")
    
    # ========== 6. 洞察变量 ==========
    st.subheader("💡 洞察变量")
    st.markdown("**使用方法**：在 PPT 模板中插入文本框，输入 `{{INSIGHT:xxx}}`")
    
    insights = placeholders_config.get('placeholders', {}).get('insights', {})
    
    if insights:
        insight_data = []
        for chart_key, insight_cfg in insights.items():
            chart_name = chart_key.replace('CHART:', '')
            insight_data.append({
                '占位符': f'{{{{INSIGHT:{chart_name}}}}}',
                '分析维度': ', '.join(insight_cfg.get('dimensions', [])),
                '关键指标': ', '.join(insight_cfg.get('metrics', [])),
                '对比基准': insight_cfg.get('baseline', ''),
                '洞察风格': insight_cfg.get('style', ''),
                '字数要求': f"{insight_cfg.get('word_count', 150)}字",
                '启用': '✅' if insight_cfg.get('enabled', True) else '❌'
            })
        st.dataframe(pd.DataFrame(insight_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无洞察配置，请在'💡 洞察配置'标签页配置")
    
    st.markdown("---")
    
    # ========== 7. 表格变量 ==========
    st.subheader("📋 表格变量")
    st.markdown("**使用方法**：在 PPT 模板中插入表格占位符 `[TABLE:xxx]`")
    
    table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
    
    if table_vars:
        table_data = []
        for table_key, table_cfg in table_vars.items():
            table_data.append({
                '占位符': f'[{table_key}]',
                '描述': table_cfg.get('description', ''),
                '数据源': table_cfg.get('data_source', ''),
                'PPT 页码': str(table_cfg.get('slide_index', '未设置'))
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
    else:
        st.info("暂无表格变量配置")
    
    st.markdown("---")
    
    # ========== 8. 特殊变量（AI 自动生成） ==========
    st.subheader("🎯 特殊变量（AI 自动生成）")
    st.markdown("💡 **提示**：结论和策略变量可在'🎯 结论 & 策略'标签页中自定义添加、编辑、删除")
    
    special_vars = placeholders_config.get('special_insights', {})
    variables = special_vars.get('variables', [])
    
    if variables:
        for var in variables:
            var_key = var.get('key', '')
            var_name = var.get('name', var_key)
            var_dims = var.get('dimensions', [])
            var_style = var.get('style', '数据驱动')
            var_words = var.get('word_count', 300)
            
            st.info(f"""
            **{var_name}**：
            ```
            {{INSIGHT:{var_key}}}
            ```
            **说明**：{var.get('description', 'AI 自动生成')}
            **分析维度**：{', '.join(var_dims)}
            **风格**：{var_style} | **字数**：{var_words}字
            """)
    else:
        st.info("暂无特殊变量配置，请在'🎯 结论 & 策略'标签页添加")
    
    st.markdown("---")
    st.info("""
    💡 **使用提示**：
    - 以上所有变量均为动态配置，实际显示您已配置的变量
    - 复制占位符到 PPT 模板中的对应位置即可使用
    - 运行 `Run.bat` 时会自动替换为实际内容
    - **文本/日期变量** → 文本框
    - **图片/视频变量** → 媒体占位符
    - **图表/表格变量** → 图表/表格占位符
    - **洞察变量** → AI 自动生成的分析文本
    """)
