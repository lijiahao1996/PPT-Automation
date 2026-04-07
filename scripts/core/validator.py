# -*- coding: utf-8 -*-
"""
数据校验器 - 企业级数据质量网关
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataQualityError(Exception):
    """数据质量异常"""
    pass


class DataValidator:
    """数据质量校验器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.rules = []
    
    def add_rule(self, field: str, check: str, action: str = 'fail',
                 params: Dict = None, message: str = None):
        """
        添加校验规则
        
        Args:
            field: 字段名
            check: 校验类型 (no_null, no_negative, date_range, min_count, etc.)
            action: 处理方式 ('fail' 终止执行，'warn' 仅警告，'alert' 记录但继续)
            params: 校验参数
            message: 自定义错误消息
        """
        self.rules.append({
            'field': field,
            'check': check,
            'action': action,
            'params': params or {},
            'message': message
        })
    
    def validate(self, df: pd.DataFrame) -> bool:
        """
        执行所有校验规则
        
        Returns:
            bool: 是否全部通过（fail 级别的规则）
        """
        self.errors = []
        self.warnings = []
        
        for rule in self.rules:
            result = self._check_rule(df, rule)
            
            if not result['passed']:
                if rule['action'] == 'fail':
                    self.errors.append(result['message'])
                    logger.error(f"数据校验失败：{result['message']}")
                elif rule['action'] == 'warn':
                    self.warnings.append(result['message'])
                    logger.warning(f"数据警告：{result['message']}")
                elif rule['action'] == 'alert':
                    self.warnings.append(result['message'])
                    logger.info(f"数据提示：{result['message']}")
        
        if self.errors:
            raise DataQualityError(f"数据校验失败：{'; '.join(self.errors)}")
        
        return True
    
    def _check_rule(self, df: pd.DataFrame, rule: Dict) -> Dict:
        """执行单条校验规则"""
        field = rule['field']
        check = rule['check']
        params = rule['params']
        message = rule['message']
        
        passed = True
        detail = ''
        
        try:
            if check == 'no_null':
                # 检查空值
                null_count = df[field].isna().sum()
                passed = null_count == 0
                detail = f"字段 '{field}' 有 {null_count} 个空值"
            
            elif check == 'no_negative':
                # 检查负值
                if pd.api.types.is_numeric_dtype(df[field]):
                    negative_count = (df[field] < 0).sum()
                    passed = negative_count == 0
                    detail = f"字段 '{field}' 有 {negative_count} 个负值"
            
            elif check == 'date_range':
                # 检查日期范围
                min_date = params.get('min')
                max_date = params.get('max')
                
                dates = pd.to_datetime(df[field], errors='coerce')
                valid_dates = dates.dropna()
                
                if min_date and len(valid_dates) > 0:
                    min_found = valid_dates.min()
                    if min_found < pd.to_datetime(min_date):
                        passed = False
                        detail = f"字段 '{field}' 最小日期 {min_found} 早于 {min_date}"
                
                if max_date and passed and len(valid_dates) > 0:
                    max_found = valid_dates.max()
                    if max_found > pd.to_datetime(max_date):
                        passed = False
                        detail = f"字段 '{field}' 最大日期 {max_found} 晚于 {max_date}"
            
            elif check == 'min_count':
                # 检查最小记录数
                min_count = params.get('min', 1)
                actual_count = len(df)
                passed = actual_count >= min_count
                detail = f"记录数 {actual_count} 小于最小要求 {min_count}"
            
            elif check == 'max_count':
                # 检查最大记录数
                max_count = params.get('max')
                if max_count:
                    actual_count = len(df)
                    passed = actual_count <= max_count
                    detail = f"记录数 {actual_count} 超过最大限制 {max_count}"
            
            elif check == 'unique':
                # 检查唯一性
                duplicates = df[field].duplicated().sum()
                passed = duplicates == 0
                detail = f"字段 '{field}' 有 {duplicates} 个重复值"
            
            elif check == 'in_range':
                # 检查值范围
                min_val = params.get('min')
                max_val = params.get('max')
                
                if pd.api.types.is_numeric_dtype(df[field]):
                    if min_val is not None:
                        below_min = (df[field] < min_val).sum()
                        if below_min > 0:
                            passed = False
                            detail = f"字段 '{field}' 有 {below_min} 个值小于 {min_val}"
                    
                    if max_val is not None and passed:
                        above_max = (df[field] > max_val).sum()
                        if above_max > 0:
                            passed = False
                            detail = f"字段 '{field}' 有 {above_max} 个值大于 {max_val}"
            
            elif check == 'valid_values':
                # 检查有效值列表
                valid_values = params.get('values', [])
                if valid_values:
                    invalid = df[~df[field].isin(valid_values)]
                    if len(invalid) > 0:
                        passed = False
                        detail = f"字段 '{field}' 有 {len(invalid)} 个无效值"
            
            elif check == 'custom':
                # 自定义校验函数
                func = params.get('func')
                if callable(func):
                    result = func(df)
                    passed = result[0]
                    detail = result[1] if len(result) > 1 else ''
            
            if not message:
                message = detail
            
        except Exception as e:
            passed = False
            message = f"校验执行错误：{str(e)}"
        
        return {
            'passed': passed,
            'message': message,
            'rule': rule
        }
    
    def get_summary(self, df: pd.DataFrame) -> Dict:
        """生成数据质量摘要报告"""
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': {}
        }
        
        for col in df.columns:
            col_info = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isna().sum()),
                'null_pct': round(df[col].isna().sum() / len(df) * 100, 2)
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['min'] = float(df[col].min()) if not df[col].isna().all() else None
                col_info['max'] = float(df[col].max()) if not df[col].isna().all() else None
                col_info['mean'] = round(float(df[col].mean()), 2) if not df[col].isna().all() else None
            
            if pd.api.types.is_object_dtype(df[col]):
                col_info['unique_count'] = int(df[col].nunique())
                col_info['top_value'] = str(df[col].mode().iloc[0]) if len(df[col].mode()) > 0 else None
            
            summary['columns'][col] = col_info
        
        return summary


