# -*- coding: utf-8 -*-
"""
PPT 配置工具 - 应用配置
包含 CSS 样式、常量定义、工具函数
"""

# ========== 页面配置 ==========
PAGE_CONFIG = {
    "page_title": "PPT 报告配置工具",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# ========== CSS 样式 ==========
CUSTOM_CSS = """
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
.log-container {
    background-color: #1e1e1e;
    color: #d4d4d4;
    padding: 1rem;
    border-radius: 0.5rem;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.85rem;
    max-height: 400px;
    overflow-y: auto;
}
</style>
"""

# ========== Tab 定义 ==========
TAB_DEFINITIONS = [
    ("📋 统计规则配置", "tab1_stats_rules"),
    ("📈 图表配置", "tab2_chart_config"),
    ("💡 洞察配置", "tab3_insight_config"),
    ("⚙️ 自定义变量", "tab4_custom_vars"),
    ("🤖 AI 综合洞察", "tab5_conclusion_strategy"),
    ("🔖 PPT 变量总览", "tab6_ppt_vars"),
    ("⚙️ 项目配置", "tab7_project_config"),
    ("🚀 生成 PPT 报告", "tab8_generate_report"),
]

TAB_LABELS = [tab[0] for tab in TAB_DEFINITIONS]

# ========== 默认配置 ==========
DEFAULT_BASE_DIR = r"C:\Users\50319\Desktop\n8n"

DEFAULT_STATS_CONFIG = {
    "version": "1.0",
    "stats_sheets": {},
    "global_settings": {
        "date_range_auto_detect": True
    }
}

DEFAULT_PLACEHOLDERS_CONFIG = {
    "version": "3.0",
    "placeholders": {
        "charts": {},
        "insights": {},
        "text": {},
        "tables": {}
    }
}

# ========== 目录配置 ==========
def get_output_dirs(base_dir):
    """获取 output 目录结构"""
    output_dir = os.path.join(base_dir, "output")
    return {
        "base": output_dir,
        "uploaded": os.path.join(output_dir, "uploaded"),     # 上传的 Excel
        "summary": os.path.join(output_dir, "summary"),       # 统计汇总 Excel
        "report": os.path.join(output_dir, "report"),         # PPT 报告
    }

def ensure_output_dirs(base_dir):
    """确保 output 子目录存在"""
    dirs = get_output_dirs(base_dir)
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    return dirs

# ========== 工具函数 ==========
def validate_path(path):
    """验证路径是否存在"""
    import os
    return os.path.exists(path)

def get_default_raw_data_filename():
    """获取默认原始数据文件名"""
    import configparser
    import os
    
    config = configparser.ConfigParser()
    config_path = os.path.join(DEFAULT_BASE_DIR, "config.ini")
    
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
        return config.get('paths', 'raw_data_file', fallback='帆软销售明细.xlsx')
    return '帆软销售明细.xlsx'

def get_summary_filename(raw_data_filename):
    """根据原始数据文件名生成统计汇总文件名"""
    if raw_data_filename.endswith('.xlsx'):
        return raw_data_filename.replace('.xlsx', '_统计汇总.xlsx')
    else:
        return raw_data_filename + '_统计汇总.xlsx'

def load_json_file(filepath, default=None):
    """加载 JSON 文件，失败时返回默认值"""
    import json
    import os
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    return default if default is not None else {}
