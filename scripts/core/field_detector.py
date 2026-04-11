# -*- coding: utf-8 -*-
"""
智能字段检测引擎
支持规则匹配 + AI 辅助检测
"""
import pandas as pd
import json
import os
from typing import Dict, List, Optional, Any
import logging

from ai.qwen_client import QwenClient

logger = logging.getLogger(__name__)


class FieldDetector:
    """智能字段检测引擎"""
    
    # 字段别名规则库
    FIELD_ALIASES = {
        '销售额': ['销售额', '销售金额', '金额', '收入', '营收', 'sales', 'amount', 'revenue', 'income'],
        '订单时间': ['订单时间', '下单时间', '日期', '时间', 'order_date', 'date', 'time', 'order_time'],
        '销售员': ['销售员', '销售人员', '业务员', '销售', 'salesperson', 'salesman', 'seller', 'employee'],
        '产品': ['产品', '商品', '品名', '产品名称', 'product', 'item', 'goods', 'product_name'],
        '城市': ['城市', '地区', '区域', 'city', 'region', 'area', 'district'],
        '客户': ['客户', '顾客', '客户名称', 'customer', 'client', 'customer_name'],
        '利润': ['利润', '毛利', '盈利', 'profit', 'gross_profit'],
        '成本': ['成本', '成本价', 'cost'],
        '数量': ['数量', '件数', '个数', 'quantity', 'count', 'amount'],
        '单价': ['单价', '价格', 'unit_price', 'price'],
        '订单号': ['订单号', '订单编号', '单号', 'order_id', 'order_no', 'order_number'],
        '客户类型': ['客户类型', '客户属性', '新老客', 'customer_type', 'customer_category'],
        '年龄段': ['年龄段', '年龄', 'age', 'age_group'],
    }
    
    # 必填字段（用于严格模式）
    REQUIRED_FIELDS = ['销售额']
    
    def __init__(self, base_dir: str = None, enable_ai: bool = True):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(__file__))
        self.enable_ai = enable_ai
        self.qwen_client = QwenClient(base_dir) if enable_ai else None
        self.aliases = self._load_aliases()
    
    def _load_aliases(self) -> Dict:
        """加载字段别名库"""
        aliases_file = os.path.join(self.base_dir, 'config', 'field_aliases.json')
        if os.path.exists(aliases_file):
            with open(aliases_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.FIELD_ALIASES
    
    def detect(self, df: pd.DataFrame, excel_filename: str = '') -> Dict:
        """
        检测字段（规则 + AI）
        
        Args:
            df: DataFrame
            excel_filename: Excel 文件名（用于 AI 分析）
        
        Returns:
            检测结果字典
        """
        # Step 1: 规则匹配
        rule_detected = self._detect_by_rules(df)
        
        # Step 2: AI 辅助（如果启用）
        if self.enable_ai and self.qwen_client and self.qwen_client.is_available():
            ai_detected = self._detect_by_ai(df, excel_filename)
            # 合并结果，AI 结果优先（高置信度）
            return self._merge_detection(rule_detected, ai_detected)
        
        return rule_detected
    
    def _detect_by_rules(self, df: pd.DataFrame) -> Dict:
        """基于规则匹配检测字段"""
        detected = {}
        
        for column in df.columns:
            column_lower = column.lower()
            match_info = self._match_field(column_lower)
            
            detected[column] = {
                'standard_name': match_info['standard_name'],
                'confidence': match_info['confidence'],  # high/medium/none
                'type': self._infer_type(df[column]),
                'method': 'rule',
                'sample_values': df[column].head(3).dropna().tolist()[:3]
            }
        
        return detected
    
    def _match_field(self, column_lower: str) -> Dict:
        """匹配字段别名"""
        for standard_name, aliases in self.aliases.items():
            if any(alias in column_lower for alias in aliases):
                # 根据匹配长度判断置信度
                match_length = max(len(alias) for alias in aliases if alias in column_lower)
                confidence = 'high' if match_length > 4 else 'medium'
                return {
                    'standard_name': standard_name,
                    'confidence': confidence
                }
        
        return {'standard_name': None, 'confidence': 'none'}
    
    def _infer_type(self, series: pd.Series) -> str:
        """推断数据类型"""
        if pd.api.types.is_numeric_dtype(series):
            # 检查是否是百分比
            if series.max() <= 1 and series.min() >= 0:
                return 'percentage'
            return 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(series):
            return 'datetime'
        elif pd.api.types.is_bool_dtype(series):
            return 'boolean'
        else:
            return 'text'
    
    def _detect_by_ai(self, df: pd.DataFrame, excel_filename: str) -> Dict:
        """AI 辅助检测"""
        # 构建样本数据（前 5 行）
        sample_data = df.head(5).to_dict('records')
        
        # 构建 Prompt
        prompt = f"""
你是一个数据分析专家。请分析以下 Excel 数据的字段含义：

文件名：{excel_filename}
列名列表：{list(df.columns)}
数据样本（前 5 行）：
{json.dumps(sample_data, ensure_ascii=False, indent=2)}

请判断每个列的：
1. 标准字段名（从以下选择：销售额、订单时间、销售员、产品、城市、客户、利润、成本、数量、单价、订单号、客户类型、年龄段、其他）
2. 数据类型（numeric/text/datetime/percentage/boolean）
3. 是否必填字段（true/false）
4. 置信度（0-100）

输出 JSON 格式：
{{
  "columns": {{
    "列名 1": {{
      "standard_name": "标准字段名",
      "type": "numeric",
      "required": true,
      "confidence": 95
    }},
    ...
  }}
}}
"""
        
        system_prompt = "你是数据分析专家，输出严格 JSON 格式。只输出 JSON，不要任何其他文字。"
        
        response = self.qwen_client.chat(system_prompt, prompt, json_mode=True)
        
        if response:
            result = self.qwen_client.parse_json_response(response)
            if result and 'columns' in result:
                # 转换为统一格式
                detected = {}
                for col, info in result['columns'].items():
                    detected[col] = {
                        'standard_name': info.get('standard_name'),
                        'confidence': 'high' if info.get('confidence', 0) >= 80 else 'medium',
                        'type': info.get('type', 'text'),
                        'required': info.get('required', False),
                        'method': 'ai'
                    }
                return detected
        
        return {}
    
    def _merge_detection(self, rule_detected: Dict, ai_detected: Dict) -> Dict:
        """合并规则和 AI 检测结果"""
        merged = rule_detected.copy()
        
        for col, ai_info in ai_detected.items():
            if col in merged:
                rule_info = merged[col]
                # AI 置信度高则优先
                if ai_info.get('confidence') == 'high':
                    merged[col] = ai_info
                    merged[col]['method'] = 'ai_enhanced'
            else:
                merged[col] = ai_info
        
        return merged
    
    def get_required_fields_status(self, detected: Dict) -> Dict:
        """检查必填字段状态"""
        status = {
            'missing': [],
            'found': [],
            'valid': True
        }
        
        found_fields = {info['standard_name'] for info in detected.values() if info.get('standard_name')}
        
        for field in self.REQUIRED_FIELDS:
            if field in found_fields:
                status['found'].append(field)
            else:
                status['missing'].append(field)
                status['valid'] = False
        
        return status
    
    def get_field_statistics(self, df: pd.DataFrame, detected: Dict) -> Dict:
        """获取字段统计信息"""
        stats = {}
        
        for col, info in detected.items():
            col_stats = {
                'type': info['type'],
                'non_null_count': int(df[col].notna().sum()),
                'null_count': int(df[col].isna().sum()),
                'unique_count': int(df[col].nunique())
            }
            
            if info['type'] == 'numeric':
                col_stats['min'] = float(df[col].min()) if df[col].notna().any() else None
                col_stats['max'] = float(df[col].max()) if df[col].notna().any() else None
                col_stats['mean'] = round(float(df[col].mean()), 2) if df[col].notna().any() else None
            
            stats[col] = col_stats
        
        return stats
