# -*- coding: utf-8 -*-
"""
PPT 配置工具 - Streamlit 应用（模块化版本）
图形化配置 stats_rules.json 和 placeholders.json
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

# 添加 tabs 目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 页面配置
st.set_page_config(
    page_title="PPT 报告配置工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1F4E79;
    text-align: center;
    padding: 1rem 0;
}
.config-section {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">📊 PPT 报告配置工具</h1>', unsafe_allow_html=True)
st.markdown("---")

# 侧边栏 - 项目路径配置
with st.sidebar:
    st.header("⚙️ 项目设置")
    
    default_base_dir = r"C:\Users\50319\Desktop\n8n"
    base_dir = st.text_input("项目根目录", value=default_base_dir)
    
    if not os.path.exists(base_dir):
        st.error("❌ 目录不存在！")
        st.stop()
    
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    
    st.success(f"✅ 项目路径：{base_dir}")
    
    st.markdown("---")
    st.info("💡 **提示**:\n1. 先配置统计规则\n2. 生成测试数据\n3. 配置图表\n4. 导出配置")

# 主功能选择
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 统计规则配置", 
    "📈 图表配置", 
    "💡 洞察配置", 
    "⚙️ 自定义变量", 
    "🎯 结论 & 策略", 
    "🔖 PPT 变量"
])

# 加载配置文件
stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
placeholders_file = os.path.join(templates_dir, "placeholders.json")

# 初始化 stats_config
if 'stats_config' not in st.session_state:
    if os.path.exists(stats_rules_file):
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            st.session_state.stats_config = json.load(f)
    else:
        st.session_state.stats_config = {"version": "1.0", "stats_sheets": {}, "global_settings": {"date_range_auto_detect": True}}

# 加载 placeholders_config
if os.path.exists(placeholders_file):
    with open(placeholders_file, 'r', encoding='utf-8') as f:
        placeholders_config = json.load(f)
else:
    placeholders_config = {"version": "3.0", "placeholders": {"charts": {}, "insights": {}, "text": {}, "tables": {}}}

# ========== Tab 1: 统计规则配置 ==========
with tab1:
    from tabs import render_tab1
    render_tab1(base_dir, templates_dir, output_dir)

# ========== Tab 2: 图表配置 ==========
with tab2:
    from tabs import render_tab2
    render_tab2(templates_dir, output_dir)

# ========== Tab 3: 洞察配置 ==========
with tab3:
    from tabs import render_tab3
    render_tab3(templates_dir)

# ========== Tab 4: 自定义变量 ==========
with tab4:
    from tabs import render_tab4
    render_tab4(templates_dir)

# ========== Tab 5: 结论 & 策略 ==========
with tab5:
    from tabs import render_tab5
    render_tab5(templates_dir)

# ========== Tab 6: PPT 变量总览 ==========
with tab6:
    from tabs import render_tab6
    # 需要最新的 stats_config 和 placeholders_config
    if os.path.exists(stats_rules_file):
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            current_stats = json.load(f)
    else:
        current_stats = {"stats_sheets": {}}
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            current_placeholders = json.load(f)
    else:
        current_placeholders = {"placeholders": {}}
    
    render_tab6(templates_dir, current_stats, current_placeholders)

# 页脚
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'><p>📊 PPT 报告配置工具 v2.0（模块化版本）</p></div>", unsafe_allow_html=True)
