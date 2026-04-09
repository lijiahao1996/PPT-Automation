# -*- coding: utf-8 -*-
"""Tab 5: 结论 & 策略配置（支持动态增删变量）"""
import streamlit as st
import json
import os

def render_tab5(templates_dir):
    st.header("🎯 结论 & 策略配置")
    st.markdown("自定义 AI 生成的变量，可自由新增、编辑、删除")
    
    placeholders_file = os.path.join(templates_dir, "placeholders.json")
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {"placeholders": {}}
    
    # 初始化 special_insights 为列表结构，支持多个变量
    if "special_insights" not in placeholders_config:
        placeholders_config["special_insights"] = {
            "variables": [
                {
                    "key": "conclusion",
                    "name": "核心结论",
                    "description": "AI 自动生成 4 条核心结论",
                    "dimensions": ["业绩结构", "增长亮点", "核心短板", "业务风险"],
                    "style": "数据驱动",
                    "word_count": 300,
                    "custom_prompt": "请从以下 4 个维度生成核心结论：\n1. 业绩结构：分析销售、产品、客户、区域的集中度风险\n2. 增长亮点：识别增长最快的指标和驱动因素\n3. 核心短板：指出最明显的业务弱点和瓶颈\n4. 业务风险：预警潜在的结构性风险和外部威胁"
                },
                {
                    "key": "strategy",
                    "name": "落地策略",
                    "description": "AI 自动生成 4 条落地策略",
                    "dimensions": ["客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略"],
                    "style": "建议导向",
                    "word_count": 400,
                    "custom_prompt": "请从以下 4 个维度生成落地策略：\n1. 客户运营策略：新老客分层运营、复购提升、LTV 优化\n2. 产品组合策略：爆品依赖降低、连带率提升、产品矩阵优化\n3. 团队管理策略：销售产能规划、激励机制、培训体系\n4. 营销节奏策略：活动节奏、渠道投放、促销时机"
                }
            ]
        }
    
    special_insights = placeholders_config["special_insights"]
    
    if "variables" not in special_insights:
        special_insights["variables"] = []
    
    variables = special_insights["variables"]
    
    # ========== 上方：添加新变量 ==========
    st.subheader("➕ 添加新变量")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_var_key = st.text_input("变量 Key", placeholder="例如：conclusion", help="用于 PPT 占位符：{{INSIGHT:xxx}}")
        new_var_name = st.text_input("变量名称", placeholder="例如：核心结论")
        new_var_desc = st.text_area("变量说明", placeholder="例如：AI 自动生成 4 条核心结论", height=60)
    
    with col2:
        new_var_style = st.selectbox("洞察风格", options=["数据驱动", "问题导向", "建议导向", "平衡型"], index=3)
        new_var_words = st.slider("字数要求", min_value=0, max_value=500, value=300, step=10)
    
    new_var_dimensions = st.multiselect(
        "分析维度",
        options=["业绩结构", "增长亮点", "核心短板", "业务风险", "趋势分析", "对比分析", "占比分析", "异常检测",
                 "客户运营策略", "产品组合策略", "团队管理策略", "营销节奏策略", "渠道拓展", "数字化转型", "供应链优化", "风控体系"],
        default=["业绩结构", "增长亮点", "核心短板", "业务风险"]
    )
    
    new_var_prompt = st.text_area("自定义生成提示词", placeholder="请输入详细的生成提示词，包括分析维度、格式要求等", height=150)
    
    if st.button("➕ 添加变量", type="primary"):
        if not new_var_key:
            st.error("❌ 请填写变量 Key")
        else:
            new_var = {
                "key": new_var_key,
                "name": new_var_name or new_var_key,
                "description": new_var_desc,
                "dimensions": new_var_dimensions,
                "style": new_var_style,
                "word_count": new_var_words,
                "custom_prompt": new_var_prompt
            }
            
            # 检查是否已存在
            existing_keys = [v.get('key') for v in variables]
            if new_var_key in existing_keys:
                st.warning(f"⚠️ 变量 Key 已存在：{new_var_key}")
            else:
                variables.append(new_var)
                # 自动保存到文件
                with open(placeholders_file, 'w', encoding='utf-8') as f:
                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                st.success(f"✅ 已添加变量：{{{{INSIGHT:{new_var_key}}}}}（已自动保存）")
                st.rerun()
    
    st.markdown("---")
    
    # ========== 下方：现有变量列表 ==========
    st.subheader("📋 现有变量")
    
    if variables:
        for i, var in enumerate(variables):
            with st.expander(f"🔖 {var.get('name', var.get('key', f'变量{i}'))} (占位符：{{{{INSIGHT:{var.get('key', '')}}}}})"):
                st.json(var)
                if st.button(f"🗑️ 删除", key=f"delete_var_{i}"):
                    variables.pop(i)
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"✅ 已删除变量")
                    st.rerun()
    else:
        st.info("暂无变量，请添加")
    
    st.markdown("---")
    st.info("""💡 **提示**：
- 添加的变量可在 PPT 模板中使用 `{{INSIGHT:变量 Key}}` 占位符
- 变量会在 AI 洞察生成时自动使用
- 运行 `Run.bat` 时会自动替换为实际内容""")
