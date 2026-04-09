# -*- coding: utf-8 -*-
"""Tab 2: 图表配置"""
import streamlit as st
import pandas as pd
import json
import os

def render_tab2(templates_dir, output_dir):
    st.header("📈 图表配置")
    st.markdown("配置 PPT 中显示的图表")
    
    placeholders_file = os.path.join(templates_dir, "placeholders.json")
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
        st.success("✅ 已加载现有配置")
    else:
        placeholders_config = {"version": "3.0", "placeholders": {"charts": {}, "insights": {}, "text": {}}}
        st.info("📝 创建新配置")
    
    chart_types = {
        "bar_horizontal": "📊 横向条形图", "bar_vertical": "📊 纵向柱状图",
        "pie": "🥧 环形饼图", "column_clustered": "📊 多列柱状图",
        "line": "📈 折线图", "heatmap": "🔥 热力图", "scatter": "⚡ 散点图",
        "area": "📊 面积图", "histogram": "📊 直方图", "boxplot": "📦 箱线图",
        "bubble": "🎈 气泡图", "errorbar": "📏 误差棒图", "polar": "🎯 极坐标图",
        "violin": "🎻 小提琴图", "waterfall": "💧 瀑布图", "funnel": "🌀 漏斗图"
    }
    
    available_sheets = []
    summary_path = os.path.join(output_dir, '销售统计汇总.xlsx')
    if os.path.exists(summary_path):
        try:
            with pd.ExcelFile(summary_path) as xls:
                available_sheets = xls.sheet_names
        except Exception as e:
            st.warning(f"⚠️ 读取统计汇总失败：{e}")
    
    st.subheader("添加图表配置")
    
    if not available_sheets:
        st.warning("⚠️ 未找到统计汇总文件，请先在「📋 统计规则配置」页签点击「🔄 保存配置并生成数据」")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_key = st.text_input("图表 Key", placeholder="例如：sales_by_person", help="用于 PPT 占位符：[CHART:xxx]")
        chart_title = st.text_input("图表标题", placeholder="例如：销售员业绩表现分析")
        chart_type = st.selectbox("图表类型", options=list(chart_types.keys()), format_func=lambda x: chart_types[x])
        
        if available_sheets:
            data_source = st.selectbox("数据源", options=available_sheets, help="选择要使用的 Excel Sheet")
            if data_source:
                try:
                    df_preview = pd.read_excel(summary_path, sheet_name=data_source, nrows=5)
                    with st.expander(f"📊 预览数据源 '{data_source}' (前 5 行)", expanded=False):
                        st.dataframe(df_preview, use_container_width=True, width='stretch')
                        st.caption(f"共 {len(pd.read_excel(summary_path, sheet_name=data_source))} 行 × {len(df_preview.columns)} 列")
                except Exception as e:
                    st.warning(f"⚠️ 预览失败：{e}")
        else:
            data_source = st.text_input("数据源", placeholder="请先去生成数据", disabled=True)
    
    with col2:
        st.markdown("### 字段配置")
        auto_fields_info = ""
        available_fields = []
        if data_source and os.path.exists(summary_path):
            try:
                df_temp = pd.read_excel(summary_path, sheet_name=data_source, nrows=1)
                available_fields = df_temp.columns.tolist()
                auto_fields_info = f"📊 可用字段：{', '.join(available_fields)}"
            except Exception:
                pass
        
        if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel"]:
            x_field = st.text_input("X 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 轴字段", placeholder="例如：销售员", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "pie":
            x_field = st.text_input("分类字段", placeholder="例如：产品", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("数值字段", placeholder="例如：占比", help=auto_fields_info if auto_fields_info else None)
        elif chart_type in ["boxplot", "violin"]:
            x_field = st.text_input("分类字段", placeholder="例如：城市", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("数值字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "bubble":
            x_field = st.text_input("X 轴字段", placeholder="例如：年龄段", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None)
            size_field = st.text_input("大小字段", placeholder="例如：订单数", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "polar":
            x_field = st.text_input("角度字段", placeholder="例如：星期", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("半径字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None)
        else:
            x_field = st.text_area("字段配置", placeholder="JSON 格式", help=auto_fields_info if auto_fields_info else None)
            y_field = ""
    
    description = st.text_area("描述", placeholder="例如：销售员业绩横向条形图")
    
    if st.button("➕ 添加图表配置"):
        if not chart_key or not chart_title or not data_source:
            st.error("❌ 请填写必填字段")
        else:
            chart_config = {"description": description, "data_source": data_source, "chart_type": chart_type, "title": chart_title}
            
            if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel", "bubble", "polar"]:
                chart_config["x_field"] = x_field
                chart_config["y_field"] = y_field
                if chart_type == "bubble" and 'size_field' in locals():
                    chart_config["size_field"] = size_field
                if chart_type == "polar":
                    chart_config["angle_field"] = x_field
                    chart_config["radius_field"] = y_field
            elif chart_type == "pie":
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["boxplot", "violin"]:
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            
            key = f"CHART:{chart_key}"
            if key not in placeholders_config["placeholders"]["charts"]:
                placeholders_config["placeholders"]["charts"][key] = chart_config
                try:
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已添加图表配置：{key}（已自动保存）")
                except Exception as e:
                    st.error(f"❌ 保存失败：{e}")
                    st.success(f"✅ 已添加图表配置：{key}")
            else:
                st.warning(f"⚠️ 图表配置已存在：{key}")
    
    st.markdown("---")
    st.subheader("📊 现有图表配置")
    
    edit_key = st.session_state.get('editing_chart_key', None)
    
    if placeholders_config["placeholders"]["charts"]:
        for key, config in placeholders_config["placeholders"]["charts"].items():
            if edit_key == key:
                st.markdown(f"#### ✏️ 编辑：{config.get('title', key)}")
                edit_chart_key = st.text_input("图表 Key", value=key.replace("CHART:", ""), key=f"edit_key_input_{key}")
                edit_title = st.text_input("图表标题", value=config.get('title', ''), key=f"edit_title_{key}")
                edit_type = st.selectbox("图表类型", options=list(chart_types.keys()), 
                                        format_func=lambda x: chart_types[x],
                                        index=list(chart_types.keys()).index(config.get('chart_type', 'bar_horizontal')) if config.get('chart_type') in chart_types.keys() else 0,
                                        key=f"edit_type_{key}")
                edit_data_source = st.selectbox("数据源", options=available_sheets, key=f"edit_source_{key}")
                edit_x_field = st.text_input("X 轴字段", value=config.get('x_field', ''), key=f"edit_x_{key}")
                edit_y_field = st.text_input("Y 轴字段", value=config.get('y_field', ''), key=f"edit_y_{key}")
                edit_description = st.text_area("描述", value=config.get('description', ''), key=f"edit_desc_{key}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 保存修改", type="primary", key=f"edit_save_{key}"):
                        new_key = f"CHART:{edit_chart_key}"
                        new_config = {"description": edit_description, "data_source": edit_data_source, "chart_type": edit_type, "title": edit_title}
                        if edit_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter', 'area', 'histogram', 'waterfall', 'funnel']:
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                        elif edit_type == 'pie':
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type in ['boxplot', 'violin']:
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type == 'bubble':
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                        elif edit_type == 'polar':
                            new_config['angle_field'] = edit_x_field
                            new_config['radius_field'] = edit_y_field
                        
                        if new_key != key:
                            del placeholders_config["placeholders"]["charts"][key]
                        placeholders_config["placeholders"]["charts"][new_key] = new_config
                        
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
                            try:
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"保存失败：{e}")
                            st.rerun()
    else:
        st.info("暂无图表配置，请添加")
