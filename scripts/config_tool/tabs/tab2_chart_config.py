# -*- coding: utf-8 -*-
"""Tab 2: 图表配置 - AI 增强版"""
import streamlit as st
import pandas as pd
import json
import os

def render_tab2(templates_dir, output_dir, base_dir=None):
    st.header("📈 图表配置")
    st.markdown("配置 PPT 中显示的图表")
    
    placeholders_file = os.path.join(templates_dir, "placeholders.json")
    
    # 加载配置
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
    
    # ========== 动态检测统计汇总文件 ==========
    available_sheets = []
    summary_path = None
    summary_file_name = None
    
    # 优先使用 session_state 中记录的上传文件名
    if 'uploaded_file_name' in st.session_state:
        uploaded_name = st.session_state['uploaded_file_name']
        if uploaded_name.endswith('.xlsx'):
            summary_name = uploaded_name.replace('.xlsx', '_统计汇总.xlsx')
        else:
            summary_name = uploaded_name + '_统计汇总.xlsx'
        summary_path = os.path.join(output_dir, summary_name)
        summary_file_name = summary_name
    
    # 如果没有，自动检测 output 目录中的统计汇总文件
    if not summary_path or not os.path.exists(summary_path):
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                summary_path = os.path.join(output_dir, f)
                summary_file_name = f
                break
    
    # 读取 Sheet 列表
    if summary_path and os.path.exists(summary_path):
        try:
            with pd.ExcelFile(summary_path) as xls:
                available_sheets = xls.sheet_names
        except Exception as e:
            st.warning(f"⚠️ 读取统计汇总失败：{e}")
    
    st.subheader("添加图表配置")
    
    if not available_sheets:
        st.warning("⚠️ 未找到统计汇总文件，请先在「📋 统计规则配置」页签点击「▶ 执行统计并生成 Excel」")
    else:
        st.info(f"📊 当前统计汇总：`{summary_file_name}`，共 {len(available_sheets)} 个 Sheet")
    
    # ========== AI 智能分析 ===========
    st.subheader("🤖 AI 智能分析")
    
    use_ai = st.checkbox("✨ 使用 AI 自动推荐图表配置", value=False, key="tab2_use_ai")
    
    if use_ai and available_sheets:
        if st.button("🤖 开始 AI 智能分析", type="primary", key="tab2_start_ai"):
            try:
                # 分析每个 Sheet 的数据特征
                sheet_analysis = []
                for sheet_name in available_sheets:
                    df = pd.read_excel(summary_path, sheet_name=sheet_name, nrows=5)
                    sheet_info = {
                        'name': sheet_name,
                        'columns': df.columns.tolist(),
                        'row_count': len(pd.read_excel(summary_path, sheet_name=sheet_name)),
                        'sample': df.head(3).to_dict('records')
                    }
                    sheet_analysis.append(sheet_info)
                
                st.session_state['sheet_analysis'] = sheet_analysis
                
                # 调用 AI（使用 chart-config-recommender SKILL）
                from ai.qwen_client import QwenClient
                qwen = QwenClient(base_dir=base_dir)
                
                if qwen.is_available():
                    # 读取 SKILL.md
                    skill_path = os.path.join(base_dir, 'skills', 'chart-config-recommender', 'SKILL.md')
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        skill_content = f.read()
                    
                    # 构建 Prompt
                    prompt = f"""
请根据以下统计 Sheet 数据，推荐合适的图表配置：

统计汇总文件：{summary_file_name}
统计 Sheet 列表:
{json.dumps(sheet_analysis, ensure_ascii=False, indent=2)}

{skill_content}

请根据 SKILL 中的规则，推荐图表配置。
"""
                    
                    system_prompt = "你是数据可视化专家，输出严格 JSON 格式。只输出 JSON，不要任何其他文字。"
                    response = qwen.chat(system_prompt, prompt, json_mode=True)
                    
                    if response:
                        result = qwen.parse_json_response(response)
                        if result and 'chart_recommendations' in result:
                            st.session_state['ai_chart_recommendations'] = result['chart_recommendations']
                            st.success(f"🤖 AI 推荐了 {len(result['chart_recommendations'])} 个图表配置")
                            st.rerun()
                    else:
                        st.warning("⚠️ AI 未返回有效结果")
                else:
                    st.warning("⚠️ Qwen API Key 未配置，无法使用 AI 推荐")
            
            except Exception as e:
                st.error(f"❌ AI 分析失败：{e}")
                import traceback
                with st.expander("📄 查看详细错误"):
                    st.code(traceback.format_exc())
    
    # 显示 AI 推荐列表
    if 'ai_chart_recommendations' in st.session_state:
        recommendations = st.session_state['ai_chart_recommendations']
        
        if recommendations:
            st.markdown("### AI 推荐图表列表")
            
            for i, rec in enumerate(recommendations):
                already_added = False
                existing_charts = placeholders_config.get('placeholders', {}).get('charts', {})
                for chart_key in existing_charts.keys():
                    if chart_key == f"CHART:{rec.get('chart_key', '')}":
                        already_added = True
                        break
                
                # 折叠后显示：图表名 + 添加/删除按钮
                col_title, col_btn = st.columns([4, 1])
                
                with col_title:
                    status_icon = "✅" if already_added else "⬜"
                    st.write(f"{status_icon} **{rec.get('chart_title', '')}** - {rec.get('reason', '')}")
                
                with col_btn:
                    if already_added:
                        # 已添加：显示删除按钮
                        if st.button("🗑️ 删除", key=f"del_chart_{rec.get('chart_key', '')}_{i}", use_container_width=True):
                            chart_key = f"CHART:{rec.get('chart_key', '')}"
                            if chart_key in placeholders_config.get('placeholders', {}).get('charts', {}):
                                del placeholders_config['placeholders']['charts'][chart_key]
                                
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                
                                st.session_state.stats_config = placeholders_config
                                st.rerun()
                    else:
                        # 未添加：显示添加按钮
                        if st.button("➕ 添加并保存", key=f"add_chart_{rec.get('chart_key', '')}_{i}", use_container_width=True):
                            chart_config = {
                                "description": rec.get('reason', ''),
                                "data_source": rec.get('data_source', ''),
                                "chart_type": rec.get('chart_type', 'bar_horizontal'),
                                "title": rec.get('chart_title', ''),
                                "x_field": rec.get('x_field', ''),
                                "y_field": rec.get('y_field', '')
                            }
                            
                            chart_key = f"CHART:{rec.get('chart_key', '')}"
                            placeholders_config.setdefault('placeholders', {}).setdefault('charts', {})[chart_key] = chart_config
                            
                            with open(placeholders_file, 'w', encoding='utf-8') as f:
                                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                            
                            st.session_state.stats_config = placeholders_config
                            st.rerun()
                
                # 展开查看详情
                with st.expander("查看配置详情", expanded=False):
                    st.json(rec)
            
            # 一键保存按钮放在最下面
            st.markdown("---")
            if st.button("🚀 一键保存所有推荐图表", type="primary", use_container_width=True, key="save_all_charts"):
                added_count = 0
                for rec in recommendations:
                    chart_key = f"CHART:{rec.get('chart_key', '')}"
                    if chart_key not in placeholders_config.get('placeholders', {}).get('charts', {}):
                        chart_config = {
                            "description": rec.get('reason', ''),
                            "data_source": rec.get('data_source', ''),
                            "chart_type": rec.get('chart_type', 'bar_horizontal'),
                            "title": rec.get('chart_title', ''),
                            "x_field": rec.get('x_field', ''),
                            "y_field": rec.get('y_field', '')
                        }
                        placeholders_config.setdefault('placeholders', {}).setdefault('charts', {})[chart_key] = chart_config
                        added_count += 1
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                
                if added_count > 0:
                    st.success(f"✅ 已一键保存 {added_count} 个图表配置")
                    st.balloons()
                    st.session_state['ai_chart_recommendations'] = []
                    st.info("💡 配置已保存，请滚动到下方查看'现有图表配置'")
                else:
                    st.info("ℹ️ 所有推荐图表都已添加")
    
    st.markdown("---")
    
    # ========== 手动添加图表配置 ==========
    st.subheader("📝 手动添加图表配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_key = st.text_input("图表 Key", placeholder="例如：sales_by_person", help="用于 PPT 占位符：[CHART:xxx]", key="chart_key_input")
        chart_title = st.text_input("图表标题", placeholder="例如：销售员业绩表现分析", key="chart_title_input")
        chart_type = st.selectbox("图表类型", options=list(chart_types.keys()), format_func=lambda x: chart_types[x], key="chart_type_select")
        
        if available_sheets:
            data_source = st.selectbox("数据源", options=available_sheets, help="选择要使用的 Excel Sheet", key="data_source_select")
            if data_source:
                try:
                    df_preview = pd.read_excel(summary_path, sheet_name=data_source, nrows=5)
                    with st.expander(f"📊 预览数据源 '{data_source}' (前 5 行)", expanded=False):
                        st.dataframe(df_preview, use_container_width=True, width='stretch')
                        st.caption(f"共 {len(pd.read_excel(summary_path, sheet_name=data_source))} 行 × {len(df_preview.columns)} 列")
                except Exception as e:
                    st.warning(f"⚠️ 预览失败：{e}")
        else:
            data_source = st.text_input("数据源", placeholder="请先去生成数据", disabled=True, key="data_source_input")
    
    with col2:
        st.markdown("### 字段配置")
        auto_fields_info = ""
        available_fields = []
        if data_source and summary_path and os.path.exists(summary_path):
            try:
                df_temp = pd.read_excel(summary_path, sheet_name=data_source, nrows=1)
                available_fields = df_temp.columns.tolist()
                auto_fields_info = f"📊 可用字段：{', '.join(available_fields)}"
            except Exception:
                pass
        
        if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel"]:
            x_field = st.text_input("X 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None, key="x_field_input")
            y_field = st.text_input("Y 轴字段", placeholder="例如：销售员", help=auto_fields_info if auto_fields_info else None, key="y_field_input")
        elif chart_type == "pie":
            x_field = st.text_input("分类字段", placeholder="例如：产品", help=auto_fields_info if auto_fields_info else None, key="x_field_pie")
            y_field = st.text_input("数值字段", placeholder="例如：占比", help=auto_fields_info if auto_fields_info else None, key="y_field_pie")
        elif chart_type in ["boxplot", "violin"]:
            x_field = st.text_input("分类字段", placeholder="例如：城市", help=auto_fields_info if auto_fields_info else None, key="x_field_box")
            y_field = st.text_input("数值字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_box")
        elif chart_type == "bubble":
            x_field = st.text_input("X 轴字段", placeholder="例如：年龄段", help=auto_fields_info if auto_fields_info else None, key="x_field_bubble")
            y_field = st.text_input("Y 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_bubble")
            size_field = st.text_input("大小字段", placeholder="例如：订单数", help=auto_fields_info if auto_fields_info else None, key="size_field_bubble")
        elif chart_type == "polar":
            x_field = st.text_input("角度字段", placeholder="例如：星期", help=auto_fields_info if auto_fields_info else None, key="x_field_polar")
            y_field = st.text_input("半径字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_polar")
        else:
            x_field = st.text_area("字段配置", placeholder="JSON 格式", help=auto_fields_info if auto_fields_info else None, key="x_field_json")
            y_field = ""
    
    description = st.text_area("描述", placeholder="例如：销售员业绩横向条形图", key="chart_desc_input")
    
    if st.button("➕ 添加图表配置", key="add_chart_manual"):
        if not chart_key or not chart_title or not data_source:
            st.error("❌ 请填写必填字段")
        else:
            chart_config = {
                "description": description,
                "data_source": data_source,
                "chart_type": chart_type,
                "title": chart_title
            }
            
            if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel", "bubble", "polar"]:
                chart_config["x_field"] = x_field
                chart_config["y_field"] = y_field
                if chart_type == "bubble" and 'size_field_bubble' in st.session_state and st.session_state.size_field_bubble:
                    chart_config["size_field"] = st.session_state.size_field_bubble
            elif chart_type == "pie":
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["boxplot", "violin"]:
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            
            key = f"CHART:{chart_key}"
            if key not in placeholders_config.setdefault('placeholders', {}).setdefault('charts', {}):
                placeholders_config['placeholders']['charts'][key] = chart_config
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                
                st.success(f"✅ 已添加图表配置：{key}")
                st.balloons()
                st.rerun()
            else:
                st.warning(f"⚠️ 图表配置已存在：{key}")
    
    st.markdown("---")
    st.subheader("📊 现有图表配置")
    
    # 重新加载最新配置
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    
    charts = placeholders_config.get('placeholders', {}).get('charts', {})
    
    if charts:
        for chart_key, chart_cfg in charts.items():
            # 折叠后显示：图表名 + 编辑/删除按钮
            col_title, col_btn1, col_btn2 = st.columns([3, 1, 1])
            
            with col_title:
                with st.expander(f"📈 {chart_key} - {chart_cfg.get('title', '')}", expanded=False):
                    st.json(chart_cfg)
            
            with col_btn1:
                if st.button("✏️ 编辑", key=f"edit_chart_{chart_key}", use_container_width=True):
                    st.session_state['editing_chart'] = chart_key
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️ 删除", key=f"delete_chart_{chart_key}", use_container_width=True):
                    del placeholders_config['placeholders']['charts'][chart_key]
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.rerun()
            
            # 编辑模式
            if st.session_state.get('editing_chart') == chart_key:
                st.markdown(f"#### ✏️ 编辑：{chart_key}")
                
                edit_key = st.text_input("图表 Key", value=chart_key.replace('CHART:', ''), key=f"edit_key_{chart_key}")
                edit_title = st.text_input("图表标题", value=chart_cfg.get('title', ''), key=f"edit_title_{chart_key}")
                edit_type = st.selectbox("图表类型", options=list(chart_types.keys()), 
                                        format_func=lambda x: chart_types[x],
                                        index=list(chart_types.keys()).index(chart_cfg.get('chart_type', 'bar_horizontal')) if chart_cfg.get('chart_type') in chart_types.keys() else 0,
                                        key=f"edit_type_{chart_key}")
                edit_source = st.selectbox("数据源", options=available_sheets, 
                                          index=available_sheets.index(chart_cfg.get('data_source', '')) if chart_cfg.get('data_source', '') in available_sheets else 0,
                                          key=f"edit_source_{chart_key}")
                edit_x = st.text_input("X 轴字段", value=chart_cfg.get('x_field', ''), key=f"edit_x_{chart_key}")
                edit_y = st.text_input("Y 轴字段", value=chart_cfg.get('y_field', ''), key=f"edit_y_{chart_key}")
                edit_desc = st.text_area("描述", value=chart_cfg.get('description', ''), key=f"edit_desc_{chart_key}")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 保存修改", type="primary", key=f"edit_save_{chart_key}"):
                        new_key = f"CHART:{edit_key}"
                        new_config = {
                            "description": edit_desc,
                            "data_source": edit_source,
                            "chart_type": edit_type,
                            "title": edit_title,
                            "x_field": edit_x,
                            "y_field": edit_y
                        }
                        
                        # 如果 key 改变了，先删除旧的
                        if new_key != chart_key:
                            del placeholders_config['placeholders']['charts'][chart_key]
                        
                        placeholders_config['placeholders']['charts'][new_key] = new_config
                        
                        with open(placeholders_file, 'w', encoding='utf-8') as f:
                            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                        
                        st.session_state['editing_chart'] = None
                        st.success("✅ 已保存修改")
                        st.rerun()
                
                with col_cancel:
                    if st.button("❌ 取消编辑", key=f"edit_cancel_{chart_key}"):
                        st.session_state['editing_chart'] = None
                        st.rerun()
    else:
        st.info("暂无图表配置")
