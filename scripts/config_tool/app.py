# -*- coding: utf-8 -*-
"""
PPT 配置工具 - Streamlit 应用
图形化配置 stats_rules.json 和 placeholders.json
"""
import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path

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
    
    # 默认项目根目录
    default_base_dir = r"C:\Users\50319\Desktop\n8n"
    base_dir = st.text_input("项目根目录", value=default_base_dir)
    
    # 验证路径
    if not os.path.exists(base_dir):
        st.error("❌ 目录不存在！")
        st.stop()
    
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    
    st.success(f"✅ 项目路径：{base_dir}")
    
    st.markdown("---")
    st.info("💡 **提示**:\n1. 先配置统计规则\n2. 生成测试数据\n3. 配置图表\n4. 导出配置")

# 主功能选择
tab1, tab2, tab3, tab4 = st.tabs(["📋 统计规则配置", "📈 图表配置", "📊 数据预览", "💾 导出配置"])

# ========== Tab 1: 统计规则配置 ==========
with tab1:
    st.header("📋 统计规则配置")
    st.markdown("配置要生成哪些统计表格（Excel Sheet）")
    
    # 加载现有配置
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
    if os.path.exists(stats_rules_file):
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            stats_config = json.load(f)
        st.success("✅ 已加载现有配置")
    else:
        stats_config = {
            "version": "1.0",
            "stats_sheets": {},
            "global_settings": {
                "date_range_auto_detect": True
            }
        }
        st.info("📝 创建新配置")
    
    # 统计类型选择
    stats_types = {
        "kpi": "📊 核心 KPI - 汇总指标",
        "ranking": "🏆 排名统计 - 销售员/城市排名",
        "composition": "🥧 占比分析 - 产品占比",
        "comparison": "⚖️ 对比分析 - 新老客对比",
        "trend": "📈 趋势分析 - 月度趋势",
        "distribution": "📊 分布分析 - 星期分布",
        "matrix": "🔲 矩阵分析 - 销售员 - 产品",
        "outlier": "⚠️ 异常检测 - 异常订单"
    }
    
    st.subheader("添加统计规则")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sheet_name = st.text_input("统计表格名称", placeholder="例如：销售员业绩")
        stat_type = st.selectbox("统计类型", options=list(stats_types.keys()), format_func=lambda x: stats_types[x])
        enabled = st.checkbox("启用", value=True)
        description = st.text_area("描述", placeholder="例如：销售员业绩排名")
    
    with col2:
        st.markdown("### 分组字段")
        group_fields = st.text_area("分组字段\n（每行一个）", placeholder="销售员\n城市", height=100)
        
        st.markdown("### 统计指标")
        metrics_config = st.text_area("统计指标配置\n（JSON 格式）", 
                                     value='[{"field": "销售额", "agg": "sum", "alias": "总销售额"}]',
                                     height=150)
    
    # 预览配置
    if st.button("➕ 添加统计规则"):
        try:
            metrics = json.loads(metrics_config)
            groups = [g.strip() for g in group_fields.strip().split('\n') if g.strip()]
            
            rule = {
                "description": description,
                "type": stat_type,
                "enabled": enabled,
                "group_by": groups,
                "metrics": metrics
            }
            
            if sheet_name not in stats_config["stats_sheets"]:
                stats_config["stats_sheets"][sheet_name] = rule
                st.success(f"✅ 已添加统计规则：{sheet_name}")
            else:
                st.warning(f"⚠️ 统计规则已存在：{sheet_name}")
        except json.JSONDecodeError as e:
            st.error(f"❌ 指标配置格式错误：{e}")
    
    # 显示现有规则
    st.markdown("---")
    st.subheader("📋 现有统计规则")
    
    if stats_config["stats_sheets"]:
        for name, rule in stats_config["stats_sheets"].items():
            with st.expander(f"{'✅' if rule.get('enabled', True) else '❌'} {name} - {rule.get('description', '')}"):
                st.json(rule)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ 编辑", key=f"edit_{name}"):
                        st.session_state[f"edit_{name}"] = True
                with col2:
                    if st.button(f"🗑️ 删除", key=f"delete_{name}"):
                        del stats_config["stats_sheets"][name]
                        st.rerun()
    else:
        st.info("暂无统计规则，请添加")

