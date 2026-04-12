# -*- coding: utf-8 -*-
"""
Tab 8: 生成 PPT 报告
一键执行完整流程：统计分析 → 图表生成 → PPT 报告
"""
import streamlit as st
import pandas as pd
import os
import sys
import threading
import time
from datetime import datetime
from queue import Queue


def render_tab8(base_dir, output_dir, templates_dir):
    """渲染 Tab 8: 生成 PPT 报告"""
    
    st.header("🚀 生成 PPT 报告")
    st.markdown("**一键执行完整流程：统计分析 → 图表生成 → PPT 报告**")
    
    # 添加脚本路径
    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
    
    # 初始化 session_state
    if 'execution_logs' not in st.session_state:
        st.session_state.execution_logs = []
    if 'execution_running' not in st.session_state:
        st.session_state.execution_running = False
    if 'execution_result' not in st.session_state:
        st.session_state.execution_result = None
    if 'execution_completed' not in st.session_state:
        st.session_state.execution_completed = False
    
    # 执行完成后自动重置运行状态
    if st.session_state.get('execution_completed', False):
        st.session_state.execution_running = False
        st.session_state.execution_completed = False
    
    def clear_logs():
        st.session_state.execution_logs = []
        st.session_state.execution_result = None
    
    # 获取目录结构
    from app_config import get_output_dirs, ensure_output_dirs
    dirs = ensure_output_dirs(base_dir)
    uploaded_dir = dirs['uploaded']
    summary_dir = dirs['summary']
    report_dir = dirs['report']
    
    # ========== 检测当前文件状态 ==========
    st.subheader("📊 当前状态")
    
    files = {'raw_data': None, 'summary': None, 'ppt_reports': []}
    
    # 检测 uploaded 目录中的原始数据
    if os.path.exists(uploaded_dir):
        uploaded_files = [f for f in os.listdir(uploaded_dir) 
                         if f.endswith(('.xlsx', '.xls')) and not f.startswith('~')]
        uploaded_files.sort(reverse=True)
        if uploaded_files:
            files['raw_data'] = uploaded_files[0]
    
    # 检测 summary 目录中的统计汇总
    if os.path.exists(summary_dir):
        summary_files = [f for f in os.listdir(summary_dir) 
                        if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~')]
        summary_files.sort(reverse=True)
        if summary_files:
            files['summary'] = summary_files[0]
    
    # 检测 report 目录中的 PPT 报告
    if os.path.exists(report_dir):
        ppt_files = [f for f in os.listdir(report_dir) if f.endswith('.pptx') and not f.startswith('~')]
        ppt_files.sort(reverse=True)
        files['ppt_reports'] = ppt_files
    
    # 显示状态
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        if files['raw_data']:
            file_path = os.path.join(uploaded_dir, files['raw_data'])
            file_size = os.path.getsize(file_path)
            st.success(f"✅ 原始数据\n\n`{files['raw_data']}`\n\n{round(file_size/1024, 1)} KB")
        else:
            st.info("ℹ️ 原始数据\n\n未上传\n\n请先在「📋 统计规则配置」页签上传 Excel")
    
    with col_s2:
        if files['summary']:
            file_path = os.path.join(summary_dir, files['summary'])
            file_size = os.path.getsize(file_path)
            st.success(f"✅ 统计汇总\n\n`{files['summary']}`\n\n{round(file_size/1024, 1)} KB")
        else:
            st.warning("⚠️ 统计汇总\n\n未生成\n\n请先在「📋 统计规则配置」页签生成数据")
    
    with col_s3:
        # 只显示与当前数据匹配的 PPT
        if files['raw_data'] and files['summary']:
            base_name = files['raw_data'].replace('.xlsx', '')
            matching_ppt = [f for f in files['ppt_reports'] if base_name in f]
            
            if matching_ppt:
                latest_ppt = matching_ppt[0]
                file_path = os.path.join(report_dir, latest_ppt)
                file_size = os.path.getsize(file_path)
                st.success(f"✅ PPT 报告\n\n`{latest_ppt}`\n\n{round(file_size/1024, 1)} KB")
            else:
                st.info("ℹ️ PPT 报告\n\n未生成\n\n点击按钮生成")
        else:
            st.info("ℹ️ PPT 报告\n\n未生成\n\n先上传数据并生成统计汇总")
    
    st.markdown("---")
    
    # ========== 执行选项 ==========
    st.subheader("⚙️ 执行选项")
    
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        regenerate_stats = st.checkbox(
            "🔄 重新生成统计数据",
            value=False,
            help="如果已存在统计汇总文件，勾选后会重新生成"
        )
    
    with col_opt2:
        template_mode = st.radio(
            "模板选择",
            options=["使用已有模板", "上传新模板"],
            index=0,
            horizontal=True,
            key="template_mode"
        )
        
        if template_mode == "使用已有模板":
            template_files = []
            if os.path.exists(templates_dir):
                template_files = [f for f in os.listdir(templates_dir) if f.endswith('.pptx') and not f.startswith('~')]
            
            template_name = st.selectbox(
                "📄 选择 PPT 模板",
                options=template_files if template_files else ["销售分析报告_标准模板.pptx"],
                help="PPT 模板文件名（在 templates 目录下）"
            )
        else:
            uploaded_template = st.file_uploader(
                "📄 上传 PPT 模板",
                type=["pptx"],
                help="上传自定义 PPT 模板"
            )
            
            if uploaded_template is not None:
                template_name = uploaded_template.name
                template_path = os.path.join(templates_dir, template_name)
                with open(template_path, "wb") as f:
                    f.write(uploaded_template.getbuffer())
                st.success(f"✅ 模板已保存：{template_name}")
                st.rerun()
            else:
                template_name = "销售分析报告_标准模板.pptx"
    
    st.markdown("---")
    
    # ========== 执行按钮 ==========
    st.subheader("🎯 执行")
    
    col_btn1, col_btn2 = st.columns([3, 1])
    
    with col_btn1:
        start_button = st.button(
            "▶️ 生成 PPT 报告",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.execution_running
        )
    
    with col_btn2:
        if st.button("🗑️ 清空日志", use_container_width=True):
            clear_logs()
            st.rerun()
    
    # 日志容器
    log_container = st.empty()
    progress_bar = st.progress(0)
    
    # 显示现有日志
    if st.session_state.execution_logs:
        logs_text = ''.join(st.session_state.execution_logs)
        log_container.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
    
    # ========== 执行逻辑 ==========
    if start_button and not st.session_state.execution_running:
        st.session_state.execution_running = True
        clear_logs()
        
        # 创建局部日志队列（线程安全）
        log_queue = Queue()
        
        result = {'success': False, 'files': {}}
        error_msg = None
        
        def run_pipeline():
            nonlocal result, error_msg
            try:
                from generate_report import generate_report
                
                # 获取数据文件名（使用刚才检测到的 files['raw_data']）
                use_raw_data_file = files.get('raw_data')
                
                if not use_raw_data_file:
                    # 如果没检测到，再尝试自动查找
                    for f in os.listdir(output_dir):
                        if f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                            use_raw_data_file = f
                            break
                
                if not use_raw_data_file:
                    error_msg = "未找到原始数据文件，请先上传 Excel 文件"
                    return
                
                # 日志回调（使用闭包访问 log_queue）
                def log_callback(msg):
                    log_queue.put(msg + "<br>")
                    print(msg)
                
                log_callback("=" * 60)
                log_callback("开始生成 PPT 报告...")
                log_callback(f"使用模板：{template_name}")
                log_callback(f"原始数据：{use_raw_data_file}")
                log_callback(f"统计汇总：{use_raw_data_file.replace('.xlsx', '_统计汇总.xlsx')}")
                log_callback(f"将生成：{use_raw_data_file.replace('.xlsx', '')}_报告_xxx.pptx")
                log_callback("=" * 60)
                
                # 调用生成函数（直接传入文件名）
                success = generate_report(
                    template_name=template_name,
                    output_name=None,  # 自动生成文件名
                    parallel_charts=True,
                    log_callback=log_callback,
                    raw_data_name=use_raw_data_file  # 直接传入原始数据文件名
                )
                
                result['success'] = success
                if success:
                    # 查找最新 PPT
                    ppt_files = [f for f in os.listdir(output_dir) if f.endswith('.pptx') and not f.startswith('~')]
                    if ppt_files:
                        ppt_files.sort(reverse=True)
                        result['files']['ppt_report'] = ppt_files[0]
                        log_callback(f"✅ PPT 生成成功：{ppt_files[0]}")
                else:
                    log_callback("❌ PPT 生成失败")
                    
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
                log_callback(f"❌ 错误：{str(e)}")
            finally:
                # 不直接设置 session_state，由主线程处理
                pass
        
        # 启动线程（非 daemon 模式）
        thread = threading.Thread(target=run_pipeline, daemon=False)
        thread.start()
        
        # 等待完成
        timeout = 300
        start_time = time.time()
        
        while thread.is_alive() and (time.time() - start_time) < timeout:
            time.sleep(0.5)
            
            # 更新日志（从局部队列读取）
            while not log_queue.empty():
                try:
                    log_entry = log_queue.get_nowait()
                    st.session_state.execution_logs.append(log_entry)
                except:
                    break
            
            if st.session_state.execution_logs:
                logs_text = ''.join(st.session_state.execution_logs)
                log_container.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
        
        # 线程结束后处理
        if thread.is_alive():
            log_callback("⚠️ 执行超时（超过 5 分钟）")
        
        # 确保最后更新一次日志
        while not log_queue.empty():
            try:
                log_entry = log_queue.get_nowait()
                st.session_state.execution_logs.append(log_entry)
            except:
                break
        
        if st.session_state.execution_logs:
            logs_text = ''.join(st.session_state.execution_logs)
            log_container.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)
        
        progress_bar.progress(100)
        
        # 保存执行结果
        if result['success']:
            st.session_state.execution_result = result
        
        # 标记执行完成（下次渲染时会自动重置 execution_running）
        st.session_state.execution_completed = True
        
        # 不再自动 rerun，让用户手动操作
    
    # ========== 显示结果 ==========
    if st.session_state.execution_result and st.session_state.execution_result.get('success'):
        result = st.session_state.execution_result
        
        st.success("✅ PPT 报告生成成功！")
        
        # 下载区域
        st.markdown("---")
        st.subheader("📥 下载生成的文件")
        
        col_down1, col_down2 = st.columns(2)
        
        # 下载统计汇总 Excel
        with col_down1:
            if files['summary']:
                summary_path = os.path.join(output_dir, files['summary'])
                if os.path.exists(summary_path):
                    with open(summary_path, 'rb') as f:
                        st.download_button(
                            label=f"📊 下载统计汇总 ({files['summary']})",
                            data=f.read(),
                            file_name=files['summary'],
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            use_container_width=True
                        )
        
        # 下载 PPT 报告
        with col_down2:
            if result.get('files', {}).get('ppt_report'):
                latest_ppt = result['files']['ppt_report']
                ppt_path = os.path.join(output_dir, latest_ppt)
                if os.path.exists(ppt_path):
                    with open(ppt_path, 'rb') as f:
                        st.download_button(
                            label=f"📄 下载 PPT 报告 ({latest_ppt})",
                            data=f.read(),
                            file_name=latest_ppt,
                            mime='application/vnd.openxmlformats-officedocument.presentationml.presentation',
                            use_container_width=True
                        )
    
    elif st.session_state.execution_result and not st.session_state.execution_result.get('success'):
        st.error("❌ PPT 报告生成失败，请查看上方日志")
