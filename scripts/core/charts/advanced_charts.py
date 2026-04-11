# -*- coding: utf-8 -*-
"""
高级图表模块 - 6 种特殊图表
- 面积图、误差棒图、极坐标图、瀑布图、漏斗图
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AdvancedChartsMixin:
    """高级图表混合类"""
    
    def create_area(self, df: pd.DataFrame, x_field: str, y_fields: List[str],
                    title: str = '', output_path: str = None,
                    figsize: Tuple[int, int] = (10, 6)) -> str:
        """面积图 - 累积趋势"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = df[x_field].tolist()
        colors = self.colors.get('chart_palettes', {}).get('default', ['#1F4E79', '#2E75B6', '#3498DB'])
        
        ax.stackplot(x, [df[y].tolist() for y in y_fields], labels=y_fields, colors=colors[:len(y_fields)], alpha=0.8)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.legend(loc='upper left', framealpha=0.95)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"面积图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_errorbar(self, df: pd.DataFrame, x_field: str, y_field: str, error_field: str,
                        title: str = '', output_path: str = None,
                        figsize: Tuple[int, int] = (10, 6),
                        color: str = None) -> str:
        """误差棒图 - 带误差范围"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x = df[x_field].tolist()
        y = df[y_field].tolist()
        yerr = df[error_field].tolist()
        color = color or self.colors.get('primary', '#1F4E79')
        
        ax.errorbar(x, y, yerr=yerr, fmt='o', color=color, ecolor='#E74C3C',
                   elinewidth=2, capsize=5, markersize=8, alpha=0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_field, fontsize=11)
        ax.set_ylabel(y_field, fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"误差棒图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_polar(self, df: pd.DataFrame, angle_field: str, radius_field: str,
                     title: str = '', output_path: str = None,
                     figsize: Tuple[int, int] = (8, 8),
                     color: str = None) -> str:
        """极坐标图/雷达图"""
        fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
        
        angles = np.radians(df[angle_field].tolist())
        radii = df[radius_field].tolist()
        color = color or self.colors.get('primary', '#1F4E79')
        
        ax.plot(angles, radii, linewidth=2, color=color, marker='o', markersize=8)
        ax.fill(angles, radii, alpha=0.25, color=color)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"极坐标图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_waterfall(self, df: pd.DataFrame, category_field: str, value_field: str,
                         title: str = '', output_path: str = None,
                         figsize: Tuple[int, int] = (10, 6)) -> str:
        """瀑布图 - 增减变化"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].tolist()
        values = df[value_field].tolist()
        
        colors = ['#27AE60' if v > 0 else '#E74C3C' for v in values]
        
        cumulative = 0
        for i, (cat, val) in enumerate(zip(categories, values)):
            ax.bar(i, val, bottom=cumulative if val > 0 else cumulative + val,
                  color=colors[i], alpha=0.8, edgecolor='white')
            cumulative += val
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories)
        ax.grid(True, alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"瀑布图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_funnel(self, df: pd.DataFrame, stage_field: str, value_field: str,
                      title: str = '', output_path: str = None,
                      figsize: Tuple[int, int] = (8, 10)) -> str:
        """漏斗图 - 流程转化"""
        fig, ax = plt.subplots(figsize=figsize)
        
        stages = df[stage_field].tolist()
        values = df[value_field].tolist()
        max_value = max(values)
        
        colors = self.colors.get('chart_palettes', {}).get('sequential', ['#1F4E79', '#2E75B6', '#3498DB', '#5DADE2', '#85C1E9'])
        
        for i, (stage, value) in enumerate(zip(stages, values)):
            width = (value / max_value) * 100
            left = (100 - width) / 2
            ax.barh(i, width, left=left, height=0.8, color=colors[i % len(colors)], alpha=0.8, edgecolor='white')
            ax.text(50, i, f'{value:,.0f}', ha='center', va='center', fontsize=11, fontweight='bold', color='#2C3E50')
            ax.text(50, i, f'{stage}', ha='center', va='bottom', fontsize=10, color='#7F8C8D', transform=ax.transData)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, len(stages) - 0.5)
        ax.set_axis_off()
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"漏斗图已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def clear_temp(self):
        """清理临时文件"""
        import shutil
        import os
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
            logger.info("临时图表文件已清理")
