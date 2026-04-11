# -*- coding: utf-8 -*-
"""
基础图表模块 - 6 种常用图表
- 横向条形图、纵向柱状图、饼图/环形图、折线图
- 热力图、多系列柱状图
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class BasicChartsMixin:
    """基础图表混合类"""
    
    def create_bar_horizontal(self, df: pd.DataFrame, x_field: str, y_field: str,
                               title: str = '', output_path: str = None,
                               figsize: Tuple[int, int] = (10, 6),
                               color: str = None) -> str:
        """横向条形图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[y_field].tolist()
        values = df[x_field].tolist()
        
        if color:
            colors = color
        else:
            colors = self.colors.get('chart_palettes', {}).get('default', ['#1F4E79'])
            if isinstance(colors, list) and len(colors) > 1:
                colors = colors[:len(categories)]
            elif isinstance(colors, list):
                colors = colors[0]
        
        bars = ax.barh(categories, values, color=colors)
        
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(bar.get_width() + max(values) * 0.01,
                   bar.get_y() + bar.get_height() / 2,
                   f'{value:,.0f}',
                   va='center', fontsize=9, color='#2C3E50')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_bar_vertical(self, df: pd.DataFrame, x_field: str, y_field: str,
                            title: str = '', output_path: str = None,
                            figsize: Tuple[int, int] = (10, 6),
                            color: str = None) -> str:
        """纵向柱状图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[x_field].tolist()
        values = df[y_field].tolist()
        
        if color:
            colors = color
        else:
            colors = self.colors.get('chart_palettes', {}).get('default', ['#1F4E79'])
            if isinstance(colors, list) and len(colors) > 1:
                colors = colors[:len(categories)]
            elif isinstance(colors, list):
                colors = colors[0]
        
        bars = ax.bar(categories, values, color=colors)
        
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + max(values) * 0.01,
                   f'{value:,.0f}',
                   ha='center', va='bottom', fontsize=9, color='#2C3E50')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=45, ha='right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_pie(self, df: pd.DataFrame, category_field: str, value_field: str,
                   title: str = '', output_path: str = None,
                   figsize: Tuple[int, int] = (8, 8),
                   show_percentage: bool = True) -> str:
        """饼图/环形图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].tolist()
        values = df[value_field].tolist()
        
        colors = self.colors.get('chart_palettes', {}).get('categorical',
                    ['#1F4E79', '#27AE60', '#E74C3C', '#F39C12', '#9B59B6', '#3498DB'])
        
        wedges, texts, autotexts = ax.pie(values, labels=categories,
                                           colors=colors[:len(categories)],
                                           autopct='%1.1f%%' if show_percentage else None,
                                           startangle=90,
                                           pctdistance=0.85,
                                           wedgeprops=dict(width=0.4, edgecolor='white'))
        
        plt.setp(texts, fontsize=10, color='#2C3E50')
        if show_percentage:
            plt.setp(autotexts, fontsize=9, color='white', weight='bold')
        
        centre_circle = plt.Circle((0, 0), 0.35, fc='white')
        ax.add_artist(centre_circle)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_line(self, df: pd.DataFrame, x_field: str, y_field: str,
                    title: str = '', output_path: str = None,
                    figsize: Tuple[int, int] = (12, 6),
                    show_markers: bool = True,
                    show_values: bool = True) -> str:
        """折线图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        x_values = df[x_field].tolist()
        y_values = df[y_field].tolist()
        
        line_color = self.colors.get('colors', {}).get('primary', '#1F4E79')
        
        marker = 'o' if show_markers else None
        ax.plot(x_values, y_values, marker=marker, linewidth=2.5,
               color=line_color, markersize=8, markerfacecolor='white',
               markeredgewidth=2, markeredgecolor=line_color)
        
        ax.fill_between(range(len(x_values)), y_values, alpha=0.2, color=line_color)
        
        if show_values:
            for i, (x, y) in enumerate(zip(x_values, y_values)):
                ax.text(i, y + max(y_values) * 0.02,
                       f'{y:,.0f}',
                       ha='center', fontsize=9, color='#2C3E50')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.tick_params(axis='x', rotation=0)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, index_field: str,
                       columns: List[str], title: str = '',
                       output_path: str = None,
                       figsize: Tuple[int, int] = (10, 6),
                       cmap: str = 'YlOrRd',
                       annot: bool = True) -> str:
        """热力图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        index_values = df[index_field].tolist()
        data = []
        for _, row in df.iterrows():
            row_data = [float(row.get(col, 0)) for col in columns]
            data.append(row_data)
        
        data = np.array(data)
        
        sns.heatmap(data, annot=annot, fmt='.0f', cmap=cmap,
                   xticklabels=columns, yticklabels=index_values,
                   ax=ax, cbar_kws={'label': '销售额 (元)'},
                   linewidths=0.5, linecolor='white')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
    
    def create_multi_column(self, df: pd.DataFrame, category_field: str,
                            series: List[str], title: str = '',
                            output_path: str = None,
                            figsize: Tuple[int, int] = (10, 6)) -> str:
        """多系列柱状图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].tolist()
        x = np.arange(len(categories))
        
        colors = self.colors.get('chart_palettes', {}).get('categorical',
                    ['#1F4E79', '#27AE60', '#E74C3C', '#F39C12', '#9B59B6', '#3498DB'])
        
        width = 0.8 / len(series)
        
        for i, (series_name, color) in enumerate(zip(series, colors)):
            values = df[series_name].tolist()
            offset = (i - len(series) / 2 + 0.5) * width
            ax.bar(x + offset, values, width, label=series_name,
                  color=color, edgecolor='white', linewidth=1)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(loc='best', framealpha=0.95)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            logger.info(f"图表已保存：{output_path}")
            plt.close(fig)
            return output_path
        
        return fig
