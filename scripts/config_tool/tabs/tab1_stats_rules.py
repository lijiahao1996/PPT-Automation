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
    
    # 获取数据文件
    from app_config import get_default_raw_data_filename
    raw_data_file_name = get_default_raw_data_filename()
    raw_data_file = os.path.join(output_dir, raw_data_file_name)
    
    if 'uploaded_file_name' in st.session_state:
        raw_data_file = os.path.join(output_dir, st.session_state['uploaded_file_name'])
        raw_data_file_name = st.session_state['uploaded_file_name']
    
    # 统计汇总文件名
    if raw_data_file_name.endswith('.xlsx'):
        summary_file_name = raw_data_file_name.replace('.xlsx', '_统计汇总.xlsx')
    else:
        summary_file_name = raw_data_file_name + '_统计汇总.xlsx'
    summary_file = os.path.join(output_dir, summary_file_name)
    
    # Excel 上传功能
    st.subheader("📤 上传原始数据 Excel")
    uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx", "xls"], key="upload_excel")
    
    if uploaded_file is not None:
        os.makedirs(output_dir, exist_ok=True)
        uploaded_file_name = uploaded_file.name
        output_file = os.path.join(output_dir, uploaded_file_name)
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
            
        except Exception as e:
            st.error(f"❌ 上传失败：{e}")
    
    if os.path.exists(raw_data_file):
        file_size = os.path.getsize(raw_data_file)
        st.success(f"✅ 数据文件：`{os.path.basename(raw_data_file)}` ({round(file_size/1024, 1)} KB)")
    else:
        st.info("💡 请先上传 Excel 数据文件")
    
    st.markdown("---")
    
    # AI 智能分析
    st.subheader("🤖 AI 智能分析")
    
    # 初始化待添加规则（移到外层，避免 rerun 后丢失）
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    use_ai = st.checkbox("✨ 使用 AI 自动推荐统计规则", value=False, key="use_ai_check")
    
    if use_ai and os.path.exists(raw_data_file):
        if st.button("🤖 开始 AI 智能分析", type="primary", key="start_ai_analysis"):
            try:
                df = pd.read_excel(raw_data_file)
                
                # 构建数据样本
                sample_data = df.head(5).to_dict('records')
                columns_info = []
                for col in df.columns:
                    col_info = {
                        'name': col,
                        'type': str(df[col].dtype),
                        'sample': df[col].head(3).dropna().tolist()
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

Excel 文件：{raw_data_file_name}
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
    
    # 显示推荐列表（在外层，使用 session_state 保存的推荐）
    if 'ai_recommendations_list' in st.session_state:
        recommendations = st.session_state['ai_recommendations_list']
        
        if recommendations:
            st.markdown("### 推荐规则列表")
            
            for i, rec in enumerate(recommendations):
                already_added = rec['name'] in st.session_state.stats_config.get('stats_sheets', {})
                
                # 折叠后显示：规则名 + 添加/删除按钮
                col_title, col_btn = st.columns([4, 1])
                
                with col_title:
                    status_icon = "✅" if already_added else "⬜"
                    st.write(f"{status_icon} **{rec['name']}** - {rec.get('ai_reason', '')}")
                
                with col_btn:
                    if already_added:
                        # 已添加：显示删除按钮
                        if st.button("🗑️ 删除", key=f"del_{rec['name']}_{i}", use_container_width=True):
                            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                                current_config = json.load(f)
                            
                            if rec['name'] in current_config['stats_sheets']:
                                del current_config['stats_sheets'][rec['name']]
                                
                                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                    json.dump(current_config, f, ensure_ascii=False, indent=2)
                                
                                st.session_state.stats_config = current_config
                                st.rerun()
                    else:
                        # 未添加：显示添加按钮
                        if st.button("➕ 添加并保存", key=f"add_{rec['name']}_{i}", use_container_width=True):
                            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                                current_config = json.load(f)
                            
                            current_config['stats_sheets'][rec['name']] = {
                                'description': rec.get('description', ''),
                                'type': rec['type'],
                                'enabled': True,
                                'group_by': rec.get('group_by', []),
                                'metrics': rec.get('metrics', [])
                            }
                            
                            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                json.dump(current_config, f, ensure_ascii=False, indent=2)
                            
                            st.session_state.stats_config = current_config
                            st.rerun()
                
                # 展开查看详情
                with st.expander("查看配置详情", expanded=False):
                    st.json(rec)
            
            # 一键保存按钮放在最下面
            st.markdown("---")
            if st.button("🚀 一键保存所有推荐规则", type="primary", use_container_width=True, key="save_all_ai_rules"):
                try:
                    with open(stats_rules_file, 'r', encoding='utf-8') as f:
                        current_config = json.load(f)
                    
                    added_count = 0
                    for rec in recommendations:
                        if rec['name'] not in current_config['stats_sheets']:
                            current_config['stats_sheets'][rec['name']] = {
                                'description': rec.get('description', ''),
                                'type': rec['type'],
                                'enabled': True,
                                'group_by': rec.get('group_by', []),
                                'metrics': rec.get('metrics', [])
                            }
                            added_count += 1
                    
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(current_config, f, ensure_ascii=False, indent=2)
                    
                    if added_count > 0:
                        st.success(f"✅ 已一键保存 {added_count} 条规则到 stats_rules.json")
                        st.balloons()
                        
                        st.session_state.stats_config = current_config
                        st.session_state.ai_recommendations_list = []
                        
                        st.info("💡 规则已保存，请滚动到下方查看'现有统计规则'")
                    else:
                        st.info("ℹ️ 所有规则都已添加")
                
                except Exception as e:
                    st.error(f"❌ 保存失败：{e}")
                    import traceback
                    st.code(traceback.format_exc())
    
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
        custom_sheet_name = st.text_input("统计表格名称", placeholder="例如：销售员业绩", key="custom_sheet_name")
        custom_stat_type = st.selectbox("统计类型", options=list(stats_types.keys()), format_func=lambda x: stats_types[x], key="custom_stat_type")
        custom_enabled = st.checkbox("启用", value=True, key="custom_enabled")
        custom_description = st.text_area("描述", placeholder="例如：销售员业绩排名", height=60, key="custom_desc")
    
    with col2:
        custom_group_fields = st.text_area("分组字段（每行一个）", placeholder="销售员\n城市", height=100, key="custom_groups")
        custom_metrics = st.text_area("统计指标（JSON 格式）", 
                                     value='[{"field": "销售额", "agg": "sum", "alias": "总销售额"}]',
                                     height=150, key="custom_metrics")
    
    if st.button("➕ 添加自定义统计规则", use_container_width=True, key="add_custom_rule"):
        if not custom_sheet_name.strip():
            st.error("❌ 请填写统计表格名称")
        elif not custom_group_fields.strip():
            st.error("❌ 请填写分组字段")
        else:
            try:
                metrics = json.loads(custom_metrics)
                groups = [g.strip() for g in custom_group_fields.strip().split('\n') if g.strip()]
                
                rule = {
                    "description": custom_description,
                    "type": custom_stat_type,
                    "enabled": custom_enabled,
                    "group_by": groups,
                    "metrics": metrics
                }
                
                if custom_sheet_name not in st.session_state.stats_config.get("stats_sheets", {}):
                    st.session_state.stats_config["stats_sheets"][custom_sheet_name] = rule
                    
                    # 保存到文件
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"✅ 已添加自定义规则：{custom_sheet_name}")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning(f"⚠️ 统计规则已存在：{custom_sheet_name}")
            
            except json.JSONDecodeError as e:
                st.error(f"❌ 指标配置格式错误：{e}")
    
    st.markdown("---")
    
    # 现有统计规则
    st.subheader("📋 现有统计规则")
    
    # 重新读取最新的 stats_rules.json（确保显示最新数据）
    if os.path.exists(stats_rules_file):
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            latest_config = json.load(f)
        st.session_state.stats_config = latest_config
    
    if st.session_state.stats_config.get('stats_sheets'):
        for name, rule in st.session_state.stats_config['stats_sheets'].items():
            # 折叠后显示：规则名 + 删除按钮
            col_title, col_btn = st.columns([4, 1])
            
            with col_title:
                with st.expander(f"{'✅' if rule.get('enabled', True) else '❌'} {name}", expanded=False):
                    st.json(rule)
            
            with col_btn:
                if st.button("🗑️ 删除", key=f"delete_{name}", use_container_width=True):
                    del st.session_state.stats_config['stats_sheets'][name]
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                    st.rerun()
    else:
        st.info("暂无统计规则")
    
    st.markdown("---")
    st.subheader("💾 操作")
    
    if st.button("▶ 执行统计并生成 Excel", type="primary", use_container_width=True):
        try:
            # 先读取最新的 stats_rules.json
            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                latest_config = json.load(f)
            
            st.info(f"📝 读取配置：{len(latest_config.get('stats_sheets', {}))} 条规则")
            
            with st.spinner("⚙️ 正在执行统计引擎..."):
                sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                from core.stats_engine import StatsEngine
                from core.data_loader import DataLoader
                
                # 使用用户上传的文件名
                use_file_name = st.session_state.get('uploaded_file_name')
                
                if not use_file_name:
                    # 如果没有上传，自动检测 output 目录中的第一个非统计汇总文件
                    for f in os.listdir(output_dir):
                        if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                            use_file_name = f
                            st.session_state['uploaded_file_name'] = f
                            break
                
                if not use_file_name:
                    st.error("❌ 未找到数据文件，请先上传 Excel")
                    st.stop()
                
                st.info(f"📊 使用数据文件：{use_file_name}")
                
                data_loader = DataLoader(base_dir)
                raw_df = data_loader.load_raw_data(use_file_name)
                
                stats_engine = StatsEngine(base_dir=base_dir)
                output_path = os.path.join(output_dir, summary_file_name)
                results = stats_engine.run_all(raw_df, output_path=output_path)
                
                st.success(f"✅ 已生成 {len(results)} 个统计 Sheet！")
                
                # 显示生成的 Sheet 列表
                with st.expander("📊 查看生成的 Sheet", expanded=True):
                    for sheet_name, df in results.items():
                        st.write(f"**{sheet_name}**: {len(df)} 行")
            
            st.success("🎉 完成！")
            
        except FileNotFoundError as e:
            st.error(f"❌ 数据文件不存在：{e}")
        except Exception as e:
            st.error(f"❌ 执行失败：{e}")
            import traceback
            with st.expander("📄 查看详细错误"):
                st.code(traceback.format_exc())
    
    # ========== 集成数据概览功能 ==========
    st.markdown("---")
    st.header("📊 查看生成的数据")
    st.markdown("*预览统计汇总 Excel 中的 Sheet 数据*")
    
    # 根据上传的文件名构建统计汇总文件名
    summary_file = None
    if 'uploaded_file_name' in st.session_state:
        uploaded_name = st.session_state['uploaded_file_name']
        if uploaded_name.endswith('.xlsx'):
            summary_name = uploaded_name.replace('.xlsx', '_统计汇总.xlsx')
        else:
            summary_name = uploaded_name + '_统计汇总.xlsx'
        summary_file = os.path.join(output_dir, summary_name)
    
    # 如果找不到，自动检测 output 目录
    if not summary_file or not os.path.exists(summary_file):
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                summary_file = os.path.join(output_dir, f)
                break
    
    if summary_file and os.path.exists(summary_file):
        st.success("✅ 找到统计汇总文件")
        
        try:
            xls = pd.ExcelFile(summary_file)
            sheet_names = xls.sheet_names
            
            st.markdown(f"##### 📋 共有 {len(sheet_names)} 个统计 Sheet")
            
            # 创建概览表格
            overview_data = []
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(summary_file, sheet_name=sheet_name, nrows=1)
                    row_count = len(pd.read_excel(summary_file, sheet_name=sheet_name))
                    col_count = len(df.columns)
                    columns_list = df.columns.tolist()
                    
                    overview_data.append({
                        'Sheet 名称': sheet_name,
                        '行数': row_count,
                        '列数': col_count,
                        '字段列表': ', '.join(columns_list[:5]) + ('...' if len(columns_list) > 5 else '')
                    })
                except Exception as e:
                    overview_data.append({
                        'Sheet 名称': sheet_name,
                        '行数': '读取失败',
                        '列数': '-',
                        '字段列表': f'错误：{e}'
                    })
            
            overview_df = pd.DataFrame(overview_data)
            st.dataframe(overview_df, width='stretch', hide_index=True)
            
            # 详细查看某个 Sheet
            st.markdown("---")
            st.subheader("🔍 详细查看")
            
            selected_sheet = st.selectbox("选择 Sheet 查看详细数据", sheet_names)
            
            if selected_sheet:
                try:
                    df_detail = pd.read_excel(summary_file, sheet_name=selected_sheet)
                    st.dataframe(df_detail.head(100), width='stretch')
                    
                    st.markdown(f"##### 数据信息")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总行数", len(df_detail))
                    with col2:
                        st.metric("总列数", len(df_detail.columns))
                    with col3:
                        st.metric("内存占用", f"{df_detail.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
                    with col4:
                        st.metric("空值总数", df_detail.isnull().sum().sum())
                    
                    # 字段详情
                    with st.expander("📊 查看字段详情"):
                        field_info = []
                        for col in df_detail.columns:
                            field_info.append({
                                '字段名': col,
                                '数据类型': str(df_detail[col].dtype),
                                '非空值': int(df_detail[col].notnull().sum()),
                                '空值数': int(df_detail[col].isnull().sum()),
                                '唯一值': int(df_detail[col].nunique())
                            })
                        st.dataframe(pd.DataFrame(field_info), width='stretch', hide_index=True)
                except Exception as e:
                    st.error(f"❌ 读取失败：{e}")
        except Exception as e:
            st.warning(f"⚠️ 读取统计汇总失败：{e}")
    else:
        st.warning("⚠️ 未找到统计汇总文件")
        st.info("""💡 **如何生成数据**:
1. 在上方配置统计规则（AI 推荐或自定义添加）
2. 点击「▶ 执行统计并生成 Excel」按钮
3. 返回此处查看生成的 Excel 文件""")
