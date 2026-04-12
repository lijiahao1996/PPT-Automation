# -*- coding: utf-8 -*-
"""Tab 1: 统计规则配置"""
import streamlit as st
import pandas as pd
import json
import os
import sys

def render_tab1(base_dir, templates_dir, output_dir):
    st.header("📋 统计规则配置")
    
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
    from app_config import get_output_dirs, ensure_output_dirs
    dirs = ensure_output_dirs(base_dir)
    uploaded_dir = dirs['uploaded']
    summary_dir = dirs['summary']
    
    # 确保目录存在
    os.makedirs(uploaded_dir, exist_ok=True)
    os.makedirs(summary_dir, exist_ok=True)
    
    # 加载配置
    if os.path.exists(stats_rules_file):
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            stats_config = json.load(f)
    else:
        stats_config = {"stats_sheets": {}}
    
    # ========== 文件选择 ==========
    st.subheader("📤 选择/上传 Excel")
    
    uploaded_files = []
    if os.path.exists(uploaded_dir):
        uploaded_files = [f for f in os.listdir(uploaded_dir) 
                         if f.endswith(('.xlsx', '.xls')) and not f.startswith('~')]
        uploaded_files.sort(reverse=True)
    
    # 初始化 session_state（只初始化一次）
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = uploaded_files[0] if uploaded_files else None
    
    # 文件选择器 - 不使用 key 避免状态问题
    if uploaded_files:
        selected_file = st.selectbox(
            "选择已上传的 Excel 文件",
            options=uploaded_files,
            index=uploaded_files.index(st.session_state.uploaded_file_name) if st.session_state.uploaded_file_name in uploaded_files else 0
        )
        # 直接更新，不触发 rerun
        st.session_state.uploaded_file_name = selected_file
    else:
        selected_file = None
        st.info("💡 暂无文件，请在下方上传")
    
    # 文件上传 - 使用 on_change 回调，不用 rerun
    def handle_upload():
        pass  # 上传后自动处理
    
    uploaded_file = st.file_uploader(
        "上传新的 Excel 文件",
        type=["xlsx", "xls"],
        key="uploader",
        on_change=handle_upload
    )
    
    if uploaded_file is not None:
        output_file = os.path.join(uploaded_dir, uploaded_file.name)
        
        try:
            if os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except PermissionError:
                    st.warning("⚠️ 文件被占用，请关闭 Excel 后重试")
                    st.stop()
            
            with open(output_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 更新选中文件
            st.session_state.uploaded_file_name = uploaded_file.name
            selected_file = uploaded_file.name
            
            # 显示预览（不 rerun）
            df_preview = pd.read_excel(output_file, nrows=5)
            st.success(f"✅ 上传成功：{uploaded_file.name}")
            with st.expander("📋 预览", expanded=True):
                st.dataframe(df_preview, width='stretch')
            
        except Exception as e:
            st.error(f"❌ 上传失败：{e}")
    
    # 显示当前文件
    if selected_file:
        raw_path = os.path.join(uploaded_dir, selected_file)
        if os.path.exists(raw_path):
            size = os.path.getsize(raw_path)
            st.success(f"✅ 当前文件：`{selected_file}` ({round(size/1024, 1)} KB)")
    
    st.markdown("---")
    
    # ========== AI 分析 ==========
    st.subheader("🤖 AI 智能分析")
    
    use_ai = st.checkbox("使用 AI 推荐统计规则", value=False, key="ai_check")
    
    if use_ai and selected_file:
        if st.button("开始 AI 分析", type="primary", key="ai_btn"):
            with st.spinner("分析中..."):
                try:
                    df = pd.read_excel(os.path.join(uploaded_dir, selected_file))
                    
                    sample = []
                    for _, row in df.head(5).iterrows():
                        d = {}
                        for c, v in row.items():
                            if hasattr(v, 'strftime'):
                                d[c] = v.strftime('%Y-%m-%d %H:%M:%S')
                            elif pd.isna(v):
                                d[c] = None
                            else:
                                d[c] = v
                        sample.append(d)
                    
                    cols = []
                    for c in df.columns:
                        vals = df[c].head(3).dropna().tolist()
                        pvals = [v.strftime('%Y-%m-%d %H:%M:%S') if hasattr(v, 'strftime') else str(v) for v in vals]
                        cols.append({'name': c, 'type': str(df[c].dtype), 'sample': pvals})
                    
                    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                    from ai.qwen_client import QwenClient
                    qwen = QwenClient(base_dir=base_dir)
                    
                    if qwen.is_available():
                        skill = ""
                        skill_path = os.path.join(base_dir, 'skills', 'stats-rule-recommender', 'SKILL.md')
                        if os.path.exists(skill_path):
                            with open(skill_path, 'r', encoding='utf-8') as f:
                                skill = f.read()
                        
                        prompt = f"""Excel: {selected_file}
列：{json.dumps(cols, ensure_ascii=False)}
数据：{json.dumps(sample, ensure_ascii=False)}
{skill}
推荐统计规则，输出 JSON。"""
                        
                        resp = qwen.chat("输出严格 JSON", prompt, json_mode=True)
                        if resp:
                            result = qwen.parse_json_response(resp)
                            if result and 'recommendations' in result:
                                st.session_state.ai_recs = result['recommendations']
                                st.success(f"AI 推荐了 {len(result['recommendations'])} 条规则")
                                st.rerun()
                    else:
                        st.warning("Qwen API 未配置")
                except Exception as e:
                    st.error(f"AI 分析失败：{e}")
    
    # 显示 AI 推荐
    if hasattr(st.session_state, 'ai_recs') and st.session_state.ai_recs:
        st.markdown("### AI 推荐")
        
        # 重新加载最新配置
        with open(stats_rules_file, 'r', encoding='utf-8') as f:
            stats_config = json.load(f)
        
        for i, rec in enumerate(st.session_state.ai_recs):
            name = rec.get('name', '')
            added = name in stats_config.get('stats_sheets', {})
            
            c1, c2 = st.columns([5, 1])
            with c1:
                st.write(f"{'✅' if added else '⬜'} **{name}** - {rec.get('description', '')}")
            with c2:
                if added:
                    if st.button("🗑️", key=f"del_{name}_{i}", use_container_width=True):
                        del stats_config['stats_sheets'][name]
                        with open(stats_rules_file, 'w', encoding='utf-8') as f:
                            json.dump(stats_config, f, ensure_ascii=False, indent=2)
                        st.rerun()
                else:
                    if st.button("➕", key=f"add_{name}_{i}", use_container_width=True):
                        stats_config['stats_sheets'][name] = {
                            'description': rec.get('description', ''),
                            'type': rec.get('type', 'kpi'),
                            'enabled': True,
                            'group_by': rec.get('group_by', []),
                            'metrics': rec.get('metrics', [])
                        }
                        with open(stats_rules_file, 'w', encoding='utf-8') as f:
                            json.dump(stats_config, f, ensure_ascii=False, indent=2)
                        st.rerun()
            
            with st.expander("详情", expanded=False):
                st.json(rec)
        
        if st.button("🚀 一键保存所有", type="primary", use_container_width=True, key="save_all"):
            cnt = 0
            for rec in st.session_state.ai_recs:
                name = rec.get('name', '')
                if name not in stats_config['stats_sheets']:
                    stats_config['stats_sheets'][name] = {
                        'description': rec.get('description', ''),
                        'type': rec.get('type', 'kpi'),
                        'enabled': True,
                        'group_by': rec.get('group_by', []),
                        'metrics': rec.get('metrics', [])
                    }
                    cnt += 1
            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                json.dump(stats_config, f, ensure_ascii=False, indent=2)
            if cnt > 0:
                st.success(f"✅ 保存 {cnt} 条")
                st.session_state.ai_recs = []
                st.rerun()
    
    st.markdown("---")
    
    # ========== 自定义添加 ==========
    st.subheader("📝 自定义添加")
    
    types = {"kpi": "KPI", "ranking": "排名", "composition": "占比", "comparison": "对比", 
             "trend": "趋势", "distribution": "分布", "matrix": "矩阵", "outlier": "异常"}
    
    c1, c2 = st.columns([2, 1])
    with c1:
        n_name = st.text_input("名称", key="n_name")
        n_type = st.selectbox("类型", list(types.keys()), format_func=lambda x: types[x], key="n_type")
        n_en = st.checkbox("启用", value=True, key="n_en")
        n_desc = st.text_area("描述", height=50, key="n_desc")
    with c2:
        n_grp = st.text_area("分组字段", height=85, key="n_grp")
        n_met = st.text_area("指标 JSON", value='[{"field":"销售额","agg":"sum","alias":"总额"}]', height=135, key="n_met")
    
    if st.button("➕ 添加", use_container_width=True, key="add_btn"):
        if not n_name.strip():
            st.error("请填写名称")
        elif not n_grp.strip():
            st.error("请填写分组字段")
        else:
            try:
                if n_name not in stats_config.get("stats_sheets", {}):
                    stats_config["stats_sheets"][n_name] = {
                        "description": n_desc,
                        "type": n_type,
                        "enabled": n_en,
                        "group_by": [g.strip() for g in n_grp.strip().split('\n') if g.strip()],
                        "metrics": json.loads(n_met)
                    }
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(stats_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已添加：{n_name}")
                    st.rerun()
                else:
                    st.warning("规则已存在")
            except json.JSONDecodeError as e:
                st.error(f"JSON 格式错误：{e}")
    
    st.markdown("---")
    
    # ========== 现有规则 ==========
    st.subheader("📋 现有统计规则")
    
    # 重新加载
    with open(stats_rules_file, 'r', encoding='utf-8') as f:
        stats_config = json.load(f)
    
    editing = st.session_state.get('editing_rule', None)
    
    if stats_config.get('stats_sheets'):
        for name, rule in stats_config['stats_sheets'].items():
            if editing == name:
                st.markdown(f"#### ✏️ 编辑：{name}")
                
                e_name = st.text_input("名称", value=name, key=f"en_{name}")
                e_type = st.selectbox("类型", list(types.keys()), format_func=lambda x: types[x],
                                     index=list(types.keys()).index(rule.get('type', 'kpi')) if rule.get('type') in types else 0,
                                     key=f"et_{name}")
                e_en = st.checkbox("启用", value=rule.get('enabled', True), key=f"ee_{name}")
                e_desc = st.text_area("描述", value=rule.get('description', ''), height=50, key=f"ed_{name}")
                e_grp = st.text_area("分组", value='\n'.join(rule.get('group_by', [])), height=70, key=f"eg_{name}")
                e_met = st.text_area("指标 JSON", value=json.dumps(rule.get('metrics', []), ensure_ascii=False, indent=2), height=100, key=f"em_{name}")
                
                cs, cc = st.columns(2)
                with cs:
                    if st.button("💾 保存", type="primary", key=f"sv_{name}", use_container_width=True):
                        try:
                            if e_name != name:
                                del stats_config["stats_sheets"][name]
                            stats_config["stats_sheets"][e_name] = {
                                "description": e_desc, "type": e_type, "enabled": e_en,
                                "group_by": [x.strip() for x in e_grp.strip().split('\n') if x.strip()],
                                "metrics": json.loads(e_met)
                            }
                            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            st.session_state.editing_rule = None
                            st.success("✅ 已保存")
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"JSON 错误：{e}")
                with cc:
                    if st.button("❌ 取消", key=f"ca_{name}", use_container_width=True):
                        st.session_state.editing_rule = None
                        st.rerun()
                st.markdown("---")
            else:
                ct, ce, cd = st.columns([5, 1, 1])
                with ct:
                    icon = "✅" if rule.get('enabled', True) else "❌"
                    with st.expander(f"{icon} {name}", expanded=False):
                        st.json(rule)
                with ce:
                    if st.button("✏️", key=f"eb_{name}", use_container_width=True):
                        st.session_state.editing_rule = name
                        st.rerun()
                with cd:
                    if st.button("🗑️", key=f"db_{name}", use_container_width=True):
                        del stats_config['stats_sheets'][name]
                        with open(stats_rules_file, 'w', encoding='utf-8') as f:
                            json.dump(stats_config, f, ensure_ascii=False, indent=2)
                        st.rerun()
    else:
        st.info("暂无规则")
    
    st.markdown("---")
    
    # ========== 执行 ==========
    st.subheader("💾 操作")
    
    if st.button("▶ 执行统计", type="primary", use_container_width=True):
        try:
            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                json.dump(stats_config, f, ensure_ascii=False, indent=2)
            
            if not selected_file:
                st.error("请先选择文件")
                st.stop()
            
            with st.spinner("执行中..."):
                sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                from core.stats_engine import StatsEngine
                
                raw_df = pd.read_excel(os.path.join(uploaded_dir, selected_file))
                out_name = selected_file.replace('.xlsx', '_统计汇总.xlsx') if selected_file.endswith('.xlsx') else selected_file + '_统计汇总.xlsx'
                out_path = os.path.join(summary_dir, out_name)
                
                engine = StatsEngine(base_dir=base_dir, raw_data_file=selected_file)
                results = engine.run_all(raw_df, output_path=out_path)
                
                st.session_state.generated_summary_name = out_name
                
                st.success(f"✅ 生成 {len(results)} 个 Sheet")
                
                with st.expander("结果", expanded=True):
                    for sn, df in results.items():
                        st.write(f"**{sn}**: {len(df)} 行")
                    skip = set(stats_config.get('stats_sheets', {}).keys()) - set(results.keys())
                    if skip:
                        st.warning(f"失败：{', '.join(sorted(skip))}")
            
            st.success("完成！")
        except Exception as e:
            st.error(f"失败：{e}")
    
    # ========== 查看数据 ==========
    st.markdown("---")
    st.header("📊 查看数据")
    
    summ = None
    if hasattr(st.session_state, 'generated_summary_name') and st.session_state.generated_summary_name:
        summ = os.path.join(summary_dir, st.session_state.generated_summary_name)
    
    if not summ or not os.path.exists(summ):
        if os.path.exists(summary_dir):
            for f in os.listdir(summary_dir):
                if f.endswith('.xlsx') and '统计汇总' in f:
                    summ = os.path.join(summary_dir, f)
                    break
    
    if summ and os.path.exists(summ):
        try:
            xls = pd.ExcelFile(summ)
            sheets = xls.sheet_names
            st.write(f"共 {len(sheets)} 个 Sheet")
            
            data = []
            for sn in sheets:
                df = pd.read_excel(summ, sheet_name=sn)
                data.append({'Sheet': sn, '行数': len(df), '列': len(df.columns), '字段': ', '.join(df.columns.tolist()[:5])})
            st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)
            
            sel = st.selectbox("查看详细", sheets)
            if sel:
                df = pd.read_excel(summ, sheet_name=sel)
                st.dataframe(df.head(100), use_container_width=True)
                st.caption(f"共 {len(df)} 行")
        except Exception as e:
            st.warning(f"读取失败：{e}")
    else:
        st.info("执行统计后在此查看结果")
