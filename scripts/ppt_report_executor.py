from queue import Queue
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
        self.log_callback = log_callback or (lambda x: print(x))
        # 使用队列来安全地传递日志（避免多线程问题）
        self.log_queue = Queue()
        
        # 确保目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
    
    def _log(self, message: str, level: str = 'INFO'):
        """输出日志（线程安全）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        log_entry_html = f"[{timestamp}] [{level}] {message}<br>"  # 添加 <br> 换行用于 Web 显示
        
        # 写入文件日志
        try:
            logs_dir = os.path.join(self.base_dir, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            log_file = os.path.join(logs_dir, f'ppt_{datetime.now().strftime("%Y%m%d")}.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            pass  # 忽略文件写入错误
        
        # 将日志放入队列（线程安全）
        self.log_queue.put(log_entry_html)
        # 同时调用回调（如果在主线程中）
        try:
            self.log_callback(log_entry_html)
        except:
            pass  # 忽略多线程中的 UI 调用错误
    
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
            self._log("=" * 60, 'INFO')
            self._log("步骤 2: 统计分析（清洗 + 统计）", 'INFO')
            self._log("=" * 60, 'INFO')
            
            # 导入统计引擎
            sys.path.insert(0, self.scripts_dir)
            from core.stats_engine import StatsEngine
            
            # 加载原始数据
            raw_data_path = os.path.join(self.output_dir, raw_data_file)
            self._log(f"[1/6] 读取原始数据...", 'INFO')
            self._log(f"      文件路径：{raw_data_path}", 'INFO')
            raw_df = pd.read_excel(raw_data_path)
            self._log(f"      原始数据：{len(raw_df)} 行", 'INFO')
            self._log(f"      列名：{list(raw_df.columns)}", 'INFO')
            
            # 执行统计引擎
            stats_engine = StatsEngine(base_dir=self.base_dir, raw_data_file=raw_data_file)
            summary_file = raw_data_file.replace('.xlsx', '_统计汇总.xlsx') if raw_data_file.endswith('.xlsx') else raw_data_file + '_统计汇总.xlsx'
            output_path = os.path.join(self.output_dir, summary_file)
            
            self._log(f"[2/6] 执行统计引擎...", 'INFO')
            results = stats_engine.run_all(raw_df, output_path=output_path)
            
            self._log(f"      [OK] 统计引擎执行完成，生成 {len(results)} 个统计表", 'SUCCESS')
            self._log(f"      [OK] 统计汇总：{output_path}", 'SUCCESS')
            self._log(f"      [OK] 共 {len(results)} 个 Sheet", 'SUCCESS')
            
            # 显示 Sheet 列表
            self._log("", 'INFO')
            self._log("生成的统计 Sheet:", 'INFO')
            for sheet_name, df in results.items():
                self._log(f"  - {sheet_name}: {len(df)} 行", 'INFO')
            
            self._log("", 'INFO')
            self._log(f"✅ 统计生成完成：{summary_file}", 'SUCCESS')
            return True
            
        except Exception as e:
            self._log(f"❌ 统计生成失败：{e}", 'ERROR')
            import traceback
            self._log(traceback.format_exc(), 'ERROR')
            return False
    
    def generate_report(self, template_name: str = None) -> bool:
        """生成 PPT 报告"""
        try:
            self._log("=" * 60, 'INFO')
            self._log("步骤 3: 生成 PPT 报告（模板 + 图表 + AI）", 'INFO')
            self._log("=" * 60, 'INFO')
            
            # 导入报告生成器
            sys.path.insert(0, self.scripts_dir)
            from generate_report import generate_report
            
            # 执行生成
            self._log(f"使用模板：{template_name}", 'INFO')
            self._log("执行报告生成...", 'INFO')
            success = generate_report(
                template_name=template_name,
                output_name=None,
                parallel_charts=True,
                log_callback=lambda msg: self._log(msg, 'INFO')
            )
            
            if success:
                self._log("", 'INFO')
                self._log("=" * 60, 'SUCCESS')
                self._log("[OK] 报告生成完成！", 'SUCCESS')
                self._log("=" * 60, 'SUCCESS')
            else:
                self._log("❌ PPT 报告生成失败", 'ERROR')
            
            return success
            
        except Exception as e:
            self._log(f"❌ PPT 报告生成失败：{e}", 'ERROR')
            import traceback
            self._log(traceback.format_exc(), 'ERROR')
            return False
    
    def run_full_pipeline(self, regenerate_stats: bool = False, template_name: str = None, raw_data_file: str = None) -> Dict:
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
        # 初始化 files 变量
        files = result['files']
        
        self._log("========================================<br>", 'INFO')
        self._log("  🚀 PPT 报告生成器 - Web 版<br>", 'INFO')
        self._log("========================================<br>", 'INFO')
        self._log("<br>", 'INFO')
        
        self._log("", 'INFO')
        
        # 1. 检测文件（优先使用传入的 raw_data_file 参数）
        if raw_data_file:
            files['raw_data'] = raw_data_file
            # 统计汇总文件名
            summary_name = raw_data_file.replace('.xlsx', '_统计汇总.xlsx') if raw_data_file.endswith('.xlsx') else raw_data_file + '_统计汇总.xlsx'
            summary_path = os.path.join(self.output_dir, summary_name)
            if os.path.exists(summary_path):
                files['summary'] = summary_name
        else:
            # 没有传入参数，使用 session_state 或自动检测
            import streamlit as st
            if 'uploaded_file_name' in st.session_state:
                uploaded_name = st.session_state['uploaded_file_name']
                raw_path = os.path.join(self.output_dir, uploaded_name)
                if os.path.exists(raw_path):
                    files['raw_data'] = uploaded_name
                    # 统计汇总文件名
                    summary_name = uploaded_name.replace('.xlsx', '_统计汇总.xlsx') if uploaded_name.endswith('.xlsx') else uploaded_name + '_统计汇总.xlsx'
                    summary_path = os.path.join(self.output_dir, summary_name)
                    if os.path.exists(summary_path):
                        files['summary'] = summary_name
            
            # 如果还没有，自动检测
            if not files['raw_data']:
                files = self.detect_files()
        
        
        if not files['raw_data']:
            self._log("❌ 未找到原始数据文件，请先上传 Excel 文件", 'ERROR')
            return result
        
        result['files']['raw_data'] = files['raw_data']
        self._log(f"[OK] Raw data file: {files['raw_data']}", 'SUCCESS')
        
        if files['summary'] and not regenerate_stats:
            result['files']['summary'] = files['summary']
            self._log(f"[OK] Summary file exists: {files['summary']}", 'SUCCESS')
        else:
            if files['summary'] and regenerate_stats:
                self._log(f"[INFO] Will regenerate summary: {files['summary']}", 'INFO')
        
        # 2. 生成统计数据（如果需要）
        if not files['summary'] or regenerate_stats:
            self._log("", 'INFO')
            self._log("Step 1: Analyze Data (with validation)...", 'INFO')
            if self.generate_statistics(files['raw_data']):
                result['steps']['statistics'] = True
                # 重新检测文件
                files = self.detect_files()
                result['files']['summary'] = files['summary']
            else:
                self._log("❌ 统计生成失败，终止流程", 'ERROR')
                return result
        else:
            self._log("[OK] Using existing summary file", 'SUCCESS')
        
        # 3. 生成 PPT 报告
        self._log("", 'INFO')
        self._log("Step 2: Generate Report (Template + Charts + AI)...", 'INFO')
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
        self._log("", 'INFO')
        self._log("========================================", 'SUCCESS')
        self._log("  Complete!", 'SUCCESS')
        self._log("========================================", 'SUCCESS')
        
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
