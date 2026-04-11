# -*- coding: utf-8 -*-
"""Tab 1: 统计规则配置 - AI 增强版"""
import streamlit as st
import pandas as pd
import json
import os

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
    
    use_ai = st.checkbox("✨ 使用 AI 自动推荐统计规则", value=False, key="use_ai_check")
    
    # 初始化待添加规则（移到外层，避免 rerun 后丢失）
    if 'ai_recommendations' not in st.session_state:
        st.session_state.ai_recommendations = []
    
    if use_ai and os.path.exists(raw_data_file):
        if st.button("🤖 开始 AI 智能分析", type="primary", key="start_ai_analysis"):
            try:
                df = pd.read_excel(raw_data_file)
                
                from core.field_detector import FieldDetector
                detector = FieldDetector(base_dir=base_dir, enable_ai=True)
                detected = detector.detect(df, raw_data_file_name)
                
                st.session_state['field_detection'] = detected
                
                st.success(f"✅ 检测到 {len(detected)} 个字段")
                
                with st.expander("📊 查看字段检测结果", expanded=True):
                    detection_data = []
                    for col, info in detected.items():
                        detection_data.append({
                            'Excel 列名': col,
                            '系统字段': info.get('standard_name', '未识别'),
                            '类型': info.get('type', 'unknown'),
                            '置信度': '🤖高' if info.get('confidence') == 'high' else '中',
                            '检测方法': 'AI+ 规则' if info.get('method') == 'ai_enhanced' else '规则'
                        })
                    st.dataframe(pd.DataFrame(detection_data), width='stretch', hide_index=True)
                
                from core.stats_recommender import StatsRecommender
                recommender = StatsRecommender()
                
                field_mapping = {col: info['standard_name'] for col, info in detected.items() if info.get('standard_name')}
                recommendations = recommender.recommend(field_mapping)
                
                # 保存推荐到 session_state，避免 rerun 后丢失
                st.session_state['ai_recommendations_list'] = recommendations
                
                if recommendations:
                    st.success(f"🤖 AI 推荐了 {len(recommendations)} 条统计规则")
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ AI 分析失败：{e}")
                import traceback
                with st.expander("📄 查看详细错误"):
                    st.code(traceback.format_exc())
    
    # 显示推荐列表（在外层，使用 session_state 保存的推荐）
    if 'ai_recommendations_list' in st.session_state:
        recommendations = st.session_state['ai_recommendations_list']
        
        if recommendations:
            st.success(f"🤖 AI 推荐了 {len(recommendations)} 条统计规则")
            
            # 一键全部保存按钮（放在顶部）
            not_added = [rec for rec in recommendations if rec['name'] not in st.session_state.stats_config.get('stats_sheets', {})]
            
            if not_added:
                col_all1, col_all2 = st.columns([3, 1])
                with col_all1:
                    st.info(f"📋 还有 {len(not_added)} 条规则未添加")
                with col_all2:
                    if st.button("🚀 一键保存所有推荐规则", type="primary", use_container_width=True, key="save_all_ai_rules"):
                        try:
                            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                                current_config = json.load(f)
                            
                            added_count = 0
                            for rec in not_added:
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
                            
                            st.success(f"✅ 已一键保存 {added_count} 条规则到 stats_rules.json")
                            st.balloons()
                            
                            st.session_state.stats_config = current_config
                            st.session_state.ai_recommendations_list = []
                            
                            st.info("💡 请刷新页面（F5）查看结果")
                        
                        except Exception as e:
                            st.error(f"❌ 保存失败：{e}")
                            import traceback
                            st.code(traceback.format_exc())
            
            st.markdown("---")
            st.markdown("### 推荐规则列表")
            
            for i, rec in enumerate(recommendations):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    status_icon = "✅" if rec.get('enabled', False) else "⬜"
                    st.write(f"{status_icon} **{rec['name']}** - {rec.get('ai_reason', '')}")
                
                with col2:
                    already_added = rec['name'] in st.session_state.stats_config.get('stats_sheets', {})
                    
                    if already_added:
                        st.success("✅ 已添加")
                    else:
                        # 单条立即保存按钮
                        if st.button("➕ 添加并保存", key=f"add_single_{rec['name']}_{i}", use_container_width=True):
                            try:
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
                                
                                st.success(f"✅ 已添加：{rec['name']}")
                                st.balloons()
                                
                                st.session_state.stats_config = current_config
                                
                                st.info("💡 请刷新页面（F5）查看结果")
                            
                            except Exception as e:
                                st.error(f"❌ 失败：{e}")
                                import traceback
                                st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # 现有统计规则
    st.subheader("💾 操作")
    
    if st.button("▶ 执行统计并生成 Excel", type="primary", use_container_width=True):
        try:
            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
            st.info("📝 配置已保存")
            
            with st.spinner("⚙️ 正在执行统计引擎..."):
                sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                from core.stats_engine import StatsEngine
                from core.data_loader import DataLoader
                
                data_loader = DataLoader(base_dir)
                raw_df = data_loader.load_raw_data(st.session_state.get('uploaded_file_name', '帆软销售明细.xlsx'))
                
                stats_engine = StatsEngine(base_dir=base_dir)
                output_path = os.path.join(output_dir, summary_file_name)
                results = stats_engine.run_all(raw_df, output_path=output_path)
                
                st.success(f"✅ 已生成 {len(results)} 个统计 Sheet！")
            
            st.success("🎉 完成！")
            
        except FileNotFoundError as e:
            st.error(f"❌ 数据文件不存在：{e}")
        except Exception as e:
            st.error(f"❌ 执行失败：{e}")
            import traceback
            with st.expander("📄 查看详细错误"):
                st.code(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("📋 现有统计规则")
    
    if stats_config["stats_sheets"]:
        for name, rule in stats_config["stats_sheets"].items():
            with st.expander(f"{'✅' if rule.get('enabled', True) else '❌'} {name}"):
                st.json(rule)
                
                if st.button(f"🗑️ 删除", key=f"delete_{name}"):
                    del stats_config["stats_sheets"][name]
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(stats_config, f, ensure_ascii=False, indent=2)
                    st.rerun()
    else:
        st.info("暂无统计规则")
