# -*- coding: utf-8 -*-
"""Tab 3: 洞察配置（支持折叠）"""
import streamlit as st
import json
import os

def render_tab3(artifacts_dir):
    st.header("💡 洞察配置")
    st.markdown("为每个图表配置 AI 洞察分析要点")
    
    placeholders_file = os.path.join(artifacts_dir, "placeholders.json")
    
    # 确保目录存在
    os.makedirs(artifacts_dir, exist_ok=True)
    
    # 加载配置（文件不存在时创建默认）
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {"placeholders": {}}
        # 创建默认配置文件
        with open(placeholders_file, 'w', encoding='utf-8') as f:
            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
    
    charts_config = placeholders_config.get("placeholders", {}).get("charts", {})
    
    if not charts_config:
        st.warning("⚠️ 请先在'图表配置'标签页添加图表")
        st.stop()
    
    existing_insights = placeholders_config.get("placeholders", {}).get("insights", {})
    st.info(f"📊 当前图表数量：{len(charts_config)} | 已配置洞察：{len(existing_insights)}")
    
    st.subheader("配置洞察分析要点")
    st.markdown("*点击图表名称展开配置*")
    
    insights_config = {}
    
    for i, (chart_key, chart_cfg) in enumerate(charts_config.items(), 1):
        existing = existing_insights.get(chart_key, {})
        default_dimensions = existing.get("dimensions", ["趋势分析", "对比分析"])
        default_metrics = existing.get("metrics", ["总销售额", "订单数", "客单价"])
        default_baseline = existing.get("baseline", "环比")
        default_style = existing.get("style", "平衡型")
        default_word_count = existing.get("word_count", 150)
        default_enabled = existing.get("enabled", True)
        default_prompt = existing.get("custom_prompt", "")
        
        # 使用折叠容器
        with st.expander(f"📊 {i}. {chart_cfg.get('title', chart_key)}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                analysis_dimensions = st.multiselect(
                    "分析维度",
                    options=["趋势分析", "对比分析", "占比分析", "排名分析", "异常检测", "相关性分析", "分布分析"],
                    default=default_dimensions, key=f"dim_{chart_key}")
                
                key_metrics = st.text_area("关键指标（每行一个）", placeholder="总销售额\n订单数\n客单价",
                                           value='\n'.join(default_metrics), key=f"metrics_{chart_key}")
                
                baseline_options = ["环比", "同比", "目标值", "平均值", "头部对比", "尾部对比", "无对比"]
                baseline = st.selectbox("对比基准", options=baseline_options,
                                        index=baseline_options.index(default_baseline) if default_baseline in baseline_options else 0,
                                        key=f"baseline_{chart_key}")
            
            with col2:
                style_options = ["数据驱动", "问题导向", "建议导向", "平衡型"]
                insight_style = st.selectbox("洞察风格", options=style_options,
                                             index=style_options.index(default_style) if default_style in style_options else 3,
                                             key=f"style_{chart_key}")
                
                word_count = st.slider("字数要求", min_value=0, max_value=300, value=default_word_count, step=10, key=f"words_{chart_key}")
                enabled = st.checkbox("启用", value=default_enabled, key=f"enabled_{chart_key}")
            
            custom_prompt = st.text_area("自定义提示词（可选）", placeholder="例如：重点分析头部销售员的业绩贡献度...",
                                         value=default_prompt, height=80, key=f"prompt_{chart_key}")
            
            insights_config[chart_key] = {
                "dimensions": analysis_dimensions,
                "metrics": [m.strip() for m in key_metrics.split('\n') if m.strip()],
                "baseline": baseline, "style": insight_style, "word_count": word_count,
                "enabled": enabled, "custom_prompt": custom_prompt
            }
    
    # 自动保存洞察配置
    placeholders_config["placeholders"]["insights"] = insights_config
    with open(placeholders_file, 'w', encoding='utf-8') as f:
        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
    
    st.markdown("---")
    st.subheader("📋 洞察配置预览")
    if insights_config:
        for chart_key, insight_cfg in insights_config.items():
            with st.expander(f"💡 {chart_key}"):
                st.json(insight_cfg)
