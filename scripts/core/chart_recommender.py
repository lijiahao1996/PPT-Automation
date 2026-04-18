# -*- coding: utf-8 -*-
"""
图表推荐引擎
基于统计规则自动推荐图表类型
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ChartRecommender:
    """图表推荐引擎"""
    
    # 统计类型 → 推荐图表类型
    CHART_MAP = {
        'kpi': {'type': 'bar_vertical', 'reason': 'KPI 指标适合用柱状图对比'},
        'ranking': {'type': 'bar_horizontal', 'reason': '排名适合用横向条形图对比'},
        'composition': {'type': 'pie', 'reason': '占比适合用饼图/环形图展示'},
        'comparison': {'type': 'column_clustered', 'reason': '对比适合用分组柱状图'},
        'trend': {'type': 'line', 'reason': '趋势适合用折线图展示'},
        'distribution': {'type': 'histogram', 'reason': '分布适合用直方图展示'},
        'matrix': {'type': 'heatmap', 'reason': '矩阵适合用热力图展示'},
        'outlier': {'type': 'boxplot', 'reason': '异常检测适合用箱线图'}
    }
    
    def recommend(self, stats_config: List[Dict]) -> List[Dict]:
        """
        基于统计规则推荐图表
        
        Args:
            stats_config: 统计规则配置列表
        
        Returns:
            图表推荐列表
        """
        chart_recommendations = []
        
        for stat in stats_config:
            if not stat.get('enabled', False):
                continue
            
            stat_type = stat.get('type', '')
            stat_name = stat.get('name', 'unknown')
            
            # 获取推荐图表类型
            chart_info = self.CHART_MAP.get(stat_type, {'type': 'bar_vertical', 'reason': '默认柱状图'})
            
            # 生成图表配置
            chart_config = {
                'chart_key': self._generate_key(stat_name),
                'description': f"{stat_name}图表",
                'data_source': stat_name,
                'chart_type': chart_info['type'],
                'title': f"{stat_name}分析",
                'ai_reason': chart_info['reason']
            }
            
            # 根据统计类型添加特定配置（严格按照图表引擎要求）
            if stat_type == 'ranking':
                # bar_horizontal: x_field=数值, y_field=分类
                chart_config['params'] = {
                    'x_field': '总销售额',
                    'y_field': stat.get('group_by', [''])[0] if stat.get('group_by') else ''
                }
            elif stat_type == 'composition':
                # pie: category_field=分类, value_field=数值
                chart_config['params'] = {
                    'category_field': stat.get('group_by', [''])[0] if stat.get('group_by') else '',
                    'value_field': '销售额'
                }
            elif stat_type == 'trend':
                # line: x_field=时间, y_field=数值
                chart_config['params'] = {
                    'x_field': '年月',
                    'y_field': '总销售额'
                }
            elif stat_type == 'matrix':
                # heatmap: 只需要 y_field（行字段）
                chart_config['params'] = {
                    'y_field': stat.get('group_by', [''])[0] if stat.get('group_by') else ''
                }
            elif stat_type == 'comparison':
                # column_clustered: category_field=分类, series=数值列表
                chart_config['params'] = {
                    'category_field': stat.get('group_by', [''])[0] if stat.get('group_by') else '',
                    'series': [m.get('alias', '') for m in stat.get('metrics', []) if m.get('alias')]
                }
            elif stat_type == 'distribution':
                # histogram: y_field=数值
                chart_config['params'] = {
                    'y_field': stat.get('metrics', [{}])[0].get('alias', '数值')
                }
            elif stat_type == 'outlier':
                # boxplot: category_field=分类, value_field=数值
                chart_config['params'] = {
                    'category_field': stat.get('group_by', [''])[0] if stat.get('group_by') else '',
                    'value_field': stat.get('metrics', [{}])[0].get('alias', '数值')
                }
            elif stat_type == 'kpi':
                # bar_vertical: x_field=分类, y_field=数值
                chart_config['params'] = {
                    'x_field': '指标名称',
                    'y_field': stat.get('metrics', [{}])[0].get('alias', '总销售额')
                }
            
            chart_recommendations.append(chart_config)
        
        return chart_recommendations
    
    def _generate_key(self, name: str) -> str:
        """生成图表 Key"""
        # 中文转拼音（简化版，直接用中文）
        key_map = {
            '核心 KPI': 'kpi_summary',
            '销售员业绩': 'sales_by_person',
            '产品占比': 'product_pie',
            '城市排名': 'city_ranking',
            '客户类型': 'customer_comparison',
            '月度趋势': 'monthly_trend',
            '季度对比': 'quarterly_comparison',
            '利润分析': 'profit_analysis'
        }
        return key_map.get(name, name.replace(' ', '_').lower())
    
    def ai_enhance(self, chart_config: List[Dict], base_dir: str = None) -> List[Dict]:
        """
        AI 增强图表推荐
        
        Args:
            chart_config: 基础图表配置
            base_dir: 项目根目录
        
        Returns:
            AI 增强后的配置
        """
        from ai.qwen_client import QwenClient
        
        qwen = QwenClient(base_dir)
        if not qwen.is_available():
            return chart_config
        
        # 构建 Prompt
        prompt = f"""
你是数据可视化专家。请优化以下图表配置：

当前配置：
{str(chart_config[:3])}  # 只显示前 3 个

请为每个图表推荐：
1. 最佳图表类型（从以下选择：bar_horizontal, bar_vertical, pie, line, heatmap, scatter, area, histogram, boxplot）
2. 图表标题（简洁明了）
3. 配色建议（从以下选择：primary, categorical, sequential）

输出 JSON 格式：
{{
  "enhanced_charts": [
    {{
      "chart_key": "chart_key",
      "chart_type": "bar_horizontal",
      "title": "优化后的标题",
      "color_scheme": "primary",
      "reason": "优化理由"
    }},
    ...
  ]
}}
"""
        
        system_prompt = "你是数据可视化专家，输出严格 JSON 格式。只输出 JSON，不要任何其他文字。"
        
        response = qwen.chat(system_prompt, prompt, json_mode=True)
        
        if response:
            result = qwen.parse_json_response(response)
            if result and 'enhanced_charts' in result:
                # 合并 AI 推荐
                enhanced_map = {c['chart_key']: c for c in result['enhanced_charts']}
                for chart in chart_config:
                    if chart['chart_key'] in enhanced_map:
                        ai_rec = enhanced_map[chart['chart_key']]
                        chart['chart_type'] = ai_rec.get('chart_type', chart['chart_type'])
                        chart['title'] = ai_rec.get('title', chart['title'])
                        chart['ai_enhanced'] = True
                        chart['ai_reason'] = ai_rec.get('reason', chart.get('ai_reason', ''))
        
        return chart_config
