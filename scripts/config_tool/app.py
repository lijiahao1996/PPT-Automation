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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📋 统计规则配置", "📈 图表配置", "💡 洞察配置", "🔖 PPT 变量", "📊 数据预览", "💾 导出配置", "⚙️ 自定义变量"])

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

# ========== Tab 3: 洞察配置 ==========
with tab3:
    st.header("💡 洞察配置")
    st.markdown("为每个图表配置 AI 洞察分析要点")
    
    # 加载图表配置
    charts_config = placeholders_config.get("placeholders", {}).get("charts", {})
    
    if not charts_config:
        st.warning("⚠️ 请先在'图表配置'标签页添加图表")
        st.stop()
    
    st.info(f"📊 当前图表数量：{len(charts_config)}")
    
    # 为每个图表配置洞察要点
    st.subheader("配置洞察分析要点")
    
    insights_config = {}
    
    for i, (chart_key, chart_cfg) in enumerate(charts_config.items(), 1):
        st.markdown(f"### {i}. {chart_cfg.get('title', chart_key)}")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 分析维度选择
            analysis_dimensions = st.multiselect(
                "分析维度",
                options=["趋势分析", "对比分析", "占比分析", "排名分析", "异常检测", "相关性分析", "分布分析"],
                default=["趋势分析", "对比分析"],
                key=f"dim_{chart_key}"
            )
            
            # 关键指标
            key_metrics = st.text_area(
                "关键指标（每行一个）",
                placeholder="总销售额\n订单数\n客单价",
                key=f"metrics_{chart_key}"
            )
            
            # 对比基准
            baseline = st.selectbox(
                "对比基准",
                options=["环比", "同比", "目标值", "平均值", "头部对比", "尾部对比", "无对比"],
                index=0,
                key=f"baseline_{chart_key}"
            )
        
        with col2:
            # 洞察风格
            insight_style = st.selectbox(
                "洞察风格",
                options=["数据驱动", "问题导向", "建议导向", "平衡型"],
                index=3,
                key=f"style_{chart_key}"
            )
            
            # 字数要求
            word_count = st.slider(
                "字数要求",
                min_value=50,
                max_value=300,
                value=150,
                step=50,
                key=f"words_{chart_key}"
            )
            
            # 是否启用
            enabled = st.checkbox("启用", value=True, key=f"enabled_{chart_key}")
        
        # 自定义提示词
        custom_prompt = st.text_area(
            "自定义提示词（可选）",
            placeholder="例如：重点分析头部销售员的业绩贡献度...",
            height=80,
            key=f"prompt_{chart_key}"
        )
        
        # 保存配置
        insights_config[chart_key] = {
            "dimensions": analysis_dimensions,
            "metrics": [m.strip() for m in key_metrics.split('\n') if m.strip()],
            "baseline": baseline,
            "style": insight_style,
            "word_count": word_count,
            "enabled": enabled,
            "custom_prompt": custom_prompt
        }
        
        st.markdown("---")
    
    # 保存洞察配置
    if st.button("💾 保存洞察配置", type="primary"):
        # 更新 placeholders.json
        placeholders_config["placeholders"]["insights"] = insights_config
        
        with open(placeholders_file, 'w', encoding='utf-8') as f:
            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
        
        st.success(f"✅ 已保存 {len(insights_config)} 个图表的洞察配置")
        st.balloons()
    
    # 显示配置预览
    st.markdown("---")
    st.subheader("📋 洞察配置预览")
    
    if insights_config:
        for chart_key, insight_cfg in insights_config.items():
            with st.expander(f"💡 {chart_key}"):
                st.json(insight_cfg)

