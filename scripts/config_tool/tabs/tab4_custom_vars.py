# -*- coding: utf-8 -*-
"""Tab 4: 自定义变量（支持编辑）"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

def render_tab4(artifacts_dir):
    st.header("⚙️ 自定义变量")
    st.markdown("自定义 PPT 模板中的变量，支持文本、表格、日期、图片、视频、链接等多种类型")
    
    placeholders_file = os.path.join(artifacts_dir, "placeholders.json")
    
    # 创建资源目录
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(artifacts_dir)), "resources")
    images_dir = os.path.join(resources_dir, "images")
    videos_dir = os.path.join(resources_dir, "videos")
    
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {"placeholders": {"charts": {}, "insights": {}, "text": {}, "tables": {}, "dates": {}, "images": {}, "videos": {}, "links": {}}}
    
    # ========== 区块 1: 文本变量 ==========
    st.markdown("### 📝 文本变量")
    st.markdown("*用于 PPT 中的文本占位符，例如报告标题、公司名称等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加文本变量")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custom_var_key = st.text_input("变量 Key", placeholder="例如：report_title", help="用于 PPT 占位符：[TEXT:xxx]", key="text_var_key")
            custom_var_desc = st.text_input("变量描述", placeholder="例如：报告标题", key="text_var_desc")
        
        with col2:
            custom_var_default = st.text_area("默认值", placeholder="例如：2026 年 Q1 销售分析报告", height=80, key="text_var_default")
            custom_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, help="占位符所在的 PPT 页码（从 0 开始）", key="text_var_page")
        
        if st.button("➕ 添加文本变量", type="primary", key="add_text_var"):
            if not custom_var_key:
                st.error("❌ 请填写变量 Key")
            else:
                full_key = f"TEXT:{custom_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "text" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["text"] = {}
                
                placeholders_config["placeholders"]["text"][full_key] = {
                    "description": custom_var_desc, 
                    "default": custom_var_default, 
                    "slide_index": custom_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加自定义变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的文本变量")
        
        text_vars = placeholders_config.get('placeholders', {}).get('text', {})
        
        if text_vars:
            editing_text_var = st.session_state.get('editing_text_var', None)
            
            for var_key, var_cfg in text_vars.items():
                if var_key.startswith('TEXT:'):
                    if editing_text_var == var_key:
                        st.markdown(f"#### ✏️ 编辑：{var_key}")
                        
                        edit_key = st.text_input("变量 Key", value=var_key.replace('TEXT:', ''), key=f"edit_text_key_{var_key}")
                        edit_desc = st.text_input("变量描述", value=var_cfg.get('description', ''), key=f"edit_text_desc_{var_key}")
                        edit_default = st.text_area("默认值", value=var_cfg.get('default', ''), height=80, key=f"edit_text_default_{var_key}")
                        edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_text_page_{var_key}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存修改", type="primary", key=f"save_text_edit_{var_key}"):
                                new_key = f"TEXT:{edit_key}"
                                if new_key != var_key and new_key in text_vars:
                                    st.error(f"❌ 变量 Key 已存在：{new_key}")
                                else:
                                    if new_key != var_key:
                                        del placeholders_config["placeholders"]["text"][var_key]
                                    
                                    placeholders_config["placeholders"]["text"][new_key] = {
                                        "description": edit_desc,
                                        "default": edit_default,
                                        "slide_index": edit_page
                                    }
                                    
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    
                                    st.session_state['editing_text_var'] = None
                                    st.success(f"✅ 已保存修改")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 取消编辑", key=f"cancel_text_edit_{var_key}"):
                                st.session_state['editing_text_var'] = None
                                st.rerun()
                        
                        st.divider()
                    else:
                        with st.container(border=True):
                            col_edit, col_del, col_info = st.columns([1, 1, 5])
                            
                            with col_info:
                                st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**默认值**：{var_cfg.get('default', '无')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                            
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_text_{var_key}", type="secondary"):
                                    st.session_state['editing_text_var'] = var_key
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ 删除", key=f"delete_{var_key}", type="secondary"):
                                    del placeholders_config["placeholders"]["text"][var_key]
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    st.success(f"✅ 已删除：[{var_key}]")
                                    st.rerun()
        else:
            st.info("暂无自定义文本变量")
    
    st.markdown("---")
    
    # ========== 区块 2: 日期变量 ==========
    st.markdown("### 📅 日期变量")
    st.markdown("*用于 PPT 中的日期占位符，例如报告日期、统计周期等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加日期变量")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date_var_key = st.text_input("变量 Key", placeholder="例如：report_date", help="用于 PPT 占位符：[DATE:xxx]", key="date_var_key")
            date_var_desc = st.text_input("变量描述", placeholder="例如：报告生成日期", key="date_var_desc")
            date_var_format = st.selectbox("日期格式", options=["%Y-%m-%d", "%Y/%m/%d", "%Y 年%m 月%d 日", "%Y.%m.%d", "%m/%d/%Y"], index=0, key="date_var_format")
        
        with col2:
            date_var_default = st.date_input("默认日期", value=datetime.now(), key="date_var_default_val")
            date_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="date_var_page")
        
        if st.button("➕ 添加日期变量", type="primary", key="add_date_var"):
            if not date_var_key:
                st.error("❌ 请填写变量 Key")
            else:
                full_key = f"DATE:{date_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "dates" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["dates"] = {}
                
                placeholders_config["placeholders"]["dates"][full_key] = {
                    "description": date_var_desc,
                    "default": date_var_default.strftime(date_var_format),
                    "format": date_var_format,
                    "slide_index": date_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加日期变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的日期变量")
        
        date_vars = placeholders_config.get('placeholders', {}).get('dates', {})
        
        if date_vars:
            editing_date_var = st.session_state.get('editing_date_var', None)
            
            for var_key, var_cfg in date_vars.items():
                if var_key.startswith('DATE:'):
                    if editing_date_var == var_key:
                        st.markdown(f"#### ✏️ 编辑：{var_key}")
                        
                        edit_key = st.text_input("变量 Key", value=var_key.replace('DATE:', ''), key=f"edit_date_key_{var_key}")
                        edit_desc = st.text_input("变量描述", value=var_cfg.get('description', ''), key=f"edit_date_desc_{var_key}")
                        edit_format = st.selectbox("日期格式", options=["%Y-%m-%d", "%Y/%m/%d", "%Y 年%m 月%d 日", "%Y.%m.%d", "%m/%d/%Y"], 
                                                  index=["%Y-%m-%d", "%Y/%m/%d", "%Y 年%m 月%d 日", "%Y.%m.%d", "%m/%d/%Y"].index(var_cfg.get('format', '%Y-%m-%d')), 
                                                  key=f"edit_date_format_{var_key}")
                        try:
                            edit_default = st.date_input("默认日期", value=datetime.strptime(var_cfg.get('default', datetime.now().strftime('%Y-%m-%d')), var_cfg.get('format', '%Y-%m-%d')), key=f"edit_date_default_{var_key}")
                        except:
                            edit_default = st.date_input("默认日期", value=datetime.now(), key=f"edit_date_default_{var_key}")
                        edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_date_page_{var_key}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存修改", type="primary", key=f"save_date_edit_{var_key}"):
                                new_key = f"DATE:{edit_key}"
                                if new_key != var_key and new_key in date_vars:
                                    st.error(f"❌ 变量 Key 已存在：{new_key}")
                                else:
                                    if new_key != var_key:
                                        del placeholders_config["placeholders"]["dates"][var_key]
                                    
                                    placeholders_config["placeholders"]["dates"][new_key] = {
                                        "description": edit_desc,
                                        "default": edit_default.strftime(edit_format),
                                        "format": edit_format,
                                        "slide_index": edit_page
                                    }
                                    
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    
                                    st.session_state['editing_date_var'] = None
                                    st.success(f"✅ 已保存修改")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 取消编辑", key=f"cancel_date_edit_{var_key}"):
                                st.session_state['editing_date_var'] = None
                                st.rerun()
                        
                        st.divider()
                    else:
                        with st.container(border=True):
                            col_edit, col_del, col_info = st.columns([1, 1, 5])
                            
                            with col_info:
                                st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**默认值**：{var_cfg.get('default', '无')}  \n**格式**：{var_cfg.get('format', '%Y-%m-%d')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                            
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_date_{var_key}", type="secondary"):
                                    st.session_state['editing_date_var'] = var_key
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ 删除", key=f"delete_{var_key}", type="secondary"):
                                    del placeholders_config["placeholders"]["dates"][var_key]
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    st.success(f"✅ 已删除：[{var_key}]")
                                    st.rerun()
        else:
            st.info("暂无日期变量")
    
    st.markdown("---")
    
    # ========== 区块 3: 图片变量 ==========
    st.markdown("### 🖼️ 图片变量")
    st.markdown("*用于 PPT 中的图片占位符，例如 Logo、产品图、封面图等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加图片变量")
        
        col1, col2 = st.columns(2)
        
        with col1:
            img_var_key = st.text_input("变量 Key", placeholder="例如：company_logo", help="用于 PPT 占位符：[IMAGE:xxx]", key="img_var_key")
            img_var_desc = st.text_input("变量描述", placeholder="例如：公司 Logo", key="img_var_desc")
            img_var_type = st.selectbox("图片类型", options=["logo", "cover", "product", "chart", "other"], index=0, key="img_var_type")
            img_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="img_var_page_num")
        
        with col2:
            img_upload_method = st.radio("图片来源", options=["上传文件", "输入路径"], index=0, key="img_upload_method")
            
            if img_upload_method == "上传文件":
                img_file = st.file_uploader("上传图片", type=["png", "jpg", "jpeg", "gif", "webp", "svg"], key="img_file_uploader")
                img_var_path = None
                if img_file:
                    save_path = os.path.join(images_dir, img_file.name)
                    with open(save_path, "wb") as f:
                        f.write(img_file.getbuffer())
                    img_var_path = os.path.join("resources", "images", img_file.name)
                    st.success(f"✅ 图片已上传：{img_file.name}")
            else:
                img_var_path = st.text_input("图片路径", placeholder="例如：images/logo.png 或 http://xxx.com/logo.png", key="img_var_path")
        
        if st.button("➕ 添加图片变量", type="primary", key="add_img_var"):
            if not img_var_key:
                st.error("❌ 请填写变量 Key")
            elif not img_var_path:
                st.error("❌ 请上传图片或输入图片路径")
            else:
                full_key = f"IMAGE:{img_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "images" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["images"] = {}
                
                placeholders_config["placeholders"]["images"][full_key] = {
                    "description": img_var_desc,
                    "path": img_var_path,
                    "type": img_var_type,
                    "slide_index": img_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加图片变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的图片变量")
        
        img_vars = placeholders_config.get('placeholders', {}).get('images', {})
        
        if img_vars:
            editing_img_var = st.session_state.get('editing_img_var', None)
            
            for var_key, var_cfg in img_vars.items():
                if var_key.startswith('IMAGE:'):
                    if editing_img_var == var_key:
                        st.markdown(f"#### ✏️ 编辑：{var_key}")
                        
                        edit_key = st.text_input("变量 Key", value=var_key.replace('IMAGE:', ''), key=f"edit_img_key_{var_key}")
                        edit_desc = st.text_input("变量描述", value=var_cfg.get('description', ''), key=f"edit_img_desc_{var_key}")
                        edit_type = st.selectbox("图片类型", options=["logo", "cover", "product", "chart", "other"], 
                                                index=["logo", "cover", "product", "chart", "other"].index(var_cfg.get('type', 'other')), 
                                                key=f"edit_img_type_{var_key}")
                        edit_path = st.text_input("图片路径", value=var_cfg.get('path', ''), key=f"edit_img_path_{var_key}")
                        edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_img_page_{var_key}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存修改", type="primary", key=f"save_img_edit_{var_key}"):
                                new_key = f"IMAGE:{edit_key}"
                                if new_key != var_key and new_key in img_vars:
                                    st.error(f"❌ 变量 Key 已存在：{new_key}")
                                else:
                                    if new_key != var_key:
                                        del placeholders_config["placeholders"]["images"][var_key]
                                    
                                    placeholders_config["placeholders"]["images"][new_key] = {
                                        "description": edit_desc,
                                        "path": edit_path,
                                        "type": edit_type,
                                        "slide_index": edit_page
                                    }
                                    
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    
                                    st.session_state['editing_img_var'] = None
                                    st.success(f"✅ 已保存修改")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 取消编辑", key=f"cancel_img_edit_{var_key}"):
                                st.session_state['editing_img_var'] = None
                                st.rerun()
                        
                        st.divider()
                    else:
                        with st.container(border=True):
                            col_edit, col_del, col_info = st.columns([1, 1, 5])
                            
                            with col_info:
                                st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**类型**：{var_cfg.get('type', 'other')}  \n**路径**：{var_cfg.get('path', '无')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                            
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_img_{var_key}", type="secondary"):
                                    st.session_state['editing_img_var'] = var_key
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ 删除", key=f"delete_{var_key}", type="secondary"):
                                    del placeholders_config["placeholders"]["images"][var_key]
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    st.success(f"✅ 已删除：[{var_key}]")
                                    st.rerun()
        else:
            st.info("暂无图片变量")
    
    st.markdown("---")
    
    # ========== 区块 4: 视频变量 ==========
    st.markdown("### 🎬 视频变量")
    st.markdown("*用于 PPT 中的视频占位符，例如产品介绍视频、宣传视频等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加视频变量")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_var_key = st.text_input("变量 Key", placeholder="例如：promo_video", help="用于 PPT 占位符：[VIDEO:xxx]", key="video_var_key")
            video_var_desc = st.text_input("变量描述", placeholder="例如：产品宣传视频", key="video_var_desc")
            video_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="video_var_page_num2")
        
        with col2:
            video_upload_method = st.radio("视频来源", options=["上传文件", "输入路径"], index=0, key="video_upload_method")
            
            if video_upload_method == "上传文件":
                video_file = st.file_uploader("上传视频", type=["mp4", "avi", "mov", "wmv", "flv", "webm"], key="video_file_uploader")
                video_var_path = None
                if video_file:
                    save_path = os.path.join(videos_dir, video_file.name)
                    with open(save_path, "wb") as f:
                        f.write(video_file.getbuffer())
                    video_var_path = os.path.join("resources", "videos", video_file.name)
                    st.success(f"✅ 视频已上传：{video_file.name}")
            else:
                video_var_path = st.text_input("视频路径", placeholder="例如：videos/promo.mp4 或 http://xxx.com/video.mp4", key="video_var_path")
        
        if st.button("➕ 添加视频变量", type="primary", key="add_video_var"):
            if not video_var_key:
                st.error("❌ 请填写变量 Key")
            elif not video_var_path:
                st.error("❌ 请上传视频或输入视频路径")
            else:
                full_key = f"VIDEO:{video_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "videos" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["videos"] = {}
                
                placeholders_config["placeholders"]["videos"][full_key] = {
                    "description": video_var_desc,
                    "path": video_var_path,
                    "slide_index": video_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加视频变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的视频变量")
        
        video_vars = placeholders_config.get('placeholders', {}).get('videos', {})
        
        if video_vars:
            editing_video_var = st.session_state.get('editing_video_var', None)
            
            for var_key, var_cfg in video_vars.items():
                if var_key.startswith('VIDEO:'):
                    if editing_video_var == var_key:
                        st.markdown(f"#### ✏️ 编辑：{var_key}")
                        
                        edit_key = st.text_input("变量 Key", value=var_key.replace('VIDEO:', ''), key=f"edit_video_key_{var_key}")
                        edit_desc = st.text_input("变量描述", value=var_cfg.get('description', ''), key=f"edit_video_desc_{var_key}")
                        edit_path = st.text_input("视频路径", value=var_cfg.get('path', ''), key=f"edit_video_path_{var_key}")
                        edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_video_page_{var_key}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存修改", type="primary", key=f"save_video_edit_{var_key}"):
                                new_key = f"VIDEO:{edit_key}"
                                if new_key != var_key and new_key in video_vars:
                                    st.error(f"❌ 变量 Key 已存在：{new_key}")
                                else:
                                    if new_key != var_key:
                                        del placeholders_config["placeholders"]["videos"][var_key]
                                    
                                    placeholders_config["placeholders"]["videos"][new_key] = {
                                        "description": edit_desc,
                                        "path": edit_path,
                                        "slide_index": edit_page
                                    }
                                    
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    
                                    st.session_state['editing_video_var'] = None
                                    st.success(f"✅ 已保存修改")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 取消编辑", key=f"cancel_video_edit_{var_key}"):
                                st.session_state['editing_video_var'] = None
                                st.rerun()
                        
                        st.divider()
                    else:
                        with st.container(border=True):
                            col_edit, col_del, col_info = st.columns([1, 1, 5])
                            
                            with col_info:
                                st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**路径**：{var_cfg.get('path', '无')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                            
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_video_{var_key}", type="secondary"):
                                    st.session_state['editing_video_var'] = var_key
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ 删除", key=f"delete_{var_key}", type="secondary"):
                                    del placeholders_config["placeholders"]["videos"][var_key]
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    st.success(f"✅ 已删除：[{var_key}]")
                                    st.rerun()
        else:
            st.info("暂无视频变量")
    
    st.markdown("---")
    
    # ========== 区块 5: 链接变量 ==========
    st.markdown("### 🔗 链接变量")
    st.markdown("*用于 PPT 中的超链接占位符，例如二维码跳转 URL、参考链接等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加链接变量")
        
        col1, col2 = st.columns(2)
        
        with col1:
            link_var_key = st.text_input("变量 Key", placeholder="例如：qr_code_url", help="用于 PPT 占位符：[LINK:xxx]", key="link_var_key")
            link_var_desc = st.text_input("变量描述", placeholder="例如：公众号二维码链接", key="link_var_desc")
            link_var_type = st.selectbox("链接类型", options=["url", "email", "tel", "file"], index=0, key="link_var_type")
        
        with col2:
            link_var_url = st.text_input("链接地址", placeholder="例如：https://wechat.qq.com/xxx 或 mailto:xxx@example.com", key="link_var_url")
            link_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="link_var_page_num3")
        
        if st.button("➕ 添加链接变量", type="primary", key="add_link_var"):
            if not link_var_key:
                st.error("❌ 请填写变量 Key")
            elif not link_var_url:
                st.error("❌ 请填写链接地址")
            else:
                full_key = f"LINK:{link_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "links" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["links"] = {}
                
                placeholders_config["placeholders"]["links"][full_key] = {
                    "description": link_var_desc,
                    "url": link_var_url,
                    "type": link_var_type,
                    "slide_index": link_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加链接变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的链接变量")
        
        link_vars = placeholders_config.get('placeholders', {}).get('links', {})
        
        if link_vars:
            editing_link_var = st.session_state.get('editing_link_var', None)
            
            for var_key, var_cfg in link_vars.items():
                if var_key.startswith('LINK:'):
                    if editing_link_var == var_key:
                        st.markdown(f"#### ✏️ 编辑：{var_key}")
                        
                        edit_key = st.text_input("变量 Key", value=var_key.replace('LINK:', ''), key=f"edit_link_key_{var_key}")
                        edit_desc = st.text_input("变量描述", value=var_cfg.get('description', ''), key=f"edit_link_desc_{var_key}")
                        edit_type = st.selectbox("链接类型", options=["url", "email", "tel", "file"], 
                                                index=["url", "email", "tel", "file"].index(var_cfg.get('type', 'url')), 
                                                key=f"edit_link_type_{var_key}")
                        edit_url = st.text_input("链接地址", value=var_cfg.get('url', ''), key=f"edit_link_url_{var_key}")
                        edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_link_page_{var_key}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("💾 保存修改", type="primary", key=f"save_link_edit_{var_key}"):
                                new_key = f"LINK:{edit_key}"
                                if new_key != var_key and new_key in link_vars:
                                    st.error(f"❌ 变量 Key 已存在：{new_key}")
                                else:
                                    if new_key != var_key:
                                        del placeholders_config["placeholders"]["links"][var_key]
                                    
                                    placeholders_config["placeholders"]["links"][new_key] = {
                                        "description": edit_desc,
                                        "url": edit_url,
                                        "type": edit_type,
                                        "slide_index": edit_page
                                    }
                                    
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    
                                    st.session_state['editing_link_var'] = None
                                    st.success(f"✅ 已保存修改")
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("❌ 取消编辑", key=f"cancel_link_edit_{var_key}"):
                                st.session_state['editing_link_var'] = None
                                st.rerun()
                        
                        st.divider()
                    else:
                        with st.container(border=True):
                            col_edit, col_del, col_info = st.columns([1, 1, 5])
                            
                            with col_info:
                                st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**类型**：{var_cfg.get('type', 'url')}  \n**链接**：{var_cfg.get('url', '无')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                            
                            with col_edit:
                                if st.button("✏️ 编辑", key=f"edit_link_{var_key}", type="secondary"):
                                    st.session_state['editing_link_var'] = var_key
                                    st.rerun()
                            
                            with col_del:
                                if st.button("🗑️ 删除", key=f"delete_{var_key}", type="secondary"):
                                    del placeholders_config["placeholders"]["links"][var_key]
                                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                    st.success(f"✅ 已删除：[{var_key}]")
                                    st.rerun()
        else:
            st.info("暂无链接变量")
    
    st.markdown("---")
    
    # ========== 区块 6: 表格变量 ==========
    st.markdown("### 📋 表格变量")
    st.markdown("*用于 PPT 中的数据表格占位符，例如 KPI 汇总表、排名表等*")
    
    with st.container(border=True):
        st.subheader("➕ 添加表格变量")
        
        col3, col4 = st.columns(2)
        
        with col3:
            table_var_key = st.text_input("表格变量 Key", placeholder="例如：kpi_summary", help="用于 PPT 占位符：[TABLE:xxx]", key="table_var_key2")
            table_var_desc = st.text_input("表格描述", placeholder="例如：核心 KPI 汇总表", key="table_var_desc2")
            table_var_source = st.text_input("数据源", placeholder="Excel Sheet 名称，例如：核心 KPI", key="table_var_source2")
        
        with col4:
            table_var_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=0, key="table_var_page_num4")
            
            st.markdown("""
            **💡 使用示例**：
            ```
            [TABLE:kpi_summary]
            ```
            运行 `Run.bat` 时会自动从指定的 Excel Sheet 读取数据并填充到 PPT 表格中
            """)
        
        if st.button("➕ 添加表格变量", type="primary", key="add_table_var2"):
            if not table_var_key:
                st.error("❌ 请填写表格变量 Key")
            else:
                full_key = f"TABLE:{table_var_key}"
                if "placeholders" not in placeholders_config:
                    placeholders_config["placeholders"] = {}
                if "tables" not in placeholders_config["placeholders"]:
                    placeholders_config["placeholders"]["tables"] = {}
                
                placeholders_config["placeholders"]["tables"][full_key] = {
                    "description": table_var_desc, 
                    "data_source": table_var_source, 
                    "slide_index": table_var_page
                }
                
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加自定义表格变量：[{full_key}]")
                st.rerun()
        
        st.divider()
        
        st.subheader("📋 已配置的表格变量")
        
        table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
        
        if table_vars:
            editing_table_var = st.session_state.get('editing_table_var', None)
            
            for var_key, var_cfg in table_vars.items():
                if editing_table_var == var_key:
                    st.markdown(f"#### ✏️ 编辑：{var_key}")
                    
                    edit_key = st.text_input("表格变量 Key", value=var_key.replace('TABLE:', ''), key=f"edit_table_key_{var_key}")
                    edit_desc = st.text_input("表格描述", value=var_cfg.get('description', ''), key=f"edit_table_desc_{var_key}")
                    edit_source = st.text_input("数据源", value=var_cfg.get('data_source', ''), key=f"edit_table_source_{var_key}")
                    edit_page = st.number_input("PPT 页码", min_value=0, max_value=20, value=var_cfg.get('slide_index', 0), key=f"edit_table_page_{var_key}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 保存修改", type="primary", key=f"save_table_edit_{var_key}"):
                            new_key = f"TABLE:{edit_key}"
                            if new_key != var_key and new_key in table_vars:
                                st.error(f"❌ 表格变量 Key 已存在：{new_key}")
                            else:
                                if new_key != var_key:
                                    del placeholders_config["placeholders"]["tables"][var_key]
                                
                                placeholders_config["placeholders"]["tables"][new_key] = {
                                    "description": edit_desc,
                                    "data_source": edit_source,
                                    "slide_index": edit_page
                                }
                                
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                
                                st.session_state['editing_table_var'] = None
                                st.success(f"✅ 已保存修改")
                                st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ 取消编辑", key=f"cancel_table_edit_{var_key}"):
                            st.session_state['editing_table_var'] = None
                            st.rerun()
                    
                    st.divider()
                else:
                    with st.container(border=True):
                        col_edit, col_del, col_info = st.columns([1, 1, 5])
                        
                        with col_info:
                            st.markdown(f"**占位符**：`[{var_key}]`  \n**描述**：{var_cfg.get('description', '无')}  \n**数据源**：{var_cfg.get('data_source', '无')}  \n**PPT 页码**：{var_cfg.get('slide_index', '未设置')}")
                        
                        with col_edit:
                            if st.button("✏️ 编辑", key=f"edit_table_{var_key}", type="secondary"):
                                st.session_state['editing_table_var'] = var_key
                                st.rerun()
                        
                        with col_del:
                            if st.button("🗑️ 删除", key=f"delete_table_{var_key}", type="secondary"):
                                del placeholders_config["placeholders"]["tables"][var_key]
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                                st.success(f"✅ 已删除：[{var_key}]")
                                st.rerun()
        else:
            st.info("暂无自定义表格变量")
    
    st.markdown("---")
    st.info("""
    💡 **使用提示**：
    - **文本变量** `[TEXT:xxx]` - 报告标题、公司名称、作者等文本内容
    - **日期变量** `[DATE:xxx]` - 报告日期、统计周期等，支持多种格式
    - **图片变量** `[IMAGE:xxx]` - Logo、产品图、封面图等，支持上传或输入路径
    - **视频变量** `[VIDEO:xxx]` - 产品介绍视频、宣传视频等，支持上传或输入路径
    - **链接变量** `[LINK:xxx]` - 超链接、二维码跳转 URL、邮箱、电话等
    - **表格变量** `[TABLE:xxx]` - 从 Excel Sheet 自动填充数据表格
    - 所有变量可在「🔖 PPT 变量」页签统一查看
    - 上传的图片/视频文件保存在 `resources/` 目录下
    - ✨ **点击"✏️ 编辑"按钮可修改变量配置**
    """)
