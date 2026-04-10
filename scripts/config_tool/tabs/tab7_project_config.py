# -*- coding: utf-8 -*-
"""
Tab 7: 项目配置 - Web 界面管理 config.ini
"""

import streamlit as st
import configparser
import os

def render_tab7(base_dir):
    """渲染 Tab 7: 项目配置"""
    st.header("⚙️ 项目配置")
    st.markdown("**管理项目配置文件 (config.ini)**")
    
    config_file = os.path.join(base_dir, 'config.ini')
    config_example = os.path.join(base_dir, 'config.ini.example')
    
    # 加载配置
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
        st.success(f"✅ 已加载配置：{config_file}")
    else:
        st.warning("⚠️ 配置文件不存在，将创建新配置")
        if os.path.exists(config_example):
            config.read(config_example, encoding='utf-8')
    
    # 帆软账号配置
    st.subheader("🔐 帆软账号配置")
    
    col1, col2 = st.columns(2)
    with col1:
        fanruan_username = config.get('fanruan', 'username', fallback='')
        fanruan_username = st.text_input("帆软账号", value=fanruan_username, key="cfg_fanruan_user")
    
    with col2:
        fanruan_password = config.get('fanruan', 'password', fallback='')
        fanruan_password = st.text_input("帆软密码", value=fanruan_password, type="password", key="cfg_fanruan_pwd")
    
    fanruan_data_url = config.get('fanruan', 'data_url', fallback='https://demo.fanruan.com/webroot/decision#/datacenter/config/table/5bad5de2769141e8bcada4e0df0e5b5d')
    fanruan_data_url = st.text_input("数据 URL", value=fanruan_data_url, key="cfg_fanruan_url")
    
    st.markdown("---")
    
    # API Key 配置
    st.subheader("🔑 API Key 配置")
    
    qwen_api_key = config.get('api_keys', 'qwen_api_key', fallback='')
    qwen_api_key = st.text_input("Qwen API Key", value=qwen_api_key, type="password", key="cfg_qwen_key", help="阿里云百炼 Qwen API Key")
    
    st.info("💡 获取 API Key: https://bailian.console.aliyun.com/")
    
    st.markdown("---")
    
    # 路径配置
    st.subheader("📁 路径配置")
    st.caption("一般不需要修改，留空则使用当前目录")
    
    col1, col2 = st.columns(2)
    with col1:
        work_dir = config.get('paths', 'work_dir', fallback='')
        work_dir = st.text_input("工作目录", value=work_dir, key="cfg_work_dir")
        
        output_dir = config.get('paths', 'output_dir', fallback='')
        output_dir = st.text_input("输出目录", value=output_dir, key="cfg_output_dir")
    
    with col2:
        scripts_dir = config.get('paths', 'scripts_dir', fallback='')
        scripts_dir = st.text_input("脚本目录", value=scripts_dir, key="cfg_scripts_dir")
        
        artifacts_dir = config.get('paths', 'artifacts_dir', fallback='')
        artifacts_dir = st.text_input("临时文件目录", value=artifacts_dir, key="cfg_artifacts_dir")
    
    logs_dir = config.get('paths', 'logs_dir', fallback='')
    logs_dir = st.text_input("日志目录", value=logs_dir, key="cfg_logs_dir")
    
    st.markdown("---")
    
    # 文件名配置
    st.subheader("📄 文件名配置")
    st.caption("原始数据文件和统计汇总文件的文件名")
    
    col1, col2 = st.columns(2)
    with col1:
        raw_data_file = config.get('paths', 'raw_data_file', fallback='帆软销售明细.xlsx')
        raw_data_file = st.text_input("原始数据文件名", value=raw_data_file, key="cfg_raw_data_file")
    
    with col2:
        summary_file = config.get('paths', 'summary_file', fallback='销售统计汇总.xlsx')
        summary_file = st.text_input("统计汇总文件名", value=summary_file, key="cfg_summary_file")
    
    st.markdown("---")
    
    # 高级配置
    st.subheader("⚙️ 高级配置")
    
    col1, col2 = st.columns(2)
    with col1:
        session_max_age = config.getint('advanced', 'session_max_age', fallback=7)
        session_max_age = st.number_input("会话有效期（天）", min_value=1, max_value=30, value=session_max_age, key="cfg_session_age")
    
    with col2:
        log_level = config.get('advanced', 'log_level', fallback='INFO')
        log_level = st.selectbox("日志级别", options=['DEBUG', 'INFO', 'WARNING', 'ERROR'], index=['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(log_level) if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR'] else 1, key="cfg_log_level")
    
    st.markdown("---")
    
    # 保存按钮
    if st.button("💾 保存配置", type="primary", use_container_width=True):
        try:
            # 更新配置
            config['fanruan'] = {
                'username': fanruan_username,
                'password': fanruan_password,
                'data_url': fanruan_data_url
            }
            
            config['api_keys'] = {
                'qwen_api_key': qwen_api_key
            }
            
            config['paths'] = {
                'work_dir': work_dir,
                'output_dir': output_dir,
                'scripts_dir': scripts_dir,
                'artifacts_dir': artifacts_dir,
                'logs_dir': logs_dir,
                'raw_data_file': raw_data_file,
                'summary_file': summary_file
            }
            
            config['advanced'] = {
                'session_max_age': str(session_max_age),
                'log_level': log_level
            }
            
            # 保存到文件
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            st.success(f"✅ 配置已保存到：{config_file}")
            
            # 显示配置预览
            with st.expander("📄 查看配置预览"):
                st.code(f"""[fanruan]
username = {fanruan_username}
password = {'*' * len(fanruan_password)}
data_url = {fanruan_data_url}

[api_keys]
qwen_api_key = {qwen_api_key[:10]}...

[paths]
work_dir = {work_dir or '(当前目录)'}
output_dir = {output_dir or '(当前目录)'}
scripts_dir = {scripts_dir or '(当前目录)'}
artifacts_dir = {artifacts_dir or '(当前目录)'}
logs_dir = {logs_dir or '(当前目录)'}
raw_data_file = {raw_data_file}
summary_file = {summary_file}

[advanced]
session_max_age = {session_max_age}
log_level = {log_level}
""")
            
        except Exception as e:
            st.error(f"❌ 保存失败：{e}")
            import traceback
            st.code(traceback.format_exc())
