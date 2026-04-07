# -*- coding: utf-8 -*-
"""
图表引擎 - 企业级图表生成器（Matplotlib + 企业样式）
"""
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ChartEngine:
    """企业级图表引擎"""
    
    def __init__(self, base_dir: str = None):
        # 支持 EXE 打包：优先使用 EXE_WORK_DIR 环境变量
        self.base_dir = os.environ.get('EXE_WORK_DIR') or base_dir or os.path.dirname(os.path.dirname(__file__))
        self.styles_dir = os.path.join(self.base_dir, 'core', 'styles')  # styles 在 core 目录下
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
    
    def _load_color_palette(self) -> Dict:
        """加载配色方案"""
        palette_file = os.path.join(self.styles_dir, 'color_palette.json')
        if os.path.exists(palette_file):
            with open(palette_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def create_bar_horizontal(self, df: pd.DataFrame, x_field: str, y_field: str,
                               title: str = '', output_path: str = None,
                               figsize: Tuple[int, int] = (10, 6),
                               color: str = None) -> str:
        """横向条形图"""
        fig, ax = plt.subplots(figsize=figsize)
        
        # 准备数据
        categories = df[y_field].tolist()
        values = df[x_field].tolist()
        
        # 颜色
        if color:
            colors = color
        else:
            colors = self.colors.get('chart_palettes', {}).get('default', ['#1F4E79'])
            if isinstance(colors, list) and len(colors) > 1:
                colors = colors[:len(categories)]
            elif isinstance(colors, list):
                colors = colors[0]
        
        # 绘制
        bars = ax.barh(categories, values, color=colors)
        
        # 添加数据标签
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
        
        # 添加数据标签
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
        
        # 颜色
        colors = self.colors.get('chart_palettes', {}).get('categorical',
                    ['#1F4E79', '#27AE60', '#E74C3C', '#F39C12', '#9B59B6', '#3498DB'])
        
        # 创建环形图
        wedges, texts, autotexts = ax.pie(values, labels=categories,
                                           colors=colors[:len(categories)],
                                           autopct='%1.1f%%' if show_percentage else None,
                                           startangle=90,
                                           pctdistance=0.85,
                                           wedgeprops=dict(width=0.4, edgecolor='white'))
        
        # 设置字体
        plt.setp(texts, fontsize=10, color='#2C3E50')
        if show_percentage:
            plt.setp(autotexts, fontsize=9, color='white', weight='bold')
        
        # 添加中心圆，形成环形效果
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
        
        # 颜色
        line_color = self.colors.get('colors', {}).get('primary', '#1F4E79')
        
        # 绘制折线
        marker = 'o' if show_markers else None
        ax.plot(x_values, y_values, marker=marker, linewidth=2.5,
               color=line_color, markersize=8, markerfacecolor='white',
               markeredgewidth=2, markeredgecolor=line_color)
        
        # 填充区域
        ax.fill_between(range(len(x_values)), y_values, alpha=0.2, color=line_color)
        
        # 添加数据标签
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
        
        # 准备数据
        index_values = df[index_field].tolist()
        data = []
        for _, row in df.iterrows():
            row_data = [float(row.get(col, 0)) for col in columns]
            data.append(row_data)
        
        data = np.array(data)
        
        # 创建热力图
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
        
        # 颜色
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
    
    # ========== 扩展图表类型 ==========
    
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
    
    def create_waterfall(self, df: pd.DataFrame, category_field: str, value_field: str,
                         title: str = '', output_path: str = None,
                         figsize: Tuple[int, int] = (10, 6)) -> str:
        """瀑布图 - 增减变化"""
        fig, ax = plt.subplots(figsize=figsize)
        
        categories = df[category_field].tolist()
        values = df[value_field].tolist()
        
        colors = ['#27AE60' if v > 0 else '#E74C3C' for v in values]
        
        cumulative = 0
        bars = []
        for i, (cat, val) in enumerate(zip(categories, values)):
            bars.append(ax.bar(i, val, bottom=cumulative if val > 0 else cumulative + val,
                              color=colors[i], alpha=0.8, edgecolor='white'))
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
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
            logger.info("临时图表文件已清理")
