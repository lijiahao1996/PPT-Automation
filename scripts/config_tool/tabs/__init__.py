# Tabs package - PPT 配置工具 8 个页签
from .tab1_stats_rules import render_tab1
from .tab2_chart_config import render_tab2
from .tab3_insight_config import render_tab3
from .tab4_custom_vars import render_tab4
from .tab5_conclusion_strategy import render_tab5
from .tab6_ppt_vars import render_tab6
from .tab7_project_config import render_tab7
from .tab8_generate_report import render_tab8

__all__ = [
    'render_tab1',
    'render_tab2',
    'render_tab3',
    'render_tab4',
    'render_tab5',
    'render_tab6',
    'render_tab7',
    'render_tab8'
]
