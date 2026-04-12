# -*- coding: utf-8 -*-
"""Tab 2: 图表配置 - AI 增强版"""
import streamlit as st
import pandas as pd
import json
import os
import sys

def render_tab2(artifacts_dir, output_dir, base_dir=None):
    st.header("📈 图表配置")
    st.markdown("配置 PPT 中显示的图表")
    
    placeholders_file = os.path.join(artifacts_dir, "placeholders.json")
    
    # 获取目录结构
    from app_config import get_output_dirs, ensure_output_dirs
    dirs = ensure_output_dirs(base_dir)
    summary_dir = dirs['summary']
    
    # 加载配置
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
        st.success("✅ 已加载现有配置")
    else:
        placeholders_config = {"version": "3.0", "placeholders": {"charts": {}, "insights": {}, "text": {}}}
        st.info("📝 创建新配置")
    
    chart_types = {
        "bar_horizontal": "横向条形图", "bar_vertical": "纵向柱状图",
        "pie": "环形饼图", "column_clustered": "多列柱状图",
        "line": "折线图", "heatmap": "热力图", "scatter": "散点图",
        "area": "面积图", "histogram": "直方图", "boxplot": "箱线图",
        "bubble": "气泡图", "errorbar": "误差棒图", "polar": "极坐标图",
        "violin": "小提琴图", "waterfall": "瀑布图", "funnel": "漏斗图"
    }
    
    # ========== 统计汇总文件选择 ==========
    st.subheader("📊 选择统计汇总 Excel")
    
    # 获取 summary 目录下的所有统计汇总文件
    summary_files = []
    if os.path.exists(summary_dir):
        summary_files = [f for f in os.listdir(summary_dir) 
                        if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~')]
        summary_files.sort(reverse=True)  # 最新的在前
    
    # 优先使用 session_state 中记录的文件名（Tab 1 刚生成的）
    if 'generated_summary_name' in st.session_state and st.session_state['generated_summary_name'] in summary_files:
        default_index = summary_files.index(st.session_state['generated_summary_name'])
    else:
        default_index = 0
    
    if summary_files:
        selected_summary = st.selectbox(
            "选择统计汇总文件",
            options=summary_files,
            index=min(default_index, len(summary_files) - 1),
            key="summary_file_select"
        )
        
        # 更新 session_state
        if selected_summary != st.session_state.get('selected_summary_name'):
            st.session_state['selected_summary_name'] = selected_summary
            st.rerun()
    else:
        st.warning("⚠️ 暂无统计汇总文件，请先在「📋 统计规则配置」页签生成数据")
        selected_summary = None
    
    # 读取 Sheet 列表
    available_sheets = []
    summary_path = None
    
    if selected_summary:
        summary_path = os.path.join(summary_dir, selected_summary)
        if os.path.exists(summary_path):
            try:
                with pd.ExcelFile(summary_path) as xls:
                    available_sheets = xls.sheet_names
                st.info(f"📊 当前统计汇总：`{selected_summary}`，共 {len(available_sheets)} 个 Sheet")
            except Exception as e:
                st.warning(f"⚠️ 读取统计汇总失败：{e}")
    
    st.markdown("---")
    
    # ========== 添加图表配置 ==========
    st.subheader("添加图表配置")
    
    if not available_sheets:
        st.warning("⚠️ 未找到统计汇总文件，请先在「📋 统计规则配置」页签点击「▶ 执行统计并生成 Excel」")
    else:
        # AI 智能分析
        st.subheader("🤖 AI 智能分析")
        
        use_ai = st.checkbox("✨ 使用 AI 自动推荐图表配置", value=False, key="tab2_use_ai")
        
        if use_ai and available_sheets:
            if st.button("🤖 开始 AI 智能分析", type="primary", key="tab2_start_ai"):
                try:
                    # 分析每个 Sheet 的数据特征
                    sheet_analysis = []
                    for sheet_name in available_sheets:
                        df = pd.read_excel(summary_path, sheet_name=sheet_name, nrows=5)
                        # 将 Timestamp 转换为字符串
                        sample_data = []
                        for _, row in df.head(3).iterrows():
                            row_dict = {}
                            for col, val in row.items():
                                if hasattr(val, 'strftime'):  # Timestamp
                                    row_dict[col] = val.strftime('%Y-%m-%d')
                                else:
                                    row_dict[col] = val
                            sample_data.append(row_dict)
                        
                        sheet_info = {
                            'name': sheet_name,
                            'columns': df.columns.tolist(),
                            'row_count': len(pd.read_excel(summary_path, sheet_name=sheet_name)),
                            'sample': sample_data
                        }
                        sheet_analysis.append(sheet_info)
                    
                    st.session_state['sheet_analysis'] = sheet_analysis
                    
                    # 调用 AI（使用 chart-config-recommender SKILL）
                    if base_dir:
                        scripts_dir = os.path.join(base_dir, 'scripts')
                        if scripts_dir not in sys.path:
                            sys.path.insert(0, scripts_dir)
                        
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

统计汇总文件：{selected_summary}
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
                                    "title": rec.get('chart_title', '')
                                }
                                
                                # 根据图表类型转换字段名（支持 AI 输出的多种字段名）
                                chart_type = rec.get('chart_type', '')
                                
                                # 收集所有可能的字段（AI 可能输出不同的字段名）
                                all_fields = {}
                                for k, v in rec.items():
                                    if k not in ['chart_key', 'chart_title', 'data_source', 'chart_type', 'description', 'reason']:
                                        all_fields[k] = v
                                
                                if chart_type == 'pie':
                                    # 饼图：需要 category_field 和 value_field
                                    if all_fields.get('category_field'): chart_config['category_field'] = all_fields['category_field']
                                    elif all_fields.get('x_field'): chart_config['category_field'] = all_fields['x_field']
                                    
                                    if all_fields.get('value_field'): chart_config['value_field'] = all_fields['value_field']
                                    elif all_fields.get('y_field'): chart_config['value_field'] = all_fields['y_field']
                                
                                elif chart_type in ['multi_column', 'column_clustered']:
                                    # 多列柱状图：需要 category_field 和 series（数组）
                                    if all_fields.get('category_field'): chart_config['category_field'] = all_fields['category_field']
                                    elif all_fields.get('x_field'): chart_config['category_field'] = all_fields['x_field']
                                    
                                    # series 可能是 series/y_field/fields，可能是字符串或数组
                                    series_val = all_fields.get('series') or all_fields.get('y_field') or all_fields.get('fields')
                                    if series_val:
                                        if isinstance(series_val, list):
                                            chart_config['series'] = series_val
                                        else:
                                            try:
                                                chart_config['series'] = json.loads(str(series_val)) if str(series_val).startswith('[') else [series_val]
                                            except:
                                                chart_config['series'] = [series_val]
                                
                                elif chart_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter']:
                                    # 这些图表使用 x_field 和 y_field
                                    if all_fields.get('x_field'): chart_config['x_field'] = all_fields['x_field']
                                    if all_fields.get('y_field'): chart_config['y_field'] = all_fields['y_field']
                                
                                else:
                                    # 其他图表类型直接使用 AI 输出的字段
                                    chart_config.update(all_fields)
                                
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
                                "title": rec.get('chart_title', '')
                            }
                            
                            # 根据图表类型转换字段名（支持 AI 输出的多种字段名）
                            chart_type = rec.get('chart_type', '')
                            
                            # 收集所有可能的字段（AI 可能输出不同的字段名）
                            all_fields = {}
                            for k, v in rec.items():
                                if k not in ['chart_key', 'chart_title', 'data_source', 'chart_type', 'description', 'reason']:
                                    all_fields[k] = v
                            
                            if chart_type == 'pie':
                                if all_fields.get('category_field'): chart_config['category_field'] = all_fields['category_field']
                                elif all_fields.get('x_field'): chart_config['category_field'] = all_fields['x_field']
                                
                                if all_fields.get('value_field'): chart_config['value_field'] = all_fields['value_field']
                                elif all_fields.get('y_field'): chart_config['value_field'] = all_fields['y_field']
                            
                            elif chart_type in ['multi_column', 'column_clustered']:
                                if all_fields.get('category_field'): chart_config['category_field'] = all_fields['category_field']
                                elif all_fields.get('x_field'): chart_config['category_field'] = all_fields['x_field']
                                
                                series_val = all_fields.get('series') or all_fields.get('y_field') or all_fields.get('fields')
                                if series_val:
                                    if isinstance(series_val, list):
                                        chart_config['series'] = series_val
                                    else:
                                        try:
                                            chart_config['series'] = json.loads(str(series_val)) if str(series_val).startswith('[') else [series_val]
                                        except:
                                            chart_config['series'] = [series_val]
                            
                            elif chart_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter']:
                                if all_fields.get('x_field'): chart_config['x_field'] = all_fields['x_field']
                                if all_fields.get('y_field'): chart_config['y_field'] = all_fields['y_field']
                            
                            else:
                                chart_config.update(all_fields)
                            
                            placeholders_config.setdefault('placeholders', {}).setdefault('charts', {})[chart_key] = chart_config
                            added_count += 1
                    
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    
                    if added_count > 0:
                        st.success(f"✅ 已一键保存 {added_count} 个图表配置")
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
            
            # 根据图表类型显示不同的字段配置 UI
            auto_fields_info = ""
            available_fields = []
            if data_source and summary_path and os.path.exists(summary_path):
                try:
                    df_temp = pd.read_excel(summary_path, sheet_name=data_source, nrows=1)
                    available_fields = df_temp.columns.tolist()
                    auto_fields_info = f"📊 可用字段：{', '.join(available_fields)}"
                except Exception:
                    pass
            
            # 根据图表类型显示不同的字段配置 UI
            if chart_type in ["bar_horizontal", "bar_vertical"]:
                st.info("💡 条形图/柱状图：需要 X 轴（数值）和 Y 轴（分类）字段")
                x_field = st.text_input("X 轴字段（数值）", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None, key="x_field_input")
                y_field = st.text_input("Y 轴字段（分类）", placeholder="例如：销售员", help=auto_fields_info if auto_fields_info else None, key="y_field_input")
            
            elif chart_type == "line":
                st.info("💡 折线图：需要 X 轴（时间）和 Y 轴（数值）字段")
                x_field = st.text_input("X 轴字段（时间）", placeholder="例如：年月", help=auto_fields_info if auto_fields_info else None, key="x_field_line")
                y_field = st.text_input("Y 轴字段（数值）", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_line")
            
            elif chart_type == "pie":
                st.info("💡 饼图：需要分类字段和数值字段")
                x_field = st.text_input("分类字段", placeholder="例如：产品", help=auto_fields_info if auto_fields_info else None, key="x_field_pie")
                y_field = st.text_input("数值字段", placeholder="例如：占比", help=auto_fields_info if auto_fields_info else None, key="y_field_pie")
            
            elif chart_type in ["multi_column", "column_clustered"]:
                st.info("💡 多列柱状图：需要分类字段和多指标列表（JSON 格式）")
                x_field = st.text_input("分类字段", placeholder="例如：客户类型", help=auto_fields_info if auto_fields_info else None, key="x_field_multi")
                y_field = st.text_area("多指标列表（JSON 格式）", 
                                      placeholder='["总销售额", "订单数", "客单价"]', 
                                      value='["总销售额"]',
                                      height=80, 
                                      key="y_field_multi")
            
            elif chart_type == "scatter":
                st.info("💡 散点图：需要 X 轴和 Y 轴字段（都是数值）")
                x_field = st.text_input("X 轴字段", placeholder="例如：订单时间", help=auto_fields_info if auto_fields_info else None, key="x_field_scatter")
                y_field = st.text_input("Y 轴字段", placeholder="例如：销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_scatter")
            
            elif chart_type == "heatmap":
                st.info("💡 热力图：需要行字段和列字段列表（JSON 格式）")
                x_field = st.text_input("行字段", placeholder="例如：销售员", help=auto_fields_info if auto_fields_info else None, key="x_field_heatmap")
                y_field = st.text_area("列字段列表（JSON 格式）", 
                                      placeholder='["可乐", "巧克力", "牛奶"]', 
                                      value='[]',
                                      height=80, 
                                      key="y_field_heatmap")
            
            elif chart_type == "bubble":
                st.info("💡 气泡图：需要 X 轴、Y 轴和大小字段")
                x_field = st.text_input("X 轴字段", placeholder="例如：年龄段", help=auto_fields_info if auto_fields_info else None, key="x_field_bubble")
                y_field = st.text_input("Y 轴字段", placeholder="例如：总销售额", help=auto_fields_info if auto_fields_info else None, key="y_field_bubble")
                size_field = st.text_input("大小字段", placeholder="例如：订单数", help=auto_fields_info if auto_fields_info else None, key="size_field_bubble")
            
            else:
                # 其他图表类型使用通用配置
                st.info(f"💡 {chart_types.get(chart_type, '')}：根据图表类型配置字段")
                x_field = st.text_area("字段配置（JSON 格式）", 
                                      placeholder='{"category_field": "城市", "value_field": "销售额"}',
                                      height=100, 
                                      key="x_field_json")
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
                    
                    # 根据图表类型保存正确的字段名
                    if chart_type == "pie":
                        # 饼图使用 category_field 和 value_field
                        if x_field: chart_config["category_field"] = x_field
                        if y_field: chart_config["value_field"] = y_field
                    
                    elif chart_type in ["multi_column", "column_clustered"]:
                        # 多列柱状图使用 category_field 和 series（列表）
                        if x_field: chart_config["category_field"] = x_field
                        # series 必须是 JSON 列表
                        if y_field:
                            try:
                                chart_config["series"] = json.loads(y_field)
                            except:
                                # 如果不是 JSON，尝试转为列表
                                chart_config["series"] = [y_field] if y_field else []
                    
                    elif chart_type == "heatmap":
                        # 热力图使用 index_field 和 columns（列表）
                        if x_field: chart_config["index_field"] = x_field
                        if y_field:
                            try:
                                chart_config["columns"] = json.loads(y_field)
                            except:
                                chart_config["columns"] = []
                    
                    elif chart_type == "bubble":
                        # 气泡图使用 x_field, y_field, size_field
                        if x_field: chart_config["x_field"] = x_field
                        if y_field: chart_config["y_field"] = y_field
                        if 'size_field_bubble' in st.session_state and st.session_state.size_field_bubble:
                            chart_config["size_field"] = st.session_state.size_field_bubble
                    
                    elif chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter"]:
                        # 这些图表使用 x_field 和 y_field
                        if x_field: chart_config["x_field"] = x_field
                        if y_field: chart_config["y_field"] = y_field
                    
                    else:
                        # 其他图表类型：尝试解析 JSON 配置
                        if x_field:
                            try:
                                extra_fields = json.loads(x_field)
                                chart_config.update(extra_fields)
                            except:
                                chart_config["x_field"] = x_field
                    
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
        
        # ========== 现有图表配置 ==========
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
                        
                        # 添加渲染模式选择器
                        render_mode = chart_cfg.get('render_mode', 'native')  # 默认原生方式
                        
                        # 根据图表类型判断是否支持原生模式
                        chart_type = chart_cfg.get('chart_type', '')
                        native_supported = chart_type in ['bar_horizontal', 'bar_vertical', 'pie', 'line', 'area', 'scatter', 'column_clustered', 'multi_column']
                        
                        if not native_supported:
                            # 不支持原生模式，强制使用图片方式
                            if render_mode != 'image':
                                chart_cfg['render_mode'] = 'image'
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                st.info(f"ℹ️ {chart_type} 不支持原生模式，已自动切换为图片方式")
                            st.caption("💡 此图表类型仅支持图片方式")
                            render_mode_options = ["image"]
                            render_mode_index = 0
                        else:
                            # 支持原生模式，默认原生
                            render_mode_options = ["native", "image"]  # 原生在前
                            render_mode_index = render_mode_options.index(render_mode) if render_mode in render_mode_options else 0
                        
                        new_render_mode = st.selectbox(
                            "图表渲染方式",
                            options=render_mode_options,
                            format_func=lambda x: "🖼️ 图片方式（不可编辑）" if x == "image" else "📊 原生方式（可编辑）",
                            index=render_mode_index,
                            key=f"render_mode_{chart_key}",
                            help="图片方式：生成 PNG 插入 PPT（速度快，支持所有图表类型）\n原生方式：在 PPT 中创建可编辑图表（可后期修改，仅支持基础图表）"
                        )
                        
                        if new_render_mode != render_mode:
                            chart_cfg['render_mode'] = new_render_mode
                            with open(placeholders_file, 'w', encoding='utf-8') as f:
                                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                            st.success(f"✅ 已更新 {chart_key} 的渲染方式为 {new_render_mode}")
                            st.rerun()
                
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
                    
                    # 根据图表类型显示正确的字段输入框
                    chart_type = chart_cfg.get('chart_type', '')
                    
                    if chart_type == 'pie':
                        # 饼图：显示 category_field 和 value_field
                        edit_cat = st.text_input("分类字段", value=chart_cfg.get('category_field', chart_cfg.get('x_field', '')), key=f"edit_cat_{chart_key}")
                        edit_val = st.text_input("数值字段", value=chart_cfg.get('value_field', chart_cfg.get('y_field', '')), key=f"edit_val_{chart_key}")
                        edit_x = None
                        edit_y = None
                    elif chart_type in ['multi_column', 'column_clustered']:
                        # 多列柱状图：显示 category_field 和 series
                        edit_cat = st.text_input("分类字段", value=chart_cfg.get('category_field', chart_cfg.get('x_field', '')), key=f"edit_cat_{chart_key}")
                        series_val = chart_cfg.get('series', chart_cfg.get('y_field', '[]'))
                        if isinstance(series_val, list):
                            series_val = json.dumps(series_val, ensure_ascii=False)
                        edit_ser = st.text_area("多指标列表（JSON 格式）", value=series_val, height=80, key=f"edit_ser_{chart_key}")
                        edit_x = None
                        edit_y = None
                    else:
                        # 其他图表：显示 x_field 和 y_field
                        edit_cat = None
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
                                "title": edit_title
                            }
                            
                            # 根据图表类型保存正确的字段名
                            if edit_type == 'pie':
                                if edit_cat: new_config['category_field'] = edit_cat
                                if edit_val: new_config['value_field'] = edit_val
                            elif edit_type in ['multi_column', 'column_clustered']:
                                if edit_cat: new_config['category_field'] = edit_cat
                                if edit_ser:
                                    try:
                                        new_config['series'] = json.loads(edit_ser)
                                    except:
                                        new_config['series'] = [edit_ser] if edit_ser else []
                            else:
                                if edit_x: new_config['x_field'] = edit_x
                                if edit_y: new_config['y_field'] = edit_y
                            
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