# ========== Tab 4: PPT 变量可视化 ==========
with tab4:
    st.header("🔖 PPT 变量可视化")
    st.markdown("动态展示所有已配置的变量，方便在 PPT 模板中使用")
    
    # 加载配置
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        st.warning("⚠️ 配置文件不存在")
        st.stop()
    
    # 统计变量数量
    charts_count = len(placeholders_config.get('placeholders', {}).get('charts', {}))
    insights_count = len(placeholders_config.get('placeholders', {}).get('insights', {}))
    text_vars_count = len(placeholders_config.get('placeholders', {}).get('text', {}))
    tables_count = len(placeholders_config.get('placeholders', {}).get('tables', {}))
    total_count = charts_count + insights_count + text_vars_count + tables_count + 2  # +2 for conclusion & strategy
    
    st.metric("变量总数", total_count, f"图表{charts_count} + 洞察{insights_count} + 文本{text_vars_count} + 表格{tables_count} + 特殊 2")
    
    st.markdown("---")
    st.subheader("📊 图表变量（动态配置）")
    st.markdown("""
    **使用方法**：在 PPT 模板中插入文本框，输入以下占位符：
    ```
    [CHART:xxx]
    ```
    """)
    
    charts = placeholders_config.get('placeholders', {}).get('charts', {})
    
    if charts:
        chart_data = []
        for chart_key, chart_cfg in charts.items():
            chart_data.append({
                '占位符': f'[CHART:{chart_key.replace("CHART:", "")}]',
                '图表标题': chart_cfg.get('title', ''),
                '数据源': chart_cfg.get('data_source', ''),
                '图表类型': chart_cfg.get('chart_type', ''),
                'PPT 页码': chart_cfg.get('slide_index', '未设置')
            })
        
        st.dataframe(chart_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无图表配置")
    
    st.markdown("---")
    st.subheader("💡 洞察变量")
    st.markdown("""
    **使用方法**：在 PPT 模板中插入文本框，输入以下占位符：
    ```
    {{INSIGHT:xxx}}
    ```
    """)
    
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
        
        st.dataframe(insight_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无洞察配置，请在'💡 洞察配置'标签页配置")
    
    st.markdown("---")
    st.subheader("📝 文本变量")
    st.markdown("""
    **使用方法**：在 PPT 模板中插入文本框，输入以下占位符：
    ```
    [TEXT:xxx]
    ```
    """)
    
    text_vars = placeholders_config.get('placeholders', {}).get('text', {})
    
    if text_vars:
        text_data = []
        for text_key, text_cfg in text_vars.items():
            text_data.append({
                '占位符': f'[{text_key}]',
                '描述': text_cfg.get('description', ''),
                '默认值': text_cfg.get('default', ''),
                'PPT 页码': text_cfg.get('slide_index', '未设置')
            })
        
        st.dataframe(text_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无文本变量配置")
    
    st.markdown("---")
    st.subheader("📊 KPI 卡片变量")
    st.markdown("""
    **使用方法**：在 PPT 模板中插入文本框，输入以下占位符：
    ```
    [KPI:cards]
    ```
    **说明**：自动生成 5 个核心 KPI 卡片（总销售额、总订单数、平均客单价、最高单额、最低单额）
    """)
    
    st.info("📌 KPI 卡片变量固定为 `[KPI:cards]`，自动生成 5 个指标")
    
    st.markdown("---")
    st.subheader("📋 表格变量")
    st.markdown("""
    **使用方法**：在 PPT 模板中插入文本框，输入以下占位符：
    ```
    [TABLE:xxx]
    ```
    """)
    
    table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
    
    if table_vars:
        table_data = []
        for table_key, table_cfg in table_vars.items():
            table_data.append({
                '占位符': f'[{table_key}]',
                '描述': table_cfg.get('description', ''),
                '数据源': table_cfg.get('data_source', ''),
                'PPT 页码': table_cfg.get('slide_index', '未设置')
            })
        
        st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.info("暂无表格变量配置")
    
    st.markdown("---")
    st.subheader("🎯 特殊变量（AI 自动生成）")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **结论变量**：
        ```
        {{INSIGHT:conclusion}}
        ```
        **说明**：AI 自动生成 4 条核心结论
        - 业绩结构
        - 增长亮点
        - 核心短板
        - 业务风险
        """)
    
    with col2:
        st.info("""
        **策略变量**：
        ```
        {{INSIGHT:strategy}}
        ```
        **说明**：AI 自动生成 4 条落地策略
        - 客户运营策略
        - 产品组合策略
        - 团队管理策略
        - 营销节奏策略
        """)
    
    st.markdown("---")
    st.info("""💡 **提示**：
- 以上所有变量均为动态配置，实际显示您已配置的变量
- 复制占位符到 PPT 模板中的文本框即可使用
- 运行 `Run.bat` 时会自动替换为实际内容""")

# ========== Tab 5: 数据预览 ==========
with tab5:
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

# ========== Tab 6: 导出配置 ==========
with tab6:
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
        st.subheader("保存完整配置")
        
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
    ### 配置流程：
    
    1. **配置统计规则** - 在"📋 统计规则配置"标签页
    2. **配置图表** - 在"📈 图表配置"标签页
    3. **配置洞察** - 在"💡 洞察配置"标签页
    4. **自定义变量** - 在"⚙️ 自定义变量"标签页（可选）
    5. **查看变量** - 在"🔖 PPT 变量"标签页确认
    6. **保存配置** - 点击上方的保存按钮
    7. **生成 PPT** - 运行 `Run.bat`
    
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

# ========== Tab 7: 自定义变量 ==========
with tab7:
    st.header("⚙️ 自定义变量")
    st.markdown("自定义 PPT 模板中的变量，完全自由配置")
    
    # 加载配置
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {
            "placeholders": {
                "charts": {},
                "insights": {},
                "text": {},
                "tables": {}
            }
        }
    
    st.subheader("📝 添加自定义文本变量")
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_var_key = st.text_input(
            "变量 Key",
            placeholder="例如：custom_title",
            help="用于 PPT 占位符：[TEXT:custom_title]"
        )
        
        custom_var_desc = st.text_input(
            "变量描述",
            placeholder="例如：自定义标题"
        )
    
    with col2:
        custom_var_default = st.text_area(
            "默认值",
            placeholder="例如：销售数据分析报告",
            height=80
        )
        
        custom_var_page = st.number_input(
            "PPT 页码",
            min_value=0,
            max_value=20,
            value=0,
            help="占位符所在的 PPT 页码（从 0 开始）"
        )
    
    if st.button("➕ 添加自定义变量", type="primary"):
        if not custom_var_key:
            st.error("❌ 请填写变量 Key")
        else:
            full_key = f"TEXT:{custom_var_key}"
            
            if "placeholders" not in placeholders_config:
                placeholders_config["placeholders"] = {}
            
            if "text" not in placeholders_config["placeholders"]:
                placeholders_config["placeholders"]["text"] = {}
            
            placeholders_config["placeholders"]["text"][full_key] = {
                "description": custom_var_desc,
                "default": custom_var_default,
                "slide_index": custom_var_page
            }
            
            # 保存配置
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ 已添加自定义变量：[{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📋 已配置的自定义变量")
    
    text_vars = placeholders_config.get('placeholders', {}).get('text', {})
    
    if text_vars:
        for var_key, var_cfg in text_vars.items():
            if var_key.startswith('TEXT:'):
                with st.expander(f"📝 [{var_key}] - {var_cfg.get('description', '')}"):
                    st.json(var_cfg)
                    
                    if st.button(f"🗑️ 删除", key=f"delete_{var_key}"):
                        del placeholders_config["placeholders"]["text"][var_key]
                        
                        with open(placeholders_file, 'w', encoding='utf-8') as f:
                            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                        
                        st.success(f"✅ 已删除：[{var_key}]")
                        st.rerun()
    else:
        st.info("暂无自定义变量")
    
    st.markdown("---")
    st.subheader("📋 添加自定义表格变量")
    
    col3, col4 = st.columns(2)
    
    with col3:
        table_var_key = st.text_input(
            "表格变量 Key",
            placeholder="例如：custom_table",
            help="用于 PPT 占位符：[TABLE:custom_table]"
        )
        
        table_var_desc = st.text_input(
            "表格描述",
            placeholder="例如：自定义数据表"
        )
        
        table_var_source = st.text_input(
            "数据源",
            placeholder="Excel Sheet 名称，例如：自定义统计"
        )
    
    with col4:
        table_var_page = st.number_input(
            "PPT 页码",
            min_value=0,
            max_value=20,
            value=0,
            key="table_page"
        )
    
    if st.button("➕ 添加自定义表格变量"):
        if not table_var_key:
            st.error("❌ 请填写表格变量 Key")
        else:
            full_key = f"TABLE:{table_var_key}"
            
            if "placeholders" not in placeholders_config:
                placeholders_config["placeholders"] = {}
            
            if "tables" not in placeholders_config["placeholders"]:
                placeholders_config["placeholders"]["tables"] = {}
            
            placeholders_config["placeholders"]["tables"][full_key] = {
                "description": table_var_desc,
                "data_source": table_var_source,
                "slide_index": table_var_page
            }
            
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ 已添加自定义表格变量：[{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📋 已配置的自定义表格变量")
    
    table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
    
    if table_vars:
        for var_key, var_cfg in table_vars.items():
            with st.expander(f"📋 [{var_key}] - {var_cfg.get('description', '')}"):
                st.json(var_cfg)
                
                if st.button(f"🗑️ 删除", key=f"delete_table_{var_key}"):
                    del placeholders_config["placeholders"]["tables"][var_key]
                    
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ 已删除：[{var_key}]")
                    st.rerun()
    else:
        st.info("暂无自定义表格变量")
    
    st.markdown("---")
    st.info("💡 **提示**：\n- 自定义变量后，在 PPT 模板中插入文本框，输入对应的占位符\n- 文本变量：`[TEXT:xxx]`\n- 表格变量：`[TABLE:xxx]`\n- 运行 `Run.bat` 时会自动替换")
# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 PPT 报告配置工具 v1.0 | 让配置更简单</p>
</div>
""", unsafe_allow_html=True)
