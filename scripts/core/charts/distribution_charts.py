# -*- coding: utf-8 -*-
"""
分布图表模块 - 5 种分布分析图表
- 散点图、直方图、箱线图、小提琴图、气泡图
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DistributionChartsMixin:
    """分布图表混合类"""
    
    def create_scatter(self, df: pd.DataFrame, x_field: str, y_field: str,
                       title: str = '', output_path: str = None,
                       figsize: Tuple[int, int] = (10, 6),
                       color: str = None, size: int = 50) -> str:
        """散点图 - 相关性分析"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = df[x_field].tolist()
        y = df[y_field].tolist()
        
        color = color or self.colors.get('primary', '#1F4E79')
        ax.scatter(x, y, c=color, alpha=0.6, s=size, edgecolors='white', linewidth=0.5)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_field, fontsize=11)
        ax.set_ylabel(y_field, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"散点图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_histogram(self, df: pd.DataFrame, field: str,
                         title: str = '', output_path: str = None,
                         figsize: Tuple[int, int] = (10, 6),
                         bins: int = 20,
                         color: str = None) -> str:
        """直方图 - 分布分析"""
        fig, ax = plt.subplots(figsize=figsize)
        
        data = df[field].dropna().tolist()
        color = color or self.colors.get('primary', '#1F4E79')
        
        ax.hist(data, bins=bins, color=color, alpha=0.7, edgecolor='white', linewidth=0.5)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(field, fontsize=11)
        ax.set_ylabel('频数', fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"直方图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_boxplot(self, df: pd.DataFrame, category_field: str, value_field: str,
                       title: str = '', output_path: str = None,
                       figsize: Tuple[int, int] = (10, 6)) -> str:
        """箱线图 - 分布分析"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].unique()
        data = [df[df[category_field] == cat][value_field].dropna().tolist() for cat in categories]
        
        bp = ax.boxplot(data, labels=categories, patch_artist=True,
                       boxprops=dict(facecolor=self.colors.get('primary', '#1F4E79'), alpha=0.3),
                       medianprops=dict(color='#E74C3C', linewidth=2),
                       whiskerprops=dict(color='#2C3E50'),
                       capprops=dict(color='#2C3E50'))
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel(value_field, fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"箱线图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_violin(self, df: pd.DataFrame, category_field: str, value_field: str,
                      title: str = '', output_path: str = None,
                      figsize: Tuple[int, int] = (10, 6)) -> str:
        """小提琴图 - 分布密度"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].unique()
        data = [df[df[category_field] == cat][value_field].dropna().tolist() for cat in categories]
        
        parts = ax.violinplot(data, showmeans=True, showmedians=True)
        
        for pc in parts['bodies']:
            pc.set_facecolor(self.colors.get('primary', '#1F4E79'))
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel(value_field, fontsize=11)
        ax.set_xticks(range(1, len(categories) + 1))
        ax.set_xticklabels(categories)
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"小提琴图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_bubble(self, df: pd.DataFrame, x_field: str, y_field: str, size_field: str,
                      title: str = '', output_path: str = None,
                      figsize: Tuple[int, int] = (10, 6),
                      color: str = None,
                      size_multiplier: float = 10) -> str:
        """气泡图 - 三维数据对比"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = df[x_field].tolist()
        y = df[y_field].tolist()
        sizes = (df[size_field] / df[size_field].max() * 50 * size_multiplier).tolist()
        color = color or self.colors.get('primary', '#1F4E79')
        
        scatter = ax.scatter(x, y, s=sizes, c=color, alpha=0.6, edgecolors='white', linewidth=0.5)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_field, fontsize=11)
        ax.set_ylabel(y_field, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"气泡图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