# 预设校验规则集
class PresetValidators:
    """预设校验规则集"""
    
    @staticmethod
    def sales_data_validator(df: pd.DataFrame) -> DataValidator:
        """销售数据校验器"""
        validator = DataValidator()
        
        # 必填字段不能为空
        required_fields = ['订单时间', '销售员', '产品', '城市', '销售额']
        for field in required_fields:
            if field in df.columns:
                validator.add_rule(field, 'no_null', action='fail',
                                 message=f"必填字段 '{field}' 不能为空")
        
        # 销售额不能为负
        if '销售额' in df.columns:
            validator.add_rule('销售额', 'no_negative', action='fail',
                             message="销售额不能为负值")
        
        # 记录数检查
        validator.add_rule('_count', 'min_count', action='fail',
                          params={'min': 10},
                          message="数据量过少，至少需要 10 条记录")
        
        # 日期范围检查（可选）
        if '订单时间' in df.columns:
            validator.add_rule('订单时间', 'date_range', action='warn',
                              params={'min': '2020-01-01', 'max': '2030-12-31'},
                              message="订单时间超出合理范围")
        
        return validator
    
    @staticmethod
    def summary_data_validator(data: Dict[str, pd.DataFrame]) -> DataValidator:
        """统计汇总数据校验器"""
        validator = DataValidator()
        
        # 检查必要的 Sheet 是否存在
        required_sheets = ['核心 KPI', '销售员业绩', '产品占比', '城市排名']
        for sheet in required_sheets:
            if sheet not in data:
                validator.errors.append(f"缺少必要的统计表：{sheet}")
        
        if validator.errors:
            raise DataQualityError('; '.join(validator.errors))
        
        return validator
