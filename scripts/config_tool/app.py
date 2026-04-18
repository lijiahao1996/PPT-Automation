# -*- coding: utf-8 -*-
"""
PPT 配置工具 - Streamlit 应用（精简版）
图形化配置 stats_rules.json 和 placeholders.json

架构：
- app.py: 主入口（页面初始化 + Tab 渲染）
- app_config.py: 配置和工具函数
- tabs/: 8 个功能页签模块
"""
import streamlit as st
import os
import sys

# 添加 tabs 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入配置
from app_config import (
    PAGE_CONFIG,
    CUSTOM_CSS,
    TAB_LABELS,
    DEFAULT_BASE_DIR,
    get_default_raw_data_filename,
    get_summary_filename,
    validate_path
)

# ========== 页面初始化 ==========
st.set_page_config(**PAGE_CONFIG)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<h1 class="main-header">📊 PPT 报告配置工具</h1>', unsafe_allow_html=True)
st.markdown("---")

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("⚙️ 项目设置")
    
    # 环境检测
    import platform
    is_docker = os.path.exists('/.dockerenv') or os.environ.get('N8N_SCRIPTS_BASE_DIR') == '/app'
    
    if is_docker:
        st.info("🐳 **Docker 环境**")
    else:
        st.info(f"💻 **本地环境** ({platform.system()})")
    
    base_dir = st.text_input("项目根目录", value=DEFAULT_BASE_DIR)
    
    if not validate_path(base_dir):
        st.error("❌ 目录不存在！")
        st.stop()
    
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    
    # 检测 output/uploaded 目录中的文件
    uploaded_dir = os.path.join(output_dir, "uploaded")
    raw_data_file_name = None
    
    if os.path.exists(uploaded_dir):
        for f in os.listdir(uploaded_dir):
            if f.endswith('.xlsx') and not f.startswith('~'):
                raw_data_file_name = f
                break
    
    # 如果没有在 uploaded 中找到，检测 output 根目录（兼容旧版本）
    if not raw_data_file_name and os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                raw_data_file_name = f
                break
    
    # 检测 summary 目录
    summary_dir = os.path.join(output_dir, "summary")
    summary_file_name = None
    
    if os.path.exists(summary_dir):
        for f in os.listdir(summary_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                summary_file_name = f
                break
    
    # 如果没有检测到，使用默认值
    if not raw_data_file_name:
        raw_data_file_name = "未上传"
    if not summary_file_name:
        summary_file_name = "未生成"
    
    st.success(f"✅ 项目路径：{base_dir}")
    st.info(f"📁 **文件配置**:\n- 原始数据：`{raw_data_file_name}`\n- 统计汇总：`{summary_file_name}`")
    
    st.markdown("---")
    st.info("💡 **使用流程**:\n1. 上传 Excel 数据文件\n2. 添加统计规则\n3. 点击【保存配置并生成数据】\n4. 配置图表和洞察\n5. 生成 PPT 报告")

# ========== 主功能 Tabs ==========
tabs = st.tabs(TAB_LABELS)

# ========== Tab 1: 统计规则配置 ==========
with tabs[0]:
    from tabs.tab1_stats_rules import render_tab1
    render_tab1(base_dir, artifacts_dir, output_dir)

# ========== Tab 2: 图表配置 ==========
with tabs[1]:
    from tabs.tab2_chart_config import render_tab2
    render_tab2(artifacts_dir, output_dir, base_dir)

# ========== Tab 3: 洞察配置 ==========
with tabs[2]:
    from tabs.tab3_insight_config import render_tab3
    render_tab3(artifacts_dir)

# ========== Tab 4: 自定义变量 ==========
with tabs[3]:
    from tabs.tab4_custom_vars import render_tab4
    render_tab4(artifacts_dir)

# ========== Tab 5: AI 综合洞察 ==========
with tabs[4]:
    from tabs.tab5_conclusion_strategy import render_tab5
    render_tab5(artifacts_dir)

# ========== Tab 6: PPT 变量总览 ==========
with tabs[5]:
    from tabs.tab6_ppt_vars import render_tab6
    
    # 加载最新配置
    from app_config import load_json_file
    stats_rules_file = os.path.join(artifacts_dir, "stats_rules.json")
    placeholders_file = os.path.join(artifacts_dir, "placeholders.json")
    
    current_stats = load_json_file(stats_rules_file, {"stats_sheets": {}})
    current_placeholders = load_json_file(placeholders_file, {"placeholders": {}})
    
    render_tab6(templates_dir, current_stats, current_placeholders)

# ========== Tab 7: 项目配置 ==========
with tabs[6]:
    from tabs.tab7_project_config import render_tab7
    render_tab7(base_dir)

# ========== Tab 8: 生成 PPT 报告 ==========
with tabs[7]:
    from tabs.tab8_generate_report import render_tab8
    render_tab8(base_dir, output_dir, templates_dir)

# ========== 页脚 ==========
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "<p>📊 PPT 报告配置工具 v5.0 | 企业版</p>"
    "</div>",
    unsafe_allow_html=True
)
