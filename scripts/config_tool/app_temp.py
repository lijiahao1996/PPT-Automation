# -*- coding: utf-8 -*-
"""
PPT 閰嶇疆宸ュ叿 - Streamlit 搴旂敤
鍥惧舰鍖栭厤缃?stats_rules.json 鍜?placeholders.json
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
from pathlib import Path

# 椤甸潰閰嶇疆
st.set_page_config(
    page_title="PPT 鎶ュ憡閰嶇疆宸ュ叿",
    page_icon="馃搳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 鑷畾涔?CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1F4E79;
    text-align: center;
    padding: 1rem 0;
}
.config-section {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
</style>
""", unsafe_allow_html=True)

# 鏍囬
st.markdown('<h1 class="main-header">馃搳 PPT 鎶ュ憡閰嶇疆宸ュ叿</h1>', unsafe_allow_html=True)
st.markdown("---")

# 渚ц竟鏍?- 椤圭洰璺緞閰嶇疆
with st.sidebar:
    st.header("鈿欙笍 椤圭洰璁剧疆")
    
    # 榛樿椤圭洰鏍圭洰褰?
    default_base_dir = r"C:\Users\50319\Desktop\n8n"
    base_dir = st.text_input("椤圭洰鏍圭洰褰?, value=default_base_dir)
    
    # 楠岃瘉璺緞
    if not os.path.exists(base_dir):
        st.error("鉂?鐩綍涓嶅瓨鍦紒")
        st.stop()
    
    templates_dir = os.path.join(base_dir, "templates")
    output_dir = os.path.join(base_dir, "output")
    
    st.success(f"鉁?椤圭洰璺緞锛歿base_dir}")
    
    st.markdown("---")
    st.info("馃挕 **鎻愮ず**:\n1. 鍏堥厤缃粺璁¤鍒橽n2. 鐢熸垚娴嬭瘯鏁版嵁\n3. 閰嶇疆鍥捐〃\n4. 瀵煎嚭閰嶇疆")

# 涓诲姛鑳介€夋嫨
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["馃搵 缁熻瑙勫垯閰嶇疆", "馃搱 鍥捐〃閰嶇疆", "馃挕 娲炲療閰嶇疆", "鈿欙笍 鑷畾涔夊彉閲?, "馃幆 缁撹 & 绛栫暐", "馃搳 鏁版嵁姒傝", "馃敄 PPT 鍙橀噺"])

# ========== Tab 1: 缁熻瑙勫垯閰嶇疆 ==========
with tab1:
    st.header("馃搵 缁熻瑙勫垯閰嶇疆")
    st.markdown("閰嶇疆瑕佺敓鎴愬摢浜涚粺璁¤〃鏍硷紙Excel Sheet锛?)
    
    # 鍔犺浇鐜版湁閰嶇疆鍒?session_state
    stats_rules_file = os.path.join(templates_dir, "stats_rules.json")
    
    # 鍒濆鍖?session_state
    if 'stats_config' not in st.session_state:
        if os.path.exists(stats_rules_file):
            with open(stats_rules_file, 'r', encoding='utf-8') as f:
                st.session_state.stats_config = json.load(f)
            st.success("鉁?宸插姞杞界幇鏈夐厤缃?)
        else:
            st.session_state.stats_config = {
                "version": "1.0",
                "stats_sheets": {},
                "global_settings": {
                    "date_range_auto_detect": True
                }
            }
            st.info("馃摑 鍒涘缓鏂伴厤缃?)
    
    stats_config = st.session_state.stats_config
    
    # 缁熻绫诲瀷閫夋嫨
    stats_types = {
        "kpi": "馃搳 鏍稿績 KPI - 姹囨€绘寚鏍?,
        "ranking": "馃弳 鎺掑悕缁熻 - 閿€鍞憳/鍩庡競鎺掑悕",
        "composition": "馃ェ 鍗犳瘮鍒嗘瀽 - 浜у搧鍗犳瘮",
        "comparison": "鈿栵笍 瀵规瘮鍒嗘瀽 - 鏂拌€佸瀵规瘮",
        "trend": "馃搱 瓒嬪娍鍒嗘瀽 - 鏈堝害瓒嬪娍",
        "distribution": "馃搳 鍒嗗竷鍒嗘瀽 - 鏄熸湡鍒嗗竷",
        "matrix": "馃敳 鐭╅樀鍒嗘瀽 - 閿€鍞憳 - 浜у搧",
        "outlier": "鈿狅笍 寮傚父妫€娴?- 寮傚父璁㈠崟"
    }
    
    st.subheader("娣诲姞缁熻瑙勫垯")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sheet_name = st.text_input("缁熻琛ㄦ牸鍚嶇О", placeholder="渚嬪锛氶攢鍞憳涓氱哗")
        stat_type = st.selectbox("缁熻绫诲瀷", options=list(stats_types.keys()), format_func=lambda x: stats_types[x])
        enabled = st.checkbox("鍚敤", value=True)
        description = st.text_area("鎻忚堪", placeholder="渚嬪锛氶攢鍞憳涓氱哗鎺掑悕")
    
    with col2:
        st.markdown("### 鍒嗙粍瀛楁")
        group_fields = st.text_area("鍒嗙粍瀛楁\n锛堟瘡琛屼竴涓級", placeholder="閿€鍞憳\n鍩庡競", height=100)
        
        st.markdown("### 缁熻鎸囨爣")
        metrics_config = st.text_area("缁熻鎸囨爣閰嶇疆\n锛圝SON 鏍煎紡锛?, 
                                     value='[{"field": "閿€鍞", "agg": "sum", "alias": "鎬婚攢鍞"}]',
                                     height=150)
    
    # 棰勮閰嶇疆
    if st.button("鉃?娣诲姞缁熻瑙勫垯"):
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
                
                # 鑷姩淇濆瓨鍒版枃浠?
                try:
                    with open(stats_rules_file, 'w', encoding='utf-8') as f:
                        json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                    st.success(f"鉁?宸叉坊鍔犵粺璁¤鍒欙細{sheet_name} 锛堝凡鑷姩淇濆瓨锛?)
                except Exception as e:
                    st.error(f"鉂?淇濆瓨澶辫触锛歿e}")
                    st.success(f"鉁?宸叉坊鍔犵粺璁¤鍒欙細{sheet_name}")
                
                st.rerun()  # 鍒锋柊椤甸潰鏄剧ず鏇存柊
            else:
                st.warning(f"鈿狅笍 缁熻瑙勫垯宸插瓨鍦細{sheet_name}")
        except json.JSONDecodeError as e:
            st.error(f"鉂?鎸囨爣閰嶇疆鏍煎紡閿欒锛歿e}")
    
    # 鎿嶄綔鎸夐挳鍖哄煙
    st.markdown("---")
    st.subheader("馃捑 鎿嶄綔")
    
    if st.button("馃攧 淇濆瓨閰嶇疆骞剁敓鎴愭暟鎹?, type="primary", use_container_width=True, help="淇濆瓨閰嶇疆鍚庣珛鍗虫墽琛岀粺璁″紩鎿庯紝鐢熸垚 Excel Sheet"):
            try:
                # 1. 淇濆瓨閰嶇疆
                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.stats_config, f, ensure_ascii=False, indent=2)
                st.info("馃摑 閰嶇疆宸蹭繚瀛?)
                
                # 2. 鎵ц缁熻寮曟搸鐢熸垚鏁版嵁
                with st.spinner("鈿欙笍 姝ｅ湪鎵ц缁熻寮曟搸锛岀敓鎴?Excel Sheet..."):
                    # 瀵煎叆缁熻寮曟搸
                    sys.path.insert(0, os.path.join(base_dir, 'scripts'))
                    from core.stats_engine import StatsEngine
                    from core.data_loader import DataLoader
                    
                    # 鍔犺浇鍘熷鏁版嵁
                    data_loader = DataLoader(base_dir)
                    raw_df = data_loader.load_raw_data('甯嗚蒋閿€鍞槑缁?xlsx')
                    
                    # 鎵ц缁熻寮曟搸
                    stats_engine = StatsEngine(base_dir=base_dir)
                    output_path = os.path.join(output_dir, '閿€鍞粺璁℃眹鎬?xlsx')
                    results = stats_engine.run_all(raw_df, output_path=output_path)
                    
                    st.success(f"鉁?宸茬敓鎴?{len(results)} 涓粺璁?Sheet锛?)
                    
                    # 鏄剧ず鐢熸垚鐨?Sheet 鍒楄〃
                    with st.expander("馃搳 鏌ョ湅鐢熸垚鐨?Sheet", expanded=True):
                        for sheet_name, df in results.items():
                            st.write(f"**{sheet_name}**: {len(df)} 琛?)
                
                st.success("馃帀 閰嶇疆淇濆瓨骞舵暟鎹敓鎴愬畬鎴愶紒鐜板湪鍙互鍘汇€岎煋?鍥捐〃閰嶇疆銆嶉〉绛鹃厤缃浘琛ㄤ簡")
                
            except FileNotFoundError as e:
                st.error(f"鉂?鏁版嵁鏂囦欢涓嶅瓨鍦細{e}\n\n馃挕 璇峰厛纭繚 output 鐩綍涓湁 `甯嗚蒋閿€鍞槑缁?xlsx` 鏂囦欢")
            except Exception as e:
                st.error(f"鉂?鎵ц澶辫触锛歿e}")
                import traceback
                with st.expander("馃搫 鏌ョ湅璇︾粏閿欒"):
                    st.code(traceback.format_exc())
    
    # 鏄剧ず鐜版湁瑙勫垯
    st.markdown("---")
    st.subheader("馃搵 鐜版湁缁熻瑙勫垯")
    
    # 妫€鏌ユ槸鍚︽湁姝ｅ湪缂栬緫鐨勯厤缃?
    edit_rule_name = st.session_state.get('editing_rule_name', None)
    
    if stats_config["stats_sheets"]:
        for name, rule in stats_config["stats_sheets"].items():
            # 濡傛灉鏄鍦ㄧ紪杈戠殑閰嶇疆锛屾樉绀虹紪杈戣〃鍗?
            if edit_rule_name == name:
                st.markdown(f"#### 鉁忥笍 缂栬緫锛歿name}")
                
                edit_sheet_name = st.text_input("缁熻琛ㄦ牸鍚嶇О", value=name, key=f"edit_sheet_input_{name}")
                edit_type = st.selectbox("缁熻绫诲瀷", options=list(stats_types.keys()),
                                        format_func=lambda x: stats_types[x],
                                        index=list(stats_types.keys()).index(rule.get('type', 'kpi')) if rule.get('type') in stats_types.keys() else 0,
                                        key=f"edit_type_{name}")
                edit_enabled = st.checkbox("鍚敤", value=rule.get('enabled', True), key=f"edit_enabled_{name}")
                edit_description = st.text_area("鎻忚堪", value=rule.get('description', ''), key=f"edit_desc_{name}")
                edit_groups = st.text_area("鍒嗙粍瀛楁锛堟瘡琛屼竴涓級", value='\n'.join(rule.get('group_by', [])), key=f"edit_groups_{name}")
                edit_metrics = st.text_area("缁熻鎸囨爣閰嶇疆锛圝SON 鏍煎紡锛?, 
                                           value=json.dumps(rule.get('metrics', []), ensure_ascii=False, indent=2),
                                           key=f"edit_metrics_{name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("馃捑 淇濆瓨淇敼", type="primary", key=f"edit_save_{name}"):
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
                            
                            # 濡傛灉鍚嶇О鏀瑰彉浜嗭紝鍏堝垹闄ゆ棫鐨?
                            if edit_sheet_name != name:
                                del stats_config["stats_sheets"][name]
                            
                            stats_config["stats_sheets"][edit_sheet_name] = new_rule
                            
                            # 鑷姩淇濆瓨
                            with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            
                            st.session_state['editing_rule_name'] = None
                            st.success("鉁?宸蹭繚瀛樺苟鑷姩淇濆瓨鏂囦欢")
                            st.rerun()
                        except json.JSONDecodeError as e:
                            st.error(f"鉂?鎸囨爣閰嶇疆鏍煎紡閿欒锛歿e}")
                
                with col2:
                    if st.button("鉂?鍙栨秷缂栬緫", key=f"edit_cancel_{name}"):
                        st.session_state['editing_rule_name'] = None
                        st.rerun()
                
                st.markdown("---")
            else:
                # 鏄剧ず閰嶇疆鍗＄墖
                with st.expander(f"{'鉁? if rule.get('enabled', True) else '鉂?} {name} - {rule.get('description', '')}"):
                    st.json(rule)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"鉁忥笍 缂栬緫", key=f"edit_btn_{name}"):
                            st.session_state['editing_rule_name'] = name
                            st.rerun()
                    with col2:
                        if st.button(f"馃棏锔?鍒犻櫎", key=f"delete_{name}"):
                            del stats_config["stats_sheets"][name]
                            # 鑷姩淇濆瓨
                            try:
                                with open(stats_rules_file, 'w', encoding='utf-8') as f:
                                    json.dump(stats_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"淇濆瓨澶辫触锛歿e}")
                            st.rerun()
    else:
        st.info("鏆傛棤缁熻瑙勫垯锛岃娣诲姞")
    
    # ========== 闆嗘垚鏁版嵁姒傝 ==========
    st.markdown("---")
    st.subheader("馃搳 鏁版嵁姒傝锛堥泦鎴愶級")
    st.caption("蹇€熸煡鐪嬬粺璁℃眹鎬绘枃浠讹紝鏃犻渶鍒囨崲椤电")
    
    summary_file = os.path.join(output_dir, "閿€鍞粺璁℃眹鎬?xlsx")
    
    if os.path.exists(summary_file):
        st.success("鉁?鎵惧埌缁熻姹囨€绘枃浠?)
        
        try:
            xls = pd.ExcelFile(summary_file)
            sheet_names = xls.sheet_names
            
            selected_sheet = st.selectbox("閫夋嫨 Sheet 棰勮", sheet_names, key="data_preview_sheet")
            
            if selected_sheet:
                df = pd.read_excel(summary_file, sheet_name=selected_sheet)
                st.dataframe(df, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("琛屾暟", len(df))
                with col2:
                    st.metric("鍒楁暟", len(df.columns))
                with col3:
                    st.metric("瀛楁", ", ".join(df.columns[:5]) + ("..." if len(df.columns) > 5 else ""))
        except Exception as e:
            st.warning(f"鈿狅笍 棰勮澶辫触锛歿e}")
    else:
        st.warning("鈿狅笍 鏈壘鍒扮粺璁℃眹鎬绘枃浠讹紝璇峰厛杩愯 Run.bat 鐢熸垚鏁版嵁")

# ========== Tab 2: 鍥捐〃閰嶇疆 ==========
with tab2:
    st.header("馃搱 鍥捐〃閰嶇疆")
    st.markdown("閰嶇疆 PPT 涓樉绀虹殑鍥捐〃")
    
    # 鍔犺浇鐜版湁閰嶇疆
    placeholders_file = os.path.join(templates_dir, "placeholders.json")
    
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
        st.success("鉁?宸插姞杞界幇鏈夐厤缃?)
    else:
        placeholders_config = {
            "version": "3.0",
            "placeholders": {
                "charts": {},
                "insights": {},
                "text": {}
            }
        }
        st.info("馃摑 鍒涘缓鏂伴厤缃?)
    
    # 鍥捐〃绫诲瀷
    chart_types = {
        "bar_horizontal": "馃搳 妯悜鏉″舰鍥?,
        "bar_vertical": "馃搳 绾靛悜鏌辩姸鍥?,
        "pie": "馃ェ 鐜舰楗煎浘",
        "column_clustered": "馃搳 澶氬垪鏌辩姸鍥?,
        "line": "馃搱 鎶樼嚎鍥?,
        "heatmap": "馃敟 鐑姏鍥?,
        "scatter": "鈿?鏁ｇ偣鍥?,
        "area": "馃搳 闈㈢Н鍥?,
        "histogram": "馃搳 鐩存柟鍥?,
        "boxplot": "馃摝 绠辩嚎鍥?,
        "bubble": "馃巿 姘旀场鍥?,
        "errorbar": "馃搹 璇樊妫掑浘",
        "polar": "馃幆 鏋佸潗鏍囧浘",
        "violin": "馃幓 灏忔彁鐞村浘",
        "waterfall": "馃挧 鐎戝竷鍥?,
        "funnel": "馃寑 婕忔枟鍥?
    }
    
    # 鑾峰彇鍙敤鐨勬暟鎹簮锛圗xcel Sheet 鍒楄〃锛?
    available_sheets = []
    summary_path = os.path.join(output_dir, '閿€鍞粺璁℃眹鎬?xlsx')
    if os.path.exists(summary_path):
        try:
            with pd.ExcelFile(summary_path) as xls:
                available_sheets = xls.sheet_names
        except Exception as e:
            st.warning(f"鈿狅笍 璇诲彇缁熻姹囨€诲け璐ワ細{e}")
    
    st.subheader("娣诲姞鍥捐〃閰嶇疆")
    
    # 鎻愮ず鐢ㄦ埛濡傛灉娌℃湁鏁版嵁婧愶紝鍏堝幓鐢熸垚
    if not available_sheets:
        st.warning("鈿狅笍 鏈壘鍒扮粺璁℃眹鎬绘枃浠讹紝璇峰厛鍦ㄣ€岎煋?缁熻瑙勫垯閰嶇疆銆嶉〉绛剧偣鍑汇€岎煍?淇濆瓨閰嶇疆骞剁敓鎴愭暟鎹€?)
    
    col1, col2 = st.columns(2)
    
    with col1:
        chart_key = st.text_input("鍥捐〃 Key", placeholder="渚嬪锛歴ales_by_person", help="鐢ㄤ簬 PPT 鍗犱綅绗︼細[CHART:xxx]")
        chart_title = st.text_input("鍥捐〃鏍囬", placeholder="渚嬪锛氶攢鍞憳涓氱哗琛ㄧ幇鍒嗘瀽")
        chart_type = st.selectbox("鍥捐〃绫诲瀷", options=list(chart_types.keys()), format_func=lambda x: chart_types[x])
        
        # 鏁版嵁婧愭敼涓轰笅鎷夐€夋嫨
        if available_sheets:
            data_source = st.selectbox(
                "鏁版嵁婧?,
                options=available_sheets,
                help="閫夋嫨瑕佷娇鐢ㄧ殑 Excel Sheet锛堟潵鑷粺璁℃眹鎬绘枃浠讹級"
            )
            
            # 鏁版嵁婧愰瑙?- 閫変腑鍚庣洿鎺ユ樉绀哄墠 5 琛?
            if data_source:
                try:
                    df_preview = pd.read_excel(summary_path, sheet_name=data_source, nrows=5)
                    with st.expander(f"馃搳 棰勮鏁版嵁婧?'{data_source}' (鍓?5 琛?", expanded=False):
                        st.dataframe(df_preview, use_container_width=True)
                        st.caption(f"鍏?{len(pd.read_excel(summary_path, sheet_name=data_source))} 琛?脳 {len(df_preview.columns)} 鍒?)
                except Exception as e:
                    st.warning(f"鈿狅笍 棰勮澶辫触锛歿e}")
        else:
            data_source = st.text_input("鏁版嵁婧?, placeholder="璇峰厛鍘荤敓鎴愭暟鎹?, help="蹇呴』涓庣粺璁¤鍒欎腑鐨勫悕绉颁竴鑷?, disabled=True)
    
    with col2:
        st.markdown("### 瀛楁閰嶇疆")
        
        # 濡傛灉閫夋嫨浜嗘暟鎹簮锛屽皾璇曡嚜鍔ㄨ鍙栧瓧娈?
        auto_fields_info = ""
        available_fields = []
        if data_source and os.path.exists(summary_path):
            try:
                df_temp = pd.read_excel(summary_path, sheet_name=data_source, nrows=1)
                available_fields = df_temp.columns.tolist()
                auto_fields_info = f"馃搳 鍙敤瀛楁锛歿', '.join(available_fields)}"
            except Exception:
                pass
        
        # 鏍规嵁鍥捐〃绫诲瀷鏄剧ず涓嶅悓鐨勫瓧娈佃緭鍏?
        if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel"]:
            # 鍙屽瓧娈靛浘琛紙X 杞?+ Y 杞达級
            x_field = st.text_input("X 杞村瓧娈?, placeholder="渚嬪锛氭€婚攢鍞", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 杞村瓧娈?, placeholder="渚嬪锛氶攢鍞憳", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "pie":
            # 楗煎浘锛堝垎绫?+ 鏁板€硷級
            x_field = st.text_input("鍒嗙被瀛楁", placeholder="渚嬪锛氫骇鍝?, help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("鏁板€煎瓧娈?, placeholder="渚嬪锛氬崰姣?, help=auto_fields_info if auto_fields_info else None)
        elif chart_type in ["boxplot", "violin"]:
            # 绠辩嚎鍥?灏忔彁鐞村浘锛堝垎绫?+ 鏁板€硷級
            x_field = st.text_input("鍒嗙被瀛楁", placeholder="渚嬪锛氬煄甯?, help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("鏁板€煎瓧娈?, placeholder="渚嬪锛氶攢鍞", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "bubble":
            # 姘旀场鍥撅紙X + Y + 澶у皬锛?
            x_field = st.text_input("X 杞村瓧娈?, placeholder="渚嬪锛氬勾榫勬", help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("Y 杞村瓧娈?, placeholder="渚嬪锛氭€婚攢鍞", help=auto_fields_info if auto_fields_info else None)
            size_field = st.text_input("澶у皬瀛楁", placeholder="渚嬪锛氳鍗曟暟", help=auto_fields_info if auto_fields_info else None)
        elif chart_type == "polar":
            # 鏋佸潗鏍囧浘锛堣搴?+ 鍗婂緞锛?
            x_field = st.text_input("瑙掑害瀛楁", placeholder="渚嬪锛氭槦鏈?, help=auto_fields_info if auto_fields_info else None)
            y_field = st.text_input("鍗婂緞瀛楁", placeholder="渚嬪锛氶攢鍞", help=auto_fields_info if auto_fields_info else None)
        elif chart_type in ["multi_column", "column_clustered", "heatmap"]:
            # 澶嶆潅鍥捐〃锛堜娇鐢?JSON 閰嶇疆锛?
            x_field = st.text_area("瀛楁閰嶇疆", 
                                  placeholder='{"category_field": "閿€鍞憳", "series": ["浜у搧 A", "浜у搧 B"]}',
                                  help=auto_fields_info if auto_fields_info else None)
            y_field = ""
        else:
            # 鍏朵粬鍥捐〃绫诲瀷
            x_field = st.text_area("瀛楁閰嶇疆", placeholder="JSON 鏍煎紡锛屾牴鎹浘琛ㄧ被鍨嬮厤缃?, help=auto_fields_info if auto_fields_info else None)
            y_field = ""
    
    description = st.text_area("鎻忚堪", placeholder="渚嬪锛氶攢鍞憳涓氱哗妯悜鏉″舰鍥?)
    
    if st.button("鉃?娣诲姞鍥捐〃閰嶇疆"):
        if not chart_key or not chart_title or not data_source:
            st.error("鉂?璇峰～鍐欏繀濉瓧娈?)
        else:
            chart_config = {
                "description": description,
                "data_source": data_source,
                "chart_type": chart_type,
                "title": chart_title
            }
            
            # 鏍规嵁鍥捐〃绫诲瀷淇濆瓨瀵瑰簲瀛楁
            if chart_type in ["bar_horizontal", "bar_vertical", "line", "scatter", "area", "histogram", "waterfall", "funnel", "bubble", "polar"]:
                chart_config["x_field"] = x_field
                chart_config["y_field"] = y_field
                # 姘旀场鍥鹃澶栦繚瀛?size_field
                if chart_type == "bubble" and 'size_field' in locals():
                    chart_config["size_field"] = size_field
                # 鏋佸潗鏍囧浘浣跨敤 angle_field 鍜?radius_field 鍚嶇О
                if chart_type == "polar":
                    chart_config["angle_field"] = x_field
                    chart_config["radius_field"] = y_field
            elif chart_type == "pie":
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["boxplot", "violin"]:
                chart_config["category_field"] = x_field
                chart_config["value_field"] = y_field
            elif chart_type in ["multi_column", "column_clustered"]:
                # 瑙ｆ瀽 JSON 閰嶇疆
                try:
                    json_config = json.loads(x_field) if x_field else {}
                    if 'category_field' in json_config:
                        chart_config["category_field"] = json_config['category_field']
                    if 'series' in json_config:
                        chart_config["series"] = json_config['series']
                except json.JSONDecodeError:
                    st.warning("鈿狅笍 瀛楁閰嶇疆鏍煎紡閿欒锛屽皢淇濆瓨涓哄瓧绗︿覆")
                    chart_config["category_field"] = x_field
            elif chart_type == "heatmap":
                # 瑙ｆ瀽 JSON 閰嶇疆
                try:
                    json_config = json.loads(x_field) if x_field else {}
                    if 'index_field' in json_config:
                        chart_config["index_field"] = json_config['index_field']
                    if 'columns' in json_config:
                        chart_config["columns"] = json_config['columns']
                except json.JSONDecodeError:
                    st.warning("鈿狅笍 瀛楁閰嶇疆鏍煎紡閿欒锛屽皢淇濆瓨涓哄瓧绗︿覆")
                    chart_config["index_field"] = x_field
            
            key = f"CHART:{chart_key}"
            if key not in placeholders_config["placeholders"]["charts"]:
                placeholders_config["placeholders"]["charts"][key] = chart_config
                
                # 鑷姩淇濆瓨鍒版枃浠?
                try:
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    st.success(f"鉁?宸叉坊鍔犲浘琛ㄩ厤缃細{key} 锛堝凡鑷姩淇濆瓨锛?)
                except Exception as e:
                    st.error(f"鉂?淇濆瓨澶辫触锛歿e}")
                    st.success(f"鉁?宸叉坊鍔犲浘琛ㄩ厤缃細{key} 锛堣鎵嬪姩淇濆瓨锛?)
            else:
                st.warning(f"鈿狅笍 鍥捐〃閰嶇疆宸插瓨鍦細{key}")
    
    # 鏄剧ず鐜版湁鍥捐〃
    st.markdown("---")
    st.subheader("馃搳 鐜版湁鍥捐〃閰嶇疆")
    
    # 妫€鏌ユ槸鍚︽湁姝ｅ湪缂栬緫鐨勯厤缃?
    edit_key = st.session_state.get('editing_chart_key', None)
    
    if placeholders_config["placeholders"]["charts"]:
        for key, config in placeholders_config["placeholders"]["charts"].items():
            # 濡傛灉鏄鍦ㄧ紪杈戠殑閰嶇疆锛屾樉绀虹紪杈戣〃鍗?
            if edit_key == key:
                st.markdown(f"#### 鉁忥笍 缂栬緫锛歿config.get('title', key)}")
                
                edit_chart_key = st.text_input("鍥捐〃 Key", value=key.replace("CHART:", ""), key=f"edit_key_input_{key}")
                edit_title = st.text_input("鍥捐〃鏍囬", value=config.get('title', ''), key=f"edit_title_{key}")
                edit_type = st.selectbox("鍥捐〃绫诲瀷", options=list(chart_types.keys()), 
                                        format_func=lambda x: chart_types[x],
                                        index=list(chart_types.keys()).index(config.get('chart_type', 'bar_horizontal')) if config.get('chart_type') in chart_types.keys() else 0,
                                        key=f"edit_type_{key}")
                edit_data_source = st.selectbox("鏁版嵁婧?, options=available_sheets, 
                                               index=available_sheets.index(config.get('data_source', '')) if config.get('data_source') in available_sheets else 0,
                                               key=f"edit_source_{key}")
                edit_x_field = st.text_input("X 杞村瓧娈?, value=config.get('x_field', ''), key=f"edit_x_{key}")
                edit_y_field = st.text_input("Y 杞村瓧娈?, value=config.get('y_field', ''), key=f"edit_y_{key}")
                edit_description = st.text_area("鎻忚堪", value=config.get('description', ''), key=f"edit_desc_{key}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("馃捑 淇濆瓨淇敼", type="primary", key=f"edit_save_{key}"):
                        new_key = f"CHART:{edit_chart_key}"
                        new_config = {
                            "description": edit_description,
                            "data_source": edit_data_source,
                            "chart_type": edit_type,
                            "title": edit_title,
                        }
                        
                        # 鏍规嵁鍥捐〃绫诲瀷淇濆瓨瀵瑰簲瀛楁
                        if edit_type in ['bar_horizontal', 'bar_vertical', 'line', 'scatter', 'area', 'histogram', 'waterfall', 'funnel']:
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                        elif edit_type == 'pie':
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type in ['multi_column', 'column_clustered']:
                            new_config['category_field'] = edit_x_field
                            # series 瀛楁鏆備笉鏀寔缂栬緫
                        elif edit_type == 'heatmap':
                            new_config['index_field'] = edit_x_field
                            # columns 瀛楁鏆備笉鏀寔缂栬緫
                        elif edit_type in ['boxplot', 'violin']:
                            new_config['category_field'] = edit_x_field
                            new_config['value_field'] = edit_y_field
                        elif edit_type == 'bubble':
                            new_config['x_field'] = edit_x_field
                            new_config['y_field'] = edit_y_field
                            # size_field 鏆備笉鏀寔缂栬緫
                        elif edit_type == 'polar':
                            new_config['angle_field'] = edit_x_field
                            new_config['radius_field'] = edit_y_field
                        
                        # 濡傛灉 key 鏀瑰彉浜嗭紝鍏堝垹闄ゆ棫鐨?
                        if new_key != key:
                            del placeholders_config["placeholders"]["charts"][key]
                        
                        placeholders_config["placeholders"]["charts"][new_key] = new_config
                        
                        # 鑷姩淇濆瓨
                        with open(placeholders_file, 'w', encoding='utf-8') as f:
                            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                        
                        st.session_state['editing_chart_key'] = None
                        st.success("鉁?宸蹭繚瀛樺苟鑷姩淇濆瓨鏂囦欢")
                        st.rerun()
                
                with col2:
                    if st.button("鉂?鍙栨秷缂栬緫", key=f"edit_cancel_{key}"):
                        st.session_state['editing_chart_key'] = None
                        st.rerun()
                
                st.markdown("---")
            else:
                # 鏄剧ず閰嶇疆鍗＄墖
                with st.expander(f"馃搱 {key} - {config.get('title', '')}"):
                    st.json(config)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"鉁忥笍 缂栬緫", key=f"edit_btn_{key}"):
                            st.session_state['editing_chart_key'] = key
                            st.rerun()
                    with col2:
                        if st.button(f"馃棏锔?鍒犻櫎", key=f"delete_chart_{key}"):
                            del placeholders_config["placeholders"]["charts"][key]
                            # 鑷姩淇濆瓨
                            try:
                                with open(placeholders_file, 'w', encoding='utf-8') as f:
                                    json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                            except Exception as e:
                                st.error(f"淇濆瓨澶辫触锛歿e}")
                            st.rerun()
    else:
        st.info("鏆傛棤鍥捐〃閰嶇疆锛岃娣诲姞")
    
    # 缁熶竴淇濆瓨鎸夐挳
    st.markdown("---")
    if st.button("馃捑 淇濆瓨鎵€鏈夊浘琛ㄩ厤缃?, type="primary", use_container_width=True):
        try:
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            st.success(f"鉁?宸蹭繚瀛橈細{placeholders_file}")
        except Exception as e:
            st.error(f"鉂?淇濆瓨澶辫触锛歿e}")

# ========== Tab 3: 娲炲療閰嶇疆 ==========
with tab3:
    st.header("馃挕 娲炲療閰嶇疆")
    st.markdown("涓烘瘡涓浘琛ㄩ厤缃?AI 娲炲療鍒嗘瀽瑕佺偣锛堟姌鍙犵紪杈戯紝淇敼鍚庤嚜鍔ㄤ繚瀛橈級")
    
    # 鍔犺浇鍥捐〃閰嶇疆
    charts_config = placeholders_config.get("placeholders", {}).get("charts", {})
    
    if not charts_config:
        st.warning("鈿狅笍 璇峰厛鍦?鍥捐〃閰嶇疆'鏍囩椤垫坊鍔犲浘琛?)
        st.stop()
    
    # 鍔犺浇宸叉湁鐨勬礊瀵熼厤缃?
    existing_insights = placeholders_config.get("placeholders", {}).get("insights", {})
    
    st.info(f"馃搳 褰撳墠鍥捐〃鏁伴噺锛歿len(charts_config)} | 宸查厤缃礊瀵燂細{len(existing_insights)}")
    
    # 涓烘瘡涓浘琛ㄩ厤缃礊瀵熻鐐癸紙鎶樺彔 + 瀹炴椂淇濆瓨锛?
    st.subheader("閰嶇疆娲炲療鍒嗘瀽瑕佺偣")
    st.caption("馃挕 鐐瑰嚮灞曞紑缂栬緫锛屼慨鏀瑰悗鑷姩淇濆瓨")
    
    insights_config = {}
    
    for i, (chart_key, chart_cfg) in enumerate(charts_config.items(), 1):
        # 灏濊瘯鍔犺浇宸叉湁閰嶇疆
        existing = existing_insights.get(chart_key, {})
        
        # 浠庡凡鏈夐厤缃垨榛樿鍊煎姞杞?
        default_dimensions = existing.get("dimensions", ["瓒嬪娍鍒嗘瀽", "瀵规瘮鍒嗘瀽"])
        default_metrics = existing.get("metrics", ["鎬婚攢鍞", "璁㈠崟鏁?, "瀹㈠崟浠?])
        default_baseline = existing.get("baseline", "鐜瘮")
        default_style = existing.get("style", "骞宠　鍨?)
        default_word_count = existing.get("word_count", 150)
        default_enabled = existing.get("enabled", True)
        default_prompt = existing.get("custom_prompt", "")
        
        # 浣跨敤鎶樺彔瀹瑰櫒
        with st.expander(f"馃搳 {i}. {chart_cfg.get('title', chart_key)}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 鍒嗘瀽缁村害閫夋嫨
                analysis_dimensions = st.multiselect(
                    "鍒嗘瀽缁村害",
                    options=["瓒嬪娍鍒嗘瀽", "瀵规瘮鍒嗘瀽", "鍗犳瘮鍒嗘瀽", "鎺掑悕鍒嗘瀽", "寮傚父妫€娴?, "鐩稿叧鎬у垎鏋?, "鍒嗗竷鍒嗘瀽"],
                    default=default_dimensions,
                    key=f"dim_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 鍏抽敭鎸囨爣
                key_metrics = st.text_area(
                    "鍏抽敭鎸囨爣锛堟瘡琛屼竴涓級",
                    placeholder="鎬婚攢鍞\n璁㈠崟鏁癨n瀹㈠崟浠?,
                    value='\n'.join(default_metrics),
                    key=f"metrics_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 瀵规瘮鍩哄噯
                baseline_options = ["鐜瘮", "鍚屾瘮", "鐩爣鍊?, "骞冲潎鍊?, "澶撮儴瀵规瘮", "灏鹃儴瀵规瘮", "鏃犲姣?]
                baseline = st.selectbox(
                    "瀵规瘮鍩哄噯",
                    options=baseline_options,
                    index=baseline_options.index(default_baseline) if default_baseline in baseline_options else 0,
                    key=f"baseline_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
            
            with col2:
                # 娲炲療椋庢牸
                style_options = ["鏁版嵁椹卞姩", "闂瀵煎悜", "寤鸿瀵煎悜", "骞宠　鍨?]
                insight_style = st.selectbox(
                    "娲炲療椋庢牸",
                    options=style_options,
                    index=style_options.index(default_style) if default_style in style_options else 3,
                    key=f"style_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 瀛楁暟瑕佹眰
                word_count = st.slider(
                    "瀛楁暟瑕佹眰",
                    min_value=50,
                    max_value=300,
                    value=default_word_count,
                    step=10,
                    key=f"words_{chart_key}",
                    on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
                )
                
                # 鏄惁鍚敤
                enabled = st.checkbox("鍚敤", value=default_enabled, key=f"enabled_{chart_key}",
                                     on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config))
            
            # 鑷畾涔夋彁绀鸿瘝
            custom_prompt = st.text_area(
                "鑷畾涔夋彁绀鸿瘝锛堝彲閫夛級",
                placeholder="渚嬪锛氶噸鐐瑰垎鏋愬ご閮ㄩ攢鍞憳鐨勪笟缁╄础鐚害...",
                value=default_prompt,
                height=80,
                key=f"prompt_{chart_key}",
                on_change=lambda: save_insights_auto(charts_config, placeholders_file, placeholders_config)
            )
            
            # 淇濆瓨閰嶇疆
            insights_config[chart_key] = {
                "dimensions": analysis_dimensions,
                "metrics": [m.strip() for m in key_metrics.split('\n') if m.strip()],
                "baseline": baseline,
                "style": insight_style,
                "word_count": word_count,
                "enabled": enabled,
                "custom_prompt": custom_prompt
            }
    
    # 瀹炴椂淇濆瓨鍑芥暟
    def save_insights_auto(charts_cfg, p_file, p_config):
        """瀹炴椂淇濆瓨娲炲療閰嶇疆"""
        current_insights = {}
        for ck in charts_cfg.keys():
            current_insights[ck] = {
                "dimensions": st.session_state.get(f"dim_{ck}", ["瓒嬪娍鍒嗘瀽", "瀵规瘮鍒嗘瀽"]),
                "metrics": [m.strip() for m in st.session_state.get(f"metrics_{ck}", "").split('\n') if m.strip()],
                "baseline": st.session_state.get(f"baseline_{ck}", "鐜瘮"),
                "style": st.session_state.get(f"style_{ck}", "骞宠　鍨?),
                "word_count": st.session_state.get(f"words_{ck}", 150),
                "enabled": st.session_state.get(f"enabled_{ck}", True),
                "custom_prompt": st.session_state.get(f"prompt_{ck}", "")
            }
        
        p_config["placeholders"]["insights"] = current_insights
        
        try:
            with open(p_file, 'w', encoding='utf-8') as f:
                json.dump(p_config, f, ensure_ascii=False, indent=2)
            st.toast("馃搳 娲炲療閰嶇疆宸茶嚜鍔ㄤ繚瀛?, icon="鉁?)
        except Exception as e:
            st.toast(f"淇濆瓨澶辫触锛歿e}", icon="鉂?)
    
    # 鏄剧ず閰嶇疆棰勮锛堟姌鍙狅級
    st.markdown("---")
    st.subheader("馃搵 娲炲療閰嶇疆棰勮")
    
    if insights_config:
        with st.expander("馃搵 鐐瑰嚮鏌ョ湅/澶嶅埗閰嶇疆棰勮", expanded=False):
            for chart_key, insight_cfg in insights_config.items():
                with st.expander(f"馃挕 {chart_key}"):
                    st.json(insight_cfg)

# ========== Tab 7: PPT 鍙橀噺鎬昏 ==========
with tab7:
    st.header("馃敄 PPT 鍙橀噺鎬昏")
    st.markdown("鍔ㄦ€佸睍绀烘墍鏈夊凡閰嶇疆鐨勫彉閲忥紝鏂逛究鍦?PPT 妯℃澘涓娇鐢?)
    
    # 鍔犺浇閰嶇疆
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        st.warning("鈿狅笍 閰嶇疆鏂囦欢涓嶅瓨鍦?)
        st.stop()
    
    # 缁熻鍙橀噺鏁伴噺
    charts_count = len(placeholders_config.get('placeholders', {}).get('charts', {}))
    insights_count = len(placeholders_config.get('placeholders', {}).get('insights', {}))
    text_vars_count = len(placeholders_config.get('placeholders', {}).get('text', {}))
    tables_count = len(placeholders_config.get('placeholders', {}).get('tables', {}))
    total_count = charts_count + insights_count + text_vars_count + tables_count + 2  # +2 for conclusion & strategy
    
    st.metric("鍙橀噺鎬绘暟", total_count, f"鍥捐〃{charts_count} + 娲炲療{insights_count} + 鏂囨湰{text_vars_count} + 琛ㄦ牸{tables_count} + 鐗规畩 2")
    
    st.markdown("---")
    st.subheader("馃搳 鍥捐〃鍙橀噺锛堝姩鎬侀厤缃級")
    st.markdown("""
    **浣跨敤鏂规硶**锛氬湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ヤ互涓嬪崰浣嶇锛?
    ```
    [CHART:xxx]
    ```
    """)
    
    charts = placeholders_config.get('placeholders', {}).get('charts', {})
    
    if charts:
        chart_data = []
        for chart_key, chart_cfg in charts.items():
            chart_data.append({
                '鍗犱綅绗?: f'[CHART:{chart_key.replace("CHART:", "")}]',
                '鍥捐〃鏍囬': chart_cfg.get('title', ''),
                '鏁版嵁婧?: chart_cfg.get('data_source', ''),
                '鍥捐〃绫诲瀷': chart_cfg.get('chart_type', ''),
                'PPT 椤电爜': chart_cfg.get('slide_index', '鏈缃?)
            })
        
        st.dataframe(chart_data, use_container_width=True, hide_index=True)
    else:
        st.info("鏆傛棤鍥捐〃閰嶇疆")
    
    st.markdown("---")
    st.subheader("馃挕 娲炲療鍙橀噺")
    st.markdown("""
    **浣跨敤鏂规硶**锛氬湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ヤ互涓嬪崰浣嶇锛?
    ```
    {{INSIGHT:xxx}}
    ```
    """)
    
    insights = placeholders_config.get('placeholders', {}).get('insights', {})
    
    if insights:
        insight_data = []
        for chart_key, insight_cfg in insights.items():
            chart_name = chart_key.replace('CHART:', '')
            insight_data.append({
                '鍗犱綅绗?: f'{{{{INSIGHT:{chart_name}}}}}',
                '鍒嗘瀽缁村害': ', '.join(insight_cfg.get('dimensions', [])),
                '鍏抽敭鎸囨爣': ', '.join(insight_cfg.get('metrics', [])),
                '瀵规瘮鍩哄噯': insight_cfg.get('baseline', ''),
                '娲炲療椋庢牸': insight_cfg.get('style', ''),
                '瀛楁暟瑕佹眰': f"{insight_cfg.get('word_count', 150)}瀛?,
                '鍚敤': '鉁? if insight_cfg.get('enabled', True) else '鉂?
            })
        
        st.dataframe(insight_data, use_container_width=True, hide_index=True)
    else:
        st.info("鏆傛棤娲炲療閰嶇疆锛岃鍦?馃挕 娲炲療閰嶇疆'鏍囩椤甸厤缃?)
    
    st.markdown("---")
    st.subheader("馃摑 鏂囨湰鍙橀噺")
    st.markdown("""
    **浣跨敤鏂规硶**锛氬湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ヤ互涓嬪崰浣嶇锛?
    ```
    [TEXT:xxx]
    ```
    """)
    
    text_vars = placeholders_config.get('placeholders', {}).get('text', {})
    
    if text_vars:
        text_data = []
        for text_key, text_cfg in text_vars.items():
            text_data.append({
                '鍗犱綅绗?: f'[{text_key}]',
                '鎻忚堪': text_cfg.get('description', ''),
                '榛樿鍊?: text_cfg.get('default', ''),
                'PPT 椤电爜': text_cfg.get('slide_index', '鏈缃?)
            })
        
        st.dataframe(text_data, use_container_width=True, hide_index=True)
    else:
        st.info("鏆傛棤鏂囨湰鍙橀噺閰嶇疆")
    
    st.markdown("---")
    st.subheader("馃搳 KPI 鍗＄墖鍙橀噺")
    st.markdown("""
    **浣跨敤鏂规硶**锛氬湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ヤ互涓嬪崰浣嶇锛?
    ```
    [KPI:cards]
    ```
    **璇存槑**锛氳嚜鍔ㄧ敓鎴愭牳蹇?KPI 鍗＄墖锛堜粠缁熻瑙勫垯涓瘑鍒?type="kpi" 鐨勬寚鏍囷級
    """)
    
    # 鍔ㄦ€佽鍙?KPI 鎸囨爣 - 浠庣粺璁¤鍒欎腑鏌ユ壘 type="kpi" 鐨勯厤缃?
    kpi_metrics = []
    stats_sheets = stats_config.get("stats_sheets", {})
    for sheet_name, rule in stats_sheets.items():
        if rule.get("type") == "kpi" and rule.get("enabled", True):
            metrics = rule.get("metrics", [])
            for m in metrics:
                kpi_metrics.append(m.get("alias", m.get("field", "鏈煡鎸囨爣")))
    
    if kpi_metrics:
        st.success(f"鉁?宸茶瘑鍒?{len(kpi_metrics)} 涓?KPI 鎸囨爣锛歿', '.join(kpi_metrics[:10])}{'...' if len(kpi_metrics) > 10 else ''}")
    else:
        st.info("馃挕 鏆傛棤 KPI 鎸囨爣锛岃鍦ㄣ€岎煋?缁熻瑙勫垯閰嶇疆銆嶄腑娣诲姞 type=\"kpi\" 鐨勭粺璁¤鍒?)
    
    st.markdown("---")
    st.subheader("馃搵 琛ㄦ牸鍙橀噺")
    st.markdown("""
    **浣跨敤鏂规硶**锛氬湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ヤ互涓嬪崰浣嶇锛?
    ```
    [TABLE:xxx]
    ```
    """)
    
    table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
    
    if table_vars:
        table_data = []
        for table_key, table_cfg in table_vars.items():
            table_data.append({
                '鍗犱綅绗?: f'[{table_key}]',
                '鎻忚堪': table_cfg.get('description', ''),
                '鏁版嵁婧?: table_cfg.get('data_source', ''),
                'PPT 椤电爜': table_cfg.get('slide_index', '鏈缃?)
            })
        
        st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.info("鏆傛棤琛ㄦ牸鍙橀噺閰嶇疆")
    
    st.markdown("---")
    st.subheader("馃幆 鐗规畩鍙橀噺锛圓I 鑷姩鐢熸垚锛?)
    st.markdown("""馃挕 **鎻愮ず**锛氱粨璁哄拰绛栫暐鍙橀噺鍙湪'馃幆 缁撹 & 绛栫暐'鏍囩椤典腑鑷畾涔夌敓鎴愭彁绀鸿瘝""")
    
    # 鍔ㄦ€佽鍙栫壒娈婂彉閲忛厤缃?- 浠庣粨璁?绛栫暐 tab 鐨勯厤缃腑璇诲彇
    special_vars = placeholders_config.get('special_insights', {})
    
    conclusion_cfg = special_vars.get('conclusion', {})
    strategy_cfg = special_vars.get('strategy', {})
    
    # 鑾峰彇鍔ㄦ€侀厤缃殑缁村害
    conclusion_dims = conclusion_cfg.get('dimensions', ['涓氱哗缁撴瀯', '澧為暱浜偣', '鏍稿績鐭澘', '涓氬姟椋庨櫓'])
    strategy_dims = strategy_cfg.get('dimensions', ['瀹㈡埛杩愯惀绛栫暐', '浜у搧缁勫悎绛栫暐', '鍥㈤槦绠＄悊绛栫暐', '钀ラ攢鑺傚绛栫暐'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **缁撹鍙橀噺**锛?
        ```
        {{INSIGHT:conclusion}}
        ```
        **璇存槑**锛歿conclusion_cfg.get('description', 'AI 鑷姩鐢熸垚鏍稿績缁撹')}
        **鍒嗘瀽缁村害**锛歿', '.join(conclusion_dims)}
        **椋庢牸**锛歿conclusion_cfg.get('style', '鏁版嵁椹卞姩')} | **瀛楁暟**锛歿conclusion_cfg.get('word_count', 300)}瀛?
        """)
    
    with col2:
        st.info(f"""
        **绛栫暐鍙橀噺**锛?
        ```
        {{INSIGHT:strategy}}
        ```
        **璇存槑**锛歿strategy_cfg.get('description', 'AI 鑷姩鐢熸垚钀藉湴绛栫暐')}
        **绛栫暐缁村害**锛歿', '.join(strategy_dims)}
        **椋庢牸**锛歿strategy_cfg.get('style', '寤鸿瀵煎悜')} | **瀛楁暟**锛歿strategy_cfg.get('word_count', 400)}瀛?
        """)
    
    st.markdown("---")
    st.info("""馃挕 **鎻愮ず**锛?
- 浠ヤ笂鎵€鏈夊彉閲忓潎涓哄姩鎬侀厤缃紝瀹為檯鏄剧ず鎮ㄥ凡閰嶇疆鐨勫彉閲?
- 澶嶅埗鍗犱綅绗﹀埌 PPT 妯℃澘涓殑鏂囨湰妗嗗嵆鍙娇鐢?
- 杩愯 `Run.bat` 鏃朵細鑷姩鏇挎崲涓哄疄闄呭唴瀹?"")

# ========== Tab 4: 鑷畾涔夊彉閲?==========
with tab4:
    st.header("鈿欙笍 鑷畾涔夊彉閲?)
    st.markdown("鑷畾涔?PPT 妯℃澘涓殑鍙橀噺锛屽畬鍏ㄨ嚜鐢遍厤缃?)
    
    # 鍔犺浇閰嶇疆
    if os.path.exists(placeholders_file):
        with open(placeholders_file, 'r', encoding='utf-8') as f:
            placeholders_config = json.load(f)
    else:
        placeholders_config = {
            "placeholders": {
                "charts": {},
                "insights": {},
                "text": {},
                "tables": {}
            }
        }
    
    st.subheader("馃摑 娣诲姞鑷畾涔夋枃鏈彉閲?)
    
    col1, col2 = st.columns(2)
    
    with col1:
        custom_var_key = st.text_input(
            "鍙橀噺 Key",
            placeholder="渚嬪锛歝ustom_title",
            help="鐢ㄤ簬 PPT 鍗犱綅绗︼細[TEXT:custom_title]"
        )
        
        custom_var_desc = st.text_input(
            "鍙橀噺鎻忚堪",
            placeholder="渚嬪锛氳嚜瀹氫箟鏍囬"
        )
    
    with col2:
        custom_var_default = st.text_area(
            "榛樿鍊?,
            placeholder="渚嬪锛氶攢鍞暟鎹垎鏋愭姤鍛?,
            height=80
        )
        
        custom_var_page = st.number_input(
            "PPT 椤电爜",
            min_value=0,
            max_value=20,
            value=0,
            help="鍗犱綅绗︽墍鍦ㄧ殑 PPT 椤电爜锛堜粠 0 寮€濮嬶級"
        )
    
    if st.button("鉃?娣诲姞鑷畾涔夊彉閲?, type="primary"):
        if not custom_var_key:
            st.error("鉂?璇峰～鍐欏彉閲?Key")
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
            
            # 淇濆瓨閰嶇疆
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            
            st.success(f"鉁?宸叉坊鍔犺嚜瀹氫箟鍙橀噺锛歔{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("馃搵 宸查厤缃殑鑷畾涔夊彉閲?)
    
    text_vars = placeholders_config.get('placeholders', {}).get('text', {})
    
    if text_vars:
        for var_key, var_cfg in text_vars.items():
            if var_key.startswith('TEXT:'):
                with st.expander(f"馃摑 [{var_key}] - {var_cfg.get('description', '')}"):
                    st.json(var_cfg)
                    
                    if st.button(f"馃棏锔?鍒犻櫎", key=f"delete_{var_key}"):
                        del placeholders_config["placeholders"]["text"][var_key]
                        
                        with open(placeholders_file, 'w', encoding='utf-8') as f:
                            json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                        
                        st.success(f"鉁?宸插垹闄わ細[{var_key}]")
                        st.rerun()
    else:
        st.info("鏆傛棤鑷畾涔夊彉閲?)
    
    st.markdown("---")
    st.subheader("馃搵 娣诲姞鑷畾涔夎〃鏍煎彉閲?)
    
    col3, col4 = st.columns(2)
    
    with col3:
        table_var_key = st.text_input(
            "琛ㄦ牸鍙橀噺 Key",
            placeholder="渚嬪锛歝ustom_table",
            help="鐢ㄤ簬 PPT 鍗犱綅绗︼細[TABLE:custom_table]"
        )
        
        table_var_desc = st.text_input(
            "琛ㄦ牸鎻忚堪",
            placeholder="渚嬪锛氳嚜瀹氫箟鏁版嵁琛?
        )
        
        table_var_source = st.text_input(
            "鏁版嵁婧?,
            placeholder="Excel Sheet 鍚嶇О锛屼緥濡傦細鑷畾涔夌粺璁?
        )
    
    with col4:
        table_var_page = st.number_input(
            "PPT 椤电爜",
            min_value=0,
            max_value=20,
            value=0,
            key="table_page"
        )
    
    if st.button("鉃?娣诲姞鑷畾涔夎〃鏍煎彉閲?):
        if not table_var_key:
            st.error("鉂?璇峰～鍐欒〃鏍煎彉閲?Key")
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
            
            st.success(f"鉁?宸叉坊鍔犺嚜瀹氫箟琛ㄦ牸鍙橀噺锛歔{full_key}]")
            st.rerun()
    
    st.markdown("---")
    st.subheader("馃搵 宸查厤缃殑鑷畾涔夎〃鏍煎彉閲?)
    
    table_vars = placeholders_config.get('placeholders', {}).get('tables', {})
    
    if table_vars:
        for var_key, var_cfg in table_vars.items():
            with st.expander(f"馃搵 [{var_key}] - {var_cfg.get('description', '')}"):
                st.json(var_cfg)
                
                if st.button(f"馃棏锔?鍒犻櫎", key=f"delete_table_{var_key}"):
                    del placeholders_config["placeholders"]["tables"][var_key]
                    
                    with open(placeholders_file, 'w', encoding='utf-8') as f:
                        json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"鉁?宸插垹闄わ細[{var_key}]")
                    st.rerun()
    else:
        st.info("鏆傛棤鑷畾涔夎〃鏍煎彉閲?)
    
    st.markdown("---")
    st.info("馃挕 **鎻愮ず**锛歕n- 鑷畾涔夊彉閲忓悗锛屽湪 PPT 妯℃澘涓彃鍏ユ枃鏈锛岃緭鍏ュ搴旂殑鍗犱綅绗n- 鏂囨湰鍙橀噺锛歚[TEXT:xxx]`\n- 琛ㄦ牸鍙橀噺锛歚[TABLE:xxx]`\n- 杩愯 `Run.bat` 鏃朵細鑷姩鏇挎崲")
    
    # 缁熶竴淇濆瓨鎸夐挳
    st.markdown("---")
    if st.button("馃捑 淇濆瓨鎵€鏈夎嚜瀹氫箟鍙橀噺", type="primary", use_container_width=True):
        try:
            with open(placeholders_file, 'w', encoding='utf-8') as f:
                json.dump(placeholders_config, f, ensure_ascii=False, indent=2)
            st.success(f"鉁?宸蹭繚瀛橈細{placeholders_file}")
        except Exception as e:
            st.error(f"鉂?淇濆瓨澶辫触锛歿e}")

# ========== Tab 5: 缁撹 & 绛栫暐 ==========