# ========== Tab 2: 图表配置 ==========
with tab2:
    st.header("📈 图表配置")
    st.markdown("配置 PPT 中显示的图表")
    
    # 加载现有配置
    placeholders_file = os.path.join(templates_dir, "placeholders.json")
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
        st.success("✅ 已加载现有配置")
    else:
        placeholders_config = {
            "version": "3.0",
            "placeholders": {
                "charts": {},
                "insights": {},
                "text": {}
            }
        }
        st.info("📝 创建新配置")
    
    # 图表类型
    chart_types = {
        "bar_horizontal": "📊 横向条形图",
        "bar_vertical": "📊 纵向柱状图",
        "pie": "🥧 环形饼图",
        "column_clustered": "📊 多列柱状图",
        "line": "📈 折线图",
        "heatmap": "🔥 热力图",
        "scatter": "⚡ 散点图",
        "area": "📊 面积图",
        "histogram": "📊 直方图",
        "boxplot": "📦 箱线图",
        "bubble": "🎈 气泡图",
        "errorbar": "📏 误差棒图",
        "polar": "🎯 极坐标图",
        "violin": "🎻 小提琴图",
        "waterfall": "💧 瀑布图",
        "funnel": "🌀 漏斗图"
    }
    
    st.subheader("添加图表配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_key = st.text_input("图表 Key", placeholder="例如：sales_by_person", help="用于 PPT 占位符：[CHART:xxx]")
        chart_title = st.text_input("图表标题", placeholder="例如：销售员业绩表现分析")
        chart_type = st.selectbox("图表类型", options=list(chart_types.keys()), format_func=lambda x: chart_types[x])
        data_source = st.text_input("数据源", placeholder="Excel Sheet 名称", help="必须与统计规则中的名称一致")
    
    with col2:
        st.markdown("### 字段配置")
        
        if chart_type in ["bar_horizontal", "bar_vertical", "line"]:
            x_field = st.text_input("X 轴字段", placeholder="例如：总销售额")
            y_field = st.text_input("Y 轴字段", placeholder="例如：销售员")
        elif chart_type == "pie":
            x_field = st.text_input("分类字段", placeholder="例如：产品")
            y_field = st.text_input("数值字段", placeholder="例如：占比")
        else:
            x_field = st.text_area("字段配置", placeholder="JSON 格式，根据图表类型配置")
            y_field = ""
    
    description = st.text_area("描述", placeholder="例如：销售员业绩横向条形图")
    
    if st.button("➕ 添加图表配置"):
        if not chart_key or not chart_title or not data_source:
            st.error("❌ 请填写必填字段")
        else:
            chart_config = {
                "description": description,
                "data_source": data_source,
                "chart_type": chart_type,
                "title": chart_title
            }
            
            if chart_type in ["bar_horizontal", "bar_vertical", "line"]:
                chart_config["x_field"] = x_field
                chart_config["y_field"] = y_field
            elif chart_type == "pie":
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            
            key = f"CHART:{chart_key}"
            if key not in placeholders_config["placeholders"]["charts"]:
                placeholders_config["placeholders"]["charts"][key] = chart_config
                st.success(f"✅ 已添加图表配置：{key}")
            else:
                st.warning(f"⚠️ 图表配置已存在：{key}")
    
    # 显示现有图表
    st.markdown("---")
    st.subheader("📊 现有图表配置")
    
    if placeholders_config["placeholders"]["charts"]:
        for key, config in placeholders_config["placeholders"]["charts"].items():
            with st.expander(f"📈 {key} - {config.get('title', '')}"):
                st.json(config)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ 编辑", key=f"edit_chart_{key}"):
                        st.session_state[f"edit_chart_{key}"] = True
                with col2:
                    if st.button(f"🗑️ 删除", key=f"delete_chart_{key}"):
                        del placeholders_config["placeholders"]["charts"][key]
                        st.rerun()
    else:
        st.info("暂无图表配置，请添加")

# ========== Tab 3: 数据预览 ==========
with tab3:
    st.header("📊 数据预览")
    st.markdown("预览统计数据和配置效果")
    
    # 检查是否有统计数据
    summary_file = os.path.join(output_dir, "销售统计汇总.xlsx")
    
    if os.path.exists(summary_file):
        st.success("✅ 找到统计汇总文件")
        
        # 读取所有 Sheet
        xls = pd.ExcelFile(summary_file)
        sheet_names = xls.sheet_names
        
        selected_sheet = st.selectbox("选择 Sheet 预览", sheet_names)
        
        if selected_sheet:
            df = pd.read_excel(summary_file, sheet_name=selected_sheet)
            st.dataframe(df, use_container_width=True)
            
            st.markdown(f"##### 数据信息")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("行数", len(df))
            with col2:
                st.metric("列数", len(df.columns))
            with col3:
                st.metric("字段", ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else ""))
    else:
        st.warning("⚠️ 未找到统计汇总文件，请先运行 Run.bat 生成数据")
        
        st.info("💡 **如何生成数据**:\n1. 配置统计规则\n2. 导出配置\n3. 运行 `Run.bat`\n4. 查看生成的 Excel 文件")

# ========== Tab 4: 导出配置 ==========
with tab4:
    st.header("💾 导出配置")
    st.markdown("保存配置文件并生成 PPT")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("保存统计规则")
        
        if st.button("💾 保存 stats_rules.json", type="primary", use_container_width=True):
            try:
                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                    json.dump(stats_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已保存：{stats_rules_file}")
                
                # 显示文件内容预览
                with st.expander("📄 查看文件内容"):
                    st.json(stats_config)
            except Exception as e:
                st.error(f"❌ 保存失败：{e}")
    
    with col2:
        st.subheader("保存图表配置")
        
        if st.button("💾 保存 placeholders.json", type="primary", use_container_width=True):
            try:
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已保存：{placeholders_file}")
                
                # 显示文件内容预览
                with st.expander("📄 查看文件内容"):
                    st.json(placeholders_config)
            except Exception as e:
                st.error(f"❌ 保存失败：{e}")
    
    st.markdown("---")
    st.subheader("🚀 下一步")
    
    st.markdown("""
    ### 配置完成后：
    
    1. **保存配置文件** - 点击上方的保存按钮
    2. **生成测试数据** - 运行 `Run.bat` 生成 Excel
    3. **验证数据** - 在"数据预览"标签页检查
    4. **配置 PPT 模板** - 在 PPT 中添加占位符
    5. **生成 PPT** - 再次运行 `Run.bat`
    
    ### 快速命令：
    ```bash
    # 方式 1：双击运行
    .\\启动器.bat
    
    # 方式 2：PowerShell
    .\\Run.ps1
    
    # 方式 3：EXE
    .\\PPT 生成.exe
    ```
    """)
    
    # 快捷操作
    if st.button("🚀 直接运行生成 PPT", type="secondary", use_container_width=True):
        st.info("正在启动 Run.bat，请稍候...")
        st.write("提示：请在新的命令行窗口查看运行进度")
        # 这里可以添加自动运行逻辑，但为了安全，建议手动运行

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 PPT 报告配置工具 v1.0 | 让配置更简单</p>
</div>
""", unsafe_allow_html=True)
