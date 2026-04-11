# -*- coding: utf-8 -*-
"""
统计规则推荐引擎
基于字段映射自动推荐统计规则
"""
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class StatsRecommender:
    """统计规则推荐引擎"""
    
    def __init__(self):
        # 统计规则模板
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """加载统计规则模板"""
        return {
            'kpi': {
                'name': '核心 KPI',
                'type': 'kpi',
                'description': '核心经营指标汇总',
                'metrics': [
                    {'field': '销售额', 'agg': 'sum', 'alias': '总销售额'},
                    {'field': '销售额', 'agg': 'count', 'alias': '总订单数'},
                    {'field': '销售额', 'agg': 'mean', 'alias': '平均客单价'},
                    {'field': '销售额', 'agg': 'max', 'alias': '最高单额'},
                    {'field': '销售额', 'agg': 'min', 'alias': '最低单额'}
                ]
            },
            'ranking': {
                'name': '{dimension}排名',
                'type': 'ranking',
                'description': '按维度排名统计',
                'group_by': ['{dimension}'],
                'metrics': [
                    {'field': '销售额', 'agg': 'sum', 'alias': '总销售额'},
                    {'field': '销售额', 'agg': 'count', 'alias': '订单数'}
                ],
                'sort_by': '总销售额',
                'sort_asc': False
            },
            'composition': {
                'name': '{dimension}占比',
                'type': 'composition',
                'description': '按维度占比分析',
                'group_by': ['{dimension}'],
                'metrics': [
                    {'field': '销售额', 'agg': 'sum', 'alias': '销售额'}
                ],
                'add_percentage': True
            },
            'trend': {
                'name': '月度趋势',
                'type': 'trend',
                'description': '月度销售趋势分析',
                'group_by': ['年月'],
                'metrics': [
                    {'field': '销售额', 'agg': 'sum', 'alias': '总销售额'},
                    {'field': '销售额', 'agg': 'count', 'alias': '订单数'}
                ],
                'sort_by': '年月'
            },
            'comparison': {
                'name': '{dimension}对比',
                'type': 'comparison',
                'description': '按维度对比分析',
                'group_by': ['{dimension}'],
                'metrics': [
                    {'field': '销售额', 'agg': 'sum', 'alias': '总销售额'},
                    {'field': '销售额', 'agg': 'count', 'alias': '订单数'},
                    {'field': '销售额', 'agg': 'mean', 'alias': '客单价'}
                ]
            }
        }
    
    def recommend(self, field_mapping: Dict) -> List[Dict]:
        """
        基于字段映射推荐统计规则
        
        Args:
            field_mapping: 字段映射 {excel_column: standard_name}
        
        Returns:
            推荐的统计规则列表
        """
        recommendations = []
        mapped_fields = set(field_mapping.values())
        
        # 规则 1: 有销售额字段 → 推荐核心 KPI
        if '销售额' in mapped_fields:
            kpi_template = self.templates['kpi'].copy()
            recommendations.append({
                **kpi_template,
                'enabled': True,
                'ai_reason': '检测到销售额字段，建议生成核心 KPI 统计'
            })
        
        # 规则 2: 有销售员 + 销售额 → 推荐排名统计
        if '销售员' in mapped_fields and '销售额' in mapped_fields:
            ranking_template = self._fill_template('ranking', dimension='销售员')
            recommendations.append({
                **ranking_template,
                'enabled': True,
                'ai_reason': '检测到销售员和销售额字段，建议生成业绩排名'
            })
        
        # 规则 3: 有产品 + 销售额 → 推荐占比分析
        if '产品' in mapped_fields and '销售额' in mapped_fields:
            composition_template = self._fill_template('composition', dimension='产品')
            recommendations.append({
                **composition_template,
                'enabled': True,
                'ai_reason': '检测到产品和销售额字段，建议生成占比分析'
            })
        
        # 规则 4: 有城市 + 销售额 → 推荐城市排名
        if '城市' in mapped_fields and '销售额' in mapped_fields:
            city_ranking = self._fill_template('ranking', dimension='城市')
            city_ranking['name'] = '城市排名'
            recommendations.append({
                **city_ranking,
                'enabled': True,
                'ai_reason': '检测到城市和销售额字段，建议生成城市排名'
            })
        
        # 规则 5: 有客户类型 + 销售额 → 推荐客户对比
        if '客户类型' in mapped_fields and '销售额' in mapped_fields:
            comparison_template = self._fill_template('comparison', dimension='客户类型')
            recommendations.append({
                **comparison_template,
                'enabled': True,
                'ai_reason': '检测到客户类型字段，建议生成新老客对比'
            })
        
        # 规则 6: 有时间字段 + 销售额 → 推荐趋势分析
        if '订单时间' in mapped_fields and '销售额' in mapped_fields:
            trend_template = self.templates['trend'].copy()
            recommendations.append({
                **trend_template,
                'enabled': True,
                'ai_reason': '检测到时间字段，建议生成趋势分析'
            })
        
        # 规则 7: 有利润 + 销售额 → 推荐利润分析
        if '利润' in mapped_fields and '销售额' in mapped_fields:
            profit_kpi = {
                'name': '利润分析',
                'type': 'kpi',
                'enabled': False,  # 默认不启用，用户可选择
                'description': '利润相关指标',
                'metrics': [
                    {'field': '利润', 'agg': 'sum', 'alias': '总利润'},
                    {'field': '利润', 'agg': 'mean', 'alias': '平均利润'}
                ],
                'ai_reason': '检测到利润字段，可选生成利润分析'
            }
            recommendations.append(profit_kpi)
        
        return recommendations
    
    def _fill_template(self, template_name: str, **kwargs) -> Dict:
        """填充模板变量"""
        template = self.templates.get(template_name, {})
        result = json.loads(json.dumps(template))  # 深拷贝
        
        for key, value in kwargs.items():
            result['name'] = result.get('name', '').replace(f'{{{key}}}', value)
            if 'group_by' in result:
                result['group_by'] = [g.replace(f'{{{key}}}', value) for g in result['group_by']]
        
        return result
    
    def ai_enhance(self, df_info: Dict, field_mapping: Dict, base_dir: str = None) -> List[Dict]:
        """
        AI 增强推荐（调用千问生成额外推荐）
        
        Args:
            df_info: DataFrame 信息（行数、列数等）
            field_mapping: 字段映射
            base_dir: 项目根目录
        
        Returns:
            AI 生成的额外推荐
        """
        from ai.qwen_client import QwenClient
        
        qwen = QwenClient(base_dir)
        if not qwen.is_available():
            return []
        
        # 构建 Prompt
        prompt = f"""
你是数据分析专家。基于以下数据信息，推荐合适的统计规则：

数据信息:
- 行数：{df_info.get('row_count', 0)}
- 列数：{df_info.get('col_count', 0)}
- 字段映射：{json.dumps(field_mapping, ensure_ascii=False)}

请从以下统计类型中选择适合的（可多选）：
- 核心 KPI（适合所有销售数据）
- 排名统计（适合有分类字段的数据）
- 占比分析（适合分析结构）
- 趋势分析（适合有时间字段的数据）
- 对比分析（适合有分组字段的数据）
- 分布分析（适合分析数据分布）
- 异常检测（适合大数据量）

输出 JSON 格式：
{{
  "recommendations": [
    {{
      "name": "统计名称",
      "type": "统计类型",
      "enabled": true,
      "reason": "推荐理由"
    }},
    ...
  ]
}}
"""
        
        system_prompt = "你是数据分析专家，输出严格 JSON 格式。只输出 JSON，不要任何其他文字。"
        
        response = qwen.chat(system_prompt, prompt, json_mode=True)
        
        if response:
            result = qwen.parse_json_response(response)
            if result and 'recommendations' in result:
                return result['recommendations']
        
        return []
