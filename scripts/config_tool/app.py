# -*- coding: utf-8 -*-
"""
PPT 配置工具 - Streamlit 应用
图形化配置 stats_rules.json 和 placeholders.json
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 统计规则配置", "📈 图表配置", "💡 洞察配置", "⚙️ 自定义变量", "🎯 结论 & 策略"])

# ========== Tab 1: 统计规则配置 ==========
with tab1:
    st.header("📋 统计规则配置")
    st.markdown("配置要生成哪些统计表格（Excel Sheet）")
    
    # 加载现有配置到 session_state
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
    # 初始化 session_state
    if 'stats_config' not in st.session_state:
        if os.path.exists(stats_rules_file):
            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                st.session_state.stats_config = json.load(f)
            st.success("✅ 已加载现有配置")
        else:
            st.session_state.stats_config = {
                "version": "1.0",
                "stats_sheets": {},
                "global_settings": {
                    "date_range_auto_detect": True
                }
            }
            st.info("📝 创建新配置")
    
    stats_config = st.session_state.stats_config
    
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
            
            if sheet_name not in st.session_state.stats_config["stats_sheets"]:
                st.session_state.stats_config["stats_sheets"][sheet_name] = rule
                
                # 自动保存到文件
                try:
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已添加统计规则：{sheet_name} （已自动保存）")
                except Exception as e:
                    st.error(f"❌ 保存失败：{e}")
                    st.success(f"✅ 已添加统计规则：{sheet_name}")
                
                st.rerun()  # 刷新页面显示更新
            else:
                st.warning(f"⚠️ 统计规则已存在：{sheet_name}")
        except json.JSONDecodeError as e:
            st.error(f"❌ 指标配置格式错误：{e}")
    
    # 操作按钮区域
    st.markdown("---")
    st.subheader("💾 操作")
    
    if st.button("🔄 保存配置并生成数据", type="primary", use_container_width=True, help="保存配置后立即执行统计引擎，生成 Excel Sheet"):
            try:
                # 1. 保存配置
                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                st.info("📝 配置已保存")
                
                # 2. 执行统计引擎生成数据
                with st.spinner("⚙️ 正在执行统计引擎，生成 Excel Sheet..."):
                    # 导入统计引擎
                    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                    from core.stats_engine import StatsEngine
                    from core.data_loader import DataLoader
                    
                    # 加载原始数据
                    data_loader = DataLoader(base_dir)
                    raw_df = data_loader.load_raw_data('帆软销售明细.xlsx')
                    
                    # 执行统计引擎
                    stats_engine = StatsEngine(base_dir=base_dir)
                    output_path = os.path.join(output_dir, '销售统计汇总.xlsx')
                    results = stats_engine.run_all(raw_df, output_path=output_path)
                    
                    st.success(f"✅ 已生成 {len(results)} 个统计 Sheet！")
                    
                    # 显示生成的 Sheet 列表
                    with st.expander("📊 查看生成的 Sheet", expanded=True):
                        for sheet_name, df in results.items():
                            st.write(f"**{sheet_name}**: {len(df)} 行")
                
                st.success("🎉 配置保存并数据生成完成！现在可以去「📈 图表配置」页签配置图表了")
                
            except FileNotFoundError as e:
                st.error(f"❌ 数据文件不存在：{e}\n\n💡 请先确保 output 目录中有 `帆软销售明细.xlsx` 文件")
            except Exception as e:
                st.error(f"❌ 执行失败：{e}")
                import traceback
                with st.expander("📄 查看详细错误"):
                    st.code(traceback.format_exc())
    
    # 显示现有规则
    st.markdown("---")
    st.subheader("📋 现有统计规则")
    
    # 检查是否有正在编辑的配置
    edit_rule_name = st.session_state.get('editing_rule_name', None)
    
    if stats_config["stats_sheets"]:
        for name, rule in stats_config["stats_sheets"].items():
            # 如果是正在编辑的配置，显示编辑表单
            if edit_rule_name == name:
                st.markdown(f"#### ✏️ 编辑：{name}")
                
                edit_sheet_name = st.text_input("统计表格名称", value=name, key=f"edit_sheet_input_{name}")
                edit_type = st.selectbox("统计类型", options=list(stats_types.keys()),
                                        format_func=lambda x: stats_types[x],
                                        index=list(stats_types.keys()).index(rule.get('type', 'kpi')) if rule.get('type') in stats_types.keys() else 0,
                                        key=f"edit_type_{name}")
                edit_enabled = st.checkbox("启用", value=rule.get('enabled', True), key=f"edit_enabled_{name}")
                edit_description = st.text_area("描述", value=rule.get('description', ''), key=f"edit_desc_{name}")
                edit_groups = st.text_area("分组字段（每行一个）", value='\n'.join(rule.get('group_by', [])), key=f"edit_groups_{name}")
                edit_metrics = st.text_area("统计指标配置（JSON 格式）", 
                                           value=json.dumps(rule.get('metrics', []), ensure_ascii=False, indent=2),
                                           key=f"edit_metrics_{name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 保存修改", type="primary", key=f"edit_save_{name}"):
                        try:
                            metrics = json.loads(edit_metrics)
                            groups = [g.strip() for g in edit_groups.strip().split('\n') if g.strip()]
                            
                            new_rule = {
                                "description": edit_description,
                                "type": edit_type,
                                "enabled": edit_enabled,
                                "group_by": groups,
                                "metrics": metrics
                            }
                            
                            # 如果名称改变了，先删除旧的
                            if edit_sheet_name != name:
                                del stats_config["stats_sheets"][name]
                            
                            stats_config["stats_sheets"][edit_sheet_name] = new_rule
                            
                            # 自动保存
                            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            
                            st.session_state['editing_rule_name'] = None
                            st.success("✅ 已保存并自动保存文件")
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"❌ 指标配置格式错误：{e}")
                
                with col2:
                    if st.button("❌ 取消编辑", key=f"edit_cancel_{name}"):
                        st.session_state['editing_rule_name'] = None
                        st.rerun()
                
                st.markdown("---")
            else:
                # 显示配置卡片
                with st.expander(f"{'✅' if rule.get('enabled', True) else '❌'} {name} - {rule.get('description', '')}"):
                    st.json(rule)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ 编辑", key=f"edit_btn_{name}"):
                            st.session_state['editing_rule_name'] = name
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️ 删除", key=f"delete_{name}"):
                            del stats_config["stats_sheets"][name]
                            # 自动保存
                            try:
                                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                    json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"保存失败：{e}")
                            st.rerun()
    else:
        st.info("暂无统计规则，请添加")
    
    # ========== 集成数据概览 ==========
    st.markdown("---")
    st.subheader("📊 数据概览（集成）")
    st.caption("快速查看统计汇总文件，无需切换页签")
    
    summary_file = os.path.join(output_dir, "销售统计汇总.xlsx")
    
    if os.path.exists(summary_file):
        st.success("✅ 找到统计汇总文件")
        
        try:
            xls = pd.ExcelFile(summary_file)
            sheet_names = xls.sheet_names
            
            selected_sheet = st.selectbox("选择 Sheet 预览", sheet_names, key="data_preview_sheet")
            
            if selected_sheet:
                df = pd.read_excel(summary_file, sheet_name=selected_sheet)
                st.dataframe(df, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("行数", len(df))
                with col2:
                    st.metric("列数", len(df.columns))
                with col3:
                    st.metric("字段", ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else ""))
        except Exception as e:
            st.warning(f"⚠️ 预览失败：{e}")
    else:
        st.warning("⚠️ 未找到统计汇总文件，请先运行 Run.bat 生成数据")

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
    
    # 获取可用的数据源（Excel Sheet 列表）
    available_sheets = []
    summary_path = os.path.join(output_dir, '销售统计汇总.xlsx')
    if os.path.exists(summary_path):
        try:
            with pd.ExcelFile(summary_path) as xls:
                available_sheets = xls.sheet_names
        except Exception as e:
            st.warning(f"⚠️ 读取统计汇总失败：{e}")
    
    st.subheader("添加图表配置")
    
    # 提示用户如果没有数据源，先去生成
    if not available_sheets:
        st.warning("⚠️ 未找到统计汇总文件，请先在「📋 统计规则配置」页签点击「🔄 保存配置并生成数据」")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_key = st.text_input("图表 Key", placeholder="例如：sales_by_person", help="用于 PPT 占位符：[CHART:xxx]")
        chart_title = st.text_input("图表标题", placeholder="例如：销售员业绩表现分析")
        chart_type = st.selectbox("图表类型", options=list(chart_types.keys()), format_func=lambda x: chart_types[x])
        
        # 数据源改为下拉选择
        if available_sheets:
            data_source = st.selectbox(
                "数据源",
                options=available_sheets,
                help="选择要使用的 Excel Sheet（来自统计汇总文件）"
            )
            
            # 数据源预览 - 选中后直接显示前 5 行
            if data_source:
                try:
                    df_preview = pd.read_excel(summary_path, sheet_name=data_source, nrows=5)
                    with st.expander(f"📊 预览数据源 '{data_source}' (前 5 行)", expanded=False):
                        st.dataframe(df_preview, use_container_width=True)
                        st.caption(f"共 {len(pd.read_excel(summary_path, sheet_name=data_source))} 行 × {len(df_preview.columns)} 列")
                except Exception as e:
                    st.warning(f"⚠️ 预览失败：{e}")
        else:
            data_source = st.text_input("数据源", placeholder="请先去生成数据", help="必须与统计规则中的名称一致", disabled=True)
    
    with col2:
        st.markdown("### 字段配置")
        
        # 如果选择了数据源，尝试自动读取字段
        auto_fields_info = ""
        available_fields = []
        if data_source and os.path.exists(summary_path):
            try:
                df_temp = pd.read_excel(summary_path, sheet_name=data_source, nrows=1)
                available_fields = df_temp.columns.tolist()
                auto_fields_info = f"📊 可用字段：{', '.join(available_fields)}"
            except Exception:
                pass
        
        # 根据图表类型显示不同的字段输入
        if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel"]:
            # 双字段图表（X 轴 + Y 轴）
            x_field = st.text_input("X 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 轴字段", placeholder="例如：销售员", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "pie":
            # 饼图（分类 + 数值）
            x_field = st.text_input("分类字段", placeholder="例如：产品", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("数值字段", placeholder="例如：占比", help=auto_fields_info if auto_fields_info else None)
        elif chart_type in ["boxplot", "violin"]:
            # 箱线图/小提琴图（分类 + 数值）
            x_field = st.text_input("分类字段", placeholder="例如：城市", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("数值字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "bubble":
            # 气泡图（X + Y + 大小）
            x_field = st.text_input("X 轴字段", placeholder="例如：年龄段", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None)
            size_field = st.text_input("大小字段", placeholder="例如：订单数", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "polar":
            # 极坐标图（角度 + 半径）
            x_field = st.text_input("角度字段", placeholder="例如：星期", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("半径字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None)
        elif chart_type in ["multi_column", "column_clustered", "heatmap"]:
            # 复杂图表（使用 JSON 配置）
            x_field = st.text_area("字段配置", 
                                  placeholder='{"category_field": "销售员", "series": ["产品 A", "产品 B"]}',
                                  help=auto_fields_info if auto_fields_info else None)
            y_field = ""
        else:
            # 其他图表类型
            x_field = st.text_area("字段配置", placeholder="JSON 格式，根据图表类型配置", help=auto_fields_info if auto_fields_info else None)
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
            
            # 根据图表类型保存对应字段
            if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel", "bubble", "polar"]:
                chart_config["x_field"] = x_field
                chart_config["y_field"] = y_field
                # 气泡图额外保存 size_field
                if chart_type == "bubble" and 'size_field' in locals():
                    chart_config["size_field"] = size_field
                # 极坐标图使用 angle_field 和 radius_field 名称
                if chart_type == "polar":
                    chart_config["angle_field"] = x_field
                    chart_config["radius_field"] = y_field
            elif chart_type == "pie":
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["boxplot", "violin"]:
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["multi_column", "column_clustered"]:
                # 解析 JSON 配置
                try:
                    json_config = json.loads(x_field) if x_field else {}
                    if 'category_field' in json_config:
                        chart_config["category_field"] = json_config['category_field']
                    if 'series' in json_config:
                        chart_config["series"] = json_config['series']
                except json.JSONDecodeError:
                    st.warning("⚠️ 字段配置格式错误，将保存为字符串")
                    chart_config["category_field"] = x_field
            elif chart_type == "heatmap":
                # 解析 JSON 配置
                try:
                    json_config = json.loads(x_field) if x_field else {}
                    if 'index_field' in json_config:
                        chart_config["index_field"] = json_config['index_field']
                    if 'columns' in json_config:
                        chart_config["columns"] = json_config['columns']
                except json.JSONDecodeError:
                    st.warning("⚠️ 字段配置格式错误，将保存为字符串")
                    chart_config["index_field"] = x_field
            
            key = f"CHART:{chart_key}"
            if key not in placeholders_config["placeholders"]["charts"]:
                placeholders_config["placeholders"]["charts"][key] = chart_config
                
                # 自动保存到文件
                try:
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已添加图表配置：{key} （已自动保存）")
                except Exception as e:
                    st.error(f"❌ 保存失败：{e}")
                    st.success(f"✅ 已添加图表配置：{key} （请手动保存）")
            else:
                st.warning(f"⚠️ 图表配置已存在：{key}")
    
    # 显示现有图表
    st.markdown("---")
    st.subheader("📊 现有图表配置")
    
    # 检查是否有正在编辑的配置
    edit_key = st.session_state.get('editing_chart_key', None)
    
    if placeholders_config["placeholders"]["charts"]:
        for key, config in placeholders_config["placeholders"]["charts"].items():
            # 如果是正在编辑的配置，显示编辑表单
            if edit_key == key:
                st.markdown(f"#### ✏️ 编辑：{config.get('title', key)}")
                
                edit_chart_key = st.text_input("图表 Key", value=key.replace("CHART:", ""), key=f"edit_key_input_{key}")
                edit_title = st.text_input("图表标题", value=config.get('title', ''), key=f"edit_title_{key}")
                edit_type = st.selectbox("图表类型", options=list(chart_types.keys()), 
                                        format_func=lambda x: chart_types[x],
                                        index=list(chart_types.keys()).index(config.get('chart_type', 'bar_horizontal')) if config.get('chart_type') in chart_types.keys() else 0,
                                        key=f"edit_type_{key}")
                edit_data_source = st.selectbox("数据源", options=available_sheets, 
                                               index=available_sheets.index(config.get('data_source', '')) if config.get('data_source') in available_sheets else 0,
                                               key=f"edit_source_{key}")
                edit_x_field = st.text_input("X 轴字段", value=config.get('x_field', ''), key=f"edit_x_{key}")
                edit_y_field = st.text_input("Y 轴字段", value=config.get('y_field', ''), key=f"edit_y_{key}")
                edit_description = st.text_area("描述", value=config.get('description', ''), key=f"edit_desc_{key}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 保存修改", type="primary", key=f"edit_save_{key}"):
                        new_key = f"CHART:{edit_chart_key}"
                        new_config = {
                            "description": edit_description,
                            "data_source": edit_data_source,
                            "chart_type": edit_type,
                            "title": edit_title,
                        }
                        
                        # 根据图表类型保存对应字段
                        if edit_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter', 'area', 'histogram', 'waterfall', 'funnel']:
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                        elif edit_type == 'pie':
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type in ['multi_column', 'column_clustered']:
                            new_config['category_field'] = edit_x_field
                            # series 字段暂不支持编辑
                        elif edit_type == 'heatmap':
                            new_config['index_field'] = edit_x_field
                            # columns 字段暂不支持编辑
                        elif edit_type in ['boxplot', 'violin']:
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type == 'bubble':
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                            # size_field 暂不支持编辑
                        elif edit_type == 'polar':
                            new_config['angle_field'] = edit_x_field
                            new_config['radius_field'] = edit_y_field
                        
                        # 如果 key 改变了，先删除旧的
                        if new_key != key:
                            del placeholders_config["placeholders"]["charts"][key]
                        
                        placeholders_config["placeholders"]["charts"][new_key] = new_config
                        
                        # 自动保存
                        with open(placeholders_file, 'w', encoding='utf-8') as f:
                            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                        
                        st.session_state['editing_chart_key'] = None
                        st.success("✅ 已保存并自动保存文件")
                        st.rerun()
                
                with col2:
                    if st.button("❌ 取消编辑", key=f"edit_cancel_{key}"):
                        st.session_state['editing_chart_key'] = None
                        st.rerun()
                
                st.markdown("---")
            else:
                # 显示配置卡片
                with st.expander(f"📈 {key} - {config.get('title', '')}"):
                    st.json(config)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"✏️ 编辑", key=f"edit_btn_{key}"):
                            st.session_state['editing_chart_key'] = key
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️ 删除", key=f"delete_chart_{key}"):
                            del placeholders_config["placeholders"]["charts"][key]
                            # 自动保存
                            try:
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"保存失败：{e}")
                            st.rerun()
    else:
        st.info("暂无图表配置，请添加")

# ========== Tab 3: 洞察配置 ==========
with tab3:
    st.header("💡 洞察配置")
    st.markdown("为每个图表配置 AI 洞察分析要点（折叠编辑，修改后自动保存）")
    
    # 加载图表配置
    charts_config = placeholders_config.get("placeholders", {}).get("charts", {})
    
    if not charts_config:
        st.warning("⚠️ 请先在'图表配置'标签页添加图表")
        st.stop()
    
    # 加载已有的洞察配置
    existing_insights = placeholders_config.get("placeholders", {}).get("insights", {})
    
    st.info(f"📊 当前图表数量：{len(charts_config)} | 已配置洞察：{len(existing_insights)}")
    
    # 为每个图表配置洞察要点（折叠 + 实时保存）
    st.subheader("配置洞察分析要点")
    st.caption("💡 未配置的图表默认展开，已配置的自动收起")
    
    insights_config = {}
    
    for i, (chart_key, chart_cfg) in enumerate(charts_config.items(), 1):
        # 尝试加载已有配置
        existing = existing_insights.get(chart_key, {})
        
        # 判断是否已配置（有自定义提示词或修改过默认值）
        is_configured = bool(existing) and (existing.get("custom_prompt") or 
                                            existing.get("dimensions") != ["趋势分析", "对比分析"] or
                                            existing.get("style") != "平衡型")
        
        # 从未配置的默认展开，已配置的默认收起
        expanded = not is_configured
        
        # 从已有配置或默认值加载
        default_dimensions = existing.get("dimensions", ["趋势分析", "对比分析"])
        default_metrics = existing.get("metrics", ["总销售额", "订单数", "客单价"])
        default_baseline = existing.get("baseline", "环比")
        default_style = existing.get("style", "平衡型")
        default_word_count = existing.get("word_count", 150)
        default_enabled = existing.get("enabled", True)
        default_prompt = existing.get("custom_prompt", "")
        
        # 使用折叠容器
        with st.expander(f"📊 {i}. {chart_cfg.get('title', chart_key)}", expanded=expanded):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 分析维度选择
                analysis_dimensions = st.multiselect(
                    "分析维度",
                    options=["趋势分析", "对比分析", "占比分析", "排名分析", "异常检测", "相关性分析", "分布分析"],
                    default=default_dimensions,
                    key=f"dim_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 关键指标
                key_metrics = st.text_area(
                    "关键指标（每行一个）",
                    placeholder="总销售额\n订单数\n客单价",
                    value='\n'.join(default_metrics),
                    key=f"metrics_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 对比基准
                baseline_options = ["环比", "同比", "目标值", "平均值", "头部对比", "尾部对比", "无对比"]
                baseline = st.selectbox(
                    "对比基准",
                    options=baseline_options,
                    index=baseline_options.index(default_baseline) if default_baseline in baseline_options else 0,
                    key=f"baseline_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
            
            with col2:
                # 洞察风格
                style_options = ["数据驱动", "问题导向", "建议导向", "平衡型"]
                insight_style = st.selectbox(
                    "洞察风格",
                    options=style_options,
                    index=style_options.index(default_style) if default_style in style_options else 3,
                    key=f"style_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 字数要求
                word_count = st.slider(
                    "字数要求",
                    min_value=50,
                    max_value=300,
                    value=default_word_count,
                    step=10,
                    key=f"words_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 是否启用
                enabled = st.checkbox("启用", value=default_enabled, key=f"enabled_{chart_key}",
                                     on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config))
            
            # 自定义提示词
            custom_prompt = st.text_area(
                "自定义提示词（可选）",
                placeholder="例如：重点分析头部销售员的业绩贡献度...",
                value=default_prompt,
                height=80,
                key=f"prompt_{chart_key}",
                on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
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
    
    # 实时保存函数
    def save_insights_auto(charts_cfg, p_file, p_config):
        """实时保存洞察配置"""
        current_insights = {}
        for ck in charts_cfg.keys():
            current_insights[ck] = {
                "dimensions": st.session_state.get(f"dim_{ck}", ["趋势分析", "对比分析"]),
                "metrics": [m.strip() for m in st.session_state.get(f"metrics_{ck}", "").split('\n') if m.strip()],
                "baseline": st.session_state.get(f"baseline_{ck}", "环比"),
                "style": st.session_state.get(f"style_{ck}", "平衡型"),
                "word_count": st.session_state.get(f"words_{ck}", 150),
                "enabled": st.session_state.get(f"enabled_{ck}", True),
                "custom_prompt": st.session_state.get(f"prompt_{ck}", "")
            }
        
        p_config["placeholders"]["insights"] = current_insights
        
        try:
            with open(p_file, 'w', encoding='utf-8') as f:
                json.dump(p_config, f, ensure_ascii=False, indent=2)
            st.toast("📊 洞察配置已自动保存", icon="✅")
        except Exception as e:
            st.toast(f"保存失败：{e}", icon="❌")
    
    # 显示配置预览（折叠）
    st.markdown("---")
    st.subheader("📋 洞察配置预览")
    
    if insights_config:
        with st.expander("📋 点击查看/复制配置预览", expanded=False):
            for chart_key, insight_cfg in insights_config.items():
                with st.expander(f"💡 {chart_key}"):
                    st.json(insight_cfg)

# ========== Tab 4: 自定义变量 ==========
with tab4:
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
    
    # ========== 添加日期变量 ==========
    st.subheader("📅 添加自定义日期变量")
    st.caption("💡 使用日历选择日期，自动格式化保存")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        date_var_key = st.text_input("变量 Key", placeholder="例如：report_date", help="占位符：[DATE:report_date]")
        date_var_desc = st.text_input("描述", placeholder="例如：报告生成日期")
    
    with col_d2:
        # 使用日历选择器
        date_var_default_calendar = st.date_input("选择日期", value=None, key="date_calendar")
        date_var_format = st.selectbox("日期格式", options=["%Y-%m-%d", "%Y年%m月%d日", "%Y/%m/%d", "%m-%d", "%Y-%m"], index=0)
        date_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="date_page")
    
    if st.button("➕ 添加日期变量", key="add_date_btn"):
        if not date_var_key:
            st.error("❌ 请填写变量 Key")
        elif date_var_default_calendar is None:
            st.error("❌ 请选择日期")
        else:
            full_key = f"DATE:{date_var_key}"
            # 根据格式转换日期
            date_str = date_var_default_calendar.strftime(date_var_format)
            
            if "placeholders" not in placeholders_config:
                placeholders_config["placeholders"] = {}
            if "dates" not in placeholders_config["placeholders"]:
                placeholders_config["placeholders"]["dates"] = {}
            
            placeholders_config["placeholders"]["dates"][full_key] = {
                "description": date_var_desc,
                "default": date_str,
                "format": date_var_format,
                "slide_index": date_var_page
            }
            
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ 已添加：[{full_key}]（日期：{date_str}）")
            st.rerun()
    
    st.markdown("---")
    st.subheader("📅 已配置的日期变量")
    
    date_vars = placeholders_config.get('placeholders', {}).get('dates', {})
    if date_vars:
        for var_key, var_cfg in date_vars.items():
            with st.expander(f"📅 [{var_key}] - {var_cfg.get('description', '')}"):
                st.json(var_cfg)
                if st.button("🗑️ 删除", key=f"del_{var_key}"):
                    del placeholders_config["placeholders"]["dates"][var_key]
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已删除：[{var_key}]")
                    st.rerun()
    else:
        st.info("暂无日期变量")
    
    st.markdown("---")
    
    # ========== 添加图片变量 ==========
    st.subheader("🖼️ 添加自定义图片变量")
    st.caption("💡 支持上传图片，自动保存到 resources/images 目录")
    
    col_i1, col_i2 = st.columns(2)
    
    with col_i1:
        img_var_key = st.text_input("变量 Key", placeholder="例如：logo", help="占位符：[IMAGE:logo]")
        img_var_desc = st.text_input("描述", placeholder="例如：公司 Logo")
        img_var_type = st.selectbox("图片类型", options=["logo", "product", "chart", "background", "other"], index=0)
    
    with col_i2:
        img_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="img_page")
    
    # 图片上传方式选择（使用 img_page 作为唯一 key）
    img_upload_method = st.radio("图片上传方式", options=["📁 上传本地图片", "🔗 使用已有图片路径"], index=0, key=f"img_method_{img_var_page}")
    
    if img_upload_method == "📁 上传本地图片":
        # 确保 resources/images 目录存在
        images_dir = os.path.join(base_dir, "resources", "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # 使用 img_page 作为唯一 key
        uploaded_file = st.file_uploader("选择图片文件", type=["png", "jpg", "jpeg", "gif", "webp"], key=f"img_file_{img_var_page}")
        
        if uploaded_file is not None:
            # 保存文件到 resources/images
            import shutil
            file_name = uploaded_file.name
            # 如果文件名已存在，添加时间戳
            base_name, ext = os.path.splitext(file_name)
            counter = 1
            while os.path.exists(os.path.join(images_dir, file_name)):
                file_name = f"{base_name}_{counter}{ext}"
                counter += 1
            
            dest_path = os.path.join(images_dir, file_name)
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(uploaded_file, f)
            
            # 相对路径
            relative_path = f"resources/images/{file_name}"
            st.success(f"✅ 图片已上传：{relative_path}")
            
            img_var_path = relative_path
        else:
            img_var_path = None
    else:
        img_var_path = st.text_input("图片路径", placeholder="例如：resources/images/logo.png")
    
    if st.button("➕ 添加图片变量", key="add_img_btn"):
        if not img_var_key:
            st.error("❌ 请填写变量 Key")
        elif not img_var_path:
            st.error("❌ 请上传图片或填写图片路径")
        else:
            full_key = f"IMAGE:{img_var_key}"
            
            if "placeholders" not in placeholders_config:
                placeholders_config["placeholders"] = {}
            if "images" not in placeholders_config["placeholders"]:
                placeholders_config["placeholders"]["images"] = {}
            
            placeholders_config["placeholders"]["images"][full_key] = {
                "description": img_var_desc,
                "path": img_var_path,
                "type": img_var_type,
                "slide_index": img_var_page
            }
            
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ 已添加：[{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("🖼️ 已配置的图片变量")
    
    img_vars = placeholders_config.get('placeholders', {}).get('images', {})
    if img_vars:
        for var_key, var_cfg in img_vars.items():
            with st.expander(f"🖼️ [{var_key}] - {var_cfg.get('description', '')}"):
                st.json(var_cfg)
                if st.button("🗑️ 删除", key=f"del_{var_key}"):
                    del placeholders_config["placeholders"]["images"][var_key]
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已删除：[{var_key}]")
                    st.rerun()
    else:
        st.info("暂无图片变量")
    
    st.markdown("---")
    
    # ========== 添加链接变量 ==========
    st.subheader("🔗 添加自定义链接变量")
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        link_var_key = st.text_input("变量 Key", placeholder="例如：website", help="占位符：[LINK:website]")
        link_var_desc = st.text_input("描述", placeholder="例如：公司官网")
        link_var_type = st.selectbox("链接类型", options=["url", "email", "file"], index=0)
    
    with col_l2:
        link_var_url = st.text_input("链接地址", placeholder="例如：https://www.example.com")
        link_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="link_page")
    
    if st.button("➕ 添加链接变量", key="add_link_btn"):
        if not link_var_key or not link_var_url:
            st.error("❌ 请填写变量 Key 和链接地址")
        else:
            full_key = f"LINK:{link_var_key}"
            
            if "placeholders" not in placeholders_config:
                placeholders_config["placeholders"] = {}
            if "links" not in placeholders_config["placeholders"]:
                placeholders_config["placeholders"]["links"] = {}
            
            placeholders_config["placeholders"]["links"][full_key] = {
                "description": link_var_desc,
                "url": link_var_url,
                "type": link_var_type,
                "slide_index": link_var_page
            }
            
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"✅ 已添加：[{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("🔗 已配置的链接变量")
    
    link_vars = placeholders_config.get('placeholders', {}).get('links', {})
    if link_vars:
        for var_key, var_cfg in link_vars.items():
            with st.expander(f"🔗 [{var_key}] - {var_cfg.get('description', '')}"):
                st.json(var_cfg)
                if st.button("🗑️ 删除", key=f"del_{var_key}"):
                    del placeholders_config["placeholders"]["links"][var_key]
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已删除：[{var_key}]")
                    st.rerun()
    else:
        st.info("暂无链接变量")
    
    st.markdown("---")
    st.info("💡 **提示**：\n- 所有变量添加/删除时自动保存，无需手动保存\n- 文本变量：`[TEXT:xxx]` | 日期：`[DATE:xxx]` | 图片：`[IMAGE:xxx]` | 链接：`[LINK:xxx]` | 表格：`[TABLE:xxx]`")

# ========== Tab 5: 结论 & 策略 ==========
with tab5:
    st.header("🎯 结论 & 策略配置")
    st.markdown("自定义 AI 生成的核心结论和落地策略（支持自定义 Skill 和变量）")
    
    # 加载配置
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {"placeholders": {}, "special_insights": {}}
    
    # 初始化 special_insights
    if "special_insights" not in placeholders_config:
        placeholders_config["special_insights"] = {
            "conclusion": {
                "description": "AI 自动生成核心结论",
                "dimensions": ["业绩结构", "增长亮点", "核心短板", "业务风险"],
                "style": "数据驱动",
                "word_count": 300,
                "custom_prompt": ""
            },
            "strategy": {
                "description": "AI 自动生成落地策略",
                "dimensions": ["客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略"],
                "style": "建议导向",
                "word_count": 400,
                "custom_prompt": ""
            }
        }
    
    st.subheader("📝 核心结论配置")
    st.caption("💡 修改后自动保存")
    
    conclusion_cfg = placeholders_config["special_insights"].get("conclusion", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        conclusion_desc = st.text_area(
            "结论说明",
            value=conclusion_cfg.get("description", "AI 自动生成核心结论"),
            height=60,
            key="conclusion_desc",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
        
        conclusion_dimensions = st.multiselect(
            "分析维度（可选 4 条）",
            options=["业绩结构", "增长亮点", "核心短板", "业务风险", "趋势分析", "对比分析", "占比分析", "异常检测"],
            default=conclusion_cfg.get("dimensions", ["业绩结构", "增长亮点", "核心短板", "业务风险"]),
            key="conclusion_dims",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
    
    with col2:
        conclusion_style = st.selectbox(
            "洞察风格",
            options=["数据驱动", "问题导向", "建议导向", "平衡型"],
            index=["数据驱动", "问题导向", "建议导向", "平衡型"].index(conclusion_cfg.get("style", "数据驱动")) if conclusion_cfg.get("style") in ["数据驱动", "问题导向", "建议导向", "平衡型"] else 3,
            key="conclusion_style",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
        
        conclusion_words = st.slider(
            "字数要求",
            min_value=100,
            max_value=500,
            value=conclusion_cfg.get("word_count", 300),
            step=50,
            key="conclusion_words",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
    
    conclusion_prompt = st.text_area(
        "自定义生成提示词（可选，留空使用默认）",
        value=conclusion_cfg.get("custom_prompt", ""),
        height=150,
        placeholder="请输入结论生成的详细提示词，包括分析维度、格式要求等。留空则使用默认提示词。",
        key="conclusion_prompt",
        on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
    )
    
    st.markdown("---")
    st.subheader("📝 落地策略配置")
    st.caption("💡 修改后自动保存")
    
    strategy_cfg = placeholders_config["special_insights"].get("strategy", {})
    
    col3, col4 = st.columns(2)
    
    with col3:
        strategy_desc = st.text_area(
            "策略说明",
            value=strategy_cfg.get("description", "AI 自动生成落地策略"),
            height=60,
            key="strategy_desc",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
        
        strategy_dimensions = st.multiselect(
            "策略维度（可选 4 条）",
            options=["客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略", "渠道拓展", "数字化转型", "供应链优化", "风控体系"],
            default=strategy_cfg.get("dimensions", ["客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略"]),
            key="strategy_dims",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
    
    with col4:
        strategy_style = st.selectbox(
            "洞察风格",
            options=["数据驱动", "问题导向", "建议导向", "平衡型"],
            index=["数据驱动", "问题导向", "建议导向", "平衡型"].index(strategy_cfg.get("style", "建议导向")) if strategy_cfg.get("style") in ["数据驱动", "问题导向", "建议导向", "平衡型"] else 2,
            key="strategy_style",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
        
        strategy_words = st.slider(
            "字数要求",
            min_value=200,
            max_value=600,
            value=strategy_cfg.get("word_count", 400),
            step=50,
            key="strategy_words",
            on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
        )
    
    strategy_prompt = st.text_area(
        "自定义生成提示词（可选，留空使用默认）",
        value=strategy_cfg.get("custom_prompt", ""),
        height=150,
        placeholder="请输入策略生成的详细提示词，包括策略维度、可执行性要求等。留空则使用默认提示词。",
        key="strategy_prompt",
        on_change=lambda: save_conclusion_strategy(placeholders_file, placeholders_config)
    )
    
    st.markdown("---")
    st.subheader("🔖 结论策略变量")
    st.info("""
    **结论变量**：`{{INSIGHT:conclusion}}`
    
    **策略变量**：`{{INSIGHT:strategy}}`
    
    💡 **提示**：
    - 在 PPT 模板中插入文本框，输入上述占位符
    - 运行 `Run.bat` 时 AI 会根据配置自动生成内容
    - 所有修改会自动保存到 `placeholders.json` 和 `skills/data-insight/SKILL.md`
    """)
    
    # 实时保存函数
    def save_conclusion_strategy(p_file, p_config):
        """实时保存结论策略配置"""
        p_config["special_insights"] = {
            "conclusion": {
                "description": st.session_state.get("conclusion_desc", "AI 自动生成核心结论"),
                "dimensions": st.session_state.get("conclusion_dims", ["业绩结构", "增长亮点", "核心短板", "业务风险"]),
                "style": st.session_state.get("conclusion_style", "数据驱动"),
                "word_count": st.session_state.get("conclusion_words", 300),
                "custom_prompt": st.session_state.get("conclusion_prompt", "")
            },
            "strategy": {
                "description": st.session_state.get("strategy_desc", "AI 自动生成落地策略"),
                "dimensions": st.session_state.get("strategy_dims", ["客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略"]),
                "style": st.session_state.get("strategy_style", "建议导向"),
                "word_count": st.session_state.get("strategy_words", 400),
                "custom_prompt": st.session_state.get("strategy_prompt", "")
            }
        }
        
        try:
            with open(p_file, 'w', encoding='utf-8') as f:
                json.dump(p_config, f, ensure_ascii=False, indent=2)
            st.toast("🎯 结论策略配置已自动保存", icon="✅")
        except Exception as e:
            st.toast(f"保存失败：{e}", icon="❌")


