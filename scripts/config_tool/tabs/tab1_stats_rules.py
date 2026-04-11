# -*- coding: utf-8 -*-
"""Tab 1: 统计规则配置"""
import streamlit as st
import pandas as pd
import json
import os
import sys

def render_tab1(base_dir, templates_dir, output_dir):
    st.header("📋 统计规则配置")
    st.markdown("配置要生成哪些统计表格（Excel Sheet）")
    
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
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
    
    # 从 config.ini 读取默认文件名
    from app_config import get_default_raw_data_filename
    raw_data_file_name = get_default_raw_data_filename()
    raw_data_file = os.path.join(output_dir, raw_data_file_name)
    
    # 如果有上传的文件，使用上传的文件名
    if 'uploaded_file_name' in st.session_state:
        raw_data_file = os.path.join(output_dir, st.session_state['uploaded_file_name'])
        raw_data_file_name = st.session_state['uploaded_file_name']
    
    # 统计汇总文件名
    if raw_data_file_name.endswith('.xlsx'):
        summary_file_name = raw_data_file_name.replace('.xlsx', '_统计汇总.xlsx')
    else:
        summary_file_name = raw_data_file_name + '_统计汇总.xlsx'
    summary_file = os.path.join(output_dir, summary_file_name)
    
    # ========== Excel 上传功能 ==========
    st.subheader("📤 上传原始数据 Excel")
    st.caption("💡 上传从帆软导出的销售明细数据，或手动整理的数据")
    
    uploaded_file = st.file_uploader(
        "上传 Excel 文件",
        type=["xlsx", "xls"],
        help="上传帆软销售明细数据，保持原始文件名"
    )
    
    if uploaded_file is not None:
        os.makedirs(output_dir, exist_ok=True)
        uploaded_file_name = uploaded_file.name
        output_file = os.path.join(output_dir, uploaded_file_name)
        st.session_state['uploaded_file_name'] = uploaded_file_name
        raw_data_file = output_file
        
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
            file_size = os.path.getsize(output_file)
            
            st.success(f"✅ 上传成功！")
            st.info(f"""📊 **文件信息**：
- 保存位置：`{output_file}`
- 文件大小：{round(file_size/1024, 1)} KB
- 列名：{', '.join(df_preview.columns)}
- 预览：前 5 行数据已读取""")
            
            with st.expander("📋 查看数据预览", expanded=True):
                st.dataframe(df_preview, width='stretch')
            
        except Exception as e:
            st.error(f"❌ 上传失败：{e}")
    
    if os.path.exists(raw_data_file):
        file_size = os.path.getsize(raw_data_file)
        st.success(f"✅ 已找到数据文件：`{os.path.basename(raw_data_file)}` ({round(file_size/1024, 1)} KB)")
    else:
        st.info("💡 请先上传 Excel 数据文件，或运行 `Run.bat` 自动爬取数据")
    
    st.markdown("---")
    
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
        group_fields = st.text_area("分组字段（每行一个）", placeholder="销售员\n城市", height=100)
        
        st.markdown("### 统计指标")
        metrics_config = st.text_area("统计指标配置（JSON 格式）", 
                                     value='[{"field": "销售额", "agg": "sum", "alias": "总销售额"}]',
                                     height=150)
    
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
                try:
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已添加统计规则：{sheet_name}（已自动保存）")
                except Exception as e:
                    st.error(f"❌ 保存失败：{e}")
                    st.success(f"✅ 已添加统计规则：{sheet_name}")
                st.rerun()
            else:
                st.warning(f"⚠️ 统计规则已存在：{sheet_name}")
        except json.JSONDecodeError as e:
            st.error(f"❌ 指标配置格式错误：{e}")
    
    st.markdown("---")
    st.subheader("💾 操作")
    
    if st.button("▶ 执行统计并生成 Excel", type="primary", use_container_width=True):
        try:
            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
            st.info("📝 配置已保存")
            
            # 检查是否有上传的文件
            if 'uploaded_file_name' not in st.session_state:
                st.error("❌ 请先上传 Excel 数据文件\n\n💡 在上方「📤 上传原始数据 Excel」处上传文件")
                st.stop()
            
            uploaded_file_name = st.session_state['uploaded_file_name']
            raw_data_path = os.path.join(output_dir, uploaded_file_name)
            
            if not os.path.exists(raw_data_path):
                st.error(f"❌ 数据文件不存在：{raw_data_path}\n\n💡 请重新上传文件")
                st.stop()
            
            with st.spinner("⚙️ 正在执行统计引擎，生成 Excel Sheet..."):
                sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                from core.stats_engine import StatsEngine
                from core.data_loader import DataLoader
                
                data_loader = DataLoader(base_dir)
                raw_df = data_loader.load_raw_data(uploaded_file_name)
                
                # 生成统计汇总文件名（基于上传的文件名）
                if uploaded_file_name.endswith('.xlsx'):
                    summary_name = uploaded_file_name.replace('.xlsx', '_统计汇总.xlsx')
                else:
                    summary_name = uploaded_file_name + '_统计汇总.xlsx'
                output_path = os.path.join(output_dir, summary_name)
                
                stats_engine = StatsEngine(base_dir=base_dir, raw_data_file=uploaded_file_name)
                results = stats_engine.run_all(raw_df, output_path=output_path)
                
                st.success(f"✅ 已生成 {len(results)} 个统计 Sheet！")
                st.info(f"📄 输出文件：`{summary_name}`")
                
                with st.expander("📊 查看生成的 Sheet", expanded=True):
                    for sheet_name, df in results.items():
                        st.write(f"**{sheet_name}**: {len(df)} 行")
            
            st.success("🎉 配置保存并数据生成完成！现在可以去「📈 图表配置」页签配置图表了")
        except Exception as e:
            st.error(f"❌ 执行失败：{e}")
            import traceback
            with st.expander("📄 查看详细错误"):
                st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("📋 现有统计规则")
    
    edit_rule_name = st.session_state.get('editing_rule_name', None)
    
    if stats_config["stats_sheets"]:
        for name, rule in stats_config["stats_sheets"].items():
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
        
        # ========== 导出功能 ==========
        st.subheader("💾 导出数据")
        
        with open(summary_file, "rb") as f:
            file_size = os.path.getsize(summary_file)
            file_mtime = pd.Timestamp.fromtimestamp(os.path.getmtime(summary_file)).strftime('%Y-%m-%d %H:%M:%S')
            
            st.download_button(
                label=f"📄 下载统计汇总 Excel ({round(file_size/1024, 1)} KB, 更新于 {file_mtime})",
                data=f.read(),
                file_name="销售统计汇总.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width='stretch',
                help="下载完整的统计汇总 Excel 文件，包含所有 Sheet"
            )
        
        st.caption("💡 提示：下载的文件包含所有统计 Sheet，可直接用 Excel 或 WPS 打开编辑")
        st.markdown("---")
        
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
1. 在上方配置统计规则
2. 点击「▶ 执行统计并生成 Excel」按钮
3. 返回此处查看生成的 Excel 文件""")
