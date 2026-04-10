# -*- coding: utf-8 -*-
"""
Tab 8: 生成 PPT 报告
一键执行完整流程：统计分析 → 图表生成 → PPT 报告
"""
import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime


def render_tab8(base_dir, output_dir, templates_dir):
    """渲染 Tab 8: 生成 PPT 报告"""
    
    st.header("🚀 生成 PPT 报告")
    st.markdown("**一键执行完整流程：统计分析 → 图表生成 → PPT 报告**")
    
    # 初始化执行器
    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
    
    # 日志存储
    if 'execution_logs' not in st.session_state:
        st.session_state.execution_logs = []
    if 'execution_running' not in st.session_state:
        st.session_state.execution_running = False
    if 'execution_result' not in st.session_state:
        st.session_state.execution_result = None
    
    def add_log(message: str, level: str = 'INFO'):
        """添加日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        st.session_state.execution_logs.append(log_entry)
    
    def clear_logs():
        """清空日志"""
        st.session_state.execution_logs = []
        st.session_state.execution_result = None
    
    # 检测当前文件状态
    st.subheader("📊 当前状态")
    
    files_detected = {'raw_data': None, 'summary': None, 'ppt_reports': []}
    
    # 优先使用 session_state 中记录的上传文件名
    if 'uploaded_file_name' in st.session_state:
        uploaded_name = st.session_state['uploaded_file_name']
        raw_path = os.path.join(output_dir, uploaded_name)
        if os.path.exists(raw_path):
            files_detected['raw_data'] = uploaded_name
            # 统计汇总文件名
            summary_name = uploaded_name.replace('.xlsx', '_统计汇总.xlsx') if uploaded_name.endswith('.xlsx') else uploaded_name + '_统计汇总.xlsx'
            summary_path = os.path.join(output_dir, summary_name)
            if os.path.exists(summary_path):
                files_detected['summary'] = summary_name
    
    # 如果没有记录，则自动检测
    if not files_detected['raw_data'] and os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                files_detected['raw_data'] = f
                break
    
    # 检测统计汇总文件
    if not files_detected['summary'] and os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                files_detected['summary'] = f
                break
    
    # 检测 PPT 报告（根据上传的文件名查找对应的报告）
    if os.path.exists(output_dir):
        # 优先使用 session_state 中记录的上传文件名
        if 'uploaded_file_name' in st.session_state:
            uploaded_name = st.session_state['uploaded_file_name']
            base_name = uploaded_name.replace('.xlsx', '') if uploaded_name.endswith('.xlsx') else uploaded_name
            
            # 查找所有 PPT 文件
            all_ppt = [f for f in os.listdir(output_dir) if f.endswith('.pptx') and not f.startswith('~')]
            
            # 优先查找包含基础名称的 PPT 报告
            matching_ppt = [f for f in all_ppt if base_name in f]
            other_ppt = [f for f in all_ppt if base_name not in f]
            
            # 排序：匹配的文件在前，按时间倒序
            matching_ppt.sort(reverse=True)
            other_ppt.sort(reverse=True)
            
            # 合并列表
            files_detected['ppt_reports'] = matching_ppt + other_ppt
        else:
            # 没有记录，显示所有 PPT 文件
            ppt_files = [f for f in os.listdir(output_dir) if f.endswith('.pptx') and not f.startswith('~')]
            ppt_files.sort(reverse=True)
            files_detected['ppt_reports'] = ppt_files
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        # 只展示与 session_state 中记录的上传文件匹配的原始数据
        matching_raw = None
        if 'uploaded_file_name' in st.session_state:
            uploaded_name = st.session_state['uploaded_file_name']
            raw_path = os.path.join(output_dir, uploaded_name)
            if os.path.exists(raw_path):
                matching_raw = uploaded_name
        
        if matching_raw:
            file_size = os.path.getsize(os.path.join(output_dir, matching_raw))
            st.success(f"✅ 原始数据\n\n`{matching_raw}`\n\n{round(file_size/1024, 1)} KB")
        else:
            st.info("ℹ️ 原始数据\n\n未上传\n\n请先在「📋 统计规则配置」页签上传 Excel 数据文件")
    
    with col_s2:
        # 只展示与上传文件匹配的统计汇总
        matching_summary = None
        if 'uploaded_file_name' in st.session_state and files_detected['summary']:
            uploaded_name = st.session_state['uploaded_file_name']
            expected_summary = uploaded_name.replace('.xlsx', '_统计汇总.xlsx') if uploaded_name.endswith('.xlsx') else uploaded_name + '_统计汇总.xlsx'
            # 检查是否存在匹配的统计汇总
            if files_detected['summary'] == expected_summary and os.path.exists(os.path.join(output_dir, expected_summary)):
                matching_summary = expected_summary
        
        if matching_summary:
            file_size = os.path.getsize(os.path.join(output_dir, matching_summary))
            st.success(f"✅ 统计汇总\n\n`{matching_summary}`\n\n{round(file_size/1024, 1)} KB")
        else:
            st.warning("⚠️ 统计汇总\n\n未生成\n\n请先在「📋 统计规则配置」页签上传 Excel 并点击【🔄 保存配置并生成数据】")
    
    with col_s3:
        # 只显示与上传文件名匹配的 PPT 报告
        matching_ppt = None
        if 'uploaded_file_name' in st.session_state and files_detected['ppt_reports']:
            uploaded_name = st.session_state['uploaded_file_name']
            base_name = uploaded_name.replace('.xlsx', '') if uploaded_name.endswith('.xlsx') else uploaded_name
            # 查找匹配的文件
            for ppt_file in files_detected['ppt_reports']:
                if base_name in ppt_file:
                    matching_ppt = ppt_file
                    break
        
        if matching_ppt:
            file_size = os.path.getsize(os.path.join(output_dir, matching_ppt))
            st.success(f"✅ PPT 报告\n\n`{matching_ppt}`\n\n{round(file_size/1024, 1)} KB")
        else:
            st.info("ℹ️ PPT 报告\n\n未生成\n\n将在执行时生成")
    
    st.markdown("---")
    
    # 执行选项
    st.subheader("⚙️ 执行选项")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        regenerate_stats = st.checkbox(
            "🔄 重新生成统计数据",
            value=False,
            help="如果已存在统计汇总文件，勾选后会重新生成"
        )
    
    with col_opt2:
        # PPT 模板选择方式
        template_mode = st.radio(
            "模板选择",
            options=["使用已有模板", "上传新模板"],
            index=0,
            horizontal=True,
            key="template_mode"
        )
        
        if template_mode == "使用已有模板":
            # 扫描 templates 目录中的 PPT 文件
            template_files = []
            if os.path.exists(templates_dir):
                template_files = [f for f in os.listdir(templates_dir) if f.endswith('.pptx') and not f.startswith('~')]
            
            template_name = st.selectbox(
                "📄 选择 PPT 模板",
                options=template_files if template_files else ["销售分析报告_标准模板.pptx"],
                help="PPT 模板文件名（在 templates 目录下）"
            )
        else:
            # 上传新模板
            uploaded_template = st.file_uploader(
                "📄 上传 PPT 模板",
                type=["pptx"],
                help="上传自定义 PPT 模板"
            )
            
            if uploaded_template is not None:
                # 保存上传的模板
                template_name = uploaded_template.name
                template_path = os.path.join(templates_dir, template_name)
                with open(template_path, "wb") as f:
                    f.write(uploaded_template.getbuffer())
                st.success(f"✅ 模板已保存：{template_name}")
            else:
                template_name = "销售分析报告_标准模板.pptx"
    
    st.markdown("---")
    
    # 执行按钮
    st.subheader("🎯 执行")
    
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        start_button = st.button(
            "▶️ 开始生成 PPT 报告",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.execution_running
        )
    
    with col_btn2:
        if st.button("🗑️ 清空日志", use_container_width=True):
            clear_logs()
    
    # 创建日志容器和进度条（在 if start_button 之前，这样重新运行时不会丢失）
    log_container = st.empty()
    progress_bar = st.progress(0)
    
    if start_button and not st.session_state.execution_running:
        import threading
        import time
        
        st.session_state.execution_running = True
        clear_logs()
        
        result = [None]
        error = [None]
        generator = [None]
        
        def run_pipeline():
            try:
                from ppt_report_executor import PPTReportGenerator
                generator[0] = PPTReportGenerator(base_dir=base_dir)
                
                use_raw_data_file = None
                if 'uploaded_file_name' in st.session_state:
                    use_raw_data_file = st.session_state['uploaded_file_name']
                
                result[0] = generator[0].run_full_pipeline(
                    regenerate_stats=regenerate_stats,
                    template_name=template_name,
                    raw_data_file=use_raw_data_file
                )
            except Exception as e:
                error[0] = e
        
        # 启动后台线程
        thread = threading.Thread(target=run_pipeline)
        thread.start()
        
        # 实时处理日志队列
        while thread.is_alive() or (generator[0] and not generator[0].log_queue.empty()):
            if generator[0]:
                while not generator[0].log_queue.empty():
                    try:
                        log_entry = generator[0].log_queue.get_nowait()
                        if 'execution_logs' not in st.session_state:
                            st.session_state.execution_logs = []
                        st.session_state.execution_logs.append(log_entry)
                        # 实时更新显示
                        logs_text = ''.join(st.session_state.execution_logs)
                        try:
                            log_container.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
                        except:
                            pass
                    except:
                        break
            time.sleep(0.1)
        
        # 更新进度
        progress_bar.progress(100)
        
        # 更新结果
        if error[0]:
            st.error(f"❌ 错误：{error[0]}")
        else:
            st.session_state.execution_result = result[0]
            # 更新文件显示
            if generator[0]:
                files = generator[0].detect_files()
                if files.get('summary'):
                    st.success(f"✅ 统计汇总：{files['summary']}")
                if files.get('ppt_reports'):
                    latest_ppt = sorted(files['ppt_reports'])[-1]
                    st.success(f"✅ PPT 报告：{latest_ppt}")
        
        st.session_state.execution_running = False
        if files.get('ppt_reports'):
            latest_ppt = sorted(files['ppt_reports'])[-1]
            ppt_path = os.path.join(output_dir, latest_ppt)
            with open(ppt_path, 'rb') as f:
                st.download_button(
                    label=f"📄 下载 PPT 报告 ({latest_ppt})",
                    data=f.read(),
                    file_name=latest_ppt,
                    mime='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    use_container_width=True
                )

