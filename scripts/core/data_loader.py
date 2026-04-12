# -*- coding: utf-8 -*-
"""
数据加载器 - 统一数据读取接口
"""
import pandas as pd
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """数据加载器 - 支持多种数据源"""
    
    def __init__(self, base_dir: str = None):
        # 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
        self.base_dir = os.environ.get('EXE_WORK_DIR') or base_dir or os.path.dirname(os.path.dirname(__file__))
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.artifacts_dir = os.path.join(self.base_dir, 'artifacts')
        self._cache = {}
    
    def load_raw_data(self, filename: str = '帆软销售明细.xlsx') -> pd.DataFrame:
        """加载原始数据"""
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"原始数据文件不存在：{filepath}")
        
        logger.info(f"加载原始数据：{filepath}")
        df = pd.read_excel(filepath, header=0)
        logger.info(f"  行数：{len(df)}, 列数：{len(df.columns)}")
        
        return df
    
    def load_summary(self, filename: str = None) -> Dict[str, pd.DataFrame]:
        """加载统计汇总表（所有 Sheet）"""
        # 支持从 summary 子目录或 output 根目录加载
        summary_subdir = os.path.join(self.output_dir, 'summary')
        
        # 如果没有指定文件名，自动查找
        if filename is None:
            # 优先从 summary 目录查找
            if os.path.exists(summary_subdir):
                for f in os.listdir(summary_subdir):
                    if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                        filename = f
                        filepath = os.path.join(summary_subdir, filename)
                        break
            
            # 如果 summary 目录没有，从 output 根目录查找
            if filename is None:
                for f in os.listdir(self.output_dir):
                    if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                        filename = f
                        filepath = os.path.join(self.output_dir, filename)
                        break
            
            # 如果还没找到，使用默认值
            if filename is None:
                filename = '销售统计汇总.xlsx'
                filepath = os.path.join(summary_subdir, filename)
        else:
            # 指定了文件名，优先从 summary 目录查找
            filepath = os.path.join(summary_subdir, filename)
            if not os.path.exists(filepath):
                # 如果 summary 目录没有，尝试 output 根目录
                filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            # 尝试自动查找最近的 xlsx 文件
            search_dirs = [summary_subdir, self.output_dir] if os.path.exists(summary_subdir) else [self.output_dir]
            for search_dir in search_dirs:
                xlsx_files = [f for f in os.listdir(search_dir) if f.endswith('.xlsx') and not f.startswith('~')]
                if xlsx_files:
                    for f in sorted(xlsx_files, reverse=True):
                        if '统计汇总' not in f:
                            filepath = os.path.join(search_dir, f)
                            logger.info(f"自动使用文件：{filepath}")
                            break
                if os.path.exists(filepath):
                    break
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"统计汇总文件不存在：{filepath}")
        
        logger.info(f"加载统计汇总：{filepath}")
        
        data = {}
        with pd.ExcelFile(filepath) as xls:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                data[sheet_name] = df
                logger.info(f"  Sheet '{sheet_name}': {len(df)} 行")
        
        return data
    
    def load_sheet(self, sheet_name: str, filename: str = '销售统计汇总.xlsx') -> pd.DataFrame:
        """加载指定 Sheet"""
        data = self.load_summary(filename)
        
        if sheet_name not in data:
            available = list(data.keys())
            raise KeyError(f"Sheet '{sheet_name}' 不存在，可用的 Sheet: {available}")
        
        return data[sheet_name]
    
    def get_kpi(self, sheet_name: str = '核心 KPI') -> Dict[str, float]:
        """获取 KPI 字典"""
        df = self.load_sheet(sheet_name)
        kpi_dict = {}
        
        for _, row in df.iterrows():
            metric_name = row.iloc[0]
            value = row.iloc[1]
            unit = row.iloc[2] if len(row) > 2 else ''
            kpi_dict[metric_name] = {
                'value': value,
                'unit': unit,
                'formatted': f"{value:,.2f}" if unit == '元' else f"{int(value):,}"
            }
        
        return kpi_dict
    
    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("数据缓存已清除")
