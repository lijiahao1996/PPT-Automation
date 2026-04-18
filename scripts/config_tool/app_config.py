# -*- coding: utf-8 -*-
"""
PPT 配置工具 - 应用配置
包含 CSS 样式、常量定义、工具函数
"""
import os

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
# 项目根目录：支持环境变量、配置文件、动态检测
def get_base_dir():
    """
    获取项目根目录
    优先级：环境变量 N8N_SCRIPTS_BASE_DIR > 动态检测当前工作目录 > 配置文件
    """
    import os
    import configparser
    
    # 1. 优先使用环境变量（Docker 环境中设置为 /app）
    env_base_dir = os.environ.get('N8N_SCRIPTS_BASE_DIR')
    if env_base_dir:
        # Docker 环境中，环境变量是可信的
        if os.path.exists(env_base_dir):
            return env_base_dir
        else:
            # 如果路径不存在，输出警告并使用当前工作目录
            print(f"[WARNING] N8N_SCRIPTS_BASE_DIR={env_base_dir} 不存在，将使用当前工作目录")
    
    # 2. 使用当前工作目录（Docker 中是 /app，本地是项目根目录）
    cwd = os.getcwd()
    # 验证当前目录是否包含 scripts 目录（判断是否为项目根目录）
    if os.path.exists(os.path.join(cwd, 'scripts')):
        return cwd
    
    # 3. 尝试从脚本位置推算项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # scripts/config_tool -> scripts -> project_root
    project_root = os.path.dirname(os.path.dirname(script_dir))
    if os.path.exists(project_root):
        return project_root
    
    # 4. 最后尝试读取配置文件
    config_ini_path = os.path.join(script_dir, '..', '..', 'config.ini')
    if os.path.exists(config_ini_path):
        config = configparser.ConfigParser()
        try:
            config.read(config_ini_path, encoding='utf-8')
            if config.has_option('paths', 'base_dir'):
                config_base_dir = config.get('paths', 'base_dir')
                if config_base_dir and config_base_dir != '@N8N_SCRIPTS_BASE_DIR@' and os.path.exists(config_base_dir):
                    return config_base_dir
        except Exception:
            pass
    
    # 5. 兜底：返回脚本推算的根目录
    return project_root

DEFAULT_BASE_DIR = get_base_dir()

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

def enforce_single_file(directory, file_pattern='.xlsx', exclude_patterns=None):
    """
    确保目录中只保留一个文件（最新的）
    注意：此函数会在文件列表变化时自动执行，避免死循环
    
    Args:
        directory: 目录路径
        file_pattern: 文件扩展名过滤
        exclude_patterns: 排除的文件名模式列表
    
    Returns:
        str: 保留的文件名，如果没有文件则返回 None
    """
    import time
    
    if not os.path.exists(directory):
        return None
    
    if exclude_patterns is None:
        exclude_patterns = ['~$', 'temp', 'tmp']
    
    # 获取所有匹配的文件
    files = []
    for f in os.listdir(directory):
        # 跳过排除的模式
        if any(pattern in f for pattern in exclude_patterns):
            continue
        if f.endswith(file_pattern):
            files.append(f)
    
    # 如果没有文件或只有一个文件，直接返回
    if len(files) <= 1:
        return files[0] if files else None
    
    # 按修改时间排序，保留最新的
    files_with_time = []
    for f in files:
        filepath = os.path.join(directory, f)
        mtime = os.path.getmtime(filepath)
        files_with_time.append((f, mtime))
    
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # 保留最新的，删除其他
    latest_file = files_with_time[0][0]
    deleted_count = 0
    for f, _ in files_with_time[1:]:
        try:
            filepath = os.path.join(directory, f)
            # 添加小延迟避免文件系统竞争
            time.sleep(0.1)
            os.remove(filepath)
            deleted_count += 1
            print(f"[INFO] 删除旧文件: {f}")
        except Exception as e:
            print(f"[WARNING] 删除文件失败 {f}: {e}")
    
    # 如果有删除操作，等待一下让文件系统稳定
    if deleted_count > 0:
        time.sleep(0.2)
    
    return latest_file

# ========== 工具函数 ==========
def validate_path(path):
    """验证路径是否存在"""
    import os
    return os.path.exists(path)

def get_default_raw_data_filename():
    """获取默认原始数据文件名"""
    import configparser
    import os
    
    base_dir = get_base_dir()
    config_path = os.path.join(base_dir, "config.ini")
    
    if os.path.exists(config_path):
        config = configparser.ConfigParser()
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
