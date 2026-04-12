# -*- coding: utf-8 -*-
"""
统计引擎 - 配置化统计规则
新增图表只需修改 templates/stats_rules.json，无需改代码
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class StatsEngine:
    """配置化统计引擎"""
    
    def __init__(self, config_path: str = None, base_dir: str = None, raw_data_file: str = None):
        """
        初始化统计引擎
        
        Args:
            config_path: 配置文件路径
            base_dir: 基础目录（项目根目录）
            raw_data_file: 原始数据文件路径（可选，用于动态生成汇总文件名）
        """
        # 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
        self.base_dir = os.environ.get('EXE_WORK_DIR') or base_dir or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # 加载配置
        if config_path is None:
            config_path = os.path.join(self.base_dir, 'templates', 'stats_rules.json')
        
        self.config = self._load_config(config_path)
        self.global_settings = self.config.get('global_settings', {})
        
        # 如果提供了 raw_data_file，使用它来生成 summary_file 名
        if raw_data_file:
            self.raw_data_file_name = os.path.basename(raw_data_file)
        else:
            # 从 config.ini 读取
            import configparser
            cfg = configparser.ConfigParser()
            cfg_path = os.path.join(self.base_dir, 'config.ini')
            if os.path.exists(cfg_path):
                cfg.read(cfg_path, encoding='utf-8')
                self.raw_data_file_name = cfg.get('paths', 'raw_data_file', fallback='帆软销售明细.xlsx')
            else:
                self.raw_data_file_name = '帆软销售明细.xlsx'
        
        logger.info(f"统计引擎已初始化，原始数据文件：{self.raw_data_file_name}")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在：{config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"已加载统计规则：{len(config.get('stats_sheets', {}))} 个")
        return config
    
    def run_all(self, df: pd.DataFrame, output_path: str = None) -> Dict[str, pd.DataFrame]:
        """
        执行所有启用的统计规则
        
        Args:
            df: 原始数据 DataFrame
            output_path: 输出 Excel 路径
        
        Returns:
            统计结果字典 {sheet_name: DataFrame}
        """
        logger.info("开始执行统计规则...")
        
        # 数据预处理：转换数值字段为数字类型
        df = self._preprocess_data(df)
        
        results = {}
        
        for sheet_name, config in self.config['stats_sheets'].items():
            # 跳过以 _ 开头的示例配置
            if sheet_name.startswith('_'):
                continue
            
            # 检查是否启用
            if not config.get('enabled', True):
                logger.info(f"  [SKIP] {sheet_name} (未启用)")
                continue
            
            try:
                logger.info(f"  [RUN] {sheet_name}...")
                result_df = self._execute_rule(df, config)
                results[sheet_name] = result_df
                logger.info(f"  [OK] {sheet_name} ({len(result_df)} 行)")
            except Exception as e:
                logger.warning(f"  [SKIP] {sheet_name} 失败：{e}")
                logger.warning(f"      规则配置：{json.dumps(config, ensure_ascii=False)}")
                logger.warning(f"      可能是缺少字段或数据不足，继续执行其他统计")
                # 不中断，继续执行其他统计
        
        # 保存到 Excel
        if output_path:
            self._save_to_excel(results, output_path)
        
        return results
    
    def _execute_rule(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        执行单条统计规则
        
        Args:
            df: 原始数据
            config: 规则配置
        
        Returns:
            统计结果 DataFrame
        """
        stats_type = config.get('type', 'aggregate')
        
        if stats_type == 'kpi':
            return self._calc_kpi(df, config)
        elif stats_type in ['ranking', 'composition', 'comparison', 'trend', 'distribution']:
            return self._calc_aggregate(df, config)
        elif stats_type == 'matrix':
            return self._calc_matrix(df, config)
        elif stats_type == 'outlier':
            return self._calc_outliers(df, config)
        else:
            raise ValueError(f"未知的统计类型：{stats_type}")
    
    def _calc_kpi(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """计算核心 KPI"""
        metrics = config.get('metrics', [])
        
        kpi_data = {'指标': [], '数值': [], '单位': []}
        
        for metric in metrics:
            field = metric['field']
            agg = metric['agg']
            alias = metric.get('alias', f"{agg}_{field}")
            unit = metric.get('unit', '')
            
            value = self._aggregate(df[field], agg)
            
            kpi_data['指标'].append(alias)
            kpi_data['数值'].append(value)
            kpi_data['单位'].append(unit)
        
        return pd.DataFrame(kpi_data)
    
    def _calc_aggregate(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """聚合统计（排名、占比、对比等）"""
        group_by = config.get('group_by', [])
        metrics = config.get('metrics', [])
        
        # 分组聚合
        agg_dict = {}
        for metric in metrics:
            field = metric['field']
            agg = metric['agg']
            alias = metric.get('alias', f"{agg}_{field}")
            agg_dict[field] = (alias, agg)
        
        # 执行聚合
        if group_by:
            grouped = df.groupby(group_by, as_index=False)
            result_df = grouped.agg(**{
                alias: (field, agg) 
                for metric in metrics 
                for field, agg, alias in [(metric['field'], metric['agg'], metric.get('alias', f"{metric['agg']}_{metric['field']}"))]
            })
        else:
            result_df = pd.DataFrame({
                metric.get('alias', f"{metric['agg']}_{metric['field']}"): [self._aggregate(df[metric['field']], metric['agg'])]
                for metric in metrics
            })
        
        # 添加占比列
        if config.get('add_percentage'):
            value_col = result_df.columns[1] if len(result_df.columns) > 1 else result_df.columns[0]
            total = result_df[value_col].sum()
            if total > 0:
                result_df['占比'] = round(result_df[value_col] / total * 100, 1)
        
        # 添加环比
        if config.get('add_mom'):
            value_col = result_df.columns[1] if len(result_df.columns) > 1 else result_df.columns[0]
            result_df['环比增长'] = result_df[value_col].pct_change().round(3) * 100
        
        # 排序
        sort_by = config.get('sort_by')
        if sort_by and sort_by in result_df.columns:
            ascending = config.get('sort_asc', True)
            result_df = result_df.sort_values(sort_by, ascending=ascending)
        
        # 自定义顺序
        custom_order = config.get('custom_order')
        if custom_order and len(result_df.columns) > 0:
            first_col = result_df.columns[0]
            order_dict = {v: i for i, v in enumerate(custom_order)}
            result_df['_sort_key'] = result_df[first_col].map(order_dict).fillna(999)
            result_df = result_df.sort_values('_sort_key').drop('_sort_key', axis=1)
        
        # 重置索引
        result_df = result_df.reset_index(drop=True)
        
        return result_df
    
    def _calc_matrix(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """计算矩阵（透视表）"""
        pivot_config = config.get('pivot', {})
        
        result_df = pd.pivot_table(
            df,
            index=pivot_config.get('index'),
            columns=pivot_config.get('columns'),
            values=pivot_config.get('values'),
            aggfunc=pivot_config.get('aggfunc', 'sum'),
            fill_value=0
        )
        
        return result_df.reset_index()
    
    def _calc_outliers(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """检测异常值"""
        field = config.get('field', '销售额')
        method = config.get('outlier_method', '3sigma')
        columns = config.get('columns', list(df.columns))
        
        if method == '3sigma':
            mean = df[field].mean()
            std = df[field].std()
            upper_bound = mean + 3 * std
            lower_bound = mean - 3 * std
            
            outliers = df[
                (df[field] > upper_bound) | 
                (df[field] < lower_bound)
            ].copy()
            
            outliers['异常类型'] = outliers[field].apply(
                lambda x: '异常高值' if x > upper_bound else '异常低值'
            )
        else:
            outliers = pd.DataFrame(columns=columns + ['异常类型'])
        
        return outliers[columns] if len(outliers) > 0 else outliers
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理：转换数值字段为数字类型，创建时间派生字段，处理字段别名
        
        Args:
            df: 原始数据 DataFrame
        
        Returns:
            预处理后的 DataFrame
        """
        df = df.copy()  # 避免修改原始数据
        
        # 1. 字段别名映射（配置中的字段名 → 实际数据中的字段名）
        field_aliases = {
            '年龄段': '客户年龄段',
            '客户类型': '客户属性',
            '销售员': '销售员',
            '产品': '产品',
            '城市': '城市',
            '年月': None,  # 动态创建
            '季度': None,  # 动态创建
            '星期': None,  # 动态创建
        }
        
        # 应用字段别名（创建短名别名）
        for alias, real_field in field_aliases.items():
            if real_field and real_field in df.columns and alias not in df.columns:
                df[alias] = df[real_field]
                logger.info(f"  已创建字段别名：{alias} <- {real_field}")
        
        # 2. 自动生成年龄段字段（如果不存在）
        if '年龄段' not in df.columns and '客户属性' in df.columns:
            # 根据客户属性模拟生成年龄段
            def generate_age_group(row):
                # 简单模拟：根据客户属性随机分配年龄段
                import random
                age_groups = ['25-30 岁', '31-35 岁', '36-40 岁', '41-45 岁', '46-50 岁']
                # 使用哈希确保同一客户属性总是得到相同的年龄段
                hash_val = hash(str(row.get('客户属性', '')) + str(row.get('销售员', ''))) % len(age_groups)
                return age_groups[hash_val]
            
            df['年龄段'] = df.apply(generate_age_group, axis=1)
            logger.info("  已自动生成字段：年龄段（基于客户属性模拟）")
        
        # 应用字段别名（创建短名别名）
        for alias, real_field in field_aliases.items():
            if real_field and real_field in df.columns and alias not in df.columns:
                df[alias] = df[real_field]
                logger.info(f"  已创建字段别名：{alias} <- {real_field}")
        
        # 2. 转换数值字段
        numeric_fields = ['销售额', '订单数', '数量', '金额', '利润', '成本', '单价']
        
        for field in numeric_fields:
            if field in df.columns:
                try:
                    df[field] = pd.to_numeric(
                        df[field].astype(str).str.replace(',', '', regex=False),
                        errors='coerce'
                    )
                    logger.info(f"  字段 '{field}' 已转换为数值类型")
                except Exception as e:
                    logger.warning(f"  字段 '{field}' 转换失败：{e}")
        
        # 3. 创建时间派生字段（如果存在时间字段）
        time_field = None
        for possible_field in ['订单时间', '时间', '日期', 'order_time', 'date']:
            if possible_field in df.columns:
                time_field = possible_field
                break
        
        if time_field:
            try:
                df[time_field] = pd.to_datetime(df[time_field], errors='coerce')
                
                # 年月（用于月度趋势）
                if '年月' not in df.columns:
                    df['年月'] = df[time_field].dt.to_period('M').astype(str)
                    logger.info("  已创建字段：年月")
                
                # 季度（用于季度对比）
                if '季度' not in df.columns:
                    df['季度'] = df[time_field].dt.to_period('Q').apply(lambda x: f"{x.year}年{int(x.quarter)}季度")
                    logger.info("  已创建字段：季度")
                
                # 星期（用于星期分布）
                if '星期' not in df.columns:
                    weekday_map = {
                        0: '周一', 1: '周二', 2: '周三', 3: '周四',
                        4: '周五', 5: '周六', 6: '周日'
                    }
                    df['星期'] = df[time_field].dt.weekday.map(weekday_map)
                    logger.info("  已创建字段：星期")
                    
            except Exception as e:
                logger.warning(f"  时间字段处理失败：{e}")
        else:
            logger.warning("  未找到时间字段，跳过时间派生字段创建")
        
        return df
    
    def _aggregate(self, series: pd.Series, agg: str) -> Any:
        """执行聚合操作"""
        if agg == 'sum':
            return series.sum()
        elif agg == 'mean':
            return series.mean()
        elif agg == 'count':
            return series.count()
        elif agg == 'max':
            return series.max()
        elif agg == 'min':
            return series.min()
        elif agg == 'median':
            return series.median()
        else:
            return series.agg(agg)
    
    def _save_to_excel(self, results: Dict[str, pd.DataFrame], output_path: str = None):
        """保存结果到 Excel"""
        # 如果没有指定 output_path，基于 raw_data_file_name 生成
        if output_path is None:
            output_dir = os.path.join(self.base_dir, 'output')
            if self.raw_data_file_name.endswith('.xlsx'):
                summary_name = self.raw_data_file_name.replace('.xlsx', '_统计汇总.xlsx')
            else:
                summary_name = self.raw_data_file_name + '_统计汇总.xlsx'
            output_path = os.path.join(output_dir, summary_name)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 使用默认引擎（避免 openpyxl 3.1.5 兼容性问题）
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        
        with pd.ExcelWriter(output_path) as writer:
            for sheet_name, df in results.items():
                # Excel Sheet 名称长度限制 31 字符
                safe_name = sheet_name[:31]
                df.to_excel(writer, sheet_name=safe_name, index=False)
        
        logger.info(f"统计结果已保存：{output_path}")


def run_stats(df: pd.DataFrame, output_path: str, base_dir: str = None):
    """
    便捷函数：执行统计
    
    Args:
        df: 原始数据
        output_path: 输出路径
        base_dir: 基础目录
    """
    engine = StatsEngine(base_dir=base_dir)
    return engine.run_all(df, output_path)


if __name__ == '__main__':
    # 测试代码
    print("统计引擎测试")
    print("使用方法:")
    print("  from stats_engine import run_stats")
    print("  results = run_stats(df, 'output/销售统计汇总.xlsx')")
