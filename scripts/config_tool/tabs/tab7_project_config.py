# -*- coding: utf-8 -*-
"""
Tab 7: 项目配置 - Web 界面管理 config.ini（简化版）
"""

import streamlit as st
import configparser
import os

def render_tab7(base_dir):
    """渲染 Tab 7: 项目配置"""
    st.header("⚙️ 项目配置")
    st.markdown("**管理项目配置文件 (config.ini)**")
    
    config_file = os.path.join(base_dir, 'config.ini')
    
    # 加载配置
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file, encoding='utf-8')
        st.success(f"✅ 已加载配置")
    else:
        st.warning("⚠️ 配置文件不存在，将创建新配置")
    
    st.markdown("---")
    
    # API Key 配置
    st.subheader("🔑 API Key 配置")
    st.caption("用于 AI 洞察生成")
    
    qwen_api_key = config.get('api_keys', 'qwen_api_key', fallback='')
    qwen_api_key = st.text_input(
        "Qwen API Key", 
        value=qwen_api_key, 
        type="password", 
        key="cfg_qwen_key",
        help="阿里云百炼 Qwen API Key - https://bailian.console.aliyun.com/"
    )
    
    st.info("💡 获取 API Key: https://bailian.console.aliyun.com/")
    
    st.markdown("---")
    
    # 路径配置
    st.subheader("📁 路径配置")
    st.caption("留空则使用默认值")
    
    col1, col2 = st.columns(2)
    with col1:
        output_dir = config.get('paths', 'output_dir', fallback='output')
        output_dir = st.text_input("输出目录", value=output_dir, key="cfg_output_dir")
        
        artifacts_dir = config.get('paths', 'artifacts_dir', fallback='artifacts')
        artifacts_dir = st.text_input("临时文件目录", value=artifacts_dir, key="cfg_artifacts_dir")
    
    with col2:
        logs_dir = config.get('paths', 'logs_dir', fallback='logs')
        logs_dir = st.text_input("日志目录", value=logs_dir, key="cfg_logs_dir")
    
    st.markdown("---")
    
    # AI 功能开关
    st.subheader("🤖 AI 功能配置")
    
    st.info("💡 **AI 增强功能说明**:\n\n1. **Tab 1 - AI 字段检测**: 自动识别 Excel 字段含义\n2. **Tab 1 - AI 统计推荐**: 基于字段自动推荐统计规则\n3. **AI 洞察生成**: 为 PPT 生成商业洞察文案")
    
    enable_ai = config.getboolean('ai', 'enable_ai_insight', fallback=True)
    enable_ai = st.checkbox(
        "启用 AI 洞察生成（PPT 文案）",
        value=enable_ai,
        key="cfg_enable_ai",
        help="禁用后将跳过 AI 洞察生成，节省 Token 消耗（但 PPT 中的洞察占位符将为空）"
    )
    
    st.markdown("---")
    st.subheader("📊 Tab 1 AI 功能")
    
    st.info("ℹ️ **Tab 1 中的 AI 功能**:\n\n在「📋 统计规则配置」页签上传 Excel 后，勾选「✨ 使用 AI 自动推荐统计规则」，然后点击「🤖 开始 AI 智能分析」即可。\n\n- ✅ 自动识别字段含义（如：sales → 销售额）\n- ✅ 推荐统计规则（KPI、排名、占比等）\n- ✅ 推荐图表类型\n\n**Token 消耗**: 每次约¥0.004，非常便宜！")
    
    st.markdown("---")
    
    # 高级配置
    st.subheader("⚙️ 高级配置")
    
    col1, col2 = st.columns(2)
    with col1:
        session_max_age = config.getint('advanced', 'session_max_age', fallback=7)
        session_max_age = st.number_input(
            "会话有效期（天）", 
            min_value=1, 
            max_value=30, 
            value=session_max_age, 
            key="cfg_session_age",
            help="帆软会话的有效期"
        )
    
    with col2:
        log_level = config.get('advanced', 'log_level', fallback='INFO')
        log_level = st.selectbox(
            "日志级别", 
            options=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
            index=['DEBUG', 'INFO', 'WARNING', 'ERROR'].index(log_level) if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR'] else 1, 
            key="cfg_log_level"
        )
    
    st.markdown("---")
    
    # 保存按钮
    if st.button("💾 保存配置", type="primary", use_container_width=True):
        try:
            # 更新配置
            config['api_keys'] = {
                'qwen_api_key': qwen_api_key
            }
            
            config['paths'] = {
                'output_dir': output_dir,
                'artifacts_dir': artifacts_dir,
                'logs_dir': logs_dir
            }
            
            config['ai'] = {
                'enable_ai_insight': 'True' if enable_ai else 'False'
            }
            
            config['advanced'] = {
                'session_max_age': str(session_max_age),
                'log_level': log_level
            }
            
            # 保存到文件
            with open(config_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            st.success(f"✅ 配置已保存")
            
            # 显示配置预览
            with st.expander("📄 查看配置"):
                st.code(f"""[api_keys]
qwen_api_key = {qwen_api_key[:10]}...

[paths]
output_dir = {output_dir}
artifacts_dir = {artifacts_dir}
logs_dir = {logs_dir}

[advanced]
session_max_age = {session_max_age}
log_level = {log_level}
""")
            
        except Exception as e:
            st.error(f"❌ 保存失败：{e}")
