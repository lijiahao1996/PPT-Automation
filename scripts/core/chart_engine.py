# -*- coding: utf-8 -*-
"""
图表引擎 - 企业级图表生成器（Matplotlib + 企业样式）

重构版本：按图表类型拆分为子模块
- basic_charts.py: 6 种基础图表（条形图、柱状图、饼图、折线图、热力图、多列柱状图）
- distribution_charts.py: 5 种分布图表（散点图、直方图、箱线图、小提琴图、气泡图）
- advanced_charts.py: 6 种高级图表（面积图、误差棒图、极坐标图、瀑布图、漏斗图）
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import logging

from .charts.basic_charts import BasicChartsMixin
from .charts.distribution_charts import DistributionChartsMixin
from .charts.advanced_charts import AdvancedChartsMixin

logger = logging.getLogger(__name__)


class ChartEngine(BasicChartsMixin, DistributionChartsMixin, AdvancedChartsMixin):
    """
    企业级图表引擎 - 支持 17 种图表类型
    
    使用 Mixin 模式组织图表方法：
    - BasicChartsMixin: 6 种基础图表
    - DistributionChartsMixin: 5 种分布图表  
    - AdvancedChartsMixin: 6 种高级图表
    """
    
    def __init__(self, base_dir: str = None):
        # 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
        self.base_dir = os.environ.get('EXE_WORK_DIR') or base_dir or os.path.dirname(os.path.dirname(__file__))
        self.styles_dir = os.path.join(self.base_dir, 'core', 'styles')
        self.temp_dir = os.path.join(self.base_dir, 'artifacts', 'temp')
        
        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 加载配色方案
        self.colors = self._load_color_palette()
        
        # 应用中文字体配置
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 应用企业样式
        style_file = os.path.join(self.styles_dir, 'enterprise.mplstyle')
        if os.path.exists(style_file):
            plt.style.use(style_file)
            logger.info(f"已应用企业样式：{style_file}")
    
    def _load_color_palette(self) -> dict:
        """加载配色方案"""
        import json
        palette_file = os.path.join(self.styles_dir, 'color_palette.json')
        if os.path.exists(palette_file):
            with open(palette_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


# 导出所有图表方法
__all__ = ['ChartEngine']
