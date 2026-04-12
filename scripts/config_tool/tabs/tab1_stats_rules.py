# -*- coding: utf-8 -*-
"""Tab 1: 统计规则配置 - AI 增强版 + 自定义添加"""
import streamlit as st
import pandas as pd
import json
import os
import sys

def render_tab1(base_dir, templates_dir, output_dir):
    st.header("📋 统计规则配置")
    st.markdown("配置要生成哪些统计表格（Excel Sheet）")
    
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
    # 获取目录结构
    from app_config import get_output_dirs, ensure_output_dirs
    dirs = ensure_output_dirs(base_dir)
    uploaded_dir = dirs['uploaded']
    summary_dir = dirs['summary']
    
    # 加载配置
    if 'stats_config' not in st.session_state:
        if os.path.exists(stats_rules_file):
            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                st.session_state.stats_config = json.load(f)
            st.success("✅ 已加载现有配置")
        else:
            st.session_state.stats_config = {
                "version": "1.0",
                "stats_sheets": {},
                "global_settings": {"date_range_auto_detect": True}
            }
            st.info("📝 创建新配置")
    
    stats_config = st.session_state.stats_config
    
    # ========== 上传的 Excel 文件选择 ==========
    st.subheader("📤 选择/上传原始数据 Excel")
    
    # 获取 uploaded 目录下的所有 Excel 文件
    uploaded_files = []
    if os.path.exists(uploaded_dir):
        uploaded_files = [f for f in os.listdir(uploaded_dir) 
                         if f.endswith(('.xlsx', '.xls')) and not f.startswith('~')]
        uploaded_files.sort(reverse=True)  # 最新的在前
    
    # 优先使用刚上传的文件
    if 'uploaded_file_name' in st.session_state and st.session_state['uploaded_file_name'] in uploaded_files:
        default_index = uploaded_files.index(st.session_state['uploaded_file_name'])
    else:
        default_index = 0
    
    if uploaded_files:
        selected_file = st.selectbox(
            "选择已上传的 Excel 文件",
            options=uploaded_files,
            index=min(default_index, len(uploaded_files) - 1),
            key="uploaded_file_select"
        )
        
        # 更新 session_state
        if selected_file != st.session_state.get('uploaded_file_name'):
            st.session_state['uploaded_file_name'] = selected_file
            st.rerun()
    else:
        st.info("💡 暂无上传的 Excel 文件，请在下方上传")
        selected_file = None
    
    # Excel 上传功能
    uploaded_file = st.file_uploader("上传新的 Excel 文件", type=["xlsx", "xls"], key="upload_excel")
    
    if uploaded_file is not None:
        os.makedirs(uploaded_dir, exist_ok=True)
        uploaded_file_name = uploaded_file.name
        output_file = os.path.join(uploaded_dir, uploaded_file_name)
        st.session_state['uploaded_file_name'] = uploaded_file_name
        
        try:
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except PermissionError:
                    st.warning("⚠️ 文件被占用，请关闭 Excel/WPS 后重试")
                    st.stop()
            
            with open(output_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            df_preview = pd.read_excel(output_file, nrows=5)
            st.success(f"✅ 上传成功！")
            st.info(f"📊 列名：{', '.join(df_preview.columns)}")
            
            with st.expander("📋 查看数据预览", expanded=True):
                st.dataframe(df_preview, width='stretch')
            
            # 上传后自动刷新选中
            st.session_state['uploaded_file_name'] = uploaded_file_name
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 上传失败：{e}")
    
    # 显示当前选中的文件信息
    if selected_file:
        raw_data_file = os.path.join(uploaded_dir, selected_file)
        if os.path.exists(raw_data_file):
            file_size = os.path.getsize(raw_data_file)
            st.success(f"✅ 当前数据文件：`{selected_file}` ({round(file_size/1024, 1)} KB)")
        else:
            st.error(f"❌ 文件不存在：{selected_file}")
    else:
        st.info("💡 请先上传 Excel 数据文件")
    
    st.markdown("---")
    
    # AI 智能分析
    st.subheader("🤖 AI 智能分析")
    
    # 初始化待添加规则（移到外层，避免 rerun 后丢失）
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    use_ai = st.checkbox("✨ 使用 AI 自动推荐统计规则", value=False, key="use_ai_check")
    
    if use_ai and selected_file:
        if st.button("🤖 开始 AI 智能分析", type="primary", key="start_ai_analysis"):
            try:
                raw_data_file = os.path.join(uploaded_dir, selected_file)
                df = pd.read_excel(raw_data_file)
                
                # 构建数据样本（处理 Timestamp 序列化问题）
                sample_data = []
                for _, row in df.head(5).iterrows():
                    row_dict = {}
                    for col, val in row.items():
                        if hasattr(val, 'strftime'):  # Timestamp 转为字符串
                            row_dict[col] = val.strftime('%Y-%m-%d %H:%M:%S')
                        elif pd.isna(val):  # NaN 转为 None
                            row_dict[col] = None
                        else:
                            row_dict[col] = val
                    sample_data.append(row_dict)
                
                # 构建列信息（处理 Timestamp 序列化问题）
                columns_info = []
                for col in df.columns:
                    sample_vals = df[col].head(3).dropna().tolist()
                    # 处理 Timestamp 转为字符串
                    processed_samples = []
                    for v in sample_vals:
                        if hasattr(v, 'strftime'):
                            processed_samples.append(v.strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            processed_samples.append(v)
                    
                    col_info = {
                        'name': col,
                        'type': str(df[col].dtype),
                        'sample': processed_samples
                    }
                    columns_info.append(col_info)
                
                # 调用 AI（使用 stats-rule-recommender SKILL）
                # 添加 scripts 目录到路径
                scripts_dir = os.path.join(base_dir, 'scripts')
                if scripts_dir not in sys.path:
                    sys.path.insert(0, scripts_dir)
                
                from ai.qwen_client import QwenClient
                qwen = QwenClient(base_dir=base_dir)
                
                if qwen.is_available():
                    # 读取 SKILL.md
                    skill_path = os.path.join(base_dir, 'skills', 'stats-rule-recommender', 'SKILL.md')
                    with open(skill_path, 'r', encoding='utf-8') as f:
                        skill_content = f.read()
                    
                    # 构建 Prompt
                    prompt = f"""
请根据以下 Excel 数据结构，推荐合适的统计规则配置：

Excel 文件：{selected_file}
列信息：
{json.dumps(columns_info, ensure_ascii=False, indent=2)}

数据样本（前 5 行）：
{json.dumps(sample_data, ensure_ascii=False, indent=2)}

{skill_content}

请根据 SKILL 中的规则，推荐统计规则配置。
"""
                    
                    system_prompt = "你是数据分析专家，输出严格 JSON 格式。只输出 JSON，不要任何其他文字。"
                    response = qwen.chat(system_prompt, prompt, json_mode=True)
                    
                    if response:
                        result = qwen.parse_json_response(response)
                        if result and 'recommendations' in result:
                            st.session_state['ai_recommendations_list'] = result['recommendations']
                            st.success(f"🤖 AI 推荐了 {len(result['recommendations'])} 条统计规则")
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
    if 'ai_recommendations_list' in st.session_state:
        recommendations = st.session_state['ai_recommendations_list']
        
        if recommendations:
            st.markdown("### AI 推荐统计规则")
            
            for i, rec in enumerate(recommendations):
                already_added = rec.get('name', '') in stats_config.get('stats_sheets', {})
                
                st.markdown(f"**{i+1}. {rec.get('name', '')}** - {rec.get('description', '')}")
                st.json(rec)
                
                if already_added:
                    st.success("✅ 已添加")
                else:
                    if st.button("➕ 添加并保存", key=f"add_rec_{i}"):
                        stats_config['stats_sheets'][rec.get('name', '')] = rec
                        with open(stats_rules_file, 'w', encoding='utf-8') as f:
                            json.dump(stats_config, f, ensure_ascii=False, indent=2)
                        st.success(f"✅ 已添加：{rec.get('name', '')}")
                        st.session_state['ai_recommendations_list'] = None
                        st.rerun()
            
            # 一键保存按钮
            st.markdown("---")
            if st.button("📥 一键保存所有推荐规则", type="primary", use_container_width=True):
                added_count = 0
                for rec in recommendations:
                    if rec.get('name', '') not in stats_config.get('stats_sheets', {}):
                        stats_config['stats_sheets'][rec.get('name', '')] = rec
                        added_count += 1
                
                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                    json.dump(stats_config, f, ensure_ascii=False, indent=2)
                
                if added_count > 0:
                    st.success(f"✅ 已一键保存 {added_count} 条统计规则")
                    st.session_state['ai_recommendations_list'] = None
                    st.rerun()
                else:
                    st.info("ℹ️ 所有推荐规则都已添加")
    
    st.markdown("---")
    
    # ========== 自定义添加统计规则 ==========
    st.subheader("📝 自定义添加统计规则")
    st.caption("手动配置统计规则，不依赖 AI 推荐")
    
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
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sheet_name = st.text_input("统计表格名称", placeholder="例如：销售员业绩", key="custom_sheet_name")
        stat_type = st.selectbox("统计类型", options=list(stats_types.keys()), format_func=lambda x: stats_types[x], key="custom_stat_type")
        enabled = st.checkbox("启用", value=True, key="custom_enabled")
        description = st.text_area("描述", placeholder="例如：销售员业绩排名", height=60, key="custom_desc")
    
    with col2:
        group_fields = st.text_area("分组字段（每行一个）", placeholder="销售员\n城市", height=100, key="custom_groups")
        metrics_config = st.text_area("统计指标（JSON 格式）", 
                                     value='[{"field": "销售额", "agg": "sum", "alias": "总销售额"}]',
                                     height=150, key="custom_metrics")
    
    if st.button("➕ 添加自定义统计规则", key="add_custom_rule"):
        if not sheet_name.strip():
            st.error("❌ 请填写统计表格名称")
        elif not group_fields.strip():
            st.error("❌ 请填写分组字段")
        else:
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
                
                if sheet_name not in stats_config.get('stats_sheets', {}):
                    stats_config['stats_sheets'][sheet_name] = rule
                    
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(stats_config, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ 已添加自定义规则：{sheet_name}")
                    st.rerun()
                else:
                    st.warning(f"⚠️ 统计规则已存在：{sheet_name}")
            
            except json.JSONDecodeError as e:
                st.error(f"❌ 指标配置格式错误：{e}")
    
    st.markdown("---")
    
    # ========== 执行统计并生成 Excel ==========
    st.subheader("💾 操作")
    
    if st.button("▶ 执行统计并生成 Excel", type="primary", use_container_width=True):
        try:
            # 保存当前配置到 stats_rules.json
            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                json.dump(stats_config, f, ensure_ascii=False, indent=2)
            st.info("📝 配置已保存")
            
            if not selected_file:
                st.error("❌ 请先选择或上传 Excel 文件")
                st.stop()
            
            with st.spinner("⚙️ 正在执行统计引擎..."):
                scripts_dir = os.path.join(base_dir, 'scripts')
                if scripts_dir not in sys.path:
                    sys.path.insert(0, scripts_dir)
                
                from core.stats_engine import StatsEngine
                
                # 从 uploaded 目录读取原始数据
                raw_data_file = os.path.join(uploaded_dir, selected_file)
                raw_df = pd.read_excel(raw_data_file)
                
                # 生成到 summary 目录
                summary_file_name = selected_file.replace('.xlsx', '_统计汇总.xlsx') if selected_file.endswith('.xlsx') else selected_file + '_统计汇总.xlsx'
                output_path = os.path.join(summary_dir, summary_file_name)
                
                stats_engine = StatsEngine(base_dir=base_dir, raw_data_file=selected_file)
                results = stats_engine.run_all(raw_df, output_path=output_path)
                
                # 保存生成的统计汇总文件名到 session_state（Tab 2 优先使用）
                st.session_state['generated_summary_name'] = summary_file_name
                
                st.success(f"✅ 已生成 {len(results)} 个统计 Sheet！")
                
                # 显示生成的 Sheet 列表和跳过的项目
                with st.expander("📊 查看生成的 Sheet", expanded=True):
                    for sheet_name, df in results.items():
                        st.write(f"**{sheet_name}**: {len(df)} 行")
                    
                    # 显示跳过的规则
                    all_rules = set(stats_config.get('stats_sheets', {}).keys())
                    generated = set(results.keys())
                    skipped = all_rules - generated
                    
                    if skipped:
                        st.warning(f"⚠️ 以下 {len(skipped)} 条规则执行失败（可能是缺少字段）：")
                        for name in sorted(skipped):
                            st.write(f"- {name}")
                        st.info("💡 **提示**: 请检查这些规则配置的字段是否存在于 Excel 中")
            
            st.success("🎉 完成！")
            
        except FileNotFoundError as e:
            st.error(f"❌ 数据文件不存在：{e}")
        except Exception as e:
            st.error(f"❌ 执行失败：{e}")
            import traceback
            with st.expander("📄 查看详细错误"):
                st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # ========== 现有统计规则 ==========
    st.subheader("📋 现有统计规则")
    
    edit_rule_name = st.session_state.get('editing_rule_name', None)
    
    if stats_config.get('stats_sheets'):
        for name, rule in stats_config['stats_sheets'].items():
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
                edit_metrics = st.text_area("统计指标（JSON 格式）", 
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
                            try:
                                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                    json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"保存失败：{e}")
                            st.rerun()
    else:
        st.info("暂无统计规则，请添加")
