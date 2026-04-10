# -*- coding: utf-8 -*-
"""
PPT 报告生成执行器
整合统计分析、图表生成、PPT 生成的完整流程
"""
import os
import sys
import json
import time
from datetime import datetime
from typing import Callable, Optional, Dict, List
import pandas as pd

class PPTReportGenerator:
    """PPT 报告生成器"""
    
    def __init__(self, base_dir: str, log_callback: Optional[Callable[[str], None]] = None):
        """
        初始化生成器
        
        Args:
            base_dir: 项目根目录
            log_callback: 日志回调函数，用于实时输出日志
        """
        self.base_dir = base_dir
        self.output_dir = os.path.join(base_dir, 'output')
        self.templates_dir = os.path.join(base_dir, 'templates')
        self.artifacts_dir = os.path.join(base_dir, 'artifacts')
        self.scripts_dir = os.path.join(base_dir, 'scripts')
        self.log = log_callback or (lambda x: print(x))
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
    
    def _log(self, message: str, level: str = 'INFO'):
        """输出日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log(f"[{timestamp}] [{level}] {message}")
    
    def detect_files(self) -> Dict[str, Optional[str]]:
        """检测 output 目录中的文件"""
        result = {
            'raw_data': None,
            'summary': None,
            'ppt_reports': []
        }
        
        if not os.path.exists(self.output_dir):
            return result
        
        for f in os.listdir(self.output_dir):
            if f.endswith('.xlsx') and '统计汇总' in f and not f.startswith('~'):
                result['summary'] = f
            elif f.endswith('.xlsx') and '统计汇总' not in f and not f.startswith('~'):
                result['raw_data'] = f
            elif f.endswith('.pptx') and not f.startswith('~'):
                result['ppt_reports'].append(f)
        
        return result
    
    def generate_statistics(self, raw_data_file: str) -> bool:
        """生成统计数据"""
        try:
            self._log("开始生成统计数据...")
            
            # 导入统计引擎
            sys.path.insert(0, self.scripts_dir)
            from core.stats_engine import StatsEngine
            
            # 加载原始数据
            raw_data_path = os.path.join(self.output_dir, raw_data_file)
            self._log(f"加载原始数据：{raw_data_path}")
            raw_df = pd.read_excel(raw_data_path)
            self._log(f"已加载 {len(raw_df)} 行 × {len(raw_df.columns)} 列")
            
            # 执行统计引擎
            stats_engine = StatsEngine(base_dir=self.base_dir, raw_data_file=raw_data_file)
            summary_file = raw_data_file.replace('.xlsx', '_统计汇总.xlsx') if raw_data_file.endswith('.xlsx') else raw_data_file + '_统计汇总.xlsx'
            output_path = os.path.join(self.output_dir, summary_file)
            
            self._log("执行统计引擎...")
            results = stats_engine.run_all(raw_df, output_path=output_path)
            
            self._log(f"✅ 统计生成完成：{summary_file} ({len(results)} 个 Sheet)", 'SUCCESS')
            return True
            
        except Exception as e:
            self._log(f"❌ 统计生成失败：{e}", 'ERROR')
            return False
    
    def generate_report(self, template_name: str = None) -> bool:
        """生成 PPT 报告"""
        try:
            self._log("开始生成 PPT 报告...")
            
            # 导入报告生成器
            sys.path.insert(0, self.scripts_dir)
            from generate_report import generate_report
            
            # 执行生成
            self._log("执行报告生成...")
            success = generate_report(
                template_name=template_name,
                output_name=None,
                parallel_charts=True
            )
            
            if success:
                self._log("✅ PPT 报告生成完成", 'SUCCESS')
            else:
                self._log("❌ PPT 报告生成失败", 'ERROR')
            
            return success
            
        except Exception as e:
            self._log(f"❌ PPT 报告生成失败：{e}", 'ERROR')
            import traceback
            self._log(traceback.format_exc(), 'ERROR')
            return False
    
    def run_full_pipeline(self, regenerate_stats: bool = False, template_name: str = None) -> Dict:
        """
        执行完整流程
        
        Args:
            regenerate_stats: 是否重新生成统计数据
            template_name: PPT 模板文件名
        
        Returns:
            执行结果字典
        """
        result = {
            'success': False,
            'files': {
                'raw_data': None,
                'summary': None,
                'ppt_report': None
            },
            'steps': {
                'statistics': False,
                'report': False
            }
        }
        
        self._log("=" * 60)
        self._log("🚀 开始执行 PPT 报告生成流程", 'INFO')
        self._log("=" * 60)
        
        # 1. 检测文件
        self._log("步骤 1: 检测文件...")
        files = self.detect_files()
        
        if not files['raw_data']:
            self._log("❌ 未找到原始数据文件，请先上传 Excel 文件", 'ERROR')
            return result
        
        result['files']['raw_data'] = files['raw_data']
        self._log(f"✓ 原始数据：{files['raw_data']}")
        
        if files['summary'] and not regenerate_stats:
            result['files']['summary'] = files['summary']
            self._log(f"✓ 统计汇总：{files['summary']} (使用已有文件)")
        else:
            if files['summary'] and regenerate_stats:
                self._log(f"ℹ 将重新生成统计汇总：{files['summary']}")
        
        # 2. 生成统计数据（如果需要）
        if not files['summary'] or regenerate_stats:
            self._log("步骤 2: 生成统计数据...")
            if self.generate_statistics(files['raw_data']):
                result['steps']['statistics'] = True
                # 重新检测文件
                files = self.detect_files()
                result['files']['summary'] = files['summary']
            else:
                self._log("❌ 统计生成失败，终止流程", 'ERROR')
                return result
        else:
            self._log("步骤 2: 跳过（使用已有统计文件）")
            result['steps']['statistics'] = True
        
        # 3. 生成 PPT 报告
        self._log("步骤 3: 生成 PPT 报告...")
        if self.generate_report(template_name):
            result['steps']['report'] = True
            # 重新检测文件
            files = self.detect_files()
            if files['ppt_reports']:
                result['files']['ppt_report'] = files['ppt_reports'][-1]  # 最新的报告
        else:
            self._log("❌ PPT 报告生成失败", 'ERROR')
            result['success'] = False
            return result
        
        # 完成
        result['success'] = True
        self._log("=" * 60)
        self._log("🎉 PPT 报告生成流程完成！", 'SUCCESS')
        self._log("=" * 60)
        
        return result


if __name__ == '__main__':
    # 测试
    def test_log(msg):
        print(msg)
    
    generator = PPTReportGenerator(
        base_dir=r'C:\Users\50319\Desktop\n8n',
        log_callback=test_log
    )
    
    result = generator.run_full_pipeline(regenerate_stats=False)
    print(f"\n执行结果：{result}")
